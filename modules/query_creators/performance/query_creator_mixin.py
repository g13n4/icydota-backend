from sqlalchemy.orm import aliased

from models import ComparisonType, ByTeamType, Team
from models.performance import PerformanceTotalData, PerformanceWindowData, Performance, \
    PerformanceWindowTable
from modules.query_creators.helpers import ModelList, JoinList


class PerformanceQueryCreatorMixin:
    def __init__(self):
        self.data_model = None
        self.data_model_name = None
        self.is_header = False
        self.is_total_data = None

        self.models = ModelList()
        self.joins = JoinList()
        self.where = []


    def _set_model(self, calculation_type_id: int | None, is_header: bool):
        if calculation_type_id:
            self.data_model = PerformanceWindowData
            self.data_model_name = 'window_data'
        else:
            self.data_model = PerformanceTotalData
            self.data_model_name = 'total_data'
            self.is_header = is_header


    def _set_data_model(self, calculation_type_id: int, field: str | None = None, header: bool = True):
        self._set_model(calculation_type_id, header)

        self.models.add(self.data_model, self.data_model_name, header)

        self.joins.add(Performance, self.data_model.performance_id == Performance.id)

        if calculation_type_id > 0:
            self.models.add(PerformanceWindowTable, 'window_table', header)
            self.joins.add(
                PerformanceWindowTable,
                PerformanceWindowData.performance_table_id == PerformanceWindowTable.id,
                True
            )
            self.where.append(PerformanceWindowData.calc_type_id == calculation_type_id)


    def _set_comparison_model(self, is_flat: bool, basic: bool | None = None, name: None | str = None):
        self.models.add(ComparisonType.cps_name_short, name or 'opponent', True)
        self.joins.add(ComparisonType, Performance.id == ComparisonType.performance_id)

        self.where.append(ComparisonType.basic == basic)
        self.where.append(ComparisonType.is_flat == is_flat)


    def get_model_names(self, only_header: bool = False) -> list[str]:
        return self.models.get_names(only_header=only_header)


    def _set_by_team_model(self, is_flat: bool | None = None, name: None | str = None):

        self.joins.add(ByTeamType, ByTeamType.performance_id == Performance.id)

        self.models.add(Team.name, "team", True)
        self.joins.add(Team, ByTeamType.team_id == Team.id)


        self.where.append(ByTeamType.is_flat == is_flat)

