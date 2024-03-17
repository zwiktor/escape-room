from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def get_instance(session: AsyncSession, model, **kwargs):
    stmt = select(model).filter_by(**kwargs)
    result = await session.execute(stmt)
    instance = result.scalars().first()
    if instance:
        return instance


async def get_or_create(session: AsyncSession, model, **kwargs):
    instance = await get_instance(session, model, **kwargs)
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
    return instance
