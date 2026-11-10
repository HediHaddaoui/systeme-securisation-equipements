"""
Tests automatisés pour l'application de sécurisation des équipements.
Couvre tous les modules requis par le cahier des charges.
"""
import os
import sys
import unittest

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Equipment, RFIDTag, Notification, EventHistory, UserSettings


class SecuritySystemTestCase(unittest.TestCase):
    """Classe de base pour les tests avec application Flask en mode test."""

    def setUp(self):
        """Configure l'application de test et la base de données."""
        self.app = create_app('default')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Créer un administrateur par défaut seulement s'il n'existe pas
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', email='admin@securite.local', role='admin')
                admin.set_password('Admin123!')
                db.session.add(admin)
                db.session.commit()
                db.session.add(UserSettings(user_id=admin.id, language='fr', dark_mode=False))
                db.session.commit()

    def tearDown(self):
        """Nettoie après chaque test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login_admin(self):
        """Connecte l'administrateur via session_transaction."""
        with self.app.app_context():
            admin = User.query.filter_by(username='admin').first()
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(admin.id)
                sess['_fresh'] = True

    def login_user(self, username='regular', email='regular@test.com', role='user'):
        """Connecte un utilisateur via session_transaction."""
        with self.app.app_context():
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(username=username, email=email, role=role)
                user.set_password('User123!')
                db.session.add(user)
                db.session.commit()
                db.session.add(UserSettings(user_id=user.id, language='fr', dark_mode=False))
                db.session.commit()
            with self.client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            return user

    # ================================================================
    # 1. AUTHENTIFICATION
    # ================================================================

    def test_01_admin_registration(self):
        """Test: Un nouvel administrateur peut s'enregistrer."""
        with self.app.app_context():
            count_before = User.query.count()
        response = self.client.post('/auth/register', data=dict(
            username='newadmin',
            email='newadmin@test.com',
            password='Admin123!',
            confirm_password='Admin123!',
            role='admin'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            count_after = User.query.count()
            self.assertEqual(count_after, count_before + 1)
            new_user = User.query.filter_by(username='newadmin').first()
            self.assertIsNotNone(new_user)
            self.assertTrue(new_user.check_password('Admin123!'))

    def test_02_successful_login(self):
        """Test: Connexion réussie avec l'administrateur par défaut."""
        response = self.client.post('/auth/login', data=dict(
            email='admin@securite.local',
            password='Admin123!'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_03_invalid_login(self):
        """Test: Connexion refusée avec mauvais identifiants."""
        response = self.client.post('/auth/login', data=dict(
            email='admin@securite.local',
            password='mauvaismotdepasse'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le formulaire de connexion est réaffiché (échec)
        self.assertIn(b'Connexion', response.data)
        # Vérifier que l'utilisateur n'est pas connecté (toujours sur la page de login)
        self.assertIn(b'Mot de passe', response.data)

    def test_04_logout(self):
        """Test: Déconnexion fonctionne."""
        self.login_admin()
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # ================================================================
    # 2. GESTION DES UTILISATEURS (CRUD)
    # ================================================================

    def test_05_add_user(self):
        """Test: Ajout d'un utilisateur par l'admin."""
        self.login_admin()
        response = self.client.post('/admin/users/add', data=dict(
            username='testuser',
            email='testuser@test.com',
            password='User123!',
            confirm_password='User123!',
            role='user'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.role, 'user')

    def test_06_edit_user(self):
        """Test: Modification d'un utilisateur."""
        self.login_admin()
        self.client.post('/admin/users/add', data=dict(
            username='editme',
            email='editme@test.com',
            password='User123!',
            confirm_password='User123!',
            role='user'
        ))
        with self.app.app_context():
            user = User.query.filter_by(username='editme').first()
            user_id = user.id
        response = self.client.post(f'/admin/users/{user_id}/edit', data=dict(
            username='edited',
            email='edited@test.com',
            password='',
            role='admin'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            user = User.query.get(user_id)
            self.assertEqual(user.username, 'edited')
            self.assertEqual(user.role, 'admin')

    def test_07_delete_user(self):
        """Test: Suppression d'un utilisateur."""
        self.login_admin()
        self.client.post('/admin/users/add', data=dict(
            username='todelete',
            email='todelete@test.com',
            password='User123!',
            confirm_password='User123!',
            role='user'
        ))
        with self.app.app_context():
            user = User.query.filter_by(username='todelete').first()
            user_id = user.id
        response = self.client.post(f'/admin/users/{user_id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            user = User.query.get(user_id)
            self.assertIsNone(user)

    # ================================================================
    # 3. GESTION DU MATÉRIEL
    # ================================================================

    def test_08_equipment_creation(self):
        """Test: Création d'un équipement."""
        self.login_admin()
        response = self.client.post('/equipments/add', data=dict(
            name='Ordinateur portable',
            type='Informatique',
            serial_number='SN123456',
            description='PC portable de bureau',
            assigned_user_id='0',
            rfid_identifier='RFID-TEST01',
            status='normal'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            equip = Equipment.query.filter_by(serial_number='SN123456').first()
            self.assertIsNotNone(equip)
            self.assertEqual(equip.name, 'Ordinateur portable')

    def test_09_equipment_modification(self):
        """Test: Modification d'un équipement."""
        self.login_admin()
        self.client.post('/equipments/add', data=dict(
            name='Matériel test',
            type='Test',
            serial_number='SNMODIFY',
            description='Desc',
            assigned_user_id='0',
            rfid_identifier='',
            status='normal'
        ))
        with self.app.app_context():
            equip = Equipment.query.filter_by(serial_number='SNMODIFY').first()
            equip_id = equip.id
        response = self.client.post(f'/equipments/{equip_id}/edit', data=dict(
            name='Matériel modifié',
            type='Test modifié',
            serial_number='SNMODIFY',
            description='Desc modifiée',
            assigned_user_id='0',
            rfid_identifier='',
            status='suspect'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            equip = Equipment.query.get(equip_id)
            self.assertEqual(equip.name, 'Matériel modifié')
            self.assertEqual(equip.status, 'suspect')

    def test_10_equipment_deletion(self):
        """Test: Suppression d'un équipement."""
        self.login_admin()
        self.client.post('/equipments/add', data=dict(
            name='À supprimer',
            type='Test',
            serial_number='SNDELETE',
            description='Desc',
            assigned_user_id='0',
            rfid_identifier='',
            status='normal'
        ))
        with self.app.app_context():
            equip = Equipment.query.filter_by(serial_number='SNDELETE').first()
            equip_id = equip.id
        response = self.client.post(f'/equipments/{equip_id}/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            equip = Equipment.query.get(equip_id)
            self.assertIsNone(equip)

    # ================================================================
    # 4. MODULE RFID
    # ================================================================

    def test_11_rfid_simulation(self):
        """Test: Le simulateur RFID génère des événements."""
        self.login_admin()
        response = self.client.post('/rfid/simulator/detect', json=dict(
            tag_id='RFID-SIM-TEST'
        ))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['tag_id'], 'RFID-SIM-TEST')
        self.assertTrue(data['simulated'])

    def test_12_suspicious_event_detection(self):
        """Test: Détection d'un événement suspect."""
        self.login_admin()
        response = self.client.post('/rfid/simulator/suspicious', json=dict(
            tag_id='RFID-SUSPECT'
        ))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['event_type'], 'suspect')

    def test_13_notification_generation(self):
        """Test: Une notification est créée pour un événement suspect."""
        self.login_admin()
        self.client.post('/rfid/simulator/suspicious', json=dict(
            tag_id='RFID-NOTIF-TEST'
        ))
        with self.app.app_context():
            admin = User.query.filter_by(username='admin').first()
            notifs = Notification.query.filter_by(
                user_id=admin.id
            ).all()
            self.assertTrue(len(notifs) > 0)

    def test_14_notification_reading(self):
        """Test: Marquer une notification comme lue."""
        self.login_admin()
        self.client.post('/rfid/simulator/suspicious', json=dict(
            tag_id='RFID-READ-TEST'
        ))
        with self.app.app_context():
            admin = User.query.filter_by(username='admin').first()
            notif = Notification.query.filter_by(user_id=admin.id).first()
            notif_id = notif.id
            self.assertFalse(notif.is_read)
        response = self.client.post(f'/notifications/{notif_id}/read', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            notif = Notification.query.get(notif_id)
            self.assertTrue(notif.is_read)

    # ================================================================
    # 5. HISTORIQUE DES ÉVÉNEMENTS
    # ================================================================

    def test_15_event_history(self):
        """Test: L'historique des événements est enregistré."""
        self.login_admin()
        self.client.post('/rfid/simulator/detect', json=dict(
            tag_id='RFID-HISTORY'
        ))
        response = self.client.get('/events/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            events = EventHistory.query.filter_by(event_type='rfid_detection').all()
            self.assertTrue(len(events) > 0)

    # ================================================================
    # 6. PARAMÈTRES
    # ================================================================

    def test_16_settings(self):
        """Test: Les paramètres utilisateur sont sauvegardés."""
        self.login_admin()
        response = self.client.post('/settings/update', data=dict(
            language='fr',
            dark_mode='on',
            notifications_enabled='on',
            email_notifications='off',
            location='Bâtiment A'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            admin = User.query.filter_by(username='admin').first()
            settings = UserSettings.query.filter_by(user_id=admin.id).first()
            self.assertTrue(settings.dark_mode)
            self.assertEqual(settings.location, 'Bâtiment A')

    # ================================================================
    # 7. CONTRÔLE D'ACCÈS (ROLES)
    # ================================================================

    def test_17_role_permissions(self):
        """Test: Un utilisateur ordinaire ne peut pas accéder aux routes admin."""
        self.login_user(username='regular', email='regular@test.com', role='user')
        response = self.client.get('/admin/users', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # L'accès doit être refusé (redirection avec message)
        self.assertTrue(b'autoris' in response.data.lower() or b'acces' in response.data.lower())


if __name__ == '__main__':
    unittest.main()
