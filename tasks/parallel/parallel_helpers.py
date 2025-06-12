from typing import Literal, Callable

from modules.key_creators import RedisParallelKeyCreator, AggregationPlayerKeyCreator, CrossComparisonPlayerKeyCreator, \
    AggregationTeamKeyCreator, CrossComparisonTeamKeyCreator
from modules.query_creators.cross_comparison_query_creator_function import match_ccomparison_query_creator, \
    team_ccomparison_query_creator
from modules.query_creators.match_aggregation_query_creator_function import match_aggregation_query_creator
from modules.query_creators.team_aggregation_query_creator_function import team_aggregation_query_creator


T = AggregationPlayerKeyCreator | AggregationTeamKeyCreator | CrossComparisonPlayerKeyCreator | CrossComparisonTeamKeyCreator


def get_parallel_helpers(with_query: bool = False, **kwargs) -> tuple[T, str] | tuple[T, str, Callable]:
    processing_type: Literal["aggregation", "cross-comparison"] = kwargs.get("processing_type")
    PoT: Literal["player", "team"] = kwargs.get("PoT")

    agg_type = kwargs.get("aggregation_type")
    ccomp_type = kwargs.get("ccomparison_type")
    type_value = agg_type or ccomp_type or None

    KEY = RedisParallelKeyCreator(
        processing_type=processing_type,
        PoT=PoT,
        aggregation_type=type_value,
        league_id=kwargs["league_id"],
        patch_id=kwargs["patch_id"],
        ccomp_pos_id=kwargs.get("ccomp_pos_id", None),
    )

    match [processing_type, PoT]:
        case ["aggregation", "player"]:
            KC = AggregationPlayerKeyCreator(type_value)
            query = match_aggregation_query_creator
        case ["aggregation", "team"]:
            KC = AggregationTeamKeyCreator()
            query = team_aggregation_query_creator
        case ["cross-comparison", "player"]:
            KC = CrossComparisonPlayerKeyCreator(type_value)
            query = match_ccomparison_query_creator
        case ["cross-comparison", "team"]:
            KC = CrossComparisonTeamKeyCreator()
            query = team_ccomparison_query_creator
        case _:
            raise KeyError(f"Wrong data for processing type or PoT: {processing_type} and {PoT}")

    if with_query:
        return KC, KEY.base, query

    return KC, KEY.base
