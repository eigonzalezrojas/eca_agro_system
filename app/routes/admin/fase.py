from flask import Blueprint, session, jsonify, render_template, request, flash, redirect, url_for
from app.models import Fase, Usuario, Cultivo
from app.extensions import db

fase = Blueprint('fase', __name__, url_prefix='/admin/fase')
@fase.route('/')
def fases():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    usuario = Usuario.query.filter_by(rut=user_id).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    fases = db.session.query(Fase, Cultivo).join(Cultivo, Fase.fk_cultivo == Cultivo.id).all()
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
    cultivo_id = request.form['cultivo']

    errores = []

    if not nombre:
        errores.append("El nombre de fase es obligatorio.")

    if not cultivo_id:
        errores.append("El cultivo es obligatorio.")

    if errores:
        for error in errores:
            flash(error, 'danger')
        return redirect(url_for('fase.fases'))

    try:
        cultivo = Cultivo.query.get(int(cultivo_id))
        if not cultivo:
            flash("El cultivo seleccionado no existe.", "danger")
            return redirect(url_for('fase.fases'))

        nueva_fase = Fase(
            nombre=nombre,
            fk_cultivo=cultivo.id
        )

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

    fase.id = request.form.get('idFase', fase.id)
    fase.nombre = request.form.get('editFase', fase.nombre)
    fase.fk_cultivo = request.form.get('editCultivo', fase.fk_cultivo)

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
        return jsonify({"error": "Fase no encontrado"}), 404
    return jsonify({
        "id": fase.id,
        "nombre": fase.nombre,
        "fk_cultivo": fase.fk_cultivo
    })