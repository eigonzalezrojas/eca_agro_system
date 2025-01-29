from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import Usuario, Rol
from app import db
import random, string
from app.services.email_service import enviar_correo
from app.services.whatssap_service import enviar_whatsapp

user = Blueprint('user', __name__)

@user.route('/usuarios')
def usuarios():
    usuarios = Usuario.query.all()
    roles = Rol.query.all()
    return render_template('sections/admin/usuarios.html', usuarios=usuarios, roles=roles)

@user.route('/usuarios/crear', methods=['POST'])
def crear_usuario():
    rut = request.form['rut']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    fono = request.form['fono']
    correo = request.form['correo']
    rol_id = request.form['rol']

    # Generar contraseña aleatoria
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    # Crear el usuario
    nuevo_usuario = Usuario(
        rut=rut,
        nombre=nombre,
        apellido=apellido,
        fono=fono,
        correo=correo,
        fk_rol=rol_id
    )
    nuevo_usuario.set_password(password)
    db.session.add(nuevo_usuario)
    db.session.commit()

    # Enviar la contraseña por correo
    enviar_correo(
        destinatario=correo,
        asunto="Bienvenido a ECA Innovation",
        mensaje=f"Hola {nombre},\n\nTu cuenta ha sido creada exitosamente. Tu contraseña provisoria es: {password}\n\nPor favor, cámbiala en tu perfil."
    )

    # Enviar la contraseña por WhatsApp
    enviar_whatsapp(
        to=fono,
        message=f"Hola {nombre}, tu cuenta ha sido creada exitosamente. Tu contraseña provisoria es: {password}. Por favor, cámbiala en tu perfil."
    )

    flash('Usuario creado exitosamente. Se envió la contraseña por correo y WhatsApp.', 'success')
    return redirect(url_for('user.usuarios'))

@user.route('/usuarios/editar/<rut>', methods=['POST'])
def editar_usuario(rut):
    usuario = Usuario.query.get_or_404(rut)
    usuario.nombre = request.form['nombre']
    usuario.apellido = request.form['apellido']
    usuario.fono = request.form['fono']
    usuario.correo = request.form['correo']
    usuario.fk_rol = request.form['fk_rol']

    db.session.commit()
    flash('Usuario actualizado exitosamente', 'success')
    return redirect(url_for('user.usuarios'))

@user.route('/usuarios/eliminar/<rut>', methods=['POST'])
def eliminar_usuario(rut):
    usuario = Usuario.query.get_or_404(rut)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado exitosamente', 'success')
    return redirect(url_for('user.usuarios'))


@user.route('/usuarios/<rut>', methods=['GET'])
def obtener_usuario(rut):
    usuario = Usuario.query.get_or_404(rut)
    return {
        "rut": usuario.rut,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "fono": usuario.fono,
        "correo": usuario.correo,
        "fk_rol": usuario.fk_rol
    }