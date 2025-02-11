from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from app.models import Registro, Dispositivo, Cultivo, Parcela, Usuario
from app.extensions import db
from sqlalchemy import text

registro = Blueprint('registro', __name__)


@registro.route('/registros')
def registros():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    usuario = Usuario.query.filter_by(rut=user_id).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    registros = Registro.query.join(Dispositivo).join(Cultivo).join(Parcela).join(Usuario).all()
    usuarios = Usuario.query.all()
    dispositivos = Dispositivo.query.all()
    cultivos = Cultivo.query.all()

    # Obtener la lista de tablas que comienzan con "data"
    query = text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() 
        AND table_name LIKE 'data%'
    """)

    tablas = db.session.execute(query).fetchall()
    fuente = [tabla[0] for tabla in tablas]

    return render_template('sections/admin/registros.html',
                           usuario=usuario,
                           registros=registros,
                           usuarios=usuarios,
                           dispositivos=dispositivos,
                           cultivos=cultivos,
                           fuente=fuente)

@registro.route('/crear', methods=['POST'])
def crear_registro():
    fk_usuario = request.form.get('usuario')
    fk_dispositivo = request.form.get('dispositivo')
    fk_parcela = request.form.get('parcela')
    fk_cultivo = request.form.get('cultivo')
    fk_cultivo_fase = request.form.get('fase')
    fuente = request.form.get('fuente')

    # Verificar que todos los campos están llenos
    if not all([fk_usuario, fk_dispositivo, fk_parcela, fk_cultivo, fk_cultivo_fase, fuente]):
        flash('Todos los campos son obligatorios', 'error')
        return redirect(url_for('registro.nuevo_registro'))

    # Crear el nuevo registro
    nuevo_registro = Registro(
        fk_usuario=fk_usuario,
        fk_dispositivo=fk_dispositivo,
        fk_parcela=fk_parcela,
        fk_cultivo=fk_cultivo,
        fk_cultivo_fase=fk_cultivo_fase,
        fuente=fuente
    )

    db.session.add(nuevo_registro)
    db.session.commit()
    flash('Registro creado con éxito', 'success')

    return redirect(url_for('registro.registros'))


@registro.route('/editar/<int:id>', methods=['POST'])
def editar_registro(id):
    registro = Registro.query.get_or_404(id)

    registro.fk_usuario = request.form.get('editUsuario', registro.fk_usuario)
    registro.fk_dispositivo = request.form.get('editDispositivo', registro.fk_dispositivo)
    registro.fk_parcela = request.form.get('editParcela', registro.fk_parcela)
    registro.fk_cultivo = request.form.get('editCultivo', registro.fk_cultivo)
    registro.fk_cultivo_fase = request.form.get('editFase', registro.fk_cultivo_fase)
    registro.fuente = request.form.get('editFuente', registro.fuente)

    db.session.commit()
    flash('Registro actualizado exitosamente', 'success')
    return redirect(url_for('registro.registros'))


@registro.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_registro(id):
    registro = Registro.query.get_or_404(id)

    if not registro:
        return {"error": f"Registro con id {id} no encontrado"}, 404

    db.session.delete(registro)
    db.session.commit()
    flash('Registro eliminado exitosamente', 'success')
    return redirect(url_for('registro.registros'))


@registro.route('/buscar/<int:id>', methods=['GET'])
def obtener_registro(id):
    registro = Registro.query.get_or_404(id)

    return {
        "id": registro.id,
        "fk_dispositivo": registro.fk_dispositivo,
        "fk_cultivo": registro.fk_cultivo,
        "fk_parcela": registro.fk_parcela,
        "fk_usuario": registro.fk_usuario,
        "fuente": registro.fuente,
        "fecha_registro": registro.fecha_registro.strftime('%Y-%m-%d %H:%M')
    }