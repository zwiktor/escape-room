import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from db.models import Base, User#, Story, Stage, Document, Hint, StoryAccess, PasswordAttempt


class TestDatabase:
    def setup_class(self):
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def teardown_class(self):
        self.session.rollback()
        self.session.close()

    def test_create_users(self):
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

        assert super_user.email
        assert super_user.hashed_password
        assert super_user.is_active
        assert super_user.is_superuser
        assert super_user.is_verified
        assert super_user.gold > 0


    def test_query_users(self):
        user = self.session.query(User).filter(User.email == 'mailmail@gmail.com').first()
        super_user = self.session.query(User).filter(User.email == 'admin@admin.com').first()

        assert not user.is_superuser
        assert super_user.is_superuser


if __name__ == '__main__':
    unittest.main()