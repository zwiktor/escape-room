from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from db.models import User, Story, Attempt, StoryAccess
from schemas.access import StoryStatus, StatusEnum, StoryAccessBase, AttemptBase
from schemas.attempt import HintsDisplay, HintBase
from typing import Optional
from db.db_attempt import get_active_attempt, get_hints
from db.db_access import get_story_access_by_attempt, get_story_access
from db.db_story import get_story_by_id
from db.db_queries import convert_to_pydantic


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
        self.attempt_finished: bool = False

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
        self.current_attempt = await get_active_attempt(self.db, self.story_access.id)

        # Sytuacja w której zostanie podany attempt_id który został już rozwiązany
        # Należy przenieść historię do aktualnego lub stowrzyć stronę ze wskazaniem na aktualny
        if self.current_attempt.id != attempt_id:
            self.attempt_finished = True

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
                        finish_date=self.current_attempt.finish_date,
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
        """
        Allows the user to purchase a story if they have enough gold.

        :raises ValueError: If the user does not have enough gold.
        :raises Exception: If the story access creation fails.
        """
        # Check if the story exists
        if not self.story:
            raise ValueError(f"Story with id {story_id} does not exist.")

        # Check if the user already has access
        if self.story_access:
            raise ValueError("User already owns this story.")

        if self.user.gold < self.story.cost:
            raise ValueError("Insufficient gold to purchase the story.")

        try:
            # Deduct the cost from the user's gold
            self.user.gold -= self.story.cost
            self.db.add(self.user)

            # Create a new StoryAccess record
            new_access = StoryAccess(user_id=self.user.id, story_id=self.story.id)
            self.db.add(new_access)

            # Commit the transaction
            await self.db.commit()

            # Update the StoryManager state
            self.story_access = new_access
            self.story_status = StatusEnum.purchased
        except IntegrityError:
            await self.db.rollback()
            raise Exception("Failed to create story access due to a database error.")
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"An unexpected error occurred: {str(e)}")

    async def start_story(self):
        """
        Starts the story by creating the first attempt if the user has access.
        Updates the StoryManager's state accordingly.

        :raises ValueError: If the user does not have access to the story.
        """
        # Ensure the user has access to the story
        if not self.story_access:
            raise ValueError("User does not have access to this story.")

        # Check if an active attempt already exists
        if self.current_attempt:
            return

        self.current_attempt = await create_first_attempt(
            db=self.db,
            story_access_id=self.story_access,
        )

    async def check_password(self):
        pass

    async def move_to_next_stage(self):
        pass

    async def get_hints(self) -> HintsDisplay:
        hints = await get_hints(self.db, self.current_attempt.id)
        return HintsDisplay(hints=convert_to_pydantic(hints, HintBase))
