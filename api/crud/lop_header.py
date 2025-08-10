from decimal import Decimal

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from constants.league_and_patch_short_data import LeaguePatchShortDataConstant, LOPShortDataValueFormat
from models import LoPShortData, LoPShortDataMomentum


def compare_value_to_bool(value: int | float | Decimal, cmp_value: int | float | Decimal):
    if value > cmp_value:
        return True
    elif value < cmp_value:
        return False
    else:
        return None


def process_value(field: str, value: int | float | Decimal):
    match getattr(LeaguePatchShortDataConstant, field).value_format:
        case LOPShortDataValueFormat.RAW:
            return str(value)
        case LOPShortDataValueFormat.PERCENT:
            return f"{value * 100:.1f}%"
        case LOPShortDataValueFormat.LEVEL:
            return f"{value} lvl"
        case LOPShortDataValueFormat.TIME:
            return f'{value // 60}:{value % 60:02}'

    return None


def create_value(key: str, data_obj: LoPShortData, momentum_obj: LoPShortDataMomentum | None):
    data_value = getattr(data_obj, key)
    item = dict()

    item["label"] = getattr(LeaguePatchShortDataConstant, key).description
    item["value"] = process_value(field=key, value=data_value)

    if momentum_obj is not None and getattr(momentum_obj, key, None) is not None:
        momentum_value = getattr(momentum_obj, key)
        item["cmp_value"] = process_value(field=key, value=momentum_value)
        item["cmp_mom"] = compare_value_to_bool(value=data_value, cmp_value=momentum_value)

    return item


async def get_lop_header(db_session: AsyncSession, league_id: int | None = None, patch_id: int | None = None) -> dict:
    if league_id is None and patch_id is None:
        raise TypeError("Parameter should be provided! League and Patch ids are empty!")
    elif (league_id and patch_id):
        raise TypeError("Only one parameter should be provided! Provided both League or Patch.")

    if league_id:
        where = LoPShortData.league_id == league_id
    else:
        where = LoPShortData.patch_id == patch_id

    aquery = (await db_session.exec(
        select(LoPShortData, LoPShortDataMomentum)
        .join(LoPShortDataMomentum, LoPShortDataMomentum.data_id == LoPShortData.id, isouter=True)
        .where(where)
    )).first()

    if aquery is None:
        raise HTTPException(status_code=404)

    data_obj, momentum_obj = aquery

    return {
        "data": {
            item.name: create_value(key=item.name, data_obj=data_obj, momentum_obj=momentum_obj) for item in
            LeaguePatchShortDataConstant.VALUES
        },
        "patch": momentum_obj.compared_to,
    }
