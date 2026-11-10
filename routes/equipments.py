from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Equipment, EventHistory, User, RFIDTag
from forms import EquipmentForm
from utils import admin_required

equipments_bp = Blueprint('equipments', __name__, url_prefix='/equipments')


@equipments_bp.route('/')
@login_required
def list():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')

    query = Equipment.query
    if search:
        query = query.filter(
            (Equipment.name.contains(search)) |
            (Equipment.serial_number.contains(search)) |
            (Equipment.type.contains(search))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)

    equipments = query.order_by(Equipment.registration_date.desc()).all()
    status_choices = Equipment.STATUS_CHOICES
    return render_template('equipments/list.html', equipments=equipments,
                           search=search, status_filter=status_filter,
                           status_choices=status_choices)


@equipments_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    form = EquipmentForm()
    # Charger les utilisateurs pour le champ assigned_user
    from models import User
    users = User.query.all()
    form.assigned_user_id.choices = [(0, 'Non assigné')] + [(u.id, u.username) for u in users]

    if form.validate_on_submit():
        assigned_user_id = form.assigned_user_id.data if form.assigned_user_id.data != 0 else None
        equipment = Equipment(
            name=form.name.data,
            type=form.type.data,
            serial_number=form.serial_number.data,
            description=form.description.data,
            assigned_user_id=assigned_user_id,
            rfid_identifier=form.rfid_identifier.data,
            status=form.status.data,
        )
        db.session.add(equipment)
        db.session.commit()

        event = EventHistory(
            event_type='equipment_created',
            equipment_id=equipment.id,
            user_id=current_user.id,
            description=f'Création du matériel "{equipment.name}" (série: {equipment.serial_number})',
            result='success',
            simulated=False
        )
        db.session.add(event)
        db.session.commit()

        flash(f'Le matériel "{equipment.name}" a été ajouté.', 'success')
        return redirect(url_for('equipments.list'))
    return render_template('equipments/add.html', form=form, users=users)


@equipments_bp.route('/<int:equipment_id>')
@login_required
def detail(equipment_id):
    equipment = db.session.get(Equipment, equipment_id)
    if not equipment:
        flash('Matériel introuvable.', 'danger')
        return redirect(url_for('equipments.list'))

    events = EventHistory.query.filter_by(equipment_id=equipment.id)\
        .order_by(EventHistory.created_at.desc()).all()
    rfid_tags = RFIDTag.query.filter_by(equipment_id=equipment.id).all()
    return render_template('equipments/detail.html', equipment=equipment,
                           events=events, rfid_tags=rfid_tags)


@equipments_bp.route('/<int:equipment_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(equipment_id):
    equipment = db.session.get(Equipment, equipment_id)
    if not equipment:
        flash('Matériel introuvable.', 'danger')
        return redirect(url_for('equipments.list'))

    form = EquipmentForm(obj=equipment)
    from models import User
    users = User.query.all()
    form.assigned_user_id.choices = [(0, 'Non assigné')] + [(u.id, u.username) for u in users]

    if form.validate_on_submit():
        equipment.name = form.name.data
        equipment.type = form.type.data
        equipment.serial_number = form.serial_number.data
        equipment.description = form.description.data
        equipment.assigned_user_id = form.assigned_user_id.data if form.assigned_user_id.data != 0 else None
        equipment.rfid_identifier = form.rfid_identifier.data
        equipment.status = form.status.data
        db.session.commit()

        event = EventHistory(
            event_type='equipment_updated',
            equipment_id=equipment.id,
            user_id=current_user.id,
            description=f'Modification du matériel "{equipment.name}"',
            result='success',
            simulated=False
        )
        db.session.add(event)
        db.session.commit()

        flash(f'Le matériel "{equipment.name}" a été modifié.', 'success')
        return redirect(url_for('equipments.detail', equipment_id=equipment.id))

    if request.method == 'GET':
        form.assigned_user_id.data = equipment.assigned_user_id or 0
    return render_template('equipments/edit.html', form=form, equipment=equipment, users=users)


@equipments_bp.route('/<int:equipment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(equipment_id):
    equipment = db.session.get(Equipment, equipment_id)
    if not equipment:
        flash('Matériel introuvable.', 'danger')
        return redirect(url_for('equipments.list'))

    name = equipment.name
    db.session.delete(equipment)
    db.session.commit()

    event = EventHistory(
        event_type='equipment_deleted',
        user_id=current_user.id,
        description=f'Suppression du matériel "{name}"',
        result='success',
        simulated=False
    )
    db.session.add(event)
    db.session.commit()

    flash(f'Le matériel "{name}" a été supprimé.', 'success')
    return redirect(url_for('equipments.list'))


@equipments_bp.route('/api/search')
@login_required
def api_search():
    q = request.args.get('q', '')
    if not q:
        return jsonify([])
    equipments = Equipment.query.filter(
        (Equipment.name.contains(q)) |
        (Equipment.serial_number.contains(q))
    ).limit(10).all()
    results = [{
        'id': e.id,
        'name': e.name,
        'serial_number': e.serial_number,
        'status': e.status,
        'status_label': e.status_label
    } for e in equipments]
    return jsonify(results)
