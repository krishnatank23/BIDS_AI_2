import asyncio
import sys
import os

# Add the current directory to sys.path to import app
sys.path.append(os.getcwd())

from app.db.database import engine, init_db
from app.db.models import Project

async def test():
    print("Testing database connection...")
    try:
        await init_db()
        print("✓ Database tables initialized/verified.")
        
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        async_session_factory = async_sessionmaker(engine, class_=AsyncSession)
        
        async with async_session_factory() as session:
            from sqlalchemy import select
            res = await session.execute(select(Project).limit(1))
            print("✓ Successfully executed select query.")
            
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
