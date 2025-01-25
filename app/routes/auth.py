from flask import Blueprint, request, flash, redirect, url_for, session, render_template
from app.models import db, Usuario
from app.services.password_service import generar_password
from app.services.email_service import enviar_correo
from app.services.whatssap_service import enviar_whatsapp

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
        correo = request.form.get('correo')
        password = request.form.get('password')

        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario and usuario.check_password(password):
            session['user_id'] = usuario.id
            session['user_role'] = usuario.fk_rol
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')

    return render_template('auth/login.html')