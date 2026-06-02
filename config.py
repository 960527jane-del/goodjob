"""
隨「食」隨地 — 專案設定檔
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 資料庫設定
DATABASE = os.path.join(BASE_DIR, 'instance', 'goodjob.db')

# Flask 設定
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# 開發階段：硬編碼使用者 ID（待登入模組完成後替換）
DEV_USER_ID = 1

# 寵物系統設定
EXP_PER_LEVEL_MULTIPLIER = 50  # 每級所需經驗值 = 等級 × 此值
