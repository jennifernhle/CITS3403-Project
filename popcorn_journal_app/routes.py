from flask import Blueprint, render_template, flash, redirect, url_for
from popcorn_journal_app.models import User, Movie, Series, Review, List

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title = 'Home')

@bp.route('/about-us')
def about_us():
    return render_template('about-us.html', title = 'About Us')

@bp.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html', title = 'Forgot Password')

@bp.route('/login')
def login():
    return render_template('login.html', title = 'Login')

@bp.route('/profile') # view own profile page
def profile():
    return render_template('profile.html', title = 'Profile')

@bp.route('/settings')
def settings():
    return render_template('settings.html', title = 'Settings')

#@bp.route('/<username>') # view another user's page
#def other_user(username):
#    return render_template('user.html', username=username)

@bp.route('/register')
def register():
    return render_template('register.html', title = 'Register')

@bp.route('/reset-password')
def reset_password():
    return render_template('reset_password.html', title = 'Reset Password')

@bp.route('/review')
def review():
    return render_template('review.html', title = 'Reviews')

@bp.route('/search')
def search():
    return render_template('search.html', title = 'Search')

@bp.route('/watchlist')
def watchlist():
    return render_template('watchlist.html', title = 'Watchlist')

@bp.route('/lists')
def lists():
    mock_lists = [
        {'id': 3, 'name': 'Films Directed by Women', 'description': 'My favourite women-directed films.', 'movies': [1, 2, 3]},
        {'id': 2, 'name': 'Cozy Rainy Day Movies', 'description': 'Movies for cozy rainy days.', 'movies': [1, 2]}
    ]
    return render_template('lists.html', lists=mock_lists, title = 'Lists')

@bp.route('/logout')
def logout():
    return render_template('index.html', title = 'Home')


@bp.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = {'title': 'Inception', 'id': movie_id, 'release_year': '2010', 'rating': 8.8}
    return render_template('review.html', movie=movie['title'])
