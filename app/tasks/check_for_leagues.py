import re
from datetime import datetime
from time import mktime
from typing import List, Dict

import httpx
from bs4 import BeautifulSoup, Tag
from celery.schedules import crontab
from sqlmodel import create_engine, select, Session

from .process_league import process_league
from ..celery import celery_app
from ..models import League

engine = create_engine("sqlite:///database.db")
BASE_SITE = 'https://liquipedia.net'


def datetime_to_timestamp(date: str) -> int:
    test_datetime = datetime.fromisoformat(date)
    test_stamp = mktime(test_datetime.timetuple())
    return int(test_stamp)


def _set_odota_name(league_info: dict) -> None:
    response = httpx.get('https://api.opendota.com/api/leagues/' + str(league_info['league_id']))
    if response.status_code == 200:
        league_info['name'] = response.content
    else:
        league_info['name'] = None

    return None


def _set_league_date(league_info: dict) -> None:
    response = httpx.get(league_info['link'])
    text = str(response.content)
    for key, match_string, to_timestamp in [('league_id', r'www.datdota.com/leagues/(\d+)', False),
                                            ('league_start', r'start date:.*(\d{4}-\d{2}-\d{2})', True),
                                            ('league_end', r'end date:.*(\d{4}-\d{2}-\d{2})', True)]:

        league_info[key] = None
        if (match := re.search(match_string, text, re.IGNORECASE)):
            if to_timestamp:
                league_info[key] = datetime_to_timestamp(match[1])
            else:
                league_info[key] = match[1]


def _set_additional_league_info(league_info: dict) -> None:
    _set_odota_name(league_info)
    _set_league_date(league_info)
    return None


def _get_league_info_from_main_page(site_piece: Tag) -> Dict[str, str] | None:
    info = {}
    match = re.search(r'((Tier|Qual)\s?\d)', site_piece.text, re.IGNORECASE)
    if not match:
        return None

    _, name, *_ = site_piece.find_all('a')

    info['tier'] = match[1]
    info['link'] = BASE_SITE + name.attrs['href']

    return info


def _get_leagues_from_main_page(soup: BeautifulSoup) -> List[Dict[str, str]]:
    leagues_list_ul = soup.find('ul', {'class': 'tournaments-list'})
    leagues_list = []
    for league_stage_name, league_ul in zip(['upcoming', 'ongoing', 'completed'], leagues_list_ul):
        for league_elem in league_ul.find_all('li'):
            league_info = _get_league_info_from_main_page(league_elem)
            if league_info:
                league_info['status'] = league_stage_name
                leagues_list.append(league_info)

    return leagues_list


@celery_app.task
def check_for_leagues(db_engine,
                      lowest_tier: int = 2,
                      qualifications_allowed: bool = False):
    with Session(db_engine) as session:
        db_leagues = session.exec(select(League))
        db_leagues_dict: Dict[str, League] = {x.pd_link: x for x in db_leagues}

        r = httpx.get("https://liquipedia.net/dota2/Main_Page")
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, features="lxml")
            leagues = _get_leagues_from_main_page(soup)
            for league in leagues:
                # check if should be added to the db
                tier = league['tier']
                tier_name, tier_number = tier[0:4], int(tier[-1])
                if tier_name.lower() == 'qual' and not qualifications_allowed:
                    continue
                if tier_number > lowest_tier:
                    continue

                # league is already in db
                if (this_db_league := db_leagues_dict.get(league['link'], None)):

                    if not this_db_league.ended and league['status'] == 'completed':
                        this_db_league.ended = True
                        session.add(this_db_league)

                    if not this_db_league.start_date and this_db_league.end_date:
                        _set_additional_league_info(league)

                        if not this_db_league.start_date and league['start_date']:
                            this_db_league.start_data = league['start_date']

                        if not this_db_league.end_date and league['end_date']:
                            this_db_league.end_date = league['end_date']

                        session.add(this_db_league)

                # league is not db
                else:
                    _set_additional_league_info(league)
                    new_league = League(
                        pd_link=league['link'],
                        league_id=league['league_id'],
                        name=league['name'],

                        start_date=league['end_date'],
                        end_date=league['end_date'],

                        ended=True if league['status'] == 'completed' else False,
                        fully_parsed=False,
                    )
                    session.add(new_league)

            session.commit()
        # leagues check
        db_leagues = session.exec(select(League))
        for db_league in db_leagues:
            if not db_league.fully_parsed:
                process_league.delay(engine=db_league, league_obj=db_league)


@celery_app.on_after_configure.connect
def check_for_new_leagues(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='0', hour='*/6'),
        check_for_leagues.s(engine=engine),
    )
