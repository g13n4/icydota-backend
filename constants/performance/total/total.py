from collections.abc import Iterable
from typing import Any, ClassVar, Optional, Literal

from pydantic import condecimal, BaseModel, ConfigDict

from constants.field_types.field_availability import FieldAvailability
from constants.field_types.field_option import FieldOption, RepresentationNumbersMixin
from constants.field_types.field_representation import DATA_TYPE_TYPE, TotalFieldRepresentation
from constants.helpers import Item
from constants.performance.total.category import GameTotalsCategory
from constants.performance.total.processing_options import TotalTeamProcessingOption
from helpers import to_proper_name
from modules.unique_index_checker import UniqueIndexChecker


MINUTE = 60

FIELD_AVAILABILITY_DATA_REPRESENTATION_TYPE_LITERAL = Literal[DATA_TYPE_TYPE]


class GameTotal(BaseModel, RepresentationNumbersMixin):
    model_config = ConfigDict(slots=True)

    value_type: Any

    index: int
    name: str | None = None
    description: str | None = None
    pseudo_bool: bool = False
    field_options: FieldOption | None = None
    sort_offset: int = 0
    category: None | Item = None
    team_processing_option: None | int = None


def set_total_name(klass: object):
    values = []
    checker = UniqueIndexChecker()
    for name, type_ in klass.__annotations__.items():
        if type_ is GameTotal:
            item = getattr(klass, name)
            item.name = name
            if item.description is None:
                item.description = to_proper_name(name)

            values.append(item)

            checker.add(item.index)

            if item.category is None:
                item.category = GameTotalsCategory.GENERAL

    setattr(klass, '_VALUES', values)

    return klass


class GameTotalsIterator:
    def __init__(self, values: list[GameTotal]):
        self._values = values


    def __len__(self):
        return len(self._values)


    def __call__(
            self,
            available_for: Iterable | None = None,
            only_pseudo_bools: bool = False,
            only_comparable: bool = False,
            only_field: Literal["index", "name"] | None = None,
    ):
        for item in self._values:
            if only_pseudo_bools and not item.pseudo_bool:
                continue

            if only_comparable and (item.field_options and not item.field_options.is_comparable):
                continue

            if available_for and item.field_options is not None:
                if not item.field_options.is_available(*available_for):
                    continue

            if only_field is None:
                yield item
            else:
                yield getattr(item, only_field)


    def __iter__(self):
        yield from self._values


@set_total_name
class GameTotals:
    gold: GameTotal = GameTotal(value_type=condecimal(max_digits=10, decimal_places=2), index=1)
    xp: GameTotal = GameTotal(value_type=condecimal(max_digits=8, decimal_places=2), index=2)
    kills_per_min: GameTotal = GameTotal(
        value_type=condecimal(max_digits=5, decimal_places=2),
        index=3,
        category=GameTotalsCategory.KDA,
    )
    kda: GameTotal = GameTotal(
        value_type=condecimal(max_digits=5, decimal_places=2),
        index=4,
        category=GameTotalsCategory.KDA,
    )
    neutral_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=5)
    tower_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=5, decimal_places=2), index=6)
    courier_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=7)
    lane_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=8)
    hero_kills: GameTotal = GameTotal(
        value_type=condecimal(max_digits=6, decimal_places=2),
        index=9,
        category=GameTotalsCategory.KDA,

    )
    observer_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=4, decimal_places=2), index=10)
    sentry_kills: GameTotal = GameTotal(
        value_type=condecimal(max_digits=4, decimal_places=2),
        index=11,
        description="Sentries killed"
    )
    roshan_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=4, decimal_places=2), index=12)
    runes_picked_up: GameTotal = GameTotal(value_type=condecimal(max_digits=4, decimal_places=2), index=13)
    ancient_kills: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=14)
    buyback_count: GameTotal = GameTotal(value_type=condecimal(max_digits=4, decimal_places=2), index=15)
    observer_uses: GameTotal = GameTotal(value_type=condecimal(max_digits=4, decimal_places=2), index=16)
    sentry_uses: GameTotal = GameTotal(value_type=condecimal(max_digits=4, decimal_places=2), index=17)
    lane_efficiency: GameTotal = GameTotal(
        value_type=condecimal(max_digits=4, decimal_places=3),
        index=18,
        team_processing_option=TotalTeamProcessingOption.AVERAGE,
        field_options=FieldOption(
            representation=TotalFieldRepresentation(
                field_repr="percent",
            )
        ),
    )
    first_blood_claimed: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=20,
        description="First Blood",
        pseudo_bool=True,
        category=GameTotalsCategory.KDA,
        team_processing_option=TotalTeamProcessingOption.CEIL,
        field_options=FieldOption(
            is_comparable=False,
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    comparison="none"
                ),
            ],
        ),
    )
    first_kill_time: GameTotal = GameTotal(
        value_type=Optional[int],
        index=24,
        category=GameTotalsCategory.KDA,
        team_processing_option=TotalTeamProcessingOption.BIGGEST,
        field_options=FieldOption(
            is_comparable=False,
            representation=TotalFieldRepresentation(
                field_repr="time",
                data_type=None,
                pot=None,
            )
        ),
    )
    died_first: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=21,
        pseudo_bool=True,
        category=GameTotalsCategory.KDA,
        team_processing_option=TotalTeamProcessingOption.CEIL,
        field_options=FieldOption(
            is_comparable=False,
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    comparison="none"
                ),
            ],
        ),
    )
    died_first_time: GameTotal = GameTotal(
        value_type=Optional[int],
        index=25,
        category=GameTotalsCategory.KDA,
        team_processing_option=TotalTeamProcessingOption.BIGGEST,
        field_options=FieldOption(
            is_comparable=False,
            representation=TotalFieldRepresentation(
                field_repr="time",
                data_type=None,
                pot=None,
            )
        ),
    )

    # FIRST T1 TOWER (NOT FOR AGGREGATION)
    lost_tower_first: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=22,
        pseudo_bool=True,
        description="First to lose a tower",
        category=GameTotalsCategory.T1_TOWERS,
        team_processing_option=TotalTeamProcessingOption.BIGGEST,
        field_options=FieldOption(
            is_comparable=False,
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    comparison="none"
                ),
            ],
        ),
    )
    lost_tower_time: GameTotal = GameTotal(
        value_type=Optional[int],
        index=27,
        category=GameTotalsCategory.T1_TOWERS,
        field_options=FieldOption(
            is_comparable=False,
            representation=TotalFieldRepresentation(
                field_repr="time",
            )
        ),
    )
    lost_tower_lane: GameTotal = GameTotal(
        value_type=Optional[int],
        index=26,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(
                aggregation=False,
                cross_comparison=False,
                for_any_option=True
            ),
            representation=TotalFieldRepresentation(
                field_repr="lane",
                data_type="match",
            )
        ),
        category=GameTotalsCategory.T1_TOWERS,
        team_processing_option=TotalTeamProcessingOption.BIGGEST,
    )

    destroyed_tower_first: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=23,
        pseudo_bool=True,
        description="First to destroy a tower",
        category=GameTotalsCategory.T1_TOWERS,
        team_processing_option=TotalTeamProcessingOption.BIGGEST,
        field_options=FieldOption(
            is_comparable=False,
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    comparison="none"
                ),
            ],
        ),
    )
    destroyed_tower_lane: GameTotal = GameTotal(
        value_type=Optional[int],
        index=28,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(aggregation=False, cross_comparison=False, for_any_option=True),
            representation=TotalFieldRepresentation(
                field_repr="lane",
                data_type="match",
                pot=None,
            )
        ),
        category=GameTotalsCategory.T1_TOWERS,
        team_processing_option=TotalTeamProcessingOption.BIGGEST,
    )
    destroyed_tower_time: GameTotal = GameTotal(
        value_type=Optional[int],
        index=29,
        category=GameTotalsCategory.T1_TOWERS,
        team_processing_option=TotalTeamProcessingOption.BIGGEST,
        field_options=FieldOption(
            is_comparable=False,
            representation=TotalFieldRepresentation(
                field_repr="time",
                data_type=None,
                pot=None,
            )
        ),
    )

    win: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=30,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(match=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="team",
                pot=None,
            ),
        ),
        pseudo_bool=True,
        category=GameTotalsCategory.STATS,
    )
    picked: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=31,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(is_hidden=True),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    comparison="none"
                ),
            ],
        ),
        pseudo_bool=True,
        category=GameTotalsCategory.STATS,
    )

    no_death: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2), index=32,
        field_options=FieldOption(
            is_comparable=False,
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot=None,
            ),
        ),
        category=GameTotalsCategory.KDA,
        pseudo_bool=True
    )
    no_kills: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=33,
        field_options=FieldOption(
            is_comparable=False,
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot=None,
            ),
        ),
        category=GameTotalsCategory.KDA,
        pseudo_bool=True,
    )

    deaths: GameTotal = GameTotal(
        value_type=condecimal(max_digits=6, decimal_places=2),
        category=GameTotalsCategory.KDA,
        index=34,
    )
    assists: GameTotal = GameTotal(
        value_type=condecimal(max_digits=6, decimal_places=2),
        category=GameTotalsCategory.KDA,
        index=35,
    )

    last_hits: GameTotal = GameTotal(value_type=condecimal(max_digits=7, decimal_places=2), index=36)
    denies: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=37)

    gold_per_min: GameTotal = GameTotal(value_type=condecimal(max_digits=6, decimal_places=2), index=38)
    xp_per_min: GameTotal = GameTotal(
        value_type=condecimal(max_digits=6, decimal_places=2),
        index=39,
        description="XP per minute",
    )
    level: GameTotal = GameTotal(
        value_type=condecimal(max_digits=5, decimal_places=2),
        index=40,
        field_options=FieldOption(
            representation=TotalFieldRepresentation(
                field_repr="level",
                data_type=None,
                pot=None,
            ),
        ),
    )

    net_worth: GameTotal = GameTotal(value_type=condecimal(max_digits=8, decimal_places=2), index=41)

    aghanims_scepter: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=42,
        pseudo_bool=True,
        field_options=FieldOption(
            is_comparable=False,
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="player",
                )],
        ),
    )
    aghanims_shard: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=43,
        pseudo_bool=True,
        field_options=FieldOption(
            is_comparable=False,
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="player",
                )],
        ),
    )
    moonshard: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=44,
        field_options=FieldOption(
            is_comparable=False,
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="player",
                )],
        ),
        pseudo_bool=True,
    )

    hero_damage: GameTotal = GameTotal(value_type=condecimal(max_digits=8, decimal_places=2), index=45)
    tower_damage: GameTotal = GameTotal(value_type=condecimal(max_digits=8, decimal_places=2), index=46)
    hero_healing: GameTotal = GameTotal(value_type=condecimal(max_digits=8, decimal_places=2), index=47)

    no_assists: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=48,
        field_options=FieldOption(
            is_comparable=False,
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="player",
            )
        ),
        category=GameTotalsCategory.KDA,
        pseudo_bool=True,

    )
    # FIRST T1 TOWER (FOR AGGREGATION)
    first_tower_destroyed_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=49,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="team",
            ),
        ),
        pseudo_bool=True,
        description="First tower to be destroyed - mid",
        category=GameTotalsCategory.T1_TOWERS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_tower_destroyed_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=50,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="team",
            ),
        ),
        pseudo_bool=True,
        description="First tower to be destroyed - top",
        category=GameTotalsCategory.T1_TOWERS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_tower_destroyed_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=51,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="team",
            ),
        ),
        pseudo_bool=True,
        description="First tower to be destroyed - bot",
        category=GameTotalsCategory.T1_TOWERS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_tower_lost_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=52,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="team",
            ),
        ),
        pseudo_bool=True,
        description="First tower to be lost - mid",
        category=GameTotalsCategory.T1_TOWERS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_tower_lost_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=53,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="team",
            ),
        ),
        pseudo_bool=True,
        description="First tower to be lost - top",
        category=GameTotalsCategory.T1_TOWERS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_tower_lost_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=54,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="team",
            ),
        ),
        pseudo_bool=True,
        description="First tower to be lost - bot",
        category=GameTotalsCategory.T1_TOWERS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    # PICKS
    first_pick_win: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=55,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="team",
            ),
        ),
        pseudo_bool=True,
        category=GameTotalsCategory.PICKS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_pick_lose: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=56,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="team",
            ),
        ),
        pseudo_bool=True,
        category=GameTotalsCategory.PICKS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    last_pick_win: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=57,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="team",
            ),
        ),
        pseudo_bool=True,
        category=GameTotalsCategory.PICKS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    last_pick_lose: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=58,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="team",
            ),
        ),
        pseudo_bool=True,
        category=GameTotalsCategory.PICKS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    last_pick_hero: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=59,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(team=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="player",
            ),
        ),
        pseudo_bool=True,
        category=GameTotalsCategory.PICKS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_pick_hero: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=60,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(team=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="player",
            ),
        ),
        pseudo_bool=True,
        category=GameTotalsCategory.PICKS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    # FIRST T3 TOWER
    first_tower_lane_destroyed_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=61,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First T3 tower destroyed - mid",
        category=GameTotalsCategory.T3_TOWERS_AND_LANES,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_tower_lane_destroyed_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=62,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First T3 tower destroyed - top",
        category=GameTotalsCategory.T3_TOWERS_AND_LANES,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_tower_lane_destroyed_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=63,
        field_options=FieldOption(
            availability=FieldAvailability(player=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First T3 tower destroyed - bot",
        category=GameTotalsCategory.T3_TOWERS_AND_LANES,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_tower_lane_lost_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=64,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First lost T3 tower - mid",
        category=GameTotalsCategory.T3_TOWERS_AND_LANES,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_tower_lane_lost_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=65,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First lost T3 tower - top",
        category=GameTotalsCategory.T3_TOWERS_AND_LANES,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_tower_lane_lost_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=66,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        description="First lost T3 tower - bot",
        pseudo_bool=True,
        category=GameTotalsCategory.T3_TOWERS_AND_LANES,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    # FIRST RAX SET
    first_barracks_set_destroyed_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=67,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First rax set destroyed - mid",
        category=GameTotalsCategory.T3_TOWERS_AND_LANES,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_barracks_set_destroyed_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=68,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First rax set destroyed - top",
        category=GameTotalsCategory.T3_TOWERS_AND_LANES,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_barracks_set_destroyed_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=69,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First rax set destroyed - bot",
        category=GameTotalsCategory.T3_TOWERS_AND_LANES,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_barracks_set_lost_mid: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=70,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First rax set lost - mid",
        category=GameTotalsCategory.T3_TOWERS_AND_LANES,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_barracks_set_lost_top: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=71,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First rax set lost - top",
        category=GameTotalsCategory.T3_TOWERS_AND_LANES,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_barracks_set_lost_bot: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=72,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(player=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First rax set lost - bot",
        category=GameTotalsCategory.T3_TOWERS_AND_LANES,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    # FIRST PICK POSITION
    first_pick_pos_1: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=73,
        field_options=FieldOption(
            availability=FieldAvailability(match=False, player=False, for_any_option=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First pick - pos 1",
        category=GameTotalsCategory.PICKS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_pick_pos_2: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=74,
        field_options=FieldOption(
            availability=FieldAvailability(match=False, player=False, for_any_option=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First pick - pos 2",
        category=GameTotalsCategory.PICKS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_pick_pos_3: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=75,
        field_options=FieldOption(
            availability=FieldAvailability(match=False, player=False, for_any_option=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First pick - pos 3",
        category=GameTotalsCategory.PICKS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_pick_pos_4: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=76,
        field_options=FieldOption(
            availability=FieldAvailability(match=False, player=False, for_any_option=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First pick - pos 4",
        category=GameTotalsCategory.PICKS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    first_pick_pos_5: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=77,
        field_options=FieldOption(
            availability=FieldAvailability(match=False, player=False, for_any_option=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        description="First pick - pos 5",
        category=GameTotalsCategory.PICKS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    win_dire: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=78,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(match=False, player=False, for_any_option=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ),
        pseudo_bool=True,
        category=GameTotalsCategory.STATS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    win_sent: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=79,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(match=False, player=False, for_any_option=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ), pseudo_bool=True,
        category=GameTotalsCategory.STATS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    duration: GameTotal = GameTotal(
        value_type=Optional[int],
        index=80,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(match=False, player=False, for_any_option=True)
        ),
        category=GameTotalsCategory.STATS,
        team_processing_option=TotalTeamProcessingOption.BIGGEST,
    )

    win_with_megas: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=81,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(match=False, player=False, for_any_option=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ), pseudo_bool=True,
        category=GameTotalsCategory.STATS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )

    lose_with_megas: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=82,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(match=False, player=False, for_any_option=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ), pseudo_bool=True,
        category=GameTotalsCategory.STATS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )

    win_and_opponent_with_megas: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=83,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(match=False, player=False, for_any_option=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ), pseudo_bool=True,
        category=GameTotalsCategory.STATS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )
    lose_and_opponent_with_megas: GameTotal = GameTotal(
        value_type=condecimal(max_digits=3, decimal_places=2),
        index=84,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(match=False, player=False, for_any_option=False),
            representation=[
                TotalFieldRepresentation(
                    field_repr="percent",
                    comparison="none"
                ),
                TotalFieldRepresentation(
                    field_repr="boolean",
                    data_type="match",
                    pot="team",
                ),
            ]
        ), pseudo_bool=True,
        category=GameTotalsCategory.STATS,
        team_processing_option=TotalTeamProcessingOption.CEIL,
    )

    gold_advantage: GameTotal = GameTotal(
        value_type=condecimal(max_digits=10, decimal_places=2),
        index=85,
        category=GameTotalsCategory.STATS,
        description="Maximal gold advantage",
    )
    gold_advantage_win: GameTotal = GameTotal(
        value_type=condecimal(max_digits=10, decimal_places=2),
        index=86,
        category=GameTotalsCategory.STATS,
        field_options=FieldOption(
            availability=FieldAvailability(match=False, player=False, for_any_option=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="team",
            ),
        ),
        description="Maximal gold advantage (win)",
    )
    gold_advantage_lose: GameTotal = GameTotal(
        value_type=condecimal(max_digits=10, decimal_places=2),
        index=87,
        category=GameTotalsCategory.STATS,
        description="Maximal gold advantage (lose)",
        field_options=FieldOption(
            availability=FieldAvailability(match=False, player=False, for_any_option=False),
            representation=TotalFieldRepresentation(
                field_repr="boolean",
                data_type="match",
                pot="team",
            ),
        ),
    )
    duration_win: GameTotal = GameTotal(
        value_type=Optional[int],
        index=88,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(match=False, player=False, for_any_option=True)
        ),
        category=GameTotalsCategory.STATS,
        team_processing_option=TotalTeamProcessingOption.BIGGEST,
    )
    duration_lose: GameTotal = GameTotal(
        value_type=Optional[int],
        index=89,
        field_options=FieldOption(
            is_comparable=False,
            availability=FieldAvailability(match=False, player=False, for_any_option=True)
        ),
        category=GameTotalsCategory.STATS,
        team_processing_option=TotalTeamProcessingOption.BIGGEST,
    )

    _VALUES: ClassVar[list[GameTotal]]
    VALUES: GameTotalsIterator
    VALUES_NAMES: list[str]


GameTotals.VALUES = GameTotalsIterator(GameTotals._VALUES)
GameTotals.VALUES_NAMES = list(GameTotals.VALUES(only_field="name"))
