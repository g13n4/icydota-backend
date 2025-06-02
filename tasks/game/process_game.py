import json
import os
import sys
import warnings
from pathlib import Path
from typing import Dict, List

from celery import shared_task
from celery.utils.log import get_task_logger
from sqlmodel import Session

from constants.performance.game_side import SidePerformance
from db import get_sync_db_session
from models import Player, Team, SidePerformanceData, PlayerGameData, Game, PositionApproximation
from models.game import Patch
from models.performance import PerformanceTotalData
from tasks.game.helpers import fix_odota_data
from tasks.game.manual_processing import check_for_manual_fix_inplace
from tasks.game.proces_game_replay import process_game_replay
from tasks.league.create_league import get_or_create_league
from utils import none_to_zero, get_or_create, get_positions_approximations
from utils.helpers import is_equals_to_zero


CURRENT_DIR = Path.cwd().absolute()
BASE_PATH = os.path.join(CURRENT_DIR, Path('./replays'))

assert Path(BASE_PATH).is_dir() == True

logger = get_task_logger(__name__)

if not sys.warnoptions:
    warnings.simplefilter("ignore")


def create_game_data_objs(
        totals: Dict[int, PerformanceTotalData]
) -> tuple[SidePerformanceData, SidePerformanceData]:
    dict_sides = {
        'sent': { 'first_blood_claimed': False },
        'dire': { 'first_blood_claimed': False },
    }

    for slot, PTD_item in totals.items():
        PTD_item_dict: dict = PTD_item.model_dump()
        this_side_name = 'sent' if slot < 5 else 'dire'
        this_side_dict = dict_sides[this_side_name]

        for field in SidePerformance.VALUES_NAMES:
            this_value = PTD_item_dict[field]

            if field in ['first_blood_claimed'] and this_value:
                this_side_dict[field] = True
            else:
                if field not in this_side_dict:
                    this_side_dict[field] = 0

                this_side_dict[field] += int(this_value)

    dict_sides['sent']['dire'] = False
    dict_sides['dire']['dire'] = True

    return SidePerformanceData(**dict_sides['sent']), SidePerformanceData(**dict_sides['dire'])


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
        team_obj = get_or_create(
            logger=logger,
            db_session=db_session,
            model_obj=Team,
            get_key=data['team_id'],
            object_data=dict(
                id=data['team_id'],
                name=data['name'],
                tag=data['tag'],
            )
        )

        obj_teams[key] = team_obj
        obj_teams[f'{key}_tag'] = data['tag']

    db_session.commit()
    return obj_teams


def process_players(db_session, players: List[dict]) -> Dict[int, Player]:
    players_dict: dict = { x: None for x in range(10) }

    for player in players:
        this_account_id = player['account_id']
        this_nickname = player['name']
        this_current_acc_name = player['personaname']

        this_name_to_use = this_nickname or this_current_acc_name or str(this_account_id)
        official_name = (this_nickname == this_name_to_use)

        player_obj = get_or_create(
            logger=logger,
            db_session=db_session,
            model_obj=Player,
            get_key=this_account_id,
            object_data=dict(
                nickname=this_name_to_use,
                account_id=this_account_id,
                official_name=official_name,
            )
        )

        if this_nickname and this_nickname != player_obj.nickname:
            player_obj.nickname = this_nickname
            db_session.add(player_obj)

        players_dict[player['player_slot']] = player_obj

    db_session.commit()

    return players_dict


@shared_task(name='process_game_data', retry=True, max_retries=2, default_retry_delay=120, ignore_result=True)
def process_game_data(match_id: int, league_id: int | None = None):
    logger.info(f'Process replay for {match_id}')

    db_session: Session = get_sync_db_session()

    game = db_session.get(Game, match_id)
    processed_counter = 1
    if game:
        logger.warning('Deleting already existing Game object')
        processed_counter = game.processed_counter + 1
        db_session.delete(game)
        db_session.commit()

    match_folder_path = Path(f'{BASE_PATH}/{match_id}/')
    json_path = Path(f'{BASE_PATH}/{match_id}/{match_id}.json')

    with open(json_path, "r") as match_json:
        game_data = json.load(match_json)

    patch_id = game_data['patch']
    patch_obj = db_session.get(Patch, patch_id)

    if patch_obj is None:
        patch_obj = Patch(
            id=patch_id,
            aggregation_allowed=True,
        )
    elif not patch_obj.aggregation_allowed:
        patch_obj.aggregation_allowed = True

    if not league_id:
        league_id = game_data['league']['leagueid']
    league_obj = get_or_create_league(league_id=league_id, db_session=db_session)

    fix_odota_data(game_data)

    teams_dict = process_teams(
        db_session,
        dire_data=game_data['dire_team'],
        radiant_data=game_data['radiant_team']
    )

    players_dict = process_players(db_session, game_data['players'])

    # META DATA
    match_meta_info = {
        "league_id": league_obj.id,
        "match_id": match_id,
        "patch_id": patch_id,

        "dire": teams_dict['dire'].id,
        "sent": teams_dict['radiant'].id,
    }

    # APPROXIMATION POSITIONS
    approx_pos: dict = get_positions_approximations(
        db_session=db_session,
        model=PositionApproximation,
        league_id=league_id
    )

    # INITIAL DATA CREATION
    player_data_dict = dict()
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
        this_facet: int = player_info.get('hero_variant', None)

        position_id: int = player_info['lane_role']
        this_position: int = approx_pos.get(players_dict[this_slot].account_id, position_id)

        PGD_obj = PlayerGameData(
            team_id=this_team.id,
            player_id=players_dict[this_slot].account_id,

            position_id=this_position,
            hero_id=this_hero,
            lane=player_info['lane'],
            is_roaming=player_info['is_roaming'],

            win=player_info['win'],
            dire=(not player_info['isRadiant']),

            rank=player_info['rank_tier'],
            apm=player_info['actions_per_min'],
            slot=this_slot,
            pings=player_info.get('pings', 0), )

        db_session.add(PGD_obj)

        hero_kills = none_to_zero(player_info['hero_kills'])
        deaths = none_to_zero(player_info['deaths'])
        assists = none_to_zero(player_info['assists'])
        PTD_obj = PerformanceTotalData(
            gold=none_to_zero(player_info['total_gold']),
            xp=none_to_zero(player_info['total_xp']),
            kills_per_min=none_to_zero(player_info.get('kills_per_min', None)),

            first_blood_claimed=none_to_zero(player_info.get('firstblood_claimed', 0)),

            kda=none_to_zero(player_info['kda']),

            neutral_kills=none_to_zero(player_info['neutral_kills']),
            tower_kills=none_to_zero(player_info['tower_kills']),
            courier_kills=none_to_zero(player_info['courier_kills']),

            lane_kills=none_to_zero(player_info['lane_kills']),
            hero_kills=hero_kills,
            deaths=deaths,
            assists=assists,
            observer_kills=none_to_zero(player_info['observer_kills']),
            sentry_kills=none_to_zero(player_info['sentry_kills']),
            roshan_kills=none_to_zero(player_info['roshan_kills']),
            runes_picked_up=none_to_zero(player_info['rune_pickups']),

            ancient_kills=none_to_zero(player_info['ancient_kills']),
            buyback_count=none_to_zero(player_info['buyback_count']),
            observer_uses=none_to_zero(player_info['observer_uses']),
            sentry_uses=none_to_zero(player_info['sentry_uses']),

            lane_efficiency=none_to_zero(player_info.get('lane_efficiency', None)),
            lane_efficiency_pct=none_to_zero(player_info.get('lane_efficiency_pct', None)),

            no_death=is_equals_to_zero(deaths, pseudo=True),
            no_kill=is_equals_to_zero(hero_kills, pseudo=True),
            no_assists=is_equals_to_zero(assists, pseudo=True),

            last_hits=none_to_zero(player_info['last_hits']),
            denies=none_to_zero(player_info['denies']),

            gold_per_min=none_to_zero(player_info['gold_per_min']),
            xp_per_min=none_to_zero(player_info['xp_per_min']),
            level=none_to_zero(player_info['level']),
            net_worth=none_to_zero(player_info['net_worth']),

            aghanims_scepter=none_to_zero(player_info['aghanims_scepter']),
            aghanims_shard=none_to_zero(player_info['aghanims_shard']),
            moonshard=none_to_zero(player_info['moonshard']),

            hero_damage=none_to_zero(player_info['hero_damage']),
            tower_damage=none_to_zero(player_info['tower_damage']),
            hero_healing=none_to_zero(player_info['hero_healing']),


            # use in aggregation
            win=int(player_info['win']),
            picked=1,
        )

        # FIX FOR BROKEN SQLMODEL Decimal field
        PTD_obj.kills_per_min = none_to_zero(player_info.get('kills_per_min', None))
        PTD_obj.kda = none_to_zero(player_info['kda'])

        db_session.add(PTD_obj)

        player_data = {
            'position': this_position,
            'position_id': this_position,
            'hero_id': this_hero,
            'facet_id': this_hero * 100 + this_facet,
            'player_id': players_dict[this_slot].account_id,
            'player_game_data': PGD_obj,
            'performance_total_data': PTD_obj,
        }

        check_for_manual_fix_inplace(game_id=match_id, data=player_data)
        player_data_dict[this_slot] = player_data

    # CREATING GAMEDATA OBJECTS
    game_data_sent_obj, game_data_dire_obj = create_game_data_objs(
        totals={ slot: player_data_dict[slot]['performance_total_data'] for slot in player_data_dict }
    )
    db_session.add(game_data_sent_obj)
    db_session.add(game_data_dire_obj)

    db_session.commit()

    # GAME OBJECT

    game_ibj = Game(
        id=match_id,

        processed_counter=processed_counter,

        league=league_obj,
        league_id=league_obj.id,
        name=f"{teams_dict['radiant'].name} vs {teams_dict['dire'].name}",

        patch_id=patch_obj.id,

        sent_team_id=teams_dict['radiant'].id,
        dire_team_id=teams_dict['dire'].id,
        dire_win=(not game_data['radiant_win']),

        sides_performance=[game_data_sent_obj, game_data_dire_obj],

        game_start_time=game_data['start_time'],
        duration=game_data['duration'],
        replay_url=game_data['replay_url'],
    )

    match_meta_info['game_obj'] = game_ibj

    db_session.add(game_ibj)

    # PARSING
    PGD_objs, additional_data = process_game_replay(
        db_session=db_session,
        match_info=match_meta_info,
        match_replay_folder_path=match_folder_path,
        additional_player_data=player_data_dict,
        logger=logger,
    )

    logger.info("Creating Game object...")

    game_ibj.players_game_data = PGD_objs
    game_ibj.average_roshan_window_time = additional_data['average_roshan_window_time']
    game_ibj.roshan_death = additional_data['roshan_death']
    game_ibj.first_ten_kills_dire = additional_data['first_ten_kills_dire']
    game_ibj.hero_death = additional_data['hero_death']
    game_ibj.dire_lost_first_tower = additional_data['dire_lost_first_tower']
    game_ibj.dire_building_status_id = additional_data['dire_building_status_id']
    game_ibj.sent_building_status_id = additional_data['sent_building_status_id']

    db_session.add(game_ibj)
    db_session.commit()
    db_session.close()
    logger.info("Parsing complete")
