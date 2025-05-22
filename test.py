#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import hmac, base64, hashlib, requests, json
import time
# auth
class Api_Auth(object):
	def __init__(self):
     # replace following params with your ak sk
		self.ak = 'yYaQ0JQfKJEwqwKtyD30XwbDDrEVh6N7z4y5eqYN'
		self.sk = bytes('hPwpUBPwitSJ6gwG4wmDYO6PJKqb1Ubo20tVUOe1', encoding='utf-8')
		self.host = "api.niulinkcloud.com"

	def getSignKey(self, data):
		sign = hmac.new(self.sk, data, hashlib.sha1).digest()
		token = self.ak + ":" + base64.urlsafe_b64encode(sign).decode("utf-8")
		return "Qiniu " + token

	def getRequestData(self, method, path, queryStr="", bodyStr="", contentType="application/json"):
		data = method+" "+path
		if queryStr != "":
			data += "?"+queryStr
		data += "\nHost: "+self.host
		if bodyStr != "":
			data += "\nContent-Type: " + contentType
		data += "\n\n"
		if bodyStr != "" and bodyStr != "application/octet-stream":
			data += bodyStr
		return data

# get status
class Api_Data(object):
	def get_data(self):
		# 修改为正确的 API 路径
		url = 'https://api.niulinkcloud.com/v1/ant/status'
		path = '/v1/ant/status'
		
		# 添加分页参数
		params = {
			'page': 1,
			'limit': 100  # 每页最大数量为100
		}
		
		# 构建查询字符串
		queryStr = '&'.join([f"{k}={v}" for k, v in params.items()])
		
		# 获取认证信息
		data = Api_Auth().getRequestData("GET", path, queryStr, "")
		signkey = Api_Auth().getSignKey(data.encode('utf-8'))
		
		headers = {
			'Authorization': signkey,
		}
		
		try:
			response = requests.get(url, headers=headers, params=params, verify=False)
			if response.status_code == 200:
				return response.json()
			else:
				print(f"请求失败，状态码：{response.status_code}")
				return response.json()
		except requests.exceptions.RequestException as e:
			print(f"请求错误: {str(e)}")
			return None

	def get_node_status(self, node_id):
		# 修改为正确的 API 路径
		url = f'https://api.niulinkcloud.com/v1/ant/{node_id}/status'
		path = f'/v1/ant/{node_id}/status'
		
		# 获取认证信息
		data = Api_Auth().getRequestData("GET", path, "", "")
		signkey = Api_Auth().getSignKey(data.encode('utf-8'))
		
		headers = {
			'Authorization': signkey,
		}
		
		try:
			response = requests.get(url, headers=headers, verify=False)
			if response.status_code == 200:
				return response.json()
			else:
				print(f"请求失败，状态码：{response.status_code}")
				return response.json()
		except requests.exceptions.RequestException as e:
			print(f"请求错误: {str(e)}")
			return None

	# use /v1/nodes/:nodeId/submit as an example of POST api, path is like '/v1/nodes/aaa/submit'
	# PUT DELETE PATCH api can refer to this api
	def post_data(self, path, jsonData):
		api = Api_Auth()
		data = Api_Auth().getRequestData("POST", path, "", json.dumps(jsonData))
		signkey = Api_Auth().getSignKey(data.encode('utf-8'))
		headers = {
			'Authorization': signkey,
		  'Content-Type': 'application/json',
		}
		# print(signkey)

		url = 'https://'+api.host+path
		response = requests.post(url, headers=headers,  data=json.dumps(jsonData))
		return response.content.decode()

	def get_bill_details(self, node_ids, day):
		"""
		查询指定节点的账单详情
		:param node_ids: 节点ID列表，最大数量为1000
		:param day: 日期，格式：yyyymmdd，示例：20060102
		:return: 账单详情
		"""
		url = 'https://api.niulinkcloud.com/v1/ant/batch/amount/details'
		path = '/v1/ant/batch/amount/details'
		
		# 构建请求数据
		json_data = {
			"nodeIds": node_ids,
			"day": day
		}
		
		# 获取认证信息
		data = Api_Auth().getRequestData("POST", path, "", json.dumps(json_data))
		signkey = Api_Auth().getSignKey(data.encode('utf-8'))
		
		headers = {
			'Authorization': signkey,
			'Content-Type': 'application/json'
		}
		
		try:
			response = requests.post(url, headers=headers, json=json_data, verify=False)
			if response.status_code == 200:
				return response.json()
			else:
				print(f"请求失败，状态码：{response.status_code}")
				return response.json()
		except requests.exceptions.RequestException as e:
			print(f"请求错误: {str(e)}")
			return None

# 测试代码
# 查询所有节点
print("查询所有节点：")
result = Api_Data().get_data()
if result:
	print("节点列表：")
	for node in result.get('items', []):
		print(f"节点ID: {node.get('nodeID')}")
		print(f"状态: {node.get('status')}")
		print(f"阶段: {node.get('stage')}")
		print(f"备注: {node.get('remark')}")
		print("-------------------")

# # 查询特定节点
# print("\n查询特定节点：")
# node_id = "ant89fd01e5d0ef2cac1515bfbefb594"
# result = Api_Data().get_node_status(node_id)
# if result:
# 	print("节点状态信息：")
# 	print(f"节点ID: {result.get('nodeID')}")
# 	print(f"业务阶段: {result.get('stage')}")
# 	print(f"网络状态: {result.get('status')}")
# 	print(f"网络压测状态: {result.get('netBenchStatus')}")
# 	print(f"验收未通过原因: {result.get('acceptanceRejectReason')}")
# 	print(f"备注: {result.get('remark')}")

# 查询账单
print("\n查询账单详情：")
node_ids = ["ant0fc6d97b039c6d09d7b2f0143c60c"]  # 可以添加多个节点ID
day = "20250521"  # 格式：yyyymmdd
bill_result = Api_Data().get_bill_details(node_ids, day)
if bill_result and 'details' in bill_result:
	for node_id, detail in bill_result['details'].items():
		print(f"\n节点 {node_id} 的账单信息：")
		if 'measuredAmount' in detail:
			amount = detail['measuredAmount']
			print(f"原始金额: {amount.get('originalAmount')} 元")
			print(f"SLA扣减金额: {amount.get('slaDeduction')} 元")
			print(f"最终金额: {amount.get('settleAmount')} 元")
			print(f"出账状态: {'出账中' if amount.get('isBilling') else '已出账'}")
		if 'errorCode' in detail:
			print(f"错误码: {detail.get('errorCode')}")


