from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import Parcela
from app.extensions import db

parcela = Blueprint('parcela', __name__)


@parcela.route('/parcelas')
def parcelas():
    parcelas = Parcela.query.all()
    return render_template('sections/admin/parcelas.html', parcelas=parcelas)


@parcela.route('/parcelas/crear', methods=['POST'])
def crear_parcela():
    # Implementar lógica para crear una parcela
    pass


@parcela.route('/parcelas/editar/<int:id>', methods=['POST'])
def editar_parcela(id):
    # Implementar lógica para editar una parcela
    pass


@parcela.route('/parcelas/eliminar/<int:id>', methods=['POST'])
def eliminar_parcela(id):
    # Implementar lógica para eliminar una parcela
    pass
