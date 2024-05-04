import os

import requests
from dotenv import load_dotenv

load_dotenv()
STRATZ_API_TOKEN = os.getenv('STRATZ_API_TOKEN')


def get_stratz_league_data(league_id: int) -> dict | None:
    r = requests.get(f'https://api.stratz.com/api/v1/league/{league_id}',
                     headers={
                         'Content-Type': 'application/json',
                         'Authorization': f'Bearer {STRATZ_API_TOKEN}',
                     }, )
    if r.status_code == 200:
        return r.json()
    else:
        raise ConnectionError(f"Can't access STRATZ. Request code {r.status_code} {r.content}")


# FIX: DOES IT EVEN WORK? ERROR 500
def get_stratz_player_data() -> dict | None:
    r = requests.get('https://api.stratz.com/api/v1/Player/proSteamAccount',
                     headers={
                         'charset': 'utf-8',
                         'Content-Type': 'application/json',
                         'Authorization': f'Bearer {STRATZ_API_TOKEN}',
                     }, )
    if r.status_code == 200:
        return r.json()
    else:
        raise ConnectionError(f"Can't access STRATZ. Request code {r.status_code} {r.content}")
