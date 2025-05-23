<template>
  <div class="profile-container">
    
    <!-- 统计信息卡片 -->
    <el-card class="statistics-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>账户统计</span>
        </div>
      </template>
      
      <div class="statistics-content">
        <div class="stat-section">
          <h3>提现信息</h3>
          <div class="stat-item">
            <span class="label">已提现金额：</span>
            <span class="value">¥{{ statistics.withdrawn.toFixed(2) }}</span>
          </div>
          <div class="stat-item">
            <span class="label">未提现金额：</span>
            <span class="value">¥{{ statistics.unwithdrawn.toFixed(2) }}</span>
          </div>
          <div class="stat-item">
            <span class="label">总额：</span>
            <span class="value">¥{{ total.toFixed(2) }}</span>
          </div>
        </div>

        <div class="stat-section">
          <h3>设备信息</h3>
          <div class="stat-item">
            <span class="label">抽成总额：</span>
            <span class="value">¥{{ statistics.commission_total.toFixed(2) }}</span>
          </div>
          <div class="stat-item">
            <span class="label">设备金额总和：</span>
            <span class="value">¥{{ statistics.device_total.toFixed(2) }}</span>
          </div>
        </div>

        <div class="stat-section">
          <h3>返现信息(待定)</h3>
          <div class="stat-item">
            <span class="label">返现总额：</span>
            <span class="value">¥{{ statistics.return_total.toFixed(2) }}</span>
          </div>
          <div class="stat-item">
            <span class="label">已打款返现金额：</span>
            <span class="value">¥{{ statistics.paid_return.toFixed(2) }}</span>
          </div>
          <div class="stat-item">
            <span class="label">未打款返现金额：</span>
            <span class="value">¥{{ statistics.unpaid_return.toFixed(2) }}</span>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 加载状态
const loading = ref(false)

// 统计信息
const statistics = ref({
  withdrawn: 0,          // 已提现金额
  unwithdrawn: 0,        // 未提现金额
  commission_total: 0,   // 抽成总额
  device_total: 0,       // 设备金额总和
  return_total: 0,       // 返现总额
  paid_return: 0,        // 已打款返现金额
  unpaid_return: 0       // 未打款返现金额
})

// 使用计算属性计算总额
const total = computed(() => statistics.value.withdrawn + statistics.value.unwithdrawn)

// 获取已提现金额
const fetchWithdrawnAmount = async () => {
  try {
    const response = await axios.get('http://localhost:5001/api/platform/withdrawn')
    if (response.data && response.data.amount !== undefined) {
      statistics.value.withdrawn = response.data.amount
    } else {
      ElMessage.warning('获取已提现金额数据格式不正确')
    }
  } catch (error) {
    console.error('获取已提现金额失败:', error)
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    } else {
      ElMessage.error('获取已提现金额失败')
    }
  }
}

// 获取未提现金额
const fetchUnwithdrawnAmount = async () => {
  try {
    const response = await axios.get('http://localhost:5001/api/platform/unwithdrawn')
    if (response.data && response.data.amount !== undefined) {
      statistics.value.unwithdrawn = response.data.amount
    } else {
      ElMessage.warning('获取未提现金额数据格式不正确')
    }
  } catch (error) {
    console.error('获取未提现金额失败:', error)
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    } else {
      ElMessage.error('获取未提现金额失败')
    }
  }
}

// 获取抽成总额
const fetchCommissionTotal = async () => {
  try {
    const response = await axios.get('http://localhost:5001/api/platform/commission')
    if (response.data && response.data.amount !== undefined) {
      statistics.value.commission_total = response.data.amount
    } else {
      ElMessage.warning('获取抽成总额数据格式不正确')
    }
  } catch (error) {
    console.error('获取抽成总额失败:', error)
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    } else {
      ElMessage.error('获取抽成总额失败')
    }
  }
}

// 获取设备总额
const fetchDeviceTotal = async () => {
  try {
    const response = await axios.get('http://localhost:5001/api/platform/devices/total')
    if (response.data && response.data.amount !== undefined) {
      statistics.value.device_total = response.data.amount
    } else {
      ElMessage.warning('获取设备总额数据格式不正确')
    }
  } catch (error) {
    console.error('获取设备总额失败:', error)
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    } else {
      ElMessage.error('获取设备总额失败')
    }
  }
}

// 获取所有统计数据
const fetchAllStats = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchWithdrawnAmount(),
      fetchUnwithdrawnAmount(),
      fetchCommissionTotal(),
      fetchDeviceTotal()
    ])
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    fetchAllStats()
  ])
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.statistics-card {
  margin: 20px 0;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.statistics-content {
  display: flex;
  justify-content: space-between;
  gap: 40px;
  padding: 20px 0;
}

.stat-section {
  flex: 1;
  padding: 0 20px;
  border-right: 1px solid #EBEEF5;
}

.stat-section:last-child {
  border-right: none;
}

.stat-section h3 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 16px;
  font-weight: bold;
}

.stat-item {
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item .label {
  color: #606266;
  font-size: 14px;
}

.stat-item .value {
  font-weight: bold;
  color: #409EFF;
  font-size: 15px;
}

@media screen and (max-width: 768px) {
  .statistics-content {
    flex-direction: column;
    gap: 20px;
  }

  .stat-section {
    border-right: none;
    border-bottom: 1px solid #EBEEF5;
    padding: 0 0 20px 0;
  }

  .stat-section:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }
}
</style> 