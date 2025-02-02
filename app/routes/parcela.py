from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import Parcela, Usuario
from app.extensions import db

parcela = Blueprint('parcela', __name__)


@parcela.route('/parcelas')
def parcelas():
    parcelas = Parcela.query.all()
    usuarios = Usuario.query.all()
    return render_template('sections/admin/parcelas.html', parcelas=parcelas, usuarios=usuarios)


@parcela.route('/parcela/crear', methods=['POST'])
def crear_parcela():
    print(request.form)
    nombre = request.form['nombre']
    region = request.form['regiones']
    comuna = request.form['comunas']
    direccion = request.form['direccion']
    fk_usuario = request.form['usuario']

    errores = []

    # Validar nombre
    if not nombre:
        errores.append("El nombre de parcela es obligatorio.")

    # Validar apellido
    if not region:
        errores.append("Debe seleccionar una Región")

    # Validar teléfono
    if not comuna:
        errores.append("Debe seleccionar una Comuna")

    # Validar correo
    if not direccion:
        errores.append("Debe ingersar una Dirección")

    # Validar RUT
    if not fk_usuario:
        errores.append("Debe seleccionar el usuario")

    if errores:
        # Si hay errores, mostramos los mensajes y redirigimos
        for error in errores:
            flash(error, 'danger')
        return redirect(url_for('parcela.parcelas'))

    # Crear la Parcela
    nueva_parcela = Parcela(
        nombre=nombre,
        region=region,
        comuna=comuna,
        direccion=direccion,
        fk_usuario=fk_usuario
    )

    try:
        db.session.add(nueva_parcela)
        db.session.commit()
        flash('Parcela creada exitosamente.', 'success')
        return redirect(url_for('parcela.parcelas'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear la parcela: {str(e)}', 'danger')
        return redirect(url_for('parcela.parcelas'))
    finally:
        db.session.close()
        return redirect(url_for('parcela.parcelas'))


@parcela.route('/parcela/editar/<int:id>', methods=['POST'])
def editar_parcela(id):
    # Implementar lógica para editar una parcela
    pass


@parcela.route('/parcelas/eliminar/<int:id>', methods=['POST'])
def eliminar_parcela(id):
    # Implementar lógica para eliminar una parcela
    pass
