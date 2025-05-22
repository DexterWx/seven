<template>
  <div class="user-container">
    <div class="header">
      <el-button 
        type="primary" 
        @click="handleBack" 
        :disabled="!currentSuperior"
      >
        返回上级
      </el-button>
      <span v-if="currentSuperior" class="current-path">
        当前查看: {{ currentSuperior.name }} 的一级下线
      </span>
    </div>

    <el-table 
      :data="userList" 
      style="width: 100%" 
      v-loading="loading"
      @sort-change="handleSortChange"
    >
      <el-table-column prop="phone" label="手机号" width="150" />
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="commission_rate" label="分成比例" width="100">
        <template #default="scope">
          {{ scope.row.commission_rate ? `${scope.row.commission_rate}%` : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="superior_name" label="上级姓名" width="120">
        <template #default="scope">
          {{ scope.row.superior_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="superior_phone" label="上级电话" width="150">
        <template #default="scope">
          {{ scope.row.superior_phone || '-' }}
        </template>
      </el-table-column>
      <el-table-column 
        prop="first_level_count" 
        label="一级下线" 
        width="100"
        sortable="custom"
      >
        <template #default="scope">
          <el-button 
            type="primary" 
            link
            @click="handleViewFirstLevel(scope.row)"
            :disabled="scope.row.first_level_count === 0"
          >
            {{ scope.row.first_level_count || 0 }}
          </el-button>
        </template>
      </el-table-column>
      <el-table-column 
        prop="unwithdrawn_amount" 
        label="未提现金额" 
        width="120"
        sortable="custom"
      >
        <template #default="scope">
          {{ scope.row.unwithdrawn_amount?.toFixed(2) || '0.00' }}
        </template>
      </el-table-column>
      <el-table-column 
        prop="withdrawn_amount" 
        label="已提现金额" 
        width="120"
        sortable="custom"
      >
        <template #default="scope">
          {{ scope.row.withdrawn_amount?.toFixed(2) || '0.00' }}
        </template>
      </el-table-column>
      <el-table-column 
        prop="yesterday_income" 
        label="昨日收益" 
        width="120"
        sortable="custom"
      >
        <template #default="scope">
          {{ scope.row.yesterday_income?.toFixed(2) || '0.00' }}
        </template>
      </el-table-column>
      <el-table-column 
        prop="month_income" 
        label="本月收益" 
        width="120"
        sortable="custom"
      >
        <template #default="scope">
          {{ scope.row.month_income?.toFixed(2) || '0.00' }}
        </template>
      </el-table-column>
      <el-table-column 
        prop="created_at" 
        label="创建时间" 
        width="120"
        sortable="custom"
      >
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
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
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 配置axios
axios.defaults.baseURL = 'http://127.0.0.1:5000'
axios.defaults.timeout = 5000
axios.defaults.headers.common['Content-Type'] = 'application/json'

// 获取路由实例
const route = useRoute()
const router = useRouter()

// 用户列表数据
const userList = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const currentSuperior = ref(null)
const currentLevel = ref(0)
const sortField = ref('')  // 排序字段
const sortOrder = ref('')  // 排序方向

// 获取用户列表
const fetchUserList = async () => {
  loading.value = true
  try {
    console.log('正在获取用户列表...', {
      page: currentPage.value,
      per_page: pageSize.value,
      superior_phone: currentSuperior.value?.phone,
      sort_field: sortField.value,
      sort_order: sortOrder.value
    })
    const response = await axios.get('/api/users', {
      params: {
        page: currentPage.value,
        per_page: pageSize.value,
        superior_phone: currentSuperior.value?.phone,
        sort_field: sortField.value,
        sort_order: sortOrder.value
      }
    })
    console.log('获取到的用户列表数据:', response.data)
    if (response.data && response.data.items) {
      userList.value = response.data.items
      total.value = response.data.total
    } else {
      console.error('返回数据格式不正确:', response.data)
      ElMessage.error('返回数据格式不正确')
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    if (error.response) {
      console.error('错误响应:', error.response.data)
      ElMessage.error(`获取用户列表失败: ${error.response.data.error || error.message}`)
    } else if (error.request) {
      console.error('未收到响应:', error.request)
      ElMessage.error('服务器未响应，请检查后端服务是否运行')
    } else {
      ElMessage.error(`获取用户列表失败: ${error.message}`)
    }
  } finally {
    loading.value = false
  }
}

// 处理排序变化
const handleSortChange = ({ prop, order }) => {
  console.log('排序变化:', { prop, order })
  // 将 Element Plus 的排序值转换为后端期望的值
  sortField.value = prop || ''
  sortOrder.value = order === 'ascending' ? 'ascending' : 'descending'
  console.log('转换后的排序参数:', { sortField: sortField.value, sortOrder: sortOrder.value })
  currentPage.value = 1
  fetchUserList()
}

// 重置到根列表
const resetToRoot = () => {
  currentSuperior.value = null
  currentPage.value = 1
  currentLevel.value = 0
  sortField.value = ''  // 重置排序
  sortOrder.value = ''  // 重置排序
  fetchUserList()
}

// 监听路由变化
watch(
  () => route.path,
  (newPath) => {
    // 当路由变化时，重置状态
    resetToRoot()
  }
)

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 查看一级下线
const handleViewFirstLevel = (row) => {
  currentSuperior.value = row
  currentPage.value = 1
  currentLevel.value += 1  // 增加层级
  fetchUserList()
}

// 返回上级
const handleBack = () => {
  if (currentLevel.value === 1) {
    // 如果是第一层，直接返回根列表
    resetToRoot()
  } else if (currentSuperior.value?.superior_phone) {
    // 如果有上级，返回上级的一级下线列表
    currentSuperior.value = {
      phone: currentSuperior.value.superior_phone,
      name: currentSuperior.value.superior_name
    }
    currentLevel.value -= 1  // 减少层级
    currentPage.value = 1
    fetchUserList()
  } else {
    // 如果没有上级，返回根列表
    resetToRoot()
  }
}

// 处理页码改变
const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchUserList()
}

// 处理每页条数改变
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchUserList()
}

// 初始化
onMounted(() => {
  resetToRoot()
})
</script>

<style scoped>
.user-container {
  padding: 20px;
}

.header {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.current-path {
  color: #666;
  font-size: 14px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 