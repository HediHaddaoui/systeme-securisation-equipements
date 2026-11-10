from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' ou 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relations
    equipments_assigned = db.relationship('Equipment', foreign_keys='Equipment.assigned_user_id',
                                          backref='assigned_user', lazy=True)
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id',
                                    backref='user', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('EventHistory', foreign_keys='EventHistory.user_id',
                             backref='user', lazy=True)
    settings = db.relationship('UserSettings', foreign_keys='UserSettings.user_id',
                               backref='user', lazy=True, cascade='all, delete-orphan', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


class Equipment(db.Model):
    __tablename__ = 'equipments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    serial_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    rfid_identifier = db.Column(db.String(100), unique=True, nullable=True, index=True)
    status = db.Column(db.String(20), nullable=False, default='normal')  # normal, a_surveiller, suspect, vole
    registration_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relations
    rfid_tags = db.relationship('RFIDTag', foreign_keys='RFIDTag.equipment_id',
                                backref='equipment', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('EventHistory', foreign_keys='EventHistory.equipment_id',
                             backref='equipment', lazy=True)

    STATUS_CHOICES = [
        ('normal', 'Normal'),
        ('a_surveiller', 'À surveiller'),
        ('suspect', 'Suspect'),
        ('vole', 'Signalé comme volé'),
    ]

    @property
    def status_label(self):
        labels = dict(self.STATUS_CHOICES)
        return labels.get(self.status, self.status)

    @property
    def status_badge_class(self):
        classes = {
            'normal': 'bg-success',
            'a_surveiller': 'bg-warning text-dark',
            'suspect': 'bg-danger',
            'vole': 'bg-dark',
        }
        return classes.get(self.status, 'bg-secondary')

    def __repr__(self):
        return f'<Equipment {self.name}>'


class RFIDTag(db.Model):
    __tablename__ = 'rfid_tags'

    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.id'), nullable=True, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_detected_at = db.Column(db.DateTime, nullable=True)

    events = db.relationship('EventHistory', foreign_keys='EventHistory.rfid_tag_id',
                             backref='rfid_tag', lazy=True)

    def __repr__(self):
        return f'<RFIDTag {self.tag_id}>'


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False, default='info')  # info, warning, alert, security
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f'<Notification {self.title}>'


class EventHistory(db.Model):
    __tablename__ = 'events_history'

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)  # detection, perte, suspect, alerte, login, etc.
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.id'), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    rfid_tag_id = db.Column(db.Integer, db.ForeignKey('rfid_tags.id'), nullable=True, index=True)
    description = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(20), nullable=False, default='success')  # success, failure, alert
    simulated = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f'<EventHistory {self.event_type}>'


class UserSettings(db.Model):
    __tablename__ = 'user_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False, index=True)
    language = db.Column(db.String(10), nullable=False, default='fr')
    dark_mode = db.Column(db.Boolean, default=False, nullable=False)
    notifications_enabled = db.Column(db.Boolean, default=True, nullable=False)
    email_notifications = db.Column(db.Boolean, default=False, nullable=False)
    location = db.Column(db.String(100), nullable=True, default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<UserSettings user={self.user_id}>'
