from typing import Any, Callable

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


    def model_post_init(self, __context: Any) -> None:
        if self.start_time is None and self.end_time is None:
            self.is_total = True

        if self.start_time is not None and self.end_time is not None:
            self.length = self.end_time - self.start_time

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
    # total calc
    ltotal: GameWindow = GameWindow(start_time=None, end_time=None, description='<15m')

    l_empty_mask: str = 'l_empty_mask'
    empty_mask: str = 'l_empty_mask'

    VALUES_REAL: list[GameWindow] = [l2, l4, l6, l8, l10, l12, l15]
    VALUES_REAL_NAME: list[GameWindow] = get_only_names(VALUES_REAL)

    VALUES: list[GameWindow] = VALUES_REAL + [ltotal]
    VALUES_NAMES: list[GameWindow] = get_only_names(VALUES)


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
    g60plus: GameWindow = GameWindow(start_time=H, end_time=H * 60, description='60m - the game\'s end')
    # total calc
    gtotal: GameWindow = GameWindow(start_time=None, end_time=None, description='by the game\'s end')

    g_empty_mask: str = 'g_empty_mask'
    empty_mask: str = 'g_empty_mask'

    VALUES_REAL: list[GameWindow] = [g5, g15, g25, g35, g47, g60, g60plus]
    VALUES_REAL_NAMES: list[GameWindow] = get_only_names(VALUES_REAL)

    VALUES: list[GameWindow] = VALUES_REAL + [gtotal]
    VALUES_NAMES: list[GameWindow] = get_only_names(VALUES)


class AllWindows(LaneStageWindows, GameStageWindows):
    WINDOW_TYPES = [WindowType.lane, WindowType.game]

    VALUES: list[GameWindow] = LaneStageWindows.VALUES + GameStageWindows.VALUES
    VALUES_NAMES: list[GameWindow] = get_only_names(VALUES)

    VALUES_REAL: list[GameWindow] = LaneStageWindows.VALUES_REAL + GameStageWindows.VALUES_REAL
    VALUES_REAL_NAMES: list[GameWindow] = get_only_names(VALUES_REAL)

    WINDOWS_PROCESSING: list[tuple[list[GameWindow], GameWindow]] = [
        (LaneStageWindows.VALUES_REAL, LaneStageWindows.ltotal),
        (GameStageWindows.VALUES_REAL, GameStageWindows.gtotal),
    ]

    EMPTY_MASK_WINDOWS_MAP: list[tuple[list[GameWindow], str]] = [
        (LaneStageWindows.VALUES, LaneStageWindows.l_empty_mask),
        (GameStageWindows.VALUES, GameStageWindows.g_empty_mask),
    ]


WINDOWS_BY_TYPE = {
    WindowType.lane: LaneStageWindows,
    WindowType.game: GameStageWindows,
    'all': AllWindows,
}


WINDOWS_BY_MASK = {
    LaneStageWindows.empty_mask: LaneStageWindows,
    GameStageWindows.empty_mask: GameStageWindows,
}
