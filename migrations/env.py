import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from models import SQLModel
from dotenv import load_dotenv


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

load_dotenv()

# env
section = config.config_ini_section

POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_ADDRESS = os.environ.get("POSTGRES_ADDRESS")

PRODUCTION = os.environ.get("PRODUCTION", default=0)

config.set_section_option(section, "POSTGRES_ADDRESS", POSTGRES_ADDRESS)
config.set_section_option(section, "POSTGRES_DB", POSTGRES_DB)
config.set_section_option(section, "POSTGRES_PASSWORD", POSTGRES_PASSWORD)
config.set_section_option(section, "POSTGRES_USER", POSTGRES_USER)

config.set_main_option('sqlalchemy.url', f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_ADDRESS}/{POSTGRES_DB}")

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
metadata = SQLModel.metadata
metadata.naming_convention = convention
target_metadata = metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def _include_name(name, type_, parent_names):
    if type_ == "schema":
        return name
    else:
        return True


def skip_views(object, name: str, type_, reflected, compare_to):
    if type_ == 'table' and name.endswith('_view'):
        return False

    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        include_object=skip_views,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection,
                      target_metadata=target_metadata,
                      version_table_schema=target_metadata.schema,
                      compare_type=True,
                      include_object=skip_views,
                      include_schemas=False, )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
