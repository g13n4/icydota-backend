class AggregationConstant:
    BY_HERO: int = 1
    BY_HERO_FACET: int = 2
    BY_PLAYER: int = 3
    BY_POSITION: int = 4

    BY_HERO_PLAYER: int = 5
    BY_PLAYER_HERO: int = 6

    BY_HERO_FACET_PLAYER: int = 7
    BY_PLAYER_HERO_FACET: int = 8

    VALUES: list[int] = [
        BY_HERO,
        BY_HERO_FACET,
        BY_PLAYER,
        BY_POSITION,

        BY_HERO_PLAYER,
        BY_PLAYER_HERO,

        BY_HERO_FACET_PLAYER,
        BY_PLAYER_HERO_FACET,
    ]
