import sys
from pathlib import Path

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
        # 获取所有用户
        users = User.query.all()
        if not users:
            print("没有找到任何用户")
            return

        # 更新用户昨日收益
        updated_count = 0
        for user in users:
            # 获取用户的所有设备
            devices = Device.query.filter_by(phone=user.phone).all()
            
            # 计算用户昨日收益（所有设备的昨日收益之和）
            yesterday_income = sum(device.yesterday_income for device in devices)
            
            # 更新用户昨日收益
            user.yesterday_income = yesterday_income
            updated_count += 1
            print(f"用户 {user.phone} 昨日收益: {yesterday_income}")

        # 提交数据库更改
        db.session.commit()
        print(f"成功更新 {updated_count} 个用户的昨日收益")

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
                        device.yesterday_income = income['settle_amount'] if income else 0
                        db.session.commit()
                
                print(f"成功处理 {len(batch_devices)} 个设备的账单数据")
                
            except Exception as e:
                print(f"处理批次 {i+1}-{min(i+batch_size, total_devices)} 时出错: {str(e)}")
                continue

        print("所有设备账单数据处理完成")
        
    except Exception as e:
        print(f"获取设备账单数据时出错: {str(e)}")

if __name__ == "__main__":
    with app.app_context():
        get_device_bills_batch()
        calculate_user_income()
