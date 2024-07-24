import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SMTP2GO_API_KEY = os.environ.get('SMTP2GO_API_KEY') or 'your_smtp2go_api_key'
    SMTP2GO_USERNAME = os.environ.get('SMTP2GO_USERNAME') or 'your_smtp2go_username'
    SMTP2GO_PASSWORD = os.environ.get('SMTP2GO_PASSWORD') or 'your_smtp2go_password'
    SMTP2GO_SMTP_SERVER = 'mail.smtp2go.com'
    SMTP2GO_SMTP_PORT = 587
