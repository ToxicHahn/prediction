import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback_secret_key')
    BREVO_API_KEY = os.environ.get('BREVO_API_KEY')
