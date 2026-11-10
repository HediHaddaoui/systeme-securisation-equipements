from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """Décorateur qui restreint l'accès aux administrateurs uniquement."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('Accès réservé aux administrateurs.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def user_or_admin_required(f):
    """Décorateur pour les utilisateurs connectés (tous les rôles)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
