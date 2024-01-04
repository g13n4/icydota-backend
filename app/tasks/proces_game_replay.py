import os
import pathlib
from pathlib import Path
from typing import Dict, Any

from replay_parsing import MatchAnalyser, MatchSplitter
from .process_game_replay_addtitional import pgr_additional
from .process_game_replay_main import pgr_main
from ..models import PerformanceTotalStats, Game, PlayerGameInfo, PlayerGameData

CURRENT_DIR = Path.cwd().parent.parent.absolute()


def process_game_replay(db_session,
                        match_id: int,
                        game_obj: Game,
                        pgi_dict: Dict[int, PlayerGameInfo],
                        pperformance_objs: Dict[int, PerformanceTotalStats],
                        additional_player_data: Dict[int, Dict[str, Any]]):
    match_path = os.path.join(CURRENT_DIR, Path(f'./replays/{match_id}/{match_id}.jsonl'))

    # MATCH PARSING
    match = MatchAnalyser(pathlib.Path(match_path))
    match_data = match.get_match_data()
    match.get_players_object().set_player_data_from_dict(additional_player_data)

    MS = MatchSplitter(game_length=match.game_length)

    pws, pws_comparison = pgr_main(db_session=db_session,
                                   match=match,
                                   match_data=match_data,
                                   MS=MS,
                                   pgi_dict=pgi_dict)

    agd = pgr_additional(db_session=db_session,
                         match=match,
                         match_data=match_data,
                         pperformance_objs=pperformance_objs,
                         game_obj=game_obj, )

    db_session.commit()
    for x in range(10):
        pgi = pgi_dict[x]

        pgd = PlayerGameData(
            league_id=Game.league_id,
            game_id=Game.id,
            team_id=pgi.team_id,
            player_id=pgi.player_id,

            player_game_info_id=pgi.id,

            additional_stats_id=agd.id,

            window_stats=pws[x] + pws_comparison[x],
            total_stats=pperformance_objs[x],
        )

        db_session.add(pgd)

    db_session.commit()
