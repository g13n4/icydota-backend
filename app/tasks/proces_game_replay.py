import os
import pathlib
from pathlib import Path
from typing import Dict, Any, Tuple

from replay_parsing import MatchAnalyser, MatchSplitter
from .process_game_replay_addtitional import process_additional_data
from .process_game_replay_main import main_data
from ..models import PerformanceTotalData, GamePerformance

CURRENT_DIR = Path.cwd().parent.parent.absolute()


def process_game_replay(db_session,
                        match_id: int,
                        PTD_objs_dict: Dict[int, PerformanceTotalData],
                        additional_player_data: Dict[int, Dict[str, Any]],
                        ) -> Tuple[Dict[int, GamePerformance], Dict[str, Any]]:
    match_path = os.path.join(CURRENT_DIR, Path(f'./replays/{match_id}/{match_id}.jsonl'))

    # MATCH PARSING
    match = MatchAnalyser(pathlib.Path(match_path))
    match_data = match.get_match_data()
    match.get_players_object().set_player_data_from_dict(additional_player_data)

    MS = MatchSplitter(game_length=match.game_length)

    additional_data = process_additional_data(db_session=db_session, match=match, match_data=match_data,
                                              ptd_dict=PTD_objs_dict)

    GP_objs_dict = main_data(db_session=db_session,
                             match=match,
                             match_data=match_data,
                             MS=MS,
                             PerTotalData_dict=PTD_objs_dict, )

    return (GP_objs_dict, additional_data)
