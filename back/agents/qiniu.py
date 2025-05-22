import hmac
import base64
import hashlib
import requests
import json
from datetime import datetime, timedelta
from config import Config

class QiniuAuth:
    """七牛云API认证类"""
    def __init__(self):
        self.ak = Config.QINIU_AK
        self.sk = bytes(Config.QINIU_SK, encoding='utf-8')
        self.host = Config.QINIU_HOST

    def get_sign_key(self, data):
        """生成签名"""
        sign = hmac.new(self.sk, data, hashlib.sha1).digest()
        token = self.ak + ":" + base64.urlsafe_b64encode(sign).decode("utf-8")
        return "Qiniu " + token

    def get_request_data(self, method, path, query_str="", body_str="", content_type="application/json"):
        """构建请求数据"""
        data = method + " " + path
        if query_str:
            data += "?" + query_str
        data += "\nHost: " + self.host
        if body_str:
            data += "\nContent-Type: " + content_type
        data += "\n\n"
        if body_str and body_str != "application/octet-stream":
            data += body_str
        return data

class QiniuClient:
    """七牛云API客户端基类"""
    def __init__(self):
        self.auth = QiniuAuth()
        self.base_url = f'https://{self.auth.host}'

    def _make_request(self, method, path, params=None, json_data=None):
        """发送请求的通用方法"""
        url = self.base_url + path
        
        # 构建查询字符串
        query_str = '&'.join([f"{k}={v}" for k, v in (params or {}).items()])
        
        # 构建请求数据
        body_str = json.dumps(json_data) if json_data else ""
        request_data = self.auth.get_request_data(method, path, query_str, body_str)
        sign_key = self.auth.get_sign_key(request_data.encode('utf-8'))
        
        # 设置请求头
        headers = {
            'Authorization': sign_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json_data,
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"七牛云API请求失败: {method} {path}, 状态码: {response.status_code}")
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"七牛云API请求错误: {str(e)}")
            return None

class QiniuDeviceClient(QiniuClient):
    """七牛云设备API客户端"""
    
    def get_all_devices(self, page=1, limit=100):
        """
        获取所有设备状态
        :param page: 页码
        :param limit: 每页数量，最大100
        :return: 设备列表
        """
        path = '/v1/ant/status'
        params = {
            'page': page,
            'limit': min(limit, 100)  # 确保不超过最大限制
        }
        return self._make_request('GET', path, params=params)
    
    def get_device_status(self, node_id):
        """
        获取指定设备状态
        :param node_id: 设备ID
        :return: 设备状态信息
        """
        path = f'/v1/ant/{node_id}/status'
        return self._make_request('GET', path)
    
    def get_bill_details(self, node_ids, day=None):
        """
        查询设备账单详情
        :param node_ids: 设备ID列表，最大数量为1000
        :param day: 日期，格式：yyyymmdd，默认为今天
        :return: 账单详情
        """
        path = '/v1/ant/batch/amount/details'
        
        # 如果没有指定日期，使用今天
        if not day:
            day = datetime.now().strftime('%Y%m%d')
        
        # 确保node_ids不超过1000个
        node_ids = node_ids[:1000]
        
        json_data = {
            "nodeIds": node_ids,
            "day": day
        }
        
        return self._make_request('POST', path, json_data=json_data)
    
    def get_device_income(self, node_id, day=None):
        """
        获取单个设备的收益信息
        :param node_id: 设备ID
        :param day: 日期，格式：yyyymmdd，默认为今天
        :return: 收益信息
        """
        result = self.get_bill_details([node_id], day)
        if result and 'details' in result and node_id in result['details']:
            detail = result['details'][node_id]
            if 'measuredAmount' in detail:
                return {
                    'original_amount': detail['measuredAmount'].get('originalAmount', 0),
                    'sla_deduction': detail['measuredAmount'].get('slaDeduction', 0),
                    'settle_amount': detail['measuredAmount'].get('settleAmount', 0),
                    'is_billing': detail['measuredAmount'].get('isBilling', False)
                }
        return None
        
    def get_device_bills(self, device_ids, start_time, end_time=None):
        """
        获取设备指定时间段的账单
        :param device_ids: 设备ID列表
        :param start_time: 开始时间
        :param end_time: 结束时间，如果不传则默认为当前时间
        :return: 账单列表，每个账单包含 settle_amount 字段
        """
        if not end_time:
            end_time = datetime.now()
            
        # 将时间转换为yyyymmdd格式
        start_day = start_time.strftime('%Y%m%d')
        end_day = end_time.strftime('%Y%m%d')
        
        # 获取每天的账单
        bills = []
        current_day = datetime.strptime(start_day, '%Y%m%d')
        while current_day <= end_time:
            day_str = current_day.strftime('%Y%m%d')
            result = self.get_bill_details(device_ids, day_str)
            
            if result and isinstance(result, dict) and 'details' in result:
                for device_id, detail in result['details'].items():
                    if isinstance(detail, dict) and 'measuredAmount' in detail:
                        amount = detail['measuredAmount']
                        if isinstance(amount, dict):
                            bills.append({
                                'device_id': device_id,
                                'settle_amount': amount.get('settleAmount', 0),
                                'time': current_day.isoformat()
                            })
            
            current_day += timedelta(days=1)
            
        return bills