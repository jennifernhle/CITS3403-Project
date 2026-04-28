from flask import Flask
from popcorn_journal_app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__) 
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# import routes at end of script to avoid common Flask problem of circular imports
from popcorn_journal_app.routes import bp
app.register_blueprint(bp)

from popcorn_journal_app import models 