from flask import Flask, request, jsonify
from agents import device_agent, user_agent
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """获取设备列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    phone = request.args.get('phone')
    sort_field = request.args.get('sort_field')
    sort_order = request.args.get('sort_order')
    
    result = device_agent.get_all_devices(page, per_page, phone, sort_field, sort_order)
    return jsonify(result)

@app.route('/api/devices', methods=['POST'])
def add_device():
    """添加设备"""
    data = request.json
    success, message = device_agent.add_device(data)
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/api/devices/<device_id>/phone', methods=['PUT'])
def update_device_phone(device_id):
    """更新设备所属人电话"""
    data = request.json
    success, message = device_agent.update_device_phone(device_id, data['phone'])
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/api/devices/<device_id>/commission', methods=['PUT'])
def update_device_commission(device_id):
    """更新设备分成比例"""
    data = request.json
    success, message = device_agent.update_device_commission(device_id, data['commission_rate'])
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/api/devices/<device_id>/return', methods=['PUT'])
def update_device_return_status(device_id):
    """更新设备返现状态"""
    data = request.json
    success, message = device_agent.update_device_return_status(device_id, data['is_returned'])
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/api/devices/<device_id>/pay', methods=['POST'])
def pay_device(device_id):
    """设备打款"""
    print(f"收到打款请求，设备ID: {device_id}")  # 添加调试日志
    try:
        success, message = device_agent.pay_device(device_id)
        print(f"打款结果: success={success}, message={message}")  # 添加调试日志
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        print(f"打款出错: {str(e)}")  # 添加错误日志
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    """删除设备"""
    success, message = device_agent.delete_device(device_id)
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/api/users/search', methods=['GET'])
def search_users():
    """搜索用户"""
    phone = request.args.get('phone', '')
    users = user_agent.search_users(phone)
    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True) 