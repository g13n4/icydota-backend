import os

import requests
from dotenv import load_dotenv


load_dotenv()

STRATZ_API_TOKEN = os.getenv('STRATZ_API_TOKEN')


def get_league_data(league_id: int) -> None:
    r = requests.get(f'https://api.stratz.com/api/v1/league/{league_id}',
                     headers={
                         'Content-Type': 'application/json',
                         'Authorization': f'Bearer {STRATZ_API_TOKEN}',
                     }, )
    print(r.json())
    return


get_league_data(15931)
