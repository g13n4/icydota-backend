import pandas as pd
from celery.utils.log import get_task_logger
from sqlmodel import Session, select
from celery import shared_task

from db import get_sync_db_session
from models import PlayerGameData, Game, PositionApproximation


logger = get_task_logger(__name__)


@shared_task(name='approximate_positions_for_league', bind=True)
def approximate_positions(self, league_id: int) -> None:
    logger.info(f"Approximating positions for league {league_id}")

    db_session: Session = get_sync_db_session()

    # REMOVING OLD MODELS
    old_positions_obj = (db_session.exec(select(PositionApproximation)
                                         .where(PositionApproximation.league_id == league_id)))
    for old_pos_obj in old_positions_obj:
        db_session.delete(old_pos_obj)
    db_session.commit()

    # GETTING POSITION DATA
    players_raw_data = db_session.exec(select(PlayerGameData.player_id,
                                              PlayerGameData.team_id,
                                              PlayerGameData.position_id, )
                                       .join(Game)
                                       .where(Game.id == PlayerGameData.game_id,
                                              Game.league_id == league_id)).all()

    teams_set = set()
    players_data = []
    for player, team, position in players_raw_data:
        players_data.append({
            'position': position,
            'player': player,
            'team': team,
        })
        teams_set.add(team)

    df = pd.DataFrame(players_data)
    agg = (df.groupby(['team', 'player'])
           .agg(mode=pd.NamedAgg(column="position", aggfunc=pd.Series.mode),
                mean=pd.NamedAgg(column="position", aggfunc='mean'),
                median=pd.NamedAgg(column="position", aggfunc="median"), ))

    output = dict()
    # CHECKING CORRECT MODE POSITIONS
    unfit_teams = []
    lineup_ser = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
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
        agg = agg.loc[(unfit_teams), :].copy()
        median_eq_mode = agg['mode'] * 1.0 == agg['median']

        agg_not_eq = agg[~median_eq_mode].copy()

        agg_eq = agg[median_eq_mode]
        for idx, value in agg_eq['median'].items():
            team_id, pid = idx
            output[pid] = value

    # CALCULATING USING MEAN
    if agg_not_eq is not None and not agg_not_eq.empty:
        diff = (agg_not_eq['mean'] - agg_not_eq['median'])
        diff_div = ((-0.5 < diff) & (0.5 > diff))
        for idx, value in agg_not_eq.loc[diff_div, 'mean'].items():
            team_id, pid = idx
            output[pid] = round(value, 0)

    for k, v in output.items():
        obj = PositionApproximation(
            league_id=league_id,
            player_id=k,
            position_id=int(v),
        )
        db_session.add(obj)
    db_session.commit()

    logger.info(f"Approximated positions added to the DB")

#
# approximate_positions(15475)
# approximate_positions(15728)
# approximate_positions(16201)
