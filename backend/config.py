"""Configuration module for the Flask application."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Database
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "lab_components_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-secret-change-me")
    JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

    # Fine
    FINE_PER_DAY = float(os.getenv("FINE_PER_DAY", "10"))

    # Issue duration
    DEFAULT_ISSUE_DAYS = int(os.getenv("DEFAULT_ISSUE_DAYS", "14"))

    # CORS
    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:5173")

    # Flask
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))

    @classmethod
    def get_db_dsn(cls):
        """Return the PostgreSQL DSN connection string."""
        return (
            f"host={cls.DB_HOST} "
            f"port={cls.DB_PORT} "
            f"dbname={cls.DB_NAME} "
            f"user={cls.DB_USER} "
            f"password={cls.DB_PASSWORD}"
        )
