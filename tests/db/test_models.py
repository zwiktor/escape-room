import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import (
    Base,
    User,
    Story,
    Stage,
    Hint,
    StoryAccess,
    Attempt,
    PasswordAttempt,
    HintsAttempt,
)
from datetime import datetime, timedelta


@pytest.fixture(scope="module")
def session():
    # Setup: tworzenie silnika i sesji
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session  # Zwracanie sesji dla testów

    # Teardown: zamykanie sesji i rollback
    session.rollback()
    session.close()


def test_user_model(session):
    """Test to check user model functionality"""
    user = User(
        gold=0,
        email="mailmail@gmail.com",
        username="unique_user",
        hashed_password="123qweasdzxc",
        is_active=False,
        is_superuser=False,
        is_verified=False,
    )
    session.add(user)
    session.commit()

    user = session.query(User).filter(User.email == "mailmail@gmail.com").first()
    assert user is not None
    assert user.email == "mailmail@gmail.com"
    assert user.hashed_password == "123qweasdzxc"
    assert user.username == "unique_user"
    assert not user.is_active
    assert not user.is_superuser
    assert not user.is_verified


def test_story_model(session):
    """Test to check story model functionality"""
    story = Story(
        title="Szkola tajemni",
        description="To jest opis szkoły tajemnic, poruszajacej histrii",
        type="Normal Story",
        difficulty="Normal Diff",
        rating="2",
        cost=50,
    )
    session.add(story)
    session.commit()

    story = session.get(Story, 1)
    assert story is not None
    assert story.title == "Szkola tajemni"
    assert story.create_date < datetime.now()


def test_story_with_stage(session):
    """Test to check if stages can be associated with a story"""
    story = Story(
        title="Adventure",
        description="An exciting adventure story",
        type="Fantasy",
        difficulty="Easy",
        rating=4.5,
        cost=10,
    )
    session.add(story)
    session.commit()

    stage = Stage(
        level=1,
        name="Beginning",
        question="What is the answer?",
        password="secret",
        story_id=story.id,
    )
    session.add(stage)
    session.commit()

    # Weryfikacja relacji
    stage = session.query(Stage).filter(Stage.story_id == story.id).first()
    assert stage is not None
    assert stage.story_id == story.id
    assert stage.story.title == "Adventure"


def test_story_access_model(session):
    """Test to check if a user can have story access"""
    user = User(
        gold=100,
        username="unique_user2",
        email="testuser2@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )
    story = Story(
        title="Mystery",
        description="A mysterious story",
        type="Horror",
        difficulty="Medium",
        rating=3.8,
        cost=15,
    )
    session.add_all([user, story])
    session.commit()

    story_access = StoryAccess(
        user_id=user.id, story_id=story.id, purchase_date=datetime.now()
    )
    session.add(story_access)
    session.commit()

    # Weryfikacja relacji
    story_access = (
        session.query(StoryAccess)
        .filter(StoryAccess.user_id == user.id, StoryAccess.story_id == story.id)
        .first()
    )
    assert story_access is not None
    assert story_access.user_id == user.id
    assert story_access.story_id == story.id
    assert story_access.user.email == "testuser2@example.com"
    assert story_access.story.title == "Mystery"


def test_create_attempt(session):
    """Test to check if Attempt can be created with valid StoryAccess and Stage."""
    # Tworzenie użytkownika, historii i etapu
    user = User(
        username="test_user",
        email="testuser@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )

    session.add(user)
    session.commit()

    story = Story(
        title="Mystery Story",
        description="An engaging story",
        type="Adventure",
        difficulty="Hard",
        rating=4.0,
        cost=20,
    )

    session.add(story)
    session.commit()

    stage = Stage(
        level=1,
        name="Start",
        question="What's the first answer?",
        password="answer1",
        story_id=story.id,
    )

    # Dodaj użytkownika, historię i etap do sesji
    session.add(stage)
    session.commit()

    # Tworzenie StoryAccess dla użytkownika i historii
    story_access = StoryAccess(
        user_id=user.id, story_id=story.id, purchase_date=datetime.now()
    )
    session.add(story_access)
    session.commit()

    # Tworzenie instancji Attempt
    attempt = Attempt(
        story_access_id=story_access.id, stage_id=stage.id, start_date=datetime.now()
    )
    session.add(attempt)
    session.commit()

    # Weryfikacja, czy Attempt został utworzony poprawnie
    fetched_attempt = session.query(Attempt).filter(Attempt.id == attempt.id).first()
    assert fetched_attempt is not None
    assert fetched_attempt.start_date is not None
    assert fetched_attempt.finish_date is None
    assert fetched_attempt.stage_id == stage.id
    assert fetched_attempt.story_access_id == story_access.id


def test_attempt_relationships(session):
    """Test relationships of Attempt with Stage and StoryAccess."""
    # Tworzenie użytkownika, historii, etapu oraz dostępu do historii
    user = User(
        username="relation_user",
        email="relationuser@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )
    session.add(user)
    session.commit()

    story = Story(
        title="Adventure Story",
        description="A thrilling story",
        type="Adventure",
        difficulty="Medium",
        rating=4.3,
        cost=15,
    )
    session.add(story)
    session.commit()

    stage = Stage(
        level=2,
        name="Adventure Stage",
        question="Solve the riddle",
        password="riddle",
        story_id=story.id,
    )
    session.add(stage)
    session.commit()

    story_access = StoryAccess(
        user_id=user.id, story_id=story.id, purchase_date=datetime.now()
    )
    session.add(story_access)
    session.commit()

    # Tworzenie Attempt i przypisanie relacji
    attempt = Attempt(
        story_access_id=story_access.id, stage_id=stage.id, start_date=datetime.now()
    )
    session.add(attempt)
    session.commit()

    # Weryfikacja relacji
    fetched_attempt = session.query(Attempt).filter(Attempt.id == attempt.id).first()
    assert fetched_attempt.access.user.username == "relation_user"
    assert fetched_attempt.stage.name == "Adventure Stage"


def test_update_attempt_finish_date(session):
    """Test updating finish_date in Attempt."""
    # Tworzenie użytkownika, historii, etapu oraz dostępu do historii
    user = User(
        username="finisher_user",
        email="finisheruser@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )
    session.add(user)
    session.commit()

    story = Story(
        title="Challenge Story",
        description="A story full of challenges",
        type="Challenge",
        difficulty="Hard",
        rating=4.7,
        cost=25,
    )
    session.add(story)
    session.commit()

    stage = Stage(
        level=3,
        name="Final Stage",
        question="What is the ultimate answer?",
        password="final",
        story_id=story.id,
    )
    session.add(stage)
    session.commit()

    story_access = StoryAccess(
        user_id=user.id, story_id=story.id, purchase_date=datetime.now()
    )
    session.add(story_access)
    session.commit()

    # Tworzenie Attempt i aktualizacja finish_date
    attempt = Attempt(
        story_access_id=story_access.id, stage_id=stage.id, start_date=datetime.now()
    )
    session.add(attempt)
    session.commit()

    # Aktualizacja finish_date
    finish_time = datetime.now() + timedelta(hours=1)
    attempt.finish_date = finish_time
    session.commit()

    # Weryfikacja, czy finish_date zostało poprawnie zaktualizowane
    fetched_attempt = session.query(Attempt).filter(Attempt.id == attempt.id).first()
    assert fetched_attempt.finish_date == finish_time


def test_create_password_attempt(session):
    """Test if PasswordAttempt can be created with valid Attempt and password."""
    # Tworzenie użytkownika, historii, etapu oraz dostępu do historii
    user = User(
        username="password_user",
        email="passworduser@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )
    session.add(user)
    session.commit()

    story = Story(
        title="Password Story",
        description="A story with password challenges",
        type="Puzzle",
        difficulty="Hard",
        rating=4.6,
        cost=20,
    )
    session.add(story)
    session.commit()

    stage = Stage(
        level=1,
        name="Password Stage",
        question="What is the password?",
        password="password123",
        story_id=story.id,
    )
    session.add(stage)
    session.commit()

    story_access = StoryAccess(
        user_id=user.id, story_id=story.id, purchase_date=datetime.now()
    )
    session.add(story_access)
    session.commit()

    # Tworzenie Attempt
    attempt = Attempt(
        story_access_id=story_access.id, stage_id=stage.id, start_date=datetime.now()
    )
    session.add(attempt)
    session.commit()

    # Tworzenie instancji PasswordAttempt
    password_attempt = PasswordAttempt(attempt_id=attempt.id, password="password123")
    session.add(password_attempt)
    session.commit()

    # Weryfikacja PasswordAttempt
    fetched_password_attempt = (
        session.query(PasswordAttempt)
        .filter(PasswordAttempt.id == password_attempt.id)
        .first()
    )
    assert fetched_password_attempt is not None
    assert fetched_password_attempt.password == "password123"
    assert fetched_password_attempt.enter_date is not None
    assert fetched_password_attempt.attempt_id == attempt.id


def test_create_hints_attempt(session):
    """Test if HintsAttempt can be created with valid Attempt and Hint."""
    # Tworzenie użytkownika, historii, etapu oraz dostępu do historii
    user = User(
        username="hint_user",
        email="hintuser@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )
    session.add(user)
    session.commit()

    story = Story(
        title="Hint Story",
        description="A story with hints",
        type="Mystery",
        difficulty="Medium",
        rating=4.2,
        cost=15,
    )
    session.add(story)
    session.commit()

    stage = Stage(
        level=1,
        name="Hint Stage",
        question="What is the answer?",
        password="answer123",
        story_id=story.id,
    )
    session.add(stage)
    session.commit()

    story_access = StoryAccess(
        user_id=user.id, story_id=story.id, purchase_date=datetime.now()
    )
    session.add(story_access)
    session.commit()

    # Tworzenie Attempt
    attempt = Attempt(
        story_access_id=story_access.id, stage_id=stage.id, start_date=datetime.now()
    )
    session.add(attempt)
    session.commit()

    # Tworzenie Hint
    hint = Hint(text="Think about the obvious", trigger="first_try", stage_id=stage.id)
    session.add(hint)
    session.commit()

    # Tworzenie instancji HintsAttempt
    hints_attempt = HintsAttempt(attempt_id=attempt.id, hint_id=hint.id)
    session.add(hints_attempt)
    session.commit()

    # Weryfikacja HintsAttempt
    fetched_hints_attempt = (
        session.query(HintsAttempt).filter(HintsAttempt.id == hints_attempt.id).first()
    )
    assert fetched_hints_attempt is not None
    assert fetched_hints_attempt.attempt_id == attempt.id
    assert fetched_hints_attempt.hint_id == hint.id
    assert fetched_hints_attempt.enter_date is not None


def test_default_date_values(session):
    """Test that default dates are set to the current date and time."""
    story = Story(
        title="Date Test Story",
        description="A story to test default date",
        type="Adventure",
        difficulty="Medium",
        rating=4.5,
        cost=30,
    )
    session.add(story)
    session.commit()

    assert story.create_date is not None
    assert story.create_date <= datetime.now()

    password_attempt = PasswordAttempt(
        attempt_id=1,  # Zakładamy, że istnieje `Attempt` o `id=1`
        password="test_password",
    )
    session.add(password_attempt)
    session.commit()

    assert password_attempt.enter_date is not None
    assert password_attempt.enter_date <= datetime.now()


def test_relationship_back_populates(session):
    """Test bidirectional relationships and back_populates."""
    # Tworzenie użytkownika i powiązanej historii
    user = User(
        username="back_populate_user",
        email="backpopulate@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )
    session.add(user)
    session.commit()

    story = Story(
        title="Back Populate Story",
        description="Story to test back_populates",
        type="Mystery",
        difficulty="Easy",
        rating=3.9,
        cost=15,
    )
    session.add(story)
    session.commit()

    story_access = StoryAccess(
        user_id=user.id, story_id=story.id, purchase_date=datetime.now()
    )
    session.add(story_access)
    session.commit()

    # Sprawdzanie relacji z obiektu User
    assert user.story_accesses[0].story_id == story.id
    # Sprawdzanie relacji z obiektu StoryAccess
    assert story_access.user.username == "back_populate_user"
