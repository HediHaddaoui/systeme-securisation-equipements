# 🛡️ Système de Sécurisation des Équipements contre le Vol

Application web professionnelle de gestion et de sécurisation des équipements matériels, développée avec **Flask**, **Python** et **SQLite**.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-000?logo=flask)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?logo=sqlite)
![Bootstrap](https://img.shields.io/badge/Frontend-Bootstrap%205-7952B3?logo=bootstrap)
![Tests](https://img.shields.io/badge/Tests-17%20pass%C3%A9s-green)

---

## 📋 Aperçu

Cette application permet de sécuriser les équipements d'une organisation contre le vol grâce à un suivi complet :
- Gestion des utilisateurs avec contrôle d'accès par rôle
- Suivi des matériels avec statuts de sécurité (Normal, À surveiller, Suspect, Volé)
- Module RFID avec simulateur d'événements (détection, perte, suspect, alerte vol)
- Système de notifications en temps réel
- Historique complet des événements avec recherche et filtres
- Interface responsive (mobile + web) avec mode sombre/clair

---

## 🚀 Démarrage rapide

### Prérequis
- Python 3.8+
- pip

### Installation

```bash
# Cloner le dépôt
git clone https://github.com/VOTRE_UTILISATEUR/systeme-securisation-equipements.git
cd systeme-securisation-equipements

# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# ou source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
```

L'application sera accessible à l'adresse : `http://127.0.0.1:5000`

### Identifiants de démonstration

| Champ | Valeur |
|-------|--------|
| Email | `admin@securite.local` |
| Mot de passe | `Admin123!` |

---

## 🧪 Tests

Le projet inclut **17 tests automatisés** couvrant tous les modules :

```bash
pip install pytest
pytest tests/test_app.py -v
```

Résultat attendu : `17 passed`

---

## 🛠️ Stack technique

| Catégorie | Technologies |
|-----------|-------------|
| Backend | Python 3.11, Flask 3, Flask-SQLAlchemy, Flask-Login, Flask-WTF |
| Base de données | SQLite |
| Frontend | HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5, Bootstrap Icons |
| Tests | pytest |
| Sécurité | Werkzeug (hachage scrypt), CSRF protection, Contrôle d'accès par rôle |

---

## 📦 Modules fonctionnels

### Authentification
- Inscription, connexion, déconnexion
- Hachage sécurisé des mots de passe
- Gestion de session
- Contrôle d'accès par rôle (Admin / Utilisateur)
- Routes protégées

### Tableau de bord (Admin)
- Statistiques en temps réel depuis la base de données
- Événements récents et nouveaux utilisateurs

### Gestion des utilisateurs (CRUD complet)
- Ajouter, afficher, rechercher, modifier, supprimer
- Confirmation de suppression

### Gestion des matériels
- CRUD complet avec détails
- Statuts : Normal, À surveiller, Suspect, Volé
- Recherche et filtrage

### Module RFID
- Enregistrement et association de tags RFID
- **Simulateur** avec 4 types d'événements : détection, perte, suspect, alerte vol
- Distinction événements simulés vs réels

### Notifications
- Liste, détails, statut lu/non lu
- Compteur de non lues dans la navbar
- Création automatique pour événements suspects

### Historique des événements
- Type, équipement, utilisateur, date/heure, description, résultat
- Recherche et filtrage avancés

### Paramètres
- Langue, mode sombre/clair, notifications, lieu
- Persistance en base de données

---

## 📱 Design Responsive

L'application est conçue pour fonctionner sur :
- **Ordinateur** : Sidebar de navigation + Navbar supérieure
- **Mobile** : Barre de navigation inférieure (style app native) + Menu hamburger

---

## 🧱 Structure du projet

```
projet_securite/
├── app.py                 # Application Flask
├── config.py              # Configuration
├── models.py              # Modèles SQLAlchemy
├── forms.py               # Formulaires Flask-WTF
├── utils.py               # Utilitaires et décorateurs
├── requirements.txt       # Dépendances
├── README.md              # Documentation
├── run.bat / run.sh       # Scripts de lancement
├── database/              # Base de données SQLite
├── routes/                # Blueprints Flask
│   ├── auth.py            # Authentification
│   ├── dashboard.py       # Tableau de bord
│   ├── admin.py           # Administration
│   ├── equipments.py      # Matériels
│   ├── rfid.py            # Module RFID
│   ├── notifications.py   # Notifications
│   ├── events.py          # Historique
│   ├── profile.py         # Profil
│   └── settings.py        # Paramètres
├── templates/             # Templates Jinja2
├── static/                # CSS, JS, images
├── tests/                 # Tests automatisés (pytest)
└── docs/                  # Documentation et UML
    └── uml/               # Diagrammes Mermaid
```

---

## 📊 Diagrammes UML

Disponibles dans `docs/uml/` au format Mermaid :
- `use_case.mmd` — Cas d'utilisation
- `class.mmd` — Diagramme de classes
- `auth_sequence.mmd` — Séquence d'authentification
- `user_management_sequence.mmd` — Gestion des utilisateurs
- `add_user_sequence.mmd` — Ajout d'utilisateur

---

## 🔒 Sécurité

- Hachage des mots de passe avec Werkzeug (scrypt)
- Authentification via Flask-Login
- Protection CSRF sur tous les formulaires
- Contrôle d'accès par rôle (`@admin_required`)
- Configuration sécurisée des cookies de session
- Validation côté serveur de tous les formulaires

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.


