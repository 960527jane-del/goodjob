import sqlite3
from app.database import get_db_connection

class User:
    @staticmethod
    def get_all():
        """取得所有使用者記錄"""
        try:
            conn = get_db_connection()
            users = conn.execute('SELECT * FROM users').fetchall()
            conn.close()
            return [dict(u) for u in users]
        except sqlite3.Error as e:
            print(f"Database error in User.get_all: {e}")
            return []

    @staticmethod
    def get_by_id(user_id):
        """取得單一使用者記錄"""
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            conn.close()
            return dict(user) if user else None
        except sqlite3.Error as e:
            print(f"Database error in User.get_by_id: {e}")
            return None

    @staticmethod
    def create(username):
        """新增一筆使用者記錄"""
        try:
            conn = get_db_connection()
            cursor = conn.execute('INSERT INTO users (username) VALUES (?)', (username,))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return new_id
        except sqlite3.Error as e:
            print(f"Database error in User.create: {e}")
            return None

    @staticmethod
    def update(user_id, username):
        """更新使用者記錄"""
        try:
            conn = get_db_connection()
            conn.execute('UPDATE users SET username = ? WHERE id = ?', (username, user_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Database error in User.update: {e}")
            return False

    @staticmethod
    def delete(user_id):
        """刪除使用者記錄"""
        try:
            conn = get_db_connection()
            conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Database error in User.delete: {e}")
            return False
