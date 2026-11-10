from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, RFIDTag, Equipment, EventHistory, Notification, User
from utils import admin_required
import random
import string
from datetime import datetime

rfid_bp = Blueprint('rfid', __name__, url_prefix='/rfid')


def generate_simulated_tag_id():
    """Génère un identifiant de tag RFID simulé."""
    return 'RFID-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


@rfid_bp.route('/')
@login_required
def index():
    tags = RFIDTag.query.order_by(RFIDTag.created_at.desc()).all()
    equipments = Equipment.query.all()
    return render_template('rfid/index.html', tags=tags, equipments=equipments)


@rfid_bp.route('/tags')
@login_required
def tags():
    tags = RFIDTag.query.order_by(RFIDTag.created_at.desc()).all()
    return render_template('rfid/tags.html', tags=tags)


@rfid_bp.route('/tags/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_tag():
    if request.method == 'POST':
        tag_id = request.form.get('tag_id', '').strip()
        equipment_id = request.form.get('equipment_id', type=int)
        is_active = request.form.get('is_active') == 'on'

        if not tag_id:
            tag_id = generate_simulated_tag_id()

        existing = RFIDTag.query.filter_by(tag_id=tag_id).first()
        if existing:
            flash(f'Le tag RFID "{tag_id}" existe déjà.', 'danger')
            return redirect(url_for('rfid.add_tag'))

        tag = RFIDTag(
            tag_id=tag_id,
            equipment_id=equipment_id if equipment_id else None,
            is_active=is_active
        )
        db.session.add(tag)
        db.session.commit()

        event = EventHistory(
            event_type='rfid_tag_registered',
            equipment_id=equipment_id if equipment_id else None,
            user_id=current_user.id,
            rfid_tag_id=tag.id,
            description=f'Enregistrement du tag RFID "{tag_id}"',
            result='success',
            simulated=False
        )
        db.session.add(event)
        db.session.commit()

        flash(f'Le tag RFID "{tag_id}" a été enregistré.', 'success')
        return redirect(url_for('rfid.tags'))

    equipments = Equipment.query.all()
    return render_template('rfid/add_tag.html', equipments=equipments)


@rfid_bp.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_tag(tag_id):
    tag = db.session.get(RFIDTag, tag_id)
    if not tag:
        flash('Tag RFID introuvable.', 'danger')
        return redirect(url_for('rfid.tags'))

    if request.method == 'POST':
        tag.tag_id = request.form.get('tag_id', tag.tag_id).strip()
        tag.equipment_id = request.form.get('equipment_id', type=int)
        tag.is_active = request.form.get('is_active') == 'on'
        db.session.commit()

        event = EventHistory(
            event_type='rfid_tag_updated',
            equipment_id=tag.equipment_id,
            user_id=current_user.id,
            rfid_tag_id=tag.id,
            description=f'Modification du tag RFID "{tag.tag_id}"',
            result='success',
            simulated=False
        )
        db.session.add(event)
        db.session.commit()

        flash(f'Le tag RFID "{tag.tag_id}" a été modifié.', 'success')
        return redirect(url_for('rfid.tags'))

    equipments = Equipment.query.all()
    return render_template('rfid/edit_tag.html', tag=tag, equipments=equipments)


@rfid_bp.route('/tags/<int:tag_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_tag(tag_id):
    tag = db.session.get(RFIDTag, tag_id)
    if not tag:
        flash('Tag RFID introuvable.', 'danger')
        return redirect(url_for('rfid.tags'))

    tag_id_str = tag.tag_id
    db.session.delete(tag)
    db.session.commit()

    flash(f'Le tag RFID "{tag_id_str}" a été supprimé.', 'success')
    return redirect(url_for('rfid.tags'))


@rfid_bp.route('/simulator')
@login_required
def simulator():
    tags = RFIDTag.query.filter_by(is_active=True).all()
    equipments = Equipment.query.all()
    return render_template('rfid/simulator.html', tags=tags, equipments=equipments)


@rfid_bp.route('/simulator/detect', methods=['POST'])
@login_required
def simulate_detect():
    """Simule la détection d'un tag RFID."""
    data = request.get_json() or {}
    tag_id_str = data.get('tag_id')
    equipment_id = data.get('equipment_id')
    if equipment_id is not None:
        try:
            equipment_id = int(equipment_id)
        except (ValueError, TypeError):
            equipment_id = None

    tag = None
    if tag_id_str:
        tag = RFIDTag.query.filter_by(tag_id=tag_id_str).first()
        if not tag:
            # Créer le tag avec l'identifiant fourni
            tag = RFIDTag(tag_id=tag_id_str, is_active=True)
            db.session.add(tag)
            db.session.commit()

    if not tag:
        # Créer un tag simulé aléatoire pour la démo (si aucun ID fourni)
        tag_id_str = generate_simulated_tag_id()
        tag = RFIDTag(tag_id=tag_id_str, is_active=True)
        db.session.add(tag)
        db.session.commit()

    tag.last_detected_at = datetime.utcnow()

    # Associer à un équipement si spécifié
    if equipment_id:
        tag.equipment_id = equipment_id
        equipment = db.session.get(Equipment, equipment_id)
        equip_name = equipment.name if equipment else 'inconnu'
    else:
        equip_name = 'non assigné'

    # Enregistrer l'événement
    event = EventHistory(
        event_type='rfid_detection',
        equipment_id=tag.equipment_id,
        user_id=current_user.id,
        rfid_tag_id=tag.id,
        description=f'Détection du tag RFID "{tag.tag_id}" ({equip_name})',
        result='success',
        simulated=True
    )
    db.session.add(event)
    db.session.commit()

    return jsonify({
        'success': True,
        'event_type': 'détection',
        'tag_id': tag.tag_id,
        'equipment': equip_name,
        'simulated': True,
        'timestamp': event.created_at.strftime('%d/%m/%Y %H:%M:%S')
    })


@rfid_bp.route('/simulator/lost', methods=['POST'])
@login_required
def simulate_lost():
    """Simule la perte d'un tag RFID."""
    data = request.get_json() or {}
    tag_id_str = data.get('tag_id')

    tag = None
    if tag_id_str:
        tag = RFIDTag.query.filter_by(tag_id=tag_id_str).first()
        if not tag:
            tag = RFIDTag(tag_id=tag_id_str, is_active=False)
            db.session.add(tag)
            db.session.commit()

    if not tag:
        tag_id_str = generate_simulated_tag_id()
        tag = RFIDTag(tag_id=tag_id_str, is_active=False)
        db.session.add(tag)
        db.session.commit()

    equip_name = tag.equipment.name if tag.equipment else 'non assigné'

    event = EventHistory(
        event_type='rfid_perte',
        equipment_id=tag.equipment_id,
        user_id=current_user.id,
        rfid_tag_id=tag.id,
        description=f'Perte du tag RFID "{tag.tag_id}" ({equip_name})',
        result='failure',
        simulated=True
    )
    db.session.add(event)

    # Créer une notification d'alerte
    notification = Notification(
        user_id=current_user.id,
        title='Tag RFID perdu',
        message=f'Le tag RFID "{tag.tag_id}" associé à {equip_name} a été signalé comme perdu.',
        type='warning',
        is_read=False
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        'success': True,
        'event_type': 'perte',
        'tag_id': tag.tag_id,
        'equipment': equip_name,
        'simulated': True,
        'timestamp': event.created_at.strftime('%d/%m/%Y %H:%M:%S')
    })


@rfid_bp.route('/simulator/suspicious', methods=['POST'])
@login_required
def simulate_suspicious():
    """Simule un événement suspect."""
    data = request.get_json() or {}
    tag_id_str = data.get('tag_id')

    tag = None
    if tag_id_str:
        tag = RFIDTag.query.filter_by(tag_id=tag_id_str).first()
        if not tag:
            tag = RFIDTag(tag_id=tag_id_str, is_active=True)
            db.session.add(tag)
            db.session.commit()

    if not tag:
        tag_id_str = generate_simulated_tag_id()
        tag = RFIDTag(tag_id=tag_id_str, is_active=True)
        db.session.add(tag)
        db.session.commit()

    equip_name = tag.equipment.name if tag.equipment else 'non assigné'

    event = EventHistory(
        event_type='evenement_suspect',
        equipment_id=tag.equipment_id,
        user_id=current_user.id,
        rfid_tag_id=tag.id,
        description=f'Événement suspect détecté pour le tag RFID "{tag.tag_id}" ({equip_name})',
        result='alert',
        simulated=True
    )
    db.session.add(event)

    # Mettre à jour le statut de l'équipement si associé
    if tag.equipment:
        tag.equipment.status = 'suspect'

    # Créer une notification d'alerte de sécurité
    notification = Notification(
        user_id=current_user.id,
        title='Événement suspect détecté',
        message=f'Activité suspecte détectée sur le tag RFID "{tag.tag_id}" ({equip_name}).',
        type='security',
        is_read=False
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        'success': True,
        'event_type': 'suspect',
        'tag_id': tag.tag_id,
        'equipment': equip_name,
        'simulated': True,
        'timestamp': event.created_at.strftime('%d/%m/%Y %H:%M:%S')
    })


@rfid_bp.route('/simulator/alert', methods=['POST'])
@login_required
def simulate_alert():
    """Simule une alerte de sécurité (vol)."""
    data = request.get_json() or {}
    tag_id_str = data.get('tag_id')

    tag = None
    if tag_id_str:
        tag = RFIDTag.query.filter_by(tag_id=tag_id_str).first()
        if not tag:
            tag = RFIDTag(tag_id=tag_id_str, is_active=True)
            db.session.add(tag)
            db.session.commit()

    if not tag:
        tag_id_str = generate_simulated_tag_id()
        tag = RFIDTag(tag_id=tag_id_str, is_active=True)
        db.session.add(tag)
        db.session.commit()

    equip_name = tag.equipment.name if tag.equipment else 'non assigné'

    event = EventHistory(
        event_type='alerte_securite',
        equipment_id=tag.equipment_id,
        user_id=current_user.id,
        rfid_tag_id=tag.id,
        description=f'ALERTE DE SÉCURITÉ: Vol présumé du tag RFID "{tag.tag_id}" ({equip_name})',
        result='alert',
        simulated=True
    )
    db.session.add(event)

    # Mettre à jour le statut de l'équipement si associé
    if tag.equipment:
        tag.equipment.status = 'vole'

    # Créer une notification d'alerte de sécurité critique
    notification = Notification(
        user_id=current_user.id,
        title='ALERTE DE SÉCURITÉ - Vol présumé',
        message=f'Vol présumé détecté pour le matériel "{equip_name}" (tag RFID "{tag.tag_id}").',
        type='security',
        is_read=False
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        'success': True,
        'event_type': 'alerte',
        'tag_id': tag.tag_id,
        'equipment': equip_name,
        'simulated': True,
        'timestamp': event.created_at.strftime('%d/%m/%Y %H:%M:%S')
    })


@rfid_bp.route('/events')
@login_required
def events():
    events = EventHistory.query.filter(
        EventHistory.event_type.in_(['rfid_detection', 'rfid_perte', 'evenement_suspect', 'alerte_securite'])
    ).order_by(EventHistory.created_at.desc()).all()
    return render_template('rfid/events.html', events=events)
