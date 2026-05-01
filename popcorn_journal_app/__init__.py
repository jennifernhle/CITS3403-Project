from flask import Flask
from popcorn_journal_app.config import Config 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect() 
login = LoginManager()
login.login_view = 'main.login'  

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app) 
    login.init_app(app)

    from popcorn_journal_app.models import User
    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from popcorn_journal_app.routes import bp as main_blueprint 
    app.register_blueprint(main_blueprint)

    from popcorn_journal_app import models 
 
    return app