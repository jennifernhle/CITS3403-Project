from popcorn_journal_app import db
from popcorn_journal_app.models import List, Movie, Review, User


def test_watchlist_toggle_adds_and_removes_movie(client, app, login, movie):
    login()

    response = client.post(f"/watchlist/toggle/{movie.id}")

    assert response.status_code == 200
    assert response.get_json()["action"] == "added"

    with app.app_context():
        user = User.query.filter_by(email="alice@example.com").first()
        assert movie.id in [item.id for item in user.watchlist]

    response = client.post(f"/watchlist/toggle/{movie.id}")

    assert response.status_code == 200
    assert response.get_json()["action"] == "removed"


def test_user_can_create_list_and_add_movie(client, app, login, movie):
    login()

    response = client.post(
        "/list/create",
        data={
            "name": "Weekend Picks",
            "description": "Movies to watch this weekend.",
            "public_status": "on",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"created successfully" in response.data

    with app.app_context():
        user_list = List.query.filter_by(name="Weekend Picks").first()
        assert user_list is not None
        list_id = user_list.id

    response = client.post(
        f"/list/add-movie/{movie.id}",
        data={"list_id": list_id},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Added" in response.data

    with app.app_context():
        user_list = List.query.get(list_id)
        assert movie.id in [item.id for item in user_list.movies]


def test_private_list_is_not_visible_to_other_user(client, app, user, other_user, movie):
    with app.app_context():
        private_list = List(
            name="Private Picks",
            description="Only for Alice.",
            public_status=False,
            user_id=user.id,
        )
        private_list.movies.append(db.session.get(Movie, movie.id))
        db.session.add(private_list)
        db.session.commit()
        list_id = private_list.id

    client.post(
        "/login",
        data={"email": "bob@example.com", "password": "Password1"},
        follow_redirects=True,
    )
    response = client.get(f"/list/{list_id}", follow_redirects=True)

    assert response.status_code == 200
    assert b"do not have permission" in response.data


def test_follow_and_unfollow_user(client, app, login, other_user):
    login()

    response = client.post(f"/follow/{other_user.id}/follow")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["action"] == "unfollow"
    assert payload["follower_count"] == 1

    response = client.post(f"/follow/{other_user.id}/unfollow")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["action"] == "follow"
    assert payload["follower_count"] == 0


def test_user_can_like_and_unlike_review(client, app, login, movie, other_user):
    with app.app_context():
        review = Review(
            user_id=other_user.id,
            movie_id=movie.id,
            rating=8,
            content="A strong recommendation.",
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    login()

    response = client.post(f"/like-review/{review_id}")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["action"] == "liked"
    assert payload["count"] == 1

    response = client.post(f"/like-review/{review_id}")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["action"] == "unliked"
    assert payload["count"] == 0
