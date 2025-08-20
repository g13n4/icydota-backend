from constants.api import PoTEnum
from constants.performance.window import WINDOWS_BY_FIELD
from models import ComparisonType, CrossComparisonType, ByTeamType
from models.performance import Performance, PerformanceWindowData, PerformanceTotalData, PerformanceWindowTable
from modules.query_creators.const_map import CCOMPARISON_MODELS, CCOMPARISON_JOIN
from modules.query_creators.helpers import combine_select
from modules.query_creators.performance.query_creator_mixin import PerformanceQueryCreatorMixin


class APICrossComparisonPerformanceQueryCreator(PerformanceQueryCreatorMixin):
    def _set_data_ccomp_model(self, calculation_type_id: int | None, field: str | None = None):
        if calculation_type_id:
            self.data_model = PerformanceWindowData

            window_item = WINDOWS_BY_FIELD[field]
            self.models.add(getattr(PerformanceWindowTable, field), "value")
            self.models.add(getattr(PerformanceWindowData, window_item.empty_mask), "empty_mask")

            self.joins.add(
                PerformanceWindowTable,
                PerformanceWindowData.performance_table_id == PerformanceWindowTable.id,
                True
            )
            self.where.append(PerformanceWindowData.calc_type_id == calculation_type_id)
        else:
            self.data_model = PerformanceTotalData

            self.models.add(getattr(PerformanceTotalData, field), "value")

        self.joins.add(Performance, self.data_model.performance_id == Performance.id)
        self.where.append(Performance.outdated == False)


    def _set_cross_comparison_match_data(
            self,
            league_id: int | None,
            patch_id: int | None,
            type_id: int,
            position_id: int,
            is_flat: bool | None,
    ):

        if league_id:
            self.where.append(CrossComparisonType.league_id == league_id)
        else:
            self.where.append(CrossComparisonType.patch_id == patch_id)

        self.where.append(ComparisonType.is_flat == is_flat)

        for item in CCOMPARISON_MODELS[type_id]:
            self.models.add(item.field, item.field_name)

        self.joins.add(ComparisonType, Performance.id == ComparisonType.performance_id)
        self.joins.add(CrossComparisonType, Performance.id == CrossComparisonType.performance_id)

        self.where.append(CrossComparisonType.position_aggregation_id == position_id)
        self.where.append(CrossComparisonType.type_id == type_id)

        for model, join in CCOMPARISON_JOIN[type_id]:
            self.joins.add(model, onclause=join)


    def _set_cross_comparison_team_data(
            self,
            league_id: int | None,
            patch_id: int | None,
            is_flat: bool | None,
    ):
        if league_id:
            self.where.append(ByTeamType.league_id == league_id)
        else:
            self.where.append(ByTeamType.patch_id == patch_id)

        self._set_by_team_model(is_flat=is_flat)
        self.models.add(ByTeamType.team_cpd_id, "team_cpd_id", True)
        self.models.add(ByTeamType.team_cps_id, "team_cps_id", True)


    def get_comparison_query(
            self,
            pot: PoTEnum,
            league_id: int | None,
            patch_id: int | None,
            type_id: int,
            position_id: int,
            data_field: str,
            calculation_type_id: int | None,
            is_flat: bool,
    ):
        self._set_data_ccomp_model(calculation_type_id=calculation_type_id, field=data_field)

        if pot.isPlayer():
            self._set_cross_comparison_match_data(
                league_id=league_id,
                patch_id=patch_id,
                type_id=type_id,
                position_id=position_id,
                is_flat=is_flat
            )

            self.where.append(Performance.type_id == Performance.const.game.CROSS_COMPARISON)
        else:
            self._set_cross_comparison_team_data(league_id=league_id, patch_id=patch_id, is_flat=is_flat)
            self.where.append(Performance.type_id == Performance.const.team.TEAM_MATCH_CROSS_COMPARISON)

        return combine_select(self.models.get_models(), self.joins.data, self.where)
