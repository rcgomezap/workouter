import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from app.main import create_app
from app.infrastructure.database.models.base import Base
from app.infrastructure.database import connection
from app.config.loader import load_config as get_config
import os


@pytest.fixture(scope="function")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="function")
async def test_engine(anyio_backend):
    config = get_config()
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=True,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Manually initialize the global engine/session factory in the app's connection module
    print(f"DEBUG: Setting connection._engine to {id(engine)}")
    connection._engine = engine

    connection._session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Ensure the database file is created and metadata is set up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()
    # Wait a bit before deleting to ensure all connections are closed
    import asyncio

    await asyncio.sleep(0.1)
    if os.path.exists("test_db.sqlite"):
        try:
            os.remove("test_db.sqlite")
        except PermissionError:
            pass


@pytest_asyncio.fixture
async def db_session(test_engine):
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(test_engine):
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    app = create_app(engine=test_engine, session_factory=session_factory)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers():
    config = get_config()
    return {"Authorization": f"Bearer {config.auth.api_key}"}
