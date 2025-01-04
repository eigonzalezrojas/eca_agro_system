from dotenv import load_dotenv
import os

if not load_dotenv():
    print("Error: No se pudo cargar el archivo .env")

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY')