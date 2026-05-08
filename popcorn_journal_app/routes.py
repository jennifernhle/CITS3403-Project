import os
import uuid
import requests
from flask import Blueprint, render_template, flash, redirect, url_for, jsonify, request, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from popcorn_journal_app import db
from popcorn_journal_app.models import User, Movie, Review, List, followers
from popcorn_journal_app.forms import RegistrationForm, LoginForm, MovieForm, ReviewForm

bp = Blueprint('main', __name__)

# AUTHENTICATION AND STATIC ROUTES
@bp.route('/')
def index():
    # Landing page for guests, activity feed for logged-in users
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        f_page = request.args.get('f_page', 1, type=int)
        active_tab = request.args.get('tab', 'global')

        # Global activity feed
        recent_pagination = Review.query.order_by(Review.date_posted.desc()).paginate(page=page, per_page=5, error_out=False)

        # Following feed - reviews from users the current user follows
        following_pagination = Review.query.join(followers, (followers.c.followed_id == Review.user_id)).filter(followers.c.follower_id == current_user.id).order_by(Review.date_posted.desc()).paginate(page=f_page, per_page=5, error_out=False)

        public = List.query.filter_by(public_status=True).order_by(List.id.desc()).limit(4).all()

        return render_template('home.html', title='Home', recent_reviews=recent_pagination.items, recent_pagination=recent_pagination, following_reviews=following_pagination.items, following_pagination=following_pagination, public_lists=public, active_tab=active_tab)
    return render_template('index.html', title='Welcome')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for("main.index"))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form, title="Login")

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Checking for existing identity
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken.')
            return render_template('register.html', form=form)
    
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.')
            return render_template('register.html', form=form)
                
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/about_us')
def about_us():
    return render_template('about_us.html', title = 'About Us')

@bp.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html', title = 'Forgot Password')

@bp.route('/reset-password')
def reset_password():
    return render_template('reset_password.html', title = 'Reset Password')


# USER PROFILES AND SOCIAL
@bp.route('/profile')
@login_required
def profile():
    # Viewing current user's own profile
    if not current_user.is_authenticated:
        flash('Please log in to view your profile.')
        return redirect(url_for('main.login'))
    
    user = current_user
    page = request.args.get('page', 1, type=int)
    reviews_pagination = user.reviews.order_by(Review.date_posted.desc()).paginate(page=page, per_page=5, error_out=False)
    return render_template('profile.html', title='Profile', user=current_user, recent_reviews=reviews_pagination.items, pagination=reviews_pagination)

@bp.route('/user/<int:user_id>')
def other_user(user_id):
    # Viewing another user's public profile
    if current_user.is_authenticated and current_user.id == user_id:
        return redirect(url_for('main.profile'))
    
    user = User.query.get_or_404(user_id)
    follower_count = user.followers.count()
    following_count = user.following.count()
    
    # Get user's public lists
    public_lists = user.lists.filter_by(public_status=True).order_by(List.id.desc()).limit(6).all()
    
    # Get user's recent reviews
    page = request.args.get('page', 1, type=int)
    reviews_pagination = user.reviews.order_by(Review.date_posted.desc()).paginate(page=page, per_page=5, error_out=False)
    
    # Check if current user is following this user
    is_following = False
    if current_user.is_authenticated:
        is_following = current_user.is_following(user)
    
    return render_template('user.html', title=f"{user.username}", user=user, follower_count=follower_count, following_count=following_count, is_following=is_following, public_lists=public_lists, recent_reviews=reviews_pagination.items, pagination=reviews_pagination)

@bp.route('/follow/<int:user_id>/<action>', methods=['POST'])
@login_required
def follow_user(user_id, action):
    user = User.query.get_or_404(user_id)
    
    if action == 'follow':
        current_user.follow(user)
        db.session.commit()
        return jsonify({ 'success': True, 'action': 'unfollow', 'follower_count': user.followers.count() })
    
    elif action == 'unfollow':
        current_user.unfollow(user)
        db.session.commit()
        return jsonify({ 'success': True, 'action': 'follow', 'follower_count': user.followers.count() })
    
    return jsonify({'success': False, 'error': 'Invalid action'}), 400

# MOVIES AND REVIEWS
@bp.route('/search')
def search():
    query = request.args.get('query', '')
    genre_filter = request.args.get('genre', '')
    year_filter = request.args.get('year', '')
    page = request.args.get('page', 1, type=int)

    form = MovieForm()
    results = Movie.query

    if query:
        results = results.filter(Movie.title.ilike(f'%{query}%'))
    if genre_filter:
        results = results.filter(Movie.genre == genre_filter)
    if year_filter:
        try:
            year_int = int(year_filter)
            results = results.filter(Movie.release_year == year_int)
        except ValueError:
            pass
    
    pagination = results.paginate(page=page, per_page=12, error_out=False)
    tmdb_enabled = tmdb_api_available()
    return render_template('search.html', results=pagination.items, pagination=pagination, title='Search Results', query=query, genre_filter=genre_filter, year_filter=year_filter, form=form, tmdb_enabled=tmdb_enabled)

@bp.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    review_form = ReviewForm()
    movie_form = MovieForm(obj=movie)
    user_review = None

    if current_user.is_authenticated:
        user_review = Review.query.filter_by(movie_id=movie_id, user_id=current_user.id).first()
        if user_review:
            review_form.rating.data = str(user_review.rating)
            review_form.content.data = user_review.content
    return render_template('movie_overview.html', movie=movie, review_form=review_form, movie_form=movie_form, user_review=user_review)

@bp.route('/add-movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    form = MovieForm()
    if form.validate_on_submit():
        existing_movie = Movie.query.filter(
            Movie.title.ilike(form.title.data),
            Movie.release_year == form.release_year.data
        ).first()

        # Prevention of duplicates
        if existing_movie:
            flash(f'The movie "{form.title.data}" ({form.release_year.data}) already exists!', 'warning')
            return render_template('add_movie.html', title='Add Movie', form=form)

        file = form.movie_img.data
        filename = None
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.root_path, 'static/posters', filename))

        new_movie = Movie(
            title=form.title.data,
            director=form.director.data,
            release_year=form.release_year.data,
            genre=form.genre.data,
            synopsis=request.form.get('synopsis'),
            movie_img=filename,
            creator_id=current_user.id
        )
        db.session.add(new_movie)
        db.session.commit()
        flash(f'Movie "{new_movie.title}" added to the database!', 'success')
        return redirect(url_for('main.search'))
    
    return render_template('add_movie.html', title='Add Movie', form=form)

@bp.route('/movie/<int:movie_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    form = MovieForm(obj=movie)
    
    if form.validate_on_submit():        
        movie.title = form.title.data
        movie.director = form.director.data
        movie.release_year = form.release_year.data
        movie.genre = form.genre.data
        movie.synopsis = request.form.get('synopsis')

        if isinstance(form.movie_img.data, FileStorage) and form.movie_img.data.filename != '':
            file = form.movie_img.data
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.root_path, 'static/posters')
            
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
                
            file.save(os.path.join(upload_path, filename))
            movie.movie_img = filename

        db.session.commit()
        flash("Movie details updated!", "success")
        return redirect(url_for('main.movie_detail', movie_id=movie.id))
    
    return render_template('add_movie.html', title='Edit Movie', form=form, movie=movie)

@bp.route('/movie/<int:movie_id>/review', methods=['POST'])
@login_required
def add_review(movie_id):
    form = ReviewForm()
    if form.validate_on_submit():
        existing_review = Review.query.filter_by(movie_id=movie_id, user_id=current_user.id).first()
        rating_val = int(form.rating.data)
        content_val = form.content.data

        if existing_review:
            existing_review.rating = rating_val
            existing_review.content = content_val
            flash('Review updated!', 'success')
        else:
            new_review = Review( rating=rating_val, content=content_val, movie_id=movie_id, user_id=current_user.id )
            db.session.add(new_review)
            flash('Review posted!', 'success')
        db.session.commit()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    return redirect(url_for('main.movie_detail', movie_id=movie_id))

@bp.route('/review/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    movie_id = review.movie_id
    
    if review.user_id != current_user.id:
        flash("You can only delete your own reviews.", "danger")
        return redirect(url_for('main.movie_detail', movie_id=movie_id))
    
    db.session.delete(review)
    db.session.commit()
    flash("Review removed.", "success")
    return redirect(url_for('main.movie_detail', movie_id=movie_id))

# Liking a review
@bp.route('/like-review/<int:review_id>', methods=['POST'])
@login_required
def like_review(review_id):
    review = Review.query.get_or_404(review_id)
    
    if current_user in review.likes:
        review.likes.remove(current_user)
        action = 'unliked'
    else:
        review.likes.append(current_user)
        action = 'liked'
    
    db.session.commit()
    
    return jsonify({'success': True, 'action': action,'count': review.likes.count()})

# LISTS, WATCHLISTS AND ACCOUNT MANAGEMENT
@bp.route('/lists')
@login_required
def lists():
    my_lists = List.query.filter_by(user_id=current_user.id).order_by(List.id.desc()).all()
    public_lists = List.query.filter(List.public_status == True, List.user_id != current_user.id).order_by(List.id.desc()).all()
    return render_template('lists.html', title='Lists', my_lists=my_lists, public_lists=public_lists)

# Creating a list
@bp.route('/list/create', methods=['POST'])
@login_required
def create_list():
    name = request.form.get('name')
    description = request.form.get('description')
    public_status = True if request.form.get('public_status') == 'on' else False
    movie_id = request.form.get('movie_id')

    next_page = request.args.get('next')

    if not name:
        flash("List name is required!", "warning")
        return redirect(next_page or url_for('main.lists'))

    new_list = List(
        name=name,
        description=description,
        public_status=public_status,
        user_id=current_user.id
    )

    if movie_id:
        movie = Movie.query.get(movie_id)
        if movie:
            new_list.movies.append(movie)

    db.session.add(new_list)
    db.session.commit()
    flash(f"List '{name}' created successfully!", "success")
    return redirect(next_page or url_for('main.lists'))

# Viewing a list
@bp.route('/list/<int:list_id>')
def view_list(list_id):
    user_list = List.query.get_or_404(list_id)
    
    if not user_list.public_status and user_list.user_id != current_user.id:
        flash("You do not have permission to view this private list.", "danger")
        return redirect(url_for('main.lists'))
    return render_template('list_detail.html', title=user_list.name, user_list=user_list)

# Adding movie to list
@bp.route('/list/add-movie/<int:movie_id>', methods=['POST'])
@login_required
def add_to_list(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    list_id = request.form.get('list_id')
    
    if not list_id:
        flash("Please select a list.", "warning")
        return redirect(url_for('main.movie_detail', movie_id=movie_id))
    
    user_list = List.query.get_or_404(list_id)
    
    if user_list.user_id != current_user.id:
        flash("You do not have permission to modify this list.", "danger")
        return redirect(url_for('main.movie_detail', movie_id=movie_id))
    
    if movie in user_list.movies:
        flash(f"'{movie.title}' is already in your list: {user_list.name}", "info")
    else:
        user_list.movies.append(movie)
        db.session.commit()
        flash(f"Added '{movie.title}' to {user_list.name}!", "success")
        
    return redirect(url_for('main.movie_detail', movie_id=movie_id))

# Removing movie from a list
@bp.route('/list/<int:list_id>/remove-movie/<int:movie_id>', methods=['POST'])
@login_required
def remove_from_list(list_id, movie_id):
    user_list = List.query.get_or_404(list_id)
    
    if user_list.user_id != current_user.id:
        flash("You do not have permission to modify this list.", "danger")
        return redirect(url_for('main.view_list', list_id=list_id))
    
    movie = Movie.query.get_or_404(movie_id)
    
    if movie in user_list.movies:
        user_list.movies.remove(movie)
        db.session.commit()
        flash(f"'{movie.title}' removed from {user_list.name}.", "info")
    else:
        flash("Movie not found in this list.", "warning")
        
    return redirect(url_for('main.view_list', list_id=list_id))

# Editing lists
@bp.route('/edit-list/<int:list_id>', methods=['POST'])
@login_required
def edit_list(list_id):
    user_list = List.query.get_or_404(list_id)
    
    if user_list.user_id != current_user.id:
        flash("You do not have permission to edit this list.", "danger")
        return redirect(url_for('main.lists'))
    
    user_list.name = request.form.get('name')
    user_list.description = request.form.get('description')
    user_list.public_status = True if request.form.get('public_status') == 'on' else False
    
    db.session.commit()
    flash("List updated successfully!", "success")
    return redirect(url_for('main.view_list', list_id=user_list.id))

@bp.route('/list/delete/<int:list_id>', methods=['POST']) # delete list
@login_required
def delete_list(list_id):
    list_to_delete = List.query.get_or_404(list_id)
    if list_to_delete.user_id != current_user.id:
        flash('You can only delete your own lists.', 'danger')
        return redirect(url_for('main.lists'))
    db.session.delete(list_to_delete)
    db.session.commit()
    flash(f'List "{list_to_delete.name}" has been deleted.', 'success')
    return redirect(url_for('main.lists'))

@bp.route('/watchlist')
@login_required
def watchlist():
    movies = current_user.watchlist
    return render_template('watchlist.html', title='My Watchlist', movies=movies)

@bp.route('/watchlist/toggle/<int:movie_id>', methods=['POST'])
@login_required
def toggle_watchlist(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie in current_user.watchlist:
        current_user.watchlist.remove(movie)
        action = 'removed'
    else:
        current_user.watchlist.append(movie)
        action = 'added'
    
    db.session.commit()
    return jsonify({'success': True, 'action': action})

@bp.route('/user/delete/<int:user_id>', methods=['POST']) # delete user account
@login_required
def delete_user(user_id):
    if user_id != current_user.id:
        flash('You can only delete your own account.')
        return redirect(url_for('main.profile'))
    
    user = User.query.get_or_404(user_id)
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('Your account and all associated data have been deleted.')
    return redirect(url_for('main.index'))

# TMDB API integration
@bp.route('/tmdb-search')
@login_required
def tmdb_search():
    query = request.args.get('query', '').strip()
    year = request.args.get('year', '').strip()
    genre = request.args.get('genre', '').strip()
    
    if not any([query, year, genre]):
        return jsonify([])

    if not tmdb_api_available():
        return jsonify([])

    api_key = current_app.config.get('TMDB_API_KEY')
    
    if query:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}"
        if year:
            url += f"&primary_release_year={year}"
    else:
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}"
        if year:
            url += f"&primary_release_year={year}"
        if genre:
            # TMDB genre IDs
            genre_map = {
                'Action': 28, 'Adventure': 12, 'Animation': 16, 'Comedy': 35, 'Crime': 80,
                'Documentary': 99, 'Drama': 18, 'Family': 10751, 'Fantasy': 14, 'History': 36,
                'Horror': 27, 'Music': 10402, 'Mystery': 9648, 'Romance': 10749, 'Sci-Fi': 878,
                'TV Movie': 10770, 'Thriller': 53, 'War': 10752, 'Western': 37
            }
            genre_id = genre_map.get(genre)
            if genre_id:
                url += f"&with_genres={genre_id}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for m in data.get('results', []):
            results.append({
                'tmdb_id': m.get('id'),
                'title': m.get('title'),
                'release_year': (m.get('release_date') or "0000")[:4],
                'genre': genre or 'General',
                'poster_path': m.get('poster_path'),
                'local': False
            })
        return jsonify(results)
    except Exception as e:
        return jsonify([]), 500

@bp.route('/import-tmdb-movie/<int:tmdb_id>', methods=['POST'])
@login_required
def import_tmdb_movie(tmdb_id):
    if not tmdb_api_available():
        return jsonify({"error": "TMDB API is not enabled or configured."}), 503

    try:
        # Prevention of duplicates
        existing = Movie.query.filter_by(tmdb_id=tmdb_id).first()
        if existing:
            return jsonify({"message": "Movie already in your database!"}), 200

        # Fetching full details from TMDB
        api_key = current_app.config.get('TMDB_API_KEY')
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}&append_to_response=credits"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        movie_data = response.json()

        # Extracting director from credits
        director_name = next(
            (
                crew_member.get('name')
                for crew_member in movie_data.get('credits', {}).get('crew', [])
                if crew_member.get('job') == 'Director'
            ),
            None,
        )

        # Creation of the movie with TMDB
        new_movie = Movie(
            title=movie_data.get('title', 'Unknown'),
            release_year=safe_int(movie_data.get('release_date', '0000')[:4]),
            director=director_name or 'Unknown',
            genre=movie_data.get('genres', [{}])[0].get('name', 'General'),
            synopsis=movie_data.get('overview', 'No description available.'),
            movie_img=movie_data.get('poster_path'),
            tmdb_id=tmdb_id,
            creator_id=current_user.id
        )

        db.session.add(new_movie)
        db.session.commit()
        return jsonify({"message": f"Successfully imported {new_movie.title}!"}), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc() 
        return jsonify({"error": f"Import failed: {str(e)}"}), 500

# Helpers and utilities
def safe_int(val, default=0):
    try:
        if isinstance(val, str) and '-' in val:
            val = val[:4] # Take '2024' from '2024-12-25'
        return int(val) if val and val != "N/A" else default
    except (ValueError, TypeError):
        return default

def safe_float(val, default=0.0):
    try:
        return float(val) if val and val != "N/A" else default
    except (ValueError, TypeError):
        return default

def tmdb_api_available():
    return current_app.config.get('USE_TMDB_API', False) and bool(current_app.config.get('TMDB_API_KEY'))