from app import db
from datetime import datetime, timezone

class NodeTH(db.Model):
    __tablename__ = 'nodeTH'

    id = db.Column(db.Integer, primary_key=True)
    chipid = db.Column(db.Integer)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    temperatura = db.Column(db.Float)
    humedad = db.Column(db.Float)