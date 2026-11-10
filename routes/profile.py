from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, UserSettings
from utils import admin_required

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/')
@login_required
def index():
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id, language='fr', dark_mode=False)
        db.session.add(user_settings)
        db.session.commit()
    return render_template('profile/index.html', user=current_user, settings=user_settings)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
        current_user.username = request.form.get('username', current_user.username).strip()
        current_user.email = request.form.get('email', current_user.email).strip()

        # Vérifier l'unicité
        existing = User.query.filter(
            User.id != current_user.id,
            (User.username == current_user.username) | (User.email == current_user.email)
        ).first()
        if existing:
            flash('Ce nom d\'utilisateur ou email est déjà utilisé.', 'danger')
            return render_template('profile/edit.html', user=current_user)

        db.session.commit()
        flash('Votre profil a été mis à jour.', 'success')
        return redirect(url_for('profile.index'))

    return render_template('profile/edit.html', user=current_user)
