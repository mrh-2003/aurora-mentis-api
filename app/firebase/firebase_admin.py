# app/firebase/firebase_admin.py

import firebase_admin
from firebase_admin import credentials, firestore, auth
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred, {
        'databaseURL': settings.FIREBASE_DATABASE_URL
    })

    # Get Firestore client and Auth service
    db = firestore.client()
    auth_service = auth

    logger.info("Firebase Admin SDK initialized successfully.")

except Exception as e:
    logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
    # In a real application, you might want to handle this more gracefully,
    # but for now, we'll allow the app to fail on startup if Firebase isn't configured.
    db = None
    auth_service = None
    raise