from constants.position import PositionConstant
from modules.interval.helpers import get_line_data


class IntervalBiggestAdvantage:

    def __init__(self):
        self.current_player_gold = {
            x: 0 for x in range(10)
        }

        self.biggest_player_difference = { name: { x: 0 for x in range(10) } for name in ["dire", "sentinel"] }
        self.biggest_calculated_advantage = { name: 0 for name in ["dire", "sentinel"] }

        self.line_id = -90
        self.player_set = set()


    def _set_difference(self):
        if len(self.player_set) == 10:
            sentinel_sum = 0
            for slot in range(5):
                sentinel_sum += self.current_player_gold[slot]

            dire_sum = 0
            for slot in range(5, 10):
                dire_sum += self.current_player_gold[slot]

            difference = sentinel_sum - dire_sum

            if difference > 0:
                side = "sentinel"
            elif difference < 0:
                side = "dire"
            else:
                return None

            difference = abs(difference)

            if self.biggest_calculated_advantage[side] < difference:
                self.biggest_calculated_advantage[side] = difference

                for slot in range(10):
                    self.biggest_player_difference[side][slot] = self.current_player_gold[slot]

        return None


    def _clear_data(self):
        for x in range(10):
            self.current_player_gold[x] = 0
            self.player_set.clear()


    def add_line(self, line: dict) -> None:
        time, slot, gold = get_line_data(line, "gold")
        if time != self.line_id:
            self._clear_data()

        self.line_id = time
        self.current_player_gold[slot] = gold
        self.player_set.add(slot)

        self._set_difference()


    def _get_slot_difference(self, minuend_slot: int, subtrahend_slot: int, advantage_side: str) -> int:
        minuet_value = self.biggest_player_difference[advantage_side][minuend_slot]
        subtrahend_value = self.biggest_player_difference[advantage_side][subtrahend_slot]

        return minuet_value - subtrahend_value


    def combine_data(self, slot_to_pos: dict[str, dict[int, int]]) -> dict[int, int]:
        output = dict()

        for position in PositionConstant.POSITIONS:
            sent_slot = slot_to_pos["sentinel"][position.value]
            dire_slot = slot_to_pos["dire"][position.value]

            output[sent_slot] = self._get_slot_difference(sent_slot, dire_slot, "sentinel")
            output[dire_slot] = self._get_slot_difference(dire_slot, sent_slot, "dire")

        return output
