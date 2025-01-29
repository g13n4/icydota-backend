import pandas as pd

from modules import MatchAnalyser, MatchSplitter
from modules.performance_data_processor import PerformanceDataProcessor
from replay_parsing import process_interval_windows, process_pings_windows, process_damage_windows, process_xp_windows, \
    process_gold_windows, process_deward_windows, process_wards_windows


def set_processor_data(match: MatchAnalyser,
                       match_data: dict[str, pd.DataFrame],
                       MS: MatchSplitter,
                       PDP: PerformanceDataProcessor, ) -> None:
    process_interval_windows(match_data['interval'], MS, PDP)

    process_pings_windows(match_data['pings'], MS, PDP)

    process_wards_windows(match_data['wards'], MS, PDP)
    process_deward_windows(
        match_data['deward'],
        MS,
        PDP=PDP,
        players=match.get_players(),
        players_to_slot=match.players.get_name_slot_dict(),
    )

    process_damage_windows(match_data['damage'], MS, PDP=PDP, players=match.get_players(), )
    process_xp_windows(match_data['xp'], MS, PDP, players_to_slot=match.players.get_name_slot_dict(), )
    process_gold_windows(match_data['gold'], MS, PDP, players_to_slot=match.players.get_name_slot_dict(), )

    return None
