from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from constants.league_and_patch_short_data import LeaguePatchShortDataConstant
from models import LoPShortData


async def get_lop_header(db_session: AsyncSession, league_id: int | None = None, patch_id: int | None = None) -> dict:
    if league_id is None and patch_id is None:
        raise TypeError("Parameter should be provided! League and Patch ids are empty!")
    elif (league_id and patch_id):
        raise TypeError("Only one parameter should be provided! Provided both League or Patch.")

    if league_id:
        where = LoPShortData.league_id == league_id
    else:
        where = LoPShortData.patch_id == patch_id

    data_obj = await db_session.exec(select(LoPShortData).where(where)).first()

    return {
        key: { "label": getattr(LeaguePatchShortDataConstant, key).description, "value": value } for key, value in
        data_obj.model_dump(exclude={ "id", "league_id", "patch_id" }).items()
    }
