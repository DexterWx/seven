import axios from 'axios'

const BASE_URL = ''

// 获取用户列表
export const getUsers = async (params) => {
  try {
    const response = await axios.get(`${BASE_URL}/users`, { params })
    return response
  } catch (error) {
    console.error('Error fetching users:', error)
    throw error
  }
}

// 添加用户
export const addUser = async (data) => {
  try {
    const response = await axios.post(`${BASE_URL}/users/register`, data)
    return response
  } catch (error) {
    console.error('Error adding user:', error)
    throw error
  }
}

// 更新用户
export const updateUser = async (phone, data) => {
  try {
    const response = await axios.put(`${BASE_URL}/users/${phone}`, data)
    return response
  } catch (error) {
    console.error('Error updating user:', error)
    throw error
  }
}

// 删除用户
export const deleteUser = async (phone) => {
  try {
    const response = await axios.delete(`${BASE_URL}/users/${phone}`)
    return response
  } catch (error) {
    console.error('Error deleting user:', error)
    throw error
  }
}

// 搜索用户
export const searchUsers = async (phone) => {
  try {
    const response = await axios.get(`${BASE_URL}/users/search`, { params: { phone } })
    return response
  } catch (error) {
    console.error('Error searching users:', error)
    throw error
  }
} 