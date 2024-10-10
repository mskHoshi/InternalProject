import sqlite3
import os

# 絶対パスを使用
db_path = os.path.abspath('./assessment_app/data/personnelAssessment.db')
print(f"Database path: {db_path}")

# データベースに接続
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 取得したいテーブルの名前
table_name = 'assessment_ab'

# CREATE文を取得するSQLクエリ
get_create_table_query = f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'"

# SQLクエリを実行
cursor.execute(get_create_table_query)

# CREATE文を取得
create_table_sql = cursor.fetchone()[0]

# CREATE文を表示
print(create_table_sql)

# 接続を閉じる
conn.close()