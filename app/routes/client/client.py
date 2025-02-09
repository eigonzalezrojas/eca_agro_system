from flask import Blueprint, jsonify, session, render_template
from app.models import Usuario, Parcela, Cultivo, Registro, Dispositivo

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
    parcelas = Registro.query.filter_by(fk_usuario=user_id).join(Parcela, Registro.fk_parcela == Parcela.id).add_columns(Parcela.id, Parcela.nombre).distinct().all()

    # Obtener los cultivos asociados al usuario
    cultivos = Registro.query.filter_by(fk_usuario=user_id).join(Cultivo, Registro.fk_cultivo == Cultivo.id).add_columns(Cultivo.id, Cultivo.nombre).distinct().all()

    # Obtener los dispositivos asociados al usuario
    dispositivos = Registro.query.filter_by(fk_usuario=user_id).join(Dispositivo, Registro.fk_dispositivo == Dispositivo.id).add_columns(Dispositivo.id, Dispositivo.chipid).distinct().all()

    return render_template(
        'sections/cliente/inicio.html',
        usuario=usuario,
        parcelas=[{"id": p.id, "nombre": p.nombre} for p in parcelas],
        cultivos=[{"id": c.id, "nombre": c.nombre} for c in cultivos],
        dispositivos=[{"id": d.id, "chipid": d.chipid} for d in dispositivos]
    )