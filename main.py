from typing import Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from crud import get_items, get_categories_menu, \
    get_league_header, get_league_games, \
    get_performance_data, get_aggregated_performance_data
from db import get_sync_db_session, get_async_db_session
from models import PerformanceDataType, PerformanceDataCategory, League, Game
from tasks import process_league, process_game_helper
from utils import (to_table_format, CaseInsensitiveEnum, )


icydota_api = FastAPI()

origins = [
    "*"
]

icydota_api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], )

load_dotenv()


# TEST
@icydota_api.get('/test/')
async def get_performance_data_api(db=Depends(get_sync_db_session)):
    items = await get_performance_data(db_session=db,
                                       match_id=7206846711,
                                       data_type="total",
                                       comparison=None,
                                       flat=False)

    output = to_table_format(items, ['player'])

    return output


# MENUS
@icydota_api.get('/menu_tc/')
async def get_menu_types_and_categories(db=Depends(get_async_db_session)):
    categories = await get_categories_menu(db, PerformanceDataCategory)
    return categories


@icydota_api.get('/league_header/')
async def get_league_header_api(db=Depends(get_async_db_session)):
    items = await get_league_header(db, League)
    return items


# DATA
class AggregationTypes(CaseInsensitiveEnum):
    position = "position"
    hero = "hero"
    player = "player"


class ComparisonTypes(CaseInsensitiveEnum):
    general = "general"
    player = "player"
    none = None


@icydota_api.get('/performance_data/{match_id}/')
async def get_performance_data_api(match_id: int,
                                   data_type: int | str | None = None,
                                   comparison: ComparisonTypes | None = None,
                                   flat: bool = True,
                                   db=Depends(get_async_db_session)):
    print(data_type, flat, comparison.value)

    if not data_type:
        raise HTTPException(status_code=400, detail="Provide data_type_id or total parameters")

    if comparison and flat is None:
        raise HTTPException(status_code=400, detail="Choose whether the data for comparison should be flat or percents")

    items = await get_performance_data(db_session=db,
                                       match_id=match_id,
                                       data_type=data_type,
                                       comparison=(comparison and comparison.value),
                                       flat=flat)

    output = to_table_format(items, ['player'])

    return output


@icydota_api.get('/performance_aggregated_data/{league_id}/{aggregation_type}/')
async def get_performance_aggregated_data_api(league_id: int,
                                              aggregation_type: AggregationTypes,
                                              data_type: int | str | None = None,
                                              comparison: ComparisonTypes | None = None,
                                              flat: bool = True,
                                              db=Depends(get_async_db_session)):
    if comparison and flat is None:
        raise HTTPException(status_code=400, detail="Choose whether the data for comparison should be flat or percents")

    items = await get_aggregated_performance_data(db_session=db,
                                                  league_id=league_id,
                                                  aggregation_type=aggregation_type.value,
                                                  data_type=data_type,
                                                  comparison=(comparison and comparison.value),
                                                  flat=flat)

    output = to_table_format(items, [aggregation_type.value])

    return output


# LISTS
@icydota_api.get('/types/')
def get_performance_types(db=Depends(get_sync_db_session)):
    categories = get_items(db, PerformanceDataType)
    return categories


@icydota_api.get('/leagues/')
def get_leagues(db=Depends(get_sync_db_session)):
    league_objs = get_items(db, League)
    return league_objs


@icydota_api.get('/categories/')
def get_performance_categories(db=Depends(get_sync_db_session)):
    categories = get_items(db, PerformanceDataCategory)
    return categories


@icydota_api.get('/types/{type_id}')
def get_performance_types(type_id: Optional[int],
                          db=Depends(get_sync_db_session)):
    types = db.exec(select(PerformanceDataType)
                    .where(PerformanceDataType.data_category_id == type_id)).all()

    return types


@icydota_api.get('/games/{league_id}')
async def get_league_games_api(league_id: int, db=Depends(get_sync_db_session)):
    categories = await get_league_games(db, Game, league_id)
    return categories


# PROCESSING WITH CELERY
@icydota_api.get('/process/league/{league_id}', status_code=202)
async def process_league_api(league_id: int, overwrite: bool = False):
    new_games_number: int = process_league(league_id=league_id, overwrite=overwrite)
    if new_games_number:
        return {'status': f'processing {new_games_number} games'}

    return {'status': 'processed'}


@icydota_api.get('/process/match/{match_id}', status_code=202)
async def process_match_api(match_id: int):
    process_game_helper(match_id=match_id, )
    return {'status': 'processing'}


@icydota_api.get('/aggregate_league/{league_id}', status_code=202)
async def aggregate_league_api(league_id: int):
    process_league(league_id=league_id, )
    return {'status': 'processing'}


if __name__ == "__main__":
    uvicorn.run("main:icydota_api", host='0.0.0.0', port=8000, reload=True, workers=3)
