import time
from typing import Optional

import requests
from sqlmodel import select, Session

from models import League
from utils import get_stratz_league_data


def _is_a_value(dict_: dict, key_: str, ) -> bool:
    if key_ in dict_ and dict_[key_]:
        return True
    return False

def _same_dates(date_start: Optional[int], date_end: Optional[int], ) -> bool:
    if date_start is not None and (date_start == date_end):
        return True
    return False


def _update_league_dates(league_obj: League,
                         start_date: int | None = None,
                         end_date: int | None = None, ) -> None:
    unix_timestamp_now = int(time.time())

    league_obj.start_date = start_date
    league_obj.end_date = end_date

    league_obj.has_started = bool(start_date < unix_timestamp_now)
    league_obj.has_ended = bool(end_date < unix_timestamp_now)

    league_obj.has_dates = True

    return None


def update_league_obj_dates(league_obj: League, league_data: dict | None = None) -> bool:
    if not league_data:
        league_data = get_stratz_league_data(league_id=league_obj.id)

    updated_dates = False

    start_date = league_data.get('startDateTime', None) and int(league_data['startDateTime'])
    end_date = league_data.get('endDateTime', None) and int(league_data['endDateTime'])

    if (league_obj.start_date != start_date
            or league_obj.end_date != end_date
            or (_same_dates(league_obj.start_date, league_obj.end_date)
                and start_date
                and not _same_dates(date_start=start_date, date_end=end_date))):
        _update_league_dates(league_obj=league_obj, start_date=start_date, end_date=end_date)
        updated_dates = True

    return updated_dates


def create_league(league_id: int, **kwargs) -> League:
    try:
        # TRY TO GET THE LEAGUE DATA FROM STRATZ FIRST
        league_data = get_stratz_league_data(league_id=league_id)
        league_obj = League(
            id=league_id,
            name=league_data['displayName'],
            **kwargs, )

        update_league_obj_dates(league_obj, league_data)
    except ConnectionError:
        # TRY IT AGAIN USING OPENDOTA NOW (OPENDOTA DOESN'T PROVIDE ADDITIONAL DATA)
        r = requests.get(f'https://api.opendota.com/api/leagues/{league_id}/')
        if r.status_code == 200 and r.content:
            data = r.json()
            league_obj = League(
                id=league_id,
                name=data['name'], )

        else:
            raise ConnectionError("STRATZ and OPENDOTA don't respond. Connection problems?")

    return league_obj


def get_or_create_league(league_id: int, db_session: Session, league_obj: League = None, ) -> League:
    if league_obj is None:
        league_q = db_session.get(League, league_id)
        if not league_q:
            league_obj = create_league(league_id)
            db_session.add(league_obj)
            db_session.commit()
            db_session.refresh(league_obj)
        else:
            league_obj: League = league_q

    if not league_obj.has_dates or _same_dates(league_obj.start_date, league_obj.end_date):
        try:
            if (update_league_obj_dates(league_obj)):
                db_session.add(league_obj)
                db_session.commit()
        except ConnectionError:
            pass

    return league_obj
