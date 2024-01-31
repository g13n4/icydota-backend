import json
import os
from pathlib import Path
from typing import Dict, List

import requests
from celery.utils.log import get_task_logger
from sqlmodel import Session
from sqlmodel import select

from celery_app import celery_app
from db import get_sync_db_session
from models import Player, Team
from models import PlayerGameData, Game, PerformanceTotalData
from models import Position, Hero
from tasks.download_replay import get_match_replay
from tasks.proces_game_replay import process_game_replay
from tasks.process_game_helpers import fix_odota_data
from utils import get_all_sqlmodel_objs, none_to_zero, refresh_objects


CURRENT_DIR = Path.cwd().absolute()
BASE_PATH = os.path.join(CURRENT_DIR, Path('./replays'))

assert Path(BASE_PATH).is_dir() == True

logger = get_task_logger(__name__)


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
        team_q = db_session.execute(select(Team).where(Team.odota_id == data['team_id'])).first()
        if not team_q:
            team_obj = Team(
                odota_id=data['team_id'],
                name=data['name'],
                tag=data['tag'],
            )
            db_session.add(team_obj)
        else:
            team_obj = team_q[0]

        obj_teams[key] = team_obj

    db_session.commit()
    return obj_teams


def process_players(db_session, players: List[dict]) -> Dict[int, Player]:
    players_dict: dict = {x: None for x in range(10)}
    newly_created = list()

    for player in players:
        this_steam_id = player['account_id']
        this_nickname = player['name']
        this_current_acc_name = player['personaname']
        this_true_name_exists = True if this_nickname else False

        this_name_to_use = this_nickname if this_true_name_exists else this_current_acc_name

        player_q = db_session.execute(select(Player).where(Player.steam_id == this_steam_id)).first()
        if not player_q:
            player_obj = Player(
                nickname=this_name_to_use,
                steam_id=this_steam_id,
                official_name=this_true_name_exists,
            )
            db_session.add(player_obj)
            newly_created.append(player_obj)
        else:
            player_obj = player_q[0]

        players_dict[player['player_slot']] = player_obj

    db_session.commit()

    refresh_objects(db_session, newly_created)

    return players_dict


@celery_app.task
def process_game(match_id: int, league_id: int):
    logger.info('')
    db_session: Session = get_sync_db_session()

    match_folder_path = Path(f'{BASE_PATH}/{match_id}/')
    match_folder_path.mkdir(parents=True, exist_ok=True)

    match_json_path = match_folder_path.joinpath(f'{match_id}.json')
    if match_json_path.is_file():
        with open(match_json_path, "r") as match_json:
            game_data = json.load(match_json)
    else:
        r = requests.get(f'https://api.opendota.com/api/matches/{match_id}')
        game_data = r.json()

        with open(match_json_path, "w") as match_json:
            json.dump(game_data, match_json)

    fix_odota_data(game_data)

    teams_dict = process_teams(db_session,
                               dire_data=game_data['dire_team'],
                               radiant_data=game_data['radiant_team'])
    players_dict = process_players(db_session, game_data['players'])

    positions_all = get_all_sqlmodel_objs(db_session, Position)
    positions_dict: Dict[int, Position] = {x.number: x for x in positions_all}  # "lane_role": 3,

    heroes_all = get_all_sqlmodel_objs(db_session, Hero)
    heroes_dict: Dict[int, Hero] = {x.odota_id: x for x in heroes_all}  # "hero_id": 78,

    player_data_dict = dict()
    PTD_objs_dict = dict()
    PGD_objs_dict = dict()
    for approximated_slot, player_info in enumerate(game_data['players']):
        this_team = teams_dict['radiant'] if player_info['isRadiant'] else teams_dict['dire']
        this_hero: int = player_info['hero_id']
        this_slot: int = player_info['player_slot']
        this_position: int = player_info['lane_role']

        PGD_obj = PlayerGameData(
            team_id=this_team.id,
            player_id=players_dict[this_slot].id,

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
            'position': positions_dict[this_position].number,
            'position_id': positions_dict[this_position].id,
            'hero_id': heroes_dict[this_hero].id,
            'player_id': players_dict[this_slot].id,

        }

        PTD_obj = PerformanceTotalData(
            total_gold=player_info['total_gold'],
            total_xp=player_info['total_xp'],
            kills_per_min=none_to_zero(player_info.get('kills_per_min', None)),
            kda=none_to_zero(player_info['kda']),

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

        # FIX FOR BROKEN SQLMODEL Decimal field
        PTD_obj.kills_per_min = none_to_zero(player_info.get('kills_per_min', None))
        PTD_obj.kda = none_to_zero(player_info['kda'])

        db_session.add(PTD_obj)

        PTD_objs_dict[this_slot] = PTD_obj

    db_session.commit()

    replay_url = game_data.get('replay_url', None)
    if not game_data['replay_url']:
        replay_url = f"http://replay{game_data['cluster']}.valve.net/570/{match_id}_{game_data['replay_salt']}.dem.bz2"

    get_match_replay(match_id=match_id, url=replay_url, match_folder_path=match_folder_path)

    game_performance_objs, additional_data = process_game_replay(db_session=db_session,
                                                                 match_id=match_id,
                                                                 match_replay_folder_path=match_folder_path,
                                                                 PTD_objs_dict=PTD_objs_dict,
                                                                 additional_player_data=player_data_dict,
                                                                 logger=logger, )

    logger.info(f"Creating Game object...")
    PGD_objs = []
    for this_slot in range(10):
        PGD_obj = PGD_objs_dict[this_slot]
        GP_obj = game_performance_objs[this_slot]

        PGD_obj.performance = GP_obj
        db_session.add(PGD_obj)
        PGD_objs.append(PGD_obj)

    game = Game(
        match_id=match_id,

        league_id=league_id,

        patch=game_data['patch'],

        sent_team_id=teams_dict['radiant'].id,
        dire_team_id=teams_dict['dire'].id,
        dire_win=(not game_data['radiant_win']),

        players_data=PGD_objs,

        average_roshan_window_time=additional_data['average_roshan_window_time'],
        roshan_death=additional_data['roshan_death'],

        first_ten_kills_dire=additional_data['first_ten_kills_dire'],
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
    db_session.close()
    logger.info("Parsing complete")
