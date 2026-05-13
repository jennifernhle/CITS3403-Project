from popcorn_journal_app.models import User, Movie, Review
from popcorn_journal_app import db

# User creation and password hashing logic
def test_user_password_hashing(app):
    u = User(username='tester', email='tester@example.com')
    u.set_password('password123')
    assert u.check_password('password123')
    assert not u.check_password('wrongpassword')

# Movie creation and average rating calculation
def test_movie_average_rating_logic(app, user):
    movie = Movie(title='Test Movie', director='Test Dir', release_year=2020, genre='Drama', creator_id=user.id)
    db.session.add(movie)
    db.session.commit()
    
    assert movie.get_average_rating() == 0
    
    # Add reviews
    rev1 = Review(user_id=user.id, movie_id=movie.id, rating=10, content='Great!')
    rev2 = Review(user_id=user.id, movie_id=movie.id, rating=6, content='Okay.')
    db.session.add_all([rev1, rev2])
    db.session.commit()
    
    db.session.refresh(movie)
    assert movie.get_average_rating() == 8.0

# Counting logged movies for a user
def test_user_model_counters(app, user):
    db_user = User.query.get(user.id)
    
    movie = Movie(title='Count Test', director='Dir', release_year=2020, genre='Drama', creator_id=user.id)
    db.session.add(movie)
    db.session.commit()
    
    review = Review(user_id=user.id, movie_id=movie.id, rating=8, content='Count me!')
    db.session.add(review)
    db.session.commit()
    db.session.refresh(db_user)
    
    assert db_user.logged_movie_count == 1