import datetime
import pandas as pd
import os
import logging
import sys
from flask import Flask
from sqlalchemy import create_engine, and_, func
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Agregar la ruta correcta para importar desde la app Flask
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(BASE_DIR)

from app.extensions import db
from app.models import Registro, DataP0, HistorialClima, Usuario, Fase, Dispositivo
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

# Cargar datos desde el archivo Excel
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


def calcular_datos_reporte(fecha, session, df_umbrales):
    registros = session.query(Registro).filter_by(fk_usuario="18476159-9").all()
    reportes = []

    for registro in registros:
        logger.info(f"Procesando registro para usuario {registro.fk_usuario}, dispositivo {registro.fk_dispositivo}")

        dispositivo = session.query(Dispositivo).filter_by(id=registro.fk_dispositivo).first()
        if not dispositivo:
            logger.warning(f"No se encontró dispositivo para ID {registro.fk_dispositivo}")
            continue

        logger.info(f"Dispositivo encontrado: ChipID {dispositivo.chipid}")

        clima = session.query(HistorialClima).filter_by(fecha=fecha, chipid=dispositivo.chipid).first()
        if not clima:
            logger.warning(f"No se encontró historial climático para chipid {dispositivo.chipid} en la fecha {fecha}.")
            continue

        umbrales = obtener_umbral_para_cultivo_fase(df_umbrales, registro.cultivo_nombre, registro.fase_nombre)
        if not umbrales:
            logger.warning(
                f"No se encontraron umbrales para el cultivo {registro.cultivo_nombre} en fase {registro.fase_nombre}.")
            continue

        porcentaje_optimo, porcentaje_sobre_max, porcentaje_bajo_min, porcentaje_sobre_humedad_max, porcentaje_bajo_humedad_min, total_registros = calcular_porcentajes_condiciones(
            fecha, session, dispositivo.chipid, umbrales)

        reporte = {
            'Fecha': fecha,
            'Temperatura Máxima': clima.temp_max,
            'Temperatura Mínima': clima.temp_min,
            'Horas Frío': clima.horas_frio,
            'GDA': clima.gda,
            'Porcentaje Óptimo': round(porcentaje_optimo, 1),
            'Porcentaje Sobre Máxima': round(porcentaje_sobre_max, 1),
            'Porcentaje Bajo Mínima': round(porcentaje_bajo_min, 1),
            'Porcentaje Sobre Humedad Máxima': round(porcentaje_sobre_humedad_max, 1),
            'Porcentaje Bajo Humedad Mínima': round(porcentaje_bajo_humedad_min, 1),
            'Total Registros': total_registros,
            'Usuario': registro.fk_usuario,
            'Cultivo': registro.cultivo_nombre,
            'Fase': registro.fase_nombre
        }
        reportes.append(reporte)

    return reportes


def calcular_porcentajes_condiciones(fecha, session, chipid, umbrales):
    total_registros = session.query(DataP0).filter(
        and_(DataP0.fecha.between(f"{fecha} 08:00:00", f"{fecha} 18:00:00"), DataP0.chipid == chipid)
    ).count()

    if total_registros == 0:
        return 0, 0, 0, 0, 0, 0

    registros_sobre_max = session.query(DataP0).filter(
        and_(DataP0.fecha.between(f"{fecha} 08:00:00", f"{fecha} 18:00:00"), DataP0.chipid == chipid,
             DataP0.temperatura > umbrales['temp_critica_max'])
    ).count()

    registros_bajo_min = session.query(DataP0).filter(
        and_(DataP0.fecha.between(f"{fecha} 08:00:00", f"{fecha} 18:00:00"), DataP0.chipid == chipid,
             DataP0.temperatura < umbrales['temp_critica_min'])
    ).count()

    registros_sobre_humedad_max = session.query(DataP0).filter(
        and_(DataP0.fecha.between(f"{fecha} 08:00:00", f"{fecha} 18:00:00"), DataP0.chipid == chipid,
             DataP0.humedad > umbrales['humedad_max'])
    ).count()

    registros_bajo_humedad_min = session.query(DataP0).filter(
        and_(DataP0.fecha.between(f"{fecha} 08:00:00", f"{fecha} 18:00:00"), DataP0.chipid == chipid,
             DataP0.humedad < umbrales['humedad_min'])
    ).count()

    registros_optimos = total_registros - (
                registros_sobre_max + registros_bajo_min + registros_sobre_humedad_max + registros_bajo_humedad_min)

    return [(val / total_registros) * 100 for val in
            [registros_optimos, registros_sobre_max, registros_bajo_min, registros_sobre_humedad_max,
             registros_bajo_humedad_min, total_registros]]


if __name__ == "__main__":
    with app.app_context():
        session = db.session
        fecha_ayer = datetime.date.today() - datetime.timedelta(days=1)
        df_umbrales = pd.read_excel(ruta_excel)
        reportes = calcular_datos_reporte(fecha_ayer, session, df_umbrales)
        for reporte in reportes:
            usuario = session.query(Usuario).filter_by(rut=reporte['Usuario']).first()
            if usuario and usuario.correo:
                enviar_reporte_diario(usuario.correo, reporte['Cultivo'], reporte['Fase'], reporte)
        session.close()
