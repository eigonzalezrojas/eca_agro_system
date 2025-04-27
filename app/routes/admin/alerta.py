from flask import Blueprint, session, jsonify, render_template, request, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from app.models import Alerta, Usuario, Registro, Fase
from app.extensions import db
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
import os

alertasAdmin = Blueprint('alertasAdmin', __name__)

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
ARCHIVO_ALERTAS = os.path.join(UPLOAD_FOLDER, "tabla_alertas.xlsx")


@alertasAdmin.route('/')
def mostrar_alertas():
    user_id = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    usuario = Usuario.query.filter_by(rut=user_id).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Subconsulta: obtener la alerta más reciente por dispositivo
    subq = (
        db.session.query(
            Alerta.fk_dispositivo,
            func.max(Alerta.fecha_alerta).label("fecha_max")
        )
        .group_by(Alerta.fk_dispositivo)
        .subquery()
    )

    AlertaAlias = aliased(Alerta)

    alertas_query = (
        db.session.query(AlertaAlias)
        .join(subq, db.and_(
            AlertaAlias.fk_dispositivo == subq.c.fk_dispositivo,
            AlertaAlias.fecha_alerta == subq.c.fecha_max
        ))
        .join(Fase, AlertaAlias.fk_fase == Fase.id)
        .order_by(AlertaAlias.fecha_alerta.desc())
        .add_columns(
            AlertaAlias.id,
            AlertaAlias.mensaje,
            AlertaAlias.fecha_alerta,
            AlertaAlias.nivel_alerta,
            Fase.cultivo.label("cultivo"),
            Fase.nombre.label("fase"),
            AlertaAlias.fk_dispositivo.label("chipid")
        )
    )

    paginacion = alertas_query.paginate(page=page, per_page=per_page)
    alertas = [
        {
            "id": a.id,
            "mensaje": a.mensaje,
            "fecha": a.fecha_alerta.strftime("%d-%m-%Y %H:%M"),
            "nivel": a.nivel_alerta,
            "cultivo": a.cultivo,
            "fase": a.fase,
            "chipid": a.chipid
        }
        for a in paginacion.items
    ]

    return render_template('sections/admin/alertas.html',
                           alertas=alertas,
                           paginacion=paginacion,
                           usuario=usuario)


@alertasAdmin.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    alerta = Alerta.query.get_or_404(id)

    # Obtener nueva fase
    nueva_fase_id = request.form.get('editFase', alerta.fk_fase)
    fase = Fase.query.get(nueva_fase_id)

    if fase:
        alerta.fk_fase = fase.id
        alerta.cultivo_nombre = fase.cultivo

    alerta.mensaje = request.form.get('editMensaje', alerta.mensaje)

    db.session.commit()
    flash("Alerta editada con éxito!", "success")
    return redirect(url_for('alertasAdmin.mostrar_alertas'))



@alertasAdmin.route('/buscar/<id>', methods=['GET'])
def buscar(id):
    alerta = (
        Alerta.query
        .join(Fase, Alerta.fk_fase == Fase.id)
        .filter(Alerta.id == id)
        .add_columns(Alerta.id, Alerta.mensaje, Fase.cultivo.label("cultivo"), Fase.nombre.label("fase"))
        .first()
    )

    if not alerta:
        return jsonify({"error": "Alerta no encontrada"}), 404

    return jsonify({
        "id": alerta.id,
        "mensaje": alerta.mensaje,
        "cultivo": alerta.cultivo,
        "fase": alerta.fase
    })


@alertasAdmin.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    alerta = Alerta.query.get_or_404(id)
    db.session.delete(alerta)
    db.session.commit()
    flash('Alerta eliminada exitosamente', 'success')
    return redirect(url_for('alertasAdmin.mostrar_alertas'))


@alertasAdmin.route('/descargar', methods=['GET'])
def descargar_archivo():
    """Descargar el archivo de parámetros de alertas"""
    if os.path.exists(ARCHIVO_ALERTAS):
        return send_file(ARCHIVO_ALERTAS, as_attachment=True)
    flash("El archivo de alertas no existe.", "error")
    return redirect(url_for('alertasAdmin.mostrar_alertas'))


@alertasAdmin.route('/subir', methods=['POST'])
def subir_archivo():
    """Subir el archivo Excel con parámetros de alertas"""
    if 'archivo' not in request.files:
        flash("No se seleccionó ningún archivo.", "error")
        return redirect(url_for('alertasAdmin.mostrar_alertas'))

    archivo = request.files['archivo']
    if archivo.filename == '':
        flash("No se seleccionó ningún archivo.", "error")
        return redirect(url_for('alertasAdmin.mostrar_alertas'))

    if archivo and archivo.filename.endswith('.xlsx'):
        # Guardar el archivo con un nombre seguro
        nombre_archivo = secure_filename("tabla_alertas.xlsx")
        archivo.save(os.path.join(UPLOAD_FOLDER, nombre_archivo))
        flash("Archivo de alertas subido con éxito.", "success")
    else:
        flash("Formato de archivo no permitido. Solo se aceptan archivos .xlsx", "error")

    return redirect(url_for('alertasAdmin.mostrar_alertas'))