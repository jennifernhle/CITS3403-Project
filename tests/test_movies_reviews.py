from popcorn_journal_app.models import Movie, Review


def test_logged_in_user_can_add_movie(client, app, login):
    login()

    response = client.post(
        "/add-movie",
        data={
            "title": "Past Lives",
            "director": "Celine Song",
            "release_year": 2023,
            "genre": "Drama",
            "synopsis": "Childhood friends reconnect years later.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"added to the database" in response.data

    with app.app_context():
        movie = Movie.query.filter_by(title="Past Lives").first()
        assert movie is not None
        assert movie.director == "Celine Song"


def test_anonymous_user_cannot_add_movie(client):
    response = client.get("/add-movie", follow_redirects=False)

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_search_finds_local_movie(client, movie):
    response = client.get("/search?query=Inception")

    assert response.status_code == 200
    assert b"Inception" in response.data


def test_user_can_create_update_and_delete_review(client, app, login, movie):
    login()

    response = client.post(
        f"/movie/{movie.id}/review",
        data={"rating": "9", "content": "A clever and visually strong film."},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Review posted" in response.data

    with app.app_context():
        review = Review.query.filter_by(movie_id=movie.id).first()
        assert review is not None
        assert review.rating == 9
        review_id = review.id

    response = client.post(
        f"/movie/{movie.id}/review",
        data={"rating": "8", "content": "Still excellent on rewatch."},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Review updated" in response.data

    with app.app_context():
        review = Review.query.get(review_id)
        assert review.rating == 8
        assert review.content == "Still excellent on rewatch."

    response = client.post(f"/review/delete/{review_id}", follow_redirects=True)

    assert response.status_code == 200
    assert b"Review removed" in response.data

    with app.app_context():
        assert Review.query.get(review_id) is None
