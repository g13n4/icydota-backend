import requests
import json


def _get_leagues(match_id: int):
    r = requests.get(f'https://api.opendota.com/api/matches/{match_id}')
    if r.status_code == 200:
        with open('./leagues.json', 'w') as file:
            json.dump(r.json(), file)


_get_leagues(7393133836)