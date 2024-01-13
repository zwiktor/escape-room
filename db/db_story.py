from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import Story


async def get_all_stories(db: AsyncSession):
    stmt = select(Story)
    result = await db.execute(stmt)
    all_stories = result.scalars().all()

    return all_stories


