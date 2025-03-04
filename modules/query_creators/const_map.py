from collections import namedtuple

from constants.aggregation import AggregationConstant
from models import Hero, Player, Position, Facet, AggregationType


# Use the value from the from_model model instead of the actual model if it's set
Item = namedtuple('AggItem', ['model', 'associated_field', 'from_model'])


HERO = Item(Hero, 'hero_id', AggregationType)
PLAYER = Item(Player, 'player_id', None)
POSITION = Item(Position, 'hero_id', AggregationType)
FACET = Item(Facet, 'facet_id', None)


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



CCOMPARISON_MODELS = {
    "hero": [(Hero.name, 'hero'), (Hero.id, 'hero_id'), (AggregationType.hero_cross_cps_id, 'opponent_id')],
    "player": [
        (Player.nickname, 'Player'),
        (Player.account_id, 'account_id'),
        (AggregationType.player_cross_cps_id, 'opponent_id')],
}
