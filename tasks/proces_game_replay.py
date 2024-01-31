import os
import pathlib
from logging import Logger
from pathlib import Path
from typing import Dict, Any, Tuple

from models import PerformanceTotalData, GamePerformance
from replay_parsing import MatchAnalyser, MatchSplitter
from tasks.process_game_replay_addtitional import process_additional_replay_data
from tasks.process_game_replay_main import process_main_replay_data


CURRENT_DIR = Path.cwd().parent.parent.absolute()


def process_game_replay(db_session,
                        match_id: int,
                        match_replay_folder_path: Path,
                        PTD_objs_dict: Dict[int, PerformanceTotalData],
                        additional_player_data: Dict[int, Dict[str, Any]],
                        logger: Logger,
                        ) -> Tuple[Dict[int, GamePerformance], Dict[str, Any]]:
    logger.info('Parsing raw replay data')
    match_path = os.path.join(match_replay_folder_path, Path(f'./{match_id}.jsonl'))

    # MATCH PARSING
    match = MatchAnalyser(pathlib.Path(match_path))
    match_data = match.get_match_data()
    match.get_players_object().set_player_data_from_dict(additional_player_data)

    MS = MatchSplitter(game_length=match.game_length, match_windows=match.match_windows)

    logger.info('Processing additional data')
    additional_data = process_additional_replay_data(db_session=db_session, match=match, match_data=match_data,
                                                     ptd_dict=PTD_objs_dict)

    logger.info('Processing main replay data')
    GP_objs_dict = process_main_replay_data(db_session=db_session, match=match, match_data=match_data, MS=MS,
                                            PerTotalData_dict=PTD_objs_dict)

    return (GP_objs_dict, additional_data)
