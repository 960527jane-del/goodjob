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
    """
    建立並回傳資料庫連線
    設定 row_factory 為 sqlite3.Row 讓查詢結果可以像字典一樣透過欄位名稱存取
    """
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"資料庫連線錯誤: {e}")
        return None

class Ingredient:
    @staticmethod
    def create(name, quantity, unit, expiry_date):
        """
        新增一筆食材紀錄
        :param name: 食材名稱
        :param quantity: 數量
        :param unit: 單位
        :param expiry_date: 保存期限 (YYYY-MM-DD)
        :return: 成功時回傳新增資料的 ID，失敗回傳 None
        """
        conn = get_db_connection()
        if not conn: return None
        
        try:
            created_at = datetime.now().isoformat()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO ingredients (name, quantity, unit, expiry_date, created_at) VALUES (?, ?, ?, ?, ?)',
                (name, quantity, unit, expiry_date, created_at)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"新增食材時發生錯誤: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all():
        """
        取得所有食材紀錄，依建立時間反序排列
        :return: 包含字典的 list，若失敗回傳空 list
        """
        conn = get_db_connection()
        if not conn: return []
        
        try:
            items = conn.execute('SELECT * FROM ingredients ORDER BY created_at DESC').fetchall()
            return [dict(ix) for ix in items]
        except sqlite3.Error as e:
            print(f"取得所有食材時發生錯誤: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_by_id(ingredient_id):
        """
        根據 ID 取得單筆食材紀錄
        :param ingredient_id: 食材 ID
        :return: 成功時回傳字典格式的資料，找不到或失敗回傳 None
        """
        conn = get_db_connection()
        if not conn: return None
        
        try:
            item = conn.execute('SELECT * FROM ingredients WHERE id = ?', (ingredient_id,)).fetchone()
            return dict(item) if item else None
        except sqlite3.Error as e:
            print(f"取得單筆食材 (ID: {ingredient_id}) 時發生錯誤: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update(ingredient_id, name, quantity, unit, expiry_date):
        """
        更新特定食材紀錄
        :param ingredient_id: 食材 ID
        :param name: 新名稱
        :param quantity: 新數量
        :param unit: 新單位
        :param expiry_date: 新保存期限
        :return: 成功回傳 True，失敗回傳 False
        """
        conn = get_db_connection()
        if not conn: return False
        
        try:
            conn.execute(
                'UPDATE ingredients SET name = ?, quantity = ?, unit = ?, expiry_date = ? WHERE id = ?',
                (name, quantity, unit, expiry_date, ingredient_id)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新食材 (ID: {ingredient_id}) 時發生錯誤: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(ingredient_id):
        """
        刪除特定食材紀錄
        :param ingredient_id: 食材 ID
        :return: 成功回傳 True，失敗回傳 False
        """
        conn = get_db_connection()
        if not conn: return False
        
        try:
            conn.execute('DELETE FROM ingredients WHERE id = ?', (ingredient_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"刪除食材 (ID: {ingredient_id}) 時發生錯誤: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
