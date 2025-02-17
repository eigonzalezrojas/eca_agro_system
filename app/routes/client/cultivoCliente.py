from flask import Blueprint, render_template, session, request, jsonify
from app.models import Registro, Fase, Usuario, Dispositivo, Parcela
from app.extensions import db
from app.services.email_service import enviar_correo_cambio_fase

cultivoCliente = Blueprint('cultivoCliente', __name__)


@cultivoCliente.route('/listar', methods=['GET'])
def listar_cultivos():
    """Renderiza la tabla de cultivos asociados al usuario autenticado."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    usuario = Usuario.query.filter_by(rut=user_id).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    registros = Registro.query.filter_by(fk_usuario=user_id).all()
    cultivos_data = []
    for registro in registros:
        fase = Fase.query.get(registro.fk_fase)
        dispositivo = Dispositivo.query.get(registro.fk_dispositivo) if registro.fk_dispositivo else None

        if fase:
            cultivos_data.append({
                "id": registro.id,
                "nombre": fase.cultivo,
                "fase": fase.nombre,
                "detalle": "Información adicional",
                "parcela": registro.fk_parcela,
                "dispositivo": dispositivo.chipid if dispositivo else "No asignado"
            })

    return render_template('sections/cliente/cultivoCliente.html', usuario=usuario, cultivos=cultivos_data)


@cultivoCliente.route('/cambiar_fase', methods=['POST'])
def cambiar_fase_cultivo():
    """Permite cambiar la fase del cultivo en la tabla Registro y envía un correo de notificación."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    data = request.get_json()
    registro_id = data.get("cultivo_id")
    nueva_fase_nombre = data.get("nueva_fase")

    if not registro_id or not nueva_fase_nombre:
        return jsonify({"error": "Datos incompletos"}), 400

    # Buscar el registro
    registro = Registro.query.filter_by(id=registro_id, fk_usuario=user_id).first()
    if not registro:
        return jsonify({"error": "No tienes permisos para modificar este cultivo"}), 403

    # Buscar la fase correspondiente a la nueva fase
    nueva_fase = Fase.query.filter_by(nombre=nueva_fase_nombre, cultivo=registro.fase.cultivo).first()
    if not nueva_fase:
        return jsonify({"error": "Fase no encontrada"}), 404

    # Actualizar la fase en la tabla REGISTRO
    registro.fk_fase = nueva_fase.id
    db.session.commit()

    # Obtener usuario y parcela
    usuario = Usuario.query.filter_by(rut=user_id).first()
    parcela = Parcela.query.get(registro.fk_parcela)

    # Enviar correo con la información corregida
    mensaje_alerta = f"""
    Estimado(a) Administrador(a):

    🔄 Cambio de Fase en Cultivo

    Cliente: {usuario.nombre} {usuario.apellido} (RUT: {usuario.rut})
    Cultivo: {nueva_fase.cultivo} 
    Nueva Fase: {nueva_fase_nombre}

    📍 Ubicación de la Parcela:
    - Dirección: {parcela.direccion if parcela else 'No disponible'}
    - Comuna: {parcela.comuna if parcela else 'No disponible'}

    ✅ Se ha registrado correctamente este cambio en el sistema.

    Saludos,
    Equipo de ECA Innovation
    """

    enviar_correo_cambio_fase(
        "ecainnovation@gmail.com",
        f"Cambio de Fase en {nueva_fase.cultivo}",
        mensaje_alerta,
        "eithelgonzalezrojas@gmail.com"
    )

    return jsonify({"mensaje": "Fase actualizada correctamente."})


@cultivoCliente.route('/fases', methods=['GET'])
def obtener_fases_cultivo():
    """Obtiene las fases disponibles para un tipo de cultivo."""
    nombre_cultivo = request.args.get("nombre")
    if not nombre_cultivo:
        return jsonify({"error": "Debe proporcionar el nombre del cultivo"}), 400

    # Buscar las fases de un cultivo desde la tabla Fase
    fases = Fase.query.filter_by(cultivo=nombre_cultivo).all()
    fases = [fase.nombre for fase in fases]

    return jsonify({"fases": fases})
