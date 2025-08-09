from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from constants.league_and_patch_short_data import LeaguePatchShortDataConstant
from models import LoPShortData, LoPShortDataMomentum


def create_value(key: str, value: float | None, momentum_obj: LoPShortDataMomentum | None):
    item = {
        "label": getattr(LeaguePatchShortDataConstant, key).description,
        "value": value,
    }

    if momentum_obj is not None:
        item["mom"] = getattr(momentum_obj, key)
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

    data_obj, momentum_obj = await db_session.exec(
        select(LoPShortData, LoPShortDataMomentum)
        .join(LoPShortDataMomentum, LoPShortDataMomentum.data_id == LoPShortData.id, isouter=True)
        .where(where)
    ).first()

    return {
        key: create_value(key=key, value=value, momentum_obj=momentum_obj) for key, value in
        data_obj.model_dump(exclude={ "id", "league_id", "patch_id" }).items()
    }
