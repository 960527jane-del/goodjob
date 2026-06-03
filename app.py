import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sql_models import db, User, Pet
from app import create_app

app = create_app()

# ════════════════════════════════════════
#  首頁儀表板 (寵物養成系統)
# ════════════════════════════════════════

@app.route('/')
@login_required
def index():
    user = current_user
    pet = Pet.query.filter_by(user_id=user.id).first()
    if not pet:
        # 如果使用者沒有寵物，自動建立一隻
        pet = Pet(user_id=user.id, name="小寶貝", hunger=100, growth=0)
        db.session.add(pet)
        db.session.commit()
    return render_template('pet_dashboard.html', pet=pet)


# ════════════════════════════════════════
#  餵食 API
# ════════════════════════════════════════

@app.route('/feed', methods=['POST'])
@login_required
def feed():
    user = current_user
    pet = Pet.query.filter_by(user_id=user.id).first()
    if not pet:
        return jsonify({"success": False, "message": "找不到寵物 😢"}), 404
        
    if pet.hunger <= 0:
        return jsonify({"success": False, "message": "寵物已經吃得太飽了，不需要再餵食了 💖"}), 400
        
    # 餵食減少飢餓度 (hunger)，增加成長值 (growth)
    pet.hunger = max(0, pet.hunger - 10)
    pet.growth += 10
    db.session.commit()
    
    return jsonify({
        "success": True,
        "hunger": pet.hunger,
        "growth": pet.growth,
        "message": "餵食成功！成長值 +10，飢餓度 -10 ✨"
    })
