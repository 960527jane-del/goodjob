import sqlite3
import os
import logging

# 設定資料庫檔案路徑，與 main 同樣使用專案根目錄下的 database.db
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database.db')

class IngredientModel:
    """處理食材庫 (ingredients) 的資料庫操作"""

    @staticmethod
    def get_connection():
        """
        取得資料庫連線。
        確保 instance 目錄存在，並設定 row_factory 讓查詢結果能以 dict 方式存取。
        """
        try:
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logging.error(f"資料庫連線失敗: {e}")
            raise

    @classmethod
    def create(cls, name, quantity, unit, expiry_date=None):
        """
        新增一筆食材記錄。
        
        :param name: 食材名稱 (str)
        :param quantity: 數量 (float)
        :param unit: 單位 (str)
        :param expiry_date: 有效期限，格式 YYYY-MM-DD (str, optional)
        :return: 新增的記錄 ID，失敗則回傳 None
        """
        query = '''
            INSERT INTO ingredients (name, quantity, unit, expiry_date)
            VALUES (?, ?, ?, ?)
        '''
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name, quantity, unit, expiry_date))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logging.error(f"新增食材失敗: {e}")
            return None

    @classmethod
    def get_all(cls):
        """
        取得所有食材記錄，依照有效期限排序 (快過期的在前面)。
        
        :return: 食材記錄的 list (dict 格式)
        """
        query = 'SELECT * FROM ingredients ORDER BY expiry_date ASC, id DESC'
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"取得所有食材失敗: {e}")
            return []

    @classmethod
    def get_by_id(cls, ingredient_id):
        """
        根據 ID 取得單筆食材記錄。
        
        :param ingredient_id: 食材 ID (int)
        :return: 單筆記錄 (dict 格式)，找不到或失敗則回傳 None
        """
        query = 'SELECT * FROM ingredients WHERE id = ?'
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (ingredient_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logging.error(f"取得單筆食材失敗: {e}")
            return None

    @classmethod
    def update(cls, ingredient_id, name, quantity, unit, expiry_date=None):
        """
        更新特定食材記錄。
        
        :param ingredient_id: 食材 ID (int)
        :param name: 食材名稱 (str)
        :param quantity: 數量 (float)
        :param unit: 單位 (str)
        :param expiry_date: 有效期限，格式 YYYY-MM-DD (str, optional)
        :return: 成功與否 (bool)
        """
        query = '''
            UPDATE ingredients
            SET name = ?, quantity = ?, unit = ?, expiry_date = ?
            WHERE id = ?
        '''
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name, quantity, unit, expiry_date, ingredient_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"更新食材失敗: {e}")
            return False

    @classmethod
    def delete(cls, ingredient_id):
        """
        刪除特定食材記錄。
        
        :param ingredient_id: 食材 ID (int)
        :return: 成功與否 (bool)
        """
        query = 'DELETE FROM ingredients WHERE id = ?'
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (ingredient_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"刪除食材失敗: {e}")
            return False
