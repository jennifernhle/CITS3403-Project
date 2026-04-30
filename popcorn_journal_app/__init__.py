from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from popcorn_journal_app.config import Config

app = Flask(__name__) 
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app) # configure the login manager to work with Flask app
login_manager.login_view = 'main.login' # Avoids 401 Unauthorized error if page with a @login_required decorator is accessed without authentication and instead redirects unauthenticated users to endpoint for the login page

# Import User model for login manager
from popcorn_journal_app.models import User

@login_manager.user_loader # user_loader callback to reload user from the user ID that is stored in the session
def load_user(user_id):
    return User.query.get(int(user_id))

# import routes at end of script to avoid common Flask problem of circular imports
from popcorn_journal_app.routes import bp
app.register_blueprint(bp)

from popcorn_journal_app import models 