import sqlite3
import os
from datetime import datetime

# 確保 instance 資料夾存在，並指向正確的資料庫檔案位置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR)

DATABASE = os.path.join(INSTANCE_DIR, 'database.db')

def get_db_connection():
    """建立並回傳資料庫連線"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 讓結果可以像字典一樣透過欄位名稱存取
    return conn

class Ingredient:
    @staticmethod
    def create(name, quantity, unit, expiry_date):
        """新增一筆食材紀錄"""
        conn = get_db_connection()
        created_at = datetime.now().isoformat()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO ingredients (name, quantity, unit, expiry_date, created_at) VALUES (?, ?, ?, ?, ?)',
            (name, quantity, unit, expiry_date, created_at)
        )
        conn.commit()
        lastrowid = cursor.lastrowid
        conn.close()
        return lastrowid

    @staticmethod
    def get_all():
        """取得所有食材紀錄，依建立時間反序排列"""
        conn = get_db_connection()
        items = conn.execute('SELECT * FROM ingredients ORDER BY created_at DESC').fetchall()
        conn.close()
        return [dict(ix) for ix in items]

    @staticmethod
    def get_by_id(ingredient_id):
        """根據 ID 取得單筆食材紀錄"""
        conn = get_db_connection()
        item = conn.execute('SELECT * FROM ingredients WHERE id = ?', (ingredient_id,)).fetchone()
        conn.close()
        return dict(item) if item else None

    @staticmethod
    def update(ingredient_id, name, quantity, unit, expiry_date):
        """更新特定食材紀錄"""
        conn = get_db_connection()
        conn.execute(
            'UPDATE ingredients SET name = ?, quantity = ?, unit = ?, expiry_date = ? WHERE id = ?',
            (name, quantity, unit, expiry_date, ingredient_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(ingredient_id):
        """刪除特定食材紀錄"""
        conn = get_db_connection()
        conn.execute('DELETE FROM ingredients WHERE id = ?', (ingredient_id,))
        conn.commit()
        conn.close()
