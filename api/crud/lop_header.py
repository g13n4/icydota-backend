from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import LoPShortDataData


async def get_lop_header(db_session: AsyncSession, league_id: int | None = None, patch_id: int | None = None) -> dict:
    if league_id is None and patch_id is None:
        raise TypeError("Parameter should be provided! League and Patch ids are empty!")
    elif (league_id and patch_id):
        raise TypeError("Only one parameter should be provided! Provided both League or Patch.")

    if league_id:
        where = LoPShortDataData.league_id == league_id
    else:
        where = LoPShortDataData.patch_id == patch_id

    data_obj = await db_session.exec(select(LoPShortDataData).where(where)).first()
    return data_obj.model_dump()
