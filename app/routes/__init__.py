from flask import Flask
from .admin import admin
from .user import user
from .parcela import parcela
from .cultivo import cultivo
from .dispositivo import dispositivo
from .auth import auth
from app.routes.dashboard import dashboard
from app.routes.main import main


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'UT.17116'

    register_blueprints(app)

    return app


def register_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(user, url_prefix='/admin')
    app.register_blueprint(parcela, url_prefix='/admin')
    app.register_blueprint(cultivo, url_prefix='/admin')
    app.register_blueprint(dispositivo, url_prefix='/admin')
    app.register_blueprint(dashboard, url_prefix='/dashboard')