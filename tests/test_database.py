import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from db.models import Base, User, Story, Stage, Hint, StoryAccess, Attempt, PasswordAttempt
# Document

from datetime import datetime, timedelta

# testing meta ifnormation about table. table name, foregin key, primary key?

class TestDatabase:
    def setup_class(self):
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def teardown_class(self):
        self.session.rollback()
        self.session.close()

    def test_user_model(self):
        # create user via database
        user = User(
            gold=0,
            email='mailmail@gmail.com',
            hashed_password='123qweasdzxc',
            is_active=False,
            is_superuser=False,
            is_verified=False
        )
        self.session.add(user)
        self.session.commit()

        user = self.session.query(User).filter(User.email == 'mailmail@gmail.com').first()

        assert user.email
        assert user.hashed_password
        assert not user.is_active
        assert not user.is_superuser
        assert not user.is_verified

        super_user = User(
            gold=99999,
            email='admin@admin.com',
            hashed_password='admin',
            is_active=True,
            is_superuser=True,
            is_verified=True
        )
        self.session.add(super_user)
        self.session.commit()

        super_user = self.session.query(User).filter(User.email == 'admin@admin.com').first()

        assert super_user.email
        assert super_user.hashed_password
        assert super_user.is_active
        assert super_user.is_superuser
        assert super_user.is_verified
        assert super_user.gold > 0

    def test_story_model(self):
        story = Story(
            title='Szkola tajemni',
            description='To jest opis szkoły tajemnic, poruszajacej histrii',
            type='Normal Story',
            difficulty='Normal Diff',
            rating='2',
            cost=50
        )
        self.session.add(story)
        self.session.commit()

        story = self.session.get(Story, 1)

        assert story.title == 'Szkola tajemni'
        assert isinstance(story, Story)
        assert story.create_date < datetime.now()
        assert story.cost
        assert story.type
        assert story.description

    def test_stage_model(self):
        stage = Stage(
            name='Stara Biblioteka',
            level=1,
            question='Gdzie powinienem rozpocząć poszukwiwania',
            password='to jest jakieś miejsce',
            story_id=1
        )

        self.session.add(stage)
        self.session.commit()

        stage = self.session.get(Stage, 1)

        assert stage
        assert stage.level == 1
        assert stage.password != 'password'
        assert stage.story.title == 'Szkola tajemni'

    def test_story_stage_relation(self):
        story = self.session.get(Story, 1)

        assert story.stages
        assert story.stages[0].name == 'Stara Biblioteka'
        assert story.stages[0].story.title == 'Szkola tajemni'

    def test_hint_model(self):
        hint = Hint(
            text='to jest pierwsza wskazówka',
            trigger='to jakieś hasło',
            stage_id=1
        )
        self.session.add(hint)
        self.session.commit()

        hint = Hint(
            text='to jest pierwsza wskazówka2',
            trigger='to jakieś hasło2',
            stage_id=1
        )
        self.session.add(hint)
        self.session.commit()

        hint = Hint(
            text='to jest pierwsza wskazówka3',
            trigger='to jakieś hasło3',
            stage_id=1
        )
        self.session.add(hint)
        self.session.commit()

        hint = self.session.get(Hint,1)

        assert hint
        assert hint.trigger == 'to jakieś hasło'
        assert hint.stage.level == 1

    def test_stage_hint_relation(self):
        stage = self.session.get(Stage, 1)

        assert stage.hints
        assert stage.hints[0].trigger == 'to jakieś hasło'
        assert stage.hints[2].text == 'to jest pierwsza wskazówka3'

    def test_storyacces_model(self):
        user = self.session.query(User).all()[0]

        story_acces = StoryAccess(
            user_id=user.id,
            story_id=1,
        )
        self.session.add(story_acces)
        self.session.commit()

        story_acces = self.session.get(StoryAccess, 1)

        assert story_acces.user.id != 1
        assert story_acces.story.id == 1
        assert story_acces.purchase_date < datetime.now()
        assert len(user.story_accesses) == 1

    def test_attempt_model(self):
        attempt = Attempt(
            story_access_id=1,
            stage_id=1
        )
        self.session.add(attempt)
        self.session.commit()

        assert attempt.access.story.stages[0].name == attempt.stage.name


if __name__ == '__main__':
    unittest.main()