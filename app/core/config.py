# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    """
    Manages the application's configuration settings by loading them
    from a .env file. It uses Pydantic for data validation.

    Attributes:
        FIREBASE_SERVICE_ACCOUNT_KEY_PATH (str): Path to the Firebase service account JSON file.
        FIREBASE_DATABASE_URL (str): The database URL for the Firebase project.
        SMTP_HOST (str): The SMTP server host for sending emails.
        SMTP_PORT (int): The port for the SMTP server.
        SMTP_USER (str): The username for SMTP authentication.
        SMTP_PASSWORD (str): The password for SMTP authentication.
        FRONTEND_URL (str): The base URL for the frontend application.
    """
    # --- Firebase Configuration ---
    FIREBASE_SERVICE_ACCOUNT_KEY_PATH: str
    FIREBASE_DATABASE_URL: str

    # --- Email SMTP Configuration ---
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    # --- Frontend Configuration ---
    FRONTEND_URL: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'),
        env_file_encoding='utf-8',
        extra='ignore'
    )

# Create a single, globally accessible instance of the settings
settings = Settings()