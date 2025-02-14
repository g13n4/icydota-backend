from typing import Any, Callable

from pydantic import BaseModel
from constants.helpers import get_only_names


# MINUTE
M = 60
# HOUR
H = 60 * M


class GameWindow(BaseModel):
    order: int
    start_time: int | None
    end_time: int | None

    index: int
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


def set_window_data(window_type: str, window_empty_mask: str) -> Callable:
    def set_window_name(klass: object):
        for name, type_ in klass.__annotations__.items():
            if type_ is GameWindow:
                value = getattr(klass, name)
                value.name = name
                value.window_type = window_type
                value.empty_mask = window_empty_mask
        return klass
    return set_window_name


@set_window_data(WindowType.lane, WindowEmptyMask.l_empty_mask)
class LaneStageWindows:
    # first 2 minutes
    l2: GameWindow = GameWindow(order=1, start_time=-90, end_time=2 * M, index=1, description='-1.5m - 2m')
    # 2-4
    l4: GameWindow = GameWindow(order=2, start_time=2 * M, end_time=4 * M, index=2, description='2m - 4m')
    # 4-6
    l6: GameWindow = GameWindow(order=3, start_time=4 * M, end_time=6 * M, index=3, description='4m - 6m')
    # 6-8
    l8: GameWindow = GameWindow(order=4, start_time=6 * M, end_time=8 * M, index=4, description='6m - 8m')
    # 8-10
    l10: GameWindow = GameWindow(order=5, start_time=8 * M, end_time=10 * M, index=5, description='8m - 10m')
    # total calc
    ltotal: GameWindow = GameWindow(order=6, start_time=None, end_time=None, index=6, description='<10m')

    l_empty_mask: str = 'l_empty_mask'
    empty_mask: str = 'l_empty_mask'

    VALUES: list[GameWindow] = [l2, l4, l6, l8, l10, ltotal]
    VALUES_NAMES: list[GameWindow] = get_only_names(VALUES)

    VALUES_REAL: list[GameWindow] = [l2, l4, l6, l8, l10]
    VALUES_REAL_NAME: list[GameWindow] = get_only_names(VALUES_REAL)


@set_window_data(WindowType.game, WindowEmptyMask.g_empty_mask)
class GameStageWindows:
    # first 15 minutes
    g15: GameWindow = GameWindow(order=1, start_time=-90 * M, end_time=15 * M, index=7, description='-1.5m - 15m')
    # 15 - 30
    g30: GameWindow = GameWindow(order=2, start_time=15 * M, end_time=30 * M, index=8, description='15m - 30m')
    # 30 - 45
    g45: GameWindow = GameWindow(order=3, start_time=30 * M, end_time=45 * M, index=9, description='30m - 45m')
    # 45 - 60
    g60: GameWindow = GameWindow(order=4, start_time=45 * M, end_time=H, index=10, description='45m - 60m')
    # 60 - inf
    g60plus: GameWindow = GameWindow(order=5, start_time=H, end_time=H * 60, index=11, description='60m - the game\'s end')
    # total calc
    gtotal: GameWindow = GameWindow(order=6, start_time=None, end_time=None, index=12, description='by the game\'s end')

    g_empty_mask: str = 'g_empty_mask'
    empty_mask: str = 'g_empty_mask'

    VALUES: list[GameWindow] = [g15, g30, g45, g60, g60plus, gtotal]
    VALUES_NAMES: list[GameWindow] = get_only_names(VALUES)

    VALUES_REAL: list[GameWindow] = [g15, g30, g45, g60, g60plus]
    VALUES_REAL_NAMES: list[GameWindow] = get_only_names(VALUES_REAL)


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
