from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import Dispositivo
from app.extensions import db

dispositivo = Blueprint('dispositivo', __name__)

@dispositivo.route('/dispositivos')
def dispositivos():
    dispositivos = Dispositivo.query.all()
    return render_template('sections/admin/dispositivos.html', dispositivos=dispositivos)


@dispositivo.route('/crear', methods=['POST'])
def crear_dispositivo():
    chipid = request.form['chipid']
    modelo = request.form['modelo']
    caracteristica = request.form['caracteristica']

    errores = []

    # Validar chipid
    if not chipid:
        errores.append("El nombre de dispositivo es obligatorio.")

    # Validar modelo
    if not modelo:
        errores.append("La variedad de dispositivo es obligatorio.")

    if errores:
        # Si hay errores, mostramos los mensajes y redirigimos
        for error in errores:
            flash(error, 'danger')
        return redirect(url_for('dispositivo.dispositivos'))

    # Crear dispositivo
    nuevo_dispositivo = Dispositivo(
        chipid=chipid,
        modelo=modelo,
        caracteristica=caracteristica
    )

    try:
        db.session.add(nuevo_dispositivo)
        db.session.commit()
        flash('dispositivo creado exitosamente.', 'success')
        return redirect(url_for('dispositivo.dispositivos'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear el dispositivo: {str(e)}', 'danger')
        return redirect(url_for('dispositivo.dispositivos'))
    finally:
        db.session.close()
        return redirect(url_for('dispositivo.dispositivos'))


@dispositivo.route('/editar/<int:id>', methods=['POST'])
def editar_dispositivo(id):
    dispositivo = Dispositivo.query.get_or_404(id)

    # Actualizar los datos del dispositivo
    dispositivo.chipid = request.form.get('editChipid', dispositivo.chipid)
    dispositivo.modelo = request.form.get('editModelo', dispositivo.modelo)
    dispositivo.caracteristica = request.form.get('editCaracteristica', dispositivo.caracteristica)

    db.session.commit()
    flash('dispositivo actualizado exitosamente', 'success')
    return redirect(url_for('dispositivo.dispositivos'))


@dispositivo.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_dispositivo(id):
    dispositivo = Dispositivo.query.get_or_404(id)
    if not dispositivo:
        return {"error": f"dispositivo con id {id} no encontrado"}, 404

    db.session.delete(dispositivo)
    db.session.commit()
    flash('dispositivo eliminado exitosamente', 'success')
    return redirect(url_for('dispositivo.dispositivos'))


@dispositivo.route('/buscar/<id>', methods=['GET'])
def obtener_dispositivo(id):
    dispositivo = Dispositivo.query.filter_by(id=id).first()

    if not dispositivo:
        return {"error": f"dispositivo con id {id} no encontrado"}, 404

    return {
        "id": dispositivo.id,
        "chipid": dispositivo.chipid,
        "modelo": dispositivo.modelo,
        "caracteristica": dispositivo.caracteristica
    }