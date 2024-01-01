import os
import pathlib
from pathlib import Path
from typing import Dict, Any

from replay_parsing import MatchAnalyser, MatchSplitter
from .process_game_replay_addtitional import pgr_additional
from .process_game_replay_main import pgr_main
from ..models import PlayerPerformanceTotalStats, Game
from ..models import WindowPlayer

CURRENT_DIR = Path.cwd().parent.parent.absolute()


def process_game_replay(db_session,
                        match_id: int,
                        wp_dict: Dict[int, WindowPlayer],
                        game_obj: Game,
                        pperformance_objs: Dict[int, PlayerPerformanceTotalStats],
                        additional_player_data: Dict[int, Dict[str, Any]]):
    match_path = os.path.join(CURRENT_DIR, Path(f'./replays/{match_id}/{match_id}.jsonl'))

    # MATCH PARSING
    match = MatchAnalyser(pathlib.Path(match_path))
    match_data = match.get_match_data()
    match.get_players_object().set_player_data_from_dict(additional_player_data)

    MS = MatchSplitter(game_length=match.game_length)

    pgr_main(db_session=db_session,
             match=match,
             match_data=match_data,
             MS=MS,
             wp_dict=wp_dict)

    pgr_additional(db_session=db_session,
                   match=match,
                   match_data=match_data,
                   pperformance_objs=pperformance_objs,
                   game_obj=game_obj, )
