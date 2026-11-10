from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, User, Equipment, Notification, EventHistory, UserSettings
from forms import EditUserForm, EquipmentForm
from utils import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_equipments = Equipment.query.count()
    normal_equipments = Equipment.query.filter_by(status='normal').count()
    surveiller_equipments = Equipment.query.filter_by(status='a_surveiller').count()
    suspect_equipments = Equipment.query.filter_by(status='suspect').count()
    vole_equipments = Equipment.query.filter_by(status='vole').count()
    total_notifications = Notification.query.count()
    unread_notifications = Notification.query.filter_by(is_read=False).count()

    recent_events = EventHistory.query.order_by(EventHistory.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    stats = {
        'total_users': total_users,
        'total_equipments': total_equipments,
        'normal_equipments': normal_equipments,
        'a_surveiller_equipments': surveiller_equipments,
        'suspect_equipments': suspect_equipments,
        'vole_equipments': vole_equipments,
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
    }

    return render_template('dashboard/index.html', stats=stats,
                           recent_events=recent_events, recent_users=recent_users)


@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')

    query = User.query
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search))
        )
    if role_filter:
        query = query.filter_by(role=role_filter)

    users = query.order_by(User.created_at.desc()).all()
    return render_template('users/list.html', users=users, search=search, role_filter=role_filter)


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    from forms import RegistrationForm
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.email == form.email.data) | (User.username == form.username.data)
        ).first()
        if existing_user:
            flash('Un utilisateur avec cet email ou ce nom d\'utilisateur existe déjà.', 'danger')
            return render_template('users/add.html', form=form)

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
            event_type='user_created',
            user_id=current_user.id,
            description=f'Création de l\'utilisateur {user.username} par {current_user.username}',
            result='success',
            simulated=False
        )
        db.session.add(event)
        db.session.commit()

        flash(f'L\'utilisateur {user.username} a été ajouté avec succès.', 'success')
        return redirect(url_for('admin.users_list'))
    return render_template('users/add.html', form=form)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('Utilisateur introuvable.', 'danger')
        return redirect(url_for('admin.users_list'))

    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()

        from models import EventHistory
        event = EventHistory(
            event_type='user_updated',
            user_id=current_user.id,
            description=f'Modification de l\'utilisateur {user.username} par {current_user.username}',
            result='success',
            simulated=False
        )
        db.session.add(event)
        db.session.commit()

        flash(f'L\'utilisateur {user.username} a été modifié.', 'success')
        return redirect(url_for('admin.users_list'))
    return render_template('users/edit.html', form=form, user=user)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('Utilisateur introuvable.', 'danger')
        return redirect(url_for('admin.users_list'))

    if user.id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'danger')
        return redirect(url_for('admin.users_list'))

    username = user.username
    db.session.delete(user)
    db.session.commit()

    from models import EventHistory
    event = EventHistory(
        event_type='user_deleted',
        user_id=current_user.id,
        description=f'Suppression de l\'utilisateur {username} par {current_user.username}',
        result='success',
        simulated=False
    )
    db.session.add(event)
    db.session.commit()

    flash(f'L\'utilisateur {username} a été supprimé.', 'success')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    stats = {
        'total_users': User.query.count(),
        'total_equipments': Equipment.query.count(),
        'normal_equipments': Equipment.query.filter_by(status='normal').count(),
        'a_surveiller_equipments': Equipment.query.filter_by(status='a_surveiller').count(),
        'suspect_equipments': Equipment.query.filter_by(status='suspect').count(),
        'vole_equipments': Equipment.query.filter_by(status='vole').count(),
        'total_notifications': Notification.query.count(),
        'unread_notifications': Notification.query.filter_by(is_read=False).count(),
    }
    return jsonify(stats)
