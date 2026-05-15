import sqlite3
import os

# 預設的資料庫路徑 (對應到架構設計中的 instance/database.db)
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'database.db')

def get_db_connection():
    """建立並回傳與 SQLite 的連線"""
    # 確保 instance 資料夾存在
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    # 將回傳結果設定為字典形式，方便透過欄位名稱存取
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化資料庫並載入 schema.sql"""
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'schema.sql')
    
    if not os.path.exists(schema_path):
        print("找不到 schema.sql 檔案")
        return
        
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
        
    conn = get_db_connection()
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("資料庫初始化完成！")

if __name__ == '__main__':
    # 如果直接執行此腳本，則進行資料庫初始化
    init_db()
