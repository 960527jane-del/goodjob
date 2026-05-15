import sqlite3
from app.database import get_db_connection

class Pet:
    # 升級所需的經驗值設定
    EXP_TO_LEVEL_UP = 100

    @staticmethod
    def get_all():
        """取得所有寵物記錄"""
        try:
            conn = get_db_connection()
            pets = conn.execute('SELECT * FROM pets').fetchall()
            conn.close()
            return [dict(p) for p in pets]
        except sqlite3.Error as e:
            print(f"Database error in Pet.get_all: {e}")
            return []

    @staticmethod
    def get_by_id(pet_id):
        """取得單一寵物記錄"""
        try:
            conn = get_db_connection()
            pet = conn.execute('SELECT * FROM pets WHERE id = ?', (pet_id,)).fetchone()
            conn.close()
            return dict(pet) if pet else None
        except sqlite3.Error as e:
            print(f"Database error in Pet.get_by_id: {e}")
            return None

    @staticmethod
    def get_by_user_id(user_id):
        """根據使用者 ID 取得其寵物狀態"""
        try:
            conn = get_db_connection()
            pet = conn.execute('SELECT * FROM pets WHERE user_id = ?', (user_id,)).fetchone()
            conn.close()
            return dict(pet) if pet else None
        except sqlite3.Error as e:
            print(f"Database error in Pet.get_by_user_id: {e}")
            return None

    @staticmethod
    def create(user_id, name):
        """為使用者建立一隻新寵物"""
        try:
            conn = get_db_connection()
            cursor = conn.execute(
                'INSERT INTO pets (user_id, name, level, exp) VALUES (?, ?, 1, 0)',
                (user_id, name)
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return new_id
        except sqlite3.Error as e:
            print(f"Database error in Pet.create: {e}")
            return None

    @staticmethod
    def update(pet_id, data):
        """更新寵物記錄 (如修改名字)"""
        try:
            name = data.get('name')
            if not name:
                return False
                
            conn = get_db_connection()
            conn.execute(
                'UPDATE pets SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (name, pet_id)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Database error in Pet.update: {e}")
            return False

    @staticmethod
    def delete(pet_id):
        """刪除寵物記錄"""
        try:
            conn = get_db_connection()
            conn.execute('DELETE FROM pets WHERE id = ?', (pet_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Database error in Pet.delete: {e}")
            return False

    @staticmethod
    def feed(user_id, exp_gained):
        """
        餵食寵物並增加經驗值，若經驗值滿則自動升級。
        回傳最新的寵物資料與是否升級的布林值。
        """
        try:
            conn = get_db_connection()
            pet = conn.execute('SELECT * FROM pets WHERE user_id = ?', (user_id,)).fetchone()
            
            if not pet:
                conn.close()
                return None, False

            current_level = pet['level']
            current_exp = pet['exp']
            new_exp = current_exp + exp_gained
            
            is_level_up = False

            # 處理升級邏輯
            if new_exp >= Pet.EXP_TO_LEVEL_UP:
                new_exp = new_exp - Pet.EXP_TO_LEVEL_UP
                current_level += 1
                is_level_up = True

            # 更新資料庫
            conn.execute(
                'UPDATE pets SET level = ?, exp = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (current_level, new_exp, pet['id'])
            )
            conn.commit()
            
            # 重新獲取最新的寵物狀態
            updated_pet = conn.execute('SELECT * FROM pets WHERE id = ?', (pet['id'],)).fetchone()
            conn.close()

            return dict(updated_pet), is_level_up
        except sqlite3.Error as e:
            print(f"Database error in Pet.feed: {e}")
            return None, False
