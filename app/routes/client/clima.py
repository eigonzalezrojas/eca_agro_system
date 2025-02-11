from flask import Blueprint, jsonify, session, render_template, request
from app.models import Registro, Parcela, Usuario
import os
import requests

clima = Blueprint('clima', __name__)


@clima.route('/')
def mostrar_clima():
    """ Renderiza la plantilla de clima """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401
    usuario = Usuario.query.filter_by(rut=user_id).first()
    return render_template('sections/cliente/clima.html', usuario=usuario)


@clima.route('/parcelas', methods=['GET'])
def obtener_parcelas():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    # Obtener todas las parcelas del usuario
    parcelas = Parcela.query.join(Registro, Parcela.id == Registro.fk_parcela).filter(Registro.fk_usuario == user_id).all()

    if not parcelas:
        return jsonify({"error": "No hay parcelas asociadas al usuario"}), 404

    parcelas_data = [{"id": parcela.id, "nombre": parcela.nombre} for parcela in parcelas]

    return jsonify({"parcelas": parcelas_data})


@clima.route('/obtener-clima', methods=['GET'])
def obtener_clima_parcela():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    usuario = Usuario.query.filter_by(rut=user_id).first()

    parcela_id = request.args.get("parcela_id")
    if not parcela_id:
        return jsonify({"error": "Debe seleccionar una parcela"}), 400

    parcela = Parcela.query.get(parcela_id)
    if not parcela:
        return jsonify({"error": "No se encontró la parcela seleccionada"}), 404

    api_key = os.getenv('WEATHERAPI_KEY')
    if not api_key:
        return jsonify({"error": "No se encontró la API Key en el entorno"}), 500

    ubicacion = f"{parcela.comuna}, Chile"

    # Consultar API del clima
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={ubicacion}&days=5"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Error al obtener los datos del clima"}), response.status_code

    data = response.json()
    clima_actual = {
        "ubicacion": f"{data['location']['name']}, {data['location']['region']}, Chile",
        "descripcion": data["current"]["condition"]["text"],
        "temp_actual": data["current"]["temp_c"],
        "humedad": data["current"]["humidity"],
        "viento": data["current"]["wind_kph"],
        "codigo_clima": data["current"]["condition"]["code"],
    }

    pronostico = [
        {
            "fecha": dia["date"],
            "temp_max": dia["day"]["maxtemp_c"],
            "temp_min": dia["day"]["mintemp_c"],
            "descripcion": dia["day"]["condition"]["text"],
            "codigo_clima": dia["day"]["condition"]["code"]
        }
        for dia in data["forecast"]["forecastday"]
    ]


    return jsonify({
        "clima_actual": clima_actual,
        "pronostico": pronostico
    })



