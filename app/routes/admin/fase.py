from flask import Blueprint, session, jsonify, render_template, request, flash, redirect, url_for
from app.models import Fase, Usuario, Cultivo
from app.extensions import db

fase = Blueprint('fase', __name__, url_prefix='/admin/fase')
@fase.route('/')
def fases():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    # Obtener el usuario
    usuario = Usuario.query.filter_by(rut=user_id).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    fases = Fase.query.join(Cultivo).all()
    cultivos = Cultivo.query.all()

    data_fases = []
    for fase, cultivo in fases:
        data_fases.append({
            "id": fase.id,
            "nombre": fase.nombre,
            "cultivo": cultivo.nombre,
        })

    return render_template('sections/admin/fases.html',
                           fases=data_fases,
                           cultivos=cultivos,
                           usuario=usuario)


@fase.route('/crear', methods=['POST'])
def crear():
    nombre = request.form['nombre']
    cultivo = request.form['cultivo']

    errores = []

    # Validar nombre
    if not nombre:
        errores.append("El nombre de fase es obligatorio.")

    # Validar variedad
    if not cultivo:
        errores.append("El cultivo es obligatorio.")

    if errores:
        # Si hay errores, mostramos los mensajes y redirigimos
        for error in errores:
            flash(error, 'danger')
        return redirect(url_for('fase.fases'))

    # Crear Fase
    nueva_fase = Fase(
        nombre=nombre,
        cultivo=cultivo
    )

    try:
        db.session.add(nueva_fase)
        db.session.commit()
        flash('Fase creada exitosamente.', 'success')
        return redirect(url_for('fase.fases'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear la fase: {str(e)}', 'danger')
        return redirect(url_for('fase.fases'))
    finally:
        db.session.close()
        return redirect(url_for('fase.fases'))