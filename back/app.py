from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db
import os
from agents import user, device, profile
from config import Config

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

# 初始化数据库
db.init_app(app)

# 创建数据库表（如果数据库文件不存在）
with app.app_context():
    if not os.path.exists(DB_PATH):
        db.create_all()

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
    data = request.json
    success, message = user.register_user(data)
    return jsonify({'success': success, 'message': message})

@app.route('/api/users/login', methods=['POST'])
def login():
    data = request.json
    success, result = user.login_user(data['phone'], data['password'])
    if success:
        return jsonify({'success': True, 'data': result})
    return jsonify({'success': False, 'message': result})

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 