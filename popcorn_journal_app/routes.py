from flask import Blueprint, render_template, flash, redirect, url_for, jsonify, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from popcorn_journal_app import db
from popcorn_journal_app.models import User, Movie, Series, Review, List
import uuid

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title = 'Home - Popcorn Journal')

@bp.route('/about-us')
def about_us():
    return render_template('about-us.html', title = 'About Us - Popcorn Journal')

@bp.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html', title = 'Forgot Password - Popcorn Journal')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user) # This sets the current_user
            flash('Logged in successfully.')
            return redirect(url_for('main.profile'))
        
        if user and not check_password_hash(user.password_hash, request.form['password']):
            flash('Your password is incorrect.')
            return render_template('login.html', title = 'Login - Popcorn Journal')
        if not user:
            flash('This user does not exist.')

    return render_template('login.html', title = 'Login - Popcorn Journal')

@bp.route('/profile') # view own profile page
def profile():
    if not current_user.is_authenticated:
        flash('Please log in to view your profile.')
        return redirect(url_for('main.login'))
    if current_user.is_authenticated:
        user = User.query.get_or_404(current_user.id) # Replace with actual user retrieval logic (e.g., current_user)
        #follower_count = len(user.followers.all())  # Calculate from database
    return render_template('profile.html', title = 'Profile - Popcorn Journal', user=user)#, follower_count=follower_count, following_count=following_count)

@bp.route('/delete/<int:user_id>', methods=['POST']) # delete user account
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user == current_user:
        db.session.delete(user)
        db.session.commit()
        flash('Your account has been deleted.')
        return redirect(url_for('main.index'))
    if not user == current_user:
        flash('You can only delete your own account.')
        return redirect(url_for('main.profile'))
    else:
        flash('There was an error in your request. Please try again.')
        return redirect(url_for('main.index'))
    
@bp.route('/delete/<int:list_id>', methods=['POST']) # delete list
@login_required
def delete_list(list_id):
    list_to_delete = List.query.filter_by(id=list_id).first()
    if list_to_delete and list_to_delete.user_id == current_user.id:
        db.session.delete(list_to_delete)
        db.session.commit()
        flash(f'Your list {list_to_delete.name} has been deleted.')
        return redirect(url_for('main.profile'))
    else:
        flash('You can only delete your own lists.')
        return redirect(url_for('main.profile'))

@bp.route('/user/<int:user_id>') # view another user's page
def other_user(user_id):
    user = User.query.get_or_404(user_id)
    follower_count = len(user.followers.all())  # Calculate from database
    following_count = len(user.following.all())  # Calculate from database
    
    # Check if current user is following this user
    is_following = False # default to False if user is not authenticated
    if current_user.is_authenticated:
        is_following = current_user.is_following(user)
    
    return render_template('user.html', title = f"{user.username} - Popcorn Journal", 
                          user=user, follower_count=follower_count, following_count=following_count, is_following=is_following)

@bp.route('/follow/<int:user_id>/<action>', methods=['POST'])
@login_required
def follow_user(user_id, action):
    user = User.query.get_or_404(user_id)
    
    if action == 'follow':
        current_user.follow(user)
        db.session.commit()
        follower_count = len(user.followers.all())
        return jsonify({'success': True, 'action': 'follow', 'follower_count': follower_count})
    
    elif action == 'unfollow':
        current_user.unfollow(user)
        db.session.commit()
        follower_count = len(user.followers.all())
        return jsonify({'success': True, 'action': 'unfollow', 'follower_count': follower_count})
    
    return jsonify({'success': False, 'error': 'Invalid action'}), 400

@bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html', title = 'User Settings - Popcorn Journal')

#@bp.route('/<username>') # view another user's page
#def other_user(username):
#    return render_template('user.html', username=username)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', title = 'Register - Popcorn Journal')
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not password:
            flash('All fields are required.')
            return render_template('register.html', title='Register - Popcorn Journal')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.')
            return render_template('register.html', title='Register - Popcorn Journal')

        if User.query.filter_by(email=email).first():
            flash('Email already exists.')
            return render_template('register.html', title='Register - Popcorn Journal')
        
        # server-side validation to check if password and confirm password match
        if password != confirm_password:
            flash('Passwords do not match.')
            return render_template('register.html', title='Register - Popcorn Journal')

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Account created. Please log in.')
        return redirect(url_for('main.login'))


@bp.route('/reset-password')
def reset_password():
    return render_template('reset_password.html', title = 'Reset Password - Popcorn Journal')

@bp.route('/review')
def review():
    return render_template('review.html', title = 'Reviews - Popcorn Journal')

@bp.route('/search')
def search():
    return render_template('search.html', title = 'Search - Popcorn Journal')

@bp.route('/watchlist')
def watchlist():
    return render_template('watchlist.html', title = 'Watchlist - Popcorn Journal')

# Browse Lists page - shows all lists created by users, with option to click into each list to see the movies/series in that list
@bp.route('/lists')
def lists():
    mock_lists = [
        {'id': 3, 'name': 'Films Directed by Women', 'description': 'My favourite women-directed films.', 'movies': [1, 2, 3]},
        {'id': 2, 'name': 'Cozy Rainy Day Movies', 'description': 'Movies for cozy rainy days.', 'movies': [1, 2]}
    ]
    return render_template('lists.html', lists=mock_lists, title = 'Lists - Popcorn Journal')

# View personal page of lists - flow of webpages: click list on this page > list's page with contents > click movie/series > movie/series page with details and reviews
#@bp.route('/list/<int:list_id>')
#def list_detail(list_id):

@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been successfully logged out.')
    return redirect(url_for('main.index'))

@bp.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    #movie = {'title': 'Inception', 'id': movie_id, 'release_year': '2010', 'rating': 8.8}
    movie = Movie.query.get(movie_id)
    return render_template('review.html', movie=movie.title, title=f"{movie.title} - Popcorn Journal")
