from typing import Dict, List, Tuple

import pandas as pd

from replay_parsing import MatchAnalyser, MatchSplitter, process_interval_windows, process_pings_windows, \
    process_wards_windows, process_deward_windows, process_damage_windows, \
    process_xp_windows, process_gold_windows, postprocess_data, MatchPlayersData
from utils import get_both_slot_values, iterate_df, combine_slot_dicts, get_obj_from_list, get_all_sqlmodel_objs, \
    compare_total_performance
from ..models import PerformanceDataType, PerformanceDataDescription, PerformanceTotalData, ComparisonType, \
    Position, PerformanceWindowData, PerformanceDataCategory, GamePerformance


def _get_window_objs(db_session, ) -> Tuple[List[ComparisonType], List[PerformanceDataCategory],]:
    CT_objs = get_all_sqlmodel_objs(db_session, ComparisonType)
    PDC_objs = get_all_sqlmodel_objs(db_session, PerformanceDataCategory)
    return CT_objs, PDC_objs


def _get_PDT_objects(db_session,
                     PDC_objs: List[PerformanceDataCategory],
                     column_to_db_name: Dict[str, str], ) -> Dict[str, PerformanceDataType]:
    PDT_objs = get_all_sqlmodel_objs(db_session, PerformanceDataType, )
    PDT_dict = dict()
    if not PDT_objs:
        for column_name, db_name in column_to_db_name.items():
            category, short_name = column_name.split('|')
            PDC_obj: PerformanceDataCategory = get_obj_from_list(PDC_objs, name=category)
            PDT_obj = PerformanceDataType(
                name=db_name,
                data_category=PDC_obj, )

            db_session.add(PDT_obj)

            PDT_dict[column_name] = PDT_obj
            PDT_dict[short_name] = PDT_obj

        db_session.commit()
    else:
        for column_name, db_name in column_to_db_name.items():
            category, short_name = column_name.split('|')
            PDT_obj: PerformanceDataType = get_obj_from_list(PDT_objs, name=db_name)

            PDT_dict[column_name] = PDT_obj
            PDT_dict[short_name] = PDT_obj

    return PDT_dict


def _fill_PWDs(db_session,
               final_data: pd.DataFrame,
               PDT_dict: Dict[str, PerformanceDataType], ) -> Dict[int, List[PerformanceWindowData]]:
    window_data_by_slot = {x: [] for x in range(10)}

    for index, line in iterate_df(final_data, use_offset=False):
        data_name, slot_text = index
        wit_type, wi_name = data_name.split('|')
        _, slot_num = get_both_slot_values(slot_text)

        pdt_obj = PDT_dict[data_name]
        db_session.refresh(pdt_obj)

        psi_obj = PerformanceDataDescription(data_type_id=pdt_obj.id, )

        db_session.add(psi_obj)

        PWD_obj = PerformanceWindowData(
            data_info=psi_obj,

            l2=line['l2'],
            l4=line['l4'],
            l6=line['l6'],
            l8=line['l8'],
            l10=line['l10'],
            ltotal=line['ltotal'],

            g15=line['g15'],
            g30=line['g30'],
            g45=line['g45'],
            g60=line['g60'],
            g60plus=line['g60plus'],
            gtotal=line['gtotal'],
        )
        db_session.add(PWD_obj)

        window_data_by_slot[slot_num].append(PWD_obj)

    return window_data_by_slot


def _fill_comparison_pws(db_session,
                         comparison_data: List[dict],
                         PerfTotalData_dict: Dict[int, PerformanceTotalData],
                         players_data: MatchPlayersData,
                         PDT_dict: Dict[str, PerformanceDataType],
                         ) -> Tuple[Dict[int, List[PerformanceWindowData]], Dict[int, List[PerformanceTotalData]]]:
    window_data_by_slot = {x: [] for x in range(10)}
    window_total_data_by_slot = {x: [] for x in range(10)}
    position_objs = get_all_sqlmodel_objs(db_session, Position)

    for item in comparison_data:
        for index, line in iterate_df(item['df'], use_offset=False):
            comparandum_slot = line['slot_comparandum']
            comparandum_data = players_data[comparandum_slot]

            comparans_slot = line['slot_comparans']
            comparans_data = players_data[comparans_slot]

            w_type, w_name = line['index'].split('|')

            CT_obj = ComparisonType(
                player_cpd_id=comparandum_data['player_id'],
                player_cps_id=comparans_data['player_id'],

                hero_cpd_id=comparandum_data['hero_id'],
                hero_cps_id=comparans_data['hero_id'],

                pos_cpd_id=comparandum_data['position_id'],
                pos_cps_id=comparans_data['position_id'],
            )
            db_session.add(CT_obj)

            PDT_obj = PDT_dict[w_name]

            PDD_W_obj = PerformanceDataDescription(
                data_type_id=PDT_obj.id,
                is_comparison=True,
                comparison=CT_obj)
            db_session.add(PDD_W_obj)

            ppws_obj = PerformanceWindowData(
                data_info=PDD_W_obj,

                l2=line['l2'],
                l4=line['l4'],
                l6=line['l6'],
                l8=line['l8'],
                l10=line['l10'],
                ltotal=line['ltotal'],

                g15=line['g15'],
                g30=line['g30'],
                g45=line['g45'],
                g60=line['g60'],
                g60plus=line['g60plus'],
                gtotal=line['gtotal'],
            )
            db_session.add(ppws_obj)

            window_data_by_slot[comparandum_slot].append(ppws_obj)

            comparandum_total_obj = PerfTotalData_dict[comparandum_slot]
            comparans_total_obj = PerfTotalData_dict[comparans_slot]

            PDD_T_obj = PerformanceDataDescription(
                is_total_stats=True,
                is_comparison=True,
                comparison=CT_obj)
            db_session.add(PDD_T_obj)

            ctp_obj = compare_total_performance(comparandum_total_obj,
                                                comparans_total_obj,
                                                PerformanceTotalData)
            ctp_obj.stats_info = PDD_T_obj

            db_session.add(ctp_obj)

            window_total_data_by_slot[comparandum_slot].append(ctp_obj)

    return window_data_by_slot, window_total_data_by_slot


def main_data(db_session,
              match: MatchAnalyser,
              match_data: Dict[str, pd.DataFrame],
              MS: MatchSplitter,
              PerTotalData_dict: Dict[int, PerformanceTotalData], ) -> Dict[int, GamePerformance]:
    CT_objs, PDC_objs = _get_window_objs(db_session)

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

    column_to_db_name: Dict[str, str] = {x['_parsing_name']: x['_db_name'] for x in match_info['_0']}
    PTD_dict = _get_PDT_objects(db_session, PDC_objs, column_to_db_name)

    filled_totals_data, comparison_data = postprocess_data(match_info, match.get_players_object(), )

    PWD_dict = _fill_PWDs(db_session=db_session, final_data=filled_totals_data, PDT_dict=PTD_dict, )

    PWData_comp_dict, PTData_comp_dict = _fill_comparison_pws(db_session=db_session,
                                                              comparison_data=comparison_data,
                                                              players_data=match.players,
                                                              PerfTotalData_dict=PerTotalData_dict,
                                                              PDT_dict=PTD_dict, )

    GP_output = dict()
    for slot in range(10):
        GP = GamePerformance(
            window_data=PWD_dict[slot] + PWData_comp_dict[slot],
            total_data=PTData_comp_dict[slot] + [PerTotalData_dict[slot]], )

        db_session.add(GP)
        GP_output[slot] = GP

    return GP_output
