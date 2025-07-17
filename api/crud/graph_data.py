import orjson
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.game import GamePerformanceGraph
from modules.interval.interval_chart_data_collector import generate_chart_name


async def get_graph_data(
        adb_session: AsyncSession,
        match_id: int,
        position: int = 0,
) -> dict:
    output = {
        "gold": [],
        "xp": [],
    }
    graph_select = select(
        getattr(GamePerformanceGraph, generate_chart_name(pos=position, value_type="gold")),
        getattr(GamePerformanceGraph, generate_chart_name(pos=position, value_type="xp")),
    ).where(GamePerformanceGraph.game_id == match_id)

    graph_data = await adb_session.exec(graph_select)
    for graph_gold, graph_xp in graph_data.all():
        if graph_gold and graph_xp:
            output["gold"] = orjson.loads(graph_gold)
            output["xp"] = orjson.loads(graph_xp)
        break

    return output
