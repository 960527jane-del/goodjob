"""
隨「食」隨地 — 寵物 Model (F-03, F-06)
整合了傳統 F-03 的 Pet class 與 F-06 的 寵物圖鑑/進化資料庫操作
"""
from app.database import get_db_connection, get_db


def map_pet_row(row):
    """將資料庫 user_pets 資料列映射為同時相容 F-03 與 F-06 的格式，並自動計算進度"""
    if not row:
        return None
    d = dict(row)
    # F-03 相容性映射：把 user_pets 欄位映射為 F-03 templates/routes 期望的欄位
    d['name'] = d.get('pet_name')
    d['level'] = d.get('current_level', 1)
    d['exp'] = d.get('current_exp', 0)

    # 計算經驗值升級進度
    from config import EXP_PER_LEVEL_MULTIPLIER
    level = d['level']
    exp_to_next = level * EXP_PER_LEVEL_MULTIPLIER
    
    remaining = d['exp']
    current_l = 1
    while remaining >= (current_l * EXP_PER_LEVEL_MULTIPLIER):
        remaining -= (current_l * EXP_PER_LEVEL_MULTIPLIER)
        current_l += 1
        
    d['exp_to_next_level'] = exp_to_next
    d['exp_remaining'] = remaining
    d['exp_progress'] = round(remaining / exp_to_next * 100, 1) if exp_to_next > 0 else 100
    return d


# ============================================================
# F-06 函數式 API (使用 get_db)
# ============================================================

def get_pet_by_user(user_id):
    """取得使用者的寵物狀態（含種族與當前階段資訊）"""
    db = get_db()
    row = db.execute('''
        SELECT up.*, 
               ps.name AS species_name, ps.element, ps.emoji AS species_emoji,
               ps.color_primary, ps.color_secondary,
               pst.name AS stage_name, pst.emoji AS stage_emoji,
               pst.image_path, pst.stage_order, pst.description AS stage_description
        FROM user_pets up
        JOIN pet_species ps ON up.species_id = ps.id
        JOIN pet_stages pst ON up.current_stage_id = pst.id
        WHERE up.user_id = ?
    ''', (user_id,)).fetchone()
    return map_pet_row(row)


def create_pet(user_id, species_id, pet_name=None):
    """為使用者建立初始寵物"""
    db = get_db()
    
    # 取得該種族的第一階段
    first_stage = db.execute('''
        SELECT id FROM pet_stages 
        WHERE species_id = ? AND stage_order = 1
    ''', (species_id,)).fetchone()

    if not first_stage:
        return None

    if pet_name is None:
        species = db.execute('SELECT name FROM pet_species WHERE id = ?', (species_id,)).fetchone()
        pet_name = species['name'] if species else '寵物'

    db.execute('''
        INSERT OR IGNORE INTO user_pets (user_id, species_id, pet_name, current_level, current_exp, current_stage_id)
        VALUES (?, ?, ?, 1, 0, ?)
    ''', (user_id, species_id, pet_name, first_stage['id']))

    # 自動解鎖第一階段
    db.execute('''
        INSERT OR IGNORE INTO user_collection (user_id, pet_stage_id)
        VALUES (?, ?)
    ''', (user_id, first_stage['id']))

    db.commit()
    return get_pet_by_user(user_id)


def update_pet_level(user_id, new_level, new_exp):
    """更新寵物等級與經驗值"""
    db = get_db()
    db.execute('''
        UPDATE user_pets 
        SET current_level = ?, current_exp = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    ''', (new_level, new_exp, user_id))
    db.commit()


def update_pet_stage(user_id, stage_id):
    """更新寵物的進化階段"""
    db = get_db()
    db.execute('''
        UPDATE user_pets 
        SET current_stage_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    ''', (stage_id, user_id))
    db.commit()


def get_all_species():
    """取得所有寵物種族"""
    db = get_db()
    return db.execute('SELECT * FROM pet_species ORDER BY id').fetchall()


def get_species_by_id(species_id):
    """取得特定種族資訊"""
    db = get_db()
    return db.execute('SELECT * FROM pet_species WHERE id = ?', (species_id,)).fetchone()


# ============================================================
# F-03 物件導向式 API (使用 get_db_connection, 用於 F-03 原有邏輯)
# ============================================================

class Pet:
    @staticmethod
    def create(user_id, name):
        """建立新寵物，回傳新建立的寵物 ID"""
        conn = get_db_connection()
        try:
            # 預設建立 小食怪 種族的寵物
            first_stage = conn.execute('SELECT id FROM pet_stages WHERE species_id = 1 AND stage_order = 1').fetchone()
            stage_id = first_stage['id'] if first_stage else 1
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_pets (user_id, species_id, pet_name, current_level, current_exp, current_stage_id)
                VALUES (?, 1, ?, 1, 0, ?)
            ''', (user_id, name, stage_id))
            
            # 解鎖圖鑑
            cursor.execute('''
                INSERT OR IGNORE INTO user_collection (user_id, pet_stage_id)
                VALUES (?, ?)
            ''', (user_id, stage_id))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_all():
        """取得所有寵物記錄"""
        conn = get_db_connection()
        try:
            rows = conn.execute('''
                SELECT up.*, 
                       ps.name AS species_name, ps.element, ps.emoji AS species_emoji,
                       ps.color_primary, ps.color_secondary,
                       pst.name AS stage_name, pst.emoji AS stage_emoji,
                       pst.image_path, pst.stage_order, pst.description AS stage_description
                FROM user_pets up
                JOIN pet_species ps ON up.species_id = ps.id
                JOIN pet_stages pst ON up.current_stage_id = pst.id
            ''').fetchall()
            return [map_pet_row(row) for row in rows]
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_id(pet_id):
        """根據寵物 ID 取得寵物狀態"""
        conn = get_db_connection()
        try:
            row = conn.execute('''
                SELECT up.*, 
                       ps.name AS species_name, ps.element, ps.emoji AS species_emoji,
                       ps.color_primary, ps.color_secondary,
                       pst.name AS stage_name, pst.emoji AS stage_emoji,
                       pst.image_path, pst.stage_order, pst.description AS stage_description
                FROM user_pets up
                JOIN pet_species ps ON up.species_id = ps.id
                JOIN pet_stages pst ON up.current_stage_id = pst.id
                WHERE up.id = ?
            ''', (pet_id,)).fetchone()
            return map_pet_row(row)
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_user_id(user_id):
        """根據使用者 ID 取得寵物狀態"""
        conn = get_db_connection()
        try:
            row = conn.execute('''
                SELECT up.*, 
                       ps.name AS species_name, ps.element, ps.emoji AS species_emoji,
                       ps.color_primary, ps.color_secondary,
                       pst.name AS stage_name, pst.emoji AS stage_emoji,
                       pst.image_path, pst.stage_order, pst.description AS stage_description
                FROM user_pets up
                JOIN pet_species ps ON up.species_id = ps.id
                JOIN pet_stages pst ON up.current_stage_id = pst.id
                WHERE up.user_id = ?
            ''', (user_id,)).fetchone()
            return map_pet_row(row)
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def update(pet_id, data):
        """更新記錄 (例如更改名稱、經驗值或等級)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 支援傳統 F-03 傳入 exp, level 與 name 的更新
            name = data.get('name') or data.get('pet_name')
            exp = data.get('exp') if data.get('exp') is not None else data.get('current_exp')
            level = data.get('level') if data.get('level') is not None else data.get('current_level')
            stage_id = data.get('current_stage_id')
            
            # 動態拼接 SQL
            fields = []
            params = []
            if name is not None:
                fields.append("pet_name = ?")
                params.append(name)
            if exp is not None:
                fields.append("current_exp = ?")
                params.append(exp)
            if level is not None:
                fields.append("current_level = ?")
                params.append(level)
            if stage_id is not None:
                fields.append("current_stage_id = ?")
                params.append(stage_id)
                
            if not fields:
                return
                
            params.append(pet_id)
            cursor.execute(f'''
                UPDATE user_pets 
                SET {", ".join(fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', tuple(params))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def delete(pet_id):
        """刪除記錄"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM user_pets WHERE id = ?', (pet_id,))
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
        呼叫實作於 evolution_service 的核心進化引擎，並回傳相容 F-03 格式的字典。
        """
        # 1. 先查出 user_id
        conn = get_db_connection()
        try:
            row = conn.execute('SELECT user_id FROM user_pets WHERE id = ?', (pet_id,)).fetchone()
            if not row:
                raise ValueError("Pet not found")
            user_id = row['user_id']
        finally:
            conn.close()

        # 2. 呼叫服務層增加經驗值與處理進化
        from app.services.evolution_service import add_exp as service_add_exp
        res = service_add_exp(user_id, amount)

        # 3. 取出最新狀態並組裝回傳
        updated = Pet.get_by_id(pet_id)
        if updated:
            updated['is_level_up'] = res.get('leveled_up', False)
        return updated
