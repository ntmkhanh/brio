from ctypes import cast
from distutils.debug import DEBUG
from decouple  import config
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS=config('SQLALCHEMY_TRACK_MODIFICATIONS',cast=bool)
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'recipe_database'

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:''@localhost/recipe_database"
    DEBUG=True
    SQLALCHEMY_ECHO=True



class ProdConfig(Config):
    pass

class TestConfig(Config):
    pass