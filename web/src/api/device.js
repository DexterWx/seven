import axios from 'axios'

const BASE_URL = ''

// 获取设备列表
export const getDevices = async (params) => {
  try {
    const response = await axios.get(`${BASE_URL}/devices`, { params })
    return response
  } catch (error) {
    console.error('Error fetching devices:', error)
    throw error
  }
}

// 添加设备
export const addDevice = async (data) => {
  try {
    const response = await axios.post(`${BASE_URL}/devices`, data)
    return response
  } catch (error) {
    console.error('Error adding device:', error)
    throw error
  }
}

// 更新设备所属人电话
export const updateDevicePhone = async (deviceId, phone) => {
  try {
    const response = await axios.put(`${BASE_URL}/devices/${deviceId}/phone`, { phone })
    return response
  } catch (error) {
    console.error('Error updating device phone:', error)
    throw error
  }
}

// 更新设备分成比例
export const updateDeviceCommission = async (deviceId, commissionRate) => {
  try {
    const response = await axios.put(`${BASE_URL}/devices/${deviceId}/commission`, { commission_rate: commissionRate })
    return response
  } catch (error) {
    console.error('Error updating device commission:', error)
    throw error
  }
}

// 更新设备返现状态
export const updateDeviceReturnStatus = async (deviceId, isReturned) => {
  try {
    const response = await axios.put(`${BASE_URL}/devices/${deviceId}/return`, { is_returned: isReturned })
    return response
  } catch (error) {
    console.error('Error updating device return status:', error)
    throw error
  }
}

// 设备打款
export const payDevice = async (deviceId) => {
  try {
    const response = await axios.post(`${BASE_URL}/devices/${deviceId}/pay`)
    return response
  } catch (error) {
    console.error('Error paying device:', error)
    throw error
  }
} 