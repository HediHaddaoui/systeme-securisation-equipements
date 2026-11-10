from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Notification, EventHistory
from utils import admin_required

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@notifications_bp.route('/')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    return render_template('notifications/list.html', notifications=notifications)


@notifications_bp.route('/<int:notification_id>')
@login_required
def detail(notification_id):
    notification = db.session.get(Notification, notification_id)
    if not notification:
        flash('Notification introuvable.', 'danger')
        return redirect(url_for('notifications.list'))

    if notification.user_id != current_user.id and not current_user.is_admin():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('notifications.list'))

    if not notification.is_read:
        notification.is_read = True
        db.session.commit()

    return render_template('notifications/detail.html', notification=notification)


@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_read(notification_id):
    notification = db.session.get(Notification, notification_id)
    if not notification:
        flash('Notification introuvable.', 'danger')
        return redirect(url_for('notifications.list'))

    if notification.user_id != current_user.id and not current_user.is_admin():
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('notifications.list'))

    notification.is_read = True
    db.session.commit()
    flash('Notification marquée comme lue.', 'success')
    return redirect(url_for('notifications.list'))


@notifications_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({Notification.is_read: True})
    db.session.commit()
    flash('Toutes les notifications ont été marquées comme lues.', 'success')
    return redirect(url_for('notifications.list'))


@notifications_bp.route('/api/unread-count')
@login_required
def api_unread_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})


@notifications_bp.route('/api/recent')
@login_required
def api_recent():
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).limit(5).all()
    results = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.type,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%d/%m/%Y %H:%M')
    } for n in notifications]
    return jsonify(results)
