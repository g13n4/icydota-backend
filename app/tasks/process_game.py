import json
import os
from pathlib import Path
from typing import Dict, List

from sqlmodel import select

from utils import get_all_sqlmodel_objs
from .download_replay import get_match_replay
from .proces_game_replay import process_game_replay
from ..celery import celery_app
from ..models import Player, Team, League
from ..models import PlayerGameData, Game, PerformanceTotalData
from ..models import Position, Hero

CURRENT_DIR = Path.cwd().parent.parent.absolute()
BASE_PATH = os.path.join(CURRENT_DIR, Path('/replays'))

assert Path(BASE_PATH).is_dir() == True


def process_teams(db_session, dire_data: dict, radiant_data: dict) -> Dict[str, Team]:
    teams = {
        'radiant': radiant_data,
        'dire': dire_data,
    }

    obj_teams = {
        'radiant': None,
        'dire': None,
    }

    for key, data in teams.items():
        team_obj = db_session.execute(select(Team).where(Team.odota_id == data['team_id'])).first()
        if not team_obj:
            team_obj = Team(
                odota_id=data['team_id'],
                name=data['name'],
                tag=data['tag'],
            )
            db_session.add(team_obj)

        obj_teams[key] = team_obj

    db_session.commit()
    return obj_teams


def process_players(db_session, players: List[dict]) -> Dict[int, Player]:
    players_dict: dict = {x: None for x in range(10)}

    for player in players:
        player_obj = db_session.execute(select(Player).where(Player.steam_id == player['account_id'])).first()
        if not player_obj:
            player_obj = Player(
                nickname=player['name'],
                steam_id=player['account_id']
            )
            db_session.add(player_obj)

        players_dict[players_dict['player_slot']] = player_obj

    db_session.commit()
    return players_dict


@celery_app.task
def process_game(db_session, web_client, match_id: int, league_obj: League):
    match_folder_path = Path(f'{BASE_PATH}/{match_id}/')
    match_folder_path.mkdir(parents=True, exist_ok=True)

    match_json_path = match_folder_path.joinpath(f'{match_id}.json')
    if match_json_path.is_file():
        with open(match_json_path, "r") as match_json:
            game_data = json.load(match_json)
    else:
        r = web_client.get(f'https://api.opendota.com/api/matches/{match_id}')
        game_data = r.json()

        with open(match_json_path, "w") as match_json:
            json.dump(game_data, match_json)

    teams_dict = process_teams(db_session, game_data['dire_team'], game_data['radiant_team'])
    players_dict = process_players(db_session, game_data['players'])

    positions_all = get_all_sqlmodel_objs(db_session, Position)
    positions_dict = {x.number: x for x in positions_all}  # "lane_role": 3,

    heroes_all = get_all_sqlmodel_objs(db_session, Hero)
    heroes_dict = {x.odota_id: x for x in heroes_all}  # "hero_id": 78,

    player_data_dict = dict()
    PTD_objs_dict = dict()
    PGD_objs_dict = dict()
    for player_info in game_data['players']:
        this_team = teams_dict['radiant'] if player_info['isRadiant'] else teams_dict['dire']
        this_slot = player_info['player_slot']
        this_position = player_info['lane_role']
        this_hero = player_info['hero_id']

        PGD_obj = PlayerGameData(
            team_id=this_team.id,
            player_id=players_dict[this_slot].id,
            nickname=player_info['name'],

            position_id=positions_dict[this_position].id,
            hero_id=heroes_dict[this_hero].id,
            lane=player_info['lane'],
            is_roaming=player_info['is_roaming'],

            win=player_info['win'],
            dire=(not player_info['isRadiant']),

            rank=player_info['rank_tier'],
            apm=player_info['actions_per_min'],
            slot=this_slot,
            pings=player_info['pings'],

        )

        PGD_objs_dict[this_slot] = PGD_obj

        db_session.add(PGD_obj)

        player_data_dict[this_slot] = {
            'position': positions_dict[this_position].value,
            'position_id': positions_dict[this_position].id,
            'hero_id': heroes_dict[this_hero].id,
            'player_id': players_dict[this_slot].id,

        }

        PTD_obj = PerformanceTotalData(
            total_gold=player_info['total_gold'],
            total_xp=player_info['total_xp'],
            kills_per_min=player_info['benchmarks']['kills_per_min'],
            kda=player_info['kda'],

            neutral_kills=player_info['neutral_kills'],
            tower_kills=player_info['tower_kills'],
            courier_kills=player_info['courier_kills'],

            lane_kills=player_info['lane_kills'],
            hero_kills=player_info['hero_kills'],
            observer_kills=player_info['observer_kills'],
            sentry_kills=player_info['sentry_kills'],
            roshan_kills=player_info['roshan_kills'],
            runes_picked_up=player_info['rune_pickups'],

            ancient_kills=player_info['ancient_kills'],
            buyback_count=player_info['buyback_count'],
            observer_uses=player_info['observer_uses'],
            sentry_uses=player_info['sentry_uses'],

            lane_efficiency=player_info['lane_efficiency'],
            lane_efficiency_pct=player_info['lane_efficiency_pct'],

            # first_death_time fill later
            # first_kill_time fill later

            # first_blood_claimed=player_info['rune_pickups'],
            # died_first=player_info['rune_pickups'],
        )

        db_session.add(PTD_obj)

        PTD_objs_dict[this_slot] = PTD_obj

    db_session.commit()

    get_match_replay(match_id=match_id, )

    game_performance_objs, additional_data = process_game_replay(db_session=db_session,
                                                                 match_id=match_id,
                                                                 PTD_objs_dict=PTD_objs_dict,
                                                                 additional_player_data=player_data_dict)

    PGD_objs = []
    for this_slot in range(10):
        PGD_obj = PGD_objs_dict[this_slot]
        GP_obj = game_performance_objs[this_slot]

        PGD_obj.performance = GP_obj
        db_session.add(PGD_obj)
        PGD_objs.append(PGD_obj)

    game = Game(
        match_id=match_id,

        league=league_obj,

        patch=game_data['patch'],

        radiant_team_id=teams_dict['radiant'].id,
        dire_team_id=teams_dict['dire'].id,
        dire_win=(not game_data['radiant_win']),

        players_data=PGD_objs,

        average_roshan_window_time=additional_data['avg_rosh_death_time'],
        roshan_death=additional_data['roshan_death'],

        first_ten_kills_dire=additional_data['ftk_dire'],
        hero_death=additional_data['hero_death'],

        dire_lost_first_tower=additional_data['dire_lost_first_tower'],
        dire_building_status_id=additional_data['dire_building_status_id'],
        sent_building_status_id=additional_data['sent_building_status_id'],

        game_start_time=game_data['start_time'],
        duration=game_data['duration'],
        replay_url=game_data['replay_url'],
    )

    db_session.add(game)
    db_session.commit()
