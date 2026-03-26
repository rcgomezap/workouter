import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.loader import load_config
from app.infrastructure.database.models.muscle_group import MuscleGroupTable

MUSCLE_GROUPS = [
    "Chest", "Back", "Shoulders", "Biceps", "Triceps",
    "Quads", "Hamstrings", "Glutes", "Calves", "Abs",
    "Forearms", "Traps", "Lats"
]

async def seed():
    config = load_config()
    engine = create_async_engine(config.database.url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with session_factory() as session:
        for name in MUSCLE_GROUPS:
            stmt = select(MuscleGroupTable).where(MuscleGroupTable.name == name)
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                session.add(MuscleGroupTable(name=name))
                print(f"Adding muscle group: {name}")
        
        await session.commit()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
