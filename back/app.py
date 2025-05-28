from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Device
import os
from agents import user, device, profile
from config import Config
import hashlib

app = Flask(__name__)
# 配置 CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 获取当前文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 数据库文件路径
DB_PATH = os.path.join(BASE_DIR, 'instance', 'device.db')
# 确保 instance 目录存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['JSON_AS_ASCII'] = False  # 确保 JSON 响应支持中文

# 初始化数据库
db.init_app(app)

# 创建数据库表（如果数据库文件不存在）
with app.app_context():
    if not os.path.exists(DB_PATH):
        db.create_all()

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok'})

# 设备相关接口
@app.route('/api/devices', methods=['GET'])
def get_devices():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        phone = request.args.get('phone')
        sort_field = request.args.get('sort_field')
        sort_order = request.args.get('sort_order')
        
        result = device.get_all_devices(
            page=page,
            per_page=per_page,
            phone=phone,
            sort_field=sort_field,
            sort_order=sort_order
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices', methods=['POST'])
def add_device():
    data = request.json
    success, message = device.add_device(data)
    return jsonify({'success': success, 'message': message})

@app.route('/api/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    success, message = device.delete_device(device_id)
    return jsonify({'success': success, 'message': message})

@app.route('/api/devices/<device_id>/phone', methods=['PUT'])
def update_device_phone(device_id):
    data = request.json
    success, message = device.update_device_phone(device_id, data['phone'])
    return jsonify({'success': success, 'message': message})

@app.route('/api/devices/<device_id>/commission', methods=['PUT'])
def update_device_commission(device_id):
    data = request.json
    success, message = device.update_device_commission(device_id, data['commission_rate'])
    return jsonify({'success': success, 'message': message})

@app.route('/api/devices/<device_id>/return', methods=['PUT'])
def update_device_return(device_id):
    data = request.json
    success, message = device.update_device_return_status(device_id, data['is_returned'])
    return jsonify({'success': success, 'message': message})

@app.route('/api/devices/<device_id>/pay', methods=['POST'])
def pay_device(device_id):
    """设备打款"""
    success, message = device.pay_device(device_id)
    return jsonify({'success': success, 'message': message})

# 用户相关接口
@app.route('/api/users', methods=['GET'])
def get_users():
    """获取用户列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        superior_phone = request.args.get('superior_phone')
        sort_field = request.args.get('sort_field')
        sort_order = request.args.get('sort_order')
        phone = request.args.get('phone')
        name = request.args.get('name')

        result = user.get_all_users(
            page=page,
            per_page=per_page,
            superior_phone=superior_phone,
            sort_field=sort_field,
            sort_order=sort_order,
            phone=phone,
            name=name
        )
        
        if result is None:
            return jsonify({'error': '获取用户列表失败'}), 500
            
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_users: {str(e)}")
        return jsonify({'error': '获取用户列表失败'}), 500

@app.route('/api/users/<phone>', methods=['DELETE'])
def delete_user(phone):
    success, message = user.delete_user(phone)
    return jsonify({'success': success, 'message': message})

@app.route('/api/users/<phone>', methods=['PUT'])
def update_user(phone):
    """更新用户信息"""
    data = request.get_json()
    success, message = user.update_user(phone, data)
    return jsonify({'success': success, 'error': None if success else message})

@app.route('/api/users/search', methods=['GET'])
def search_users():
    phone = request.args.get('phone', '')
    return jsonify(user.search_users_by_phone(phone))

@app.route('/api/users/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        # 验证必要字段
        if not all(k in data for k in ['phone', 'password']):
            return jsonify({'success': False, 'message': '缺少必要字段'}), 400
            
        success, message = user.register_user(data)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        # 验证必要字段
        if not all(k in data for k in ['phone', 'password']):
            return jsonify({'success': False, 'message': '缺少必要字段'}), 400
            
        success, result = user.login_user(data['phone'], data['password'])
        if success:
            return jsonify({'success': True, 'data': result})
        return jsonify({'success': False, 'message': result}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<phone>/withdraw', methods=['POST'])
def withdraw_user(phone):
    """用户提现"""
    try:
        data = request.get_json()
        amount = data.get('amount', 0)
        if amount <= 0:
            return jsonify({'success': False, 'message': '提现金额必须大于0'}), 400
            
        success, message = user.withdraw_user(phone, amount)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        print(f"Error in withdraw_user: {str(e)}")
        return jsonify({'success': False, 'message': '提现失败'}), 500

@app.route('/api/platform/stats', methods=['GET'])
def get_platform_stats():
    """获取平台统计数据"""
    try:
        stats = profile.get_platform_stats()
        if stats is None:
            return jsonify({'error': '获取平台统计数据失败'}), 500
        return jsonify(stats)
    except Exception as e:
        print(f"Error in get_platform_stats: {str(e)}")
        return jsonify({'error': '获取平台统计数据失败'}), 500

@app.route('/api/platform/withdrawn', methods=['GET'])
def get_withdrawn():
    """获取已提现金额"""
    try:
        result = profile.get_withdrawn_amount()
        if result is None:
            return jsonify({'error': '获取已提现金额失败'}), 500
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_withdrawn: {str(e)}")
        return jsonify({'error': '获取已提现金额失败'}), 500

@app.route('/api/platform/unwithdrawn', methods=['GET'])
def get_unwithdrawn():
    """获取未提现金额"""
    try:
        result = profile.get_unwithdrawn_amount()
        if result is None:
            return jsonify({'error': '获取未提现金额失败'}), 500
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_unwithdrawn: {str(e)}")
        return jsonify({'error': '获取未提现金额失败'}), 500

@app.route('/api/platform/commission', methods=['GET'])
def get_commission():
    """获取抽成总额"""
    result = profile.get_commission_total()
    if result is None:
        return jsonify({'error': '获取抽成总额失败'}), 500
    return jsonify(result)

@app.route('/api/platform/devices/total', methods=['GET'])
def get_device_total():
    """获取设备总额"""
    result = profile.get_device_total()
    if result is None:
        return jsonify({'error': '获取设备总额失败'}), 500
    return jsonify(result)

# 小程序相关接口
@app.route('/api/wechat/users/register', methods=['POST'])
def wechat_register():
    """小程序用户注册"""
    try:
        data = request.get_json()
        # 验证必要字段
        if not all(k in data for k in ['phone', 'password']):
            return jsonify({'success': False, 'message': '缺少必要字段'}), 400
            
        success, message = user.register_user(data)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/wechat/users/login', methods=['POST'])
def wechat_login():
    """小程序用户登录"""
    try:
        data = request.get_json()
        # 验证必要字段
        if not all(k in data for k in ['phone', 'password']):
            return jsonify({'success': False, 'message': '缺少必要字段'}), 400
            
        success, result = user.login_user(data['phone'], data['password'])
        if success:
            return jsonify({'success': True, 'data': result})
        return jsonify({'success': False, 'message': result}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/wechat/users/<phone>', methods=['GET'])
def wechat_get_user_by_phone(phone):
    """小程序通过手机号获取用户信息"""
    try:
        user_obj = User.query.filter_by(phone=phone).first()
        if not user_obj:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        return jsonify({'success': True, 'data': user_obj.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/wechat/users/<phone>/devices/count', methods=['GET'])
def wechat_get_my_device_count(phone):
    """小程序获取我的设备数量"""
    try:
        success, count = device.get_my_device_count(phone)
        if success:
            return jsonify({'success': True, 'count': count})
        return jsonify({'success': False, 'message': '获取设备数量失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/wechat/users/<phone>/subordinate-devices/count', methods=['GET'])
def wechat_get_subordinate_device_count(phone):
    """小程序获取下线设备数量"""
    try:
        success, count = device.get_subordinate_device_count(phone)
        if success:
            return jsonify({'success': True, 'count': count})
        return jsonify({'success': False, 'message': '获取下线设备数量失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/wechat/users/<phone>/devices', methods=['GET'])
def wechat_get_my_devices(phone):
    """小程序获取我的设备列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        success, result = device.get_my_devices(phone, page, per_page)
        if success:
            return jsonify({'success': True, **result})
        return jsonify({'success': False, 'message': '获取设备列表失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/wechat/users/<phone>/subordinate-devices', methods=['GET'])
def wechat_get_subordinate_devices(phone):
    """小程序获取下线设备列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        success, result = device.get_subordinate_devices(phone, page, per_page)
        if success:
            return jsonify({'success': True, **result})
        return jsonify({'success': False, 'message': '获取下线设备列表失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 小程序绑定上线接口
@app.route('/api/wechat/users/bind-superior', methods=['POST'])
def wechat_bind_superior():
    """小程序绑定上线"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        superior_phone = data.get('superior_phone')
        
        if not phone or not superior_phone:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        # 检查用户是否存在
        user_obj = User.query.filter_by(phone=phone).first()
        if not user_obj:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 检查是否已经绑定上线
        if user_obj.superior_phone:
            return jsonify({'success': False, 'message': '已绑定上线，不可修改'}), 400
        
        # 检查上线用户是否存在
        superior_user = User.query.filter_by(phone=superior_phone).first()
        if not superior_user:
            return jsonify({'success': False, 'message': '上线用户不存在'}), 404
        
        # 不能绑定自己
        if phone == superior_phone:
            return jsonify({'success': False, 'message': '不能绑定自己'}), 400
        
        # 更新用户上线信息
        user_obj.superior_phone = superior_phone
        user_obj.superior_name = superior_user.name
        superior_user.first_level_count += 1
        db.session.commit()
        
        return jsonify({'success': True, 'message': '绑定成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 小程序修改密码接口
@app.route('/api/wechat/users/change-password', methods=['POST'])
def wechat_change_password():
    """小程序修改密码"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not all([phone, old_password, new_password]):
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        # 检查用户是否存在
        user_obj = User.query.filter_by(phone=phone).first()
        if not user_obj:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 验证原密码
        if user_obj.password != hashlib.md5(old_password.encode()).hexdigest():
            return jsonify({'success': False, 'message': '原密码错误'}), 400
        
        # 检查新密码长度
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': '新密码长度至少6位'}), 400
        
        # 更新密码
        user_obj.password = hashlib.md5(new_password.encode()).hexdigest()
        db.session.commit()
        
        return jsonify({'success': True, 'message': '密码修改成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 小程序获取结算信息接口
@app.route('/api/wechat/users/<phone>/payment-info', methods=['GET'])
def wechat_get_payment_info(phone):
    """小程序获取结算信息"""
    try:
        user_obj = User.query.filter_by(phone=phone).first()
        if not user_obj:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        payment_info = {
            'bank_card': {
                'card_number': user_obj.bank_card_number,
                'holder_name': user_obj.bank_holder_name,
                'id_number': user_obj.bank_id_number,
                'phone': user_obj.bank_phone
            },
            'alipay': {
                'account': user_obj.alipay_account,
                'holder_name': user_obj.alipay_holder_name,
                'id_number': user_obj.alipay_id_number,
                'phone': user_obj.alipay_phone
            }
        }
        
        return jsonify({'success': True, 'data': payment_info})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 小程序更新银行卡信息接口
@app.route('/api/wechat/users/<phone>/bank-card', methods=['PUT'])
def wechat_update_bank_card(phone):
    """小程序更新银行卡信息"""
    try:
        data = request.get_json()
        
        user_obj = User.query.filter_by(phone=phone).first()
        if not user_obj:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        print(data)
        
        # 更新银行卡信息
        user_obj.bank_card_number = data.get('bank_card_number')
        user_obj.bank_holder_name = data.get('bank_holder_name')
        user_obj.bank_id_number = data.get('bank_id_number')
        user_obj.bank_phone = data.get('bank_phone')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '银行卡信息更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# 小程序更新支付宝信息接口
@app.route('/api/wechat/users/<phone>/alipay', methods=['PUT'])
def wechat_update_alipay(phone):
    """小程序更新支付宝信息"""
    try:
        data = request.get_json()
        
        user_obj = User.query.filter_by(phone=phone).first()
        if not user_obj:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 更新支付宝信息
        user_obj.alipay_account = data.get('alipay_account')
        user_obj.alipay_holder_name = data.get('alipay_holder_name')
        user_obj.alipay_id_number = data.get('alipay_id_number')
        user_obj.alipay_phone = data.get('alipay_phone')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '支付宝信息更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    
# 小程序设置分成比例接口
@app.route('/api/wechat/devices/<device_id>/commission-rate', methods=['PUT'])
def wechat_set_commission_rate(device_id):
    """小程序设置分成比例"""
    try:
        data = request.get_json()
        first_commission_rate = data.get('first_commission_rate')
        
        if not all([first_commission_rate]):
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        device_obj = Device.query.filter_by(device_id=device_id).first()
        if not device_obj:
            return jsonify({'success': False, 'message': '设备不存在'}), 404
        
        device_obj.first_commission_rate = first_commission_rate
        db.session.commit()

        return jsonify({'success': True, 'message': '分成比例设置成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    
@app.route('/api/wechat/devices/<device_id>/phone', methods=['PUT'])
def wechat_update_device_phone(device_id):
    try:
        data = request.get_json()
        phone = data.get('phone')
        
        if not phone:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        success, message = device.update_device_phone(device_id, phone)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/wechat/devices/<device_id>/income-history', methods=['GET'])
def wechat_get_income_history(device_id):
    """小程序获取设备收益历史"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        success, result = device.get_income_history(device_id, page, page_size)
        if not success:
            return jsonify({'success': False, 'message': result}), 500
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 