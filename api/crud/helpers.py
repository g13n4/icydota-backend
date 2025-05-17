from collections.abc import Iterable

async def to_basic_list(objs: Iterable) -> list[dict]:
    return [
        {
            "title": league.name,
            "value": league.id,
        } for league in objs
    ]
