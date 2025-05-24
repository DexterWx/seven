from sqlalchemy import or_
from datetime import datetime, timedelta
from .qiniu import QiniuDeviceClient
from models import User, Device, db
import hashlib

def search_users_by_phone(phone):
    """模糊搜索用户电话号码"""
    from models import User
    try:
        users = User.query.filter(User.phone.like(f'%{phone}%')).all()
        return [user.phone for user in users]
    except Exception as e:
        print(f"Error searching users: {str(e)}")
        return []

def get_all_users(page=1, per_page=10, superior_phone=None, sort_field=None, sort_order=None, phone=None, name=None):
    """获取所有用户列表"""
    from models import User
    try:
        # 构建基础查询
        query = User.query

        # 如果指定了上级手机号，只返回该上级的下线
        if superior_phone:
            query = query.filter(User.superior_phone == superior_phone)

        # 处理手机号搜索
        if phone:
            query = query.filter(User.phone.like(f'%{phone}%'))

        # 处理姓名搜索
        if name:
            query = query.filter(User.name.like(f'%{name}%'))

        # 处理排序
        if sort_field and sort_order and sort_field.strip() and sort_order.strip():
            # 验证排序字段是否合法
            allowed_sort_fields = {
                'unwithdrawn_amount': User.unwithdrawn_amount,
                'withdrawn_amount': User.withdrawn_amount,
                'yesterday_income': User.yesterday_income,
                'month_income': User.month_income,
                'team_yesterday_income': User.team_yesterday_income,
                'team_month_income': User.team_month_income,
                'created_at': User.created_at,
                'first_level_count': User.first_level_count
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
            items.append({
                'phone': user.phone,
                'name': user.name,
                'min_commission_rate': user.min_commission_rate,
                'max_commission_rate': user.max_commission_rate,
                'superior_name': user.superior_name,
                'superior_phone': user.superior_phone,
                'unwithdrawn_amount': user.unwithdrawn_amount,
                'withdrawn_amount': user.withdrawn_amount,
                'yesterday_income': user.yesterday_income,
                'month_income': user.month_income,
                'team_yesterday_income': user.team_yesterday_income,
                'team_month_income': user.team_month_income,
                'first_level_count': user.first_level_count,
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
        return None

def register_user(data):
    """注册新用户"""
    try:
        # 检查手机号是否已存在
        if User.query.filter_by(phone=data['phone']).first():
            return False, "手机号已存在"
        
        # 密码加密
        password = hashlib.md5(data['password'].encode()).hexdigest()
        
        # 创建新用户
        user = User(
            phone=data['phone'],
            password=password,
            name=data.get('name', data['phone'])  # 如果没有提供名字，使用手机号作为默认名字
        )
        
        db.session.add(user)
        db.session.commit()
        return True, "注册成功"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def login_user(phone, password):
    """用户登录"""
    try:
        # 查找用户
        user = User.query.filter_by(phone=phone).first()
        if not user:
            return False, "用户不存在"
        
        # 验证密码
        if user.password != hashlib.md5(password.encode()).hexdigest():
            return False, "密码错误"
        
        # 更新最后登录时间
        user.last_login = datetime.now()
        db.session.commit()
        
        return True, user.to_dict()
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def delete_user(phone):
    """删除用户"""
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return False, "用户不存在"
    
    try:
        db.session.delete(user)
        db.session.commit()
        return True, "删除成功"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def update_user(phone, data):
    """更新用户信息"""
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return False, "用户不存在"
    
    try:
        # 更新基本信息
        if 'name' in data:
            user.name = data['name']
        if 'min_commission_rate' in data:
            user.min_commission_rate = data['min_commission_rate']
        if 'max_commission_rate' in data:
            user.max_commission_rate = data['max_commission_rate']
            
        # 更新上级信息
        if 'superior_phone' in data:
            superior = User.query.filter_by(phone=data['superior_phone']).first()
            if not superior:
                return False, "上级用户不存在"
            user.superior_phone = superior.phone
            user.superior_name = superior.name
            
        db.session.commit()
        return True, "更新成功"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def withdraw_user(phone, amount):
    """用户提现"""
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return False, "用户不存在"
    
    if amount > user.unwithdrawn_amount:
        return False, "提现金额不能大于未提现金额"
    
    try:
        user.unwithdrawn_amount -= amount
        user.withdrawn_amount += amount
        db.session.commit()
        return True, "提现成功"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def get_user_info(user_id):
    """获取用户信息"""
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return False, "用户不存在"
    
    return True, user.to_dict()