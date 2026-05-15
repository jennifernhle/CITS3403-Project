from popcorn_journal_app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Association tables
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

watchlist_items = db.Table('watchlist_items',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id', ondelete='CASCADE'), primary_key=True)
)

list_movies = db.Table('list_movies',
    db.Column('list_id', db.Integer, db.ForeignKey('list.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True)
)

review_likes = db.Table('review_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('review_id', db.Integer, db.ForeignKey('review.id'), primary_key=True)
)

favourite_movies = db.Table('favourite_movies',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id', ondelete='CASCADE'), primary_key=True)
)



# Models
class User(db.Model, UserMixin):
    # User information
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # Profile details
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    profile_pic = db.Column(db.String(120), default='user.png')
    bio = db.Column(db.String(256), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    watchlist = db.relationship('Movie', secondary=watchlist_items, backref=db.backref('interested_users', lazy='dynamic'))
    reviews = db.relationship('Review', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    liked_reviews = db.relationship('Review', secondary=review_likes, backref=db.backref('likes', lazy='dynamic'), lazy='dynamic')
    lists = db.relationship('List', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    favourite_movies = db.relationship('Movie', secondary=favourite_movies, backref=db.backref('favourited_by', lazy='dynamic'), lazy='dynamic')
    following = db.relationship('User', secondary=followers, primaryjoin=(followers.c.follower_id == id), secondaryjoin=(followers.c.followed_id == id), backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    # Password management
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    # Social methods
    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(followers.c.followed_id == user.id).count() > 0

    # Count of reviews written by user
    @property
    def logged_movie_count(self):
        return self.reviews.count()

    # Count of lists created by user
    @property
    def list_count(self):
        return self.lists.count()
    
    # Count of followers
    @property
    def follower_count(self):
        return self.followers.count()
    
    # Count of following
    @property
    def following_count(self):
        return self.following.count()

    def __repr__(self):
        return f'<User {self.username}>'

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    director = db.Column(db.String(64))
    release_year = db.Column(db.Integer)
    genre = db.Column(db.String(64))
    synopsis = db.Column(db.Text, nullable=True)
    movie_img = db.Column(db.String(256), nullable=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=True)

    #Relationship with creator (who added it) and reviews
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reviews = db.relationship('Review', backref='movie', lazy='dynamic', cascade='all, delete-orphan')

    # Average ratings based on overall user reviews
    def get_average_rating(self):
        reviews_list = self.reviews.all()
        if not reviews_list:
            return 0
        total = sum(review.rating for review in reviews_list)
        return total / len(reviews_list)

    def __repr__(self):
        return f'<Movie {self.title}>'

# Individual user reviews and ratings for movies
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=True) 
    
    rating = db.Column(db.Integer) 
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<Review {self.id} by {self.user_id}>'

# Collections/lists of movies (public/private)
class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(128))
    description = db.Column(db.Text)
    public_status = db.Column(db.Boolean, default=False)

    movies = db.relationship('Movie', secondary='list_movies', backref='contained_in_lists')

    #Count of movies currently in list
    @property
    def movie_count(self):
        return len(self.movies)
    
    def __repr__(self):
        return f'<List {self.name} by User {self.user_id}>'