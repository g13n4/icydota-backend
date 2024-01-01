from typing import Dict, List, Tuple

import pandas as pd

from replay_parsing import MatchAnalyser, MatchSplitter, process_interval_windows, \
    process_pings_windows, process_wards_windows, process_deward_windows, process_damage_windows, \
    process_xp_windows, process_gold_windows, postprocess_data
from utils import get_both_slot_values, iterate_df, combine_slot_dicts, get_obj_from_list, get_all_sqlmodel_objs
from ..models import PlayerPerformanceWindowStats
from ..models import WindowPlayerComparisonType, WindowInfoType, WindowInfo, WindowPlayer


def _get_window_objs(db_session) -> Tuple[List[WindowPlayerComparisonType], List[WindowInfoType], List[WindowInfo],]:
    wct = get_all_sqlmodel_objs(db_session, WindowPlayerComparisonType)
    wit = get_all_sqlmodel_objs(db_session, WindowInfoType)
    wi = get_all_sqlmodel_objs(db_session, WindowInfo)
    return wct, wit, wi


def _fill_ppws(db_session,
               final_data: pd.DataFrame,
               wit: List[WindowInfoType],
               wi: List[WindowInfo],
               wp_dict: Dict[int, WindowPlayer],
               window_data_objs: Dict[int, List[PlayerPerformanceWindowStats]], ):
    for index, line in iterate_df(final_data, use_offset=False):
        data_name, slot_text = index
        wit_type, wi_name = data_name.split('|')
        _, slot_num = get_both_slot_values(slot_text)

        wit_obj = get_obj_from_list(wit, name=wit_type)
        wi_obj = get_obj_from_list(wi, name=wi_name, info_type_id=wit_obj.id, comparison_id=None)
        wp_obj = wp_dict[slot_num]

        ppws_obj = PlayerPerformanceWindowStats(
            window_info_id=wi_obj.id,
            player_id=wp_obj.id,

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

        window_data_objs[slot_num].append(ppws_obj)


def _fill_comparison_ppws(db_session,
                          comparison_data: List[dict],
                          wit: List[WindowInfoType],
                          wi: List[WindowInfo],
                          wct: List[WindowPlayerComparisonType],
                          wp_dict: Dict[int, WindowPlayer],
                          window_data_objs: Dict[int, List[PlayerPerformanceWindowStats]], ):
    for item in comparison_data:
        for index, line in iterate_df(item['df'], use_offset=False):
            comparandum_slot = line['slot_comparandum']
            comparandum_pos = line['position_comparandum']

            comparans_slot = line['slot_comparans']
            comparans_pos = line['position_comparans']

            wit_type, wi_name = line['index'].split('|')
            wit_obj = get_obj_from_list(wit, name=wit_type)
            wct_obj = get_obj_from_list(wct, comparandum=comparandum_pos, comparans=comparans_pos)
            wi_obj = get_obj_from_list(wi, name=wi_name, info_type_id=wit_obj.id, comparison_id=wct_obj.id)

            wp_obj = wp_dict[comparandum_slot]
            comparans_obj = wp_dict[comparans_slot]

            ppws_obj = PlayerPerformanceWindowStats(
                window_info_id=wi_obj.id,
                player_id=wp_obj.id,
                comparans_id=comparans_obj.id,

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

            window_data_objs[comparandum_slot].append(ppws_obj)


def pgr_main(db_session,
             match: MatchAnalyser,
             match_data: Dict[str, pd.DataFrame],
             MS: MatchSplitter,
             wp_dict: Dict[int, WindowPlayer], ):
    wct, wit, wi = _get_window_objs(db_session)

    window_data_by_slot = {x: [] for x in range(10)}

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

    _fill_ppws(db_session=db_session,
               final_data=filled_totals_data,
               wit=wit,
               wi=wi,
               wp_dict=wp_dict,
               window_data_objs=window_data_by_slot)

    _fill_comparison_ppws(db_session=db_session,
                          comparison_data=comparison_data,
                          wct=wct,
                          wit=wit,
                          wi=wi,
                          wp_dict=wp_dict,
                          window_data_objs=window_data_by_slot)
