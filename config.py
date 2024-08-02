# config.py stores all the configurations for the entire app in 1 centralized location
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "Super_Secret_Key"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'myfoodbudget.db')}"
    DATABASE = os.path.join(basedir, 'myfoodbudget.db')
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"


class DevelopmentConfig(Config):
    DEBUG = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

# create testing and production config, when dev is shiftet to that stage

