import math
from itertools import cycle

import numpy as np

from modules.interval.helpers import get_line_data


def get_price_of_death(networth: int) -> int:
    return math.ceil(networth / 40)


def get_price_of_buyback(networth: int) -> int:
    return math.floor(200 + networth / 13)


def can_afford_buyback(gold: int, networth: int, is_dead: bool) -> bool:
    if is_dead:
        final_price = get_price_of_buyback(networth)
    else:
        final_price = get_price_of_buyback(networth) + get_price_of_death(networth)
    return (gold - final_price) > 0


class IntervalBuybackStatus:
    ROLLING_SIZE = 12
    ROLLING_PERIODICITY = 10
    BB_COOLDOWN = 7 * 60
    ROLLING_SECONDS = ROLLING_SIZE * ROLLING_PERIODICITY


    def __init__(self):
        self.rolling_gpm = { x: np.zeros(IntervalBuybackStatus.ROLLING_SIZE) for x in range(10) }
        self.rolling_xpm = { x: np.zeros(IntervalBuybackStatus.ROLLING_SIZE) for x in range(10) }

        self.rolling_index_iterable = iter(cycle(range(IntervalBuybackStatus.ROLLING_SIZE)))

        self.bb_cooldown_status = { x: None for x in range(10) }

        self.output = []


    def _update_bb_cooldown_status(self, slot: int, time: int):
        current_status: int | None = self.bb_cooldown_status[slot]
        if current_status is not None and time > current_status:
            self.bb_cooldown_status[slot] = None


    def _update_rolling_values(self, slot: int, gold: int, xp: int):
        idx = next(self.rolling_index_iterable)

        self.rolling_gpm[slot][idx] = gold
        self.rolling_xpm[slot][idx] = xp


    def _get_buyback_status(self, slot: int, gold: int, networth: int, is_alive: bool) -> bool:
        if self.bb_cooldown_status[slot] is not None:
            return False

        return can_afford_buyback(gold=gold, networth=networth, is_dead=is_alive)


    def _get_potential_loses(self, slot: int, is_alive: bool) -> tuple[float, float]:
        if is_alive:
            return 0, 0

        gold_slice = self.rolling_gpm[slot]
        xp_slice = self.rolling_xpm[slot]

        gold_loss = (gold_slice.max() - gold_slice.min()) / IntervalBuybackStatus.ROLLING_SECONDS
        xp_loss = (xp_slice.max() - xp_slice.min()) / IntervalBuybackStatus.ROLLING_SECONDS

        return gold_loss, xp_loss


    def add_interval_line(self, line: dict) -> None:
        time, slot, gold, xp, lstate, networth = get_line_data(line, "gold", "xp", "life_state", "networth")
        # 0 - alive
        is_alive = lstate == 0

        self._update_bb_cooldown_status(slot=slot, time=time)

        if not (time % IntervalBuybackStatus.ROLLING_PERIODICITY):
            self._update_rolling_values(slot=slot, gold=gold, xp=xp)

        has_bb = self._get_buyback_status(slot=slot, gold=gold, networth=networth, is_alive=is_alive)
        gold_loss, xp_loss = self._get_potential_loses(slot=slot, is_alive=is_alive)

        self.output.append(
            {
                "time": time,
                "slot": slot,

                "has_bb": has_bb,
                "has_no_bb": not has_bb,

                "gold_loss": gold_loss,
                "xp_loss": xp_loss,
            }
        )


    def add_buyback_line(self, line: dict):
        # "type": "CHAT_MESSAGE_BUYBACK"
        slot = line["player1"]
        self.bb_cooldown_status[slot] = line["time"] + IntervalBuybackStatus.BB_COOLDOWN


    def get_data(self):
        return self.output
