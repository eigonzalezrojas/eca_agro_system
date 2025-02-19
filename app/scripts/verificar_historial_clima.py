import os
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask
from sqlalchemy import func
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.extensions import db
from app.models import Registro, Dispositivo, DataP0, HistorialClima, Usuario
from app.config import config_by_name

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()

def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    env_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_by_name[env_name])
    db.init_app(app)
    return app

app = create_app()

def verificar_historial_clima():
    """Genera el historial climático diario de todos los usuarios"""
    logger.info("🔄 Iniciando verificación del historial climático...")

    # Obtener fecha de ayer
    fecha_ayer = datetime.now().date() - timedelta(days=1)

    with app.app_context():
        with db.session() as session:
            registros = session.query(Registro).all()

            for registro in registros:
                usuario = session.get(Usuario, registro.fk_usuario)
                if not usuario:
                    logger.warning(f"Usuario con RUT {registro.fk_usuario} no encontrado.")
                    continue

                dispositivo = session.get(Dispositivo, registro.fk_dispositivo)
                if not dispositivo:
                    logger.warning(f"Dispositivo ID {registro.fk_dispositivo} no encontrado.")
                    continue

                chipid = dispositivo.chipid
                logger.info(f"✅ Procesando historial para usuario {usuario.rut} y chipid {chipid}.")

                # Verificar si ya existe un registro para la fecha
                historial = session.query(HistorialClima).filter_by(rut=usuario.rut, chipid=chipid, fecha=fecha_ayer).first()

                if not historial:
                    # Calcular temperatura máxima y mínima del día anterior
                    temp_max = session.query(func.max(DataP0.temperatura)).filter(
                        DataP0.chipid == chipid,
                        DataP0.fecha.between(fecha_ayer, fecha_ayer + timedelta(days=1))
                    ).scalar()

                    temp_min = session.query(func.min(DataP0.temperatura)).filter(
                        DataP0.chipid == chipid,
                        DataP0.fecha.between(fecha_ayer, fecha_ayer + timedelta(days=1))
                    ).scalar()

                    # Calcular horas frío
                    horas_frio = session.query(func.count(DataP0.id)).filter(
                        DataP0.chipid == chipid,
                        DataP0.fecha.between(fecha_ayer, fecha_ayer + timedelta(days=1)),
                        DataP0.temperatura >= 0,
                        DataP0.temperatura <= 7.2
                    ).scalar()

                    # Calcular GDA si Temp Max y Temp Min existen
                    gda = max(((temp_max + temp_min) / 2) - 10, 0) if temp_max and temp_min else 0

                    # Guardar en HistorialClima
                    if temp_max and temp_min:
                        nuevo_registro = HistorialClima(
                            rut=usuario.rut,
                            chipid=chipid,
                            fecha=fecha_ayer,
                            temp_max=temp_max,
                            temp_min=temp_min,
                            horas_frio=horas_frio,
                            gda=gda
                        )
                        session.add(nuevo_registro)
                        session.commit()
                        logger.info(f"✅ Historial registrado para {usuario.rut} - ChipID {chipid}: {fecha_ayer}")
                    else:
                        logger.warning(f"⚠️ No hay datos de temperatura para {usuario.rut} - ChipID {chipid} el {fecha_ayer}")
                else:
                    logger.info(f"ℹ️ El historial ya existe para {usuario.rut} - ChipID {chipid} el {fecha_ayer}")

    logger.info("✅ Proceso de verificación de historial climático finalizado.")

if __name__ == "__main__":
    verificar_historial_clima()
