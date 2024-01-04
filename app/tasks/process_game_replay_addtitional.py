from typing import Dict, List

import pandas as pd

from replay_parsing import MatchAnalyser, MatchPlayersData, \
    process_building, process_hero_deaths, process_roshan_deaths
from utils import get_all_sqlmodel_objs
from ..models import AdditionalGameData, PerformanceTotalStats, Game
from ..models import HeroDeath
from ..models import InGameBuilding, InGameBuildingDestroyed, \
    InGameBuildingNotDestroyed
from ..models import RoshanDeath, BuildingStats

NUM_TOWERS = 11  # 3 bot / 3 top / 3 mid / 2 throne
NUM_RAX = 6  # 2 bot / 2 top / 2 mid
NUM_BUILDINGS = NUM_RAX + NUM_RAX


def _fill_roshan_deaths(db_session, roshan_deaths: List[dict], ) -> List[RoshanDeath]:
    roshan_objs = []
    for rosh_death in roshan_deaths:
        rd_obj = RoshanDeath(
            death_number=rosh_death['death_number'],
            death_time=rosh_death['death_time'],
            kill_dire=rosh_death['kill_dire'], )

        db_session.add(rd_obj)
        roshan_objs.append(rd_obj)
    return roshan_objs


def _fill_hero_deaths(db_session, hero_deaths: List[dict], MPD: MatchPlayersData) -> List[HeroDeath]:
    hero_deaths_obj = []
    for hero_death in hero_deaths:
        killer = MPD[hero_death['kill_slot']]
        victim = MPD[hero_death['victim_slot']]

        hero_death_obj = HeroDeath(
            death_number=hero_death['death_number'],
            death_time=hero_death['death_time'],

            kill_dire=hero_death['kill_dire'],
            killer_hero_id=killer['hero_id'],
            killer_player_id=killer['player_id'],

            victim_dire=hero_death['victim_dire'],
            victim_hero_id=victim['hero_id'],
            victim_player_id=victim['player_id'], )

        db_session.add(hero_death_obj)
        hero_deaths_obj.append(hero_death_obj)

    return hero_deaths_obj


def _get_building_dict(db_session, ) -> dict:
    igb_objs: List[InGameBuilding] = get_all_sqlmodel_objs(db_session, InGameBuilding)
    igb_dict = dict()
    for igb_obj in igb_objs:
        if igb_obj.is_tower:
            if igb_obj.tower4 is not None:
                igb_dict[(1, igb_obj.lane, igb_obj.tier)] = igb_obj
            else:
                igb_dict[(1, igb_obj.tower4, igb_obj.tier)] = igb_obj
        else:
            igb_dict[(0, igb_obj.lane, igb_obj.melee)] = igb_obj

    return igb_dict


def _fill_building_kill(db_session, building_kill: Dict[str, list | dict], ) -> Dict[str, BuildingStats]:
    igb_dict = _get_building_dict(db_session)
    output_dict = dict()
    for is_dire, side in [(True, 'dire'), (False, 'sentinel')]:
        bk_died_name = f'{side}_died'
        bk_died_data = building_kill[bk_died_name]
        bd_objs = []
        for bk in bk_died_data:
            b_obj = igb_dict[(bk['is_tower'],
                              (bk['lane']['value'] if bk['lane']['tower4'] is None else bk['lane']['tower4']),
                              bk['tower']['tier'])]
            bk_obj = InGameBuildingDestroyed(
                building_id=b_obj.id,
                death_time=bk['time'],

                destruction_order=bk['destruction_order'],
                destruction_order_tower=bk['tower']['destruction_order'],
                destruction_order_rax=bk['rax']['destruction_order'],

                # additional rax info
                destroyed_lane_one=bk['lanes_destroyed'][1],
                destroyed_lane_two=bk['lanes_destroyed'][2],
                destroyed_lane_three=bk['lanes_destroyed'][3],

                megacreeps=bk['megacreeps'],

                # additional tower info
                naked_throne=bk['naked_throne'], )

            db_session.add(bk_obj)
            bd_objs.append(bk_obj)

        bk_left_name = f'{side}_left'
        bk_left_data = building_kill[bk_left_name]

        bnk_obj = InGameBuildingNotDestroyed(
            towers_left_top=bk_left_data['towers_left_top'],
            towers_left_mid=bk_left_data['towers_left_mid'],
            towers_left_bottom=bk_left_data['towers_left_bottom'],
            towers_left_throne=bk_left_data['towers_left_throne'],

            towers_left_total=bk_left_data['towers_left_total'],

            rax_left_top=bk_left_data['rax_left_top'],
            rax_left_mid=bk_left_data['rax_left_mid'],
            rax_left_bottom=bk_left_data['rax_left_bottom'],

            rax_left_total=bk_left_data['rax_left_total'], )
        db_session.add(bnk_obj)

        bs = BuildingStats(
            dire=is_dire,

            buildings_destroyed=bd_objs,

            destroyed_buildings=NUM_BUILDINGS - (bk_left_data['towers_left_total'] + bk_left_data['rax_left_total']),
            destroyed_towers=NUM_TOWERS - bk_left_data['towers_left_total'],
            destroyed_rax=NUM_RAX - bk_left_data['rax_left_total'],

            # additional rax info
            destroyed_lane_1=bd_objs[-1].destroyed_lane_1,
            destroyed_lane_2=bd_objs[-1].destroyed_lane_2,
            destroyed_lane_3=bd_objs[-1].destroyed_lane_3,

            megacreeps=bd_objs[-1].megacreeps,

            # additional tower info
            naked_throne=bd_objs[-1].naked_throne,

            buildings_not_destroyed=bnk_obj, )
        db_session.add(bs)

        output_dict[side] = bs

    return output_dict


def pgr_additional(db_session,
                   match: MatchAnalyser,
                   match_data: Dict[str, pd.DataFrame],
                   pperformance_objs: Dict[int, PerformanceTotalStats],
                   game_obj: Game, ) -> AdditionalGameData:
    avg_rosh_death_time, roshan_deaths = process_roshan_deaths(match_data['roshan_deaths'],
                                                               players_to_slot=match.players.get_name_slot_dict())
    roshan_death_objs = _fill_roshan_deaths(db_session=db_session, roshan_deaths=roshan_deaths)

    player_data, ftk_dire, hero_deaths = process_hero_deaths(match_data['hero_deaths'],
                                                             players_to_slot=match.players.get_name_slot_dict())
    hero_death_objs = _fill_hero_deaths(db_session=db_session, hero_deaths=hero_deaths, MPD=match.players)

    player_building, building_kill = process_building(match_data['building_kill'],
                                                      pos_to_slot=match.players.get_pos_to_slot_by_side())
    building_stats_objs = _fill_building_kill(db_session=db_session, building_kill=building_kill, )

    for player_slot in range(10):
        this_pperf_obj = pperformance_objs[player_slot]

        hero_death_player_data = player_data[player_slot]

        this_pperf_obj.first_blood_claimed = hero_death_player_data['first_blood_claimed']
        this_pperf_obj.first_kill_time = hero_death_player_data['first_kill_time']
        this_pperf_obj.died_first = hero_death_player_data['died_first']
        this_pperf_obj.first_death_time = hero_death_player_data['first_death_time']

        hero_building_data = player_building[player_slot]

        this_pperf_obj.lost_tower_first = hero_building_data['lost_tower_first']
        this_pperf_obj.lost_tower_lane = hero_building_data['lost_tower_lane']
        this_pperf_obj.lost_tower_time = hero_building_data['lost_tower_time']

        this_pperf_obj.destroyed_tower_first = hero_building_data['destroyed_tower_first']
        this_pperf_obj.destroyed_tower_lane = hero_building_data['destroyed_tower_lane']
        this_pperf_obj.destroyed_tower_time = hero_building_data['destroyed_tower_time']

        db_session.add(this_pperf_obj)

    db_session.refresh(building_stats_objs['dire'])
    db_session.refresh(building_stats_objs['sentinel'])

    agd = AdditionalGameData(
        league_id=game_obj.league_id,
        game_id=game_obj.id,

        average_roshan_window_time=avg_rosh_death_time,
        roshan_death=roshan_death_objs,

        first_ten_kills_dire=ftk_dire,
        hero_death=hero_death_objs,

        dire_building_status_id=building_stats_objs['dire'].id,
        sent_building_status_id=building_stats_objs['sent'].id, )

    db_session.add(agd)

    return agd
