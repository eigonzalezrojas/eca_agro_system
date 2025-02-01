from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.models import Usuario, Parcela, Cultivo, Dispositivo

admin = Blueprint('admin', __name__)

@admin.route('/')
def admin_dashboard():
    # Verificar si el usuario tiene el rol de administrador
    if session.get('user_role') != 1:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.login'))

    return redirect(url_for('admin.inicio'))

@admin.route('/inicio')
def inicio():
    total_administradores = Usuario.query.filter_by(fk_rol=1).count()
    total_clientes = Usuario.query.filter_by(fk_rol=2).count()
    total_visitas = Usuario.query.filter_by(fk_rol=3).count()
    total_parcelas = Parcela.query.count()
    total_cultivos = Cultivo.query.count()
    total_dispositivos = Dispositivo.query.count()

    return render_template(
        'sections/admin/inicio.html',
        total_administradores=total_administradores,
        total_clientes=total_clientes,
        total_visitas=total_visitas,
        total_parcelas=total_parcelas,
        total_cultivos=total_cultivos,
        total_dispositivos=total_dispositivos
    )