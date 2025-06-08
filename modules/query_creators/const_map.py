from collections import namedtuple

from constants.aggregation import AggregationConstant
from constants.calculation.cross_comparison import CrossComparisonTypeConstant
from models import Hero, Player, Position, Facet, ComparisonType


# Use the value from the from_model model instead of the actual model if it's set
AggItem = namedtuple(
    'AggItem',
    [
        "model",
        'model_data',
        "model_data_name",
        'associated_field',
        "join_field",
    ]
    )

HERO = AggItem(Hero, Hero.name, "Hero", 'hero_id', Hero.id)
PLAYER = AggItem(Player, Player.nickname, "Nickname", 'player_id', Player.account_id)
POSITION = AggItem(Position, Position.name, "Position", 'position_id', Position.id)
FACET = AggItem(Facet, Facet.name, "Facet", 'facet_id', Facet.id)

AGGREGATION_MODELS = {
    AggregationConstant.BY_HERO: [HERO, ],
    AggregationConstant.BY_HERO_FACET: [HERO, FACET, ],
    AggregationConstant.BY_PLAYER: [PLAYER, ],
    AggregationConstant.BY_POSITION: [POSITION, ],

    AggregationConstant.BY_HERO_PLAYER: [HERO, POSITION, ],
    AggregationConstant.BY_PLAYER_HERO: [POSITION, HERO, ],

    AggregationConstant.BY_HERO_FACET_PLAYER: [
        HERO,
        FACET,
        PLAYER,
    ],
    AggregationConstant.BY_PLAYER_HERO_FACET: [
        PLAYER,
        HERO,
        FACET,
    ],

}

CComItem = namedtuple('CComItem', ['field', 'field_name', 'auxiliary'], defaults=[False])

CCOMPARISON_MODELS = {
    CrossComparisonTypeConstant.POSITION_PLAYER: [
        CComItem(Player.nickname, 'player', True),
        CComItem(ComparisonType.player_cpd_id, 'player_cpd_id', False),
        CComItem(ComparisonType.player_cps_id, 'player_cps_id', False),
    ],
    CrossComparisonTypeConstant.POSITION_HERO: [
        CComItem(ComparisonType.hero_cpd_id, 'hero_cpd_id', False),
        CComItem(ComparisonType.hero_cps_id, 'hero_cps_id', False),
    ],
    CrossComparisonTypeConstant.POSITION_HERO_FACET: [
        CComItem(ComparisonType.hero_cpd_id, 'hero_cpd_id', False),
        CComItem(ComparisonType.hero_cps_id, 'hero_cps_id', False),
        CComItem(ComparisonType.facet_cpd_id, 'facet_cpd_id', False),
        CComItem(ComparisonType.facet_cps_id, 'facet_cps_id', False),
    ],
}

CCOMPARISON_JOIN = {
    CrossComparisonTypeConstant.POSITION_HERO: [],
    CrossComparisonTypeConstant.POSITION_PLAYER: [
        (Player, ComparisonType.player_cpd_id == Player.account_id)
    ],
    CrossComparisonTypeConstant.POSITION_HERO_FACET: [],
}
