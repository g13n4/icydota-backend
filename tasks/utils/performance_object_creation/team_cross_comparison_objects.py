from models.performance import Performance
from models.performance_data_type import ByTeamType
from modules.key_creators.ccomparison_key_creator import CrossComparisonTeamKeyCreator
from sqlmodel import Session

def create_team_cross_comparison_performance_objs(
        db_session: Session,
        league_id: int | None,
        patch_id: int | None,
        data,
        is_flat: bool,
        KC: CrossComparisonTeamKeyCreator,
        output: None | dict = None,
) -> dict[tuple, Performance]:
    performance_objs_dict = dict()
    for item in data:
        key = KC.create_key(item, append=is_flat)

        type_obj = ByTeamType(
            patch_id=patch_id,
            league_id=league_id,
            team_id=item['team_cpd_id'],
            is_flat=is_flat,
            team_cpd_id=item['team_cpd_id'],
            team_cps_id=item['team_cps_id'],
        )

        performance_obj = Performance(
            type_id=Performance.const.team.TEAM_MATCH_CROSS_COMPARISON,
            by_team_type=type_obj,
        )

        db_session.add(performance_obj)
        performance_objs_dict[key] = performance_obj

    if output is not None:
        output.update(performance_objs_dict)
    return performance_objs_dict
