import os
import logging
import sys
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask
from sqlalchemy import func
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.extensions import db
from app.models import Registro, Dispositivo, Alerta, DataP0, Usuario, Fase
from app.services.email_service import alerta_humedad_cliente, alerta_humedad_admin
from app.config import config_by_name

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()

# Cargar datos desde el archivo Excel
ruta_excel = os.path.join(os.path.dirname(__file__), "../data/tabla_alertas.xlsx")
if not os.path.exists(ruta_excel):
    logger.error(f"El archivo {ruta_excel} no existe.")
    sys.exit(1)

alertas_df = pd.read_excel(ruta_excel)


def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    env_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_by_name[env_name])
    db.init_app(app)
    return app


app = create_app()


def verificar_alertas_humedad():
    """Verifica las alertas de humedad relativa en los últimos 15 minutos"""
    now = datetime.now()
    hace_15_min = now - timedelta(minutes=15)

    with app.app_context():
        with db.session() as session:
            registros = session.query(Registro).all()

            for registro in registros:
                dispositivo = session.get(Dispositivo, registro.fk_dispositivo)
                if not dispositivo:
                    continue

                fase = session.get(Fase, registro.fk_fase)
                if not fase:
                    continue

                humedad_max = session.query(func.max(DataP0.humedad)).filter(
                    DataP0.chipid == dispositivo.chipid,
                    DataP0.fecha.between(hace_15_min, now)
                ).scalar()
                humedad_min = session.query(func.min(DataP0.humedad)).filter(
                    DataP0.chipid == dispositivo.chipid,
                    DataP0.fecha.between(hace_15_min, now)
                ).scalar()

                if humedad_max is None or humedad_min is None:
                    continue

                alertas_cultivo = alertas_df[
                    (alertas_df['Cultivo'].str.strip().str.lower() == fase.cultivo.strip().lower()) &
                    (alertas_df['Fase'].str.strip().str.lower() == fase.nombre.strip().lower())
                ]

                if alertas_cultivo.empty:
                    continue

                alertas_generadas = []
                if humedad_min < alertas_cultivo['HR MIN'].values[0]:
                    alertas_generadas.append("Humedad relativa mínima")
                if humedad_max > alertas_cultivo['HR MAX'].values[0]:
                    alertas_generadas.append("Humedad relativa máxima")

                if not alertas_generadas:
                    continue

                mensaje_alerta = f"🚨 ALERTA: {', '.join(alertas_generadas)}. Humedades registradas: Min {humedad_min}% / Max {humedad_max}%."

                # Enviar alerta al cliente
                usuario = session.get(Usuario, registro.fk_usuario)
                if usuario and usuario.correo:
                    alerta_humedad_cliente(usuario.correo, fase.cultivo, fase.nombre, humedad_min, humedad_max, mensaje_alerta)

                # Enviar alerta única al administrador
                alerta_humedad_admin(dispositivo.chipid, humedad_min, humedad_max, mensaje_alerta)

                nueva_alerta = Alerta(
                    mensaje=mensaje_alerta,
                    fk_dispositivo=registro.fk_dispositivo,
                    fk_fase=fase.id,
                    cultivo_nombre=fase.cultivo,
                    nivel_alerta="Crítica"
                )
                session.add(nueva_alerta)
                session.commit()


if __name__ == "__main__":
    verificar_alertas_humedad()
