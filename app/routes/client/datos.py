from flask import Blueprint, session, jsonify, request
from app.models import Registro, Dispositivo, DataP0, HistorialClima
from datetime import datetime, timedelta
from app.extensions import db
from sqlalchemy import func

datos = Blueprint('datos', __name__)


@datos.route('/')
def obtener_datos():
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

    # btener el GDA acumulado del día anterior
    historial_anterior = HistorialClima.query.filter_by(rut=user_id, chipid=chipid, fecha=fecha_ayer - timedelta(days=1)).first()
    gda_acumulado_anterior = historial_anterior.gda if historial_anterior else 0

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

        #Calcular GDA: sumar el GDA diario al acumulado del día anterior
        gda_diario = max(((temp_max + temp_min) / 2) - 10, 0) if temp_max and temp_min else 0
        gda = gda_acumulado_anterior + gda_diario  # Suma al acumulado

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



@datos.route('/resumen', methods=['GET'])
def obtener_resumen():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    chipid = request.args.get('chipid')
    periodo = request.args.get('periodo')
    fecha = request.args.get('fecha')
    mes = request.args.get('mes')
    anio = request.args.get('anio')

    #Validación
    if not chipid:
        return jsonify({"error": "Debe seleccionar un dispositivo"}), 400

    query = db.session.query(
        func.max(DataP0.temperatura).label('temp_max'),
        func.min(DataP0.temperatura).label('temp_min'),
        func.max(DataP0.humedad).label('hum_max'),
        func.min(DataP0.humedad).label('hum_min')
    ).filter(DataP0.chipid == chipid)

    if periodo == "day" and fecha:
        query = query.filter(func.date(DataP0.fecha) == fecha)

    elif periodo == "month" and mes and anio:
        query = db.session.query(
            func.day(DataP0.fecha).label('dia'),
            func.max(DataP0.temperatura).label('temp_max'),
            func.min(DataP0.temperatura).label('temp_min'),
            func.max(DataP0.humedad).label('hum_max'),
            func.min(DataP0.humedad).label('hum_min')
        ).filter(
            func.year(DataP0.fecha) == anio,
            func.month(DataP0.fecha) == mes
        ).group_by(func.day(DataP0.fecha))

    elif periodo == "year" and anio:
        query = db.session.query(
            func.week(DataP0.fecha).label('semana'),
            func.max(DataP0.temperatura).label('temp_max'),
            func.min(DataP0.temperatura).label('temp_min'),
            func.max(DataP0.humedad).label('hum_max'),
            func.min(DataP0.humedad).label('hum_min')
        ).filter(func.year(DataP0.fecha) == anio).group_by(func.week(DataP0.fecha))

    else:
        return jsonify({"error": "Parámetros inválidos o incompletos"}), 400

    resultados = query.all()

    datos = []
    for res in resultados:
        label = str(fecha) if periodo == "day" else f"Día {res.dia}" if periodo == "month" else f"Semana {res.semana}"

        datos.append({
            "periodo": label,
            "temp_max": getattr(res, "temp_max", "--"),
            "temp_min": getattr(res, "temp_min", "--"),
            "hum_max": getattr(res, "hum_max", "--"),
            "hum_min": getattr(res, "hum_min", "--")
        })

    return jsonify(datos)

