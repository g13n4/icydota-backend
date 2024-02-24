from dotenv import load_dotenv
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from sqlmodel import select

from crud import get_items, get_performance_windows_items, get_performance_total_items
from db import get_sync_db_session
from models import PerformanceDataType, PerformanceDataCategory, League
from models import PerformanceTotalView, PerformanceWindowView
from tasks import process_league, process_game_helper


load_dotenv()

icydota_api = FastAPI()


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


@icydota_api.get('/types/')
def get_performance_types(db=Depends(get_sync_db_session)):
    categories = get_items(db, PerformanceDataType)
    return categories


@icydota_api.get('/leagues/')
def get_leagues(db=Depends(get_sync_db_session)):
    league_objs = get_items(db, League)
    return league_objs


@icydota_api.get('/performance_total_data/{league_id}')
def get_performance_total_data(league_id: int,
                               offset: int = 0,
                               limit: int = 120,
                               db=Depends(get_sync_db_session)):
    categories = get_performance_total_items(db, PerformanceTotalView, league_id=league_id, )
    return categories


@icydota_api.get('/performance_window_data/{league_id}/{data_type_id}')
def get_performance_window_data(league_id: int,
                                data_type_id: int,
                                offset: int = 0,
                                limit: int = 120,
                                db=Depends(get_sync_db_session)):
    categories = get_performance_windows_items(db, PerformanceWindowView,
                                               league_id=league_id, data_type_id=data_type_id, )
    return categories


@icydota_api.get('/process/league/{league_id}', status_code=202)
async def process_league_api(league_id: int, overwrite: bool = False):
    new_games_number: int = process_league(league_id=league_id, overwrite=overwrite)
    if not new_games_number:
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
