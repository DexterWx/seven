"""
数据库迁移脚本：添加团队历史总收益字段
执行命令：python back/tests/migrate.py
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, User
from config import Config
from flask import Flask
from sqlalchemy import text

def migrate_add_team_history_sum():
    """添加团队历史总收益字段并初始化"""
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
            
            try:
                with db.engine.connect() as conn:
                    # 添加字段
                    conn.execute(text('ALTER TABLE users ADD COLUMN team_history_sum FLOAT DEFAULT 0'))
                    # 初始化为0
                    conn.execute(text('UPDATE users SET team_history_sum = 0'))
                    conn.commit()
                print("添加并初始化 users.team_history_sum 字段成功")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    # 如果字段已存在，只更新值为0
                    try:
                        with db.engine.connect() as conn:
                            conn.execute(text('UPDATE users SET team_history_sum = 0'))
                            conn.commit()
                        print("users.team_history_sum 字段已存在，已更新为0")
                    except Exception as update_error:
                        print(f"更新 users.team_history_sum 失败: {update_error}")
                else:
                    print(f"添加 users.team_history_sum 字段失败: {e}")
                    return False
            
            print("团队历史总收益字段迁移完成!")
            return True
            
        except Exception as e:
            print(f"迁移失败: {e}")
            return False

def migrate_add_applying_amount():
    """添加申请提现金额字段并初始化"""
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
            
            try:
                with db.engine.connect() as conn:
                    # 添加字段
                    conn.execute(text('ALTER TABLE users ADD COLUMN applying_amount FLOAT DEFAULT 0'))
                    # 初始化为0
                    conn.execute(text('UPDATE users SET applying_amount = 0'))
                    conn.commit()
                print("添加并初始化 users.applying_amount 字段成功")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    # 如果字段已存在，只更新值为0
                    try:
                        with db.engine.connect() as conn:
                            conn.execute(text('UPDATE users SET applying_amount = 0'))
                            conn.commit()
                        print("users.applying_amount 字段已存在，已更新为0")
                    except Exception as update_error:
                        print(f"更新 users.applying_amount 失败: {update_error}")
                else:
                    print(f"添加 users.applying_amount 字段失败: {e}")
                    return False
            
            print("申请提现金额字段迁移完成!")
            return True
            
        except Exception as e:
            print(f"迁移失败: {e}")
            return False

if __name__ == '__main__':
    # success = migrate_add_team_history_sum()
    # if success:
    #     print("✅ 迁移成功完成")
    # else:
    #     print("❌ 迁移失败")

    success = migrate_add_applying_amount()
    if success:
        print("✅ 迁移成功完成")
    else:
        print("❌ 迁移失败")