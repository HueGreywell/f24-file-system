import os

import asyncpg
import pytest

from app.repositories.filesystem_repository import FileSystemRepository

TEST_DSN = os.environ.get(
    "TEST_DATABASE_DSN", "postgresql://f24:change-me@localhost:5433/f24"
)


@pytest.fixture
async def connection():
    try:
        conn = await asyncpg.connect(dsn=TEST_DSN)
    except (OSError, asyncpg.PostgresError) as error:
        pytest.skip(
            f"No test database reachable at {TEST_DSN} ({error}). "
            "Run `docker compose up -d postgres` first."
        )

    transaction = conn.transaction()
    await transaction.start()
    try:
        yield conn
    finally:
        await transaction.rollback()
        await conn.close()


@pytest.fixture
def repository(connection):
    return FileSystemRepository(connection)
