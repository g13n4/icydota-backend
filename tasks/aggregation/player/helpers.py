from models import AggregationType, ComparisonType
from models.performance import Performance
from tasks.aggregation.helpers import AggregationKeyCreator, COMPARISON_MAP, \
    match_aggregation_league_participants_query_creator
from tasks.helpers import PROCESSING_COMPARISON_LIST


def create_player_aggregation_performance_objs(
        db_session,
        league_id: int | None,
        AGC: AggregationKeyCreator,
        patch_id: int | None,
) -> dict[tuple, Performance]:
    output = dict()
    query, names = match_aggregation_league_participants_query_creator(league_id=league_id, patch_id=patch_id)
    league_participants = db_session.exec(query)

    for row in league_participants:
        row_data = { name: value for name, value in zip(names, row) }
        required_row_data = AGC.create_dict(row_data)

        for is_comparison, is_flat in PROCESSING_COMPARISON_LIST:
            row_key = AGC.create_key(row_data, append=is_flat)

            aggregation_obj = AggregationType(
                type_id=AGC.type_id,
                patch_id=patch_id,
                league_id=league_id,
                **required_row_data,
            )

            comparison_obj = None
            performance_type = Performance.const.game.AGGREGATION
            if is_comparison:
                performance_type = Performance.const.game.AGGREGATION_COMPARISON
                comparison_data = { COMPARISON_MAP[name].cpd: value for name, value in required_row_data.items() }

                comparison_obj = ComparisonType(
                    is_flat=is_flat,
                    **comparison_data,
                )

            performance_obj = Performance(
                type_id=performance_type,
                aggregation_type=aggregation_obj,
                comparison_type=comparison_obj,
            )
            output[row_key] = performance_obj

            db_session.add(performance_obj)

    return output
