from constants.api import PoTEnum
from models import PlayerGameData, Player, Position
from models.performance import Performance
from modules.query_creators.helpers import combine_select
from modules.query_creators.performance.query_creator_mixin import PerformanceQueryCreatorMixin


class APIMatchPerformanceQueryCreator(PerformanceQueryCreatorMixin):
    def _set_match_select_query_data(
            self,
            calculation_type_id: int,
            match_id: int | None = None,
    ) -> None:
        self._set_data_model(calculation_type_id=calculation_type_id)

        self.models.add(PlayerGameData.dire, 'side', True)
        self.joins.add(PlayerGameData, Performance.player_game_data_id == PlayerGameData.id)

        self.models.add(Position.name, 'position', True)
        self.joins.add(Position, PlayerGameData.position_id == Position.id)

        self.models.add(PlayerGameData.hero_id, 'hero_id', True)

        self.models.add(Player.nickname, 'player', True)
        self.joins.add(Player, PlayerGameData.player_id == Player.account_id)

        self.where.append(PlayerGameData.game_id == match_id)


    def get_match_query(self, match_id: int, calculation_type_id: int, pot: PoTEnum):
        self._set_match_select_query_data(calculation_type_id=calculation_type_id, match_id=match_id)
        if pot.isPlayer():
            self.where.insert(0, Performance.type_id == Performance.const.game.MATCH_DATA)
        else:
            self.where.insert(0, Performance.type_id == Performance.const.team.TEAM_MATCH_DATA)

        return combine_select(self.models.get_models(), self.joins.data, self.where)


    def get_match_comparison_query(
            self,
            match_id: int,
            calculation_type_id: int,
            pot: PoTEnum,
            basic: bool,
            is_flat: bool,
    ):
        self._set_match_select_query_data(calculation_type_id=calculation_type_id, match_id=match_id)
        self._set_comparison_model(basic=basic, is_flat=is_flat, name='compared_to')

        if pot.isPlayer():
            self.where.append(Performance.type_id == Performance.const.game.MATCH_DATA_COMPARISON)
        else:
            self.where.append(Performance.type_id == Performance.const.team.TEAM_MATCH_DATA_COMPARISON)

        return combine_select(self.models.get_models(), self.joins.data, self.where)
