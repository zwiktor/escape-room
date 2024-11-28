from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Story, attempt
from schemas.access import StoryStatus, StatusEnum, StoryAccessBase, AttemptBase
from typing import Optional
from db.db_attempt import get_active_attempt
from db.db_access import get_story_access_by_attempt, get_story_access


class StoryManager:
    def __init__(self, session: AsyncSession, current_user: User):
        """
        Initializes the StoryManager with a database session and the current user.

        :param session: AsyncSession instance for database operations.
        :param current_user: Current authenticated User instance.
        """
        self.db: AsyncSession = session
        self.user: User = current_user
        self.story: Optional[Story] = None
        self.story_access: Optional[StoryAccess] = None
        self.current_attempt: Optional[Attempt] = None
        self.story_status: Optional[StatusEnum] = StatusEnum.new

    async def load_by_story_id(self, story_id: int):
        """
        Loads story and its access information by story_id.

        :param story_id: ID of the story to load.
        """
        self.story = await get_story_by_id(self.db, story_id)
        if not self.story:
            raise ValueError(f"Story with id {story_id} not found.")

        story_access = await get_story_access(self.db, self.user, story_id)
        if story_access:
            self.story_access = story_access
            self.story_status = StatusEnum.purchased

            self.current_attempt = await get_active_attempt(
                self.db, self.story_access.id
            )
            if self.current_attempt:
                self.story_status = StatusEnum.started
                if self.current_attempt.finish_date:
                    self.story_status = StatusEnum.ended
            else:
                self.story_status = StatusEnum.purchased

    async def load_by_attempt_id(self, attempt_id: int):
        """
        Loads story and current attempt information by attempt_id.

        :param attempt_id: ID of the attempt to load.
        """
        self.story_access = await get_story_access_by_attempt(
            self.db, attempt_id, self.user
        )
        if not self.story_access:
            raise ValueError(f"Attempt - {attempt_id} does not exist")

        self.story = self.story_access.story
        self.current_attempt = await get_attempt_by_id(self.db, attempt_id)

        if self.current_attempt.finish_date:
            self.story_status = StatusEnum.ended
        else:
            self.story_status = StatusEnum.started

    async def check_access(self) -> StoryStatus:

        if self.story_status == StatusEnum.new:
            result_status = StoryStatus(status=self.story_status, story_access=None)
        elif self.story_status == StatusEnum.purchased:
            result_status = StoryStatus(
                status=self.story_status,
                story_access=StoryAccessBase(
                    purchase_date=self.story_access.purchase_date, current_attempt=None
                ),
            )
        elif self.story_status == StatusEnum.started:
            result_status = StoryStatus(
                status=self.story_status,
                story_access=StoryAccessBase(
                    purchase_date=self.story_access.purchase_date,
                    current_attempt=AttemptBase(
                        id=self.current_attempt.id,
                        story_access_id=self.story_access.id,
                        stage_id=self.current_attempt.stage_id,
                        start_date=self.current_attempt.start_date,
                    ),
                ),
            )
        else:
            result_status = StoryStatus(
                status=self.story_status,
                story_access=StoryAccessBase(
                    purchase_date=self.story_access.purchase_date,
                    current_attempt=AttemptBase(
                        id=self.current_attempt.id,
                        story_access_id=self.story_access.id,
                        stage_id=self.current_attempt.stage_id,
                        start_date=self.current_attempt.start_date,
                        finish_date=self.current_attempt.finish_date,
                    ),
                ),
            )

        return result_status

    async def buy_story(self):
        pass

    async def start_story(self):
        pass

    async def check_password(self):
        pass

    async def move_to_next_stage(self):
        pass

    async def get_hints(self):
        pass
