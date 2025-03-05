import os
import logging
import sys
from datetime import datetime, timedelta
from flask import Flask
from sqlalchemy import func, exc
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.extensions import db
from app.models import HistorialClima, DataP0
from app.config import config_by_name

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    env_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_by_name[env_name])
    db.init_app(app)
    return app


app = create_app()


def calcular_hf_gda():
    """Calcula y almacena GDA y Horas Frío para el día anterior en HistorialClima."""
    now = datetime.now()
    fecha_ayer = now.date() - timedelta(days=1)

    with app.app_context():
        with db.session() as session:
            dispositivos = session.query(DataP0.chipid).distinct().all()

            for dispositivo in dispositivos:
                chipid = dispositivo[0]

                # Verificar si ya existe un registro para este chipid y fecha
                registro_existente = session.query(HistorialClima).filter_by(
                    chipid=chipid, fecha=fecha_ayer
                ).first()

                if registro_existente:
                    logger.info(f"ℹ️ Registro ya existente para ChipID {chipid} en {fecha_ayer}. Se omite.")
                    continue

                # Obtener Temp Max y Min del día anterior
                temp_max = session.query(func.max(DataP0.temperatura)).filter(
                    DataP0.chipid == chipid,
                    DataP0.fecha == fecha_ayer
                ).scalar()

                temp_min = session.query(func.min(DataP0.temperatura)).filter(
                    DataP0.chipid == chipid,
                    DataP0.fecha == fecha_ayer
                ).scalar()

                # Calcular Horas Frío
                horas_frio = session.query(DataP0).filter(
                    DataP0.chipid == chipid,
                    DataP0.fecha == fecha_ayer,
                    DataP0.temperatura >= 0,
                    DataP0.temperatura <= 7.2
                ).count()

                # Obtener GDA acumulado del día anterior
                historial_anterior = session.query(HistorialClima).filter(
                    HistorialClima.chipid == chipid,
                    HistorialClima.fecha == fecha_ayer - timedelta(days=1)
                ).first()
                gda_acumulado_anterior = historial_anterior.gda if historial_anterior else 0

                # Calcular GDA diario
                gda_diario = max(((temp_max + temp_min) / 2) - 10, 0) if temp_max and temp_min else 0
                gda = gda_acumulado_anterior + gda_diario

                # Verificar valores antes de insertar
                logger.info(
                    f"📌 ChipID: {chipid} | Fecha: {fecha_ayer} | TempMax: {temp_max} | TempMin: {temp_min} | HorasFrío: {horas_frio} | GDA: {gda}")

                if temp_max is None or temp_min is None:
                    logger.warning(f"⚠️ Datos insuficientes para ChipID {chipid} en {fecha_ayer}. Se omite.")
                    continue

                try:
                    nuevo_registro = HistorialClima(
                        chipid=chipid,
                        fecha=fecha_ayer,
                        temp_max=temp_max,
                        temp_min=temp_min,
                        horas_frio=horas_frio,
                        gda=gda
                    )
                    session.add(nuevo_registro)
                    session.commit()
                    logger.info(
                        f"✅ Datos guardados para ChipID {chipid}: TempMax {temp_max}, TempMin {temp_min}, HorasFrío {horas_frio}, GDA {gda}")
                except exc.SQLAlchemyError as e:
                    session.rollback()
                    logger.error(f"❌ Error al insertar datos en la base de datos para ChipID {chipid}: {e}")

    logger.info("✅ Cálculo de GDA y Horas Frío completado.")


if __name__ == "__main__":
    calcular_hf_gda()
