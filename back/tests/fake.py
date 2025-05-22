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

def generate_user_data(level, parent_phone=None, parent_name=None):
    """生成用户数据"""
    users = []
    if level == 1:
        # 第一层用户
        for _ in range(2):
            phone = generate_phone()
            users.append({
                'phone': phone,
                'name': f'用户{phone[-4:]}',
                'password': hashlib.md5('123456'.encode()).hexdigest(),
                'commission_rate': random.randint(5, 20),
                'superior_phone': None,
                'superior_name': None
            })
    else:
        # 其他层用户，每个上级随机生成0-5个下级
        num_users = random.randint(0, 5)
        for _ in range(num_users):
            phone = generate_phone()
            users.append({
                'phone': phone,
                'name': f'用户{phone[-4:]}',
                'password': hashlib.md5('123456'.encode()).hexdigest(),
                'commission_rate': random.randint(5, 20),
                'superior_phone': parent_phone,
                'superior_name': parent_name
            })
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
                phone=user['phone'],  # 使用字典访问方式
                amount=round(random.uniform(1000, 5000), 2),
                is_returned=False,  # 初始状态为未返现
                is_paid=False,      # 初始状态为未打款
                remark=f"测试设备 {random.randint(1, 100)}",
                commission_rate=random.randint(5, 20)
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
            all_users = []
            
            # 生成第一层用户
            level1_users = []
            for _ in range(2):
                phone = generate_phone()
                user_data = {
                    'phone': phone,
                    'name': f'用户{phone[-4:]}',
                    'password': hashlib.md5('123456'.encode()).hexdigest(),
                    'commission_rate': random.randint(5, 20),
                    'superior_phone': None,
                    'superior_name': None,
                    'first_level_count': 0
                }
                level1_users.append(user_data)
                all_users.append(user_data)
            
            # 生成第二层用户
            level2_users = []
            for user1 in level1_users:
                num_subordinates = random.randint(0, 5)
                user1['first_level_count'] = num_subordinates
                for _ in range(num_subordinates):
                    phone = generate_phone()
                    user_data = {
                        'phone': phone,
                        'name': f'用户{phone[-4:]}',
                        'password': hashlib.md5('123456'.encode()).hexdigest(),
                        'commission_rate': random.randint(5, 20),
                        'superior_phone': user1['phone'],
                        'superior_name': user1['name'],
                        'first_level_count': 0
                    }
                    level2_users.append(user_data)
                    all_users.append(user_data)
            
            # 生成第三层用户
            level3_users = []
            for user2 in level2_users:
                num_subordinates = random.randint(0, 5)
                user2['first_level_count'] = num_subordinates
                for _ in range(num_subordinates):
                    phone = generate_phone()
                    user_data = {
                        'phone': phone,
                        'name': f'用户{phone[-4:]}',
                        'password': hashlib.md5('123456'.encode()).hexdigest(),
                        'commission_rate': random.randint(5, 20),
                        'superior_phone': user2['phone'],
                        'superior_name': user2['name'],
                        'first_level_count': 0
                    }
                    level3_users.append(user_data)
                    all_users.append(user_data)
            
            # 生成第四层用户
            level4_users = []
            for user3 in level3_users:
                num_subordinates = random.randint(0, 5)
                user3['first_level_count'] = num_subordinates
                for _ in range(num_subordinates):
                    phone = generate_phone()
                    user_data = {
                        'phone': phone,
                        'name': f'用户{phone[-4:]}',
                        'password': hashlib.md5('123456'.encode()).hexdigest(),
                        'commission_rate': random.randint(5, 20),
                        'superior_phone': user3['phone'],
                        'superior_name': user3['name'],
                        'first_level_count': 0
                    }
                    level4_users.append(user_data)
                    all_users.append(user_data)
            
            # 统计每层用户数量
            level1_count = len(level1_users)
            level2_count = len(level2_users)
            level3_count = len(level3_users)
            level4_count = len(level4_users)
            
            print(f"总共生成了 {len(all_users)} 个用户")
            print(f"第 1 层: {level1_count} 个用户")
            print(f"第 2 层: {level2_count} 个用户")
            print(f"第 3 层: {level3_count} 个用户")
            print(f"第 4 层: {level4_count} 个用户")
            
            # 保存用户数据
            print("\n正在保存用户数据到数据库...")
            for user_data in all_users:
                user = User(**user_data)
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