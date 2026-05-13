"""
寵物 Model — 處理寵物狀態的 CRUD 操作
"""
from models.db import get_db


def get_pet_by_user(user_id):
    """取得使用者的寵物狀態（含種族與當前階段資訊）"""
    db = get_db()
    return db.execute('''
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
        INSERT INTO user_pets (user_id, species_id, pet_name, current_level, current_exp, current_stage_id)
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
