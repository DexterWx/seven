import os
import sys
from pathlib import Path
import random
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from models import db, User, Device
from app import app

def generate_phone():
    """生成随机手机号"""
    prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                '150', '151', '152', '153', '155', '156', '157', '158', '159',
                '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
    return random.choice(prefixes) + ''.join(random.choices('0123456789', k=8))

def generate_device_id():
    """生成唯一的设备ID"""
    # 生成8位随机字符串
    random_str = ''.join(random.choices('0123456789ABCDEF', k=8))
    # 使用UUID的前8位
    uuid_str = str(uuid.uuid4())[:8]
    return f'DEV{uuid_str}{random_str}'

def generate_fake_users(count=50):
    """生成假用户数据"""
    users = []
    for i in range(count):
        # 生成手机号
        phone = f"1{random.choice(['3', '5', '7', '8', '9'])}{''.join(random.choices('0123456789', k=9))}"
        
        # 生成姓名
        name = f"用户{random.randint(1000, 9999)}"
        
        # 生成分成比例区间（默认都是0%-20%）
        min_rate = 0
        max_rate = 20
        
        # 生成密码（简单起见，使用固定密码）
        password = "123456"
        
        # 生成上级（随机选择）
        superior = random.choice(users) if users else None
        
        user = User(
            phone=phone,
            name=name,
            password=password,
            min_commission_rate=min_rate,
            max_commission_rate=max_rate,
            superior_phone=superior.phone if superior else None,
            superior_name=superior.name if superior else None,
            unwithdrawn_amount=random.uniform(0, 10000),
            withdrawn_amount=random.uniform(0, 50000),
            yesterday_income=random.uniform(0, 1000),
            month_income=random.uniform(0, 10000),
            team_yesterday_income=random.uniform(0, 5000),
            team_month_income=random.uniform(0, 50000),
            first_level_count=random.randint(0, 10)
        )
        users.append(user)
    
    return users

def generate_devices(users):
    """生成设备数据"""
    devices = []
    for user in users:
        # 每个用户随机生成1-3个设备
        num_devices = random.randint(1, 3)
        for _ in range(num_devices):
            device = Device(
                id=f"device_{random.randint(10000, 99999)}",
                phone=user.phone,  # 使用对象属性访问方式
                amount=round(random.uniform(1000, 5000), 2),
                is_returned=False,  # 初始状态为未返现
                is_paid=False,      # 初始状态为未打款
                remark=f"测试设备 {random.randint(1, 100)}",
                commission_rate=random.randint(5, 20),
                yesterday_income=random.uniform(0, 5)
            )
            devices.append(device)
    return devices

def init_fake_data():
    """初始化测试数据"""
    print("开始创建测试数据...")
    
    with app.app_context():
        try:
            # 清空现有数据
            Device.query.delete()
            User.query.delete()
            db.session.commit()
            
            # 生成用户数据
            print("正在生成用户数据...")
            all_users = generate_fake_users()
            
            # 统计每层用户数量
            level1_count = len(all_users)
            
            print(f"总共生成了 {len(all_users)} 个用户")
            print(f"第 1 层: {level1_count} 个用户")
            
            # 保存用户数据
            print("\n正在保存用户数据到数据库...")
            for user in all_users:
                db.session.add(user)
            db.session.commit()
            print("用户数据保存成功")
            
            # 生成设备数据
            print("\n正在生成设备数据...")
            devices = generate_devices(all_users)
            print(f"生成了 {len(devices)} 个设备对象")
            
            # 保存设备数据
            print("正在保存设备数据到数据库...")
            for device in devices:
                db.session.add(device)
            db.session.commit()
            print("设备数据保存成功")
            
            print("\n测试数据创建完成！")
            
        except Exception as e:
            print(f"创建测试数据失败: {str(e)}")
            try:
                db.session.rollback()
            except Exception as rollback_error:
                print(f"回滚失败: {str(rollback_error)}")
            raise

if __name__ == '__main__':
    init_fake_data() 