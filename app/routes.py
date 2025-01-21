from flask import Blueprint, render_template, jsonify, request
from app.models import SensorData
from app import db
from datetime import datetime, timedelta, timezone
from sqlalchemy import Date, cast, func

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/inicio')
def inicio():
    chipids = db.session.query(SensorData.chipid).distinct().all()
    chipids = [c[0] for c in chipids if c[0] != 0]

    return render_template('inicio.html', chipids=chipids)

@main.route('/temperatura')
def temperatura():
    return render_template('temperatura.html')

@main.route('/humedad')
def humedad():
    return render_template('humedad.html')

@main.route('/viento')
def viento():
    return render_template('viento.html')

@main.route('/alertas')
def alertas():
    return render_template('alertas.html')

@main.route('/api/data')
def get_data():
    period = request.args.get('period', 'day')
    chipid = request.args.get('chipid')
    custom_date = request.args.get('date')
    custom_month = request.args.get('month')
    now = datetime.now()

    if period == 'day':
        start_date = now - timedelta(days=1)
        group_by = func.date_format(SensorData.fecha, '%Y-%m-%d %H:00')
    elif period == 'week':
        start_date = now - timedelta(weeks=1)
        group_by = func.date_format(SensorData.fecha, '%Y-%m-%d')
    elif period == 'month' and custom_month:        
        try:
            year, month = custom_month.split('-')
            start_date = datetime(int(year), int(month), 1)            
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1)
            else:
                end_date = datetime(int(year), int(month) + 1, 1)
            group_by = func.date_format(SensorData.fecha, '%Y-%m-%d')
        except (ValueError, AttributeError):
            return jsonify({'error': 'Invalid month format. Use YYYY-MM'}), 400
    elif period == 'custom' and custom_date:
        start_date = datetime.strptime(custom_date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=1)
        group_by = func.date_format(SensorData.fecha, '%Y-%m-%d %H:00')
    else:
        return jsonify({'error': 'Invalid period or missing date/month'}), 400

    query = db.session.query(
        group_by.label('group'),
        SensorData.chipid,
        func.max(SensorData.temperatura).label('max_temp'),
        func.min(SensorData.temperatura).label('min_temp'),
        func.max(SensorData.humedad).label('max_hum'),
        func.min(SensorData.humedad).label('min_hum')
    )
    
    if period == 'month' and custom_month:
        query = query.filter(SensorData.fecha >= start_date, SensorData.fecha < end_date)
    else:
        query = query.filter(SensorData.fecha >= start_date)
        if period == 'custom' and (custom_date or custom_month):
            query = query.filter(SensorData.fecha < end_date)

    if chipid:
        query = query.filter(SensorData.chipid == chipid)

    query = query.group_by('group', SensorData.chipid).order_by('group')

    data = query.all()
    result = {}
    for d in data:
        if d.chipid not in result:
            result[d.chipid] = {
                'labels': [],
                'max_temp': [],
                'min_temp': [],
                'max_hum': [],
                'min_hum': []
            }
        result[d.chipid]['labels'].append(d.group)
        result[d.chipid]['max_temp'].append(float(d.max_temp))
        result[d.chipid]['min_temp'].append(float(d.min_temp))
        result[d.chipid]['max_hum'].append(float(d.max_hum))
        result[d.chipid]['min_hum'].append(float(d.min_hum))

    return jsonify(result)

@main.route('/api/years')
def get_years():
    try:        
        start_year = 2024        
        current_year = datetime.now().year        
        years = list(range(start_year, current_year + 1))

        return jsonify(years)
    except Exception as e:
        print(f"Error al obtener años: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main.route('/latest-data')
def latest_data():
    latest = SensorData.query.order_by(SensorData.fecha.desc()).first()
    if latest:
        response_data = {
            "temperatura": float(latest.temperatura),
            "humedad": float(latest.humedad),
            "fecha_hora": latest.fecha.strftime('%Y-%m-%d %H:%M:%S')
        }
        return jsonify(response_data)
    else:
        return jsonify({
            "temperatura": None,
            "humedad": None,
            "fecha_hora": None
        })

@main.route('/api/horas-frio', methods=['GET'])
def calcular_horas_frio():
    try:
        chile_tz = timezone(timedelta(hours=-3))

        ahora = datetime.now(chile_tz)
        hace_24_horas = ahora - timedelta(hours=24)

        horas_frio = (
            db.session.query(func.count(SensorData.id))
            .filter(
                SensorData.temperatura >= 0,
                SensorData.temperatura <= 7.2,
                SensorData.fecha >= hace_24_horas,
                SensorData.fecha <= ahora,
                SensorData.chipid != 48
            )
            .scalar()
        )

        return jsonify({
            "horas_frio": horas_frio,
            "periodo": {
                "inicio": hace_24_horas.isoformat(),
                "fin": ahora.isoformat()
            }
        })

    except Exception as e:
        print(f"Error en calcular_horas_frio: {str(e)}")
        return jsonify({
            "error": str(e),
            "mensaje": "Error al calcular las horas frío"
        }), 500

@main.route('/api/gda', methods=['GET'])
def calcular_gda():
    try:
        chile_tz = timezone(timedelta(hours=-3))
        
        temp_base = float(request.args.get('temp_base', 10))
        dias = int(request.args.get('dias', 7))

        ahora = datetime.now(chile_tz)
        inicio_periodo = ahora - timedelta(days=dias)

        resultados = (
            db.session.query(
                cast(SensorData.fecha, Date).label('fecha'),
                func.max(SensorData.temperatura).label('temp_max'),
                func.min(SensorData.temperatura).label('temp_min')
            )
            .filter(
                SensorData.fecha >= inicio_periodo,
                SensorData.fecha <= ahora,
                SensorData.chipid != 48
            )
            .group_by(cast(SensorData.fecha, Date))
            .order_by(cast(SensorData.fecha, Date))
            .all()
        )

        gda_diarios = []
        gda_acumulado = 0

        for resultado in resultados:
            temp_media = (resultado.temp_max + resultado.temp_min) / 2
            gda_dia = max(0, temp_media - temp_base)
            gda_acumulado += gda_dia

            gda_diarios.append({
                'fecha': resultado.fecha.isoformat(),
                'temp_max': round(resultado.temp_max, 1),
                'temp_min': round(resultado.temp_min, 1),
                'temp_media': round(temp_media, 1),
                'gda_dia': round(gda_dia, 1)
            })

        respuesta = {
            'gda_acumulado': round(gda_acumulado, 1),
            'temp_base': temp_base,
            'periodo': {
                'inicio': inicio_periodo.isoformat(),
                'fin': ahora.isoformat(),
                'dias': dias
            },
            'detalle_diario': gda_diarios
        }

        return jsonify(respuesta)

    except Exception as e:
        print(f"Error en calcular_gda: {str(e)}")
        return jsonify({
            "error": str(e),
            "mensaje": "Error al calcular los GDA"
        }), 500