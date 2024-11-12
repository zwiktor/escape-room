from db.models import User, Story, Stage, Hint, StoryAccess, Attempt, PasswordAttempt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from random import randint


async def create_random_hint(db: AsyncSession, stage: Stage, number: int):
    hint = Hint(
        text=f"podpowiedź numer {number}",
        trigger=f"Wyzwalacz podpowiedzi {number}",
        stage_id=stage.id,
    )

    db.add(hint)
    await db.commit()


async def create_random_stage(db: AsyncSession, story: Story, level: int):
    stage = Stage(
        name=f"poziom {level} do {story.title}",
        level=level,
        question="opis zadania",
        password="odpowiedź która powinna być przekazana przez uzytkownika",
        story_id=story.id,
    )
    db.add(stage)
    await db.commit()

    for i in range(1, 4):
        await create_random_hint(db, stage, i)


async def create_random_story(db: AsyncSession):
    results = await db.execute(select(Story))
    stories_count = len(results.scalars().all())
    story = Story(
        title=f"Tytuł scenariusza numer {stories_count}",
        description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industrys standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries",
        type="Normal Story",
        difficulty="Normal Diff",
        rating="2",
        cost=randint(0, 50),
    )
    db.add(story)
    await db.commit()

    for i in range(1, 6):
        await create_random_stage(db, story, i)

    return story


async def populate_user_data(db: AsyncSession):
    user = User(
        gold=0,
        email="mailmail@gmail.com",
        hashed_password="123qweasdzxc",
        is_active=False,
        is_superuser=False,
        is_verified=False,
    )

    admin = User(
        gold=99999,
        email="admin@gmail.com",
        hashed_password="123qweasdzxc123123",
        is_active=True,
        is_superuser=True,
        is_verified=True,
    )

    db.add_all([user, admin])
    await db.commit()

    return user, admin


async def populate_data(db: AsyncSession):
    story = await create_random_story(db)
    # user, admin = await populate_user_data(db)
    # await create_story_access(db, story, user)
    # await create_story_access(db, story, admin)

    return (
        f"Utworzono dodatkowy {story.title} z poziomami i podpowiedźami wraz z użytkownikami "
        # f'{user.email, admin.email} '
        f"i dostępami"
    )
