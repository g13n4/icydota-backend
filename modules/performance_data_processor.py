from collections import defaultdict
from functools import reduce

import numpy as np
from sqlmodel.ext.asyncio.session import AsyncSession

from constants.calculation.calculation_type.aggregation import TotalAggregationMethod
from constants.calculation.calculation_type.helpers import CalculationItem
from constants.calculation.calculation_types import WindowCalculations
from constants.performance.window import AllWindows
from models import ComparisonType, PlayerGameData
from models.performance import GamePerformance
from modules.match_analyser import MatchPlayer
from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor


OFFSET = 1


def create_totals_map(calculations: list) -> dict[int, list[int]]:
    totals_map = defaultdict(list)
    for calc in calculations:
        if calc.postprocessing and calc.postprocessing.total_format:
            totals_map[calc.postprocessing.total_format.value].append(calc.value - OFFSET)
    return totals_map


class PerformanceDataProcessor:
    ROWS_SIZE = len(WindowCalculations.VALUES)
    COLUMNS_SIZE = len(AllWindows.VALUES)

    TOTALS_MAP = create_totals_map(WindowCalculations.VALUES)
    COLUMN_MAP = {item.name: item.index - OFFSET for item in AllWindows.VALUES}

    def __init__(self, db_session: AsyncSession, players_data: list[MatchPlayer], ):
        self.session = db_session

        self.windows_data = dict()
        self.game_performance = dict()
        self.players_data = dict()
        self.opponents = dict()

        for this_player in players_data:
            slot: int = this_player['slot']

            self.windows_data[slot] = np.zeros(shape=(self.ROWS_SIZE, self.COLUMNS_SIZE), dtype=np.float32)
            self.game_performance[slot] = []
            self.players_data[slot] = this_player
            self.opponents[slot] = this_player['opponents']


    def calculate_totals(self):
        for name, matrix in self.windows_data.items():
            for windows, total_window in AllWindows.WINDOWS_PROCESSING:
                columns_idxs = [item.index - OFFSET for item in windows]
                total_window_idx = total_window.index - OFFSET

                for total_method, rows_idxs in self.TOTALS_MAP.items():
                    agg_func = TotalAggregationMethod.FUNCTION_MAP[total_method]
                    matrix[rows_idxs, total_window_idx] = agg_func(matrix[rows_idxs, columns_idxs], axis=1)


    def process_slot(self, slot: int) -> None:
        slot_data = self.players_data[slot]

        GP_obj = GamePerformance(
            type=GamePerformance.const.MATCH_DATA,
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
                    flat=is_flat,
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

                GP_obj = GamePerformance(
                    type=GamePerformance.const.MATCH_DATA_COMPARISON,
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

        # Aggregated comparison
        windows_data_aggregation = reduce(lambda x, y: x + y, windows_data) / opponents_size
        totals_data_aggregation = TotalPerformanceProcessor.reduce_total_objs(totals_data)

        for is_flat in [True, False]:

            comparison_obj = ComparisonType(
                flat=is_flat,
                basic=False,

                player_cpd_id=comparandum_data['player_id'],
                hero_cpd_id=comparandum_data['hero_id'],
                pos_cpd_id=comparandum_data['position_id'],
            )

            GP_obj = GamePerformance(
                type=GamePerformance.const.MATCH_DATA_COMPARISON,
                player_game_data=comparandum_data['player_game_data'],
                comparison_type=comparison_obj,
            )

            pwd_objs = []
            for PWD_obj in WindowsPerformanceProcessor.comparison_data_to_pwds(
                    comparandum_windows_data,
                    windows_data_aggregation,
                    is_flat
            ):
                pwd_objs.append(PWD_obj)

            GP_obj.window_data = pwd_objs

            GP_obj.total_data = TotalPerformanceProcessor.comparison_data_objs_to_ptd(
                comparandum_total_data,
                totals_data_aggregation,
                is_flat,
            )

            self.session.add(GP_obj)
            self.game_performance[comparandum_slot].append(GP_obj)


    def process_game_data(self):
        self.calculate_totals()
        for slot in self.windows_data.keys():
            self.process_slot(slot)
            self.process_slot_comparisons(slot)



    def get_all_player_game_data(self) -> list[PlayerGameData]:
        output = []
        for slot, data in self.players_data.items():
            data['player_game_data'].performance = self.game_performance[slot]
            output.append(data['player_game_data'])

        return output


    def get_player_data(self, slot: int) -> MatchPlayer:
        return self.players_data[slot]


    def set_value(self, slot: int, calculation: int | CalculationItem, window_index: int, value):
        if type(calculation) is CalculationItem:
            calculation = CalculationItem.value
        elif calculation is None:
            raise ValueError(f"Calculation can't be None!\nslot: {slot}, calculation: {calculation}, window_index: {window_index}, value: {value}, ")

        self.windows_data[slot][calculation-OFFSET][window_index-OFFSET] = value

