import datetime
import pandas as pd
import os
import logging
import sys
from flask import Flask
from sqlalchemy import and_, func
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Agregar la ruta correcta para importar desde la app Flask
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(BASE_DIR)

from app.extensions import db
from app.models import Registro, DataP0, HistorialClima, Usuario, Dispositivo, Parcela
from app.services.email_service import enviar_reporte_diario
from app.config import config_by_name

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URI")

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Inicializar Flask y configurar la base de datos
app = Flask(__name__)
app.config.from_object(config_by_name[os.getenv("FLASK_ENV", "default")])
db.init_app(app)

# Ruta del archivo Excel con umbrales
ruta_excel = os.path.join(os.path.dirname(__file__), "../data/tabla_alertas.xlsx")
if not os.path.exists(ruta_excel):
    logger.error(f"El archivo {ruta_excel} no existe.")
    sys.exit(1)


def obtener_umbral_para_cultivo_fase(df_umbrales, cultivo, fase):
    filtro = df_umbrales[(df_umbrales['Cultivo'].str.strip().str.lower() == cultivo.strip().lower()) &
                         (df_umbrales['Fase'].str.strip().str.lower() == fase.strip().lower())]
    if filtro.empty:
        return None
    return {
        'temp_critica_min': filtro['Temperatura crítica mínima'].values[0],
        'temp_critica_max': filtro['Temperatura máxima de crecimiento'].values[0],
        'humedad_min': filtro['HR MIN'].values[0],
        'humedad_max': filtro['HR MAX'].values[0]
    }


def calcular_porcentajes_condiciones(fecha, session, chipid, umbrales):
    registros = session.query(DataP0).filter(
        and_(DataP0.fecha.between(f"{fecha} 08:00:00", f"{fecha} 18:00:00"), DataP0.chipid == chipid)
    ).all()
    total_registros = len(registros)
    if total_registros == 0:
        return {
            'Porcentaje Óptimo': 0,
            'Porcentaje Sobre Máxima': 0,
            'Porcentaje Bajo Mínima': 0,
            'Porcentaje Sobre Humedad Máxima': 0,
            'Porcentaje Bajo Humedad Mínima': 0
        }

    registros_sobre_max = sum(1 for r in registros if r.temperatura and r.temperatura > umbrales['temp_critica_max'])
    registros_bajo_min = sum(1 for r in registros if r.temperatura and r.temperatura < umbrales['temp_critica_min'])
    registros_sobre_humedad_max = sum(1 for r in registros if r.humedad and r.humedad > umbrales['humedad_max'])
    registros_bajo_humedad_min = sum(1 for r in registros if r.humedad and r.humedad < umbrales['humedad_min'])
    registros_optimos = total_registros - (
                registros_sobre_max + registros_bajo_min + registros_sobre_humedad_max + registros_bajo_humedad_min)

    hora_temp_max = max((r.fecha for r in registros if r.temperatura), default=None)
    hora_temp_min = min((r.fecha for r in registros if r.temperatura), default=None)
    hora_hum_max = max((r.fecha for r in registros if r.humedad), default=None)
    hora_hum_min = min((r.fecha for r in registros if r.humedad), default=None)

    return {
        'Porcentaje Óptimo': round((registros_optimos / total_registros) * 100, 1),
        'Porcentaje Sobre Máxima': round((registros_sobre_max / total_registros) * 100, 1),
        'Porcentaje Bajo Mínima': round((registros_bajo_min / total_registros) * 100, 1),
        'Porcentaje Sobre Humedad Máxima': round((registros_sobre_humedad_max / total_registros) * 100, 1),
        'Porcentaje Bajo Humedad Mínima': round((registros_bajo_humedad_min / total_registros) * 100, 1),
        'Hora Temp Máx': hora_temp_max,
        'Hora Temp Mín': hora_temp_min,
        'Hora Hum Máx': hora_hum_max,
        'Hora Hum Mín': hora_hum_min
    }


def calcular_datos_reporte(fecha, session, df_umbrales):
    registros = session.query(Registro).all()
    reportes = []

    for registro in registros:
        logger.info(f"Procesando usuario {registro.fk_usuario}, dispositivo {registro.fk_dispositivo}")
        dispositivo = session.query(Dispositivo).filter_by(id=registro.fk_dispositivo).first()
        if not dispositivo:
            logger.warning(f"Dispositivo no encontrado para ID {registro.fk_dispositivo}")
            continue

        clima = session.query(HistorialClima).filter_by(fecha=fecha, chipid=dispositivo.chipid).first()
        if not clima:
            logger.warning(f"No hay historial climático para chipid {dispositivo.chipid} en {fecha}.")
            continue

        umbrales = obtener_umbral_para_cultivo_fase(df_umbrales, registro.cultivo_nombre, registro.fase_nombre)
        if not umbrales:
            logger.warning(f"No hay umbrales para cultivo {registro.cultivo_nombre}, fase {registro.fase_nombre}")
            continue

        datos_reporte = calcular_porcentajes_condiciones(fecha, session, dispositivo.chipid, umbrales)

        reporte = {
            'Fecha': fecha,
            'Temperatura Máxima': clima.temp_max,
            'Temperatura Mínima': clima.temp_min,
            'Horas Frío': clima.horas_frio,
            'GDA': clima.gda,
            'Parcela': registro.parcela.nombre if registro.parcela else 'No asignada',
            'Cliente': registro.usuario.nombre if registro.usuario else 'No registrado',
            'ChipID': dispositivo.chipid,
            **datos_reporte
        }
        reportes.append(reporte)

    return reportes


if __name__ == "__main__":
    with app.app_context():
        session = db.session
        fecha_ayer = datetime.date.today() - datetime.timedelta(days=1)
        df_umbrales = pd.read_excel(ruta_excel)
        reportes = calcular_datos_reporte(fecha_ayer, session, df_umbrales)

        for reporte in reportes:
            usuario = session.query(Usuario).filter_by(nombre=reporte['Cliente']).first()
            if usuario and usuario.correo:
                try:
                    # Enviar correo
                    enviar_reporte_diario(usuario.correo, reporte['Parcela'], reporte['Cliente'], reporte)

                    # Enviar WhatsApp si hay número
                    if usuario.fono:
                        from app.services.whatssap_service import enviar_whatsapp
                        mensaje = f"""📊 Reporte Diario - {reporte['Parcela']}
                        Cliente: {reporte['Cliente']}
                        🌡️ Temp. Máx: {reporte['Temperatura Máxima']}°C
                        ❄️ Temp. Mín: {reporte['Temperatura Mínima']}°C
                        ✅ Óptimo: {reporte['Porcentaje Óptimo']}%"""

                        enviar_whatsapp(usuario.fono, mensaje)

                    logger.info(f"Correo (y WhatsApp) enviado a: {usuario.correo}")
                except Exception as e:
                    logger.error(f"Error enviando notificaciones a {usuario.correo}: {e}")
        session.close()

