from models.performance import Performance
from models.performance_data_type import ByTeamType
from modules.key_creators.aggregation_key_creator import AggregationTeamKeyCreator
from tasks.aggregation.helpers import team_aggregation_league_participants_query_creator
from tasks.helpers import PROCESSING_COMPARISON_LIST


def create_team_aggregation_performance_objs(
        db_session,
        league_id: int | None,
        patch_id: int | None,
        CK: AggregationTeamKeyCreator,
) -> dict[tuple, Performance]:
    output = dict()
    query, names = team_aggregation_league_participants_query_creator(league_id=league_id, patch_id=patch_id)
    league_participants = db_session.exec(query)

    for row in league_participants:
        row_data = { name: value for name, value in zip(names, row) }

        for is_comparison, is_flat in PROCESSING_COMPARISON_LIST:
            row_key = CK.create_key(row_data, append=is_flat)

            type_obj = ByTeamType(
                patch_id=patch_id,  # either aggregate or choose one
                league_id=league_id,
                team_id=row_data['team_id'],
                is_flat=is_flat,
            )

            performance_type = Performance.const.team.TEAM_MATCH_AGGREGATION_COMPARISON if is_comparison \
                else Performance.const.team.TEAM_MATCH_AGGREGATION

            performance_obj = Performance(
                type_id=performance_type,
                by_team_type=type_obj,
            )
            output[row_key] = performance_obj

            db_session.add(performance_obj)

    return output
