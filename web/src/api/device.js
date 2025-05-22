import axios from 'axios'

const baseURL = 'http://localhost:5000/api'

export function getDevices(params) {
  return axios.get(`${baseURL}/devices`, { params })
}

export function addDevice(data) {
  return axios.post(`${baseURL}/devices`, data)
}

export function updateDevicePhone(deviceId, phone) {
  return axios.put(`${baseURL}/devices/${deviceId}/phone`, { phone })
}

export function updateDeviceCommission(deviceId, commissionRate) {
  return axios.put(`${baseURL}/devices/${deviceId}/commission`, { commission_rate: commissionRate })
}

export function updateDeviceReturnStatus(deviceId, isReturned) {
  return axios.put(`${baseURL}/devices/${deviceId}/return`, { is_returned: isReturned })
}

export function payDevice(deviceId) {
  return axios.post(`${baseURL}/devices/${deviceId}/pay`)
} 