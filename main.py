import os

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from api.crud.cross_comparison_field import get_cross_comparison_fields
from api.crud.graph_data import get_graph_data
from api.crud.initial_data import get_initial_data
from api.crud.lop_header import get_lop_header
from api.crud.match import get_games
from api.crud.match_all import get_games_all
from api.table.match_name import get_match_name_data
from api.table.table_data import get_performance_data, get_performance_data_comparison, get_aggregated_performance_data, \
    get_cross_comparison_performance_data
from api.table.table_formatting import to_table_format_cross_comparison, to_table_format
from api.task_helpres.process_mispositioned import process_mispositioned_games
from celery_app import celery_app
from constants.api import GameStageEnum, ComparisonEnum, ComparisonTypeEnum, PoTEnum, LoPEnum
from constants.task_reason import TaskReason
from db import get_async_db_session


__all__ = ['celery_app']

load_dotenv()

API_PREFIX = os.getenv('API_PREFIX', default='')
if API_PREFIX:
    API_PREFIX = '/' + API_PREFIX

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
backend_api = FastAPI(default_response_class=ORJSONResponse)

# CORS
backend_api.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ADDRESS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backend_api.add_middleware(GZipMiddleware, minimum_size=500)


# TEST
@backend_api.get(API_PREFIX + '/index/', status_code=200)
async def get_index():
    return { 'hello': 'world' }


@backend_api.get(API_PREFIX + '/initial')
async def get_initial_data_route(db_session: AsyncSession = Depends(get_async_db_session)) -> dict:
    items = await get_initial_data(db_session)
    return items


@backend_api.get(API_PREFIX + '/graph/{match_id}/{position}')
async def get_graph_position_route(
        match_id: int,
        position: int,
        db_session: AsyncSession = Depends(get_async_db_session),
) -> dict:
    data = await get_graph_data(adb_session=db_session, match_id=match_id, position=position)
    return data


@backend_api.get(API_PREFIX + '/cross-comparison/fields')
async def get_cross_comparison_fields_route() -> dict:
    items = await get_cross_comparison_fields()
    return items


@backend_api.get(API_PREFIX + '/league/{league_id}')
async def get_league_matches_route(
        league_id: int,
        db_session: AsyncSession = Depends(get_async_db_session),
) -> dict:
    output = await get_games(db_session, league_id=league_id)
    return output


@backend_api.get(API_PREFIX + '/all/{lop}/{lod_id}')
async def get_league_matches_route(
        lop: LoPEnum,
        lod_id: int,
        db_session: AsyncSession = Depends(get_async_db_session),
        limit: int = 48,
        offset: int = 0,
) -> dict:
    if lop == LoPEnum.league:
        output = await get_games_all(db_session=db_session, league_id=lod_id, limit=limit, offset=offset)
    else:
        output = await get_games_all(db_session=db_session, patch_id=lod_id, limit=limit, offset=offset)

    if not output:
        raise HTTPException(status_code=404)

    return { "data": output }


@backend_api.get(API_PREFIX + '/header/{lop}/{lod_id}')
async def get_league_matches_route(
        lop: LoPEnum,
        lod_id: int,
        db_session: AsyncSession = Depends(get_async_db_session),
) -> dict:
    if lop == LoPEnum.league:
        output = await get_lop_header(db_session=db_session, league_id=lod_id)
    else:
        output = await get_lop_header(db_session=db_session, patch_id=lod_id)

    return output


# DATA
@backend_api.get(API_PREFIX + '/data/match/{pot}/{match_id}/{data_type}')
async def get_performance_data_api(
        pot: PoTEnum,
        match_id: int,
        data_type: int,
        # qparams
        ctype: ComparisonTypeEnum | None = None,
        stage: GameStageEnum | None = None,
        comp: ComparisonEnum = ComparisonEnum.none,
        db=Depends(get_async_db_session)
):
    flat = comp.to_value()
    ctype_value = ctype and ctype.to_value()
    stage = stage and stage.value
    name_data_dict = await get_match_name_data(adb_session=db, match_id=match_id)
    data_type_id = data_type if data_type else None

    if flat is None:
        items, value_mapping, sum_total, rows = await get_performance_data(
            db_session=db,
            pot=pot,
            match_id=match_id,
            data_type=data_type_id,
            game_stage=stage,
        )
    else:
        items, value_mapping, sum_total, rows = await get_performance_data_comparison(
            db_session=db,
            pot=pot,
            match_id=match_id,
            calculation_type_id=data_type_id,
            game_stage=stage,
            basic=ctype_value,
            flat=flat,
        )

    if not items:
        raise HTTPException(status_code=404)

    output = to_table_format(items, value_mapping, rows, is_total=data_type_id is None)
    output["matchName"] = name_data_dict

    return output


@backend_api.get(API_PREFIX + '/data/aggregation/{pot}/{lop}/{lop_value}/{data_type}')
async def get_performance_aggregated_data_api(
        pot: PoTEnum,
        lop: LoPEnum,
        lop_value: int,
        data_type: int,
        # qparams
        atype: int | None = None,
        stage: GameStageEnum | None = None,
        comp: ComparisonEnum = ComparisonEnum.none,
        db=Depends(get_async_db_session)
):
    league_id, patch_id = lop.to_api(lop_value)
    flat = comp.to_value()
    game_stage = stage and stage.value
    data_type_id = data_type if data_type else None

    data, value_mapping, sum_total, header_fields = await get_aggregated_performance_data(
        db_session=db,
        pot=pot,
        league_id=league_id,
        patch_id=patch_id,
        aggregation_type=atype,
        calculation_type_id=data_type_id,
        game_stage=game_stage,
        flat=flat
    )

    if not data or not all(data):
        raise HTTPException(status_code=404)

    output = to_table_format(data, value_mapping, header_fields, is_total=data_type_id is None)

    return output


@backend_api.get(API_PREFIX + '/data/cross_comparison/{pot}/{lop}/{lop_value}/{data_type}')
async def get_performance_cross_comparison_data_api(
        pot: PoTEnum,
        lop: LoPEnum,
        lop_value: int,
        data_type: int,
        # qparams
        field: str,
        comp: ComparisonEnum = ComparisonEnum.flat,
        position: int | None = None,
        atype: int | None = None,
        db=Depends(get_async_db_session)
):
    league_id, patch_id = lop.to_api(lop_value)
    flat = comp.to_value()
    data_type_id = data_type if data_type else None

    data, header_name, columns, values_info = await get_cross_comparison_performance_data(
        db_session=db,
        pot=pot,
        league_id=league_id,
        patch_id=patch_id,
        aggregation_type=atype,
        position=position,
        data_field=field,
        calculation_type_id=data_type_id,
        flat=flat,
    )

    if not data or not all(data):
        raise HTTPException(status_code=404)

    output = to_table_format_cross_comparison(
        data=data,
        values_info=values_info,
        header_name=header_name,
        columns=columns,
    )

    return output


# PROCESSING WITH CELERY
if not LIGHT_MODE:
    from tasks.bulk_aggregation_process import process_full_cycle
    from tasks.aggregation_tasks_helper import aggregate_task_helper, cross_compare_task_helper, \
        approximate_positions_helper, set_comparison_names_helper, delete_league_task_helper, \
        delete_cross_comparison_task_helper, parallel_cross_comparison_task_helper, parallel_aggregate_task_helper
    from tasks.league.process_league import process_league_task_group, check_leagues_for_correctness
    from tasks.league.process_match import process_game_helper


    @backend_api.post(API_PREFIX + '/process/league/{league_id}', status_code=202)
    async def process_league_api(league_id: int, overwrite: bool = False):
        new_games_number, _ = process_league_task_group(league_id=league_id, overwrite=overwrite, execute=True)
        if new_games_number:
            return { 'status': f'processing {new_games_number} games' }

        return { 'status': 'processed' }


    @backend_api.post(API_PREFIX + '/process/all-mispositioned', status_code=202)
    async def process_all_mispositioned_api():
        process_mispositioned_games()
        return { 'status': 'processed' }


    @backend_api.post(API_PREFIX + '/process/match/{match_id}', status_code=202)
    async def process_match_api(match_id: int):
        process_game_helper(match_id=match_id, execute=True, reason=TaskReason.PROCESS_ONE_MATCH)
        return { 'status': 'processing' }


    # AGGREGATION
    @backend_api.delete(API_PREFIX + '/aggregate/{lop}/{lop_value}', status_code=204)
    async def delete_aggregation_api(lop: LoPEnum, lop_value: int):
        league_id, patch_id = lop.to_api(lop_value)
        delete_league_task_helper(league_id=league_id, patch_id=patch_id)


    @backend_api.post(API_PREFIX + '/aggregate/{lop}/{lop_value}', status_code=202)
    async def create_aggregation_api(lop: LoPEnum, lop_value: int, atype: int | None = None, preload: bool = False):
        league_id, patch_id = lop.to_api(lop_value)
        aggregate_task_helper(league_id=league_id, patch_id=patch_id, atype=atype, preload_all=preload)


    @backend_api.post(API_PREFIX + '/aggregate-parallel/{lop}/{lop_value}', status_code=202)
    async def create_aggregation_parallel_api(lop: LoPEnum, lop_value: int):
        league_id, patch_id = lop.to_api(lop_value)
        parallel_aggregate_task_helper(league_id=league_id, patch_id=patch_id)


    # CROSS-COMPARISON
    @backend_api.delete(API_PREFIX + '/cross_comparison/{lop}/{lop_value}', status_code=204)
    async def delete_cross_comparison_api(lop: LoPEnum, lop_value: int):
        league_id, patch_id = lop.to_api(lop_value)
        delete_cross_comparison_task_helper(league_id=league_id, patch_id=patch_id)


    @backend_api.post(API_PREFIX + '/cross_comparison/{lop}/{lop_value}', status_code=202)
    async def create_cross_comparison_api(lop: LoPEnum, lop_value: int, preload: bool = False):
        league_id, patch_id = lop.to_api(lop_value)
        cross_compare_task_helper(league_id=league_id, patch_id=patch_id, preload_all=preload)


    @backend_api.post(API_PREFIX + '/cross-comparison-parallel/{lop}/{lop_value}', status_code=202)
    async def create_cross_comparison_parallel_api(lop: LoPEnum, lop_value: int):
        league_id, patch_id = lop.to_api(lop_value)
        parallel_cross_comparison_task_helper(league_id=league_id, patch_id=patch_id)


    # UTILS
    @backend_api.post(API_PREFIX + '/approximate_positions/{league_id}', status_code=202)
    async def approximate_positions_api(league_id: int):
        approximate_positions_helper(league_id=league_id)


    @backend_api.post(API_PREFIX + '/process/full_cycle/{league_id}', status_code=202)
    async def process_full_cycle_api(league_id: int):
        process_full_cycle(league_id=league_id)


    @backend_api.post(API_PREFIX + '/set_comparison_names', status_code=202)
    async def set_comparison_names_api(league_id: int | None = None):
        set_comparison_names_helper(league_id=league_id)


    @backend_api.post(API_PREFIX + '/check_leagues', status_code=202)
    async def check_leagues():
        check_leagues_for_correctness()

