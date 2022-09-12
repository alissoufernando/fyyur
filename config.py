import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
from urllib.parse import quote_plus
basedir = os.path.abspath(os.path.dirname(__file__))
from dotenv import load_dotenv
 
load_dotenv()

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
PASSWORD= quote_plus(os.getenv('DB_PASSWORD'))
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:{}@localhost:5432/fyyur'.format(PASSWORD)
SQLALCHEMY_TRACK_MODIFICATIONS = False
