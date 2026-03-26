import asyncio

from sqlalchemy import select

# Import all models to ensure SQLAlchemy can resolve relationships
import app.infrastructure.database.models  # noqa: F401
from app.config.loader import load_config as get_config
from app.infrastructure.database.connection import get_session_factory, init_database
from app.infrastructure.database.models.muscle_group import MuscleGroupTable

MUSCLE_GROUPS = [
    "Chest",
    "Back",
    "Shoulders",
    "Biceps",
    "Triceps",
    "Forearms",
    "Quadriceps",
    "Hamstrings",
    "Glutes",
    "Calves",
    "Abs",
    "Traps",
    "Lats",
    "Neck",
    "Hip Flexors",
    "Adductors",
    "Abductors",
]


async def seed_muscle_groups(session_factory=None):
    if session_factory is None:
        config = get_config()
        init_database(config)
        session_factory = get_session_factory()

    async with session_factory() as session:
        for name in MUSCLE_GROUPS:
            stmt = select(MuscleGroupTable).where(MuscleGroupTable.name == name)
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                mg = MuscleGroupTable(name=name)
                session.add(mg)

        await session.commit()
        # print("Muscle groups seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed_muscle_groups())
