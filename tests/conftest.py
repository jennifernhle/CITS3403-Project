import pytest
from types import SimpleNamespace

from popcorn_journal_app import create_app, db
from popcorn_journal_app.config import TestingConfig
from popcorn_journal_app.models import Movie, User


class TestConfig(TestingConfig):
    WTF_CSRF_ENABLED = False


@pytest.fixture()
def app(tmp_path):
    class Config(TestConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{tmp_path / 'test.sqlite3'}"

    app = create_app(Config)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user(app):
    with app.app_context():
        user = User(username="alice", email="alice@example.com")
        user.set_password("Password1")
        db.session.add(user)
        db.session.commit()
        return SimpleNamespace(id=user.id, username=user.username, email=user.email)


@pytest.fixture()
def other_user(app):
    with app.app_context():
        user = User(username="bob", email="bob@example.com")
        user.set_password("Password1")
        db.session.add(user)
        db.session.commit()
        return SimpleNamespace(id=user.id, username=user.username, email=user.email)


@pytest.fixture()
def movie(app, user):
    with app.app_context():
        movie = Movie(
            title="Inception",
            director="Christopher Nolan",
            release_year=2010,
            genre="Sci-Fi",
            synopsis="A dream-sharing heist movie.",
            creator_id=user.id,
        )
        db.session.add(movie)
        db.session.commit()
        return SimpleNamespace(id=movie.id, title=movie.title)


@pytest.fixture()
def login(client, user):
    def _login(email="alice@example.com", password="Password1"):
        return client.post(
            "/login",
            data={"email": email, "password": password, "remember": "y"},
            follow_redirects=True,
        )

    return _login
