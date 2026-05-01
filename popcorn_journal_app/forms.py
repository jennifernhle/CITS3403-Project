from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, NumberRange
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('LOGIN')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=20),
        # set to match auth.js logic
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])', 
               message="Password must contain uppercase, lowercase, and a number.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('CREATE ACCOUNT')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    bio = TextAreaField('About Me')
    profile_pic = FileField('Update Profile Picture', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    submit = SubmitField('Update Profile')


class MovieForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired(), Length(max=128)])
    director = StringField('Director', validators=[DataRequired(), Length(max=64)])
    release_year = IntegerField('Release Year', validators=[DataRequired(), NumberRange(min=1888, max=2100, message="Please enter a valid year.")])
    genre = SelectField('Genre', choices=[
        ('', 'Select a genre...'), 
        ('Action', 'Action'),
        ('Adventure', 'Adventure'),
        ('Animation', 'Animation'),
        ('Comedy', 'Comedy'),
        ('Documentary', 'Documentary'),
        ('Drama', 'Drama'),
        ('Fantasy', 'Fantasy'),
        ('Horror', 'Horror'),
        ('Musical', 'Musical'),
        ('Mystery', 'Mystery'),
        ('Romance', 'Romance'),
        ('Sci-Fi', 'Sci-Fi'),
        ('Sports', 'Sports'),
        ('Thriller', 'Thriller'),
        ('Western', 'Western'),
        ('Other', 'Other')
    ], validators=[DataRequired(message="Please select a genre.")])
    movie_img = FileField('Movie Poster', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    submit = SubmitField('Add Movie')