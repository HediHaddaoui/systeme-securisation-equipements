from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from models import User


class LoginForm(FlaskForm):
    email = StringField('Adresse email', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')


class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Adresse email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe',
                                     validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Rôle', choices=[('user', 'Utilisateur'), ('admin', 'Administrateur')],
                       default='user')
    submit = SubmitField('S\'enregistrer')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Cet email est déjà utilisé.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Ce nom d\'utilisateur est déjà utilisé.')


class EditUserForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Adresse email', validators=[DataRequired(), Email()])
    password = PasswordField('Nouveau mot de passe', validators=[Optional(), Length(min=6)])
    role = SelectField('Rôle', choices=[('user', 'Utilisateur'), ('admin', 'Administrateur')])
    submit = SubmitField('Enregistrer')

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_username = None
        self.original_email = None

    def validate_username(self, field):
        if self.original_username and field.data != self.original_username:
            if User.query.filter_by(username=field.data).first():
                raise ValidationError('Ce nom d\'utilisateur est déjà utilisé.')

    def validate_email(self, field):
        if self.original_email and field.data != self.original_email:
            if User.query.filter_by(email=field.data).first():
                raise ValidationError('Cet email est déjà utilisé.')


class EquipmentForm(FlaskForm):
    name = StringField('Nom du matériel', validators=[DataRequired(), Length(min=2, max=100)])
    type = StringField('Type', validators=[DataRequired(), Length(min=2, max=50)])
    serial_number = StringField('Numéro de série', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    assigned_user_id = IntegerField('Utilisateur assigné', validators=[Optional()])
    rfid_identifier = StringField('Identifiant RFID', validators=[Optional(), Length(max=100)])
    status = SelectField('Statut',
                         choices=[('normal', 'Normal'),
                                  ('a_surveiller', 'À surveiller'),
                                  ('suspect', 'Suspect'),
                                  ('vole', 'Signalé comme volé')],
                         default='normal')
    submit = SubmitField('Enregistrer')
