import time

import requests

from models import League
from utils import get_stratz_league_data


def _is_a_value(dict_: dict, key_: str, ) -> bool:
    if key_ in dict_ and dict_[key_]:
        return True
    return False


def _update_league_dates(league_obj: League,
                         start_date: int | None = None,
                         end_date: int | None = None,
                         use_obj_values: bool = False) -> None:
    unix_timestamp_now = int(time.time())

    if not use_obj_values:
        league_obj.has_dates = True
    else:
        start_date = league_obj.start_date
        end_date = league_obj.end_date

    league_obj.has_started = bool(start_date < unix_timestamp_now)
    league_obj.has_ended = bool(end_date < unix_timestamp_now)

    return None


def update_league_obj_dates(league_obj: League, league_data: dict | None = None) -> bool:
    if not league_data:
        league_data = get_stratz_league_data(league_id=league_obj.league_id)

    updated_dates = False

    start_date = int(league_data['startDateTime']) if _is_a_value(league_data, 'startDateTime') else None
    end_date = int(league_data['endDateTime']) if _is_a_value(league_data, 'endDateTime') else None

    if league_obj.start_date != start_date or league_obj.end_date != end_date:
        _update_league_dates(league_obj=league_obj, start_date=start_date, end_date=end_date)
        updated_dates = True

    return updated_dates


def create_league(league_id: int, **kwargs) -> League:
    league_data = get_stratz_league_data(league_id=league_id)

    if league_data:
        league_obj = League(
            league_id=league_id,
            name=league_data['displayName'],
            **kwargs, )

        update_league_obj_dates(league_obj, league_data)

        return league_obj

    else:
        raise requests.ConnectionError('STRATZ is not accessible right now')
