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

from models import db, User, Device, PlatformStats
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
    # 用于记录每个用户的直接下线数量
    first_level_counts = defaultdict(int)
    
    for i in range(count):
        # 生成手机号
        phone = f"1{random.choice(['3', '5', '7', '8', '9'])}{''.join(random.choices('0123456789', k=9))}"
        
        # 生成姓名
        name = f"用户{random.randint(1000, 9999)}"
        
        # 生成分成比例区间（默认都是0%-20%）
        min_rate = 0
        max_rate = 0.2
        
        # 生成密码（简单起见，使用固定密码）
        password = "123456"
        password = hashlib.md5(password.encode()).hexdigest()
        
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
            unwithdrawn_amount=0,
            withdrawn_amount=0,
            yesterday_income=0,
            month_income=0,
            team_yesterday_income=0,
            team_month_income=0,
            first_level_count=0  # 初始化为0，后面再更新
        )
        users.append(user)
        
        # 如果有上级，更新上级的直接下线数量
        if superior:
            first_level_counts[superior.phone] += 1
    
    # 更新每个用户的直接下线数量
    for user in users:
        user.first_level_count = first_level_counts[user.phone]
    
    return users

def generate_devices(users):
    """生成设备数据"""
    devices = []
    for user in users:
        # 每个用户随机生成1-3个设备
        num_devices = random.randint(1, 3)
        for _ in range(num_devices):
            device = Device(
                device_id=f"device_{random.randint(10000, 99999)}",
                phone=user.phone,  # 使用对象属性访问方式
                amount=100.0,
                is_returned=False,  # 初始状态为未返现
                is_paid=False,      # 初始状态为未打款
                remark=f"测试设备 {random.randint(1, 100)}",
                commission_rate=0.1,
                first_commission_rate=0.1,
                yesterday_income=random.uniform(0, 5),  # 随机生成0-5的昨日收益
                created_at=datetime.utcnow()  # 添加创建时间
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
            PlatformStats.query.delete()  # 清空平台统计数据
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

            # 初始化平台统计数据
            print("\n正在初始化平台统计数据...")
            platform_stats = PlatformStats(
                withdrawn=0,
                unwithdrawn=0,
                total=0,
                commission_total=0,
                device_total=0,
                return_total=0,
                paid_return=0,
                unpaid_return=0
            )
            db.session.add(platform_stats)
            db.session.commit()
            print("平台统计数据初始化成功")
            
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