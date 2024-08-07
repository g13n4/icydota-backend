import os
from typing import Optional, Annotated, Union

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlmodel import select

from api_helpers import get_performance_data, get_aggregated_performance_data, get_cross_comparison_performance_data, \
    to_table_format_cross_comparison, to_table_format, get_performance_data_comparison
from crud import get_items, get_categories_menu, get_field_types, \
    get_league_header, get_league_games, get_league_games_info, \
    get_default_menu_data
from db import get_sync_db_session, get_async_db_session
from models import PerformanceDataType, PerformanceDataCategory, League
from utils import CaseInsensitiveEnum


load_dotenv()

API_PREFIX = os.getenv('API_PREFIX', default='')
CORS_ADDRESS = os.getenv('CORS_ADDRESS', default="*")
LIGHT_MODE = os.getenv('LIGHT_MODE', default='off')

if LIGHT_MODE == 'on':
    LIGHT_MODE = True
    print("THE APP IS IN LIGHT MODE. DATA PARSING IS NOT POSSIBLE")
elif LIGHT_MODE == 'off':
    LIGHT_MODE = False
    print("THE APP IS IN FULL MODE. YOU CAN PARSE REPLAY DATA")
else:
    LIGHT_MODE = True
    print("WARNING, \"LIGHT_MODE\" VARIABLE IS NOT SET! IT WILL BE FORCEFULLY SET AS FALSE. PARSING IS DISABLED ")
    print(LIGHT_MODE)


# FASTAPI
icydota_api = FastAPI()


# CORS
origins = [
    CORS_ADDRESS
]

icydota_api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], )

icydota_api.add_middleware(GZipMiddleware, minimum_size=500)

# CHECKING IF CELERY IS RUNNING
# try:
#     celery_app.broker_connection().ensure_connection(max_retries=3)
# except Exception as ex:
#     raise RuntimeError("Failed to connect to celery broker, {}".format(str(ex)))
#

# TEST
@icydota_api.get(API_PREFIX + '/index/', status_code=200)
async def get_index():
    return {'hello': 'world'}


# MENUS
@icydota_api.get(API_PREFIX + '/menu_tc/')
async def get_menu_types_and_categories(comparison: bool | None = None, db=Depends(get_async_db_session)):
    categories = await get_categories_menu(db, include_disabled=not comparison)
    return categories


@icydota_api.get(API_PREFIX + '/league_header/')
async def get_league_header_api(db=Depends(get_async_db_session)):
    items = await get_league_header(db)
    return items


# DATA
class AggregationTypes(CaseInsensitiveEnum):
    position = "position"
    hero = "hero"
    player = "player"


class CrossAggregationTypes(CaseInsensitiveEnum):
    hero = "hero"
    player = "player"


class CrossAggregationPositions(CaseInsensitiveEnum):
    support = "support"
    carry = "core"
    mid = "mid"


class GameStage(CaseInsensitiveEnum):
    lane = "lane"
    game = "game"
    both = "both"

    @classmethod
    def __missing__(cls, value):
        return cls.both


class FieldTypes(CaseInsensitiveEnum):
    window = "window"
    total = "total"


@icydota_api.get(API_PREFIX + '/performance_data/{match_id}/{data_type}')
async def get_performance_data_api(match_id: int,
                                   data_type: int,
                                   game_stage: GameStage,
                                   comparison: Optional[str] = None,
                                   flat: bool = None,
                                   vertical: bool = True,
                                   db=Depends(get_async_db_session)):
    if (comparison and comparison) and flat is None:
        raise HTTPException(status_code=400, detail="Choose whether the data for comparison should be flat or percents")

    is_comparison = comparison in ["player", "general"]
    rows = []
    columns = []

    if not is_comparison:
        items, value_mapping, sum_total, rows = await get_performance_data(db_session=db,
                                                                           match_id=match_id,
                                                                           data_type=data_type,
                                                                           game_stage=game_stage.value,
                                                                           is_vertical=vertical)
    else:
        items, value_mapping, sum_total, rows = await get_performance_data_comparison(db_session=db,
                                                                                      match_id=match_id,
                                                                                      data_type=data_type,
                                                                                      game_stage=game_stage.value,
                                                                                      p_comparison=comparison == "player",
                                                                                      flat=flat, is_vertical=vertical)

    if vertical:
        columns = rows
        rows = ['type']

    output = to_table_format(items, value_mapping, rows, columns=columns, sum_total=sum_total, is_vertical=vertical)

    if not output:
        raise HTTPException(status_code=404)


    return output


@icydota_api.get(API_PREFIX + '/performance_aggregated_data/{league_id}/{data_type}/{aggregation_type}')
async def get_performance_aggregated_data_api(league_id: int,
                                              aggregation_type: AggregationTypes,
                                              game_stage: GameStage,
                                              data_type: int,
                                              comparison: bool = False,
                                              flat: bool = True,
                                              db=Depends(get_async_db_session)):
    if comparison and flat is None:
        raise HTTPException(status_code=400, detail="Choose whether the data for comparison should be flat or percents")

    items, value_mapping, sum_total = await get_aggregated_performance_data(db_session=db,
                                                                            league_id=league_id,
                                                                            aggregation_type=aggregation_type,
                                                                            data_type=data_type,
                                                                            game_stage=game_stage,
                                                                            is_comparison=comparison,
                                                                            flat=flat)

    if not items:
        raise HTTPException(status_code=404)

    output = to_table_format(items, value_mapping, [aggregation_type], sum_total=sum_total)

    return output


@icydota_api.get(API_PREFIX + '/performance_cross_comparison/{league_id}/{data_type}/{aggregation_type}/{position}')
async def get_performance_cross_comparison_data_api(league_id: int,
                                                    aggregation_type: CrossAggregationTypes,
                                                    position: CrossAggregationPositions,
                                                    data_field: str,
                                                    data_type: int,
                                                    flat: bool = True,
                                                    db=Depends(get_async_db_session)):
    # TODO:  "GET /performance_cross_comparison/15475/hero/mid/?data_field=l2&data_type=106&flat=false HTTP/1.1"

    data_dict, values_info = await get_cross_comparison_performance_data(db_session=db,
                                                                         league_id=league_id,
                                                                         aggregation_type=aggregation_type.value,
                                                                         position=position.value,
                                                                         data_type=data_type,
                                                                         data_field=data_field,
                                                                         flat=flat)

    if not data_dict.keys():
        raise HTTPException(status_code=404)

    output = to_table_format_cross_comparison(data=data_dict,
                                              values_info=values_info,
                                              aggregation_type=aggregation_type.value, )

    return output


# LISTS
@icydota_api.get(API_PREFIX + '/field/{field_type}/')
async def get_field_types_api(field_type: FieldTypes):
    field_types = await get_field_types(field_type)
    return field_types


@icydota_api.get(API_PREFIX + '/types/')
async def get_performance_types(db=Depends(get_async_db_session)):
    categories = await get_items(db, PerformanceDataType)
    return categories.all()


@icydota_api.get(API_PREFIX + '/leagues/')
async def get_leagues(db=Depends(get_async_db_session)):
    league_objs = await get_items(db, League)
    return league_objs.all()


@icydota_api.get(API_PREFIX + '/categories/')
async def get_performance_categories(db=Depends(get_async_db_session)):
    categories = await get_items(db, PerformanceDataCategory)
    return categories.all()


@icydota_api.get(API_PREFIX + '/types/{type_id}')
def get_performance_types(type_id: Optional[int],
                          db=Depends(get_sync_db_session)):
    types = db.exec(select(PerformanceDataType)
                    .where(PerformanceDataType.data_category_id == type_id)).all()

    return types


@icydota_api.get(API_PREFIX + '/games/{league_id}')
async def get_league_games_api(league_id: int, db=Depends(get_async_db_session)):
    categories = await get_league_games(db, league_id)
    return categories

@icydota_api.get(API_PREFIX + '/games_info/{league_id}')
async def get_league_games_info_api(league_id: int, db=Depends(get_async_db_session)):
    categories = await get_league_games_info(db, league_id)
    return categories


@icydota_api.get(API_PREFIX + '/default_menu_data/')
async def get_default_menu_data_api(db=Depends(get_async_db_session)):
    data = await get_default_menu_data(db)
    return data

# PROCESSING WITH CELERY
if not LIGHT_MODE:
    from tasks.process_helpers import process_league, process_game_helper
    from tasks_agg import approximate_positions_helper, aggregate_league_helper, cross_compare_league_helper, set_comparison_names_helper
    from tasks_agg.bulk_process import process_full_cycle, mass_process

    @icydota_api.post(API_PREFIX + '/process/league/{league_id}', status_code=202)
    async def process_league_api(league_id: int, overwrite: bool = False):
        new_games_number: int = process_league(league_id=league_id, overwrite=overwrite)
        if new_games_number:
            return {'status': f'processing {new_games_number} games'}

        return {'status': 'processed'}


    @icydota_api.post(API_PREFIX + '/process/match/{match_id}', status_code=202)
    async def process_match_api(match_id: int):
        process_game_helper(match_id=match_id, )
        return {'status': 'processing'}


    @icydota_api.post(API_PREFIX + '/aggregate/league/{league_id}', status_code=202)
    async def aggregate_league_api(league_id: int):
        aggregate_league_helper(league_id=league_id, )


    @icydota_api.post(API_PREFIX + '/aggregate/cross_comparison/{league_id}', status_code=202)
    async def create_cross_comparison_api(league_id: int):
        cross_compare_league_helper(league_id=league_id, )


    @icydota_api.post(API_PREFIX + '/approximate_positions/{league_id}', status_code=202)
    async def approximate_positions_api(league_id: int):
        approximate_positions_helper(league_id=league_id)


    @icydota_api.post(API_PREFIX + '/process/full_cycle/{league_id}', status_code=202)
    async def process_full_cycle_api(league_id: int):
        process_full_cycle(league_id=league_id)


    class ProcessTypes(CaseInsensitiveEnum):
        process_league = "process_league"
        aggregate_league = "aggregate_league"
        cross_compare_league = "cross_compare_league"


    @icydota_api.post(API_PREFIX + '/process/all/{process_type}', status_code=202)
    async def mass_process_api(process_type: ProcessTypes,
                               ids: Annotated[Union[list[int], None], Query()] = None):
        mass_process(process_type=process_type.value, league_ids=ids)


    @icydota_api.post(API_PREFIX + '/set_comparison_names', status_code=202)
    async def set_comparison_names_api():
        set_comparison_names_helper()


# if __name__ == "__main__":
#     import uvicorn
#
#
#     uvicorn.run("main:icydota_api", host='0.0.0.0', port=3333, reload=False, workers=1, use_colors=True)
