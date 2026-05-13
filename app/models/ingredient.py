import sqlite3
import os

# 設定資料庫檔案路徑 (在 instance 資料夾下)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'database.db')

class IngredientModel:
    """處理食材庫 (ingredients) 的資料庫操作"""

    @staticmethod
    def get_connection():
        # 確保 instance 目錄存在
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 讓回傳的資料可以用 dict 的方式存取
        return conn

    @classmethod
    def create(cls, name, quantity, unit, expiry_date=None):
        """新增食材到材料庫"""
        query = '''
            INSERT INTO ingredients (name, quantity, unit, expiry_date)
            VALUES (?, ?, ?, ?)
        '''
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name, quantity, unit, expiry_date))
            conn.commit()
            return cursor.lastrowid

    @classmethod
    def get_all(cls):
        """取得所有食材，依照有效期限排序 (快過期的在前面)"""
        query = 'SELECT * FROM ingredients ORDER BY expiry_date ASC, id DESC'
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def get_by_id(cls, ingredient_id):
        """根據 ID 取得特定食材"""
        query = 'SELECT * FROM ingredients WHERE id = ?'
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (ingredient_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @classmethod
    def update(cls, ingredient_id, name, quantity, unit, expiry_date=None):
        """更新食材資訊"""
        query = '''
            UPDATE ingredients
            SET name = ?, quantity = ?, unit = ?, expiry_date = ?
            WHERE id = ?
        '''
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name, quantity, unit, expiry_date, ingredient_id))
            conn.commit()
            return cursor.rowcount > 0

    @classmethod
    def delete(cls, ingredient_id):
        """刪除食材"""
        query = 'DELETE FROM ingredients WHERE id = ?'
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (ingredient_id,))
            conn.commit()
            return cursor.rowcount > 0
