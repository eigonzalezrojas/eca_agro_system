from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.utils import login_required

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
def index():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder al dashboard.', 'warning')
        return redirect(url_for('auth.login'))

    user_role = session.get('user_role')

    if user_role == 1:
        return redirect(url_for('dashboard.admin_dashboard'))
    elif user_role == 2:
        return redirect(url_for('dashboard.user_dashboard'))
    elif user_role == 3:
        return redirect(url_for('dashboard.client_dashboard'))
    else:
        flash('Rol no reconocido. Contacta al administrador.', 'danger')
        return redirect(url_for('auth.login'))


@dashboard.route('/admin')
@login_required
def admin_dashboard():
    return render_template('dashboard/admin.html')


@dashboard.route('/user')
@login_required
def user_dashboard():
    return render_template('dashboard/user.html')


@dashboard.route('/client')
@login_required
def client_dashboard():
    return render_template('dashboard/client.html')