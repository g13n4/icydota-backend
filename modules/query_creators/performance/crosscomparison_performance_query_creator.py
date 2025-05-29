from constants.api import PoTEnum
from models import ComparisonType, AggregationType, CrossComparisonType
from models.performance import Performance
from modules.query_creators.const_map import CCOMPARISON_MODELS, CCOMPARISON_JOIN
from modules.query_creators.helpers import combine_select
from modules.query_creators.performance.query_creator_mixin import PerformanceQueryCreatorMixin


class APICrossComparisonPerformanceQueryCreator(PerformanceQueryCreatorMixin):
    def _set_cross_comparison_query_data(
            self,
            league_id: int | None,
            patch_id: int | None,
            aggregation_type_id: int,
            position_id: int,
            data_field: str,
            calculation_type_id: int,
            is_flat: bool | None,
    ):
        self._set_data_model(calculation_type_id=calculation_type_id, field=data_field)

        if league_id:
            self.where.append(AggregationType.league_id == league_id)
        else:
            self.where.append(AggregationType.patch_id == patch_id)

        self.where.append(ComparisonType.is_flat == is_flat)

        for item in CCOMPARISON_MODELS[aggregation_type_id]:
            self.models.add(item.field, item.field_name)

        self.joins.add(ComparisonType, Performance.id == ComparisonType.performance_id)
        self.joins.add(CrossComparisonType, Performance.id == CrossComparisonType.performance_id)

        self.where.append(CrossComparisonType.position_aggregation_id == position_id)

        for model, join in CCOMPARISON_JOIN[aggregation_type_id]:
            self.joins.add(model, onclause=join)


    def get_cross_comparison_query(
            self,
            pot: PoTEnum,
            league_id: int | None,
            patch_id: int | None,
            aggregation_type_id: int,
            position_id: int,
            data_field: str,
            calculation_type_id: int,
            is_flat: bool,
    ):

        self._set_cross_comparison_query_data(
            league_id=league_id,
            patch_id=patch_id,
            aggregation_type_id=aggregation_type_id,
            position_id=position_id,
            data_field=data_field,
            calculation_type_id=calculation_type_id,
            is_flat=is_flat,
        )

        if pot.isPlayer():
            self.where.append(Performance.type_id == Performance.const.game.CROSS_COMPARISON)
        else:
            self.where.append(Performance.type_id == Performance.const.team.TEAM_MATCH_CROSS_COMPARISON)

        return combine_select(self.models.get_models(), self.joins.data, self.where)
