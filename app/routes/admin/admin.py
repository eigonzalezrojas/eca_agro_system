from flask import Blueprint, render_template, session, jsonify
from app.models import Usuario, Parcela, Cultivo, Dispositivo

admin = Blueprint('admin', __name__)

@admin.route('/inicio')
def inicio():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    # Obtener el usuario
    usuario = Usuario.query.filter_by(rut=user_id).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404


    total_administradores = Usuario.query.filter_by(fk_rol=1).count()
    total_clientes = Usuario.query.filter_by(fk_rol=2).count()
    total_visitas = Usuario.query.filter_by(fk_rol=3).count()
    total_parcelas = Parcela.query.count()
    total_cultivos = Cultivo.query.count()
    total_dispositivos = Dispositivo.query.count()

    return render_template(
        'sections/admin/inicio.html',
        usuario=usuario,
        total_administradores=total_administradores,
        total_clientes=total_clientes,
        total_visitas=total_visitas,
        total_parcelas=total_parcelas,
        total_cultivos=total_cultivos,
        total_dispositivos=total_dispositivos
    )