from app.database import get_db_connection

# 每 100 經驗值升一級
LEVEL_UP_EXP = 100

class Pet:
    @staticmethod
    def create(user_id, name):
        """
        建立新寵物
        :param user_id: 主人的使用者 ID
        :param name: 寵物名稱
        :return: 新建立的寵物 ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO pets (user_id, name, exp, level) VALUES (?, ?, 0, 1)',
                (user_id, name)
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
        取得所有寵物記錄
        :return: 包含所有寵物的 dict 列表
        """
        conn = get_db_connection()
        try:
            pets = conn.execute('SELECT * FROM pets').fetchall()
            return [dict(p) for p in pets]
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_id(pet_id):
        """
        根據寵物 ID 取得寵物狀態
        :param pet_id: 寵物 ID
        :return: 寵物資料 dict 或 None
        """
        conn = get_db_connection()
        try:
            pet = conn.execute(
                'SELECT * FROM pets WHERE id = ?',
                (pet_id,)
            ).fetchone()
            return dict(pet) if pet else None
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_user_id(user_id):
        """
        根據使用者 ID 取得寵物狀態
        :param user_id: 主人的使用者 ID
        :return: 寵物資料 dict 或 None
        """
        conn = get_db_connection()
        try:
            pet = conn.execute(
                'SELECT * FROM pets WHERE user_id = ?',
                (user_id,)
            ).fetchone()
            return dict(pet) if pet else None
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def update(pet_id, data):
        """
        更新記錄 (例如更改名稱、經驗值或等級)
        :param pet_id: 寵物 ID
        :param data: 包含欲更新欄位資料的 dict
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 這裡簡化實作，假設外部會傳入完整的欲更新資料
            # 實際應用中可依據傳入的 keys 動態組裝 SQL
            cursor.execute(
                'UPDATE pets SET name = ?, exp = ?, level = ? WHERE id = ?',
                (data.get('name'), data.get('exp'), data.get('level'), pet_id)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def delete(pet_id):
        """
        刪除記錄
        :param pet_id: 欲刪除的寵物 ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM pets WHERE id = ?', (pet_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def add_exp(pet_id, amount):
        """
        為寵物增加經驗值，並處理升級邏輯。
        回傳更新後的 pet 字典，並包含 is_level_up 標記。
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            pet = cursor.execute(
                'SELECT exp, level FROM pets WHERE id = ?',
                (pet_id,)
            ).fetchone()
            
            if not pet:
                raise ValueError("Pet not found")
                
            current_exp = pet['exp']
            current_level = pet['level']
            
            new_exp = current_exp + amount
            new_level = current_level
            is_level_up = False
            
            # 每累積滿 LEVEL_UP_EXP 點數，等級為 1 + 總經驗值 // 門檻
            calculated_level = 1 + (new_exp // LEVEL_UP_EXP)
            
            if calculated_level > current_level:
                new_level = calculated_level
                is_level_up = True
                
            cursor.execute(
                'UPDATE pets SET exp = ?, level = ? WHERE id = ?',
                (new_exp, new_level, pet_id)
            )
            conn.commit()
            
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
