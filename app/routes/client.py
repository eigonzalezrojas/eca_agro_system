from flask import Blueprint, jsonify, session, render_template
from app.models import Usuario, Registro, Dispositivo, DataP0, HistorialClima
from datetime import datetime, timedelta
from app.extensions import db

client = Blueprint('client', __name__)

@client.route('/inicio')
def inicio():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    # Obtener el usuario
    usuario = Usuario.query.filter_by(rut=user_id).first()
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Obtener el registro asociado al usuario (cliente)
    registro = Registro.query.filter_by(fk_usuario=user_id).first()
    if not registro:
        return jsonify({"error": "No hay dispositivos asociados al usuario"}), 404

    # Obtener el dispositivo asociado al registro
    dispositivo = Dispositivo.query.filter_by(id=registro.fk_dispositivo).first()
    if not dispositivo:
        return jsonify({"error": "No se encontró el dispositivo asociado"}), 404

    chipid = dispositivo.chipid

    # Obtener la última lectura del dispositivo en dataP0
    ultima_medicion = DataP0.query.filter_by(chipid=chipid).order_by(DataP0.fecha.desc()).first()

    if not ultima_medicion:
        return jsonify({"error": "No hay mediciones disponibles para el dispositivo"}), 404

    # Pasar los datos
    return render_template(
        'sections/cliente/inicio.html',
        usuario=usuario,
        chipid=chipid,
        temperatura=ultima_medicion.temperatura,
        humedad=ultima_medicion.humedad,
        fecha_hora=ultima_medicion.fecha
    )


@client.route('/datos')
def datos():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    registro = Registro.query.filter_by(fk_usuario=user_id).first()
    if not registro:
        return jsonify({"error": "No hay dispositivos asociados al usuario"}), 404

    dispositivo = Dispositivo.query.filter_by(id=registro.fk_dispositivo).first()
    if not dispositivo:
        return jsonify({"error": "No se encontró el dispositivo asociado"}), 404

    chipid = dispositivo.chipid
    ultima_medicion = DataP0.query.filter_by(chipid=chipid).order_by(DataP0.fecha.desc()).first()

    if not ultima_medicion:
        return jsonify({"error": "No hay mediciones disponibles para el dispositivo"}), 404

    # Obtener fecha de ayer
    fecha_ayer = datetime.now().date() - timedelta(days=1)

    # Buscar si ya hay un registro en HistorialClima
    historial = HistorialClima.query.filter_by(rut=user_id, chipid=chipid, fecha=fecha_ayer).first()

    if not historial:
        # Calcular Temp Max y Temp Min del día anterior
        temp_max = DataP0.query.filter(
            DataP0.chipid == chipid,
            DataP0.fecha.between(fecha_ayer, fecha_ayer + timedelta(days=1))
        ).order_by(DataP0.temperatura.desc()).first()

        temp_min = DataP0.query.filter(
            DataP0.chipid == chipid,
            DataP0.fecha.between(fecha_ayer, fecha_ayer + timedelta(days=1))
        ).order_by(DataP0.temperatura.asc()).first()

        temp_max = temp_max.temperatura if temp_max else None
        temp_min = temp_min.temperatura if temp_min else None

        # Calcular Horas Frío
        horas_frio = DataP0.query.filter(
            DataP0.chipid == chipid,
            DataP0.fecha.between(fecha_ayer, fecha_ayer + timedelta(days=1)),
            DataP0.temperatura >= 0,
            DataP0.temperatura <= 7.2
        ).count()

        # Calcular GDA si Temp Max y Temp Min existen
        gda = max(((temp_max + temp_min) / 2) - 10, 0) if temp_max and temp_min else 0

        # Guardar en HistorialClima
        if temp_max and temp_min:
            nuevo_registro = HistorialClima(
                rut=user_id,
                chipid=chipid,
                fecha=fecha_ayer,
                temp_max=temp_max,
                temp_min=temp_min,
                horas_frio=horas_frio,
                gda=gda
            )
            db.session.add(nuevo_registro)
            db.session.commit()
    else:
        temp_max = historial.temp_max
        temp_min = historial.temp_min
        horas_frio = historial.horas_frio
        gda = historial.gda

    return jsonify({
        "temperatura": round(ultima_medicion.temperatura, 2),
        "humedad": round(ultima_medicion.humedad, 2),
        "fecha_hora": ultima_medicion.fecha.strftime('%Y-%m-%d %H:%M:%S'),
        "horas_frio": horas_frio if horas_frio is not None else "--",
        "gda": round(gda, 2) if isinstance(gda, (int, float)) else "--"
    })



