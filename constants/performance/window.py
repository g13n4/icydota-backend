from typing import Any, Callable

import numpy as np
from pydantic import BaseModel

from constants.helpers import get_only_names, to_range


# MINUTE
M = 60
# HOUR
H = 60 * M


class GameWindow(BaseModel):
    order: int | None = None  # is local to window group
    start_time: int | None
    end_time: int | None

    index: int | None = None  # is global
    name: str | None = None
    description: str | None = None
    window_type: str | None = None
    length: int | None = None

    is_total: bool = False
    empty_mask: str | None = None
    agg_func: Callable | None = None


    def model_post_init(self, __context: Any) -> None:
        if self.start_time is None and self.end_time is None:
            self.is_total = True

        if self.start_time is not None and self.end_time is not None:
            self.length = abs(self.end_time - self.start_time)

        return None


class WindowType:
    lane: str = 'lane'
    game: str = 'game'

    VALUES: str = [lane, game]


class WindowEmptyMask:
    l_empty_mask: str = 'l_empty_mask'
    g_empty_mask: str = 'g_empty_mask'


GLOBAL_WINDOW_COUNTER = 1


def set_window_data(window_type: str, window_empty_mask: str) -> Callable:
    def set_window_name(klass: object):
        global GLOBAL_WINDOW_COUNTER
        local_counter = 1
        for name, type_ in klass.__annotations__.items():
            if type_ is GameWindow:
                value = getattr(klass, name)
                value.name = name
                value.window_type = window_type
                value.empty_mask = window_empty_mask

                if value.description is None:
                    value.description = to_range(value.start_time, value.end_time)

                value.order = local_counter
                value.index = GLOBAL_WINDOW_COUNTER

                GLOBAL_WINDOW_COUNTER += 1
                local_counter += 1

        return klass


    return set_window_name


def set_value_names(klass: object):
    VALUES_REAL = getattr(klass, 'VALUES_REAL')
    setattr(klass, 'VALUES_REAL_NAMES', get_only_names(VALUES_REAL))

    VALUES = getattr(klass, 'VALUES')
    setattr(klass, 'VALUES_NAMES', get_only_names(VALUES))

    return klass


@set_value_names
@set_window_data(WindowType.lane, WindowEmptyMask.l_empty_mask)
class LaneStageWindows:
    # first 2 minutes
    l2: GameWindow = GameWindow(start_time=-90, end_time=2 * M)
    # 2-4
    l4: GameWindow = GameWindow(start_time=2 * M, end_time=4 * M)
    # 4-6
    l6: GameWindow = GameWindow(start_time=4 * M, end_time=6 * M)
    # 6-8
    l8: GameWindow = GameWindow(start_time=6 * M, end_time=8 * M)
    # 8-10
    l10: GameWindow = GameWindow(start_time=8 * M, end_time=10 * M)
    # 10-12
    l12: GameWindow = GameWindow(start_time=10 * M, end_time=12 * M)
    # 12-15
    l15: GameWindow = GameWindow(start_time=12 * M, end_time=15 * M)
    # 15-20
    l20: GameWindow = GameWindow(start_time=15 * M, end_time=20 * M)
    # total calc
    ltotal_max: GameWindow = GameWindow(start_time=None, end_time=None, description='<20 m. (max)', agg_func=np.max)
    ltotal_min: GameWindow = GameWindow(start_time=None, end_time=None, description='<20 m. (min)', agg_func=np.min)
    ltotal_sum: GameWindow = GameWindow(start_time=None, end_time=None, description='<20 m. (sum)', agg_func=np.sum)

    l_empty_mask: str = 'l_empty_mask'
    empty_mask: str = 'l_empty_mask'

    VALUES_REAL: list[GameWindow] = [l2, l4, l6, l8, l10, l12, l15, l20]
    VALUES_REAL_NAMES: list[GameWindow]

    VALUES_TOTALS: list[GameWindow] = [ltotal_max, ltotal_min, ltotal_sum]

    VALUES: list[GameWindow] = VALUES_REAL + VALUES_TOTALS
    VALUES_NAMES: list[GameWindow]


@set_value_names
@set_window_data(WindowType.game, WindowEmptyMask.g_empty_mask)
class GameStageWindows:
    # first 5 minutes
    g5: GameWindow = GameWindow(start_time=-90, end_time=5 * M)
    # 5 - 15
    g15: GameWindow = GameWindow(start_time=5 * M, end_time=15 * M)
    # 15 - 25
    g25: GameWindow = GameWindow(start_time=15 * M, end_time=25 * M)
    # 25 - 35
    g35: GameWindow = GameWindow(start_time=30 * M, end_time=45 * M)
    # 35 - 47
    g47: GameWindow = GameWindow(start_time=30 * M, end_time=45 * M)
    # 47 - 60
    g60: GameWindow = GameWindow(start_time=45 * M, end_time=H)
    # 60 - inf
    g60plus: GameWindow = GameWindow(start_time=H, end_time=H * 60, description='60 m. - the game\'s end')
    # total calc
    gtotal_max: GameWindow = GameWindow(
        start_time=None,
        end_time=None,
        description='by the game\'s end (max)',
        agg_func=np.max,
    )
    gtotal_min: GameWindow = GameWindow(
        start_time=None,
        end_time=None,
        description='by the game\'s end (min)',
        agg_func=np.min,
    )
    gtotal_sum: GameWindow = GameWindow(
        start_time=None,
        end_time=None,
        description='by the game\'s end (sum)',
        agg_func=np.sum,
    )

    g_empty_mask: str = 'g_empty_mask'
    empty_mask: str = 'g_empty_mask'

    VALUES_REAL: list[GameWindow] = [g5, g15, g25, g35, g47, g60, g60plus]
    VALUES_REAL_NAMES: list[GameWindow]

    VALUES_TOTALS: list[GameWindow] = [gtotal_max, gtotal_min, gtotal_sum]

    VALUES: list[GameWindow] = VALUES_REAL + VALUES_TOTALS
    VALUES_NAMES: list[GameWindow]


@set_value_names
class AllWindows(LaneStageWindows, GameStageWindows):
    WINDOW_TYPES = [WindowType.lane, WindowType.game]

    STAGES = [LaneStageWindows, GameStageWindows]

    VALUES: list[GameWindow] = LaneStageWindows.VALUES + GameStageWindows.VALUES
    VALUES_NAMES: list[GameWindow]

    VALUES_TOTALS: list[GameWindow] = LaneStageWindows.VALUES_TOTALS + GameStageWindows.VALUES_TOTALS

    VALUES_REAL: list[GameWindow] = LaneStageWindows.VALUES_REAL + GameStageWindows.VALUES_REAL
    VALUES_REAL_NAMES: list[GameWindow]

    EMPTY_MASK_WINDOWS_MAP: list[tuple[list[GameWindow], str]] = [
        (LaneStageWindows.VALUES, LaneStageWindows.l_empty_mask),
        (GameStageWindows.VALUES, GameStageWindows.g_empty_mask),
    ]


WINDOWS_BY_TYPE = {
    WindowType.lane: LaneStageWindows,
    WindowType.game: GameStageWindows,
    'both': AllWindows,
}

WINDOWS_BY_MASK = {
    LaneStageWindows.empty_mask: LaneStageWindows,
    GameStageWindows.empty_mask: GameStageWindows,
}

WINDOWS_BY_FIELD = { item.name: item for item in AllWindows.VALUES }
