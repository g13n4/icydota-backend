from collections import defaultdict
from typing import TypeVar

import numpy as np
from orjson import orjson

from constants.position import PositionConstant
from modules.interval.helpers import get_line_data


LINE_VALUES_TO_PROCESS = ["xp", "gold"]


def generate_chart_name(pos: int | None, value_type: str):
    if pos is None:
        return f"{value_type}_game"
    else:
        return f"{value_type}_{pos}"


def _arr_to_str(arr: np.array) -> bytes:
    binary_dump = orjson.dumps([int(x) for x in arr])
    return binary_dump.decode()


T = TypeVar('T')


class IntervalChartDataCollector:
    DATA_GATHERING_INTERVAL = 60 * 2


    def __init__(self):
        self.player_data = {
            slot: {
                value: [] for value in LINE_VALUES_TO_PROCESS
            } for slot in range(10)
        }

        self.player_last_seen = {
            slot: {
                value: None for value in LINE_VALUES_TO_PROCESS
            } for slot in range(10)
        }

        self.team_data = {
            value: [] for value in LINE_VALUES_TO_PROCESS
        }

        self.combined_player_data = None
        self.combined_team_data = None


    def _fill_line_data(self, slot, line, is_last: bool = False):
        for name in LINE_VALUES_TO_PROCESS:
            value = line[name]
            if is_last:
                self.player_last_seen[slot][name] = value
            else:
                self.player_data[slot][name].append(value)


    def add_line(self, line: dict) -> None:
        time, slot = get_line_data(line=line)

        if time == -89 or not (time % IntervalChartDataCollector.DATA_GATHERING_INTERVAL):
            self._fill_line_data(slot, line, is_last=False)

        self._fill_line_data(slot, line, is_last=True)


    def combine_data(self, slot_to_pos: dict[str, dict[int, int]]):
        arr_length = None
        # Filling up last remaining value
        for slot in self.player_data:
            for name in LINE_VALUES_TO_PROCESS:
                self.player_data[slot][name].append(self.player_last_seen[slot][name])
                arr_length = len(self.player_data[slot][name])

        # Output creation
        output_player = { x.value: defaultdict(dict) for x in PositionConstant.POSITIONS }
        output_team = { y: np.zeros(arr_length) for y in LINE_VALUES_TO_PROCESS }

        # Comparing
        for name in LINE_VALUES_TO_PROCESS:
            for position_item in PositionConstant.POSITIONS:

                position = position_item.value
                sent_slot = slot_to_pos["sentinel"][position]
                dire_slot = slot_to_pos["dire"][position]

                sent_arr = np.array(self.player_data[sent_slot][name])
                dire_arr = np.array(self.player_data[dire_slot][name])

                value_arr = sent_arr - dire_arr

                output_player[position][name] = value_arr
                output_team[name] += value_arr

        self.combined_player_data = output_player
        self.combined_team_data = output_team


    def get_data_dict(self) -> dict[str, str]:
        output = { }
        for value_type in LINE_VALUES_TO_PROCESS:
            for pos_item in PositionConstant.POSITIONS:
                field_name = generate_chart_name(pos=pos_item.value, value_type=value_type)
                value = _arr_to_str(self.combined_player_data[pos_item.value][value_type])
                output[field_name] = value

            field_name = generate_chart_name(pos=None, value_type=value_type)
            value = _arr_to_str(self.combined_team_data[value_type])
            output[field_name] = value

        return output
