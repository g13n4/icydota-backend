from collections import namedtuple
from typing import ClassVar, Any

from pydantic import condecimal, BaseModel
from sqlmodel import Field, SQLModel

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
    name: str = None
    description: str = None
    window_type: str
    length: int | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.start_time is not None and self.end_time is not None:
            self.length = self.end_time - self.start_time
        return None



class GameWindows:
    # first 2 minutes
    l2: GameWindow = GameWindow(order=1, start_time=-90, end_time=2 * M, index=0, window_type='lane', description='-1.5m - 2m')
    # 2-4
    l4: GameWindow = GameWindow(order=2, start_time=2 * M, end_time=4 * M, index=1, window_type='lane', description='2m - 4m')
    # 4-6
    l6: GameWindow = GameWindow(order=3, start_time=4 * M, end_time=6 * M, index=2, window_type='lane', description='4m - 6m')
    # 6-8
    l8: GameWindow = GameWindow(order=4, start_time=6 * M, end_time=8 * M, index=3, window_type='lane', description='6m - 8m')
    # 8-10
    l10: GameWindow = GameWindow(order=5, start_time=8 * M, end_time=10 * M, index=4, window_type='lane', description='8m - 10m')
    # total calc
    ltotal: GameWindow = GameWindow(order=6, start_time=None, end_time=None, index=5, window_type='lane', description='<10m')

    L_WINDOWS: list[GameWindow] = [l2, l4, l6, l8, l10, ltotal]
    L_WINDOWS_NAME: list[GameWindow] = get_only_names(L_WINDOWS)

    L_WINDOWS_REAL: list[GameWindow] = [l2, l4, l6, l8, l10]
    L_WINDOWS_REAL_NAME: list[GameWindow] = get_only_names(L_WINDOWS_REAL)


    # first 15 minutes
    g15: GameWindow = GameWindow(order=1, start_time=-90 * M, end_time=15 * M, index=6, window_type='game', description='-1.5m - 15m')
    # 15 - 30
    g30: GameWindow = GameWindow(order=2, start_time=15 * M, end_time=30 * M, index=7, window_type='game', description='15m - 30m')
    # 30 - 45
    g45: GameWindow = GameWindow(order=3, start_time=30 * M, end_time=45 * M, index=8, window_type='game', description='30m - 45m')
    # 45 - 60
    g60: GameWindow = GameWindow(order=4, start_time=45 * M, end_time=H, index=9, window_type='game', description='45m - 60m')
    # 60 - inf
    g60plus: GameWindow = GameWindow(order=5, start_time=H, end_time=H * 60, index=10, window_type='game', description='60m - the game\'s end')
    # total calc
    gtotal: GameWindow = GameWindow(order=6, start_time=None, end_time=None, index=11, window_type='game', description='by the game\'s end')

    G_WINDOWS: list[GameWindow] = [g15, g30, g45, g60, g60plus, gtotal]
    G_WINDOWS_NAMES: list[GameWindow] = get_only_names(G_WINDOWS)

    G_WINDOWS_REAL: list[GameWindow] = [g15, g30, g45, g60, g60plus]
    G_WINDOWS_REAL_NAMES: list[GameWindow] = get_only_names(G_WINDOWS_REAL)


    WINDOW_TYPES = ['lane', 'game']


    ALL_WINDOWS: list[GameWindow] = L_WINDOWS + G_WINDOWS
    ALL_WINDOWS_NAMES: list[GameWindow] = get_only_names(ALL_WINDOWS)

    ALL_WINDOWS_REAL: list[GameWindow] = L_WINDOWS_REAL + G_WINDOWS_REAL
    ALL_WINDOWS_REAL_NAMES: list[GameWindow] = get_only_names(ALL_WINDOWS_REAL)


class WindowMeta(type(SQLModel)):
    def __new__(cls, name, bases, dct, **kwargs):
        # setting const and fields for the class
        # ClassVar for const object and filling fields
        cls.const = type('Const', (object,), {})
        cls.__annotations__['const'] = ClassVar[object]

        for name, annotation_type in GameWindows.__annotations__.items():
            game_window_value = getattr(GameWindows, name)
            if isinstance(annotation_type, GameWindows):
                # create it for pydantic
                setattr(cls, name, Field(default=None, nullable=True))
                cls.__annotations__[name] = condecimal(max_digits=10, decimal_places=2)
                # create it for const

                game_window_value.name = name

            setattr(cls.const, name, game_window_value)
            cls.const.__annotations__[name] = annotation_type
        print(f"{dct=}")
        print(f"{kwargs=}")
        return super().__new__(cls, name, bases, dct, **kwargs)
