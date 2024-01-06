from typing_extensions import Annotated
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from fastapi_users.db import SQLAlchemyBaseUserTableUUID

from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped
from sqlalchemy import (func, Column, Integer, String, Text, DateTime, Float, SmallInteger,
                        ForeignKey)



class Base(DeclarativeBase):
    # Here we can add some parameters for User
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    gold: Mapped[int]

    #story_accesses: Mapped[List["StoryAccess"]] = relationship(back_populates='user')


# class Story(Base):
#     __tablename__ = 'story'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     title: Mapped[str]
#     description: Mapped[str]
#     type: Mapped[str]
#     difficulty: Mapped[str]
#     rating: Mapped[Optional[float]]
#     cost: Mapped[int]
#     create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
#
#     stages: Mapped[List["Stage"]] = relationship(back_populates='story')
#
#
# class Stage(Base):
#     __tablename__ = 'stage'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     level: Mapped[int]
#     name: Mapped[str] = mapped_column(String(128))
#     question: Mapped[str]
#     password: Mapped[str]
#     story_id: Mapped[int] = mapped_column(ForeignKey('story.id'))
#
#     story: Mapped["Story"] = relationship(back_populates='stages')
#     documents: Mapped[List["Document"]] = relationship(back_populates='stage')
#     hints: Mapped[List["Hint"]] = relationship(back_populates='stage')
#
#
# class Document(Base):
#     __tablename__ = 'document'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str]
#     stage_id: Mapped[int] = mapped_column(ForeignKey("stage.id"))
#
#     stage: Mapped["Stage"] = relationship(back_populates='documents')
#
#
# class Hint(Base):
#     __tablename__ = 'hint'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     text: Mapped[str]
#     trigger: Mapped[str]
#     stage_id: Mapped[int] = mapped_column(ForeignKey("stage.id"))
#
#     stage: Mapped["Stage"] = relationship(back_populates='hints')
#
#
# class StoryAccess(Base):
#     __tablename__ = 'story_access'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'))
#     story_id: Mapped[int] = mapped_column(ForeignKey('story.id'))
#     purchase_date: Mapped[datetime] = mapped_column(insert_default=func.now())
#
#     user: Mapped["User"] = relationship(back_populates='story_accesses')
#     story: Mapped["Story"] = relationship(back_populates='story_access')
#     attempts: Mapped[List["Attempt"]] = relationship(back_populates='access')
#
#
# class Attempt(Base):
#     __tablename__ = 'attempt'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     story_access_id: Mapped["StoryAccess"] = mapped_column(ForeignKey('story_access.id'))
#     stage_id: Mapped["Stage"] = mapped_column(ForeignKey('stage.id'))
#     start_date: Mapped[datetime] = mapped_column(insert_default=func.now())
#     finish_date: Mapped[datetime]
#
#     stage: Mapped["Stage"] = relationship(back_populates='attempts')
#     access: Mapped["StoryAccess"] = relationship(back_populates='attempts')
#
#
# class PasswordAttempt(Base):
#     __tablename__ = 'password_attempt'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     attempt_id: Mapped["Attempt"] = mapped_column(ForeignKey('attempt.id'))
#     password: Mapped[str]
#     enter_date: Mapped[datetime] = mapped_column(insert_default=func.now())
#










