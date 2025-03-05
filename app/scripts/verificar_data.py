import os
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask
from sqlalchemy import text
from dotenv import load_dotenv

# Agregar la ruta correcta para importar desde la app Flask
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(BASE_DIR)

from app.extensions import db
from app.models import Registro, Dispositivo, Alerta, Usuario, Fase, Parcela
from app.services.email_service import enviar_alerta_cliente, enviar_alerta_dispositivo_admin  # 🔹 Importamos las nuevas funciones
from app.config import config_by_name

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()

# Inicializar Flask y configurar la base de datos
app = Flask(__name__)
app.config.from_object(config_by_name[os.getenv("FLASK_ENV", "default")])
db.init_app(app)


def revisar_dispositivos():
    """
    Verifica si los dispositivos están enviando datos.
    """
    with app.app_context():
        logger.info("Iniciando revisión de dispositivos...")

        # Obtener la lista de dispositivos en la tabla Registro
        registros = db.session.query(Registro).all()
        tiempo_limite = datetime.now() - timedelta(minutes=10)
        dispositivos_alertados = set()  # Para evitar alertas duplicadas al administrador

        for registro in registros:
            dispositivo = db.session.query(Dispositivo).filter_by(id=registro.fk_dispositivo).first()

            if not dispositivo:
                continue

            chipid = dispositivo.chipid
            logger.info(f"Revisando dispositivo {chipid}...")

            # 🔹 Ejecutar consulta SQL correctamente con text()
            query_tabla = text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name LIKE 'data%'")
            tablas = db.session.execute(query_tabla).fetchall()
            tablas = [tabla[0] for tabla in tablas]

            ultima_fecha = None

            for tabla in tablas:
                query = text(f"SELECT fecha FROM {tabla} WHERE chipid = :chipid ORDER BY fecha DESC LIMIT 1")
                resultado = db.session.execute(query, {"chipid": chipid}).fetchone()

                if resultado:
                    fecha_registro = resultado[0]
                    if not ultima_fecha or fecha_registro > ultima_fecha:
                        ultima_fecha = fecha_registro

            if not ultima_fecha or ultima_fecha < tiempo_limite:
                logger.warning(f"Dispositivo {chipid} no ha enviado datos desde {ultima_fecha}")

                usuario = db.session.query(Usuario).filter_by(rut=registro.fk_usuario).first()
                parcela = db.session.query(Parcela).filter_by(id=registro.fk_parcela).first()
                fase = db.session.query(Fase).filter_by(id=registro.fk_fase).first()

                cliente = f"{usuario.nombre} {usuario.apellido}" if usuario else "Desconocido"
                cultivo = fase.cultivo if fase else "Desconocido"
                nombre_parcela = parcela.nombre if parcela else f"ID {registro.fk_parcela}"

                # Enviar alerta al cliente
                if usuario and usuario.correo:
                    enviar_alerta_cliente(usuario.correo, chipid, nombre_parcela, cultivo, ultima_fecha)

                # Enviar alerta única al administrador
                if chipid not in dispositivos_alertados:
                    enviar_alerta_dispositivo_admin(chipid, ultima_fecha)
                    dispositivos_alertados.add(chipid)

                # Registrar la alerta en la base de datos
                nueva_alerta = Alerta(
                    mensaje=f"El dispositivo {chipid} dejó de enviar datos desde {ultima_fecha}",
                    fk_dispositivo=dispositivo.id,
                    fk_fase=registro.fk_fase,
                    cultivo_nombre=cultivo,
                    nivel_alerta="Crítica"
                )
                db.session.add(nueva_alerta)
                db.session.commit()

        logger.info("✅ Revisión de dispositivos completada.")


if __name__ == "__main__":
    revisar_dispositivos()
