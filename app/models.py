from datetime import datetime, timezone
from app.extensions import db
import bcrypt


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
        """Hash de la contraseña usando bcrypt."""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Verifica la contraseña usando bcrypt."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


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
    fase = db.Column(db.String(100), nullable=False)
    detalle = db.Column(db.String(200), nullable=True)


class Dispositivo(db.Model):
    __tablename__ = 'dispositivo'
    id = db.Column(db.Integer, primary_key=True)
    chipid = db.Column(db.String(50), unique=True, nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    caracteristica = db.Column(db.String(100), nullable=True)
    fecha = db.Column(db.Date, nullable=True)


class Registro(db.Model):
    __tablename__ = 'registro'

    id = db.Column(db.Integer, primary_key=True)
    fk_dispositivo = db.Column(db.Integer, db.ForeignKey('dispositivo.id'), nullable=False)
    fk_cultivo = db.Column(db.Integer, db.ForeignKey('cultivo.id'), nullable=False)
    fk_cultivo_fase = db.Column(db.String(100), nullable=False)
    fk_parcela = db.Column(db.Integer, db.ForeignKey('parcela.id'), nullable=False)
    fk_usuario = db.Column(db.String(50), db.ForeignKey('usuario.rut'), nullable=False)
    fuente = db.Column(db.String(50), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())

    dispositivo = db.relationship('Dispositivo', backref='registros')
    cultivo = db.relationship('Cultivo', backref='registros')
    parcela = db.relationship('Parcela', backref='registros')
    usuario = db.relationship('Usuario', backref='registros')

    def __repr__(self):
        return f'<Registro {self.id}>'



class DataP0(db.Model):
    __tablename__ = 'dataP0'
    id = db.Column(db.Integer, primary_key=True)
    chipid = db.Column(db.String(50), unique=True, nullable=False)
    fecha = db.Column(db.Date, nullable=True)
    temperatura = db.Column(db.Float, nullable=True)
    humedad = db.Column(db.Float, nullable=True)
    nombre = db.Column(db.String(50), nullable=True)


class HistorialClima(db.Model):
    __tablename__ = 'historialClima'
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(15), nullable=False)
    chipid = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date, nullable=False, unique=True)
    temp_max = db.Column(db.Float, nullable=False)
    temp_min = db.Column(db.Float, nullable=False)
    horas_frio = db.Column(db.Float, nullable=False)
    gda = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<HistorialClima {self.fecha} - ChipID {self.chipid}>"


from app.extensions import db

class Alerta(db.Model):
    __tablename__ = 'alerta'

    id = db.Column(db.Integer, primary_key=True)
    mensaje = db.Column(db.String(255), nullable=False)
    fk_dispositivo = db.Column(db.Integer, db.ForeignKey('dispositivo.id'), nullable=False)
    fk_cultivo = db.Column(db.Integer, db.ForeignKey('cultivo.id'), nullable=False)
    fk_cultivo_fase = db.Column(db.String(100), nullable=False)
    fecha_alerta = db.Column(db.DateTime, default=db.func.current_timestamp())
    nivel_alerta = db.Column(db.String(50), nullable=True)

    dispositivo = db.relationship('Dispositivo', backref=db.backref('alertas', lazy=True))
    cultivo = db.relationship('Cultivo', backref=db.backref('alertas', lazy=True))

    def __repr__(self):
        return f'<Alerta {self.id}, Cultivo {self.fk_cultivo}, Fase {self.fk_cultivo_fase}>'
