from popcorn_journal_app import db

# ** remove comments later: **
# each class is a table
# __repr__ is object's string representation - for debugging purposes

class User(db.Model):
    # USER INFO
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    dob = db.Column(db.Date, nullable=True)

    # STATISTICS
    # Note: Will need to determine the best way to calculate these counts,
    # such as http GET actual values from database and then get length of each list.
    follower_count = db.Column(db.Integer, default=0) # number of followers for the user
    review_count = db.Column(db.Integer, default=0) # number of reviews written by the user
    list_count = db.Column(db.Integer, default=0) # number of lists created by the user

    def __repr__(self):
        return f'<User {self.username}>'

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    director = db.Column(db.String(64))
    release_year = db.Column(db.Integer)

    def __repr__(self):
        return f'<Movie {self.title}>'

class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    director = db.Column(db.String(64))
    release_year = db.Column(db.Integer)

    def __repr__(self):
        return f'<Series {self.title}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # author of review
    content_type = db.Column(db.String(10))  # 'movie' or 'series'
    content_id = db.Column(db.Integer)  # ID of the movie or series being reviewed
    rating = db.Column(db.Float) # out of 5, can have half-stars (e.g., 4.5)
    review_text = db.Column(db.Text)
    date_posted = db.Column(db.DateTime) # Timestamp of when the review was posted
    like_count = db.Column(db.Integer, default=0) # Number of likes for the review

    def __repr__(self):
        return f'<Review {self.id} by User {self.user_id} on {self.date_posted}>'
    
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