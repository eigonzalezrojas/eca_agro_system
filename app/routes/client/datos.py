from flask import Blueprint, session, jsonify, request
from app.models import Registro, Dispositivo, DataNodoAmbiente, HistorialClima
from datetime import datetime, timedelta
from app.extensions import db
from sqlalchemy import func

datos = Blueprint('datos', __name__)


@datos.route('/', methods=['GET'])
def obtener_datos():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    chipid = request.args.get('chipid')

    if not chipid:
        return jsonify({"error": "Dispositivo no especificado"}), 400

    ultima_medicion = DataNodoAmbiente.query.filter_by(chipid=chipid).order_by(DataNodoAmbiente.fecha.desc()).first()

    if not ultima_medicion:
        return jsonify({"error": "No hay mediciones disponibles para el dispositivo"}), 404

    fecha_ayer = datetime.now().date() - timedelta(days=1)

    historial = HistorialClima.query.filter_by(chipid=chipid, fecha=fecha_ayer).first()

    historial_anterior = HistorialClima.query.filter(
        HistorialClima.chipid == chipid,
        HistorialClima.fecha < fecha_ayer
    ).order_by(HistorialClima.fecha.desc()).first()

    gda_acumulado_anterior = historial_anterior.gda if historial_anterior else 0

    if not historial:
        temp_max = DataNodoAmbiente.query.filter(
            DataNodoAmbiente.chipid == chipid,
            DataNodoAmbiente.fecha.between(fecha_ayer, fecha_ayer + timedelta(days=1))
        ).order_by(DataNodoAmbiente.temperatura.desc()).first()

        temp_min = DataNodoAmbiente.query.filter(
            DataNodoAmbiente.chipid == chipid,
            DataNodoAmbiente.fecha.between(fecha_ayer, fecha_ayer + timedelta(days=1))
        ).order_by(DataNodoAmbiente.temperatura.asc()).first()

        temp_max = temp_max.temperatura if temp_max else None
        temp_min = temp_min.temperatura if temp_min else None

        horas_frio = DataNodoAmbiente.query.filter(
            DataNodoAmbiente.chipid == chipid,
            DataNodoAmbiente.fecha.between(fecha_ayer, fecha_ayer + timedelta(days=1)),
            DataNodoAmbiente.temperatura >= 0,
            DataNodoAmbiente.temperatura <= 7.2
        ).count()

        gda_diario = max(((temp_max + temp_min) / 2) - 10, 0) if temp_max and temp_min else 0
        gda = gda_acumulado_anterior + gda_diario

        if temp_max and temp_min:
            nuevo_registro = HistorialClima(
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

    registro = Registro.query.filter_by(fk_usuario=user_id).first()
    if not registro:
        return jsonify({"error": "No hay dispositivos asociados al usuario"}), 404

    dispositivo = Dispositivo.query.filter_by(id=registro.fk_dispositivo).first()
    if not dispositivo:
        return jsonify({"error": "No se encontró el dispositivo asociado"}), 404

    chipid = dispositivo.chipid
    periodo = request.args.get('periodo')
    fecha = request.args.get('fecha')
    mes = request.args.get('mes')
    anio = request.args.get('anio')

    if not chipid:
        return jsonify({"error": "Debe seleccionar un dispositivo"}), 400

    query = db.session.query(
        func.max(DataNodoAmbiente.temperatura).label('temp_max'),
        func.min(DataNodoAmbiente.temperatura).label('temp_min'),
        func.max(DataNodoAmbiente.humedad).label('hum_max'),
        func.min(DataNodoAmbiente.humedad).label('hum_min')
    ).filter(DataNodoAmbiente.chipid == chipid)

    if periodo == "day" and fecha:
        query = query.filter(func.date(DataNodoAmbiente.fecha) == fecha)

    elif periodo == "month" and mes and anio:
        query = db.session.query(
            func.day(DataNodoAmbiente.fecha).label('dia'),
            func.max(DataNodoAmbiente.temperatura).label('temp_max'),
            func.min(DataNodoAmbiente.temperatura).label('temp_min'),
            func.max(DataNodoAmbiente.humedad).label('hum_max'),
            func.min(DataNodoAmbiente.humedad).label('hum_min')
        ).filter(
            func.year(DataNodoAmbiente.fecha) == anio,
            func.month(DataNodoAmbiente.fecha) == mes
        ).group_by(func.day(DataNodoAmbiente.fecha))

    elif periodo == "year" and anio:
        query = db.session.query(
            func.week(DataNodoAmbiente.fecha).label('semana'),
            func.max(DataNodoAmbiente.temperatura).label('temp_max'),
            func.min(DataNodoAmbiente.temperatura).label('temp_min'),
            func.max(DataNodoAmbiente.humedad).label('hum_max'),
            func.min(DataNodoAmbiente.humedad).label('hum_min')
        ).filter(func.year(DataNodoAmbiente.fecha) == anio).group_by(func.week(DataNodoAmbiente.fecha))

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