"""A module providing database access."""

import asyncio

import databases
import sqlalchemy
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.exc import OperationalError, DatabaseError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.mutable import MutableList
from asyncpg.exceptions import ( 
    CannotConnectNowError,
    ConnectionDoesNotExistError,
)

from mealapi.config import config
from mealapi.core.domain.report import ReportReason, ReportStatus
from mealapi.core.domain.user import UserRole

metadata = sqlalchemy.MetaData()

user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column(
        "id",
        pgUUID,
        primary_key=True,
    ),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column(
        "role",
        sqlalchemy.Enum(UserRole),
        server_default=sqlalchemy.text("'USER'")
    ),
)

rating_table = sqlalchemy.Table(
    "ratings",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("author", pgUUID, sqlalchemy.ForeignKey("users.id", ondelete="CASCADE")),
    sqlalchemy.Column(
        "recipe_id", 
        sqlalchemy.Integer, 
        sqlalchemy.ForeignKey("recipes.id", ondelete="CASCADE")
    ),
    sqlalchemy.Column("value", sqlalchemy.Integer),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime(timezone=True)),
)

comment_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("author", pgUUID, sqlalchemy.ForeignKey("users.id", ondelete="CASCADE")),
    sqlalchemy.Column(
        "recipe_id", 
        sqlalchemy.Integer, 
        sqlalchemy.ForeignKey("recipes.id", ondelete="CASCADE")
    ),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime(timezone=True)),
    sqlalchemy.Column("content", sqlalchemy.String),
    sqlalchemy.Column(
        "rating_id", 
        sqlalchemy.Integer, 
        sqlalchemy.ForeignKey("ratings.id", ondelete="SET NULL"),
        nullable=True
    ),
)

report_table = sqlalchemy.Table(
    "reports",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("reporter_id", pgUUID, sqlalchemy.ForeignKey("users.id", ondelete="CASCADE")),
    sqlalchemy.Column("recipe_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("recipes.id", ondelete="CASCADE")), 
    sqlalchemy.Column("comment_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("comments.id", ondelete="CASCADE")),
    sqlalchemy.Column("reason", sqlalchemy.Enum(ReportReason)),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime),
    sqlalchemy.Column(
        "status",
        sqlalchemy.Enum(ReportStatus),
        server_default=sqlalchemy.text("'PENDING'")
    ),
    sqlalchemy.Column("resolved_by", pgUUID, sqlalchemy.ForeignKey("users.id", ondelete="SET NULL")),
    sqlalchemy.Column("resolution_note", sqlalchemy.String),
    sqlalchemy.Column("resolved_at", sqlalchemy.DateTime),
)
recipe_table = sqlalchemy.Table(
    "recipes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, index=True),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("instructions", sqlalchemy.String),
    sqlalchemy.Column("category", sqlalchemy.String, index=True),
    sqlalchemy.Column("author", pgUUID, sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), index=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime),
    sqlalchemy.Column("preparation_time", sqlalchemy.Integer, index=True),
    sqlalchemy.Column("servings", sqlalchemy.Integer),
    sqlalchemy.Column("difficulty", sqlalchemy.String),
    sqlalchemy.Column("average_rating", sqlalchemy.Float, default=0.0, index=True),
    sqlalchemy.Column("ingredients", MutableList.as_mutable(sqlalchemy.ARRAY(sqlalchemy.String))),
    sqlalchemy.Column("steps", MutableList.as_mutable(sqlalchemy.ARRAY(sqlalchemy.String))),
    sqlalchemy.Column("tags", MutableList.as_mutable(sqlalchemy.ARRAY(sqlalchemy.String)), default=[]),
    sqlalchemy.Column("ai_detected", sqlalchemy.Float, nullable=True)
)
db_uri = (
    f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASSWORD}"
    f"@{config.DB_HOST}/{config.DB_NAME}"
)

engine = create_async_engine(
    db_uri,
    echo=True,
    future=True,
    pool_pre_ping=True,
)

database = databases.Database(
    db_uri,
    force_rollback=True,
)


async def init_db(retries: int = 5, delay: int = 5) -> None:
    """Function initializing the DB.

    Args:
        retries (int, optional): Number of retries of connect to DB.
            Defaults to 5.
        delay (int, optional): Delay of connect do DB. Defaults to 2.
    """
    for attempt in range(retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(metadata.create_all)
            return
        except (
            OperationalError,
            DatabaseError,
            CannotConnectNowError,
            ConnectionDoesNotExistError,
        ) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(delay)

    raise ConnectionError("Could not connect to DB after several retries.")