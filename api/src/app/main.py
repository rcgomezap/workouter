from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from strawberry.fastapi import GraphQLRouter
from app.config.loader import load_config as get_config
from app.infrastructure.database.connection import init_database, close_database
from app.presentation.graphql.schema import schema
from app.presentation.graphql.context import Context
from app.presentation.middleware.auth import AuthMiddleware
from app.presentation.middleware.logging import LoggingMiddleware
from app.presentation.middleware.error_handler import ErrorHandlerExtension
from app.infrastructure.backup.scheduler import BackupScheduler
from app.dependencies import (
    get_exercise_service,
    get_muscle_group_service,
    get_routine_service,
    get_mesocycle_service,
    get_session_service,
    get_bodyweight_service,
    get_insight_service,
    get_calendar_service,
    get_backup_service,
)


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
        return {"status": "ok"}

    return app
