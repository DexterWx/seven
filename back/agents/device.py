from models import db, Device, User
from sqlalchemy import or_

def get_all_devices(page=1, per_page=10, phone=None, sort_field=None, sort_order=None):
    """获取所有设备列表"""
    try:
        # 构建基础查询
        query = Device.query

        # 如果指定了手机号，进行模糊搜索
        if phone:
            # 先查找匹配的用户
            users = User.query.filter(User.phone.like(f'%{phone}%')).all()
            user_phones = [user.phone for user in users]
            if user_phones:
                query = query.filter(Device.phone.in_(user_phones))
            else:
                # 如果没有找到匹配的用户，返回空结果
                return {
                    'items': [],
                    'total': 0,
                    'page': page,
                    'per_page': per_page
                }

        # 处理排序
        if sort_field and sort_order and sort_field.strip() and sort_order.strip():
            # 验证排序字段是否合法
            allowed_sort_fields = {
                'amount': Device.amount,
                'is_returned': Device.is_returned,
                'is_paid': Device.is_paid,
                'created_at': Device.created_at,
                'yesterday_income': Device.yesterday_income
            }
            
            if sort_field in allowed_sort_fields:
                sort_column = allowed_sort_fields[sort_field]
                if sort_order == 'ascending':
                    query = query.order_by(sort_column.asc())
                else:
                    query = query.order_by(sort_column.desc())
            else:
                # 如果排序字段不合法，使用默认排序（按创建时间倒序）
                query = query.order_by(Device.created_at.desc())
        else:
            # 默认排序（按创建时间倒序）
            query = query.order_by(Device.created_at.desc())

        # 获取总数
        total = query.count()

        # 分页
        devices = query.offset((page - 1) * per_page).limit(per_page).all()

        # 构建返回数据
        items = []
        for device in devices:
            user = User.query.get(device.phone) if device.phone else None
            items.append({
                'id': device.id,
                'device_id': device.device_id,
                'phone': device.phone,
                'user_name': user.name if user else None,
                'amount': device.amount,
                'is_returned': device.is_returned,
                'is_paid': device.is_paid,
                'remark': device.remark,
                'commission_rate': device.commission_rate,
                'first_commission_rate': device.first_commission_rate,
                'yesterday_income': device.yesterday_income,
                'created_at': device.created_at.isoformat() if device.created_at else None
            })

        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page
        }
    except Exception as e:
        print(f"Error in get_all_devices: {str(e)}")
        return {
            'items': [],
            'total': 0,
            'page': page,
            'per_page': per_page
        }

def update_device_phone(device_id, phone):
    """更新设备所属人电话"""
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return False, "设备不存在"
    
    # 检查用户是否存在
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return False, "用户不存在"
    
    try:
        device.phone = phone
        db.session.commit()
        return True, "更新成功"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def update_device_commission(device_id, commission_rate):
    """更新设备分成比例"""
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return False, "设备不存在"
    
    if not 0 <= commission_rate <= 1:
        return False, "分成比例必须在0-1之间"
    
    try:
        device.commission_rate = commission_rate
        db.session.commit()
        return True, "更新成功"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def update_device_return_status(device_id, is_returned):
    """更新设备返现状态"""
    try:
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return False, "设备不存在"
            
        device.is_returned = is_returned
        db.session.commit()
        
        return True, "返现状态更新成功"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def add_device(data):
    """添加新设备"""
    # 检查设备ID是否已存在
    if Device.query.get(data['device_id']):
        return False, "设备ID已存在"
    
    device = Device(
        device_id=data['device_id'],
        amount=data['amount'],
        remark=data.get('remark', '')
    )
    
    try:
        db.session.add(device)
        db.session.commit()
        return True, "添加成功"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def delete_device(device_id):
    """删除设备"""
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return False, "设备不存在"
    
    try:
        db.session.delete(device)
        db.session.commit()
        return True, "删除成功"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def pay_device(device_id):
    """设备打款"""
    try:
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return False, "设备不存在"
            
        device.is_paid = not device.is_paid
        db.session.commit()
        
        return True, "打款状态更新成功"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def get_my_device_count(phone):
    """获取我的设备数量"""
    try:
        count = Device.query.filter_by(phone=phone).count()
        return True, count
    except Exception as e:
        print(f"Error in get_my_device_count: {str(e)}")
        return False, 0

def get_subordinate_device_count(phone):
    """获取下线设备数量"""
    try:
        # 先在用户库里找到所有上级phone是我的phone的用户
        subordinates = User.query.filter_by(superior_phone=phone).all()
        subordinate_phones = [user.phone for user in subordinates]
        
        if not subordinate_phones:
            return True, 0
        
        # 去设备库里找到所有phone在这些用户phone中的设备
        count = Device.query.filter(Device.phone.in_(subordinate_phones)).count()
        return True, count
    except Exception as e:
        print(f"Error in get_subordinate_device_count: {str(e)}")
        return False, 0

def get_my_devices(phone, page=1, per_page=10):
    """获取我的设备列表（分页）"""
    try:
        # 构建查询
        query = Device.query.filter_by(phone=phone)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        devices = query.offset((page - 1) * per_page).limit(per_page).all()
        
        result = []
        
        # 获取用户信息
        user = User.query.filter_by(phone=phone).first()
        user_name = user.name if user else phone
        
        for device in devices:
            device_dict = device.to_dict()
            device_dict['user_name'] = user_name
            result.append(device_dict)
        
        return True, {
            'data': result,
            'total': total,
            'page': page,
            'per_page': per_page
        }
    except Exception as e:
        print(f"Error in get_my_devices: {str(e)}")
        return False, []

def get_subordinate_devices(phone, page=1, per_page=10):
    """获取下线设备列表（分页）"""
    try:
        # 先找到所有下线用户
        subordinates = User.query.filter_by(superior_phone=phone).all()
        subordinate_phones = [user.phone for user in subordinates]
        
        if not subordinate_phones:
            return True, {
                'data': [],
                'total': 0,
                'page': page,
                'per_page': per_page
            }
        
        # 构建查询
        query = Device.query.filter(Device.phone.in_(subordinate_phones))
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        devices = query.offset((page - 1) * per_page).limit(per_page).all()
        
        result = []
        
        # 构建用户名映射
        user_map = {user.phone: user.name for user in subordinates}
        
        for device in devices:
            device_dict = device.to_dict()
            device_dict['user_name'] = user_map.get(device.phone, device.phone)
            result.append(device_dict)
        
        return True, {
            'data': result,
            'total': total,
            'page': page,
            'per_page': per_page
        }
    except Exception as e:
        print(f"Error in get_subordinate_devices: {str(e)}")
        return False, [] 

def get_income_history(device_id):
    """获取设备收益历史"""
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return False, "设备不存在"
    return True, device.income_history