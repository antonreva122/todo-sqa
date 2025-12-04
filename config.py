import os
from dotenv import load_dotenv  # requires python-dotenv install

load_dotenv()  # loads everything from .env into environment variables


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "replace-with-real-key-during-production"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///" + os.path.join(
        basedir, "app.db"
    )
    # CSRF Protection: Set time limit for CSRF tokens (1 hour = 3600 seconds)
    WTF_CSRF_TIME_LIMIT = 3600
    # Security: Prevent CSRF tokens from being sent in cross-site requests
    WTF_CSRF_SSL_STRICT = False
    # Cookie Security: Prevent cookie from being sent in cross-site requests
    SESSION_COOKIE_SAMESITE = "Lax"
    # Ensure cookies are only sent over HTTPS in production
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    # Prevent JavaScript from accessing session cookies
    SESSION_COOKIE_HTTPONLY = True
