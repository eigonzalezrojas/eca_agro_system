from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import Cultivo
from app.extensions import db

cultivo = Blueprint('cultivo', __name__)

@cultivo.route('/cultivos')
def listar_cultivos():
    cultivos = Cultivo.query.all()
    return render_template('sections/admin/cultivos.html', cultivos=cultivos)

@cultivo.route('/cultivos/crear', methods=['POST'])
def crear_cultivo():
    # Implementar lógica para crear un cultivo
    pass

@cultivo.route('/cultivos/editar/<int:id>', methods=['POST'])
def editar_cultivo(id):
    # Implementar lógica para editar un cultivo
    pass

@cultivo.route('/cultivos/eliminar/<int:id>', methods=['POST'])
def eliminar_cultivo(id):
    # Implementar lógica para eliminar un cultivo
    pass