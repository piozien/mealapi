"""Module containing application constants."""
import os
from dotenv import load_dotenv

load_dotenv()

EXPIRATION_MINUTES = int(os.getenv('EXPIRATION_MINUTES', 30))
SECRET_KEY = os.getenv('SECRET_KEY', "")
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

API_URL_SAPLING = os.getenv('API_URL_SAPLING', "")
API_KEY_SAPLING = os.getenv('API_KEY_SAPLING', "")
