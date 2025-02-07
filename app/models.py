from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class SensorData(db.Model):
    __tablename__ = 'sensorData'
    id = db.Column(db.Integer, primary_key=True)
    chipid = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    temperatura = db.Column(db.Float, nullable=False)
    humedad = db.Column(db.Float, nullable=False)
    bateria = db.Column(db.Float, nullable=True)


class Rol(db.Model):
    __tablename__ = 'rol'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    usuarios = db.relationship('Usuario', back_populates='rol')


class Usuario(db.Model):
    __tablename__ = 'usuario'
    rut = db.Column(db.String(50), primary_key=True)
    nombre = db.Column(db.String(100), nullable=True)
    apellido = db.Column(db.String(100), nullable=True)
    correo = db.Column(db.String(100), unique=True, nullable=True)
    fono = db.Column(db.String(15), nullable=True)
    fk_rol = db.Column(db.Integer, db.ForeignKey('rol.id'), nullable=True)
    rol = db.relationship('Rol', back_populates='usuarios')
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    parcelas = db.relationship('Parcela', back_populates='usuario', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Parcela(db.Model):
    __tablename__ = 'parcela'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    comuna = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=True)
    fk_usuario = db.Column(db.String(50), db.ForeignKey('usuario.rut'), nullable=False)
    usuario = db.relationship('Usuario', back_populates='parcelas')


class Cultivo(db.Model):
    __tablename__ = 'cultivo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    variedad = db.Column(db.String(50), nullable=False)
    detalle = db.Column(db.String(200), nullable=True)


class Dispositivo(db.Model):
    __tablename__ = 'dispositivo'
    id = db.Column(db.Integer, primary_key=True)
    chipid = db.Column(db.String(50), unique=True, nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    caracteristica = db.Column(db.String(100), nullable=True)
    fecha = db.Column(db.Date, nullable=True)

