import os
import logging
import sys
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask
from sqlalchemy import text, inspect, func
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.extensions import db
from app.models import Registro, Dispositivo, Alerta, DataP0, Usuario, Cultivo
from app.services.email_service import alerta_temperatura_eca
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
logger.info(f"Columnas del archivo Excel: {alertas_df.columns.tolist()}")
logger.info(f"Primeros registros del Excel: \n{alertas_df.head()}")


def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    env_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_by_name[env_name])
    db.init_app(app)
    return app


app = create_app()


def verificar_alertas_temperatura():
    """Verifica las alertas de temperatura en los últimos 15 minutos"""
    now = datetime.now()
    hace_15_min = now - timedelta(minutes=15)

    with app.app_context():
        with db.session() as session:
            registros = session.query(Registro).all()

            for registro in registros:
                dispositivo = session.get(Dispositivo, registro.fk_dispositivo)
                if not dispositivo:
                    logger.warning(f"Dispositivo {registro.fk_dispositivo} no encontrado.")
                    continue

                logger.info(
                    f"Verificando dispositivo: {dispositivo.chipid} para cultivo {registro.fk_cultivo} en fase {registro.fk_cultivo_fase}")

                # Obtener datos de temperatura del dispositivo en los últimos 15 minutos
                temp_max = session.query(func.max(DataP0.temperatura)).filter(
                    DataP0.chipid == dispositivo.chipid,
                    DataP0.fecha.between(hace_15_min, now)
                ).scalar()
                temp_min = session.query(func.min(DataP0.temperatura)).filter(
                    DataP0.chipid == dispositivo.chipid,
                    DataP0.fecha.between(hace_15_min, now)
                ).scalar()

                logger.info(f"Temperaturas registradas - Min: {temp_min}°C / Max: {temp_max}°C")

                if temp_max is None or temp_min is None:
                    logger.warning(f"No hay registros recientes para chipid {dispositivo.chipid}.")
                    continue

                # Buscar el cultivo y fase en la tabla de alertas
                cultivo = session.get(Cultivo, registro.fk_cultivo)
                alertas_cultivo = alertas_df[
                    (alertas_df['Cultivo'].str.strip().str.lower() == cultivo.nombre.strip().lower()) &
                    (alertas_df['Fase'].str.strip().str.lower() == registro.fk_cultivo_fase.strip().lower())]

                if alertas_cultivo.empty:
                    logger.warning(
                        f"No se encontraron parámetros de alerta para {cultivo.nombre} en fase {registro.fk_cultivo_fase}.")
                    continue

                logger.info(f"Parámetros de alerta encontrados: {alertas_cultivo}")

                alertas_generadas = []

                # Evaluar alertas según la tabla de parámetros
                if temp_min < alertas_cultivo['Temperatura crítica mínima'].values[0]:
                    alertas_generadas.append("Temperatura crítica mínima")
                if temp_min < alertas_cultivo['Temperatura mínima de crecimiento'].values[0]:
                    alertas_generadas.append("T° mínima de crecimiento")
                if temp_min < alertas_cultivo['Rango Temperatura Mínimo Óptimo'].values[0]:
                    alertas_generadas.append("Rango T° Mínimo Óptimo")
                if temp_max > alertas_cultivo['Rango Temperatura Máximo Óptimo'].values[0]:
                    alertas_generadas.append("Rango T° Máximo Óptimo")
                if temp_max > alertas_cultivo['Temperatura máxima de crecimiento'].values[0]:
                    alertas_generadas.append("T° máxima de crecimiento")

                if not alertas_generadas:
                    continue

                # Generar mensaje de alerta
                mensaje_alerta = f"🚨 ALERTA: {', '.join(alertas_generadas)}. Temperaturas registradas: Min {temp_min}°C / Max {temp_max}°C."
                logger.info(f"Generando alerta: {mensaje_alerta}")

                # Enviar alerta por correo
                usuario = session.get(Usuario, registro.fk_usuario)
                if usuario and usuario.correo:
                    alerta_temperatura_eca(usuario.correo, cultivo.nombre, registro.fk_cultivo_fase, temp_max,
                                           mensaje_alerta)
                    logger.info(f"Correo enviado a: {usuario.correo}")
                else:
                    logger.warning("No se pudo enviar el correo, usuario sin dirección de correo.")

                # Guardar alerta en la base de datos
                nueva_alerta = Alerta(
                    mensaje=mensaje_alerta,
                    fk_dispositivo=registro.fk_dispositivo,
                    fk_cultivo=registro.fk_cultivo,
                    fk_cultivo_fase=registro.fk_cultivo_fase,
                    nivel_alerta="Crítica"
                )
                session.add(nueva_alerta)
                session.commit()
                logger.info(f"✅ Alerta guardada en la base de datos: {mensaje_alerta}")

    logger.info("✅ Revisión de alertas completada.")


if __name__ == "__main__":
    verificar_alertas_temperatura()
