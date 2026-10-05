import pandas as pd
from sqlalchemy import create_engine
import pymysql

# 配置
DB_USER = 'root'
DB_PASSWORD = 'Tiomot001!'
DB_HOST = 'localhost'
DB_NAME = 'olist'

# 创建数据库
conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
with conn.cursor() as cur:
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARSET utf8mb4")
conn.close()

# 用 SQLAlchemy 连接
engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4')

# CSV 文件路径（改成你解压的目录）
DATA_DIR = r"C:\Users\Tiomot\Desktop\mysqk\Olist"

# 文件名 -> 表名
files = {
    'olist_orders_dataset.csv': 'orders',
    'olist_order_items_dataset.csv': 'order_items',
    'olist_customers_dataset.csv': 'customers',
    'olist_products_dataset.csv': 'products',
    'olist_sellers_dataset.csv': 'sellers',
    'olist_order_payments_dataset.csv': 'payments',
    'olist_order_reviews_dataset.csv': 'reviews',
}

for filename, table_name in files.items():
    path = f'{DATA_DIR}\\{filename}'
    print(f'导入 {filename} -> {table_name}...')
    df = pd.read_csv(path)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f'  {len(df)} 行')

print('全部导入完成')