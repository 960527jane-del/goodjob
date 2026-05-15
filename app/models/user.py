from app.database import get_db_connection

class User:
    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def create(username):
        conn = get_db_connection()
        cursor = conn.execute('INSERT INTO users (username) VALUES (?)', (username,))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
