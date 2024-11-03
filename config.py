import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/prophetestate')
    TREB_API_KEY = os.getenv('TREB_API_KEY')
    MAPS_API_KEY = os.getenv('MAPS_API_KEY')