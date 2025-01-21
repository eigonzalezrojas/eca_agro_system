from app import db
from datetime import datetime, timezone

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
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    fono = db.Column(db.Integer, nullable=True)
    fk_rol = db.Column(db.Integer, db.ForeignKey('rol.id'), nullable=False)
    rol = db.relationship('Rol', backref='usuarios')

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    fono = db.Column(db.Integer, nullable=True)
    fk_parcela = db.Column(db.Integer, db.ForeignKey('parcela.id'), nullable=True)
    fk_rol = db.Column(db.Integer, db.ForeignKey('rol.id'), nullable=False)
    rol = db.relationship('Rol', backref='clientes')
    parcela = db.relationship('Parcela', backref='clientes')

class Parcela(db.Model):
    __tablename__ = 'parcela'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    comuna = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=True)
    fk_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)

class Cultivo(db.Model):
    __tablename__ = 'cultivo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    variedad = db.Column(db.String(50), nullable=True)
    fase = db.Column(db.String(50), nullable=True)
    fk_dispositivo = db.Column(db.Integer, db.ForeignKey('dispositivo.id'), nullable=False)
    fk_parcela = db.Column(db.Integer, db.ForeignKey('parcela.id'), nullable=False)

class Dispositivo(db.Model):
    __tablename__ = 'dispositivo'
    id = db.Column(db.Integer, primary_key=True)
    chipid = db.Column(db.String(50), unique=True, nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    caracteristica = db.Column(db.String(100), nullable=True)
    fecha = db.Column(db.Date, nullable=True)

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