from flask import Blueprint, request, flash, redirect, url_for, session, render_template
from werkzeug.security import check_password_hash
from app.extensions import db
from app.models import Usuario, Cliente
from app.services.password_service import generar_password
from app.services.email_service import enviar_correo
from app.services.whatssap_service import enviar_whatsapp
import bcrypt

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    rut = request.form.get('rut')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    correo = request.form.get('correo')
    fono = request.form.get('fono')
    fk_rol = request.form.get('fk_rol')

    password_provisoria = generar_password()

    nuevo_usuario = Usuario(
        rut=rut,
        nombre=nombre,
        apellido=apellido,
        correo=correo,
        fono=fono,
        fk_rol=fk_rol
    )
    nuevo_usuario.set_password(password_provisoria)
    db.session.add(nuevo_usuario)
    db.session.commit()

    asunto = "Tu password provisoria"
    mensaje = f"Hola {nombre}, tu password provisoria es: {password_provisoria}"
    enviar_correo(correo, asunto, mensaje)

    if fono:
        enviar_whatsapp(fono, mensaje)

    flash('Usuario creado y password enviada', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        rut = request.form.get('rut')
        password = request.form.get('password')

        usuario = Usuario.query.filter_by(rut=rut).first()
        if not usuario:
            usuario = Cliente.query.filter_by(rut=rut).first()

        if usuario and bcrypt.checkpw(password.encode('utf-8'), usuario.password_hash.encode('utf-8')):
            session['user_id'] = usuario.rut

            if isinstance(usuario, Usuario):
                if usuario.fk_rol == 1:
                    session['user_role'] = 'admin'
                    flash('Inicio de sesión como Administrador', 'success')
                    return redirect(url_for('dashboard.admin'))
                elif usuario.fk_rol == 3:
                    session['user_role'] = 'visita'
                    flash('Inicio de sesión como Visita', 'success')
                    return redirect(url_for('dashboard.visita'))
            elif isinstance(usuario, Cliente):
                session['user_role'] = 'cliente'
                flash('Inicio de sesión como Cliente', 'success')
                return redirect(url_for('dashboard.client'))

            flash('Rol no reconocido', 'danger')
            return redirect(url_for('auth.login'))
        else:
            flash('RUT o contraseña incorrectos', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')