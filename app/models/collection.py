"""
圖鑑 Model — 處理寵物圖鑑的 CRUD 操作 (F-06)
"""
from app.database import get_db


def get_all_stages():
    """取得所有進化階段（含種族資訊），按種族與階段排序"""
    db = get_db()
    return db.execute('''
        SELECT pst.*, 
               ps.name AS species_name, ps.element, ps.emoji AS species_emoji,
               ps.color_primary, ps.color_secondary
        FROM pet_stages pst
        JOIN pet_species ps ON pst.species_id = ps.id
        ORDER BY pst.species_id, pst.stage_order
    ''').fetchall()


def get_stages_by_species(species_id):
    """取得特定種族的所有進化階段"""
    db = get_db()
    return db.execute('''
        SELECT pst.*, 
               ps.name AS species_name, ps.element, ps.emoji AS species_emoji,
               ps.color_primary, ps.color_secondary
        FROM pet_stages pst
        JOIN pet_species ps ON pst.species_id = ps.id
        WHERE pst.species_id = ?
        ORDER BY pst.stage_order
    ''', (species_id,)).fetchall()


def get_stage_by_id(stage_id):
    """取得單一進化階段的詳細資訊"""
    db = get_db()
    return db.execute('''
        SELECT pst.*, 
               ps.name AS species_name, ps.element, ps.emoji AS species_emoji,
               ps.color_primary, ps.color_secondary, ps.description AS species_description
        FROM pet_stages pst
        JOIN pet_species ps ON pst.species_id = ps.id
        WHERE pst.id = ?
    ''', (stage_id,)).fetchone()


def get_user_collection(user_id):
    """取得使用者已解鎖的所有階段 ID 集合"""
    db = get_db()
    rows = db.execute('''
        SELECT pet_stage_id FROM user_collection WHERE user_id = ?
    ''', (user_id,)).fetchall()
    return set(row['pet_stage_id'] for row in rows)


def unlock_stage(user_id, stage_id):
    """解鎖新的圖鑑項目"""
    db = get_db()
    db.execute('''
        INSERT OR IGNORE INTO user_collection (user_id, pet_stage_id)
        VALUES (?, ?)
    ''', (user_id, stage_id))
    db.commit()


def is_stage_unlocked(user_id, stage_id):
    """檢查特定階段是否已解鎖"""
    db = get_db()
    row = db.execute('''
        SELECT 1 FROM user_collection 
        WHERE user_id = ? AND pet_stage_id = ?
    ''', (user_id, stage_id)).fetchone()
    return row is not None


def get_collection_progress(user_id):
    """取得圖鑑收集進度"""
    db = get_db()
    total = db.execute('SELECT COUNT(*) AS cnt FROM pet_stages').fetchone()['cnt']
    unlocked = db.execute(
        'SELECT COUNT(*) AS cnt FROM user_collection WHERE user_id = ?',
        (user_id,)
    ).fetchone()['cnt']
    return {'unlocked': unlocked, 'total': total}
