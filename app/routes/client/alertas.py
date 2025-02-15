from flask import Blueprint, render_template, session, jsonify
from app.models import Registro, Alerta, Cultivo, Usuario
from app.extensions import db

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


@alertasCliente.route('/notificaciones', methods=['GET'])
def obtener_notificaciones():
    """Obtiene las últimas alertas NO LEÍDAS como notificaciones para el cliente"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    usuario = Usuario.query.filter_by(rut=user_id).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    registros = Registro.query.filter_by(fk_usuario=user_id).all()
    dispositivos_usuario = [registro.fk_dispositivo for registro in registros]

    if not dispositivos_usuario:
        return jsonify([])  # No tiene dispositivos registrados

    # Obtener alertas no leídas
    alertas = (
        Alerta.query
        .filter(Alerta.fk_dispositivo.in_(dispositivos_usuario), Alerta.leida == False)
        .order_by(Alerta.fecha_alerta.desc())
        .limit(5)
        .all()
    )

    alertas_notificaciones = [
        {
            "id": alerta.id,
            "mensaje": alerta.mensaje[:50] + "..." if len(alerta.mensaje) > 50 else alerta.mensaje,
            "fecha": alerta.fecha_alerta.strftime("%d-%m-%Y %H:%M"),
        }
        for alerta in alertas
    ]

    return jsonify(alertas_notificaciones)


@alertasCliente.route('/marcar_leida/<int:id>', methods=['POST'])
def marcar_alerta_leida(id):
    """Marca una alerta como leída para que no aparezca en notificaciones."""
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    alerta = Alerta.query.get(id)

    if not alerta:
        return jsonify({"error": "Alerta no encontrada"}), 404

    # Marcar la alerta como leída
    alerta.leida = True
    db.session.commit()

    return jsonify({"success": True, "message": "Alerta marcada como leída"})

