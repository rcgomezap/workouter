from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config.schema import Config


# Global engine and session factory
_engine = None
_session_factory = None


def init_database(config: Config) -> None:
    global _engine, _session_factory
    
    _engine = create_async_engine(
        config.database.url,
        echo=config.database.echo,
        future=True,
    )
    
    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        from app.config.loader import load_config
        init_database(load_config())
    return _session_factory


def get_engine():
    return _engine


async def close_database() -> None:
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
