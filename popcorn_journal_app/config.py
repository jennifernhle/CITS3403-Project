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

    db_url = os.getenv('DATABASE_URL')
    if db_url:
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(instance_path, 'popcorn_journal.sqlite3')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # TMDB API integration
    raw_key = os.getenv('TMDB_API_KEY')
    TMDB_API_KEY = raw_key if raw_key and raw_key.strip() else None
    TMDB_BASE_URL = "https://api.themoviedb.org/3"

    USE_TMDB_API = (os.getenv('USE_TMDB_API', 'False').lower() in ('1', 'true', 'yes')) and (TMDB_API_KEY is not None)

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Disabling of CSRF forms protection for testing
    WTF_CSRF_ENABLED = False
    USE_TMDB_API = False
