from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.utils import login_required

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
def index():
    return render_template('auth/login.html')

@dashboard.route('/admin')
@login_required
def admin():
    if session.get('user_role') != 'admin':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.login'))
    return redirect(url_for('admin.inicio'))


@dashboard.route('/client')
@login_required
def client():
    if session.get('user_role') != 'cliente':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.login'))
    return redirect(url_for('client.inicio'))


@dashboard.route('/visita')
@login_required
def visita():
    if session.get('user_role') != 'visita':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('dashboard/visita.html')