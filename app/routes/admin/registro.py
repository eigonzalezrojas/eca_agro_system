from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from app.models import Registro, Dispositivo, Fase, Parcela, Usuario, Cultivo
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

    registros = (
        db.session.query(Registro)
        .join(Dispositivo, Registro.fk_dispositivo == Dispositivo.id)
        .join(Fase, Registro.fk_fase == Fase.id)
        .join(Parcela, Registro.fk_parcela == Parcela.id)
        .join(Usuario, Registro.fk_usuario == Usuario.rut)
        .all()
    )

    usuarios = Usuario.query.all()
    dispositivos = Dispositivo.query.all()
    cultivos = db.session.query(Cultivo.nombre).distinct().all()
    fases = Fase.query.all()

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
                           fases=fases,
                           fuente=fuente)




@registro.route('/crear', methods=['POST'])
def crear_registro():
    fk_usuario = request.form.get('usuario')
    fk_parcela = request.form.get('parcela')
    fk_fase = request.form.get('fase')
    fk_dispositivo = request.form.get('dispositivo')
    fuente = request.form.get('fuente')

    fase = Fase.query.get(int(fk_fase))
    if not fase:
        flash("La fase seleccionada no existe.", "danger")
        return redirect(url_for('registro.registros'))

    # Tomar el nombre del cultivo desde la fase seleccionada
    cultivo_nombre = fase.cultivo
    fase_nombre = fase.nombre

    if not all([fk_usuario, fk_parcela, fk_fase, fk_dispositivo, fuente]):
        flash('Todos los campos son obligatorios', 'error')
        return redirect(url_for('registro.registros'))

    nuevo_registro = Registro(
        fk_usuario=fk_usuario,
        fk_parcela=fk_parcela,
        fk_fase=fk_fase,
        fk_dispositivo=fk_dispositivo,
        cultivo_nombre=cultivo_nombre,
        fase_nombre=fase_nombre,
        fuente=fuente
    )

    db.session.add(nuevo_registro)
    db.session.commit()
    flash('Registro creado con éxito', 'success')

    return redirect(url_for('registro.registros'))



@registro.route('/editar/<int:id>', methods=['POST'])
def editar_registro(id):
    registro = Registro.query.get_or_404(id)

    fk_usuario = request.form.get('editUsuario')
    fk_parcela = request.form.get('editParcela')
    fk_cultivo = request.form.get('editCultivo')
    fk_fase = request.form.get('fase')
    fk_dispositivo = request.form.get('editDispositivo')
    fuente = request.form.get('editFuente')

    fase = Fase.query.get(int(fk_fase))
    if not fase:
        flash("La fase seleccionada no existe.", "danger")
        return redirect(url_for('registro.registros'))

    # Actualizar valores desde la fase seleccionada
    registro.fk_usuario = fk_usuario
    registro.fk_parcela = fk_parcela
    registro.fk_fase = fk_fase
    registro.fk_dispositivo = fk_dispositivo
    registro.cultivo_nombre = fase.cultivo
    registro.fase_nombre = fase.nombre
    registro.fuente = fuente

    db.session.commit()
    flash('Registro actualizado exitosamente', 'success')
    return redirect(url_for('registro.registros'))


@registro.route('/buscar/<int:id>', methods=['GET'])
def obtener_registro(id):
    registro = Registro.query.get_or_404(id)

    return jsonify({
        "id": registro.id,
        "fk_usuario": registro.fk_usuario,
        "fk_parcela": registro.fk_parcela,
        "fk_fase": registro.fk_fase,
        "fk_dispositivo": registro.fk_dispositivo,
        "cultivo_nombre": registro.cultivo_nombre,
        "fase_nombre": registro.fase_nombre,
        "fuente": registro.fuente
    })



@registro.route('/fase/por_cultivo', methods=['GET'])
def obtener_fases_por_cultivo():
    cultivo_nombre = request.args.get('cultivo_nombre')

    if not cultivo_nombre:
        return jsonify({"error": "Debe proporcionar un nombre de cultivo"}), 400

    # Buscar todas las fases asociadas al nombre del cultivo
    fases = Fase.query.filter_by(cultivo=cultivo_nombre).all()

    return jsonify([{"id": fase.id, "nombre": fase.nombre} for fase in fases])



@registro.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_registro(id):
    try:
        registro = Registro.query.get_or_404(id)
        db.session.delete(registro)
        db.session.commit()
        flash('Registro eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el registro: {str(e)}', 'danger')
    return redirect(url_for('registro.registros'))


