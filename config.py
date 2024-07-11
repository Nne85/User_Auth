from dotenv import load_dotenv
import os
import psycopg2
# Load environment variables from .env file
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

class TestingConfig(Config):
    TESTING =True
    SQLALCHEMY_DATABASE_URI = "postgresql://test:testing@localhost/teat_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
