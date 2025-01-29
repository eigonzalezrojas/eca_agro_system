from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import Dispositivo
from app import db

dispositivo = Blueprint('dispositivo', __name__)

@dispositivo.route('/dispositivos')
def listar_dispositivos():
    dispositivos = Dispositivo.query.all()
    return render_template('sections/admin/dispositivos.html', dispositivos=dispositivos)

@dispositivo.route('/dispositivos/crear', methods=['POST'])
def crear_dispositivo():
    # Implementar lógica para crear un dispositivo
    pass

@dispositivo.route('/dispositivos/editar/<int:id>', methods=['POST'])
def editar_dispositivo(id):
    # Implementar lógica para editar un dispositivo
    pass

@dispositivo.route('/dispositivos/eliminar/<int:id>', methods=['POST'])
def eliminar_dispositivo(id):
    # Implementar lógica para eliminar un dispositivo
    pass