import os
import logging
import sys
from datetime import datetime, timedelta
from flask import Flask
from sqlalchemy import func, exc
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.extensions import db
from app.models import HistorialClima, DataNodoAmbiente
from app.config import config_by_name

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

def create_app():
    app = Flask(__name__)
    env_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_by_name[env_name])
    db.init_app(app)
    return app

app = create_app()

def obtener_hora_registro(session, chipid, fecha, orden):
    registro = session.query(DataNodoAmbiente.fecha).filter(
        DataNodoAmbiente.chipid == chipid,
        func.date(DataNodoAmbiente.fecha) == fecha
    ).order_by(orden(DataNodoAmbiente.temperatura)).first()
    return registro.fecha.strftime("%H:%M:%S") if registro else "N/A"

def procesar_fecha(session, chipid, fecha):
    registro_existente = session.query(HistorialClima).filter_by(
        chipid=chipid, fecha=fecha
    ).first()

    temp_max = session.query(func.max(DataNodoAmbiente.temperatura)).filter(
        DataNodoAmbiente.chipid == chipid,
        func.date(DataNodoAmbiente.fecha) == fecha
    ).scalar()

    temp_min = session.query(func.min(DataNodoAmbiente.temperatura)).filter(
        DataNodoAmbiente.chipid == chipid,
        func.date(DataNodoAmbiente.fecha) == fecha
    ).scalar()

    hum_max = session.query(func.max(DataNodoAmbiente.humedad)).filter(
        DataNodoAmbiente.chipid == chipid,
        func.date(DataNodoAmbiente.fecha) == fecha
    ).scalar()

    hum_min = session.query(func.min(DataNodoAmbiente.humedad)).filter(
        DataNodoAmbiente.chipid == chipid,
        func.date(DataNodoAmbiente.fecha) == fecha
    ).scalar()

    horas_frio = session.query(DataNodoAmbiente).filter(
        DataNodoAmbiente.chipid == chipid,
        func.date(DataNodoAmbiente.fecha) == fecha,
        DataNodoAmbiente.temperatura >= 0,
        DataNodoAmbiente.temperatura <= 7.2
    ).count()

    historial_anterior = session.query(HistorialClima).filter(
        HistorialClima.chipid == chipid,
        HistorialClima.fecha < fecha
    ).order_by(HistorialClima.fecha.desc()).first()

    gda_acumulado_anterior = historial_anterior.gda if historial_anterior else 0
    gda_diario = max(((temp_max + temp_min) / 2) - 10, 0) if temp_max and temp_min else 0
    gda = round(gda_acumulado_anterior + gda_diario, 3)

    logger.info(f"📌 ChipID: {chipid} | Fecha: {fecha} | TempMax: {temp_max} | TempMin: {temp_min} | HumMax: {hum_max} | HumMin: {hum_min} | HorasFrío: {horas_frio} | GDA: {gda}")

    if temp_max is None or temp_min is None:
        logger.warning(f"⚠️ Datos insuficientes para ChipID {chipid} en {fecha}. Se omite.")
        return

    try:
        if registro_existente:
            registro_existente.temp_max = temp_max
            registro_existente.temp_min = temp_min
            registro_existente.horas_frio = horas_frio
            registro_existente.gda = gda
            logger.info(f"✅ Registro actualizado para ChipID {chipid} en {fecha}.")
        else:
            nuevo_registro = HistorialClima(
                chipid=chipid,
                fecha=fecha,
                temp_max=temp_max,
                temp_min=temp_min,
                horas_frio=horas_frio,
                gda=gda
            )
            session.add(nuevo_registro)
            logger.info(f"✅ Nuevo registro insertado para ChipID {chipid} en {fecha}.")

        session.commit()
    except exc.SQLAlchemyError as e:
        session.rollback()
        logger.error(f"❌ Error al insertar/actualizar datos para ChipID {chipid}: {e}")

def calcular_hf_gda():
    now = datetime.now()
    fecha_ayer = now.date() - timedelta(days=1)
    fecha_hoy = now.date()

    with app.app_context():
        with db.session() as session:
            dispositivos = session.query(DataNodoAmbiente.chipid).distinct().all()

            for dispositivo in dispositivos:
                chipid = dispositivo[0]
                logger.info(f"\n🔍 Procesando ChipID: {chipid}")

                procesar_fecha(session, chipid, fecha_ayer)

                existe_ayer = session.query(HistorialClima).filter_by(
                    chipid=chipid, fecha=fecha_ayer
                ).first()

                if not existe_ayer:
                    logger.warning(f"⚠️ Falta registro del {fecha_ayer} para ChipID {chipid}. Intentando generar el de hoy ({fecha_hoy})")
                    procesar_fecha(session, chipid, fecha_hoy)

    logger.info("✅ Cálculo de GDA y Horas Frío finalizado.")

if __name__ == "__main__":
    calcular_hf_gda()