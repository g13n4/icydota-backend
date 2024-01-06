from typing import Dict, List, Tuple

import pandas as pd

from replay_parsing import MatchAnalyser, MatchSplitter, process_interval_windows, process_pings_windows, \
    process_wards_windows, process_deward_windows, process_damage_windows, \
    process_xp_windows, process_gold_windows, postprocess_data
from utils import get_both_slot_values, iterate_df, combine_slot_dicts, get_obj_from_list, get_all_sqlmodel_objs, \
    compare_total_performance
from ..models import PerformanceWindowData
from ..models import WindowPlayerComparisonType, PlayerGameInfo, InGamePosition, WindowComparisonType
from ..models import WindowStatsType, PlayerStatsInfo, WindowHeroComparisonType, PerformanceTotalData


def _get_window_objs(db_session) -> Tuple[List[WindowPlayerComparisonType], List[WindowStatsType],]:
    wpct = get_all_sqlmodel_objs(db_session, WindowPlayerComparisonType)
    wst = get_all_sqlmodel_objs(db_session, WindowStatsType)
    return wpct, wst


def _fill_pws(db_session,
              final_data: pd.DataFrame,
              wst: List[WindowStatsType],
              pgi_dict: Dict[int, PlayerGameInfo], ) -> Dict[int, List[PerformanceWindowData]]:
    window_data_by_slot = {x: [] for x in range(10)}

    for index, line in iterate_df(final_data, use_offset=False):
        data_name, slot_text = index
        wit_type, wi_name = data_name.split('|')
        _, slot_num = get_both_slot_values(slot_text)

        wst_obj = get_obj_from_list(wst, name=wit_type)

        pgi_obj = pgi_dict[slot_num]

        psi_obj = PlayerStatsInfo(
            slot=pgi_obj.slot,
            player_id=pgi_obj.player_id,
            hero_id=pgi_obj.hero_id,
            win_stats_type=wst_obj)

        db_session.add(psi_obj)

        ppws_obj = PerformanceWindowData(
            stats_info=psi_obj,

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

        window_data_by_slot[slot_num].append(ppws_obj)

    return window_data_by_slot


def _fill_comparison_pws(db_session,
                         comparison_data: List[dict],
                         pperformance_objs: Dict[int, PerformanceTotalData],
                         wst: List[WindowStatsType],
                         pgi_dict: Dict[int, PlayerGameInfo],
                         wpct: List[WindowPlayerComparisonType],
                         ) -> Tuple[Dict[int, List[PerformanceWindowData]], Dict[int, List[PerformanceTotalData]]]:
    window_data_by_slot = {x: [] for x in range(10)}
    window_total_data_by_slot = {x: [] for x in range(10)}
    igp = get_all_sqlmodel_objs(db_session, InGamePosition)

    for item in comparison_data:
        for index, line in iterate_df(item['df'], use_offset=False):
            comparandum_slot = line['slot_comparandum']
            comparandum_pos = line['position_comparandum']
            comparandum_obj = get_obj_from_list(igp, number=comparandum_pos)
            comparandum_pgi_obj = pgi_dict[comparandum_slot]
            comparandum_total_obj = pperformance_objs[comparandum_slot]

            comparans_slot = line['slot_comparans']
            comparans_pos = line['position_comparans']
            comparans_obj = get_obj_from_list(igp, number=comparans_pos)
            comparans_pgi_obj = pgi_dict[comparans_slot]
            comparans_total_obj = pperformance_objs[comparans_slot]

            w_type, w_name = line['index'].split('|')
            wst_obj = get_obj_from_list(wst, name=w_type)
            wpct_obj = get_obj_from_list(wpct, comparandum_id=comparandum_obj.id, comparans_id=comparans_obj.id)

            wplct = WindowPlayerComparisonType(
                comparandum_id=comparandum_pgi_obj.player_id,
                comparans_id=comparans_pgi_obj.player_id,
            )
            db_session.add(wplct)

            whct = WindowHeroComparisonType(
                comparandum_id=comparandum_pgi_obj.player_id,
                comparans_id=comparans_pgi_obj.player_id,
            )
            db_session.add(whct)

            wct = WindowComparisonType(
                position_ct=wpct_obj,
                player_ct=wplct,
                hero_ct=whct,

            )
            db_session.add(whct)

            psi_obj = PlayerStatsInfo(
                slot=comparandum_pgi_obj.slot,
                player_id=comparandum_pgi_obj.player_id,
                hero_id=comparandum_pgi_obj.hero_id,
                win_stats_type=wst_obj,
                is_comparison=True,
                comparison=wct)
            db_session.add(psi_obj)

            ppws_obj = PerformanceWindowData(
                stats_info=psi_obj,

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

            psi_obj = PlayerStatsInfo(
                slot=comparandum_pgi_obj.slot,
                player_id=comparandum_pgi_obj.player_id,
                hero_id=comparandum_pgi_obj.hero_id,
                is_total_stats=True,
                is_comparison=True,
                comparison=wct)
            db_session.add(psi_obj)

            ctp_obj = compare_total_performance(comparandum_total_obj,
                                                comparans_total_obj,
                                                PerformanceTotalData)
            ctp_obj.stats_info = psi_obj

            db_session.add(ctp_obj)

            window_total_data_by_slot[comparandum_slot].append(ctp_obj)

    return window_data_by_slot, window_total_data_by_slot


def pgr_main(db_session,
             match: MatchAnalyser,
             match_data: Dict[str, pd.DataFrame],
             MS: MatchSplitter,
             pperformance_objs: Dict[int, PerformanceTotalData],
             pgi_dict: Dict[int, PlayerGameInfo],
             ) -> Tuple[Dict[int, List[PerformanceWindowData]], Dict[int, List[PerformanceTotalData]]]:
    wpct, wst = _get_window_objs(db_session)

    interval = process_interval_windows(match_data['interval'], MS)

    pings = process_pings_windows(match_data['pings'], MS)

    wards = process_wards_windows(match_data['wards'], MS, )
    deward = process_deward_windows(match_data['deward'], MS,
                                    players=match.get_players(),
                                    players_to_slot=match.players.get_name_slot_dict())

    damage = process_damage_windows(match_data['damage'], MS, players=match.get_players())
    xp = process_xp_windows(match_data['xp'], MS, players_to_slot=match.players.get_name_slot_dict())
    gold = process_gold_windows(match_data['gold'], MS, players_to_slot=match.players.get_name_slot_dict())

    match_info = combine_slot_dicts(interval, pings, wards, deward, damage, xp, gold)
    filled_totals_data, comparison_data = postprocess_data(match_info, match.get_players_object())

    pwd_dict = _fill_pws(db_session=db_session,
                         final_data=filled_totals_data,
                         wst=wst,
                         pgi_dict=pgi_dict, )

    pwd_dict_comparison, ptd_dict_comparison = _fill_comparison_pws(db_session=db_session,
                                                                    comparison_data=comparison_data,
                                                                    pperformance_objs=pperformance_objs,
                                                                    wst=wst,
                                                                    wpct=wpct,
                                                                    pgi_dict=pgi_dict, )

    pwd_output = dict()
    for slot in range(10):
        pwd_output[slot] = pwd_dict[slot] + pwd_dict_comparison[slot]

    return pwd_output, ptd_dict_comparison
