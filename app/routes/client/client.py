from flask import Blueprint, jsonify, session, render_template
from app.models import Usuario, Parcela, Fase, Registro, Dispositivo

client = Blueprint('client', __name__)

@client.route('/inicio')
def inicio():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    # Obtener el usuario
    usuario = Usuario.query.filter_by(rut=user_id).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Obtener las parcelas asociadas al usuario
    parcelas = (
        Registro.query
        .filter_by(fk_usuario=user_id)
        .join(Parcela, Registro.fk_parcela == Parcela.id)
        .add_columns(Parcela.id, Parcela.nombre)
        .distinct()
        .all()
    )

    # Obtener los cultivos asociados al usuario a través de la tabla Fase
    cultivos = (
        Registro.query
        .filter_by(fk_usuario=user_id)
        .join(Fase, Registro.fk_fase == Fase.id)
        .add_columns(Fase.cultivo)
        .distinct()
        .all()
    )

    # Obtener los dispositivos asociados al usuario
    dispositivos = (
        Registro.query
        .filter_by(fk_usuario=user_id)
        .join(Dispositivo, Registro.fk_dispositivo == Dispositivo.id)
        .add_columns(Dispositivo.id, Dispositivo.chipid)
        .distinct()
        .all()
    )

    return render_template(
        'sections/cliente/inicio.html',
        usuario=usuario,
        parcelas=[{"id": p.id, "nombre": p.nombre} for p in parcelas],
        cultivos=[{"nombre": c.cultivo} for c in cultivos],  # Ahora solo devuelve el nombre del cultivo
        dispositivos=[{"id": d.id, "chipid": d.chipid} for d in dispositivos]
    )
