"""
圖鑑路由 — 頁面與 API 端點
Blueprint: collection_bp
"""
from flask import Blueprint, render_template, jsonify, request
from models import pet as pet_model
from models import collection as collection_model
from services import evolution_service
from config import DEV_USER_ID

collection_bp = Blueprint('collection', __name__)


# ============================================================
# 頁面路由
# ============================================================

@collection_bp.route('/collection')
def collection_index():
    """圖鑑主頁面"""
    user_id = DEV_USER_ID
    pet = pet_model.get_pet_by_user(user_id)
    all_stages = collection_model.get_all_stages()
    unlocked_ids = collection_model.get_user_collection(user_id)
    progress = collection_model.get_collection_progress(user_id)
    species_list = pet_model.get_all_species()

    return render_template(
        'collection/index.html',
        pet=pet,
        all_stages=all_stages,
        unlocked_ids=unlocked_ids,
        progress=progress,
        species_list=species_list
    )


@collection_bp.route('/collection/<int:stage_id>')
def collection_detail(stage_id):
    """寵物詳情頁面"""
    user_id = DEV_USER_ID
    stage = collection_model.get_stage_by_id(stage_id)
    if not stage:
        return render_template('collection/index.html'), 404

    is_unlocked = collection_model.is_stage_unlocked(user_id, stage_id)
    all_stages_of_species = collection_model.get_stages_by_species(stage['species_id'])
    unlocked_ids = collection_model.get_user_collection(user_id)
    pet = pet_model.get_pet_by_user(user_id)

    return render_template(
        'collection/detail.html',
        stage=stage,
        is_unlocked=is_unlocked,
        all_stages_of_species=all_stages_of_species,
        unlocked_ids=unlocked_ids,
        pet=pet
    )


# ============================================================
# API 端點
# ============================================================

@collection_bp.route('/api/pet/status', methods=['GET'])
def api_pet_status():
    """取得寵物狀態"""
    user_id = DEV_USER_ID
    status = evolution_service.get_pet_status(user_id)
    if not status:
        return jsonify({'error': '尚未擁有寵物'}), 404
    return jsonify(status)


@collection_bp.route('/api/pet/add-exp', methods=['POST'])
def api_add_exp():
    """增加經驗值（供其他功能模組呼叫）"""
    user_id = DEV_USER_ID
    data = request.get_json()
    if not data or 'exp' not in data:
        return jsonify({'error': '請提供 exp 參數'}), 400

    exp_amount = int(data['exp'])
    if exp_amount <= 0:
        return jsonify({'error': '經驗值必須為正數'}), 400

    result = evolution_service.add_exp(user_id, exp_amount)
    return jsonify(result)


@collection_bp.route('/api/pet/evolve', methods=['POST'])
def api_evolve():
    """手動觸發進化檢查"""
    user_id = DEV_USER_ID
    pet = pet_model.get_pet_by_user(user_id)
    if not pet:
        return jsonify({'error': '尚未擁有寵物'}), 404

    result = evolution_service.check_and_evolve(user_id, pet['current_level'])
    if result:
        return jsonify(result)
    return jsonify({'evolved': False, 'message': '尚未達到進化條件'})


@collection_bp.route('/api/collection', methods=['GET'])
def api_collection():
    """取得圖鑑資料"""
    user_id = DEV_USER_ID
    all_stages = collection_model.get_all_stages()
    unlocked_ids = collection_model.get_user_collection(user_id)
    progress = collection_model.get_collection_progress(user_id)

    stages_data = []
    for s in all_stages:
        stages_data.append({
            'id': s['id'],
            'species_name': s['species_name'],
            'name': s['name'],
            'stage_order': s['stage_order'],
            'level_required': s['level_required'],
            'emoji': s['emoji'],
            'element': s['element'],
            'unlocked': s['id'] in unlocked_ids
        })

    return jsonify({
        'stages': stages_data,
        'progress': progress
    })


@collection_bp.route('/api/collection/<int:stage_id>', methods=['GET'])
def api_collection_detail(stage_id):
    """取得特定階段詳情"""
    user_id = DEV_USER_ID
    stage = collection_model.get_stage_by_id(stage_id)
    if not stage:
        return jsonify({'error': '找不到此階段'}), 404

    is_unlocked = collection_model.is_stage_unlocked(user_id, stage_id)
    return jsonify({
        'id': stage['id'],
        'species_name': stage['species_name'],
        'name': stage['name'] if is_unlocked else '???',
        'stage_order': stage['stage_order'],
        'level_required': stage['level_required'],
        'emoji': stage['emoji'] if is_unlocked else '❓',
        'description': stage['description'] if is_unlocked else '尚未解鎖，繼續加油！',
        'image_path': stage['image_path'] if is_unlocked else None,
        'element': stage['element'],
        'unlocked': is_unlocked
    })
