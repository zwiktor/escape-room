from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from fastapi import Depends
from app.db.models import User, Story, Attempt, StoryAccess, Stage
from app.db.database import get_async_session
from app.users.manager import current_active_user

from app.db.db_attempt import (
    get_active_attempt,
    get_hints,
    create_first_attempt,
    add_password_attempt,
    check_new_hint,
    finish_attempt,
    create_next_attempt,
)
from app.db.db_access import get_story_access_by_attempt, get_story_access
from app.db.db_story import get_story_by_id, get_all_stories
from app.db.db_queries import convert_to_pydantic
from app.db.db_stage import get_next_stage, get_stage_by_attempt

from app.schemas.access import StoryStatus, StatusEnum, StoryAccessBase, AttemptBase
from app.schemas.attempt import (
    HintsDisplay,
    HintBase,
    PasswordCheckDisplay,
    AttemptDisplay,
    StageDisplay,
)
from app.exceptions.exceptions import (
    StoryAlreadyOwnedError,
    InsufficientGoldError,
    EntityDoesNotExistError,
    StoryAlreadyStartedError,
)


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
        self.stage: Optional[Stage] = None
        self.story_status: Optional[StatusEnum] = StatusEnum.new
        self.attempt_finished: bool = False

    async def load_by_story_id(self, story_id: int):
        """
        Loads story and its access information by story_id.

        :param story_id: ID of the story to load.
        """
        self.story = await get_story_by_id(self.db, story_id)
        if not self.story:
            raise EntityDoesNotExistError(f"Story with id {story_id} not found.")

        story_access = await get_story_access(self.db, self.user, story_id)
        if story_access:
            self.story_access = story_access
            self.story_status = StatusEnum.purchased

            self.current_attempt = await get_active_attempt(
                self.db, self.story_access.id
            )
            if self.current_attempt:
                self.stage = await get_stage_by_attempt(self.db, self.current_attempt)
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

        self.story = self.story_access.story
        self.current_attempt = await get_active_attempt(self.db, self.story_access.id)
        self.stage = await get_stage_by_attempt(self.db, self.current_attempt)
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

        # Check if the user already has access
        if self.story_access:
            raise StoryAlreadyOwnedError("User already owns this story.")

        if self.user.gold < self.story.cost:
            raise InsufficientGoldError("Insufficient gold to purchase the story.")

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
        if self.story_access:
            return True
        return False

    async def start_story(self):
        """
        Starts the story by creating the first attempt if the user has access.
        Updates the StoryManager's state accordingly.

        :raises ValueError: If the user does not have access to the story.
        """
        # Ensure the user has access to the story
        if not self.story_access:
            raise EntityDoesNotExistError("User does not have access to this story.")

        # Check if an active attempt already exists
        if self.current_attempt:
            raise StoryAlreadyStartedError("User has already started this story")

        self.current_attempt = await create_first_attempt(
            db=self.db,
            story_access=self.story_access,
        )
        self.story_status = StatusEnum.started

    async def validate_password(self, password: str) -> PasswordCheckDisplay:
        password_result = PasswordCheckDisplay(
            message="Nieprawidłowa odpowiedź, próbuj dalej",
            new_hint=False,
            next_attempt=None,
            end_story=False,
        )

        # Dodaje nowe hasło do histori nie zależnie od poprawności
        await add_password_attempt(self.db, self.current_attempt, password)

        # Sprawdza, czy wprowadzone hasło wyzwala jakąś wskazówkę
        if await check_new_hint(self.db, self.current_attempt, password):
            password_result.new_hint = True
            password_result.message = "Nowa wskazowka zostala odkryta"

        # Sprawdza, czy wprowadzone hasło jest prawidłowe. Jeżeli jest kolejny etap to wysyła id,
        # a jeżeli niema to kończy historię
        # if await check_stage_password(self.db, self.current_attempt.stage, password):
        if self.stage.password == password:
            self.current_attempt = await finish_attempt(self.db, self.current_attempt)
            next_stage = await get_next_stage(self.db, self.current_attempt.stage)
            if next_stage:
                new_attemp = await create_next_attempt(
                    self.db,
                    self.current_attempt,
                    next_stage,
                )
                password_result.next_attempt = new_attemp.id
                password_result.message = "Gratulacje, to prawidlowa odpowiedz"
            else:

                password_result.message = "Gratulacje, historia zostala zakonczona"
                password_result.end_story = True

        return password_result

    async def get_hints(self) -> HintsDisplay:
        hints = await get_hints(self.db, self.current_attempt.id)
        return HintsDisplay(hints=convert_to_pydantic(hints, HintBase))

    async def get_stories(self) -> List[Story]:
        stories = await get_all_stories(self.db)
        return stories

    async def get_story(self) -> Story:
        return self.story

    async def get_story_access(self) -> StoryAccess:
        return self.story_access

    async def get_attempt(self) -> AttemptDisplay:
        attempt = AttemptDisplay(
            start_date=self.current_attempt.start_date,
            stage=StageDisplay(
                name=self.stage.name,
                level=self.stage.level,
                question=self.stage.question,
            ),
            is_finished=self.attempt_finished,
        )
        return attempt


async def get_story_manager(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> StoryManager:
    """
    Dependency to provide a StoryManager instance, with error handling.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    return StoryManager(session=session, current_user=user)
