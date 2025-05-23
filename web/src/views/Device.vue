<template>
  <div class="device-container">
    <div class="header">
      <el-button type="primary" @click="showAddDialog">录入设备</el-button>
    </div>
    
    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-item">
        <el-input
          v-model="searchForm.phone"
          placeholder="搜索所属人电话"
          clearable
          style="width: 200px;"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button v-if="searchForm.phone" @click="handleReset">返回</el-button>
      </div>
    </div>
    
    <el-table :data="deviceList" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="设备ID" width="180" />
      <el-table-column prop="phone" label="所属人电话" width="180" />
      <el-table-column prop="created_at" label="录入时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="amount" label="设备金额" width="180">
        <template #default="scope">
          {{ scope.row.amount.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" />
      <el-table-column align="center" label="操作" width="480">
        <template #default="scope">
          <el-button
            size="small"
            type="primary"
            @click="handleAssign(scope.row)"
            style="margin-right: 10px;"
          >
            分配
          </el-button>
          <el-button
            size="small"
            type="info"
            @click="handleCommission(scope.row)"
            style="margin-right: 10px;"
          >
            {{ scope.row.commission_rate }}%
          </el-button>
          <el-button
            size="small"
            :type="scope.row.is_returned ? 'success' : 'warning'"
            @click="handleReturn(scope.row)"
            style="margin-right: 10px;"
          >
            {{ scope.row.is_returned ? '已返现' : '未返现' }}
          </el-button>
          <el-button
            size="small"
            :type="scope.row.is_paid ? 'success' : 'warning'"
            @click="handlePay(scope.row)"
            style="margin-right: 10px;"
          >
            {{ scope.row.is_paid ? '已打款' : '未打款' }}
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 录入设备对话框 -->
    <el-dialog v-model="addDialogVisible" title="录入设备" width="30%">
      <el-form :model="newDevice" label-width="100px">
        <el-form-item label="设备号">
          <el-input v-model="newDevice.id" />
        </el-form-item>
        <el-form-item label="设备金额">
          <el-input v-model="newDevice.amount" type="number" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="newDevice.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddDevice">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 分配设备对话框 -->
    <el-dialog v-model="assignDialogVisible" title="分配设备" width="30%">
      <el-form :model="assignForm" label-width="100px">
        <el-form-item label="电话号码">
          <el-input v-model="assignForm.phone">
            <template #append>
              <el-button @click="searchPhone">搜索</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item v-if="phoneOptions.length > 0" label="选择号码">
          <el-select v-model="assignForm.selectedPhone" placeholder="请选择">
            <el-option
              v-for="item in phoneOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="assignDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAssign">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 设置分成对话框 -->
    <el-dialog v-model="commissionDialogVisible" title="设置分成" width="30%">
      <el-form :model="commissionForm" label-width="100px">
        <el-form-item label="分成比例">
          <el-input-number 
            v-model="commissionForm.rate" 
            :min="0" 
            :max="20"
            :step="1"
          />
          <span class="unit">%</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="commissionDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmCommission">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { getDevices, addDevice, updateDevicePhone, updateDeviceCommission, updateDeviceReturnStatus, payDevice } from '../api/device'

// 设备列表数据
const deviceList = ref([])
const loading = ref(false)
const addDialogVisible = ref(false)
const assignDialogVisible = ref(false)
const commissionDialogVisible = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 新设备表单
const newDevice = ref({
  id: '',
  amount: '',
  remark: ''
})

// 分配表单
const assignForm = ref({
  phone: '',
  selectedPhone: ''
})
const phoneOptions = ref([])
const currentDevice = ref(null)

// 分成表单
const commissionForm = ref({
  rate: 0
})

// 搜索表单
const searchForm = ref({
  phone: ''
})

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 获取设备列表
const fetchDeviceList = async () => {
  loading.value = true
  try {
    const response = await getDevices({
      page: currentPage.value,
      per_page: pageSize.value,
      phone: searchForm.value.phone || undefined
    })
    if (response.data) {
      deviceList.value = response.data.items || []
      total.value = response.data.total || 0
      if (deviceList.value.length === 0) {
        ElMessage.info('没有找到匹配的设备')
      }
    } else {
      ElMessage.error('返回数据格式不正确')
    }
  } catch (error) {
    ElMessage.error('获取设备列表失败')
    console.error('Error fetching devices:', error)
  } finally {
    loading.value = false
  }
}

// 显示添加设备对话框
const showAddDialog = () => {
  addDialogVisible.value = true
  newDevice.value = {
    id: '',
    amount: '',
    remark: ''
  }
}

// 添加设备
const handleAddDevice = async () => {
  try {
    const response = await addDevice(newDevice.value)
    if (response.data.success) {
      ElMessage.success('添加设备成功')
      addDialogVisible.value = false
      fetchDeviceList()
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    ElMessage.error('添加设备失败')
    console.error('Error adding device:', error)
  }
}

// 处理分配
const handleAssign = (row) => {
  currentDevice.value = row
  assignDialogVisible.value = true
  assignForm.value = {
    phone: '',
    selectedPhone: ''
  }
  phoneOptions.value = []
}

// 搜索电话号码
const searchPhone = async () => {
  try {
    const response = await axios.get(`http://localhost:5000/api/users/search?phone=${assignForm.value.phone}`)
    phoneOptions.value = response.data  // 直接使用返回的电话号码列表
  } catch (error) {
    ElMessage.error('搜索电话号码失败')
    console.error('Error searching phones:', error)
  }
}

// 确认分配
const confirmAssign = async () => {
  try {
    const response = await updateDevicePhone(currentDevice.value.id, assignForm.value.selectedPhone)
    if (response.data.success) {
      ElMessage.success('分配成功')
      assignDialogVisible.value = false
      fetchDeviceList()
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    ElMessage.error('分配失败')
    console.error('Error assigning device:', error)
  }
}

// 处理分成
const handleCommission = (row) => {
  currentDevice.value = row
  commissionForm.value.rate = row.commission_rate || 0
  commissionDialogVisible.value = true
}

// 确认分成
const confirmCommission = async () => {
  try {
    const response = await updateDeviceCommission(currentDevice.value.id, commissionForm.value.rate)
    if (response.data.success) {
      ElMessage.success('设置分成成功')
      commissionDialogVisible.value = false
      fetchDeviceList()
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    ElMessage.error('设置分成失败')
    console.error('Error setting commission:', error)
  }
}

// 处理返现
const handleReturn = (row) => {
  ElMessageBox.confirm(
    `确认${row.is_returned ? '取消' : '设置'}该设备返现状态？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await updateDeviceReturnStatus(row.id, !row.is_returned)
      if (response.data.success) {
        ElMessage.success(`${row.is_returned ? '取消' : '设置'}返现成功`)
        fetchDeviceList()
      } else {
        ElMessage.error(response.data.message)
      }
    } catch (error) {
      ElMessage.error(`${row.is_returned ? '取消' : '设置'}返现失败`)
      console.error('Error setting return status:', error)
    }
  })
}

// 处理删除
const handleDelete = (row) => {
  ElMessageBox.confirm(
    '确认删除该设备？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await axios.delete(`http://localhost:5000/api/devices/${row.id}`)
      if (response.data.success) {
        ElMessage.success('删除成功')
        fetchDeviceList()
      } else {
        ElMessage.error(response.data.message)
      }
    } catch (error) {
      ElMessage.error('删除失败')
      console.error('Error deleting device:', error)
    }
  })
}

// 处理页码改变
const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchDeviceList()
}

// 处理每页条数改变
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchDeviceList()
}

// 处理打款
const handlePay = (row) => {
  ElMessageBox.confirm(
    `确认${row.is_paid ? '取消' : '设置'}该设备打款状态？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await payDevice(row.id)
      if (response.data.success) {
        ElMessage.success(`${row.is_paid ? '取消' : '设置'}打款成功`)
        fetchDeviceList()
      } else {
        ElMessage.error(response.data.message)
      }
    } catch (error) {
      ElMessage.error(`${row.is_paid ? '取消' : '设置'}打款失败`)
      console.error('Error setting pay status:', error)
    }
  })
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchDeviceList()
}

// 处理搜索重置
const handleReset = () => {
  searchForm.value.phone = ''
  currentPage.value = 1
  fetchDeviceList()
}

onMounted(() => {
  fetchDeviceList()
})
</script>

<style scoped>
.device-container {
  padding: 20px;
}

.header {
  margin-bottom: 20px;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.unit {
  margin-left: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 