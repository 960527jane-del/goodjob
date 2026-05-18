from app.database import get_db_connection

class User:
    @staticmethod
    def create(username, email):
        """
        建立新使用者
        :param username: 使用者名稱
        :param email: 電子郵件
        :return: 新建立的使用者 ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, email) VALUES (?, ?)',
                (username, email)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_all():
        """
        取得所有使用者記錄
        :return: 包含所有使用者的 dict 列表
        """
        conn = get_db_connection()
        try:
            users = conn.execute('SELECT * FROM users').fetchall()
            return [dict(u) for u in users]
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        """
        根據 ID 取得使用者
        :param user_id: 使用者 ID
        :return: 使用者資料 dict 或 None
        """
        conn = get_db_connection()
        try:
            user = conn.execute(
                'SELECT * FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            return dict(user) if user else None
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username):
        """
        根據名稱取得使用者
        :param username: 使用者名稱
        :return: 使用者資料 dict 或 None
        """
        conn = get_db_connection()
        try:
            user = conn.execute(
                'SELECT * FROM users WHERE username = ?',
                (username,)
            ).fetchone()
            return dict(user) if user else None
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def update(user_id, data):
        """
        更新使用者記錄
        :param user_id: 欲更新的使用者 ID
        :param data: 包含 'username' 與 'email' 的 dict
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'UPDATE users SET username = ?, email = ? WHERE id = ?',
                (data.get('username'), data.get('email'), user_id)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def delete(user_id):
        """
        刪除記錄
        :param user_id: 欲刪除的使用者 ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
