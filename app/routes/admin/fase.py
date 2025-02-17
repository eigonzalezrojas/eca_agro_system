from flask import Blueprint, session, jsonify, render_template, request, flash, redirect, url_for
from app.models import Fase, Usuario, Cultivo
from app.extensions import db

fase = Blueprint('fase', __name__)

@fase.route('/')
def fases():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    usuario = Usuario.query.filter_by(rut=user_id).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    fases = Fase.query.all()
    cultivos = db.session.query(Cultivo.nombre).distinct().all()

    return render_template('sections/admin/fases.html',
                           fases=fases,
                           cultivos=cultivos,
                           usuario=usuario)


@fase.route('/crear', methods=['POST'])
def crear():
    nombre = request.form['nombre']
    cultivo = request.form['cultivo']

    errores = []
    if not nombre:
        errores.append("El nombre de fase es obligatorio.")
    if not cultivo:
        errores.append("El cultivo es obligatorio.")

    if errores:
        for error in errores:
            flash(error, 'danger')
        return redirect(url_for('fase.fases'))

    try:
        nueva_fase = Fase(nombre=nombre, cultivo=cultivo)
        db.session.add(nueva_fase)
        db.session.commit()
        flash('Fase creada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear la fase: {str(e)}', 'danger')
    finally:
        db.session.close()

    return redirect(url_for('fase.fases'))


@fase.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    fase = Fase.query.get_or_404(id)

    fase.nombre = request.form.get('editFase', fase.nombre)
    fase.cultivo = request.form.get('editCultivo', fase.cultivo)

    db.session.commit()
    flash('Fase editada exitosamente.', 'success')
    return redirect(url_for('fase.fases'))


@fase.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    fase = Fase.query.get_or_404(id)
    db.session.delete(fase)
    db.session.commit()
    flash('Fase eliminada exitosamente.', 'success')
    return redirect(url_for('fase.fases'))


@fase.route('/buscar/<int:id>', methods=['GET'])
def buscar(id):
    fase = Fase.query.get(id)
    if not fase:
        return jsonify({"error": "Fase no encontrada"}), 404
    return jsonify({
        "id": fase.id,
        "nombre": fase.nombre,
        "cultivo": fase.cultivo
    })
