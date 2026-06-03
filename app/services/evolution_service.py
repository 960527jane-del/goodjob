"""
進化服務 — 核心進化邏輯與經驗值計算 (F-06)
"""
from app.database import get_db
from app.models import pet as pet_model
from app.models import collection as collection_model
from config import EXP_PER_LEVEL_MULTIPLIER


def exp_needed_for_level(level):
    """計算從 level 升到 level+1 所需的經驗值"""
    return level * EXP_PER_LEVEL_MULTIPLIER


def calculate_level_from_exp(total_exp):
    """根據累積經驗值計算等級"""
    level = 1
    remaining = total_exp
    while remaining >= exp_needed_for_level(level):
        remaining -= exp_needed_for_level(level)
        level += 1
    return level, remaining  # (等級, 剩餘經驗值)


def add_exp(user_id, exp_amount):
    """
    增加經驗值，自動處理升級與進化。
    回傳結果字典，包含是否升級、是否進化等資訊。
    """
    pet = pet_model.get_pet_by_user(user_id)
    if not pet:
        return {'success': False, 'error': '找不到寵物'}

    new_total_exp = pet['current_exp'] + exp_amount
    new_level, _ = calculate_level_from_exp(new_total_exp)
    old_level = pet['current_level']
    leveled_up = new_level > old_level

    # 更新等級與經驗值
    pet_model.update_pet_level(user_id, new_level, new_total_exp)

    # 檢查是否觸發進化
    evolution_result = None
    if leveled_up:
        evolution_result = check_and_evolve(user_id, new_level)

    return {
        'success': True,
        'old_level': old_level,
        'new_level': new_level,
        'total_exp': new_total_exp,
        'leveled_up': leveled_up,
        'evolution': evolution_result
    }


def check_and_evolve(user_id, current_level):
    """
    檢查是否達到進化門檻，若達到則執行進化。
    回傳進化結果（含新舊階段資訊），若未進化則回傳 None。
    """
    db = get_db()
    pet = pet_model.get_pet_by_user(user_id)
    if not pet:
        return None

    # 找到該種族中，等級門檻 <= 當前等級的最高階段
    next_stage = db.execute('''
        SELECT * FROM pet_stages 
        WHERE species_id = ? AND level_required <= ?
        ORDER BY stage_order DESC
        LIMIT 1
    ''', (pet['species_id'], current_level)).fetchone()

    if not next_stage or next_stage['id'] == pet['current_stage_id']:
        return None  # 沒有可進化的階段

    # 取得舊階段資訊
    old_stage = collection_model.get_stage_by_id(pet['current_stage_id'])

    # 執行進化
    pet_model.update_pet_stage(user_id, next_stage['id'])
    collection_model.unlock_stage(user_id, next_stage['id'])

    # 同時解鎖中間跳過的階段（處理跨級升等的情況）
    skipped_stages = db.execute('''
        SELECT id FROM pet_stages
        WHERE species_id = ? AND level_required <= ? AND stage_order > ?
        ORDER BY stage_order
    ''', (pet['species_id'], current_level, old_stage['stage_order'])).fetchall()

    for stage in skipped_stages:
        collection_model.unlock_stage(user_id, stage['id'])

    return {
        'evolved': True,
        'old_stage': {
            'id': old_stage['id'],
            'name': old_stage['name'],
            'emoji': old_stage['emoji'],
            'stage_order': old_stage['stage_order']
        },
        'new_stage': {
            'id': next_stage['id'],
            'name': next_stage['name'],
            'emoji': next_stage['emoji'],
            'stage_order': next_stage['stage_order'],
            'image_path': next_stage['image_path'],
            'description': next_stage['description']
        }
    }


def get_pet_status(user_id):
    """取得寵物完整狀態（含進度資訊）"""
    pet = pet_model.get_pet_by_user(user_id)
    if not pet:
        return None

    current_level = pet['current_level']
    exp_to_next = exp_needed_for_level(current_level)
    _, remaining_exp = calculate_level_from_exp(pet['current_exp'])

    return {
        'pet_name': pet['pet_name'],
        'species_name': pet['species_name'],
        'element': pet['element'],
        'species_emoji': pet['species_emoji'],
        'stage_name': pet['stage_name'],
        'stage_emoji': pet['stage_emoji'],
        'stage_order': pet['stage_order'],
        'image_path': pet['image_path'],
        'current_level': current_level,
        'current_exp': pet['current_exp'],
        'exp_to_next_level': exp_to_next,
        'exp_remaining': remaining_exp,
        'exp_progress': round(remaining_exp / exp_to_next * 100, 1) if exp_to_next > 0 else 100,
        'color_primary': pet['color_primary'],
        'color_secondary': pet['color_secondary']
    }
