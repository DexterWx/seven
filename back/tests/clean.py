import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from models import db, User, Device
from app import app

def clean_database():
    """清空数据库中的所有表"""
    try:
        with app.app_context():
            # 删除所有数据
            Device.query.delete()
            User.query.delete()
            
            # 提交更改
            db.session.commit()
            print("数据库已清空")
    except Exception as e:
        print(f"清空数据库时出错: {str(e)}")
        db.session.rollback()

if __name__ == '__main__':
    clean_database() 