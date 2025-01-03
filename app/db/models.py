from typing_extensions import Annotated
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID

from sqlalchemy.orm import (
    DeclarativeBase,
    relationship,
    mapped_column,
    Mapped,
    validates,
)
from sqlalchemy import (
    func,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    SmallInteger,
    ForeignKey,
)
from datetime import datetime


class Base(DeclarativeBase):
    # Here we can add some parameters for User
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    gold: Mapped[Optional[int]]
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    story_accesses: Mapped[List["StoryAccess"]] = relationship(back_populates="user")

    @validates("username", "email")
    def validate_non_empty(self, key, value):
        if not value:
            raise ValueError(f"{key.capitalize()} cannot be empty.")
        return value


class Story(Base):
    __tablename__ = "story"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    type: Mapped[str]
    difficulty: Mapped[str]
    rating: Mapped[Optional[float]]
    cost: Mapped[int]
    create_date: Mapped[datetime] = mapped_column(insert_default=datetime.now())

    stages: Mapped[List["Stage"]] = relationship(back_populates="story")
    story_access: Mapped[List["StoryAccess"]] = relationship(back_populates="story")


class Stage(Base):
    __tablename__ = "stage"

    id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[int]
    name: Mapped[str] = mapped_column(String(128))
    question: Mapped[str]  # Tu powininem rozszerzyć tą kolumnę o tablkę w której będą
    # przechowywane treści dotyczące pytania(img, audio, text, itd)
    password: Mapped[str]  # rozważyć możliwość wpisania kilku haseł
    # Dodanie atrybutu mode - mógłby on decydować w jakim formacie będzie dany poziom
    story_id: Mapped[int] = mapped_column(ForeignKey("story.id"))

    story: Mapped["Story"] = relationship(back_populates="stages")
    # documents: Mapped[List["Document"]] = relationship(back_populates='stage')
    hints: Mapped[List["Hint"]] = relationship(back_populates="stage")
    attempts: Mapped[List["Attempt"]] = relationship(back_populates="stage")


class Hint(Base):
    __tablename__ = "hint"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    trigger: Mapped[str]
    stage_id: Mapped[int] = mapped_column(ForeignKey("stage.id"))

    stage: Mapped["Stage"] = relationship(back_populates="hints")
    hints_attempts: Mapped[List["HintsAttempt"]] = relationship(
        "HintsAttempt", back_populates="hint"
    )


class StoryAccess(Base):
    __tablename__ = "story_access"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    story_id: Mapped[int] = mapped_column(ForeignKey("story.id"))
    purchase_date: Mapped[datetime] = mapped_column(insert_default=datetime.now())

    user: Mapped["User"] = relationship(back_populates="story_accesses")
    story: Mapped["Story"] = relationship(back_populates="story_access")
    attempts: Mapped[List["Attempt"]] = relationship(back_populates="access")


class Attempt(Base):
    __tablename__ = "attempt"

    id: Mapped[int] = mapped_column(primary_key=True)
    story_access_id: Mapped["StoryAccess"] = mapped_column(
        ForeignKey("story_access.id")
    )
    stage_id: Mapped[Optional["Stage"]] = mapped_column(ForeignKey("stage.id"))
    start_date: Mapped[datetime] = mapped_column(insert_default=datetime.now())
    finish_date: Mapped[Optional[datetime]]

    stage: Mapped["Stage"] = relationship(back_populates="attempts")
    access: Mapped["StoryAccess"] = relationship(back_populates="attempts")
    password_attempts: Mapped[List["PasswordAttempt"]] = relationship(
        "PasswordAttempt", back_populates="attempt"
    )
    hints_attempts: Mapped[List["HintsAttempt"]] = relationship(
        "HintsAttempt", back_populates="attempt"
    )


class PasswordAttempt(Base):
    __tablename__ = "password_attempt"

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped["Attempt"] = mapped_column(ForeignKey("attempt.id"))
    password: Mapped[str]
    enter_date: Mapped[datetime] = mapped_column(insert_default=datetime.now())

    attempt: Mapped["Attempt"] = relationship(
        "Attempt", back_populates="password_attempts"
    )


class HintsAttempt(Base):
    __tablename__ = "hints_attempt"

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped["Attempt"] = mapped_column(ForeignKey("attempt.id"))
    hint_id: Mapped["Hint"] = mapped_column(ForeignKey("hint.id"))
    enter_date: Mapped[datetime] = mapped_column(insert_default=datetime.now())

    attempt: Mapped["Attempt"] = relationship(
        "Attempt", back_populates="hints_attempts"
    )
    hint: Mapped["Hint"] = relationship("Hint", back_populates="hints_attempts")
