import json
import os
import sys
import warnings
from pathlib import Path
from typing import Dict, List

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session

from db import get_sync_db_session
from models import Hero
from models import Player, Team, GameData
from models import PlayerGameData, Game, PerformanceTotalData, PositionApproximation
from tasks.create_league import get_or_create_league
from tasks.proces_game_replay import process_game_replay
from tasks.process_game_helpers import fix_odota_data
from utils import get_all_sqlmodel_objs, none_to_zero, get_or_create, get_positions_approximations


CURRENT_DIR = Path.cwd().absolute()
BASE_PATH = os.path.join(CURRENT_DIR, Path('./replays'))

assert Path(BASE_PATH).is_dir() == True

logger = get_task_logger(__name__)

if not sys.warnoptions:
    warnings.simplefilter("ignore")


def create_game_data_objs(total_data: Dict[int, PerformanceTotalData]) -> tuple[GameData, GameData]:
    dict_sides = {
        'sent': {'first_blood_claimed': False},
        'dire': {'first_blood_claimed': False},
    }

    for slot, item in total_data.items():
        item_dict = item.dict()
        this_side_name = 'sent' if slot < 5 else 'dire'
        this_side_dict = dict_sides[this_side_name]

        for gdn, tn in [
            ('gold', 'total_gold'),
            ('xp', 'total_xp'),
            ('hero_kills', 'hero_kills'),
            ('kpm', 'kills_per_min'),

            ('roshan_kills', 'roshan_kills'),
            ('runes_picked_up', 'runes_picked_up'),

            ('obs_placed', 'observer_uses'),
            ('obs_kills', 'observer_kills'),

            ('sentry_placed', 'sentry_uses'),
            ('sentry_kills', 'sentry_kills'),

            ('first_blood_claimed', 'first_blood_claimed')
        ]:
            this_value = item_dict[tn]

            if gdn in ['first_blood_claimed'] and this_value:
                this_side_dict[gdn] = True
            else:
                if gdn not in this_side_dict:
                    this_side_dict[gdn] = 0

                this_side_dict[gdn] += int(this_value)

    return GameData(**dict_sides['sent']), GameData(**dict_sides['dire'])



def process_teams(db_session, dire_data: dict, radiant_data: dict) -> Dict[str, Team]:
    teams = {
        'radiant': radiant_data,
        'dire': dire_data,
    }

    obj_teams = {
        'radiant': None,
        'radiant_tag': None,

        'dire': None,
        'dire_tag': None,
    }

    for key, data in teams.items():
        team_obj = get_or_create(logger=logger,
                                 db_session=db_session,
                                 model_obj=Team,
                                 get_key=data['team_id'],
                                 object_data=dict(
                                     id=data['team_id'],
                                     name=data['name'],
                                     tag=data['tag'],
                                 ))

        obj_teams[key] = team_obj
        obj_teams[f'{key}_tag'] = data['tag']

    db_session.commit()
    return obj_teams


def process_players(db_session, players: List[dict]) -> Dict[int, Player]:
    players_dict: dict = {x: None for x in range(10)}

    for player in players:
        this_account_id = player['account_id']
        this_nickname = player['name']
        this_current_acc_name = player['personaname']

        this_name_to_use = this_nickname or this_current_acc_name or str(this_account_id)
        official_name = (this_nickname == this_name_to_use)

        player_obj = get_or_create(logger=logger,
                                   db_session=db_session,
                                   model_obj=Player,
                                   get_key=this_account_id,
                                   object_data=dict(
                                       nickname=this_name_to_use,
                                       account_id=this_account_id,
                                       official_name=official_name,
                                   ))

        if this_nickname and this_nickname != player_obj.nickname:
            player_obj.nickname = this_nickname
            db_session.add(player_obj)

        players_dict[player['player_slot']] = player_obj

    db_session.commit()

    return players_dict


@shared_task(name='process_game_data', ignore_result=True)
def process_game_data(match_id: int, league_id: int | None = None):
    logger.info(f'Process replay for {match_id}')

    db_session: Session = get_sync_db_session()

    game = db_session.get(Game, match_id)
    if game:
        logger.warning('Deleting already existing Game object')
        db_session.delete(game)
        db_session.commit()

    match_folder_path = Path(f'{BASE_PATH}/{match_id}/')
    json_path = Path(f'{BASE_PATH}/{match_id}/{match_id}.json')

    with open(json_path, "r") as match_json:
        game_data = json.load(match_json)

    if not league_id:
        league_id = game_data['league']['leagueid']
    league_obj = get_or_create_league(league_id=league_id, db_session=db_session)

    fix_odota_data(game_data)

    teams_dict = process_teams(db_session,
                               dire_data=game_data['dire_team'],
                               radiant_data=game_data['radiant_team'])

    players_dict = process_players(db_session, game_data['players'])

    # DATA POOLS
    heroes_all = get_all_sqlmodel_objs(db_session, Hero)
    heroes_dict: Dict[int, Hero] = {x.id: x for x in heroes_all}  # "hero_id": 78,

    # APPROXIMATION POSITIONS
    approx_pos: dict = get_positions_approximations(db_session=db_session,
                                                    model=PositionApproximation,
                                                    league_id=league_id)

    # INITIAL DATA CREATION
    player_data_dict = dict()
    PTD_objs_dict = dict()
    PGD_objs_dict = dict()
    for approximated_slot, player_info in enumerate(game_data['players']):
        is_radiant = player_info['isRadiant']
        this_team: Team = teams_dict['radiant'] if is_radiant else teams_dict['dire']

        # replacing bad tags
        this_team_tag = teams_dict['radiant_tag'] if is_radiant else teams_dict['dire_tag']
        if this_team.tag == '-' and this_team_tag != '-':
            this_team.tag = this_team_tag
            db_session.add(this_team)

        this_hero: int = player_info['hero_id']
        this_slot: int = player_info['player_slot']

        position_id: int = player_info['lane_role']
        this_position: int = approx_pos.get(players_dict[this_slot].account_id, position_id)

        PGD_obj = PlayerGameData(
            team_id=this_team.id,
            player_id=players_dict[this_slot].account_id,

            position_id=this_position,
            hero_id=heroes_dict[this_hero].id,
            lane=player_info['lane'],
            is_roaming=player_info['is_roaming'],

            win=player_info['win'],
            dire=(not player_info['isRadiant']),

            rank=player_info['rank_tier'],
            apm=player_info['actions_per_min'],
            slot=this_slot,
            pings=player_info.get('pings', 0), )

        PGD_objs_dict[this_slot] = PGD_obj

        db_session.add(PGD_obj)

        player_data_dict[this_slot] = {
            'position': this_position,
            'position_id': this_position,
            'hero_id': heroes_dict[this_hero].id,
            'player_id': players_dict[this_slot].account_id,

        }

        PTD_obj = PerformanceTotalData(
            total_gold=none_to_zero(player_info['total_gold']),
            total_xp=none_to_zero(player_info['total_xp']),
            kills_per_min=none_to_zero(player_info.get('kills_per_min', None)),

            first_blood_claimed=none_to_zero(player_info.get('firstblood_claimed', 0)),

            kda=none_to_zero(player_info['kda']),

            neutral_kills=none_to_zero(player_info['neutral_kills']),
            tower_kills=none_to_zero(player_info['tower_kills']),
            courier_kills=none_to_zero(player_info['courier_kills']),

            lane_kills=none_to_zero(player_info['lane_kills']),
            hero_kills=none_to_zero(player_info['hero_kills']),
            observer_kills=none_to_zero(player_info['observer_kills']),
            sentry_kills=none_to_zero(player_info['sentry_kills']),
            roshan_kills=none_to_zero(player_info['roshan_kills']),
            runes_picked_up=none_to_zero(player_info['rune_pickups']),

            ancient_kills=none_to_zero(player_info['ancient_kills']),
            buyback_count=none_to_zero(player_info['buyback_count']),
            observer_uses=none_to_zero(player_info['observer_uses']),
            sentry_uses=none_to_zero(player_info['sentry_uses']),

            lane_efficiency=none_to_zero(player_info.get('lane_efficiency', None), nullify=False),
            lane_efficiency_pct=none_to_zero(player_info.get('lane_efficiency_pct', None), nullify=False),
        )

        # FIX FOR BROKEN SQLMODEL Decimal field
        PTD_obj.kills_per_min = none_to_zero(player_info.get('kills_per_min', None))
        PTD_obj.kda = none_to_zero(player_info['kda'])

        db_session.add(PTD_obj)

        PTD_objs_dict[this_slot] = PTD_obj

    # CREATING GAMEDATA OBJECTS
    game_data_sent_obj, game_data_dire_obj = create_game_data_objs(PTD_objs_dict)
    db_session.add(game_data_sent_obj)
    db_session.add(game_data_dire_obj)

    db_session.commit()


    # PARSING
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
        GP_objs = game_performance_objs[this_slot]

        PGD_obj.performance = GP_objs
        db_session.add(PGD_obj)
        PGD_objs.append(PGD_obj)



    game = Game(
        id=match_id,

        league=league_obj,
        league_id=league_obj.id,
        name=f"{teams_dict['radiant'].name} vs {teams_dict['dire'].name}",

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

        sent_game_data_id=game_data_sent_obj.id,
        dire_game_data_id=game_data_dire_obj.id,

        game_start_time=game_data['start_time'],
        duration=game_data['duration'],
        replay_url=game_data['replay_url'],
    )

    db_session.add(game)
    db_session.commit()
    db_session.close()
    logger.info("Parsing complete")
