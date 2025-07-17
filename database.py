import sqlite3

conn = sqlite3.connect("finance.db")
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        amount REAL,
        period TEXT,
        category TEST,
        description TEXT
    )
''')

conn.commit()

def add_transaction(user_id, t_type, amount, period, category, description):
    c.execute('''
        INSERT INTO transactions (user_id, type, amount, period, category, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, t_type, amount, period, category, description))
    conn.commit()

def get_transactions(user_id):
    c.execute("SELECT id, type, amount, period, description, category FROM transactions WHERE user_id = ?", (user_id,))
    return c.fetchall()

def delete_transaction(transaction_id, user_id):
    c.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id))
    conn.commit()

def update_transaction(transaction_id, amount):
    c.execute("UPDATE transactions SET amount = ? WHERE id = ?", (amount, transaction_id))
    conn.commit()

def get_all_telegram_ids():
    c.execute("SELECT telegram_id FROM users")
    return [row[0] for row in c.fetchall()]