# Use the value from the from_model model instead of the actual model if it's set
BROKEN_DICT = {
    # game_id / player_id / hero_id /facet_id
    (8302886147, None, None, 7404): 7403
}


def check_for_value(
        game_id: int | None = None,
        # all three of next fields are unique so only one can be used for matching
        player_id: int | None = None,
        hero_id: int | None = None,
        facet_id: int | None = None,
):
    match [game_id, player_id, hero_id, facet_id]:
        case [8302886147, _, _, 7404]:
            return { "facet_id": 7403 }

    return None


def check_for_manual_fix_inplace(game_id: int, data: dict) -> None:
    player_id = data["player_id"]
    hero_id = data["hero_id"]
    facet_id = data["facet_id"]

    updated_data = check_for_value(
        game_id=game_id,
        player_id=player_id,
        hero_id=hero_id,
        facet_id=facet_id
    )

    if updated_data is not None:
        data.update(updated_data)
