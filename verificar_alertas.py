import os
import logging
from datetime import datetime, timedelta

from flask import Flask
from sqlalchemy import text, inspect
from dotenv import load_dotenv
from app.extensions import db
from app.models import Registro, Dispositivo, Alerta
from app.services.email_service import alerta_temperatura_eca
from app.config import config_by_name

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()


def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)

    # Cargar configuración desde config.py
    env_name = os.getenv('FLASK_ENV', 'development')  # Por defecto, usa 'development'
    app.config.from_object(config_by_name[env_name])  # Accede directamente al diccionario de config

    db.init_app(app)  # ✅ Enlazar SQLAlchemy con la app

    return app


app = create_app()  # Crear la app antes de usar db

with app.app_context():  # ✅ Envolver en contexto de aplicación
    inspector = inspect(db.engine)
    tablas_disponibles = inspector.get_table_names()
    print("📌 Tablas disponibles en la base de datos:", tablas_disponibles)

    if "dataP0" in tablas_disponibles:
        print("✅ La tabla 'dataP0' EXISTE en la base de datos.")
    else:
        print("❌ La tabla 'dataP0' NO se encuentra en la base de datos.")


def verificar_alertas_temperatura():
    """Verifica la temperatura de los dispositivos en los últimos 15 minutos y almacena alertas en la base de datos."""
    now = datetime.now()
    hace_15_min = now - timedelta(minutes=15)

    with app.app_context():  # ✅ Envolver TODA la ejecución en app_context()
        with db.session() as session:
            registros = session.query(Registro).all()

            for registro in registros:
                dispositivo = session.get(Dispositivo, registro.fk_dispositivo)
                if not dispositivo:
                    logger.warning(f"Dispositivo {registro.fk_dispositivo} no encontrado.")
                    continue

                fuente_datos = registro.fuente
                if not fuente_datos:
                    logger.warning(f"⚠️ No se encontró fuente de datos para el dispositivo {dispositivo.chipid}.")
                    continue

                # Validar existencia de la tabla antes de consultar
                try:
                    inspector = inspect(db.engine)
                    if fuente_datos not in inspector.get_table_names():
                        logger.warning(f"⚠️ La tabla {fuente_datos} no existe en la base de datos.")
                        continue
                except Exception as e:
                    logger.error(f"❌ Error al inspeccionar la base de datos: {e}")
                    continue

                # Consulta optimizada para buscar datos en los últimos 15 minutos
                query = text(f"""
                    SELECT chipid, temperatura, fecha FROM {fuente_datos}
                    WHERE chipid = :chipid
                    AND fecha BETWEEN :hace_15_min AND :now
                    ORDER BY fecha DESC LIMIT 1
                """)

                try:
                    resultado = session.execute(query, {"chipid": dispositivo.chipid, "hace_15_min": hace_15_min,
                                                        "now": now}).fetchone()
                except Exception as e:
                    logger.error(f"❌ Error al ejecutar la consulta en {fuente_datos}: {e}")
                    continue

                if not resultado:
                    logger.warning(
                        f"No hay registros en los últimos 15 minutos para chipid {dispositivo.chipid} en {fuente_datos}.")
                    continue

                chipid, temperatura, fecha = resultado
                if not registro.cultivo:
                    logger.warning(f"⚠️ No se encontró cultivo asociado al registro {registro.id}.")
                    continue

                parametros = session.query(Alerta).filter(
                    Alerta.fk_cultivo == registro.fk_cultivo,
                    Alerta.fk_cultivo_fase == registro.fk_cultivo_fase
                ).first()

                if not parametros:
                    logger.warning(
                        f"❌ No se encontraron parámetros de alerta para {registro.cultivo.nombre} en fase {registro.fk_cultivo_fase}.")
                    continue

                temp_max_critica = parametros.get("T° máxima de crecimiento")

                if temp_max_critica is None:
                    logger.warning(
                        f"⚠️ No hay un valor crítico de temperatura para {registro.cultivo.nombre} en fase {registro.fk_cultivo_fase}.")
                    continue

                # Verificar si la alerta ya fue generada recientemente
                alerta_existente = session.query(Alerta).filter(
                    Alerta.fk_dispositivo == registro.fk_dispositivo,
                    Alerta.fk_cultivo == registro.fk_cultivo,
                    Alerta.fk_cultivo_fase == registro.fk_cultivo_fase,
                    Alerta.fecha_alerta >= hace_15_min
                ).first()

                if alerta_existente:
                    logger.info(
                        f"✅ Alerta ya registrada recientemente para {registro.cultivo.nombre}. No se duplicará.")
                    continue

                if temperatura > temp_max_critica:
                    mensaje_alerta = (
                        f"🔥 ALERTA: La temperatura actual ({temperatura}°C) ha superado el límite crítico "
                        f"({temp_max_critica}°C) para el cultivo {registro.cultivo.nombre} en fase {registro.fk_cultivo_fase}."
                    )

                    # Enviar alerta por correo
                    if registro.usuario and hasattr(registro.usuario, "email"):
                        alerta_temperatura_eca(registro.usuario.email, registro.cultivo.nombre,
                                               registro.fk_cultivo_fase, temperatura, mensaje_alerta)
                    else:
                        logger.warning(
                            f"⚠️ No se pudo enviar la alerta porque el usuario no tiene un correo registrado.")

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


# Ejecutar la verificación cada vez que el script corra
if __name__ == "__main__":
    verificar_alertas_temperatura()
