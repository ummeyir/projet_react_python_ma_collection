from collections.abc import AsyncGenerator

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from core.config import settings

engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _migrate_entry_columns(connection: Connection) -> None:
    if not inspect(connection).has_table("entry"):
        return

    column_names = {column["name"] for column in inspect(connection).get_columns("entry")}
    if "status" not in column_names:
        connection.execute(
            text("ALTER TABLE entry ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'a_decouvrir'")
        )
    if "rating" not in column_names:
        connection.execute(text("ALTER TABLE entry ADD COLUMN rating INTEGER"))
    if "comment" not in column_names:
        connection.execute(text("ALTER TABLE entry ADD COLUMN comment TEXT"))
        if "notes" in column_names:
            connection.execute(text("UPDATE entry SET comment = notes WHERE notes IS NOT NULL"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS ix_entry_status ON entry (status)"))


def _migrate_item_columns(connection: Connection) -> None:
    if not inspect(connection).has_table("item"):
        return

    column_names = {column["name"] for column in inspect(connection).get_columns("item")}
    if "year" not in column_names:
        connection.execute(text("ALTER TABLE item ADD COLUMN year INTEGER"))


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def create_db_and_tables() -> None:
    from models import Entry, Item, User

    del Entry, Item, User
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
        await connection.run_sync(_migrate_entry_columns)
        await connection.run_sync(_migrate_item_columns)