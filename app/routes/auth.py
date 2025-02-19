from flask import Blueprint, request, flash, redirect, url_for, session, render_template, jsonify
from app.services.email_service import enviar_recuperar_clave
from app.models import Usuario
from app.extensions import db
import bcrypt
import random
import string

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtener los datos del formulario
        rut = request.form.get('rut')
        password = request.form.get('password')

        # Buscar al usuario en la tabla `usuario`
        usuario = Usuario.query.filter_by(rut=rut).first()

        # Verificar si el usuario existe y la contraseña es correcta
        if usuario and bcrypt.checkpw(password.encode('utf-8'), usuario.password_hash.encode('utf-8')):
            session['user_id'] = usuario.rut

            if isinstance(usuario, Usuario):
                if usuario.fk_rol == 1:
                    session['user_role'] = 'admin'
                    return redirect(url_for('dashboard.admin'))
                elif usuario.fk_rol == 2:
                    session['user_role'] = 'cliente'
                    return redirect(url_for('dashboard.client'))
                elif usuario.fk_rol == 3:
                    session['user_role'] = 'visita'
                    return redirect(url_for('dashboard.guest'))

            flash('Rol no reconocido', 'danger')
            return redirect(url_for('auth.login'))
        else:
            flash('RUT o contraseña incorrectos', 'danger')
            return redirect(url_for('auth.login'))

    # Renderizar la página de inicio de sesión
    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)

    # Elimina la cookie de sesión
    response = redirect(url_for('auth.login'))
    response.set_cookie('session', '', expires=0)

    flash('¡Has cerrado sesión exitosamente!', 'success')

    return response


@auth.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """Página para cambiar la contraseña"""
    if request.method == 'GET':
        return render_template('auth/change_password.html')

    # Procesar el formulario
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "Usuario no autenticado"}), 401

    usuario = Usuario.query.filter_by(rut=user_id).first()

    if not usuario or not bcrypt.checkpw(old_password.encode('utf-8'), usuario.password_hash.encode('utf-8')):
        return jsonify({"success": False, "error": "Contraseña actual incorrecta"})

    # Actualizar la contraseña
    usuario.set_password(new_password)
    from app.extensions import db
    db.session.commit()

    # Cerrar la sesión después del cambio
    session.pop('user_id', None)
    session.pop('user_role', None)

    return jsonify({"success": True})


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Página para solicitar recuperación de contraseña"""
    if request.method == 'GET':
        return render_template('auth/forgot_password.html')

    # Obtener el RUT desde el formulario
    rut = request.form.get('rut')
    if not rut:
        flash('⚠️ El campo RUT es obligatorio.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    # Buscar usuario por RUT
    usuario = Usuario.query.filter_by(rut=rut).first()
    if not usuario:
        flash('❗ No existe un usuario registrado con ese RUT.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    # Generar contraseña temporal
    password_temporal = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    usuario.set_password(password_temporal)  # Actualizar la contraseña con bcrypt

    db.session.commit()

    # Enviar el correo con la contraseña temporal
    correo = usuario.correo
    asunto = "🔑 Recuperación de Contraseña - ECA Innovation"
    mensaje = f"""
    Estimado(a) {usuario.nombre} {usuario.apellido},

    Se ha solicitado la recuperación de contraseña para su cuenta asociada al RUT {usuario.rut}.

    🔒 Su nueva contraseña temporal es: {password_temporal}

    Por motivos de seguridad, le recomendamos cambiar esta contraseña temporal una vez haya iniciado sesión.

    Saludos cordiales,  
    Equipo de ECA Innovation
    """
    enviar_recuperar_clave(correo, asunto, mensaje)

    flash('✅ Se ha enviado una contraseña temporal al correo registrado.', 'success')
    return redirect(url_for('auth.login'))

