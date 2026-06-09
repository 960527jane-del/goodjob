import sqlite3
import os
import logging
from config import DATABASE

class IngredientModel:
    """處理食材庫 (ingredients) 的資料庫操作"""

    @classmethod
    def get_connection(cls):
        """
        取得資料庫連線。
        確保資料庫路徑所在目錄存在，並設定 row_factory 讓查詢結果能以 dict 方式存取。
        """
        try:
            os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = sqlite3.Row
            cls._ensure_table_exists(conn)
            return conn
        except Exception as e:
            logging.error(f"資料庫連線失敗: {e}")
            raise

    @classmethod
    def _ensure_table_exists(cls, conn):
        """確保 ingredients 資料表存在。"""
        create_table_sql = '''
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                expiry_date TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        '''
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()

        # 檢查 user_id 欄位是否存在，若不存在則動態新增
        try:
            cursor.execute("PRAGMA table_info(ingredients)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'user_id' not in columns:
                cursor.execute("ALTER TABLE ingredients ADD COLUMN user_id INTEGER DEFAULT 1")
                conn.commit()
        except Exception as e:
            logging.error(f"升級 ingredients 資料表失敗: {e}")

    @classmethod
    def create(cls, user_id, name, quantity, unit, expiry_date=None):
        """
        新增一筆食材記錄。
        
        :param user_id: 使用者 ID (int)
        :param name: 食材名稱 (str)
        :param quantity: 數量 (float)
        :param unit: 單位 (str)
        :param expiry_date: 有效期限，格式 YYYY-MM-DD (str, optional)
        :return: 新增的記錄 ID，失敗則回傳 None
        """
        query = '''
            INSERT INTO ingredients (user_id, name, quantity, unit, expiry_date)
            VALUES (?, ?, ?, ?, ?)
        '''
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_id, name, quantity, unit, expiry_date))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logging.error(f"新增食材失敗: {e}")
            return None

    @classmethod
    def get_all(cls, user_id):
        """
        取得指定使用者的所有食材記錄，依照有效期限排序 (快過期的在前面)。
        
        :param user_id: 使用者 ID (int)
        :return: 食材記錄的 list (dict 格式)
        """
        query = 'SELECT * FROM ingredients WHERE user_id = ? ORDER BY expiry_date ASC, id DESC'
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"取得所有食材失敗: {e}")
            return []

    @classmethod
    def get_by_id(cls, ingredient_id, user_id):
        """
        根據 ID 取得指定使用者的單筆食材記錄。
        
        :param ingredient_id: 食材 ID (int)
        :param user_id: 使用者 ID (int)
        :return: 單筆記錄 (dict 格式)，找不到或失敗則回傳 None
        """
        query = 'SELECT * FROM ingredients WHERE id = ? AND user_id = ?'
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (ingredient_id, user_id))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logging.error(f"取得單筆食材失敗: {e}")
            return None

    @classmethod
    def update(cls, ingredient_id, name, quantity, unit, expiry_date=None, user_id=None):
        """
        更新特定食材記錄。
        
        :param ingredient_id: 食材 ID (int)
        :param name: 食材名稱 (str)
        :param quantity: 數量 (float)
        :param unit: 單位 (str)
        :param expiry_date: 有效期限，格式 YYYY-MM-DD (str, optional)
        :param user_id: 使用者 ID (int, optional)
        :return: 成功與否 (bool)
        """
        if user_id is not None:
            query = '''
                UPDATE ingredients
                SET name = ?, quantity = ?, unit = ?, expiry_date = ?
                WHERE id = ? AND user_id = ?
            '''
            params = (name, quantity, unit, expiry_date, ingredient_id, user_id)
        else:
            query = '''
                UPDATE ingredients
                SET name = ?, quantity = ?, unit = ?, expiry_date = ?
                WHERE id = ?
            '''
            params = (name, quantity, unit, expiry_date, ingredient_id)
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"更新食材失敗: {e}")
            return False

    @classmethod
    def delete(cls, ingredient_id, user_id=None):
        """
        刪除特定食材記錄。
        
        :param ingredient_id: 食材 ID (int)
        :param user_id: 使用者 ID (int, optional)
        :return: 成功與否 (bool)
        """
        if user_id is not None:
            query = 'DELETE FROM ingredients WHERE id = ? AND user_id = ?'
            params = (ingredient_id, user_id)
        else:
            query = 'DELETE FROM ingredients WHERE id = ?'
            params = (ingredient_id,)
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"刪除食材失敗: {e}")
            return False

# Alias for compatibility with F-01 routes and templates
Ingredient = IngredientModel

