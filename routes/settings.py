from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, UserSettings

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('/')
@login_required
def index():
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id, language='fr', dark_mode=False)
        db.session.add(user_settings)
        db.session.commit()
    return render_template('settings/index.html', settings=user_settings, user=current_user)


@settings_bp.route('/update', methods=['POST'])
@login_required
def update():
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id)
        db.session.add(user_settings)

    user_settings.language = request.form.get('language', 'fr')
    user_settings.dark_mode = request.form.get('dark_mode') == 'on'
    user_settings.notifications_enabled = request.form.get('notifications_enabled') == 'on'
    user_settings.email_notifications = request.form.get('email_notifications') == 'on'
    user_settings.location = request.form.get('location', '').strip()
    db.session.commit()

    flash('Vos paramètres ont été enregistrés.', 'success')
    return redirect(url_for('settings.index'))
