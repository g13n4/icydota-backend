import asyncio

from sqlmodel import SQLModel

from base_data_creation import create_buildings, create_positions, create_heroes, \
    create_performance_data_categories
from db import engine


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

        await conn.run_sync(create_buildings,
                            create_positions,
                            create_heroes,
                            create_performance_data_categories)


if __name__ == "__main__":
    asyncio.run(init_db())
