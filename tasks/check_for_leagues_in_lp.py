import re
from typing import List, Dict

import requests
from bs4 import BeautifulSoup, Tag
from sqlmodel import select, Session

from celery_app import celery_app
from models import League
from tasks.create_league import create_league


BASE_SITE = 'https://liquipedia.net'


def get_league_id_from_lp(lp_link: str) -> int:
    response = requests.get(lp_link)
    text = str(response.content)

    return int(re.search(r'www.datdota.com/leagues/(\d+)', text, re.IGNORECASE)[1])


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
def check_for_leagues_in_lp(db_session: Session,
                            lowest_tier: int = 2,
                            qualifications_allowed: bool = False):
    sel_result = db_session.execute(select(League).where(League.fully_parsed == False))
    league_objs: List[League] = sel_result.scalars().all()

    db_leagues_dict_link: Dict[str, League] = {x.pd_link: x for x in league_objs}
    db_leagues_dict_id: Dict[int, League] = {x.league_id: x for x in league_objs}

    r = requests.get(BASE_SITE + "/dota2/Main_Page")
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, features="lxml")
        page_leagues = _get_leagues_from_main_page(soup)
        for page_league in page_leagues:
            # check if should be added to the db
            tier = page_league['tier']
            tier_name, tier_number = tier[0:4], int(tier[-1])
            if tier_name.lower() == 'qual' and not qualifications_allowed:
                continue
            if tier_number > lowest_tier:
                continue

            # league is not db or at least the link is not
            if not (db_leagues_dict_link.get(page_league['link'], None)):
                league_id = get_league_id_from_lp(page_league['link'])
                if league_id not in db_leagues_dict_id:
                    league_obj = create_league(league_id, tier=tier_number, pd_link=page_league['link'])

                    db_session.add(league_obj)
        db_session.commit()
