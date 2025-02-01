from flask import Flask
from app.routes.admin import admin
from app.routes.user import user
from app.routes.parcela import parcela
from app.routes.cultivo import cultivo
from app.routes.dispositivo import dispositivo
from app.routes.auth import auth
from app.routes.dashboard import dashboard
from app.routes.main import main
import os


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    register_blueprints(app)

    return app


def register_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(user, url_prefix='/admin/usuarios')
    app.register_blueprint(parcela, url_prefix='/admin/parcelas')
    app.register_blueprint(cultivo, url_prefix='/admin/cultivos')
    app.register_blueprint(dispositivo, url_prefix='/admin/dispositivos')
    app.register_blueprint(dashboard, url_prefix='/admin/dashboard')