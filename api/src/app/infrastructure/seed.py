import asyncio
from app.config.loader import load_config as get_config
from app.infrastructure.database.connection import init_database, get_session_factory
from app.infrastructure.database.models.muscle_group import MuscleGroup
from sqlalchemy import select

MUSCLE_GROUPS = [
    "Chest", "Back", "Shoulders", "Biceps", "Triceps", "Forearms", 
    "Quadriceps", "Hamstrings", "Glutes", "Calves", "Abs", "Traps", 
    "Lats", "Neck", "Hip Flexors", "Adductors", "Abductors"
]

async def seed_muscle_groups():
    config = get_config()
    init_database(config)
    session_factory = get_session_factory()
    
    async with session_factory() as session:
        for name in MUSCLE_GROUPS:
            stmt = select(MuscleGroup).where(MuscleGroup.name == name)
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                mg = MuscleGroup(name=name)
                session.add(mg)
        
        await session.commit()
        print("Muscle groups seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_muscle_groups())
