from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy import and_
from typing import Type, List, Any, Optional
from pydantic import BaseModel
from sqlalchemy import true


class MultipleResultsException(Exception):
    """Exception raised when multiple results are found in a single-instance query."""

    pass


def convert_to_pydantic(
    models: List[Any], pydantic_model: Type[BaseModel]
) -> List[BaseModel]:
    return [pydantic_model.model_validate(model) for model in models]


async def get_instance(
    session: AsyncSession, model: Type[Any], **kwargs
) -> Optional[Any]:
    stmt = select(model).filter_by(**kwargs)
    result = await session.execute(stmt)
    instances = result.scalars().all()

    if len(instances) > 1:
        raise MultipleResultsException(
            f"Multiple instances found for {model.__name__} with filters {kwargs}."
        )
    elif instances:
        return instances[0]
    return None


async def get_last_instance(session: AsyncSession, model, order_by, **kwargs):
    stmt = select(model).filter_by(**kwargs).order_by(desc(order_by))
    result = await session.execute(stmt)
    instance = result.scalars().first()
    if instance:
        return instance


async def create_instance(session: AsyncSession, model, **kwargs):
    instance = model(**kwargs)
    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    return instance


async def get_or_create(session: AsyncSession, model, **kwargs):
    instance = await get_instance(session, model, **kwargs)
    if not instance:
        instance = await create_instance(session, model, **kwargs)
    return instance


async def get_instances(session: AsyncSession, model, **kwargs):
    filters = []
    for attr, value in kwargs.items():
        if isinstance(value, list):
            filters.append(getattr(model, attr).in_(value))
        else:
            filters.append(getattr(model, attr) == value)
    stmt = select(model).where(and_(true(), *filters))
    result = await session.execute(stmt)
    instances = result.scalars().all()
    return instances
