"""
数据库迁移脚本：添加结算信息字段
执行命令：python back/migrations/add_payment_info.py
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, User, Device
from config import Config
from flask import Flask
from sqlalchemy import text

def migrate_add_payment_info():
    """添加结算信息字段"""
    app = Flask(__name__)
    
    # 获取当前文件所在目录的绝对路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 数据库文件路径
    DB_PATH = os.path.join(BASE_DIR, 'instance', 'device.db')
    
    # 配置数据库
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
    
    # 初始化数据库
    db.init_app(app)
    
    with app.app_context():
        try:
            # 检查数据库连接
            with db.engine.connect() as conn:
                conn.execute(text('SELECT 1'))
            print("数据库连接成功")
            
            # 添加银行卡字段
            fields_to_add = [
                ('bank_card_number', 'VARCHAR(30)'),
                ('bank_holder_name', 'VARCHAR(50)'),
                ('bank_id_number', 'VARCHAR(20)'),
                ('bank_phone', 'VARCHAR(11)'),
                ('alipay_account', 'VARCHAR(100)'),
                ('alipay_holder_name', 'VARCHAR(50)'),
                ('alipay_id_number', 'VARCHAR(20)'),
                ('alipay_phone', 'VARCHAR(11)')
            ]
            
            for field_name, field_type in fields_to_add:
                try:
                    with db.engine.connect() as conn:
                        conn.execute(text(f'ALTER TABLE users ADD COLUMN {field_name} {field_type}'))
                        conn.commit()
                    print(f"添加 {field_name} 字段成功")
                except Exception as e:
                    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                        print(f"{field_name} 字段已存在，跳过")
                    else:
                        print(f"添加 {field_name} 字段失败: {e}")
            
            print("结算信息字段迁移完成!")
            
        except Exception as e:
            print(f"迁移失败: {e}")
            return False
    
    return True

def migrate_add_history_income():
    """添加历史收益字段"""
    app = Flask(__name__)
    
    # 获取当前文件所在目录的绝对路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 数据库文件路径
    DB_PATH = os.path.join(BASE_DIR, 'instance', 'device.db')
    
    # 配置数据库
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
    
    # 初始化数据库
    db.init_app(app)
    
    with app.app_context():
        try:
            # 检查数据库连接
            with db.engine.connect() as conn:
                conn.execute(text('SELECT 1'))
            print("数据库连接成功")
            
            # 添加历史收益字段
            fields_to_add = [
                # 用户表字段
                ('users', 'history_income', 'JSON'),
                ('users', 'team_history_income', 'JSON'),
                # 设备表字段
                ('devices', 'income_history', 'JSON')
            ]
            
            for table_name, field_name, field_type in fields_to_add:
                try:
                    with db.engine.connect() as conn:
                        # SQLite 的 JSON 类型实际上是作为 TEXT 存储的
                        actual_type = 'TEXT' if field_type == 'JSON' else field_type
                        conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {field_name} {actual_type} DEFAULT "[]"'))
                        conn.commit()
                    print(f"添加 {table_name}.{field_name} 字段成功")
                except Exception as e:
                    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                        print(f"{table_name}.{field_name} 字段已存在，跳过")
                    else:
                        print(f"添加 {table_name}.{field_name} 字段失败: {e}")
            
            print("历史收益字段迁移完成!")
            
        except Exception as e:
            print(f"迁移失败: {e}")
            return False
    
    return True

if __name__ == '__main__':
    # success = migrate_add_payment_info()
    # if success:
    #     print("✅ 迁移成功完成")
    # else:
    #     print("❌ 迁移失败")

    success = migrate_add_history_income()
    if success:
        print("✅ 历史收益字段迁移成功完成")
    else:
        print("❌ 历史收益字段迁移失败") 