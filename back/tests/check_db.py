import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, User, Device
from app import app

def check_database():
    """检查数据库中的记录数"""
    try:
        with app.app_context():
            # 检查用户表
            user_count = User.query.count()
            print(f"数据库中的用户数量：{user_count}")
            
            # 检查设备表
            device_count = Device.query.count()
            print(f"数据库中的设备数量：{device_count}")
            
            # 检查是否有顶级用户（没有上级的用户）
            top_users = User.query.filter_by(superior_phone=None).all()
            print(f"顶级用户数量：{len(top_users)}")
            for user in top_users:
                print(f"顶级用户：{user.name} ({user.phone})")
            
            # 检查每个用户的一级下线数量
            users = User.query.all()
            for user in users:
                first_level = User.query.filter_by(superior_phone=user.phone).count()
                print(f"用户 {user.name} ({user.phone}) 的一级下线数量：{first_level}")
            
    except Exception as e:
        print(f"检查数据库时出错：{str(e)}")

if __name__ == '__main__':
    check_database() 