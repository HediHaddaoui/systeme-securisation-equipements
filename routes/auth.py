from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, UserSettings
from forms import LoginForm, RegistrationForm, EditUserForm
from utils import admin_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user_settings = UserSettings.query.filter_by(user_id=user.id).first()
            if not user_settings:
                user_settings = UserSettings(user_id=user.id, language='fr', dark_mode=False)
                db.session.add(user_settings)
                db.session.commit()

            from models import EventHistory
            event = EventHistory(
                event_type='login',
                user_id=user.id,
                description=f'Connexion de l\'utilisateur {user.username}',
                result='success',
                simulated=False
            )
            db.session.add(event)
            db.session.commit()

            flash(f'Bonjour {user.username}, vous êtes connecté.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Adresse email ou mot de passe incorrect.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.email == form.email.data) | (User.username == form.username.data)
        ).first()
        if existing_user:
            flash('Un utilisateur avec cet email ou ce nom d\'utilisateur existe déjà.', 'danger')
            return render_template('auth/register.html', form=form)

        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        user_settings = UserSettings(user_id=user.id, language='fr', dark_mode=False)
        db.session.add(user_settings)
        db.session.commit()

        from models import EventHistory
        event = EventHistory(
            event_type='registration',
            user_id=user.id,
            description=f'Enregistrement du nouvel utilisateur {user.username}',
            result='success',
            simulated=False
        )
        db.session.add(event)
        db.session.commit()

        flash('Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    from models import EventHistory
    event = EventHistory(
        event_type='logout',
        user_id=current_user.id,
        description=f'Déconnexion de l\'utilisateur {current_user.username}',
        result='success',
        simulated=False
    )
    db.session.add(event)
    db.session.commit()

    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))
