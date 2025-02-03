from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import Cultivo, Parcela
from app.extensions import db

cultivo = Blueprint('cultivo', __name__)

@cultivo.route('/mostrar')
def cultivos():
    cultivos = Cultivo.query.all()
    parcelas = Parcela.query.all()
    return render_template('sections/admin/cultivos.html', cultivos=cultivos, parcelas=parcelas)

@cultivo.route('/crear', methods=['POST'])
def crear_cultivo():
    nombre = request.form['nombre']
    tipo = request.form['tipo']
    variedad = request.form['variedad']
    fase = request.form['fase']
    detalle = request.form['detalle']
    fk_parcela = request.form['parcela']

    errores = []

    # Validar nombre
    if not nombre:
        errores.append("El nombre de cultivo es obligatorio.")

    # Validar tipo
    if not tipo:
        errores.append("El tipo de cultivo es obligatorio.")

    # Validar variedad
    if not variedad:
        errores.append("La variedad de cultivo es obligatorio.")

    # Validar fase
    if not fase:
        errores.append("La fase de cultivo es obligatorio.")

    # Validar detalle
    if not detalle:
        errores.append("El detalle de cultivo es obligatorio.")

    # Validar parcela
    if not fk_parcela:
        errores.append("Debe seleccionar una parcela.")

    if errores:
        # Si hay errores, mostramos los mensajes y redirigimos
        for error in errores:
            flash(error, 'danger')
        return redirect(url_for('cultivo.cultivos'))

    # Crear Cultivo
    nuevo_cultivo = Cultivo(
        nombre=nombre,
        tipo=tipo,
        variedad=variedad,
        fase=fase,
        fk_parcela=fk_parcela,
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

@cultivo.route('/cultivos/editar/<int:id>', methods=['POST'])
def editar_cultivo(id):
    # Implementar lógica para editar un cultivo
    pass

@cultivo.route('/cultivos/eliminar/<int:id>', methods=['POST'])
def eliminar_cultivo(id):
    # Implementar lógica para eliminar un cultivo
    pass