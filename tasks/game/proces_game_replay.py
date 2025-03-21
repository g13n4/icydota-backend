import os
import pathlib
from logging import Logger
from pathlib import Path
from typing import Dict, Any, Tuple, List

from models import PerformanceTotalData, GamePerformance, PlayerGameData
from modules import MatchAnalyser, MatchSplitter
from modules.performance_data_processor import PerformanceDataProcessor
from tasks.game.process_game_replay_addtitional import process_additional_replay_data
from tasks.game.process_game_replay_main import set_processor_data


CURRENT_DIR = Path.cwd().parent.parent.absolute()


def process_game_replay(db_session,
                        match_id: int,
                        match_replay_folder_path: Path,
                        additional_player_data: Dict[int, Dict[str, Any]],
                        logger: Logger,
                        ) -> Tuple[list[PlayerGameData], Dict[str, Any]]:
    logger.info('Parsing raw replay windows_data')
    match_path = os.path.join(match_replay_folder_path, Path(f'./{match_id}.jsonl'))

    # MATCH PARSING
    match = MatchAnalyser(pathlib.Path(match_path), match_id=match_id)
    match_data = match.get_match_data()
    match.players.set_player_data_from_dict(additional_player_data)
    PDP = PerformanceDataProcessor(
        db_session=db_session,
        players_data=match.players,
    )

    MS = MatchSplitter(game_length=match.game_length, match_windows=match.match_windows)

    logger.info('Processing additional windows_data')
    additional_data = process_additional_replay_data(
        db_session=db_session,
        match=match,
        match_data=match_data,
        PDP=PDP,
    )

    logger.info('Processing main replay windows_data')
    set_processor_data(
        match=match,
        match_data=match_data,
        MS=MS,
        PDP=PDP,
    )

    PDP.process_game_data()
    PDP.process_side_data()



    return (PDP.get_all_player_game_data(), additional_data)
