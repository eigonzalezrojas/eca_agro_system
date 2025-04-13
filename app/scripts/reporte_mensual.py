import datetime
import pandas as pd
import os
import logging
import sys
from flask import Flask
from sqlalchemy import func, and_
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(BASE_DIR)

from app.extensions import db
from app.models import Registro, DataNodoAmbiente, HistorialClima, Usuario, Dispositivo, Parcela
from app.services.email_service import enviar_reporte_mensual
from app.config import config_by_name

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
app.config.from_object(config_by_name[os.getenv("FLASK_ENV", "default")])
db.init_app(app)

ruta_excel = os.path.join(os.path.dirname(__file__), "../data/tabla_alertas.xlsx")

def obtener_umbral_para_cultivo_fase(df_umbrales, cultivo, fase):
    filtro = df_umbrales[(df_umbrales['Cultivo'].str.lower() == cultivo.lower())
                         & (df_umbrales['Fase'].str.lower() == fase.lower())]
    if filtro.empty:
        return None
    return {
        'temp_critica_min': filtro['Temperatura crítica mínima'].values[0],
        'temp_critica_max': filtro['Temperatura máxima de crecimiento'].values[0],
        'humedad_min': filtro['HR MIN'].values[0],
        'humedad_max': filtro['HR MAX'].values[0]
    }

def calcular_porcentajes_condiciones(session, chipid, fecha_inicio, fecha_fin, umbrales):
    registros = session.query(DataNodoAmbiente).filter(
        and_(
            DataNodoAmbiente.fecha >= fecha_inicio,
            DataNodoAmbiente.fecha <= fecha_fin,
            DataNodoAmbiente.chipid == chipid
        )
    ).all()

    total_registros = len(registros)
    if total_registros == 0:
        return {'Porcentaje Óptimo': 0}

    registros_sobre_max = sum(1 for r in registros if r.temperatura > umbrales['temp_critica_max'])
    registros_bajo_min = sum(1 for r in registros if r.temperatura < umbrales['temp_critica_min'])
    registros_sobre_hum_max = sum(1 for r in registros if r.humedad > umbrales['humedad_max'])
    registros_bajo_hum_min = sum(1 for r in registros if r.humedad < umbrales['humedad_min'])

    registros_optimos = total_registros - (registros_sobre_max + registros_bajo_min + registros_sobre_hum_max + registros_bajo_hum_min)

    return {
        'Porcentaje Óptimo': round((registros_optimos / total_registros) * 100, 1)
    }

def calcular_reporte_mensual(session, df_umbrales, fecha_inicio, fecha_fin):
    registros = session.query(Registro).all()
    reportes = []

    for registro in registros:
        dispositivo = session.query(Dispositivo).filter_by(id=registro.fk_dispositivo).first()
        if not dispositivo:
            continue

        umbrales = obtener_umbral_para_cultivo_fase(df_umbrales, registro.cultivo_nombre, registro.fase_nombre)
        if not umbrales:
            continue

        clima = session.query(
            func.max(DataNodoAmbiente.temperatura).label('temp_max'),
            func.min(DataNodoAmbiente.temperatura).label('temp_min'),
            func.max(DataNodoAmbiente.humedad).label('hum_max'),
            func.min(DataNodoAmbiente.humedad).label('hum_min')
        ).filter(
            DataNodoAmbiente.chipid == dispositivo.chipid,
            DataNodoAmbiente.fecha.between(fecha_inicio, fecha_fin)
        ).first()

        datos = calcular_porcentajes_condiciones(session, dispositivo.chipid, fecha_inicio, fecha_fin, umbrales)

        reporte = {
            'Fecha': f"{fecha_inicio} a {fecha_fin}",
            'Temperatura Máxima': clima.temp_max or "N/A",
            'Temperatura Mínima': clima.temp_min or "N/A",
            'Humedad Máxima': clima.hum_max or "N/A",
            'Humedad Mínima': clima.hum_min or "N/A",
            'Porcentaje Óptimo': datos['Porcentaje Óptimo'],
            'Parcela': registro.parcela.nombre,
            'Cliente': registro.usuario.nombre,
            'ChipID': dispositivo.chipid
        }
        reportes.append(reporte)

    return reportes


if __name__ == "__main__":
    with app.app_context():
        session = db.session
        hoy = datetime.date.today()
        primer_dia_mes_actual = hoy.replace(day=1)
        fecha_inicio = primer_dia_mes_actual - datetime.timedelta(days=primer_dia_mes_actual.day)
        fecha_fin = primer_dia_mes_actual - datetime.timedelta(days=1)

        df_umbrales = pd.read_excel(ruta_excel)

        reportes = calcular_reporte_mensual(session, df_umbrales, fecha_inicio, fecha_fin)

        for reporte in reportes:
            usuario = session.query(Usuario).filter_by(nombre=reporte['Cliente']).first()
            if usuario and usuario.correo:
                enviar_reporte_mensual(usuario.correo, reporte['Parcela'], reporte['Cliente'], reporte)
                logger.info(f"📤 Enviado reporte mensual a {usuario.correo}")

        session.close()