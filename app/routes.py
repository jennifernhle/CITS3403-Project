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
    return render_template('search.html')

@bp.route('/watchlist')
def watchlist():
    return render_template('watchlist.html')