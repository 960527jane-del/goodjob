from app.database import get_db_connection

class User:
    @staticmethod
    def create(username, email):
        """建立新使用者"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, email) VALUES (?, ?)',
                (username, email)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        """根據 ID 取得使用者"""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        conn.close()
        
        return dict(user) if user else None

    @staticmethod
    def get_by_username(username):
        """根據名稱取得使用者"""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,)
        ).fetchone()
        conn.close()
        
        return dict(user) if user else None
