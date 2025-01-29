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


class Usuario(db.Model):
    __tablename__ = 'usuario'
    rut = db.Column(db.String(50), primary_key=True)
    nombre = db.Column(db.String(100), nullable=True)
    apellido = db.Column(db.String(100), nullable=True)
    correo = db.Column(db.String(100), unique=True, nullable=True)
    fono = db.Column(db.String(15), nullable=True)
    fk_rol = db.Column(db.Integer, db.ForeignKey('rol.id'), nullable=True)
    rol = db.relationship('Rol', backref='usuarios')
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

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
    usuario = db.relationship('Usuario')
    cultivos = db.relationship('Cultivo', back_populates='parcela', cascade='all, delete-orphan')


class Cultivo(db.Model):
    __tablename__ = 'cultivo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    variedad = db.Column(db.String(50), nullable=True)
    fase = db.Column(db.String(50), nullable=True)
    fk_parcela = db.Column(db.Integer, db.ForeignKey('parcela.id'), nullable=False)
    parcela = db.relationship('Parcela', back_populates='cultivos')
    dispositivos = db.relationship('Dispositivo', back_populates='cultivo', cascade='all, delete-orphan')


class Dispositivo(db.Model):
    __tablename__ = 'dispositivo'
    id = db.Column(db.Integer, primary_key=True)
    chipid = db.Column(db.String(50), unique=True, nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    caracteristica = db.Column(db.String(100), nullable=True)
    fecha = db.Column(db.Date, nullable=True)
    fk_cultivo = db.Column(db.Integer, db.ForeignKey('cultivo.id'), nullable=False)
    cultivo = db.relationship('Cultivo', back_populates='dispositivos')

class Registro(db.Model):
    __tablename__ = 'registro'
    id = db.Column(db.Integer, primary_key=True)
    fk_dispositivo = db.Column(db.Integer, db.ForeignKey('dispositivo.id'), nullable=False)
    temperatura = db.Column(db.Float, nullable=True)
    horas_frio = db.Column(db.Float, nullable=True)
    horas_dia = db.Column(db.Float, nullable=True)
    radiacion = db.Column(db.Float, nullable=True)
    humedad = db.Column(db.Float, nullable=True)
    viento = db.Column(db.Float, nullable=True)
    fecha = db.Column(db.Date, nullable=False)

class Alerta(db.Model):
    __tablename__ = 'alerta'
    id = db.Column(db.Integer, primary_key=True)
    info = db.Column(db.String(200), nullable=False)
    fk_dispositivo = db.Column(db.Integer, db.ForeignKey('dispositivo.id'), nullable=False)