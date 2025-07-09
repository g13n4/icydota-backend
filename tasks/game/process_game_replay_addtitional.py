from typing import Dict, List, Any

import pandas as pd

from models import HeroDeath, PerformanceTotalData, Building, BuildingDestroyed, BuildingNotDestroyed, RoshanDeath, \
    BuildingData
from modules.match_analyser import MatchPlayersData, MatchAnalyser
from modules.performance_data_processor import PerformanceDataProcessor
from replay_parsing.processors.buildings import process_building
from replay_parsing.processors.deaths import process_hero_deaths, process_roshan_deaths
from utils import get_all_sqlmodel_objs


NUM_TOWERS = 11  # 3 bot / 3 top / 3 mid / 2 throne
NUM_RAX = 6  # 2 bot / 2 top / 2 mid
NUM_BUILDINGS = NUM_RAX + NUM_RAX


def _fill_roshan_deaths(db_session, roshan_deaths: List[dict], ) -> List[RoshanDeath]:
    if not roshan_deaths:
        return []

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
        if hero_death['kill_slot']:  # There is a hero killer who killed
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

        else:  # the hero died from something else
            victim = MPD[hero_death['victim_slot']]

            hero_death_obj = HeroDeath(
                death_number=hero_death['death_number'],
                death_time=hero_death['death_time'],

                kill_dire=hero_death['kill_dire'],

                victim_dire=hero_death['victim_dire'],
                victim_hero_id=victim['hero_id'],
                victim_player_id=victim['player_id'], )

        hero_deaths_obj.append(hero_death_obj)
        db_session.add(hero_death_obj)

    return hero_deaths_obj


def _get_building_dict(db_session, ) -> dict:
    igb_objs: List[Building] = get_all_sqlmodel_objs(db_session, Building)
    igb_dict = dict()
    for igb_obj in igb_objs:
        if igb_obj.is_tower:
            if igb_obj.first_tower_4 is None:
                igb_dict[(1, igb_obj.lane, igb_obj.tier)] = igb_obj
            else:
                igb_dict[(1, igb_obj.first_tower_4, igb_obj.tier)] = igb_obj
        else:
            igb_dict[(0, igb_obj.lane, igb_obj.melee)] = igb_obj

    return igb_dict


def _get_pick_data(df: pd.DataFrame, pick_data: list | None = None) -> dict[int, int]:
    output = dict()
    # I have no idea why values are this way but they have to halved
    # It's the same for open dota and parsed replay (jsonl)
    # Ursa: id 70 - draft Id 140
    counter = 1
    if pick_data:
        for item in pick_data:
            if item["pick"]:
                hero_id = item["hero_id"] // 2
                output[hero_id] = counter
                counter += 1
        return output

    if df.empty:
        return output

    counter = 1
    df['hero_id'] = df['hero_id'] / 2
    df_filtered = df[df['pick'] == True]

    for idx, line in df_filtered.iterrows():
        values = line.to_dict()

        output[values["hero_id"]] = counter

        counter += 1
    return output


def _fill_building_kill(db_session, building_kill: Dict[str, list | dict], ) -> Dict[str, BuildingData]:
    igb_dict = _get_building_dict(db_session)
    output_dict = dict()
    for is_dire, side in [(True, 'dire'), (False, 'sentinel')]:
        bk_died_name = f'{side}_died'
        bk_died_data = building_kill[bk_died_name]
        bd_objs = []  # KeyError: (1, 2, 1)
        for bk in bk_died_data:
            b_obj = igb_dict[
                (int(bk['is_tower']),
                 (bk['lane']['value'] if bk['lane']['first_tower_4'] is None else bk['lane']['first_tower_4']),
                 bk['tower']['tier'])
            ]
            bk_obj = BuildingDestroyed(
                building_id=b_obj.id,
                death_time=bk['time'],

                destruction_order=bk['destruction_order'],
                destruction_order_tower=bk['tower']['destruction_order'],
                destruction_order_rax=bk['rax']['destruction_order'],

                # additional rax info
                destroyed_lane_1=bk['lanes_destroyed'][1],
                destroyed_lane_2=bk['lanes_destroyed'][2],
                destroyed_lane_3=bk['lanes_destroyed'][3],

                megacreeps=bk['megacreeps'],

                # additional tower info
                naked_throne=bk['naked_throne'],
            )

            db_session.add(bk_obj)
            bd_objs.append(bk_obj)

        bk_left_name = f'{side}_left'
        bk_left_data = building_kill[bk_left_name]

        bnk_obj = BuildingNotDestroyed(
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

        building_data_obj = BuildingData(
            dire=is_dire,

            destruction_order=bd_objs,

            destroyed_buildings=NUM_BUILDINGS - (bk_left_data['towers_left_total'] + bk_left_data['rax_left_total']),
            destroyed_towers=NUM_TOWERS - bk_left_data['towers_left_total'],
            destroyed_rax=NUM_RAX - bk_left_data['rax_left_total'],

            # additional rax info
            destroyed_lane_1=bd_objs[-1].destroyed_lane_1 if len(bd_objs) else False,
            destroyed_lane_2=bd_objs[-1].destroyed_lane_2 if len(bd_objs) else False,
            destroyed_lane_3=bd_objs[-1].destroyed_lane_3 if len(bd_objs) else False,

            megacreeps=bd_objs[-1].megacreeps if len(bd_objs) else False,

            # additional tower info
            naked_throne=bd_objs[-1].naked_throne if len(bd_objs) else False,

            not_destroyed=bnk_obj,
        )
        db_session.add(building_data_obj)

        output_dict[side] = building_data_obj

    return output_dict


def process_additional_replay_data(
        db_session,
        opendota_data: dict[str, Any],
        match: MatchAnalyser,
        match_data: Dict[str, pd.DataFrame],
        PDP: PerformanceDataProcessor,
        paring_options: dict[str, bool],
):
    avg_rosh_death_time, roshan_deaths = process_roshan_deaths(
        match_data['roshan_deaths'],
        players_to_slot=match.players.get_name_slot_dict(),
    )
    roshan_death_objs = _fill_roshan_deaths(db_session=db_session, roshan_deaths=roshan_deaths)

    player_data, ftk_dire, hero_deaths = process_hero_deaths(
        match_data['hero_deaths'],
        players_to_slot=match.players.get_name_slot_dict(),
    )
    hero_death_objs = _fill_hero_deaths(db_session=db_session, hero_deaths=hero_deaths, MPD=match.players)

    player_building, dire_lost_first_tower, building_kill = process_building(
        match_data['building_kill'],
        pos_to_slot=match.players.get_pos_to_slot_by_side(),
    )
    building_stats_objs = _fill_building_kill(db_session=db_session, building_kill=building_kill, )

    pick_dict = _get_pick_data(match_data['draft'], opendota_data.get("draft_timings", None))

    for player_slot in range(10):
        this_player_data = PDP.get_player_data(player_slot)
        this_total_perf_obj: PerformanceTotalData = this_player_data['performance_total_data']

        hero_death_player_data = player_data[player_slot]

        this_total_perf_obj.first_blood_claimed = hero_death_player_data['first_blood_claimed']
        this_total_perf_obj.first_kill_time = hero_death_player_data['first_kill_time']
        this_total_perf_obj.died_first = hero_death_player_data['died_first']
        this_total_perf_obj.died_first_time = hero_death_player_data['died_first_time']

        hero_building_data = player_building[player_slot]

        this_total_perf_obj.lost_tower_first = hero_building_data['lost_tower_first']
        this_total_perf_obj.lost_tower_lane = hero_building_data['lost_tower_lane']
        this_total_perf_obj.lost_tower_time = hero_building_data['lost_tower_time']

        this_total_perf_obj.destroyed_tower_first = hero_building_data['destroyed_tower_first']
        this_total_perf_obj.destroyed_tower_lane = hero_building_data['destroyed_tower_lane']
        this_total_perf_obj.destroyed_tower_time = hero_building_data['destroyed_tower_time']

        # first tower
        this_total_perf_obj.first_tower_destroyed_mid = hero_building_data['first_tower_destroyed_mid']
        this_total_perf_obj.first_tower_destroyed_top = hero_building_data['first_tower_destroyed_top']
        this_total_perf_obj.first_tower_destroyed_bot = hero_building_data['first_tower_destroyed_bot']

        this_total_perf_obj.first_tower_lost_mid = hero_building_data['first_tower_lost_mid']
        this_total_perf_obj.first_tower_lost_top = hero_building_data['first_tower_lost_top']
        this_total_perf_obj.first_tower_lost_bot = hero_building_data['first_tower_lost_bot']

        # lane
        this_total_perf_obj.first_tower_lane_destroyed_mid = hero_building_data['first_tower_lane_destroyed_mid']
        this_total_perf_obj.first_tower_lane_destroyed_top = hero_building_data['first_tower_lane_destroyed_top']
        this_total_perf_obj.first_tower_lane_destroyed_bot = hero_building_data['first_tower_lane_destroyed_bot']

        this_total_perf_obj.first_tower_lane_lost_mid = hero_building_data['first_tower_lane_lost_mid']
        this_total_perf_obj.first_tower_lane_lost_top = hero_building_data['first_tower_lane_lost_top']
        this_total_perf_obj.first_tower_lane_lost_bot = hero_building_data['first_tower_lane_lost_bot']

        # rax
        this_total_perf_obj.first_barracks_set_destroyed_mid = hero_building_data['first_barracks_set_destroyed_mid']
        this_total_perf_obj.first_barracks_set_destroyed_top = hero_building_data['first_barracks_set_destroyed_top']
        this_total_perf_obj.first_barracks_set_destroyed_bot = hero_building_data['first_barracks_set_destroyed_bot']

        this_total_perf_obj.first_barracks_set_lost_mid = hero_building_data['first_barracks_set_lost_mid']
        this_total_perf_obj.first_barracks_set_lost_top = hero_building_data['first_barracks_set_lost_top']
        this_total_perf_obj.first_barracks_set_lost_bot = hero_building_data['first_barracks_set_lost_bot']

        hero_id = this_player_data['hero_id']
        position_id = this_player_data['position_id']

        is_dire = this_player_data['slot'] > 4
        is_sent = this_player_data['slot'] < 5

        first_pick = pick_dict.get(hero_id, None) == 1
        last_pick = pick_dict.get(hero_id, None) == 10

        win = this_total_perf_obj.win == True
        lose = this_total_perf_obj.win == False

        this_total_perf_obj.win_dire = int(win and is_dire)
        this_total_perf_obj.win_sent = int(win and is_sent)

        this_total_perf_obj.first_pick_win = int(first_pick and win)
        this_total_perf_obj.first_pick_lose = int(first_pick and lose)

        this_total_perf_obj.last_pick_win = int(last_pick and win)
        this_total_perf_obj.last_pick_lose = int(last_pick and lose)

        this_total_perf_obj.first_pick_hero = int(first_pick)
        this_total_perf_obj.last_pick_hero = int(last_pick)

        has_megas = building_stats_objs['dire'].megacreeps if is_dire else building_stats_objs['sentinel'].megacreeps
        opponent_has_megas = building_stats_objs['sentinel'].megacreeps if is_dire else building_stats_objs[
            'dire'].megacreeps

        this_total_perf_obj.win_with_megas = int(has_megas and win)
        this_total_perf_obj.lose_with_megas = int(has_megas and lose)

        this_total_perf_obj.win_and_opponent_with_megas = int(opponent_has_megas and win)
        this_total_perf_obj.lose_and_opponent_with_megas = int(opponent_has_megas and lose)

        for x in range(1, 6):
            attrib_name = f"first_pick_pos_{x}"
            value = int(first_pick and position_id == x)
            setattr(this_total_perf_obj, attrib_name, value)

        db_session.add(this_total_perf_obj)

    return dict(
        average_roshan_window_time=avg_rosh_death_time,
        roshan_death=roshan_death_objs,

        first_ten_kills_dire=ftk_dire,
        hero_death=hero_death_objs,

        dire_lost_first_tower=dire_lost_first_tower,

        dire_building_status=building_stats_objs['dire'],
        sent_building_status=building_stats_objs['sentinel'],
    )
