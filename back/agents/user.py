from sqlalchemy import or_
from datetime import datetime, timedelta
from .qiniu import QiniuDeviceClient
from models import User, Device

def search_users_by_phone(phone):
    """模糊搜索用户电话号码"""
    from models import User
    try:
        users = User.query.filter(User.phone.like(f'%{phone}%')).all()
        return [{
            'phone': user.phone,
            'name': user.name,
            'commission_rate': user.commission_rate,
            'superior_name': User.query.get(user.superior_phone).name if user.superior_phone else None,
            'superior_phone': user.superior_phone
        } for user in users]
    except Exception as e:
        print(f"Error searching users: {str(e)}")
        return []

def get_all_users(page=1, per_page=10, superior_phone=None, sort_field=None, sort_order=None):
    """获取所有用户列表"""
    from models import User
    try:
        # 构建基础查询
        query = User.query

        # 如果指定了上级手机号，只返回该上级的下线
        if superior_phone:
            query = query.filter(User.superior_phone == superior_phone)

        # 处理排序
        if sort_field and sort_order and sort_field.strip() and sort_order.strip():
            # 验证排序字段是否合法
            allowed_sort_fields = {
                'first_level_count': User.first_level_count,
                'unwithdrawn_amount': User.unwithdrawn_amount,
                'withdrawn_amount': User.withdrawn_amount,
                'yesterday_income': User.yesterday_income,
                'month_income': User.month_income,
                'team_yesterday_income': User.team_yesterday_income,
                'team_month_income': User.team_month_income,
                'created_at': User.created_at
            }
            
            if sort_field in allowed_sort_fields:
                sort_column = allowed_sort_fields[sort_field]
                if sort_order == 'ascending':
                    query = query.order_by(sort_column.asc())
                else:
                    query = query.order_by(sort_column.desc())
            else:
                # 如果排序字段不合法，使用默认排序（按创建时间倒序）
                query = query.order_by(User.created_at.desc())
        else:
            # 默认排序（按创建时间倒序）
            query = query.order_by(User.created_at.desc())

        # 获取总数
        total = query.count()

        # 分页
        users = query.offset((page - 1) * per_page).limit(per_page).all()

        # 构建返回数据
        items = []
        for user in users:
            superior = User.query.filter_by(phone=user.superior_phone).first() if user.superior_phone else None
            items.append({
                'id': user.phone,
                'phone': user.phone,
                'name': user.name,
                'commission_rate': user.commission_rate,
                'superior_phone': user.superior_phone,
                'superior_name': superior.name if superior else None,
                'first_level_count': user.first_level_count,
                'unwithdrawn_amount': user.unwithdrawn_amount,
                'withdrawn_amount': user.withdrawn_amount,
                'yesterday_income': user.yesterday_income,
                'month_income': user.month_income if user.phone != '13967599865' else get_user_month_income(user.phone),
                'team_yesterday_income': user.team_yesterday_income,
                'team_month_income': user.team_month_income,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })

        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page
        }
    except Exception as e:
        print(f"Error in get_all_users: {str(e)}")
        return {
            'items': [],
            'total': 0,
            'page': page,
            'per_page': per_page
        }

def register_user(data):
    """用户注册"""
    from models import db, User
    # 检查手机号是否已存在
    if User.query.get(data['phone']):
        return False, "手机号已注册"
    
    # 检查上级是否存在
    if data.get('superior_phone'):
        superior = User.query.get(data['superior_phone'])
        if not superior:
            return False, "上级用户不存在"
    
    # 创建新用户
    user = User(
        phone=data['phone'],
        name=data['name'],
        password=data['password'],
        commission_rate=data.get('commission_rate', 0),
        superior_phone=data.get('superior_phone')
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        return True, "注册成功"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def login_user(phone, password):
    """用户登录"""
    from models import User
    user = User.query.get(phone)
    if not user:
        return False, "用户不存在"
    
    if user.password != password:
        return False, "密码错误"
    
    return True, {
        'phone': user.phone,
        'name': user.name,
        'commission_rate': user.commission_rate,
        'superior_phone': user.superior_phone
    }

def delete_user(phone):
    """删除用户"""
    from models import db, User
    user = User.query.get(phone)
    if not user:
        return False, "用户不存在"
    
    try:
        db.session.delete(user)
        db.session.commit()
        return True, "删除成功"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def get_user_month_income(phone):
    """获取用户本月收益"""
    
    # 获取用户的所有设备
    user = User.query.get(phone)
    if not user:
        return 0.0
        
    devices = Device.query.filter_by(phone=phone).all()
    if not devices:
        return 0.0
        
    # 获取本月开始时间
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    
    # 获取所有设备ID
    device_ids = [device.id for device in devices]
    
    # 获取所有设备的账单
    qiniu_client = QiniuDeviceClient()
    bills = qiniu_client.get_device_bills(device_ids, month_start)
    
    # 计算总收益
    return sum(bill['settle_amount'] for bill in bills)

def get_user_yesterday_income(phone):
    """获取用户昨日收益"""
    
    # 获取用户的所有设备
    user = User.query.get(phone)
    if not user:
        return 0.0
        
    devices = Device.query.filter_by(phone=phone).all()
    if not devices:
        return 0.0
        
    # 获取昨天的时间范围
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y%m%d')
    
    # 获取所有设备ID
    device_ids = [device.id for device in devices]
    
    # 获取所有设备的账单
    qiniu_client = QiniuDeviceClient()
    bills = qiniu_client.get_device_bills(device_ids, yesterday)
    
    # 计算总收益
    return sum(bill['settle_amount'] for bill in bills)

def get_team_income(phone, start_time, end_time=None):
    """获取团队收益"""
    from models import User, Device
    from .qiniu import QiniuDeviceClient
    
    # 获取用户及其所有下线
    user = User.query.get(phone)
    if not user:
        return 0.0
        
    # 获取所有下线用户
    def get_all_subordinates(phone):
        subordinates = User.query.filter_by(superior_phone=phone).all()
        result = []
        for sub in subordinates:
            result.append(sub)
            result.extend(get_all_subordinates(sub.phone))
        return result
    
    all_members = [user] + get_all_subordinates(phone)
    if not all_members:
        return 0.0
        
    # 获取所有成员的设备
    all_devices = []
    for member in all_members:
        devices = Device.query.filter_by(phone=member.phone).all()
        all_devices.extend(devices)
    
    if not all_devices:
        return 0.0
        
    # 获取所有设备的账单
    device_ids = [device.id for device in all_devices]
    qiniu_client = QiniuDeviceClient()
    bills = qiniu_client.get_device_bills(device_ids, start_time, end_time)
    
    # 计算总收益
    return sum(bill['settle_amount'] for bill in bills)

def get_team_month_income(phone):
    """获取团队本月收益"""
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    return get_team_income(phone, month_start)

def get_team_yesterday_income(phone):
    """获取团队昨日收益"""
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_start = datetime(yesterday.year, yesterday.month, yesterday.day)
    yesterday_end = yesterday_start + timedelta(days=1)
    return get_team_income(phone, yesterday_start, yesterday_end)

def generate_fake_income():
    """生成模拟收益数据"""
    from models import db, User
    import random
    
    try:
        users = User.query.all()
        for user in users:
            # 生成个人收益
            user.yesterday_income = round(random.uniform(100, 1000), 2)
            user.month_income = round(random.uniform(1000, 10000), 2)
            
            # 生成团队收益（团队收益应该大于个人收益）
            user.team_yesterday_income = round(user.yesterday_income * random.uniform(1.5, 3), 2)
            user.team_month_income = round(user.month_income * random.uniform(1.5, 3), 2)
            
        db.session.commit()
        print("模拟收益数据生成成功")
    except Exception as e:
        db.session.rollback()
        print(f"生成模拟收益数据失败: {str(e)}")