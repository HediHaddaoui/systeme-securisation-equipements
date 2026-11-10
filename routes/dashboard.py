from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Equipment, Notification, EventHistory

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='')


@dashboard_bp.route('/dashboard')
@login_required
def index():
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
