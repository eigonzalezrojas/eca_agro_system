from flask import Blueprint, render_template, jsonify, request
from app.models import NodeTH
from app import db
from datetime import datetime, timedelta, timezone
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/inicio')
def inicio():
    chipids = db.session.query(NodeTH.chipid).distinct().all()
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
        group_by = func.date_format(NodeTH.fecha, '%Y-%m-%d %H:00')
    elif period == 'week':
        start_date = now - timedelta(weeks=1)
        group_by = func.date_format(NodeTH.fecha, '%Y-%m-%d')
    elif period == 'month' and custom_month:        
        try:
            year, month = custom_month.split('-')
            start_date = datetime(int(year), int(month), 1)            
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1)
            else:
                end_date = datetime(int(year), int(month) + 1, 1)
            group_by = func.date_format(NodeTH.fecha, '%Y-%m-%d')
        except (ValueError, AttributeError):
            return jsonify({'error': 'Invalid month format. Use YYYY-MM'}), 400
    elif period == 'custom' and custom_date:
        start_date = datetime.strptime(custom_date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=1)
        group_by = func.date_format(NodeTH.fecha, '%Y-%m-%d %H:00')
    else:
        return jsonify({'error': 'Invalid period or missing date/month'}), 400

    query = db.session.query(
        group_by.label('group'),
        NodeTH.chipid,
        func.max(NodeTH.temperatura).label('max_temp'),
        func.min(NodeTH.temperatura).label('min_temp'),
        func.max(NodeTH.humedad).label('max_hum'),
        func.min(NodeTH.humedad).label('min_hum')
    )
    
    if period == 'month' and custom_month:
        query = query.filter(NodeTH.fecha >= start_date, NodeTH.fecha < end_date)
    else:
        query = query.filter(NodeTH.fecha >= start_date)
        if period == 'custom' and (custom_date or custom_month):
            query = query.filter(NodeTH.fecha < end_date)

    if chipid:
        query = query.filter(NodeTH.chipid == chipid)

    query = query.group_by('group', NodeTH.chipid).order_by('group')

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
    latest = NodeTH.query.order_by(NodeTH.fecha.desc()).first()
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
            db.session.query(func.count(NodeTH.id))
            .filter(
                NodeTH.temperatura >= 0,
                NodeTH.temperatura <= 7.2,
                NodeTH.fecha >= hace_24_horas,
                NodeTH.fecha <= ahora,
                NodeTH.chipid != 48
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