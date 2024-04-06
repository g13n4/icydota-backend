import pandas as pd
import numpy as np
from celery.utils.log import get_task_logger
from sqlmodel import Session, select, col
from celery import shared_task
from typing import Dict, List

from db import get_sync_db_session
from models import PlayerGameData, Game, PositionApproximation

logger = get_task_logger(__name__)

TIMESTAMP_3_MONTHS = 7862400
TIMESTAMP_1_MONTHS = 2678400


def _compare_series(minu: pd.Series, sub: pd.Series, coef: float = 0.45) -> pd.Series:
    diff = (minu - sub)
    diff_div = ((-coef < diff) & (coef > diff))
    return diff_div


def _remove_ndarray(value: int | np.ndarray) -> float:
    if issubclass(type(value), np.ndarray):
        return np.mean(value)
    else:
        return value


@shared_task(name='approximate_positions_for_league', ignore_result=True)
def approximate_positions(league_id: int) -> None:
    logger.info(f"Approximating positions for league {league_id}")
    db_session: Session = get_sync_db_session()
    game_start_time = 0

    logger.info('Removing old position data')
    old_positions_obj = (db_session.exec(select(PositionApproximation)
                                         .where(PositionApproximation.league_id == league_id)))

    old_positions_data: List[tuple[dict, PositionApproximation]] = [(obj.model_dump(), obj) for obj in old_positions_obj]
    old_positions_data: Dict[tuple, PositionApproximation] = {(item['league_id'], item['player_id']): obj
                                                              for item, obj in old_positions_data}

    logger.info('Getting data from new games')
    players_raw_data = db_session.exec(select(PlayerGameData.player_id,
                                              PlayerGameData.team_id,
                                              PlayerGameData.position_id,
                                              Game.game_start_time)
                                       .join(Game)
                                       .where(Game.id == PlayerGameData.game_id,
                                              Game.league_id == league_id)).all()

    teams_set = set()
    players_data = []
    for player, team, position, start_time in players_raw_data:
        players_data.append({
            'position': position,
            'player': player,
            'team': team,
        })
        teams_set.add(team)
        game_start_time = max(game_start_time, start_time)

    logger.info('Calculating average positions...')
    df = pd.DataFrame(players_data)
    agg = (df.groupby(['team', 'player'])
           .agg(mode=pd.NamedAgg(column="position", aggfunc=pd.Series.mode),
                mean=pd.NamedAgg(column="position", aggfunc='mean'),
                median=pd.NamedAgg(column="position", aggfunc="median"), ))

    output = dict()
    # CHECKING CORRECT MODE POSITIONS
    unfit_teams = []

    lineup_ser = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    agg['mode'] = agg['mode'].apply(lambda x: _remove_ndarray(x))
    for team_id in teams_set:
        team_slice = agg.loc[(team_id), :]
        team_slice_position = sorted(team_slice['median'].values)
        if len(team_slice_position) == 5:
            equals = (team_slice_position == lineup_ser).all()
            if equals:
                for pid, posid in team_slice['median'].items():
                    output[pid] = posid
                continue

        unfit_teams.append(team_id)

    # CHECKING COMPARING MEDIAN TO MODE
    agg_not_eq = None
    if unfit_teams:
        logger.info('Fitting in stand-ins...')
        agg = agg.loc[(unfit_teams), :].copy()

        irregular_mode = ((agg['mode'] % 1) > 0)
        median_eq_mode = ((agg['mode'] * 1.0 == agg['median']) & ~irregular_mode)


        agg_not_eq = agg[~median_eq_mode].copy()

        agg_eq = agg[median_eq_mode]
        for idx, value in agg_eq['median'].items():
            team_id, pid = idx
            output[pid] = value

    # CALCULATING USING MEAN
    if agg_not_eq is not None and not agg_not_eq.empty:
        equal_mean_median = (agg_not_eq['mean'] == agg_not_eq['median'])
        can_be_calculated = agg_not_eq[~equal_mean_median]
        cannot_be_calculated: pd.DataFrame = agg_not_eq[equal_mean_median]

        if not can_be_calculated.empty:
            logger.info('Calculating mean positions...')
            diff_div = _compare_series(sub=can_be_calculated['median'], minu=can_be_calculated['mean'])

            for idx, value in can_be_calculated.loc[diff_div, 'median'].items():
                team_id, pid = idx
                if (value % 1) > 0.5:
                    output[pid] = np.ceil(value)
                else:
                    output[pid] = np.floor(value)

        if not cannot_be_calculated.empty:
            logger.info('Aggregating positions...')

            remaining_players = cannot_be_calculated.reset_index()[['player', 'median']]
            remaining_players_ids = remaining_players['player'].to_list()

            pos_slice = db_session.exec(select(PlayerGameData.player_id,
                                               PlayerGameData.position_id, )
                                        .join(Game)
                                        .where(col(PlayerGameData.player_id).in_(remaining_players_ids),
                                               Game.game_start_time < game_start_time + TIMESTAMP_1_MONTHS,
                                               Game.game_start_time > game_start_time - TIMESTAMP_3_MONTHS, )
                                        ).all()

            pos_slice_dict = {player_id: pos_id for player_id, pos_id in pos_slice}

            pos_slice_df = pd.DataFrame([{'player': player_id,
                                        'position': pos_id} for player_id, pos_id in pos_slice])
            pos_slice_agg = (pos_slice_df.groupby(['player']).
                             agg(median=pd.NamedAgg(column="position", aggfunc="median"))).reset_index()

            diff_div = _compare_series(pos_slice_agg['median'], remaining_players['median'], coef=0.51)

            for idx, value in remaining_players.loc[diff_div, 'player'].items():
                output[value] = pos_slice_dict[value]

    logger.info('Setting new positions...')
    for k, v in output.items():
        player_id: int = k
        position_id: int = int(v)

        obj: PositionApproximation | None = old_positions_data.get((league_id, player_id), None)
        if obj is None:
            obj = PositionApproximation(
                league_id=league_id,
                player_id=player_id,
                position_id=position_id,
            )
        else:
            if not obj.position_id == position_id:
                obj.position_id = position_id

        db_session.add(obj)
    db_session.commit()

    logger.info(f"Approximated positions added to the DB")
