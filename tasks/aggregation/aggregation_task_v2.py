from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd

from constants.calculation.game.calculation_types import WindowCalculations
from constants.performance.total import GameTotals
from constants.performance.window import AllWindows, WINDOWS_BY_MASK
from db import get_sync_db_session
from models import AggregationType, ComparisonType, League
from models.performance import Performance
from modules.empty_mask_converter import EmptyMaskConverter
from modules.processors.totals import TotalPerformanceProcessor
from modules.processors.windows import WindowsPerformanceProcessor
from modules.query_creators.aggregation_query_creator_function import aggregation_query_creator
from tasks.aggregation.helpers import league_participants_data_query_creator, AggregationKeyCreator, COMPARISON_MAP
from sqlmodel import Session
from celery import shared_task


DATA_MODEL_FK_FIELDS = ['id', 'game_performance_id']
# comparison / is_flat
FLAT_LIST = [(False, None), (True, True), (True, False), ]


def process_data(data: list[dict[str, Any]], group_by: list[str], is_window: bool) -> Iterable:
    df = pd.DataFrame(data)
    df.replace([np.inf, -np.inf, np.nan], None, inplace=True)

    columns = AllWindows.VALUES_NAMES if is_window else GameTotals.VALUES_NAMES
    aggregated_df = df.groupby(group_by)[columns].mean()

    for idx, this_values_dict in aggregated_df.reset_index().T.to_dict().items():
        yield this_values_dict


def _process_mask(mask_name: str, mask: int | None) -> dict:
    if mask is None:
        return { }

    windows = WINDOWS_BY_MASK[mask_name].VALUES_NAMES
    return EmptyMaskConverter.mask_to_dict(mask, windows)


def unpack_row(row: Iterable, names: list[str]) -> dict[str, Any]:
    output_mask = { }
    output = { }

    for name, value in zip(names, row):
        if name in ['l_empty_mask', 'g_empty_mask']:
            mask_data = _process_mask(name, value)
            output_mask.update(mask_data)
        elif name in ['window_table', 'total_data']:
            model_dump = value.model_dump(exclude=set(DATA_MODEL_FK_FIELDS))
            output.update(model_dump)
        else:
            output[name] = value

    output.update(output_mask)
    return output


def create_performance_objs(
        db_session,
        league_id: int,
        AGC: AggregationKeyCreator,
        ) -> dict[tuple, Performance]:
    output = dict()
    query, names = league_participants_data_query_creator(league_id=league_id)
    league_participants = db_session.exec(query)

    for row in league_participants:
        row_data = { name: value for name, value in zip(row, names) }
        required_row_data = AGC.create_dict(row_data)

        for is_comparison, is_flat in FLAT_LIST:
            row_key = AGC.create_key(row_data, append=is_flat)

            aggregation_obj = AggregationType(
                type_id=AGC.type_id,
                **required_row_data,
            )

            comparison_obj = None
            if is_comparison:
                comparison_data = { COMPARISON_MAP[name].cpd: value for name, value in required_row_data.items() }

                comparison_obj = ComparisonType(
                    flat=is_flat,
                    basic=False,
                    **comparison_data,
                )

            performance_type = Performance.const.game.AGGREGATION_COMPARISON if is_comparison \
                else Performance.const.game.AGGREGATION

            performance_obj = Performance(
                type_id=performance_type,
                aggregation_type=aggregation_obj,
                comparison_type=comparison_obj,
            )
            output[row_key] = performance_obj

            db_session.add(performance_obj)

    return output


def get_query_data(db_session, query, names: list[str]) -> list[dict]:
    query_output = db_session.exec(query)

    data = list()
    for row in query_output.all():
        row_data = unpack_row(row, names)
        data.append(row_data)

    return data


@shared_task(name="aggregate_league", ignore_result=True)
def aggregation_task(league_id: int, aggregation_type: int):
    db_session: Session = get_sync_db_session(expire=False)

    league_obj = db_session.get(League, league_id)
    if not league_obj:
        raise ValueError("No such league in the database")

    AGC = AggregationKeyCreator(aggregation_type)
    columns = AGC.get_fields()

    performance_dict = create_performance_objs(db_session=db_session, league_id=league_id, AGC=AGC)

    for is_comparison, is_flat in FLAT_LIST:
        for calculation in WindowCalculations.VALUES:
            query, names = aggregation_query_creator(
                league_id=league_id,
                data_calculation_id=calculation.value,
                is_comparison=is_comparison,
                is_flat=is_flat,
            )
            data = get_query_data(db_session=db_session, query=query, names=names)

            for window_data in process_data(data=data, group_by=columns, is_window=True):
                key = AGC.create_key(window_data, append=is_flat)
                PWD_obj = WindowsPerformanceProcessor.get_pwd_from_iterable(window_data, calculation.value)
                PWD_obj.game_performance = performance_dict[key]
                db_session.add(PWD_obj)

            db_session.commit()

        query, names = aggregation_query_creator(
            league_id=league_id,
            data_calculation_id=None,
            is_comparison=is_comparison,
            is_flat=is_flat,
        )
        data = get_query_data(db_session=db_session, query=query, names=names)

        for total_data in process_data(data=data, group_by=columns, is_window=False):
            key = AGC.create_key(total_data, append=is_flat)
            PTD_obj = TotalPerformanceProcessor.create_object_from_dict(total_data)
            PTD_obj.game_performance = performance_dict[key]
            db_session.add(PTD_obj)

        db_session.commit()



