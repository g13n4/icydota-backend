import pandas as pd

from modules.match_analyser import MatchAnalyser
from modules.match_splitter import MatchSplitter
from modules.performance_data_processor import PerformanceDataProcessor
from replay_parsing.processors.damage import process_damage_windows
from replay_parsing.processors.deward import process_deward_windows
from replay_parsing.processors.gold import process_gold_windows
from replay_parsing.processors.interval.process_interval_windows import process_interval_windows
from replay_parsing.processors.pings import process_pings_windows
from replay_parsing.processors.wards import process_wards_windows
from replay_parsing.processors.xp import process_xp_windows
from replay_parsing.processors.postprocessing import postprocess_windows


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

    postprocess_windows(PDP=PDP)

    return None
