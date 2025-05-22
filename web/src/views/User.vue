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
      <el-table-column label="分成比例" width="120">
        <template #default="scope">
          <el-button 
            type="primary" 
            link
            @click="handleEditCommissionRate(scope.row)"
          >
            {{ scope.row.min_commission_rate }}% - {{ scope.row.max_commission_rate }}%
          </el-button>
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
        prop="team_yesterday_income" 
        label="团队昨日收益" 
        width="120"
        sortable="custom"
      >
        <template #default="scope">
          {{ scope.row.team_yesterday_income?.toFixed(2) || '0.00' }}
        </template>
      </el-table-column>
      <el-table-column 
        prop="team_month_income" 
        label="团队本月收益" 
        width="120"
        sortable="custom"
      >
        <template #default="scope">
          {{ scope.row.team_month_income?.toFixed(2) || '0.00' }}
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

    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加用户' : '编辑用户'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" :disabled="dialogType === 'edit'" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="dialogType === 'add'">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-form-item label="上级手机号" prop="superior_phone">
          <el-input v-model="form.superior_phone" />
        </el-form-item>
        <el-form-item label="最小分成比例" prop="min_commission_rate">
          <el-input-number 
            v-model="form.min_commission_rate" 
            :min="0" 
            :max="20" 
            :precision="0"
          />
          <span class="unit">%</span>
        </el-form-item>
        <el-form-item label="最大分成比例" prop="max_commission_rate">
          <el-input-number 
            v-model="form.max_commission_rate" 
            :min="0" 
            :max="20" 
            :precision="0"
          />
          <span class="unit">%</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑分成比例对话框 -->
    <el-dialog
      v-model="commissionRateDialogVisible"
      title="编辑分成比例"
      width="400px"
    >
      <el-form
        ref="commissionRateFormRef"
        :model="commissionRateForm"
        :rules="commissionRateRules"
        label-width="100px"
      >
        <el-form-item label="最小分成比例" prop="min_commission_rate">
          <el-input-number 
            v-model="commissionRateForm.min_commission_rate" 
            :min="0" 
            :max="20" 
            :precision="0"
          />
          <span class="unit">%</span>
        </el-form-item>
        <el-form-item label="最大分成比例" prop="max_commission_rate">
          <el-input-number 
            v-model="commissionRateForm.max_commission_rate" 
            :min="0" 
            :max="20" 
            :precision="0"
          />
          <span class="unit">%</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="commissionRateDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCommissionRateSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>

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
import { ElMessage, ElMessageBox } from 'element-plus'
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

// 对话框相关
const dialogVisible = ref(false)
const dialogType = ref('add')  // 'add' 或 'edit'
const formRef = ref(null)
const form = ref({
  phone: '',
  name: '',
  password: '',
  superior_phone: '',
  min_commission_rate: 0,
  max_commission_rate: 20
})

// 表单验证规则
const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  min_commission_rate: [
    { required: true, message: '请输入最小分成比例', trigger: 'blur' },
    { type: 'number', min: 0, max: 20, message: '分成比例必须在0-20之间', trigger: 'blur' }
  ],
  max_commission_rate: [
    { required: true, message: '请输入最大分成比例', trigger: 'blur' },
    { type: 'number', min: 0, max: 20, message: '分成比例必须在0-20之间', trigger: 'blur' }
  ]
}

// 分成比例对话框相关
const commissionRateDialogVisible = ref(false)
const commissionRateFormRef = ref(null)
const commissionRateForm = ref({
  phone: '',
  min_commission_rate: 0,
  max_commission_rate: 20
})

// 分成比例表单验证规则
const commissionRateRules = {
  min_commission_rate: [
    { required: true, message: '请输入最小分成比例', trigger: 'blur' },
    { type: 'number', min: 0, max: 20, message: '分成比例必须在0-20之间', trigger: 'blur' }
  ],
  max_commission_rate: [
    { required: true, message: '请输入最大分成比例', trigger: 'blur' },
    { type: 'number', min: 0, max: 20, message: '分成比例必须在0-20之间', trigger: 'blur' }
  ]
}

// 获取用户列表
const fetchUserList = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/users', {
      params: {
        page: currentPage.value,
        per_page: pageSize.value,
        superior_phone: currentSuperior.value?.phone,
        sort_field: sortField.value,
        sort_order: sortOrder.value
      }
    })
    if (response.data && response.data.items) {
      userList.value = response.data.items
      total.value = response.data.total
    } else {
      ElMessage.error('返回数据格式不正确')
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error(error.response?.data?.error || error.message)
  } finally {
    loading.value = false
  }
}

// 处理编辑
const handleEdit = (row) => {
  dialogType.value = 'edit'
  form.value = {
    phone: row.phone,
    name: row.name,
    superior_phone: row.superior_phone || '',
    min_commission_rate: row.min_commission_rate,
    max_commission_rate: row.max_commission_rate
  }
  dialogVisible.value = true
}

// 处理删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该用户吗？', '提示', {
      type: 'warning'
    })
    
    const response = await axios.delete(`/api/users/${row.phone}`)
    if (response.data.success) {
      ElMessage.success('删除成功')
      fetchUserList()
    } else {
      ElMessage.error(response.data.error || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || error.message)
    }
  }
}

// 处理提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    const url = dialogType.value === 'add' ? '/api/users' : `/api/users/${form.value.phone}`
    const method = dialogType.value === 'add' ? 'post' : 'put'
    
    const response = await axios[method](url, form.value)
    if (response.data.success) {
      ElMessage.success(dialogType.value === 'add' ? '添加成功' : '更新成功')
      dialogVisible.value = false
      fetchUserList()
    } else {
      ElMessage.error(response.data.error || (dialogType.value === 'add' ? '添加失败' : '更新失败'))
    }
  } catch (error) {
    if (error.response) {
      ElMessage.error(error.response.data.error || error.message)
    }
  }
}

// 处理排序变化
const handleSortChange = ({ prop, order }) => {
  sortField.value = prop || ''
  sortOrder.value = order === 'ascending' ? 'ascending' : 'descending'
  currentPage.value = 1
  fetchUserList()
}

// 重置到根列表
const resetToRoot = () => {
  currentSuperior.value = null
  currentPage.value = 1
  currentLevel.value = 0
  sortField.value = ''
  sortOrder.value = ''
  fetchUserList()
}

// 监听路由变化
watch(
  () => route.path,
  (newPath) => {
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
  currentLevel.value += 1
  fetchUserList()
}

// 返回上级
const handleBack = () => {
  if (currentLevel.value === 1) {
    resetToRoot()
  } else if (currentSuperior.value?.superior_phone) {
    currentSuperior.value = {
      phone: currentSuperior.value.superior_phone,
      name: currentSuperior.value.superior_name
    }
    currentLevel.value -= 1
    currentPage.value = 1
    fetchUserList()
  } else {
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

// 处理编辑分成比例
const handleEditCommissionRate = (row) => {
  commissionRateForm.value = {
    phone: row.phone,
    min_commission_rate: row.min_commission_rate,
    max_commission_rate: row.max_commission_rate
  }
  commissionRateDialogVisible.value = true
}

// 处理分成比例提交
const handleCommissionRateSubmit = async () => {
  if (!commissionRateFormRef.value) return
  
  try {
    await commissionRateFormRef.value.validate()
    
    const { phone, min_commission_rate, max_commission_rate } = commissionRateForm.value
    
    if (min_commission_rate > max_commission_rate) {
      ElMessage.error('最小分成比例不能大于最大分成比例')
      return
    }
    
    const response = await axios.put(`/api/users/${phone}`, {
      min_commission_rate,
      max_commission_rate
    })
    
    if (response.data.success) {
      ElMessage.success('更新成功')
      commissionRateDialogVisible.value = false
      fetchUserList()
    } else {
      ElMessage.error(response.data.error || '更新失败')
    }
  } catch (error) {
    if (error.response) {
      ElMessage.error(error.response.data.error || error.message)
    }
  }
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

.unit {
  margin-left: 8px;
  color: #666;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 