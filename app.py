from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Путь к SQLite-базе (в корне проекта)
DB_PATH = 'users.db'

def init_db():
    """Создаёт таблицу при первом запуске."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            auth_date INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Инициализируем БД при старте
init_db()

@app.route('/health', methods=['GET'])
def health():
    """Проверка работоспособности."""
    return jsonify({"status": "ok", "db": "connected"}), 200

@app.route('/auth', methods=['GET'])
def auth_redirect():
    """
    Endpoint для data-auth-url из Telegram Login Widget.
    Telegram перенаправит сюда с параметрами — мы просто принимаем 200 OK.
    """
    return 'OK', 200

@app.route('/save', methods=['POST'])
def save_user():
    """
    Принимает JSON от фронтенда и сохраняет в SQLite.
    """
    try:
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({"success": False, "error": "Invalid data"}), 400

        telegram_id = data['id']
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        username = data.get('username')
        auth_date = data.get('auth_date')

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (telegram_id, first_name, last_name, username, auth_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, first_name, last_name, username, auth_date))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "telegram_id": telegram_id})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Запуск сервера (для локального теста и Render)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)