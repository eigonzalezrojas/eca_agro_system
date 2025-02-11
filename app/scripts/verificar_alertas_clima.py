import os
import sys
import requests
import logging
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app import create_app
from app.extensions import db
from app.models import Usuario, Parcela
from app.services.email_service import enviar_correo_alerta

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()

# API Key de WeatherAPI
API_KEY = os.getenv('WEATHERAPI_KEY')

# Crear la aplicación Flask
app = create_app()


# Función para traducir texto al español (usando MyMemory API)
def traducir_texto(texto):
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {"q": texto, "langpair": "en|es"}
        response = requests.get(url, params=params)
        data = response.json()
        return data["responseData"]["translatedText"]
    except Exception as e:
        logger.error(f"Error al traducir texto: {e}")
        return texto  # Si falla la traducción, se envía en inglés


# Función principal para verificar alertas climáticas
def verificar_alertas_clima():
    """Consulta la API del clima para obtener alertas y enviarlas a los clientes"""

    with app.app_context():
        usuarios = db.session.query(Usuario).all()

        for usuario in usuarios:
            parcelas = db.session.query(Parcela).filter_by(fk_usuario=usuario.rut).all()
            for parcela in parcelas:
                ubicacion = f"{parcela.comuna}, Chile"

                # Consultamos la API de clima con alertas
                url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={ubicacion}&days=1&alerts=yes"
                response = requests.get(url)

                if response.status_code != 200:
                    logger.warning(f"No se pudo obtener el clima para {ubicacion}.")
                    continue

                data = response.json()

                # Verificar si hay alertas
                if "alerts" in data and "alert" in data["alerts"]:
                    for alerta in data["alerts"]["alert"]:
                        titulo = traducir_texto(alerta["headline"])
                        descripcion = traducir_texto(alerta["desc"])
                        instrucciones = traducir_texto(alerta["instruction"])

                        # Enviar alerta por correo
                        enviar_correo_alerta(usuario.correo, titulo, descripcion, instrucciones)
                        logger.info(f"📩 Alerta enviada a {usuario.correo}: {titulo}")

        logger.info("✅ Verificación de alertas climáticas completada.")


# Ejecutar el script
if __name__ == "__main__":
    verificar_alertas_clima()
