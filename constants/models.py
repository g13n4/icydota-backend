from typing import ClassVar, TypeVar, Callable, Any
from collections import namedtuple
from enum import Enum

# Monotonically increasing integer
monoInt = TypeVar("monoInt")

class GameStage(Enum):
    l: str = 'LANE'
    g: str = 'GAME'


GameWindow = namedtuple('GameWindow',
                        [
                            'index',
                            'window_name',
                            'game_stage',
                            'start_time',
                            'end_time',
                            'stage_key',
                        ])

EARLY_GAME_WINDOW_LIST = [
    # first 2 minutes
    GameWindow(index=1, window_name='l2', game_stage=GameStage.l.value, start_time=-90, end_time=60 * 2, stage_key=GameStage.l.name, ),
    # 2-4
    GameWindow(index=2, window_name='l4', game_stage=GameStage.l.value, start_time=60 * 2, end_time=60 * 4, stage_key=GameStage.l.name, ),
    # 4-6
    GameWindow(index=3, window_name='l6', game_stage=GameStage.l.value, start_time=60 * 4, end_time=60 * 6, stage_key=GameStage.l.name, ),
    # 6-8
    GameWindow(index=4, window_name='l8', game_stage=GameStage.l.value, start_time=60 * 6, end_time=60 * 8, stage_key=GameStage.l.name, ),
    # 8-10
    GameWindow(index=5, window_name='l10', game_stage=GameStage.l.value, start_time=60 * 8, end_time=60 * 10, stage_key=GameStage.l.name, ),
]

LATE_GAME_WINDOW_LIST = [
    # first 15 minutes
    GameWindow(index=1, window_name='g15', game_stage=GameStage.g.value, start_time=-90, end_time=60 * 15, stage_key=GameStage.g.name, ),
    # 15 - 30
    GameWindow(index=2, window_name='g30', game_stage=GameStage.g.value, start_time=60 * 15, end_time=60 * 30, stage_key=GameStage.g.name, ),
    # 30 - 45
    GameWindow(index=3, window_name='g45', game_stage=GameStage.g.value, start_time=60 * 30, end_time=60 * 45, stage_key=GameStage.g.name, ),
    # 45 - 60
    GameWindow(index=4, window_name='g60', game_stage=GameStage.g.value, start_time=60 * 45, end_time=60 * 60, stage_key=GameStage.g.name, ),
    # 60 - inf
    GameWindow(index=5, window_name='g60plus', game_stage=GameStage.g.value, start_time=60 * 60, end_time=60 * 60 * 60, stage_key=GameStage.g.name, ),
]

FULL_GAME_WINDOW_LIST = EARLY_GAME_WINDOW_LIST + LATE_GAME_WINDOW_LIST
ALL_GAME_WINDOW_LIST = [EARLY_GAME_WINDOW_LIST, LATE_GAME_WINDOW_LIST]

def include_CV_types(types: list[Any]) -> list[Any]:
    """
    Adds ClassVar to types provided in a list
    """
    new_types = []
    for type_ in types:
        new_types.append(ClassVar[type_])

    return types + new_types


def to_nested_constant(
        start: int = 1,
        has_only_name: bool = False,
        dont_capitalize: bool = False,
        is_window_wrapper: bool = False,
) -> Callable:
    """
    Wrapper for dataclass like constants used in the system for computation and data consistency
    :param start: first integer to use with monoInt
    :param has_only_name: uses description as a name
    :param dont_capitalize: don't use capitalization during name processing for description
    :param is_window_wrapper: is a special wrapper
    :return: Callable
    """
    def main_wrapper(klass: object) -> object:
        # turn every class variable into an object that contains: description, value and system name
        counter = start
        values = []
        Item = namedtuple(klass.__name__ + 'Item', ['value', 'name', 'description'])
        for name, type_ in klass.__annotations__.items():
            description = None

            if type_ is monoInt:
                value = counter
                counter += 1
            elif type_ in include_CV_types([int, bool, ]):
                value = getattr(klass, name)
            elif type_ in include_CV_types([tuple, tuple[int, str], ]):
                value, description = getattr(klass, name)

            else:
                raise NotImplementedError("Behaviour for this type is not implemented.")

            if description is None:
                if has_only_name:
                    description = name
                else:
                    split_name = name.split('_')
                    description = ' '.join(
                        x.lower() if dont_capitalize else x.lower().capitalize()
                        for x in split_name
                    )

            constant_data = {'value': value, 'name': name, 'description': description}
            values.append(constant_data)
            new_value_class = type(name, (object,), constant_data)
            setattr(klass, name, new_value_class)

        new_values_class = type('VALUES', (object,), {
            'as_dict': values,
            'as_tuple': [Item(item['value'], item['name'], item['description']) for item in values],
        })
        setattr(klass, 'VALUES', new_values_class)

        return klass


    def window_preprocessor_wrapper(klass: object) -> object:
        for idx, window in enumerate(FULL_GAME_WINDOW_LIST):
            setattr(klass, window.window_name, idx)
            klass.__annotations__[window.window_name] = ClassVar[int]

        return klass

    def window_postprocessor_wrapper(klass: object) -> object:
        Item = namedtuple(klass.__name__ + 'Item', ['value', 'name', 'description'])
        for windows_list, windows_list_name in [(EARLY_GAME_WINDOW_LIST, 'EARLY_GAME'),
                                                (LATE_GAME_WINDOW_LIST, 'LATE_GAME'),
                                                (FULL_GAME_WINDOW_LIST, 'FULL_GAME'), ]:
            all_required_windows = []
            for gw in windows_list:
                item = getattr(klass, gw.window_name)
                all_required_windows.append(Item(item.value, item.name, item.description))

            new_values_class = type(windows_list_name, (object,), {
                'as_dict': [item._asdict() for item in all_required_windows],
                'as_tuple': all_required_windows,
            })
            setattr(klass, windows_list_name, new_values_class)

        return klass


    def window_wrapper_main(klass: object) -> object:
        klass = window_preprocessor_wrapper(klass)
        klass = main_wrapper(klass)
        klass = window_postprocessor_wrapper(klass)
        return klass


    if is_window_wrapper:
        return window_wrapper_main
    else:
        return main_wrapper


@to_nested_constant()
class GamePerformanceConstant:
    MATCH_DATA: monoInt
    MATCH_DATA_COMPARISON: monoInt
    AGGREGATION: monoInt
    AGGREGATION_COMPARISON: monoInt
    COMBINED_AGGREGATION: monoInt
    COMBINED_AGGREGATION_COMPARISON: monoInt
    CROSS_COMPARISON: monoInt


@to_nested_constant()
class PerformanceRankingConstant:
    PLAYER_MATCH_RANK: monoInt
    PLAYER_MATCH_BEST_RANK: monoInt
    PLAYER_MATCH_AVG_RANK: monoInt
    PLAYER_MATCH_COMPARISON_RANK: monoInt
    PLAYER_MATCH_COMPARISON_BEST_RANK: monoInt
    PLAYER_MATCH_COMPARISON_AVG_RANK: monoInt

    HERO_MATCH_RANK: monoInt
    HERO_MATCH_BEST_RANK: monoInt
    HERO_MATCH_AVG_RANK: monoInt
    HERO_MATCH_COMPARISON_RANK: monoInt
    HERO_MATCH_COMPARISON_BEST_RANK: monoInt

    TEAM_RANK: monoInt
    TEAM_BEST_RANK: monoInt

    LEAGUE_RANK: monoInt
    LEAGUE_BEST_RANK: monoInt

    PLAYER_AGGREGATED_RANK: monoInt
    HERO_AGGREGATED_RANK: monoInt

    PLAYER_AGGREGATED_COMPARISON_RANK: monoInt
    HERO_AGGREGATED_COMPARISON_RANK: monoInt


@to_nested_constant()
class PositionConstant:
    CARRY: monoInt
    MIDDLE: monoInt
    OFFLANE: monoInt
    SOFT_SUPPORT: monoInt
    HARD_SUPPORT: monoInt


@to_nested_constant(start=0)
class MapLane:
    BASE: monoInt
    BOTTOM: monoInt
    MIDDLE: monoInt
    TOP: monoInt


@to_nested_constant()
class TowerTier:
    TIER_ONE: ClassVar[tuple[int, str]] = (1, "Tier 1")
    TIER_TWO: ClassVar[tuple[int, str]] = (2, "Tier 2")
    TIER_THREE: ClassVar[tuple[int, str]] = (3, "Tier 3")
    TIER_FOUR: ClassVar[tuple[int, str]] = (4, "Tier 4")


@to_nested_constant()
class BuildingConstant:
    IS_MELEE: ClassVar[bool] = True
    IS_NOT_MELEE: ClassVar[bool] = False

    IS_RAX: ClassVar[bool] = True
    IS_NOT_RAX: ClassVar[bool] = False


