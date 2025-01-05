from flask import Blueprint, render_template, jsonify, request
from app.models import NodeTH
from app import db
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def index():
    chipids = db.session.query(NodeTH.chipid).distinct().all()
    chipids = [c[0] for c in chipids if c[0] != 0]

    return render_template('dashboard.html', chipids=chipids)

@main.route('/api/data')
def get_data():
    chipid = request.args.get('chipid', type=int)
    period = request.args.get('period', 'day')

    now = datetime.now()
    if period == 'day':
        start_date = now - timedelta(days=1)
    elif period == 'week':
        start_date = now - timedelta(weeks=1)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    elif period == 'year':
        start_date = now - timedelta(days=365)

    query = NodeTH.query.filter(NodeTH.fecha >= start_date)

    if chipid:
        query = query.filter(NodeTH.chipid == chipid)

    data = query.order_by(NodeTH.fecha).all()

    return jsonify({
        'labels': [d.fecha.strftime('%Y-%m-%d %H:%M:%S') for d in data],
        'temperatura': [d.temperatura for d in data],
        'humedad': [d.humedad for d in data]
    })

@main.route('/latest-data')
def latest_data():
    latest = NodeTH.query.order_by(NodeTH.fecha.desc()).first()
    if latest:
        return jsonify({
            "temperatura": latest.temperatura,
            "humedad": latest.humedad
        })
    else:
        return jsonify({
            "temperatura": None,
            "humedad": None
        })