from app import db
from datetime import datetime

class NodeTH(db.Model):
    __tablename__ = 'nodeTH'

    id = db.Column(db.Integer, primary_key=True)
    chipid = db.Column(db.Integer)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    temperatura = db.Column(db.Float)
    humedad = db.Column(db.Float)