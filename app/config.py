import os
from dotenv import load_dotenv

# 嘗試載入 .env 檔案
load_dotenv()

class Config:
    """系統基礎設定"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_dev_secret_key_here')
    RECIPE_API_KEY = os.getenv('RECIPE_API_KEY', '')
