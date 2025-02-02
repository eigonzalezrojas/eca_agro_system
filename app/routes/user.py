from itertools import cycle
from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import Usuario, Rol
from app.extensions import db
import random, string
import re
from app.services.email_service import enviar_correo_bienvenida

user = Blueprint('user', __name__)

@user.route('/usuarios')
def usuarios():
    usuarios = Usuario.query.all()
    roles = Rol.query.all()
    return render_template('sections/admin/usuarios.html', usuarios=usuarios, roles=roles)


def validar_rut(rut):
    """Valida el RUT chileno """
    rut = rut.upper().replace("-", "").replace(".", "")
    rut_aux = rut[:-1]
    dv = rut[-1:]

    if not rut_aux.isdigit() or not (1_000_000 <= int(rut_aux) <= 25_000_000):
        return False

    revertido = map(int, reversed(rut_aux))
    factors = cycle(range(2, 8))
    suma = sum(d * f for d, f in zip(revertido, factors))
    residuo = suma % 11

    if dv == 'K':
        return residuo == 1
    if dv == '0':
        return residuo == 11
    return residuo == 11 - int(dv)


def validar_correo(correo):
    """Valida el formato del correo electrónico"""
    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(patron, correo))


def validar_telefono(telefono):
    """Valida un número de teléfono formato de 9 dígitos """
    patron = r'^\d{9}$'
    return bool(re.match(patron, telefono))


@user.route('/usuarios/crear', methods=['POST'])
def crear_usuario():
    rut = request.form['rut']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    fono = request.form['fono']
    correo = request.form['correo']
    rol_id = request.form['rol']

    errores = []

    # Validar RUT
    if not rut or not validar_rut(rut):
        errores.append("El RUT es inválido o no está completo.")

    # Validar nombre
    if not nombre:
        errores.append("El nombre es obligatorio.")

    # Validar apellido
    if not apellido:
        errores.append("El apellido es obligatorio.")

    # Validar teléfono
    if not fono or not validar_telefono(fono):
        errores.append("El teléfono debe tener 9 dígitos y ser válido.")

    # Validar correo
    if not correo or not validar_correo(correo):
        errores.append("El correo electrónico no tiene un formato válido.")

    # Validar rol
    if not rol_id:
        errores.append("El rol es obligatorio.")

    if errores:
        # Si hay errores, mostramos los mensajes y redirigimos de vuelta
        for error in errores:
            flash(error, 'danger')
        return redirect(url_for('user.usuarios'))

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
    enviar_correo_bienvenida(
        destinatario=correo,
        nombre=nombre,
        apellido=apellido,
        rut=rut,
        password_provisoria=password
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
