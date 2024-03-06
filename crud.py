# from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Dict, Any, Optional, List

from sqlmodel import Session, select, and_
from sqlmodel.ext.asyncio.session import AsyncSession
from utils import get_sqlmodel_fields
from models import PlayerGameData, Game, ComparisonType, DataAggregationType
from models import PerformanceDataType, PerformanceDataCategory, League, Game, Hero, Player, Position, \
    PerformanceTotalBase
from models import PerformanceWindowData, GamePerformance, PlayerGameData, PerformanceTotalData, PerformanceWindowBase




def get_items(db: Session, model, offset: int = 0, limit: int = 100):
    return db.exec(select(model).offset(offset).limit(limit)).all()


def _to_menu_item(key: str, label: str, children: List[dict] = None, disabled: bool = False, icon: str = None):
    item = {
        'key': key,
        'label': label,
        'disabled': disabled,
    }
    if icon:
        item['icon'] = icon
    if children:
        item['children'] = children
    return item


def _process_menu_item(item, key_add: Optional[str], children_key: Optional[str] = None, name_is_id: bool = False,
                       kid_kwargs: Optional[dict] = None, id_is_key: bool = False) -> Dict[str, Any]:
    output = _to_menu_item(key=item.id if id_is_key else f"{key_add}{item.id}",
                           label=item.id if name_is_id else item.name)
    if not children_key:
        return output
    else:
        if not kid_kwargs:
            kid_kwargs = {}
        if key_add not in kid_kwargs:
            kid_kwargs['key_add'] = children_key[:3]

        output['children'] = [_process_menu_item(item=x, **kid_kwargs) for x in getattr(item, children_key)]
        return output


async def get_categories_menu(db: AsyncSession, model) -> list:
    categories = await db.exec(select(model))
    totals = [{"key": 'total', 'label': 'Total data'}]
    return totals + [_process_menu_item(x, 'c', 'data_type', kid_kwargs={'id_is_key': True}) for x in categories.all()]


async def get_league_header(db: AsyncSession, league_model, ) -> list:
    leagues = await db.exec(select(league_model).order_by(league_model.id.desc()))
    return [_process_menu_item(item, 'l', id_is_key=True) for item in leagues]


async def get_league_games(db_session: AsyncSession, game_model, league_id: int):
    league_objs = (db_session.exec(select(game_model)
                                   .where(game_model.league_id == league_id)
                                   .order_by(game_model.id)))

    return [{'value': x.id, 'label': x.name or x.id, } for x in league_objs.all()]


async def get_performance_data(db_session: AsyncSession,
                               match_id: int,
                               data_type: int | str,
                               comparison: Optional[str],
                               flat: Optional[bool], ):
    clauses = [PlayerGameData.game_id == match_id]

    if data_type == 'total':
        model = PerformanceTotalData
        fields = get_sqlmodel_fields(PerformanceTotalData, include_ids=False, to_set=True)
    else:
        model = PerformanceWindowData
        fields = get_sqlmodel_fields(PerformanceWindowData, include_ids=True, to_set=True)
        clauses.append(PerformanceWindowData.data_type_id == data_type)

    if comparison:
        clauses.extend([
            GamePerformance.is_comparison == True,
            ComparisonType.flat == flat, ])
        if comparison == 'player':
            clauses.append(ComparisonType.basic == True)
        else:
            clauses.append(ComparisonType.basic == False)

    else:
        clauses.append(GamePerformance.is_comparison == False)

    # QUERY BUILDING
    select_query = (select(model, Hero.name, Player.nickname, Position.name)
                    .join(GamePerformance)
                    .join(PlayerGameData)
                    .join(Position, onclause=PlayerGameData.position_id == Position.id)
                    .join(Hero, onclause=PlayerGameData.hero_id == Hero.id)
                    .join(Player, onclause=PlayerGameData.player_id == Player.account_id))

    if comparison:
        select_query = select_query.join(ComparisonType, ComparisonType.id == GamePerformance.comparison_id)

    select_query = select_query.where(*clauses)

    output = await db_session.exec(select_query)
    return [{
        'position': position,
        'hero': hero_name,
        'player': nickname,
        **model_obj.dict(include=fields), } for model_obj, hero_name, nickname, position in output.all()]


async def get_aggregated_performance_data(db_session: AsyncSession,
                                          league_id: int,
                                          aggregation_type: str,
                                          data_type: str | int,
                                          comparison: Optional[str],
                                          flat: Optional[bool], ):
    agg_type_dict = {
        "position": Position.name,
        "hero": Hero.name,
        "player": Player.nickname,
    }

    clauses = [DataAggregationType.league_id == league_id,
               GamePerformance.is_aggregation == True, ]

    if data_type == 'total':
        model = PerformanceTotalData
        fields = get_sqlmodel_fields(PerformanceTotalBase, include_ids=False, to_set=True)
    else:
        model = PerformanceWindowData
        fields = get_sqlmodel_fields(PerformanceWindowBase, include_ids=True, to_set=True)
        clauses.append(PerformanceWindowData.data_type_id == data_type)

    if comparison:
        clauses.extend([
            GamePerformance.is_comparison == True,
            ComparisonType.flat == flat, ])
        if comparison == 'player':
            clauses.append(ComparisonType.basic == True)
        else:
            clauses.append(ComparisonType.basic == False)
    else:
        clauses.append(GamePerformance.is_comparison == False)

    # QUERY BUILDING
    select_query = (select(*[model, agg_type_dict[aggregation_type]])
                    .join(GamePerformance)
                    .join(DataAggregationType))

    if aggregation_type == "position":
        select_query = select_query.join(Position, onclause=DataAggregationType.position_id == Position.id)
        clauses.append(DataAggregationType.by_position == True)
    elif aggregation_type == "player":
        select_query = select_query.join(Player, onclause=DataAggregationType.player_id == Player.account_id)
        clauses.append(DataAggregationType.by_player == True)
    else:
        select_query = select_query.join(Hero, onclause=DataAggregationType.hero_id == Hero.id)
        clauses.append(DataAggregationType.by_hero == True)

    if comparison:
        select_query = select_query.join(ComparisonType, ComparisonType.id == GamePerformance.comparison_id)

    select_query = select_query.where(*clauses)

    output = await db_session.exec(select_query)
    return [{
        aggregation_type: agg_type_value,
        **model_obj.dict(include=fields), } for model_obj, agg_type_value in output.all()]
