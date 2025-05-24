import requests
import json

def test_my_device_count(phone):
    """测试获取我的设备数量"""
    url = f"http://localhost:5001/api/wechat/users/{phone}/devices/count"
    response = requests.get(url)
    print(f"我的设备数量 - Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))

def test_subordinate_device_count(phone):
    """测试获取下线设备数量"""
    url = f"http://localhost:5001/api/wechat/users/{phone}/subordinate-devices/count"
    response = requests.get(url)
    print(f"下线设备数量 - Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    phone = "17610826899"  # 测试手机号
    
    print("测试设备数量接口:")
    test_my_device_count(phone)
    print("\n" + "="*50 + "\n")
    test_subordinate_device_count(phone) 