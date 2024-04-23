import re
from decimal import Decimal
from functools import partial, reduce
from typing import Dict, List

import pandas as pd

from models import PerformanceDataType, PerformanceTotalData, ComparisonType, \
    PerformanceWindowData, GamePerformance
from replay_parsing import MatchAnalyser, MatchSplitter, process_interval_windows, process_pings_windows, \
    process_wards_windows, process_deward_windows, process_damage_windows, TotalPerformanceAnalyser, \
    process_xp_windows, process_gold_windows, postprocess_data, MatchPlayersData
from utils import get_both_slot_values, combine_slot_dicts, get_obj_from_list, get_all_sqlmodel_objs, \
    to_dec
from parsing_utils.pd_helpers import iterate_df


def _get_PDT_objects(db_session,
                     column_to_category_obj: Dict[str, str], ) -> Dict[str, PerformanceDataType]:
    PDT_objs = get_all_sqlmodel_objs(db_session, PerformanceDataType, )
    PDT_dict = dict()
    for column_name, category_obj_name in column_to_category_obj.items():
        PDT_obj: PerformanceDataType = get_obj_from_list(PDT_objs, name=category_obj_name)
        if not PDT_obj.system_name:
            PDT_obj.system_name = column_name

        db_session.add(PDT_obj)
        PDT_dict[column_name] = PDT_obj
        PDT_dict[category_obj_name] = PDT_obj

    return PDT_dict


def _fill_basic_PWDs(db_session,
                     final_data: pd.DataFrame,
                     PDT_dict: Dict[str, PerformanceDataType],
                     PTD_dict: Dict[int, PerformanceTotalData],
                     model_fields: List[str],
                     ) -> Dict[int, GamePerformance]:
    window_data_by_slot = {x: [] for x in range(10)}

    for index, line in iterate_df(final_data, use_offset=False):
        data_name, slot_text = index
        wit_type, wi_name = data_name.split('|')
        _, slot_num = get_both_slot_values(slot_text)

        pwd_dict = {x: to_dec(line[x]) for x in model_fields}

        pwd_dict['data_type'] = PDT_dict[wi_name]

        pwd_obj = PerformanceWindowData(**pwd_dict)
        db_session.add(pwd_obj)

        window_data_by_slot[slot_num].append(pwd_obj)

    game_performance_objs_dict = dict()
    for slot_num, pwd_objs in window_data_by_slot.items():
        ptd_objs = PTD_dict[slot_num]

        game_performance_obj = GamePerformance(
            window_data=pwd_objs,
            total_data=[ptd_objs],
        )
        db_session.add(game_performance_obj)

        game_performance_objs_dict[slot_num] = game_performance_obj

    return game_performance_objs_dict


def _fill_comparison_pws(db_session,
                         comparison_data: List[dict],
                         PerfTotalData_dict: Dict[int, PerformanceTotalData],
                         players_data: MatchPlayersData,
                         PDT_dict: Dict[str, PerformanceDataType],
                         model_fields: List[str], ) -> Dict[int, List[GamePerformance]]:

    TPA = TotalPerformanceAnalyser(PerfTotalData_dict)
    # WINDOW DATA

    game_performance_objs = {x: [] for x in range(10)}
    # we iterate over list that contains two types of dfs: flat and perc comparisons
    for idx, item in enumerate(sorted(comparison_data, key=lambda x: not x['basic'])):  # We want to start with True's

        # iterate over these dfs one by one
        for df, flat_comparison in [(item['df_flat'], True), (item['df_percent'], False)]:

            window_objs = []
            # iterate over data in these dfs
            for index, line in iterate_df(df, use_offset=False):
                w_type, w_name = line['data'].split('|')

                pwd_dict = {x: to_dec(line[x]) for x in model_fields}
                data_type_obj = PDT_dict[w_name]

                pwd_dict['data_type'] = data_type_obj

                ppws_obj = PerformanceWindowData(**pwd_dict)

                db_session.add(ppws_obj)
                window_objs.append(ppws_obj)

            # TOTAL DATA
            comparandum_slot = item['slot_comparandum']
            comparandum_data = players_data[comparandum_slot]

            # NOT A COMBINATION
            if item['basic']:
                comparans_slot = item['slot_comparans']
                comparans_data = players_data[comparans_slot]

                CT_obj = ComparisonType(
                    flat=flat_comparison,
                    basic=True,

                    player_cpd_id=comparandum_data['player_id'],
                    player_cps_id=comparans_data['player_id'],

                    hero_cpd_id=comparandum_data['hero_id'],
                    hero_cps_id=comparans_data['hero_id'],

                    pos_cpd_id=comparandum_data['position_id'],
                    pos_cps_id=comparans_data['position_id'],
                )
                db_session.add(CT_obj)

                ctp_data = TPA.compare_to_one(comparandum_slot, comparans_slot, flat=flat_comparison)
            else:
                # COMBINATION OF SEVERAL DATA

                CT_obj = ComparisonType(
                    flat=flat_comparison,
                    basic=False,

                    player_cpd_id=comparandum_data['player_id'],
                    hero_cpd_id=comparandum_data['hero_id'],
                    pos_cpd_id=comparandum_data['position_id'],
                )
                db_session.add(CT_obj)

                opponents: List[int] = players_data[comparandum_slot]['opponents']
                ctp_data = TPA.compare_to_many(comparandum_slot, comparans_list=opponents, flat=flat_comparison)


            # FILLING GAME PERFORMANCE
            # CREATE A TOTAL DATA COMPARISON
            ctp_obj: PerformanceTotalData = PerformanceTotalData(**ctp_data)
            db_session.add(ctp_obj)

            game_performance_obj = GamePerformance(
                window_data=window_objs,
                total_data=[ctp_obj],
                is_comparison=True,
                comparison=CT_obj,
            )
            db_session.add(game_performance_obj)

            game_performance_objs[comparandum_slot].append(game_performance_obj)

    return game_performance_objs


def process_main_replay_data(db_session,
                             match: MatchAnalyser,
                             match_data: Dict[str, pd.DataFrame],
                             MS: MatchSplitter,
                             PerTotalData_dict: Dict[int, PerformanceTotalData],
                             ) -> Dict[int, List[GamePerformance]]:
    interval = process_interval_windows(match_data['interval'], MS)

    pings = process_pings_windows(match_data['pings'], MS)

    wards = process_wards_windows(match_data['wards'], MS)
    deward = process_deward_windows(match_data['deward'], MS,
                                    players=match.get_players(),
                                    players_to_slot=match.players.get_name_slot_dict(), )

    damage = process_damage_windows(match_data['damage'], MS, players=match.get_players(), )
    xp = process_xp_windows(match_data['xp'], MS, players_to_slot=match.players.get_name_slot_dict(), )
    gold = process_gold_windows(match_data['gold'], MS, players_to_slot=match.players.get_name_slot_dict(), )

    match_info = combine_slot_dicts(interval, pings, wards, deward, damage, xp, gold, )

    column_to_category_obj: Dict[str, str] = {x['_parsing_name']: x['_db_name'] for x in match_info['_0'].values()}
    PTD_dict = _get_PDT_objects(db_session, column_to_category_obj)

    filled_totals_data, comparison_data = postprocess_data(match_info, match.get_players_object(), MS, )

    # all fields in window data are Decimal's
    fields = [x for x in PerformanceWindowData.schema()['properties'].keys()
              if not re.search(r'(^|_)id$', x)]

    GP_basic_dict = _fill_basic_PWDs(db_session=db_session,
                                     final_data=filled_totals_data,
                                     PDT_dict=PTD_dict,
                                     PTD_dict=PerTotalData_dict,
                                     model_fields=fields)

    GP_comparison_dict = _fill_comparison_pws(db_session=db_session,
                                              comparison_data=comparison_data,
                                              players_data=match.players,
                                              PerfTotalData_dict=PerTotalData_dict,
                                              PDT_dict=PTD_dict,
                                              model_fields=fields)

    all_GPs = dict()
    for x in range(10):
        basic_gp = GP_basic_dict[x]
        comparison_gps = GP_comparison_dict[x]

        comparison_gps.append(basic_gp)
        all_GPs[x] = comparison_gps

    return all_GPs
