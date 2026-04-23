from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/about-us')
def about_us():
    return render_template('about-us.html')

@bp.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route('/profile')
def profile():
    return render_template('profile.html')

@bp.route('/register')
def register():
    return render_template('register.html')

@bp.route('/reset-password')
def reset_password():
    return render_template('reset_password.html')

@bp.route('/review')
def review():
    return render_template('review.html')

@bp.route('/search')
def search():
    movies = [
        {"id": 1, "title": "Interstellar"},
        {"id": 2, "title": "Inception"}
    ]
    return render_template('search.html', movies=movies)
@bp.route('/watchlist')
def watchlist():
    return render_template('watchlist.html')

@bp.route('/lists')
def lists():
    mock_lists = [
        {'id': 3, 'name': 'Films Directed by Women', 'description': 'My favourite women-directed films.', 'movies': [1, 2, 3]},
        {'id': 2, 'name': 'Cozy Rainy Day Movies', 'description': 'Movies for cozy rainy days.', 'movies': [1, 2]}
    ]
    return render_template('lists.html', lists=mock_lists)

@bp.route('/logout')
def logout():
    return render_template('index.html')


@bp.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = {'title': 'Inception', 'id': movie_id, 'release_year': '2010', 'rating': 8.8}
    return render_template('review.html', movie=movie)
