from popcorn_journal_app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# ** remove comments later: **
# each class is a table
# __repr__ is object's string representation - for debugging purposes

# Association table for followers (many-to-many relationship)
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

watchlist_items = db.Table('watchlist_items',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    # USER INFO
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=True) # nullable now only because error occurring in registration form, there is no username being passed to the User model when creating a new user, will need to fix this in the registration form and then can set nullable=False
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    user_img = db.Column(db.String(256), nullable=True) # URL or file path to user's profile image
    profile_pic = db.Column(db.String(120), default='user.png')
    bio = db.Column(db.String(256), nullable=True)
    watchlist = db.relationship('Movie', secondary=watchlist_items, backref=db.backref('interested_users', lazy='dynamic'))
    reviews = db.relationship('Review', backref='reviewer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Relationships for followers
    following = db.relationship('User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    # STATISTICS
    # Note: Will need to determine the best way to calculate these counts,
    # such as http GET actual values from database and then get length of each list.
    follower_count = db.Column(db.Integer, default=0) # number of followers for the user
    review_count = db.Column(db.Integer, default=0) # number of reviews written by the user
    list_count = db.Column(db.Integer, default=0) # number of lists created by the user
    logged_movie_count = db.Column(db.Integer, default=0) # number of movies watched by the user AGAIN, will need to change this so it is calculated from the length of the list in the database.
    logged_series_count = db.Column(db.Integer, default=0) # number of series watched by the user, same as above.

    def follow(self, user):
        """Follow a user"""
        if not self.is_following(user):
            self.following.append(user)
            user.follower_count = len(user.followers.all())

    def unfollow(self, user):
        """Unfollow a user"""
        if self.is_following(user):
            self.following.remove(user)
            user.follower_count = len(user.followers.all())

    def is_following(self, user):
        """Check if current user is following another user"""
        return self.following.filter(followers.c.followed_id == user.id).count() > 0

    def __repr__(self):
        return f'<User {self.username}>'

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    director = db.Column(db.String(64))
    release_year = db.Column(db.Integer)
    genre = db.Column(db.String(64))
    movie_img = db.Column(db.String(256), nullable=True) # URL or file path to movie cover image
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reviews = db.relationship('Review', backref='movie', lazy=True)

    def __repr__(self):
        return f'<Movie {self.title}>'

class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    director = db.Column(db.String(64))
    release_year = db.Column(db.Integer)
    series_img = db.Column(db.String(256), nullable=True) # URL or file path to series cover image (perhaps latest season's poster)

    def __repr__(self):
        return f'<Series {self.title}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=True) 
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=True)
    
    rating = db.Column(db.Float) 
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=db.func.now())
    like_count = db.Column(db.Integer, default=0)

    author = db.relationship('User', backref='my_reviews', lazy=True)

    def __repr__(self):
        return f'<Review {self.id} by {self.user_id}>'
    
class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # owner of the list
    name = db.Column(db.String(128)) # name of the list
    description = db.Column(db.Text) # description of the list
    public_status = db.Column(db.Boolean, default=False) # public or private list, default = private
    type = db.Column(db.String(10)) # 'watchlist' or 'custom'
    content_type = db.Column(db.String(10))  # 'movie' or 'series' or 'mixed'
    content_ids = db.Column(db.String) # comma-separated list of movie/series IDs
    follower_count = db.Column(db.Integer, default=0) # number of followers for the list
    
    def __repr__(self):
        return f'<List {self.name} by User {self.user_id}>'