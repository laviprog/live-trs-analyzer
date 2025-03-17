import logging

from src.config import settings

logger = logging.getLogger(__name__)

MODEL_URL = settings.MODEL_URL
EMAIL_MODEL = settings.USERNAME_MODEL
PASSWORD_MODEL = settings.PASSWORD_MODEL