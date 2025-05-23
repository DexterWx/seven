import sys
from pathlib import Path
from collections import defaultdict

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from datetime import datetime, timedelta
from models import Device, db, User
from qiniu import QiniuDeviceClient
from sqlalchemy import func
from app import app

def calculate_user_income():
    """计算用户昨日收益并更新到数据库"""
    try:
        # 获取所有设备
        devices = Device.query.all()
        if not devices:
            print("没有找到任何设备")
            return

        # 遍历所有设备计算收益
        for device in devices:
            # 获取设备所属用户
            user = User.query.get(device.phone)
            if not user:
                continue

            # 设备原始收益
            device_income = device.yesterday_income
            
            # 1. 平台抽成
            platform_commission = device_income * device.commission_rate
            remaining_income = device_income - platform_commission
            
            # 2. 上级分成
            if user.superior_phone:
                superior = User.query.get(user.superior_phone)
                if superior:
                    superior_share = remaining_income * device.first_commission_rate
                    superior.yesterday_income += superior_share
                    remaining_income -= superior_share
            
            # 3. 用户获得剩余收益
            user.yesterday_income += remaining_income

        # 提交数据库更改
        db.session.commit()
        print("成功更新用户昨日收益")

    except Exception as e:
        db.session.rollback()
        print(f"更新用户昨日收益时出错: {str(e)}")

def get_device_bills_batch():
    """批量获取设备账单数据"""
    try:
        # 获取所有设备
        devices = Device.query.all()
        if not devices:
            print("没有找到任何设备")
            return

        # 获取昨天的日期
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y%m%d')
        print(f"获取 {yesterday_str} 的账单数据")

        # 每100个设备一批
        batch_size = 100
        total_devices = len(devices)
        
        print(f"开始处理 {total_devices} 个设备的账单数据")
        
        # 分批处理
        for i in range(0, total_devices, batch_size):
            batch_devices = devices[i:i + batch_size]
            device_ids = [device.id for device in batch_devices]
            
            print(f"正在处理第 {i+1} 到 {min(i+batch_size, total_devices)} 个设备")
            
            try:
                # 获取账单数据
                qiniu_client = QiniuDeviceClient()
                income_dict = qiniu_client.get_device_income(device_ids, yesterday_str)
                
                # 更新每个设备的昨日收益
                for device_id, income in income_dict.items():
                    device = Device.query.get(device_id)
                    if device:
                        # 记录设备的原始收益
                        original_amount = income['settle_amount'] if income else 0
                        device.yesterday_income = original_amount
                        db.session.commit()
                
                print(f"成功处理 {len(batch_devices)} 个设备的账单数据")
                
            except Exception as e:
                print(f"处理批次 {i+1}-{min(i+batch_size, total_devices)} 时出错: {str(e)}")
                continue

        print("所有设备账单数据处理完成")
        
    except Exception as e:
        print(f"获取设备账单数据时出错: {str(e)}")

def zero_user_yesterday_income():
    """清零所有用户的昨日收益"""
    try:
        # 获取所有用户
        users = User.query.all()
        if not users:
            print("没有找到任何用户")
            return

        # 清零所有用户的昨日收益
        for user in users:
            user.yesterday_income = 0

        # 提交数据库更改
        db.session.commit()
        print("成功清零所有用户的昨日收益")

    except Exception as e:
        db.session.rollback()
        print(f"清零用户昨日收益时出错: {str(e)}")

if __name__ == "__main__":
    with app.app_context():
        get_device_bills_batch()
        zero_user_yesterday_income()  # 先清零
        calculate_user_income()
