from app.extensions import db
import bcrypt


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
    mis_registros = db.relationship('Registro', back_populates='parcela', cascade="all, delete-orphan")


class Cultivo(db.Model):
    __tablename__ = 'cultivo'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    variedad = db.Column(db.String(50), nullable=False)
    detalle = db.Column(db.String(200), nullable=True)


class Fase(db.Model):
    __tablename__ = 'fase'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    cultivo = db.Column(db.String(50), nullable=False)


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
    fk_usuario = db.Column(db.String(50), db.ForeignKey('usuario.rut'), nullable=False)
    fk_parcela = db.Column(db.Integer, db.ForeignKey('parcela.id', ondelete="CASCADE"), nullable=False)
    fk_fase = db.Column(db.Integer, db.ForeignKey('fase.id'), nullable=False)
    fk_dispositivo = db.Column(db.Integer, db.ForeignKey('dispositivo.id'), nullable=False)
    cultivo_nombre = db.Column(db.String(50), nullable=False)
    cultivo_variedad = db.Column(db.String(50), nullable=False)
    fase_nombre = db.Column(db.String(50), nullable=False)
    fuente = db.Column(db.String(50), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())

    dispositivo = db.relationship('Dispositivo', backref='registros')
    fase = db.relationship('Fase', backref='registros')
    parcela = db.relationship('Parcela', back_populates='mis_registros')
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


class DataNodoAmbiente(db.Model):
    __tablename__ = 'dataNodoAmbiente'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chipid = db.Column(db.String(16), nullable=False)
    temperatura = db.Column(db.Float, nullable=False)
    humedad = db.Column(db.Float, nullable=False)
    presion = db.Column(db.Float, nullable=False)
    altitud = db.Column(db.Float, nullable=False)
    bateria = db.Column(db.Float, nullable=False)
    nombre = db.Column(db.String(30), nullable=False)
    fecha = db.Column(db.TIMESTAMP, nullable=False)

    def __repr__(self):
        return f'<DataNodoAmbiente {self.chipid} - {self.fecha}>'


class HistorialClima(db.Model):
    __tablename__ = 'historialClima'
    id = db.Column(db.Integer, primary_key=True)
    chipid = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.Date, nullable=False, unique=True)
    temp_max = db.Column(db.Float, nullable=False)
    temp_min = db.Column(db.Float, nullable=False)
    horas_frio = db.Column(db.Float, nullable=False)
    gda = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<HistorialClima {self.fecha} - ChipID {self.chipid}>"


class Alerta(db.Model):
    __tablename__ = 'alerta'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mensaje = db.Column(db.String(255), nullable=False)
    fk_dispositivo = db.Column(db.Integer, db.ForeignKey('dispositivo.id'), nullable=False)
    fk_fase = db.Column(db.Integer, db.ForeignKey('fase.id'), nullable=False)
    cultivo_nombre = db.Column(db.String(50), nullable=False)
    fecha_alerta = db.Column(db.DateTime, default=db.func.current_timestamp())
    nivel_alerta = db.Column(db.String(50), nullable=True)
    leida = db.Column(db.Boolean, default=False)

    dispositivo = db.relationship('Dispositivo', backref=db.backref('alertas', lazy=True))
    fase = db.relationship('Fase', backref=db.backref('alertas', lazy=True))

    def __repr__(self):
        return f'<Alerta {self.id}, Fase {self.fk_fase}, Cultivo {self.cultivo_nombre}>'


