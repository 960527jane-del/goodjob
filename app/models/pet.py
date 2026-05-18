from app.database import get_db_connection

# 每 100 經驗值升一級
LEVEL_UP_EXP = 100

class Pet:
    @staticmethod
    def create(user_id, name):
        """建立新寵物"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO pets (user_id, name, exp, level) VALUES (?, ?, 0, 1)',
                (user_id, name)
            )
            conn.commit()
            pet_id = cursor.lastrowid
            return pet_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_user_id(user_id):
        """根據使用者 ID 取得寵物狀態"""
        conn = get_db_connection()
        pet = conn.execute(
            'SELECT * FROM pets WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        conn.close()
        
        return dict(pet) if pet else None
        
    @staticmethod
    def get_by_id(pet_id):
        """根據寵物 ID 取得寵物狀態"""
        conn = get_db_connection()
        pet = conn.execute(
            'SELECT * FROM pets WHERE id = ?',
            (pet_id,)
        ).fetchone()
        conn.close()
        
        return dict(pet) if pet else None

    @staticmethod
    def add_exp(pet_id, amount):
        """
        為寵物增加經驗值，並處理升級邏輯。
        回傳更新後的 pet 字典，並包含 is_level_up 標記。
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 1. 取得目前寵物狀態
            pet = cursor.execute(
                'SELECT exp, level FROM pets WHERE id = ?',
                (pet_id,)
            ).fetchone()
            
            if not pet:
                raise ValueError("Pet not found")
                
            current_exp = pet['exp']
            current_level = pet['level']
            
            # 2. 計算新數值
            new_exp = current_exp + amount
            new_level = current_level
            is_level_up = False
            
            # 簡化的升級邏輯：累積 EXP 每滿 LEVEL_UP_EXP 升一級
            # 若要改為消耗 EXP 升級，此處邏輯需調整 (例如 new_exp -= LEVEL_UP_EXP)
            # 目前採持續累積，依據總經驗值計算等級
            calculated_level = 1 + (new_exp // LEVEL_UP_EXP)
            
            if calculated_level > current_level:
                new_level = calculated_level
                is_level_up = True
                
            # 3. 更新資料庫
            cursor.execute(
                'UPDATE pets SET exp = ?, level = ? WHERE id = ?',
                (new_exp, new_level, pet_id)
            )
            conn.commit()
            
            # 4. 回傳最新狀態
            updated_pet = cursor.execute(
                'SELECT * FROM pets WHERE id = ?',
                (pet_id,)
            ).fetchone()
            
            result = dict(updated_pet)
            result['is_level_up'] = is_level_up
            return result
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
