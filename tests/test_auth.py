from popcorn_journal_app.models import User


def test_register_creates_user(client, app):
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password1",
            "confirm_password": "Password1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Account created" in response.data

    with app.app_context():
        user = User.query.filter_by(email="new@example.com").first()
        assert user is not None
        assert user.check_password("Password1")


def test_login_and_logout(client, user):
    response = client.post(
        "/login",
        data={"email": "alice@example.com", "password": "Password1"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Logged in successfully" in response.data

    response = client.get("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"successfully logged out" in response.data


def test_login_rejects_wrong_password(client, user):
    response = client.post(
        "/login",
        data={"email": "alice@example.com", "password": "wrong-password"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data
