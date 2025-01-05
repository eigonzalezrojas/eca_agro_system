from flask import Blueprint, render_template, jsonify, request
from app.models import NodeTH
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/')
def index():
    chipids = db.session.query(NodeTH.chipid).distinct().all()
    chipids = [c[0] for c in chipids if c[0] != 0]

    return render_template('dashboard.html', chipids=chipids)

@main.route('/api/data')
def get_data():
    period = request.args.get('period', 'day')
    chipid = request.args.get('chipid')
    custom_date = request.args.get('date')  # Para el período "custom"
    custom_month = request.args.get('month')  # Para el período "month"
    now = datetime.now()

    if period == 'day':
        start_date = now - timedelta(days=1)
        group_by = func.date_format(NodeTH.fecha, '%Y-%m-%d %H:00')
    elif period == 'week':
        start_date = now - timedelta(weeks=1)
        group_by = func.date_format(NodeTH.fecha, '%Y-%m-%d')
    elif period == 'month':
        start_date = now.replace(day=1)
        group_by = func.date_format(NodeTH.fecha, '%Y-%m-%d')
    elif period == 'custom' and custom_date:
        start_date = datetime.strptime(custom_date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=1)
        group_by = func.date_format(NodeTH.fecha, '%Y-%m-%d %H:00')
    elif period == 'custom' and custom_month:
        start_date = datetime.strptime(custom_month, '%Y-%m')
        end_date = (start_date + timedelta(days=31)).replace(day=1)
        group_by = func.date_format(NodeTH.fecha, '%Y-%m-%d')
    else:
        return jsonify({'error': 'Invalid period'}), 400

    query = db.session.query(
        group_by.label('group'),
        NodeTH.chipid,
        func.max(NodeTH.temperatura).label('max_temp'),
        func.min(NodeTH.temperatura).label('min_temp'),
        func.max(NodeTH.humedad).label('max_hum'),
        func.min(NodeTH.humedad).label('min_hum')
    ).filter(NodeTH.fecha >= start_date)

    if chipid:
        query = query.filter(NodeTH.chipid == chipid)

    if period == 'custom' and custom_date:
        query = query.filter(NodeTH.fecha < end_date)
    elif period == 'custom' and custom_month:
        query = query.filter(NodeTH.fecha < end_date)

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

@main.route('/latest-data')
def latest_data():
    latest = NodeTH.query.order_by(NodeTH.fecha.desc()).first()
    print("Último registro encontrado:", latest)  # Para debugging
    if latest:
        response_data = {
            "temperatura": float(latest.temperatura),  # Convertir a float para asegurar serialización
            "humedad": float(latest.humedad),
            "fecha_hora": latest.fecha.strftime('%Y-%m-%d %H:%M:%S')
        }
        print("Datos a enviar:", response_data)  # Para debugging
        return jsonify(response_data)
    else:
        print("No se encontraron registros")  # Para debugging
        return jsonify({
            "temperatura": None,
            "humedad": None,
            "fecha_hora": None
        })