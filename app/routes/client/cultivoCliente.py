from flask import Blueprint, render_template, session, request, jsonify
from app.models import Registro, Cultivo, Usuario, Dispositivo, Parcela
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
        cultivo = Cultivo.query.get(registro.fk_cultivo)
        dispositivo = Dispositivo.query.get(registro.fk_dispositivo) if registro.fk_dispositivo else None
        if cultivo:
            cultivos_data.append({
                "id": cultivo.id,
                "nombre": cultivo.nombre,
                "variedad": cultivo.variedad,
                "fase": cultivo.fase,
                "detalle": cultivo.detalle,
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
    cultivo_id = data.get("cultivo_id")
    nueva_fase = data.get("nueva_fase")

    if not cultivo_id or not nueva_fase:
        return jsonify({"error": "Datos incompletos"}), 400

    # Buscar el registro asociado al usuario y cultivo
    registro = Registro.query.filter_by(fk_usuario=user_id, fk_cultivo=cultivo_id).first()
    if not registro:
        return jsonify({"error": "No tienes permisos para modificar este cultivo"}), 403

    # Obtener usuario y parcela
    usuario = Usuario.query.filter_by(rut=user_id).first()
    parcela = Parcela.query.get(registro.fk_parcela)

    # Actualizar la fase en la tabla REGISTRO
    registro.fk_cultivo_fase = nueva_fase
    db.session.commit()

    # Enviar correo con la información corregida
    mensaje_alerta = f"""
    Estimado(a) Administrador(a):
    
    🔄 Cambio de Fase en Cultivo

    Cliente: {usuario.nombre} {usuario.apellido} (RUT: {usuario.rut})
    Cultivo: {registro.cultivo.nombre} - {registro.cultivo.variedad}
    Nueva Fase: {nueva_fase}

    📍 Ubicación de la Parcela:
    - Dirección: {parcela.direccion if parcela else 'No disponible'}
    - Comuna: {parcela.comuna if parcela else 'No disponible'}

    ✅ Se ha registrado correctamente este cambio en el sistema.
    
    Saludos,
    Equipo de ECA Innovation
    """

    enviar_correo_cambio_fase(
        "ecainnovation@gmail.com",
        f"Cambio de Fase en {registro.cultivo.nombre}",
        mensaje_alerta,
        "eithelgonzalezrojas@gmail.com"
    )

    return jsonify({"mensaje": "Fase actualizada correctamente."})


@cultivoCliente.route('/fases', methods=['GET'])
def obtener_fases_cultivo():
    """Obtiene las fases disponibles para un tipo de cultivo."""
    nombre_cultivo = request.args.get("nombre")
    print(nombre_cultivo)
    if not nombre_cultivo:
        return jsonify({"error": "Debe proporcionar el nombre del cultivo"}), 400

    fases = Cultivo.query.with_entities(Cultivo.fase).filter_by(nombre=nombre_cultivo).distinct().all()
    fases = [fase[0] for fase in fases]

    return jsonify({"fases": fases})
