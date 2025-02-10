from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from app.models import Cultivo, Usuario
from app.extensions import db

cultivo = Blueprint('cultivo', __name__)

@cultivo.route('/mostrar')
def cultivos():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    # Obtener el usuario
    usuario = Usuario.query.filter_by(rut=user_id).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    cultivos = Cultivo.query.all()
    return render_template('sections/admin/cultivos.html', cultivos=cultivos, usuario=usuario)


@cultivo.route('/crear', methods=['POST'])
def crear_cultivo():
    nombre = request.form['nombre']
    variedad = request.form['variedad']
    fase = request.form['fase']
    detalle = request.form['detalle']

    errores = []

    # Validar nombre
    if not nombre:
        errores.append("El nombre de cultivo es obligatorio.")

    # Validar variedad
    if not variedad:
        errores.append("La variedad de cultivo es obligatorio.")

    if errores:
        # Si hay errores, mostramos los mensajes y redirigimos
        for error in errores:
            flash(error, 'danger')
        return redirect(url_for('cultivo.cultivos'))

    # Crear Cultivo
    nuevo_cultivo = Cultivo(
        nombre=nombre,
        variedad=variedad,
        fase=fase,
        detalle=detalle
    )

    try:
        db.session.add(nuevo_cultivo)
        db.session.commit()
        flash('Cultivo creado exitosamente.', 'success')
        return redirect(url_for('cultivo.cultivos'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear el cultivo: {str(e)}', 'danger')
        return redirect(url_for('cultivo.cultivos'))
    finally:
        db.session.close()
        return redirect(url_for('cultivo.cultivos'))


@cultivo.route('/editar/<int:id>', methods=['POST'])
def editar_cultivo(id):
    cultivo = Cultivo.query.get_or_404(id)

    # Actualizar los datos del cultivo
    cultivo.nombre = request.form.get('editNombre', cultivo.nombre)
    cultivo.variedad = request.form.get('editVariedad', cultivo.variedad)
    cultivo.fase = request.form.get('editFase', cultivo.fase)
    cultivo.detalle = request.form.get('editDetalle', cultivo.detalle)

    db.session.commit()
    flash('cultivo actualizado exitosamente', 'success')
    return redirect(url_for('cultivo.cultivos'))


@cultivo.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_cultivo(id):
    cultivo = Cultivo.query.get_or_404(id)
    if not cultivo:
        return {"error": f"Cultivo con id {id} no encontrado"}, 404

    db.session.delete(cultivo)
    db.session.commit()
    flash('Cultivo eliminado exitosamente', 'success')
    return redirect(url_for('cultivo.cultivos'))


@cultivo.route('/buscar/<id>', methods=['GET'])
def obtener_cultivo(id):
    cultivo = Cultivo.query.filter_by(id=id).first()

    if not cultivo:
        return {"error": f"Cultivo con id {id} no encontrado"}, 404

    return {
        "id": cultivo.id,
        "nombre": cultivo.nombre,
        "variedad": cultivo.variedad,
        "fase": cultivo.fase,
        "detalle": cultivo.detalle
    }