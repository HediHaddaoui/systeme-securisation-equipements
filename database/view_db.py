import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'securite.db')

if not os.path.exists(db_path):
    print(f"Base de données introuvable : {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("BASE DE DONNÉES SÉCURITÉ ÉQUIPEMENTS")
print("=" * 60)

# Liste des tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"\nNombre de tables : {len(tables)}")
print("-" * 60)

for table in tables:
    table_name = table[0]
    print(f"\nTABLE : {table_name}")
    print("-" * 40)
    
    # Compter les lignes
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Nombre d'enregistrements : {count}")
    
    # Afficher les colonnes
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"Colonnes : {', '.join([c[1] for c in columns])}")
    
    # Afficher les données (limité à 10 lignes)
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
    rows = cursor.fetchall()
    
    if rows:
        print("\nDonnées :")
        for row in rows:
            print(f"  {row}")
    else:
        print("  (aucune donnée)")
    
    print()

conn.close()
print("=" * 60)
print("Fin de l'exploration de la base de données")
