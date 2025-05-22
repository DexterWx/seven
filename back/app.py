from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db
import os
from agents import user, device
from config import Config

app = Flask(__name__)
CORS(app)

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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    return jsonify(device.get_all_devices(page, per_page))

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

        result = user.get_all_users(
            page=page,
            per_page=per_page,
            superior_phone=superior_phone,
            sort_field=sort_field,
            sort_order=sort_order
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

if __name__ == '__main__':
    app.run(debug=True) 