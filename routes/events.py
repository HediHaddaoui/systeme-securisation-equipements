from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, EventHistory, Equipment, User
from utils import admin_required

events_bp = Blueprint('events', __name__, url_prefix='/events')


@events_bp.route('/')
@login_required
def history():
    search = request.args.get('search', '')
    event_type_filter = request.args.get('event_type', '')
    result_filter = request.args.get('result', '')
    simulated_filter = request.args.get('simulated', '')

    query = EventHistory.query

    if search:
        query = query.filter(EventHistory.description.contains(search))
    if event_type_filter:
        query = query.filter_by(event_type=event_type_filter)
    if result_filter:
        query = query.filter_by(result=result_filter)
    if simulated_filter == 'true':
        query = query.filter_by(simulated=True)
    elif simulated_filter == 'false':
        query = query.filter_by(simulated=False)

    events = query.order_by(EventHistory.created_at.desc()).all()

    # Options de filtre
    event_types = db.session.query(EventHistory.event_type).distinct().all()
    event_types = [et[0] for et in event_types]

    return render_template('events/history.html', events=events,
                           search=search, event_type_filter=event_type_filter,
                           result_filter=result_filter, simulated_filter=simulated_filter,
                           event_types=event_types)


@events_bp.route('/api/list')
@login_required
def api_list():
    events = EventHistory.query.order_by(EventHistory.created_at.desc()).limit(50).all()
    results = [{
        'id': e.id,
        'event_type': e.event_type,
        'description': e.description,
        'result': e.result,
        'simulated': e.simulated,
        'created_at': e.created_at.strftime('%d/%m/%Y %H:%M:%S'),
        'equipment': e.equipment.name if e.equipment else '-',
        'user': e.user.username if e.user else '-'
    } for e in events]
    return jsonify(results)
