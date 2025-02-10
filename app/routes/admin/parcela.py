from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from app.models import Parcela, Usuario
from app.extensions import db

parcela = Blueprint('parcela', __name__)


@parcela.route('/mostrar')
def parcelas():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    # Obtener el usuario
    usuario = Usuario.query.filter_by(rut=user_id).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    usuarios = Usuario.query.all()
    parcelas = Parcela.query.all()

    return render_template('sections/admin/parcelas.html', parcelas=parcelas, usuario=usuario, usuarios=usuarios)


@parcela.route('/crear', methods=['POST'])
def crear_parcela():
    nombre = request.form['nombre']
    region = request.form['regiones']
    comuna = request.form['comunas']
    direccion = request.form['direccion']
    fk_usuario = request.form['usuario']

    errores = []

    # Validar nombre
    if not nombre:
        errores.append("El nombre de parcela es obligatorio.")

    # Validar región
    if not region:
        errores.append("Debe seleccionar una Región")

    # Validar comuna
    if not comuna:
        errores.append("Debe seleccionar una Comuna")

    # Validar dirección
    if not direccion:
        errores.append("Debe ingersar una Dirección")

    # Validar cliente
    if not fk_usuario:
        errores.append("Debe seleccionar un usuario")

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


@parcela.route('/editar/<int:id>', methods=['POST'])
def editar_parcela(id):
    parcela = Parcela.query.get_or_404(id)

    # Actualizar los datos del parcela
    parcela.nombre = request.form.get('editNombre', parcela.nombre)
    parcela.region = request.form.get('editRegiones', parcela.region)
    parcela.comuna = request.form.get('editComunas', parcela.comuna)
    parcela.direccion = request.form.get('editDireccion', parcela.direccion)
    parcela.fk_usuario = request.form.get('editUsuario', parcela.fk_usuario)

    db.session.commit()
    flash('parcela actualizado exitosamente', 'success')
    return redirect(url_for('parcela.parcelas'))


@parcela.route('/buscar/<id>', methods=['GET'])
def obtener_parcela(id):
    parcela = Parcela.query.filter_by(id=id).first()

    if not parcela:
        return {"error": f"Parcela con id {id} no encontrado"}, 404

    return {
        "id": parcela.id,
        "nombre": parcela.nombre,
        "region": parcela.region,
        "comuna": parcela.comuna,
        "direccion": parcela.direccion,
        "fk_usuario": parcela.fk_usuario
    }

@parcela.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_parcela(id):
    parcela = Parcela.query.get_or_404(id)
    if not parcela:
        return {"error": f"Parcela con id {id} no encontrado"}, 404

    db.session.delete(parcela)
    db.session.commit()
    flash('parcela eliminada exitosamente', 'success')
    return redirect(url_for('parcela.parcelas'))


@parcela.route('/buscar_por_usuario/<rut_usuario>', methods=['GET'])
def obtener_parcelas_por_usuario(rut_usuario):
    parcelas = Parcela.query.filter_by(fk_usuario=rut_usuario).all()

    if not parcelas:
        return {"error": f"No se encontraron parcelas para el usuario con RUT {rut_usuario}"}, 404
    return [
        {
            "id": parcela.id,
            "nombre": parcela.nombre,
            "region": parcela.region,
            "comuna": parcela.comuna,
            "direccion": parcela.direccion,
            "fk_usuario": parcela.fk_usuario
        }
        for parcela in parcelas
    ]