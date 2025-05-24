import requests
import json
import argparse

def test_register():
    """测试用户注册"""
    url = "http://localhost:5001/api/wechat/users/register"
    data = {
        "phone": "17643495101",
        "password": "123456",
        "name": "测试用户2"
    }
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))

def test_login(phone, password):
    """测试用户登录"""
    url = "http://localhost:5001/api/wechat/users/login"
    data = {
        "phone": phone,
        "password": password
    }
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))

def test_get_user_info(phone):
    """测试获取用户信息"""
    url = f"http://localhost:5001/api/wechat/users/{phone}"
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='API测试脚本')
    parser.add_argument('--action', choices=['register', 'login', 'info'], required=True, help='要执行的操作')
    parser.add_argument('--phone', help='手机号')
    parser.add_argument('--password', help='密码')
    
    args = parser.parse_args()
    
    if args.action == 'register':
        test_register()
    elif args.action == 'login':
        if not args.phone or not args.password:
            print("登录需要提供手机号和密码")
            exit(1)
        test_login(args.phone, args.password)
    elif args.action == 'info':
        if not args.phone:
            print("获取用户信息需要提供手机号")
            exit(1)
        test_get_user_info(args.phone)
