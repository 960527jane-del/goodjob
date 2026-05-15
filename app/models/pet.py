from app.database import get_db_connection

class Pet:
    # 升級所需的經驗值設定 (可根據需求調整，這裡假設每升一級需要 100 EXP)
    EXP_TO_LEVEL_UP = 100

    @staticmethod
    def get_by_user_id(user_id):
        """根據使用者 ID 取得其寵物狀態"""
        conn = get_db_connection()
        pet = conn.execute('SELECT * FROM pets WHERE user_id = ?', (user_id,)).fetchone()
        conn.close()
        return dict(pet) if pet else None

    @staticmethod
    def create(user_id, name):
        """為使用者建立一隻新寵物"""
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO pets (user_id, name, level, exp) VALUES (?, ?, 1, 0)',
            (user_id, name)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    @staticmethod
    def feed(user_id, exp_gained):
        """
        餵食寵物並增加經驗值，若經驗值滿則自動升級。
        回傳最新的寵物資料與是否升級的布林值。
        """
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
