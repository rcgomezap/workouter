from contextlib import asynccontextmanager

import structlog
from fastapi import Depends, FastAPI, HTTPException
from strawberry.fastapi import GraphQLRouter

from app.config.loader import load_config as get_config
from app.dependencies import (
    get_backup_service,
    get_bodyweight_service,
    get_calendar_service,
    get_exercise_service,
    get_insight_service,
    get_mesocycle_service,
    get_muscle_group_service,
    get_routine_service,
    get_session_service,
)
from app.infrastructure.backup.scheduler import BackupScheduler
from app.infrastructure.database.connection import (
    close_database,
    init_database,
)
from app.infrastructure.database.connection import (
    ping_database as check_db,
)
from app.presentation.graphql.context import Context
from app.presentation.graphql.schema import schema
from app.presentation.middleware.auth import AuthMiddleware
from app.presentation.middleware.logging import LoggingMiddleware


async def get_context(
    exercise_service=Depends(get_exercise_service),
    muscle_group_service=Depends(get_muscle_group_service),
    routine_service=Depends(get_routine_service),
    mesocycle_service=Depends(get_mesocycle_service),
    session_service=Depends(get_session_service),
    bodyweight_service=Depends(get_bodyweight_service),
    insight_service=Depends(get_insight_service),
    calendar_service=Depends(get_calendar_service),
    backup_service=Depends(get_backup_service),
) -> Context:
    return Context(
        exercise_service=exercise_service,
        muscle_group_service=muscle_group_service,
        routine_service=routine_service,
        mesocycle_service=mesocycle_service,
        session_service=session_service,
        bodyweight_service=bodyweight_service,
        insight_service=insight_service,
        calendar_service=calendar_service,
        backup_service=backup_service,
    )


def create_app(engine=None, session_factory=None) -> FastAPI:
    config = get_config()

    # Capture parameters in a local dict to avoid closure issues
    overrides = {"engine": engine, "session_factory": session_factory}

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Database Initialization
        from app.infrastructure.database import connection

        if overrides["engine"]:
            connection._engine = overrides["engine"]
        if overrides["session_factory"]:
            connection._session_factory = overrides["session_factory"]

        if connection._engine is None:
            init_database(config)

        # SQLite Auto-Initialization
        if config.database.url.startswith("sqlite"):
            import subprocess
            from pathlib import Path

            # Extract path from URL (handle sqlite+aiosqlite:///path and sqlite:///path)
            db_path_str = config.database.url.split(":///")[1]
            db_path = Path(db_path_str)

            if not db_path.exists():
                logger = structlog.get_logger()
                logger.info("sqlite_db_not_found", path=str(db_path))

                # Ensure directory exists
                db_path.parent.mkdir(parents=True, exist_ok=True)

                # Run migrations via alembic
                try:
                    logger.info("running_migrations")
                    import os
                    import sys

                    # Try to find alembic in the same directory as python or in PATH
                    alembic_cmd = "alembic"
                    python_dir = os.path.dirname(sys.executable)
                    potential_alembic = os.path.join(python_dir, "alembic")
                    if os.path.exists(potential_alembic):
                        alembic_cmd = potential_alembic

                    subprocess.run(
                        [alembic_cmd, "upgrade", "head"], check=True, capture_output=True
                    )
                    logger.info("migrations_completed")

                    # Seed initial data
                    from app.infrastructure.seed import seed_muscle_groups

                    logger.info("seeding_initial_data")
                    await seed_muscle_groups(connection.get_session_factory())
                    logger.info("seeding_completed")
                except subprocess.CalledProcessError as e:
                    logger.error("migration_failed", error=e.stderr.decode())
                except Exception as e:
                    logger.error("migration_error", error=str(e))

        # Validate database connection
        logger = structlog.get_logger()
        if not await check_db():
            logger.error("database_connection_failed", url=config.database.url)
            # In production, we might want to exit or raise an error
            # For now, we'll log it and let the app start but it will fail on DB queries
        else:
            logger.info("database_connection_verified")

        # Initialize and start backup scheduler
        from app.infrastructure.backup.manager import BackupManager

        db_engine = connection.get_engine()
        backup_scheduler = None
        if db_engine:
            manager = BackupManager(config, db_engine)
            backup_scheduler = BackupScheduler(manager)
            backup_scheduler.start()

        yield

        # Shutdown
        if backup_scheduler:
            backup_scheduler.shutdown()
        await close_database()

    app = FastAPI(
        title="Workout Tracker API", version="0.1.0", debug=config.server.debug, lifespan=lifespan
    )

    # Middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)

    # GraphQL
    graphql_app = GraphQLRouter(
        schema,
        context_getter=get_context,
        graphql_ide="graphiql" if config.server.debug else None,
    )
    app.include_router(graphql_app, prefix="/graphql")

    # Health Check
    @app.get("/health")
    async def health():
        db_ok = await check_db()
        if not db_ok:
            raise HTTPException(status_code=503, detail="Database connection unavailable")
        return {"status": "ok", "database": "ok"}

    return app
