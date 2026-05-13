import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    # Loads SECRET_KEY from environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for Flask application")
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(instance_path, 'popcorn_journal.sqlite3')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # TMDB API integration
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')
    TMDB_BASE_URL = "https://api.themoviedb.org/3"
    USE_TMDB_API = os.getenv('USE_TMDB_API', 'True').lower() in ('1', 'true', 'yes')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Disabling of CSRF forms protection for testing
    WTF_CSRF_ENABLED = False
    USE_TMDB_API = False
