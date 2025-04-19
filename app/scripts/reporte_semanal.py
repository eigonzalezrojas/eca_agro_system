import os
import sys
import logging
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask
from sqlalchemy import func, and_

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.extensions import db
from app.models import Registro, Dispositivo, DataNodoAmbiente, HistorialClima, Usuario
from app.services.email_service import enviar_reporte_semanal
from app.services.whatssap_service import enviar_whatsapp
from app.config import config_by_name

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración Flask
app = Flask(__name__)
app.config.from_object(config_by_name[os.getenv('FLASK_ENV', 'default')])
db.init_app(app)

# Ruta archivo excel
ruta_excel = os.path.join(os.path.dirname(__file__), '../data/tabla_alertas.xlsx')
df_umbrales = pd.read_excel(ruta_excel)


def obtener_umbrales(cultivo, fase):
    filtro = df_umbrales[(df_umbrales['Cultivo'].str.lower() == cultivo.lower()) &
                         (df_umbrales['Fase'].str.lower() == fase.lower())]
    if filtro.empty:
        return None
    return {
        'temp_critica_min': filtro['Temperatura crítica mínima'].values[0],
        'temp_critica_max': filtro['Temperatura máxima de crecimiento'].values[0],
        'humedad_min': filtro['HR MIN'].values[0],
        'humedad_max': filtro['HR MAX'].values[0]
    }


def calcular_datos_semanales(session, chipid, fecha_inicio, fecha_fin, umbrales):
    registros = session.query(DataNodoAmbiente).filter(
        DataNodoAmbiente.chipid == chipid,
        DataNodoAmbiente.fecha.between(fecha_inicio, fecha_fin)
    ).all()

    total = len(registros)
    if total == 0:
        return None

    temp_max = max(r.temperatura for r in registros)
    temp_min = min(r.temperatura for r in registros)
    hum_max = max(r.humedad for r in registros)
    hum_min = min(r.humedad for r in registros)

    registros_optimos = sum(1 for r in registros if (
            umbrales['temp_critica_min'] <= r.temperatura <= umbrales['temp_critica_max'] and
            umbrales['humedad_min'] <= r.humedad <= umbrales['humedad_max']
    ))

    porcentaje_optimo = round((registros_optimos / total) * 100, 2)

    return {
        'temp_max': temp_max,
        'temp_min': temp_min,
        'hum_max': hum_max,
        'hum_min': hum_min,
        'porcentaje_optimo': porcentaje_optimo
    }


if __name__ == '__main__':
    with app.app_context():
        session = db.session

        hoy = datetime.now().date()
        fecha_fin = hoy - timedelta(days=1)  # Domingo
        fecha_inicio = fecha_fin - timedelta(days=6)  # Lunes anterior

        registros = session.query(Registro).all()

        for reg in registros:
            dispositivo = session.query(Dispositivo).filter_by(id=reg.fk_dispositivo).first()
            if not dispositivo:
                continue

            umbrales = obtener_umbrales(reg.cultivo_nombre, reg.fase_nombre)
            if not umbrales:
                continue

            datos = calcular_datos_semanales(session, dispositivo.chipid, fecha_inicio, fecha_fin, umbrales)
            if not datos:
                continue

            reporte = {
                'Fecha Inicio': fecha_inicio,
                'Fecha Fin': fecha_fin,
                'Parcela': reg.parcela.nombre,
                'Cliente': reg.usuario.nombre,
                'ChipID': dispositivo.chipid,
                **datos
            }

            # Enviar Correo
            if reg.usuario.correo:
                enviar_reporte_semanal(reg.usuario.correo, reg.cultivo_nombre, reg.fase_nombre, reporte)

            # Enviar WhatsApp

        session.close()
        logger.info("Reporte semanal generado correctamente.")