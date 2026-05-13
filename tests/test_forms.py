from popcorn_journal_app.forms import RegistrationForm, LoginForm, MovieForm, ReviewForm

# Registration form requirements
def test_registration_validation_rules(app):
    form = RegistrationForm()
    
    # Fail - password missing uppercase/number
    form.username.data = 'testuser'
    form.email.data = 'test@example.com'
    form.password.data = 'password'
    form.confirm_password.data = 'password'
    assert not form.validate()
    
    # Pass - valid data
    form.password.data = 'Password123!'
    form.confirm_password.data = 'Password123!'
    assert form.validate()

def test_login_form_requirements(app):
    form = LoginForm()
    form.email.data = 'invalid-email'
    form.password.data = ''
    assert not form.validate()

# Movie form constraints (year)
def test_movie_form_requirements(app):
    form = MovieForm()
    form.title.data = 'Valid Title'
    form.director.data = 'Valid Director'
    form.genre.data = 'Drama'
    
    # Fail - year out of range
    form.release_year.data = 1800
    assert not form.validate()
    
    # Pass - valid year
    form.release_year.data = 2024
    assert form.validate()

# Review form constraints (length)
def test_review_form_length_constraints(app):
    form = ReviewForm()
    form.rating.data = '8'
    
    # Fail - too short
    form.content.data = 'Bad'
    assert not form.validate()
    
    # Pass - enough detail
    form.content.data = 'This movie was actually quite good.'
    assert form.validate()