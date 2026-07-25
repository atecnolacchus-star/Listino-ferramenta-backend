"""
seed.py — crea (o ricrea) il database SQLite con schema, account di default
e catalogo importato da products.json (lo stesso listino già caricato
nell'app front-end).

Uso:
    python3 seed.py            # crea ferramenta.db se non esiste
    python3 seed.py --force    # ricrea da zero anche se esiste già
"""
import sqlite3
import json
import sys
import os

from security import hash_password

DB_PATH = os.path.join(os.path.dirname(__file__), 'ferramenta.db')
PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), 'products.json')

DEFAULT_ACCOUNTS = [
    # id, name, role, username, password
    ('master', 'Master', 'master', 'master', 'Master2026!'),
    ('std1', 'Standard 1', 'standard', 'standard1', 'Standard1!'),
    ('std2', 'Standard 2', 'standard', 'standard2', 'Standard2!'),
    ('std3', 'Standard 3', 'standard', 'standard3', 'Standard3!'),
    ('std4', 'Standard 4', 'standard', 'standard4', 'Standard4!'),
    ('std5', 'Standard 5', 'standard', 'standard5', 'Standard5!'),
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('master','standard')),
    username TEXT NOT NULL UNIQUE,
    salt TEXT NOT NULL,
    pass_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    discount TEXT
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    code TEXT NOT NULL UNIQUE,
    descr TEXT NOT NULL,
    price REAL NOT NULL DEFAULT 0,
    unit TEXT DEFAULT 'pz',
    discount TEXT,
    sub TEXT,
    classe TEXT
);
CREATE INDEX IF NOT EXISTS idx_items_code ON items(code);
CREATE INDEX IF NOT EXISTS idx_items_classe ON items(classe);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category_id);

CREATE TABLE IF NOT EXISTS quotes (
    id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL REFERENCES accounts(id),
    owner_name TEXT NOT NULL,
    client TEXT NOT NULL,
    order_info TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('Offerta','Preventivo')),
    status TEXT NOT NULL DEFAULT 'Da confermare',
    items TEXT NOT NULL,
    totals TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_quotes_owner ON quotes(owner_id);
"""


def seed(force=False):
    if force and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Rimosso database esistente: {DB_PATH}")

    is_new = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    cur = conn.execute("SELECT COUNT(*) FROM accounts")
    if cur.fetchone()[0] == 0:
        for acc_id, name, role, username, plain_pwd in DEFAULT_ACCOUNTS:
            salt, pass_hash = hash_password(plain_pwd)
            conn.execute(
                "INSERT INTO accounts (id, name, role, username, salt, pass_hash) VALUES (?,?,?,?,?,?)",
                (acc_id, name, role, username, salt, pass_hash)
            )
        print(f"Creati {len(DEFAULT_ACCOUNTS)} account di default.")
    else:
        print("Account già presenti, non sovrascritti.")

    cur = conn.execute("SELECT COUNT(*) FROM categories")
    if cur.fetchone()[0] == 0:
        if not os.path.exists(PRODUCTS_PATH):
            print(f"ATTENZIONE: {PRODUCTS_PATH} non trovato, catalogo vuoto.")
        else:
            with open(PRODUCTS_PATH, encoding='utf-8') as f:
                categories = json.load(f)
            n_items = 0
            for cat in categories:
                cur = conn.execute(
                    "INSERT INTO categories (name, discount) VALUES (?,?)",
                    (cat['name'], cat.get('discount', ''))
                )
                cat_id = cur.lastrowid
                for it in cat['items']:
                    conn.execute(
                        """INSERT OR IGNORE INTO items
                           (category_id, code, descr, price, unit, discount, sub, classe)
                           VALUES (?,?,?,?,?,?,?,?)""",
                        (cat_id, it['code'], it['desc'], it.get('price', 0),
                         it.get('unit', 'pz'), it.get('discount', ''),
                         it.get('sub', ''), it.get('classe', 'Altro'))
                    )
                    n_items += 1
            print(f"Importate {len(categories)} categorie e {n_items} articoli da products.json.")
    else:
        print("Catalogo già presente, non reimportato (usa --force per rifare da zero).")

    conn.commit()
    conn.close()
    print(f"Database pronto: {DB_PATH}")


if __name__ == '__main__':
    seed(force='--force' in sys.argv)
