import requests
from bs4 import BeautifulSoup, Tag
import re

BASE_SITE = 'https://liquipedia.net'


def _set_odota_name(league_info: dict) -> None:
    response = requests.get('https://api.opendota.com/api/leagues/' + str(league_info['league_id']), timeout=0.7)
    if response.status_code == 200:
        league_info['name'] = response.content
    else:
        league_info['name'] = None

    return None


def _set_additional_league_info(league_info: dict) -> None:
    response = requests.get(league_info['link'], timeout=0.7)
    text = str(response.content)
    for key, match_string in [('league_id', r'www.datdota.com/leagues/(\d+)'),
                              ('league_start', r'start date:.*(\d{4}-\d{2}-\d{2})'),
                              ('league_end', r'end date:.*(\d{4}-\d{2}-\d{2})')]:

        league_info[key] = None
        match = re.search(match_string, text, re.IGNORECASE)
        if match:
            league_info[key] = match[1]
        else:
            raise KeyError(f"{key} is not found on the page")

    _set_odota_name(league_info)

    return None


print(_set_additional_league_info({'link': "https://liquipedia.net/dota2/The_International/2023"}))


def _get_league_info_from_main_page(site_piece: Tag) -> dict | None:
    info = {}
    match = re.search(r'((Tier|Qual)\s?\d)', site_piece.text, re.IGNORECASE)
    if not match:
        return None

    _, name, *_ = site_piece.find_all('a')

    info['tier'] = match[1]
    info['link'] = BASE_SITE + name.attrs['href']

    return info


def _get_leagues_info(soup: BeautifulSoup) -> list[dict]:
    leagues_list_ul = soup.find('ul', {'class': 'tournaments-list'})
    leagues_list = []
    for league_stage_name, league_ul in zip(['upcoming', 'ongoing', 'completed'], leagues_list_ul):
        for league_elem in league_ul.find_all('li'):
            league_info = _get_league_info_from_main_page(league_elem)
            if league_info:
                league_info['status'] = league_stage_name
                leagues_list.append(league_info)

    return leagues_list


def get_leagues(lowest_tier: int = 2, qualifications_allowed: bool = False):
    response = requests.get("https://liquipedia.net/dota2/Main_Page")
    soup = BeautifulSoup(response.content, features="lxml")
    leagues = _get_leagues_info(soup)
    filtered_leagues = []
    for league in leagues:
        tier = league['tier']
        tier_name, tier_number = tier[0:4], int(tier[-1])
        if tier_name.lower() == 'qual' and not qualifications_allowed:
            continue
        if tier_number > lowest_tier:
            continue

        _set_additional_league_info(league)

        filtered_leagues.append(league)

    return filtered_leagues

#
# lgs = get_leagues()
# for x in lgs:
#     print(x)
