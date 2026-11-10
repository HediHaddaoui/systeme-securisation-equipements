from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from config import config
from models import db, User, Equipment, RFIDTag, Notification, EventHistory, UserSettings
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.dashboard import dashboard_bp
from routes.equipments import equipments_bp
from routes.rfid import rfid_bp
from routes.notifications import notifications_bp
from routes.events import events_bp
from routes.profile import profile_bp
from routes.settings import settings_bp

login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Enregistrer les blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(equipments_bp)
    app.register_blueprint(rfid_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(settings_bp)

    # Contexte global pour tous les templates
    @app.context_processor
    def inject_globals():
        unread_count = 0
        settings = None
        recent_notifs = []
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
            settings = UserSettings.query.filter_by(user_id=current_user.id).first()
            if not settings:
                settings = UserSettings(user_id=current_user.id, language='fr', dark_mode=False)
                db.session.add(settings)
                db.session.commit()
            recent_notifs = Notification.query.filter_by(
                user_id=current_user.id
            ).order_by(Notification.created_at.desc()).limit(5).all()
        return dict(
            unread_notifications_count=unread_count,
            settings=settings,
            recent_notifications=recent_notifs
        )

    # Gestionnaire d'erreurs
    @app.errorhandler(403)
    def forbidden(error):
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('dashboard.index'))

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Initialisation de la base de données et création du compte admin par défaut
    with app.app_context():
        db.create_all()
        _initialize_default_data()

    return app


def _initialize_default_data():
    """Crée le compte administrateur par défaut s'il n'existe pas."""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@securite.local',
            role='admin'
        )
        admin.set_password('Admin123!')
        db.session.add(admin)
        db.session.commit()

        # Créer les paramètres par défaut pour l'admin
        settings = UserSettings(user_id=admin.id, language='fr', dark_mode=False)
        db.session.add(settings)
        db.session.commit()

    # S'assurer que tous les utilisateurs ont des paramètres
    users_without_settings = User.query.filter(
        ~User.id.in_(db.session.query(UserSettings.user_id))
    ).all()
    for user in users_without_settings:
        settings = UserSettings(user_id=user.id, language='fr', dark_mode=False)
        db.session.add(settings)
    db.session.commit()


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
