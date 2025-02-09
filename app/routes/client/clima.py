import requests
from flask import Blueprint, jsonify, session, render_template
from app.models import Registro, Parcela, Usuario
import os

clima = Blueprint('clima', __name__)


@clima.route('/')
def mostrar_clima():
    """ Renderiza la plantilla de clima """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401
    usuario = Usuario.query.filter_by(rut=user_id).first()
    return render_template('sections/cliente/clima.html', usuario=usuario)


@clima.route('/obtener', methods=['GET'])
def obtener_clima():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    registro = Registro.query.filter_by(fk_usuario=user_id).first()
    if not registro:
        return jsonify({"error": "No se encontró un registro asociado al usuario"}), 404

    parcela = Parcela.query.get(registro.fk_parcela)
    if not parcela:
        return jsonify({"error": "No se encontró la parcela asociada"}), 404

    api_key = os.getenv('WEATHERAPI_KEY')
    if not api_key:
        return jsonify({"error": "No se encontró la API Key en el entorno"}), 500

    ubicacion = f"{parcela.comuna}, Chile"

    # ✅ Consultamos el clima actual y el pronóstico de 5 días
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={ubicacion}&days=5&aqi=no&alerts=no"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Error al obtener los datos del clima"}), response.status_code

    data = response.json()

    # 🔹 Extraer información del clima actual
    clima_actual = {
        "ubicacion": f"{data['location']['name']}, {data['location']['region']}, Chile",
        "descripcion": data["current"]["condition"]["text"],
        "temp_actual": data["current"]["temp_c"],
        "humedad": data["current"]["humidity"],
        "viento": data["current"]["wind_kph"],
        "codigo_clima": data["current"]["condition"]["code"],
    }

    # 🔹 Extraer pronóstico para los próximos 5 días
    pronostico = []
    for dia in data["forecast"]["forecastday"]:
        pronostico.append({
            "fecha": dia["date"],
            "temp_max": dia["day"]["maxtemp_c"],
            "temp_min": dia["day"]["mintemp_c"],
            "descripcion": dia["day"]["condition"]["text"],
            "codigo_clima": dia["day"]["condition"]["code"]
        })

    return jsonify({
        "clima_actual": clima_actual,
        "pronostico": pronostico
    })
