from flask import Flask
from app.routes.admin.admin import admin
from app.routes.admin.user import user
from app.routes.admin.parcela import parcela
from app.routes.admin.cultivo import cultivo
from app.routes.admin.dispositivo import dispositivo
from app.routes.auth import auth
from app.routes.dashboard import dashboard
from app.routes.admin.registro import registro
from app.routes.main import main
from app.routes.client.client import client
from app.routes.client.datos import datos
from app.routes.client.clima import clima
from app.routes.client.cultivoCliente import cultivoCliente
from app.routes.client.alertas import alertasCliente

import os


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    register_blueprints(app)

    return app


def register_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(user, url_prefix='/admin/usuario')
    app.register_blueprint(parcela, url_prefix='/admin/parcela')
    app.register_blueprint(cultivo, url_prefix='/admin/cultivo')
    app.register_blueprint(dispositivo, url_prefix='/admin/dispositivo')
    app.register_blueprint(registro, url_prefix='/admin/registro')
    app.register_blueprint(client, url_prefix='/client')
    app.register_blueprint(datos, url_prefix='/client/datos')
    app.register_blueprint(clima, url_prefix='/client/clima')
    app.register_blueprint(cultivoCliente, url_prefix='/client/cultivoCliente')
    app.register_blueprint(alertasCliente, url_prefix='/client/alertasCliente')