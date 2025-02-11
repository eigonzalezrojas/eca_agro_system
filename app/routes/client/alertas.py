from flask import Blueprint, render_template, session, jsonify
from app.models import Registro, Alerta, Cultivo, Usuario

alertasCliente = Blueprint('alertasCliente', __name__)

@alertasCliente.route('/listar', methods=['GET'])
def listar_alertas():
    """Obtiene las alertas asociadas al usuario autenticado."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    usuario = Usuario.query.filter_by(rut=user_id).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Obtener registros del usuario autenticado
    registros = Registro.query.filter_by(fk_usuario=user_id).all()
    alertas_data = []

    for registro in registros:
        alertas = Alerta.query.filter_by(fk_dispositivo=registro.fk_dispositivo).order_by(Alerta.fecha_alerta.desc()).all()
        for alerta in alertas:
            cultivo = Cultivo.query.get(alerta.fk_cultivo)
            alertas_data.append({
                "id": alerta.id,
                "cultivo": cultivo.nombre if cultivo else "Desconocido",
                "fase": alerta.fk_cultivo_fase,
                "fecha": alerta.fecha_alerta.strftime("%d-%m-%Y %H:%M"),
                "mensaje": alerta.mensaje,
                "nivel": alerta.nivel_alerta
            })

    return render_template('sections/cliente/alertas.html', usuario=usuario, alertas=alertas_data)
