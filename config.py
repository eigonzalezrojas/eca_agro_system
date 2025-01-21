from dotenv import load_dotenv
import os


if not load_dotenv():
    print("Advertencia: No se pudo cargar el archivo .env")


def str_to_bool(value):
    return value.lower() in ['true', '1', 'yes'] if isinstance(value, str) else bool(value)


class Config:    
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = str_to_bool(os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False'))
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}