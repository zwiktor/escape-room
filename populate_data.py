from db.models import User, Story, Stage, Hint, StoryAccess, Attempt, PasswordAttempt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from random import randint


async def create_random_story(db: AsyncSession):
    results = await db.execute(select(Story))
    stories_count = len(results.scalars().all())
    story = Story(
        title=f'Tytuł scenariusza o numerze {stories_count}',
        description='Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industrys standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries',
        type='Normal Story',
        difficulty='Normal Diff',
        rating='2',
        cost=randint(0,50)
    )
    db.add(story)
    await db.commit()
    return story


async def create_random_stage(db: AsyncSession, story: Story, level: int):
    results = await db.execute(select(Stage).where(Stage.story_id == story.id))
    stage_count = len(results.scalars().all()) + 1

    stage = Stage(
        name=f'poziom {stage_count} do scenariusza {story.title}',
        level=level,
        question='opis zadania',
        password='odpowiedź która powinna być przekazana przez uzytkownika',
        story_id=story.id
    )

    db.add(stage)
    await db.commit()
    return story


async def populate_initial_data(db: AsyncSession):
    story = await create_random_story(db)
    stage1 = await create_random_stage(db, story, 1)
    stage2 = await create_random_stage(db, story, 2)
    stage3 = await create_random_stage(db, story, 3)
    stage4 = await create_random_stage(db, story, 4)
    stage5 = await create_random_stage(db, story, 5)




    return f'baza danych została powiększona'
