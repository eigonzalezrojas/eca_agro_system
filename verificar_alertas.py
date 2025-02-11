import os
import pandas as pd
import logging
from sqlalchemy import text, inspect
from dotenv import load_dotenv
from app.extensions import db
from app.models import Registro, Dispositivo, Alerta
from app.services.email_service import alerta_temperatura_eca

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener la ruta del archivo de alertas
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE_PATH = os.path.join(BASE_DIR, "app", "data", "tabla_alertas.xlsx")

# Cargar el archivo Excel con las alertas
df_alertas = pd.read_excel(DATA_FILE_PATH, sheet_name="Hoja1")
df_alertas["Cultivo"].fillna(method="ffill", inplace=True)

def obtener_parametros_alerta(cultivo, fase):
    """Obtener los parámetros de alerta para un cultivo y fase específica."""
    datos = df_alertas[(df_alertas["Cultivo"] == cultivo) & (df_alertas["Fase"] == fase)]
    return datos.iloc[0].to_dict() if not datos.empty else None

def tabla_existe(session, nombre_tabla):
    """Verifica si la tabla existe en la base de datos."""
    inspector = inspect(session.bind)
    return nombre_tabla in inspector.get_table_names()

def verificar_alertas_temperatura():
    """Verifica la temperatura de los dispositivos y almacena alertas en la base de datos."""
    with db.session() as session:
        registros = session.query(Registro).all()

        for registro in registros:
            dispositivo = session.get(Dispositivo, registro.fk_dispositivo)
            if not dispositivo:
                logger.warning(f"Dispositivo {registro.fk_dispositivo} no encontrado.")
                continue

            fuente_datos = registro.fuente  # Nombre de la tabla con la temperatura

            # Validar existencia de la tabla antes de consultar
            if not tabla_existe(session, fuente_datos):
                logger.warning(f"⚠️ La tabla {fuente_datos} no existe en la base de datos.")
                continue

            # Consulta optimizada para buscar la última temperatura del día actual
            query = text(f"""
                SELECT chipid, temperatura, fecha FROM {fuente_datos}
                WHERE chipid = :chipid
                AND fecha >= CURDATE() AND fecha <= NOW()
                ORDER BY fecha DESC LIMIT 1
            """)

            try:
                resultado = session.execute(query, {"chipid": dispositivo.chipid}).fetchone()
            except Exception as e:
                logger.error(f"❌ Error al ejecutar la consulta: {e}")
                continue

            if not resultado:
                logger.warning(f"No hay registros de hoy para chipid {dispositivo.chipid} en {fuente_datos}.")
                continue

            chipid, temperatura, fecha = resultado
            parametros = obtener_parametros_alerta(registro.fk_cultivo, registro.fk_cultivo_fase)

            if not parametros:
                logger.warning(f"❌ No se encontraron parámetros de alerta para {registro.fk_cultivo} en fase {registro.fk_cultivo_fase}.")
                continue

            temp_max_critica = parametros.get("T° máxima de crecimiento")

            if temp_max_critica is None:
                logger.warning(f"⚠️ No hay un valor crítico de temperatura para {registro.fk_cultivo} en fase {registro.fk_cultivo_fase}.")
                continue

            if temperatura > temp_max_critica:
                mensaje_alerta = (
                    f"🔥 ALERTA: La temperatura actual ({temperatura}°C) ha superado el límite crítico "
                    f"({temp_max_critica}°C) para el cultivo {registro.fk_cultivo} en fase {registro.fk_cultivo_fase}."
                )

                # Enviar alerta por correo
                alerta_temperatura_eca(registro.usuario.email, registro.fk_cultivo, registro.fk_cultivo_fase, temperatura, mensaje_alerta)

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
