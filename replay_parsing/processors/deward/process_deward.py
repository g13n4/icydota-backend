import re
from typing import List

import pandas as pd

from constants.calculation.game.calculation_type.deward import DewardCalculations
from modules.match_splitter import MatchSplitter
from modules.performance_data_processor import PerformanceDataProcessor


KILLED_WARDS = {
    'sen': (DewardCalculations.killed_sen, DewardCalculations.killed_sen_pm),
    'obs': (DewardCalculations.killed_obs, DewardCalculations.killed_obs_pm),

    ('sen', 'was_dewarded'): DewardCalculations.was_dewarded_sen,
    ('sen', 'was_dewarded_perc'): DewardCalculations.was_dewarded_perc_sen,

    ('obs', 'was_dewarded'): DewardCalculations.was_dewarded_obs,
    ('obs', 'was_dewarded_perc'): DewardCalculations.was_dewarded_perc_obs,
}


def process_deward_windows(
        df: pd.DataFrame,
        MS: MatchSplitter,
        players: List[dict],
        players_to_slot: dict,
        PDP: PerformanceDataProcessor,
) -> None:
    df['slotname'] = df['slot'].replace({x['slot']: x['hero_npc_name'] for x in players})
    df['killed'] = df['slotname'] != df['attackername']

    df['attackerslot'] = df['attackername'].replace(players_to_slot)

    deward_windows = MS.split_into_windows(df, use_index=False)

    for window_df in deward_windows:
        if window_df['exists']:
            grouped_wdf = window_df['df'].groupby(['slot', 'type'])['killed'].agg(['sum', 'count'])
            grouped_wdf['was_dewarded_perc'] = grouped_wdf['sum'] / grouped_wdf['count']
            grouped_wdf.rename({'count': 'was_dewarded'}, axis='columns', inplace=True)
            for name, item in grouped_wdf[['was_dewarded', 'was_dewarded_perc']].to_dict().items():
                for k, v in item.items():
                    slot, ward_type = k
                    ward_type = 'sen' if 'sen' in ward_type else 'obs'

                    calc_type = KILLED_WARDS[(ward_type, name)]
                    PDP.set_value(slot=slot, calculation=calc_type, window_index=window_df['index'], value=v)

    for window_df in deward_windows:
        if window_df['exists']:
            grouped_wdf = window_df['df'].groupby(['attackerslot', 'type'])['killed'].agg('sum').to_dict()
            for k, v in grouped_wdf.items():
                slot, ward_type = k
                ward_type = 'sen' if 'sen' in ward_type else 'obs'
                if not re.match(r'\d', str(slot)):  # the killer must be a hero
                    continue

                calc_type, calc_type_pm = KILLED_WARDS[ward_type]
                value_pm = v / window_df['minutes']

                PDP.set_value(slot=slot, calculation=calc_type, window_index=window_df['index'], value=v)
                PDP.set_value(slot=slot, calculation=calc_type_pm, window_index=window_df['index'], value=value_pm)
