from sqlmodel import Session

from models import ComparisonType, CrossComparisonType
from models.performance import Performance
from modules.key_creators.ccomparison_key_creator import CrossComparisonPlayerKeyCreator


def create_player_cross_comparison_performance_objs(
        db_session: Session,
        league_id: int | None,
        patch_id: int | None,
        data,
        CCKC: CrossComparisonPlayerKeyCreator,
        is_flat: bool,
        ccomparison_type: int,
        position_type: int,
        output: dict | None = None,
) -> dict[tuple, Performance]:
    performance_dict = dict()
    for item in data:
        key_tuple = CCKC.create_key(item, append=is_flat)
        key_dict = CCKC.create_dict(item)

        comparison_obj = ComparisonType(
            is_flat=is_flat,
            basic=False,
            **key_dict,
        )

        ccomparison_obj = CrossComparisonType(
            league_id=league_id,
            type_id=ccomparison_type,
            patch_id=patch_id,
            position_aggregation_id=position_type,
        )

        performance_obj = Performance(
            type_id=Performance.const.game.CROSS_COMPARISON,
            comparison_type=comparison_obj,
            cross_comparison_type=ccomparison_obj,
        )

        db_session.add(performance_obj)
        performance_dict[key_tuple] = performance_obj

    if output is not None:
        output.update(performance_dict)
    return performance_dict
