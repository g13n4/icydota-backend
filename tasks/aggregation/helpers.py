from collections import namedtuple

from models import Game, PlayerGameData
from models.performance import Performance
from models.performance_data_type import ByTeamType
from modules.query_creators.helpers import ModelList, JoinList, combine_select


ComparisonItem = namedtuple('ComparisonItem', ['cpd', 'cps'])

COMPARISON_MAP = {
    'hero_id': ComparisonItem(cpd='hero_cpd_id', cps='hero_cps_id'),
    'player_id': ComparisonItem(cpd='player_cpd_id', cps='player_cps_id'),
    'position_id': ComparisonItem(cpd='position_cpd_id', cps='position_cps_id'),
    'facet_id': ComparisonItem(cpd='facet_cpd_id', cps='facet_cps_id'),
}


def match_aggregation_league_participants_query_creator(league_id: int | None, patch_id: int | None) -> tuple:
    models = ModelList()
    joins = JoinList()
    if patch_id:
        where = [Game.patch_id == patch_id]
    elif league_id:
        where = [Game.league_id == league_id]
    else:
        raise ValueError("No league_id value or patch_id value provided")

    models.add(PlayerGameData.hero_id, 'hero_id', True)
    models.add(PlayerGameData.player_id, 'player_id', True)
    models.add(PlayerGameData.position_id, 'position_id', True)
    models.add(PlayerGameData.facet_id, 'facet_id', True)

    joins.add(Performance, Performance.player_game_data_id == PlayerGameData.id)
    joins.add(Game, Game.id == PlayerGameData.game_id)

    return combine_select(models.get_models(), joins.data, where).distinct(), models.get_names()


def team_aggregation_league_participants_query_creator(league_id: int | None, patch_id: int | None) -> tuple:
    models = ModelList()
    joins = JoinList()

    if patch_id:
        where = [ByTeamType.patch_id == patch_id]
    elif league_id:
        where = [ByTeamType.league_id == league_id]
    else:
        raise ValueError("No league_id value or patch_id value provided")

    models.add(ByTeamType.team_id, 'team_id', True)
    models.add(ByTeamType.patch_id, 'patch_id', True)

    return combine_select(models.get_models(), joins.data, where).distinct(), models.get_names()
