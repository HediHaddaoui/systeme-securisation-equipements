# 🛡️ Système de Sécurisation des Équipements contre le Vol

## 📌 Présentation rapide

Application web complète de gestion et de sécurisation des équipements matériels contre le vol, développée avec **Flask** et **Python**. Interface professionnelle, responsive (mobile + web), avec mode sombre/clair.

## 🎯 Fonctionnalités principales

| Module | Description |
|--------|-------------|
| **Authentification** | Login, logout, inscription, hachage sécurisé des mots de passe, contrôle d'accès par rôle |
| **Tableau de bord** | Statistiques temps réel (utilisateurs, équipements, notifications, événements) |
| **Gestion des utilisateurs** | CRUD complet avec recherche et suppression confirmée |
| **Gestion des équipements** | CRUD avec statuts de sécurité (Normal, À surveiller, Suspect, Volé) |
| **Module RFID** | Enregistrement de tags + simulateur (détection, perte, suspect, alerte vol) |
| **Notifications** | Liste, détails, lu/non lu, compteur, création automatique |
| **Historique** | Journal complet des événements avec recherche et filtres |
| **Profil & Paramètres** | Modification du compte, langue, dark mode, préférences |

## 🛠️ Stack technique

```
Backend:    Python 3.11, Flask 3, Flask-SQLAlchemy, Flask-Login, Flask-WTF
Base de données: SQLite
Frontend:   HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5, Bootstrap Icons
Tests:      pytest (17 tests, tous passés)
Sécurité:   Werkzeug (scrypt), CSRF, RBAC, cookies sécurisés
```

## 📱 Responsive Design

- **Ordinateur** : Sidebar de navigation + Navbar supérieure
- **Mobile** : Barre de navigation inférieure (style app native) + Menu hamburger avec gestes tactiles

## 🧪 Tests

17 tests automatisés couvrant tous les modules : authentification, CRUD, RFID, notifications, historique, paramètres, contrôle d'accès.

```
pytest tests/test_app.py -v
# Résultat: 17 passed
```

## 🔗 Liens

- **GitHub** : [Votre dépôt GitHub]
- **Démo en ligne** : [URL de démo si déployé]

## 👨‍💻 Auteur

Développé par Hedi Haddaoui.
