"""
config.py
---------
Loads environment variables and initialises the Firebase Admin SDK.
This file runs ONCE when the app starts.
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load values from the .env file into os.environ
load_dotenv()


class Settings(BaseSettings):
    """All app-level settings come from environment variables."""

    firebase_project_id: str
    firebase_credentials_path: str = "firebase_credentials.json"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


# Create a single Settings instance that the rest of the app imports
settings = Settings()


# ── Firebase Initialisation ──────────────────────────────────────────────────
# We use a module-level flag so Firebase is only initialised once,
# even if this module is imported multiple times.

def init_firebase() -> None:
    """Initialise Firebase Admin SDK if it has not been initialised yet."""
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.firebase_credentials_path)
        firebase_admin.initialize_app(cred, {
            "projectId": settings.firebase_project_id,
        })


# Run initialisation immediately when the module is loaded
init_firebase()


# ── Firestore Client Factory ─────────────────────────────────────────────────
def get_firestore_client():
    """Return a Firestore client.  Call this wherever you need DB access."""
    return firestore.client()


# ── Firebase Auth Client ─────────────────────────────────────────────────────
# firebase_admin.auth is a module, so we just re-export it for convenience
firebase_auth = auth
