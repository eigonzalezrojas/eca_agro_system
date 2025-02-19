from flask import Blueprint, request, flash, redirect, url_for, session, render_template, jsonify
from app.models import Usuario
import bcrypt

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
    """ Cierra la sesión del usuario """
    session.pop('user_id', None)
    session.pop('user_role', None)

    flash("Has cerrado sesión exitosamente.", "success")
    return redirect(url_for('auth.login'))


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
