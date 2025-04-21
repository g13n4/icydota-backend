import copy
import operator
from collections import defaultdict
from functools import reduce
from typing import Any

import numpy as np
from sqlmodel.ext.asyncio.session import AsyncSession

from constants.calculation.game.calculation_type.aggregation import TotalAggregationMethod
from constants.calculation.game.calculation_type.helpers import CalculationItem
from constants.calculation.game.calculation_types import WindowCalculations
from constants.performance.window import AllWindows
from models import ComparisonType, PlayerGameData
from models.performance import Performance
from models.performance_data_type import ByTeamType
from modules.match_analyser import MatchPlayer
from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor


OFFSET = 1


def create_totals_map(calculations: list) -> dict[int, list[int]]:
    totals_map = defaultdict(list)
    for calc in calculations:
        if calc.postprocessing and calc.postprocessing.total_format:
            totals_map[calc.postprocessing.total_format].append(calc.value)
    return totals_map


class PerformanceDataProcessor:
    ROWS_SIZE = len(WindowCalculations.VALUES)
    COLUMNS_SIZE = len(AllWindows.VALUES)

    TOTALS_MAP = create_totals_map(WindowCalculations.VALUES)
    COLUMN_MAP = { item.name: item.index - OFFSET for item in AllWindows.VALUES }

    DIRE = "dire"
    SENT = "sent"

    SIDE_OPPOSITE = {
        DIRE: SENT,
        SENT: DIRE,
    }


    def __init__(self, db_session: AsyncSession, players_data: list[MatchPlayer]):
        self.session = db_session

        self.windows_data: dict[int, np.ndarray] = dict()
        self.game_performance = dict()
        self.players_data = dict()
        self.opponents = dict()

        self.windows_teams = dict()

        for this_player in players_data:
            slot: int = this_player['slot']

            self.windows_data[slot] = np.zeros(shape=(self.ROWS_SIZE, self.COLUMNS_SIZE), dtype=np.float32)
            self.game_performance[slot] = []
            self.players_data[slot]: MatchPlayer = this_player
            self.opponents[slot] = this_player['opponents']

        self.PROCESSED_GAME_DATA = False


    def calculate_windows_totals_by_type(self):
        for name, matrix in self.windows_data.items():
            for windows, total_window in AllWindows.WINDOWS_PROCESSING:
                columns_idxs = [item.index - OFFSET for item in windows]
                total_window_idx = total_window.index - OFFSET

                for total_func_idx, rows_idxs in self.TOTALS_MAP.items():
                    func = TotalAggregationMethod.FUNCTION_MAP[total_func_idx]
                    matrix[rows_idxs, :][:, total_window_idx] = func(matrix[rows_idxs, :][:, columns_idxs], axis=1)


    def process_slot(self, slot: int) -> None:
        slot_data = self.players_data[slot]

        GP_obj = Performance(
            type_id=Performance.const.game.MATCH_DATA,
            player_game_data=slot_data['player_game_data'],
            total_data=slot_data['performance_total_data'],
        )

        pwd_objs = []
        window_data = self.windows_data[slot]
        for PWD_obj in WindowsPerformanceProcessor.data_to_pwds(window_data):
            pwd_objs.append(PWD_obj)

        GP_obj.window_data = pwd_objs
        self.session.add(GP_obj)
        self.game_performance[slot].append(GP_obj)


    def _fill_performance_with_comparison_data(
            self,
            P_obj: Performance,
            windows_ndarray_cpd,
            windows_ndarray_cps,
            total_obj_cpd,
            total_obj_cps,
            is_flat: bool,
            add_to_session: bool = False,
    ) -> None | Performance:

        pwd_objs = []
        for PWD_obj in WindowsPerformanceProcessor.comparison_data_to_pwds(
                windows_ndarray_cpd,
                windows_ndarray_cps,
                is_flat
        ):
            pwd_objs.append(PWD_obj)

        P_obj.window_data = pwd_objs

        P_obj.total_data = TotalPerformanceProcessor.comparison_data_objs_to_ptd(
            total_obj_cpd,
            total_obj_cps,
            is_flat,
        )

        if add_to_session:
            self.session.add(P_obj)
        else:
            return P_obj


    def process_slot_comparisons(self, comparandum_slot: int):
        comparandum_data = self.players_data[comparandum_slot]
        opponents = self.opponents[comparandum_slot]
        comparandum_windows_data = self.windows_data[comparandum_slot]
        comparandum_total_data = comparandum_data['performance_total_data']

        windows_data = []
        totals_data = []
        opponents_size = len(opponents)
        for comparans_slot in opponents:
            comparans_data = self.players_data[comparans_slot]
            comparans_windows_data = self.windows_data[comparans_slot]
            comparans_total_data = comparans_data['performance_total_data']

            windows_data.append(comparans_windows_data)
            totals_data.append(comparans_total_data)
            for is_flat in [True, False]:

                comparison_obj = ComparisonType(
                    is_flat=is_flat,
                    basic=True,

                    player_cpd_id=comparandum_data['player_id'],
                    player_cps_id=comparans_data['player_id'],

                    hero_cpd_id=comparandum_data['hero_id'],
                    hero_cps_id=comparans_data['hero_id'],

                    facet_cpd_id=comparandum_data['facet_id'],
                    facet_cps_id=comparans_data['facet_id'],

                    pos_cpd_id=comparandum_data['position_id'],
                    pos_cps_id=comparans_data['position_id'],
                )

                GP_obj = Performance(
                    type_id=Performance.const.game.MATCH_DATA_COMPARISON,
                    player_game_data=comparandum_data['player_game_data'],
                    comparison_type=comparison_obj,
                )

                pwd_objs = []
                for PWD_obj in WindowsPerformanceProcessor.comparison_data_to_pwds(
                        comparandum_windows_data,
                        comparans_windows_data,
                        is_flat
                ):
                    pwd_objs.append(PWD_obj)

                GP_obj.window_data = pwd_objs

                GP_obj.total_data = TotalPerformanceProcessor.comparison_data_objs_to_ptd(
                    comparandum_total_data,
                    comparans_total_data,
                    is_flat,
                )

                self.session.add(GP_obj)
                self.game_performance[comparandum_slot].append(GP_obj)


        # Aggregated comparison by team
        windows_data_aggregation = reduce(operator.add, windows_data) / opponents_size
        totals_data_aggregation = TotalPerformanceProcessor.reduce_total_objs(totals_data, mode="avg")

        for is_flat in [True, False]:

            comparison_obj = ComparisonType(
                is_flat=is_flat,
                basic=False,

                player_cpd_id=comparandum_data['player_id'],
                hero_cpd_id=comparandum_data['hero_id'],
                pos_cpd_id=comparandum_data['position_id'],
            )

            GP_obj = Performance(
                type_id=Performance.const.game.MATCH_DATA_COMPARISON,
                player_game_data=comparandum_data['player_game_data'],
                comparison_type=comparison_obj,
            )

            GP_obj = self._fill_performance_with_comparison_data(
                P_obj=GP_obj,
                windows_ndarray_cpd=comparandum_windows_data,
                windows_ndarray_cps=windows_data_aggregation,
                total_obj_cpd=comparandum_total_data,
                total_obj_cps=totals_data_aggregation,
                is_flat=is_flat,
            )

            self.session.add(GP_obj)
            self.game_performance[comparandum_slot].append(GP_obj)


    def process_side_data(self, match_data: dict[str, Any]):
        if not self.PROCESSED_GAME_DATA:
            raise AssertionError("To process sides you need to process players data first!")

        side_data = {
            "ndarray": None,
            "total": None,
        }

        sides_data = {
            self.DIRE: copy.deepcopy(side_data),
            self.SENT: copy.deepcopy(side_data),
        }

        # NON COMPARISON
        for side, side_offset in [
            (self.DIRE, 0),  # sentinel_offset
            (self.SENT, 5),  # dire_offset
        ]:

            BTT_obj = ByTeamType(
                league_id=match_data["league_id"],
                match_id=match_data["game_obj"].id,
                patch_id=match_data["patch_id"],
                team_id=match_data[side],

            )

            GP_obj = Performance(
                type_id=Performance.const.team.TEAM_MATCH,
                by_team_type=BTT_obj,
            )

            side_indexes = [slot for slot in range(side_offset, 5 + side_offset)]
            total_windows = [self.windows_data[slot] for slot in side_indexes]
            windows_df: np.ndarray = reduce(operator.add, total_windows)

            total_objs = [self.players_data[idx]["performance_total_data"] for idx in side_indexes]
            total_obj = TotalPerformanceProcessor.reduce_total_objs(total_objs, mode="sum")

            GP_obj.total_data = total_obj

            pwd_objs = []
            for PWD_obj in WindowsPerformanceProcessor.data_to_pwds(windows_df):
                pwd_objs.append(PWD_obj)

            GP_obj.window_data = pwd_objs

            sides_data[side]["ndarray"] = windows_df
            sides_data[side]["total"] = total_obj

            self.session.add(GP_obj)

        # COMPARISON
        for side, data in sides_data.items():
            for is_flat in [True, False]:

                opponents_side = self.SIDE_OPPOSITE[side]
                BTT_obj = ByTeamType(
                    league_id=match_data["league_id"],
                    match_id=match_data["game_obj"].id,
                    patch_id=match_data["patch_id"],
                    team_id=match_data[side],

                    is_flat=is_flat,
                    team_cpd_id=match_data[side],
                    team_cps_id=match_data[opponents_side],
                )

                P_obj = Performance(
                    type_id=Performance.const.team.TEAM_MATCH_COMPARISON,
                    by_team_type=BTT_obj,
                )

                self._fill_performance_with_comparison_data(
                    P_obj=P_obj,
                    windows_ndarray_cpd=sides_data[side]["ndarray"],
                    windows_ndarray_cps=sides_data[opponents_side]["ndarray"],
                    total_obj_cpd=sides_data[side]["total"],
                    total_obj_cps=sides_data[opponents_side]["total"],
                    is_flat=is_flat,
                    add_to_session=True
                )



    def process_game_data(self):
        self.calculate_windows_totals_by_type()
        for slot in self.windows_data.keys():
            self.process_slot(slot)
            self.process_slot_comparisons(slot)

        self.PROCESSED_GAME_DATA = True


    def get_all_player_game_data(self) -> list[PlayerGameData]:
        output = []
        for slot, data in self.players_data.items():
            data['player_game_data'].performance = self.game_performance[slot]
            output.append(data['player_game_data'])

        return output


    def get_player_data(self, slot: int) -> MatchPlayer:
        return self.players_data[slot]


    def set_value(self, slot: int, calculation: int | CalculationItem, window_index: int, value):
        if isinstance(calculation, CalculationItem):
            calculation = calculation.value
        elif calculation is None:
            raise ValueError(
                f"Calculation can't be None!\nslot: {slot}, calculation: {calculation}, window_index: {window_index}, value: {value}, "
            )

        if calculation > self.ROWS_SIZE:
            raise KeyError(
                f"The value for calculation is too big! The value will be used in a matrix slicing and can't be bigger than the matrix itself ({self.ROWS_SIZE})"
            )

        self.windows_data[slot][calculation][window_index - OFFSET] = value
