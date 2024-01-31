import os

import requests


STRATZ_API_TOKEN = os.getenv('STRATZ_API_TOKEN')


def get_stratz_league_data(league_id: int) -> dict | None:
    r = requests.get(f'https://api.stratz.com/api/v1/league/{league_id}',
                     headers={
                         'Content-Type': 'application/json',
                         'Authorization': f'Bearer {STRATZ_API_TOKEN}',
                     }, )
    if r.status_code == 200:
        return r.json()

    return None
