import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))

class LocalDevelopmentConfig():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = timedelta(seconds=900)
    SQLITE_DB_DIR = os.path.join(basedir, '../db_directory')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(SQLITE_DB_DIR, 'database.sqlite3')
    SECRET_KEY = 'n23049mvqqlmdv09q2adf4'
    DEBUG = True