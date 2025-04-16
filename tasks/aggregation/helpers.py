from collections import namedtuple
from typing import Any

from models import Game, PlayerGameData
from models.performance import Performance
from models.performance_data_type import ByTeamType
from modules.query_creators.const_map import AGGREGATION_MODELS
from modules.query_creators.helpers import ModelList, JoinList, combine_select


APPEND_CONST = "___APPEND_CONST"


class AggregationKeyCreator:
    def __init__(self, match_type_id: int | None = None, *, fields: list[str] | None = None ):
        if match_type_id:
            self.type_id = match_type_id
            self.fields = [item.associated_field for item in AGGREGATION_MODELS[match_type_id]]
        elif fields:
            self.fields = fields
        else:
            raise ValueError("Can't create {self.__name__} without id for match or fields for team")

    def get_fields(self):
        return self.fields

    def create_key(self, data: dict, fields: list[str] | None = None, *, append: Any = APPEND_CONST) -> tuple:
        """Get a dictionary and extract values from it according to the fields set"""
        fields_to_use = fields or self.fields
        output = [data[field] for field in fields_to_use]

        if append != APPEND_CONST:
            output.append(append)

        return tuple(output)


    def create_dict(self, data: dict, fields: list[str] | None = None) -> dict:
        """Get a dictionary and recreate using only required fields"""
        fields_to_use = fields or self.fields
        output = { field: data[field] for field in fields_to_use }

        return output


ComparisonItem = namedtuple('ComparisonItem', ['cpd', 'cps'])

COMPARISON_MAP = {
    'hero_id': ComparisonItem(cpd='hero_cpd_id', cps='hero_cps_id'),
    'player_id': ComparisonItem(cpd='player_cpd_id', cps='player_cps_id'),
    'position_id': ComparisonItem(cpd='position_cpd_id', cps='position_cps_id'),
    'facet_id': ComparisonItem(cpd='facet_cpd_id', cps='facet_cps_id'),
}


def match_aggregation_league_participants_query_creator(league_id: int) -> tuple:
    models = ModelList()
    joins = JoinList()
    where = [Game.league_id == league_id]

    models.add(PlayerGameData.hero_id, 'hero_id', True)
    models.add(PlayerGameData.player_id, 'player_id', True)
    models.add(PlayerGameData.position_id, 'position_id', True)
    models.add(PlayerGameData.facet_id, 'facet_id', True)

    joins.add(Performance, Performance.player_game_data_id == PlayerGameData.id)
    joins.add(Game, Game.id == PlayerGameData.game_id)

    return combine_select(models.get_models(), joins.data, where).distinct(), models.get_names()


def team_aggregation_league_participants_query_creator(league_id: int) -> tuple:
    models = ModelList()
    joins = JoinList()
    where = [ByTeamType.league_id == league_id]

    models.add(ByTeamType.team_id, 'team_id', True)
    models.add(ByTeamType.patch_id, 'patch_id', True)

    return combine_select(models.get_models(), joins.data, where).distinct(), models.get_names()
