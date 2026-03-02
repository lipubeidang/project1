<template>
  <div class="my-templates">
    <Navbar />
    
    <div class="page-container">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-bg">
          <div class="gradient-orb orb-1"></div>
          <div class="gradient-orb orb-2"></div>
        </div>
        <div class="header-content animate-slide-up">
          <div class="header-info">
            <h1 class="page-title">
              <el-icon class="title-icon"><User /></el-icon>
              我的模版
            </h1>
            <p class="page-subtitle">管理您创建的模版和查看审核状态</p>
          </div>
          <div class="header-actions">
            <el-button type="primary" size="large" class="create-btn" @click="goToCreate">
              <el-icon><Plus /></el-icon>
              创建新模版
            </el-button>
          </div>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-section animate-slide-up delay-1">
        <div class="stats-grid">
          <div class="stat-card" @click="filterByStatus('all')">
            <div class="stat-icon all">
              <el-icon :size="28"><Files /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total }}</span>
              <span class="stat-label">全部模版</span>
            </div>
          </div>
          <div class="stat-card" @click="filterByStatus('pending')">
            <div class="stat-icon pending">
              <el-icon :size="28"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.pending }}</span>
              <span class="stat-label">待审核</span>
            </div>
          </div>
          <div class="stat-card" @click="filterByStatus('approved')">
            <div class="stat-icon approved">
              <el-icon :size="28"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.approved }}</span>
              <span class="stat-label">已通过</span>
            </div>
          </div>
          <div class="stat-card" @click="filterByStatus('rejected')">
            <div class="stat-icon rejected">
              <el-icon :size="28"><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.rejected }}</span>
              <span class="stat-label">已拒绝</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="filter-section animate-slide-up delay-2">
        <div class="filter-left">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索模版名称..."
            :prefix-icon="Search"
            size="large"
            clearable
            class="search-input"
          />
          <el-select v-model="statusFilter" placeholder="状态筛选" size="large" class="status-select">
            <el-option label="全部状态" value="all" />
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </div>
        <div class="filter-right">
          <el-button :icon="Refresh" size="large" @click="loadMyTemplates">刷新</el-button>
        </div>
      </div>

      <!-- 模版列表 -->
      <div class="templates-section animate-slide-up delay-3" v-loading="loading">
        <!-- 待审核模版 -->
        <div class="template-group" v-if="shouldShowGroup('pending') && pendingTemplates.length > 0">
          <div class="group-header">
            <div class="group-title">
              <el-icon class="group-icon pending"><Clock /></el-icon>
              <span>待审核</span>
              <el-tag type="warning" size="small" effect="light">{{ pendingTemplates.length }}</el-tag>
            </div>
          </div>
          <div class="templates-grid">
            <div 
              v-for="template in pendingTemplates" 
              :key="template.templateId"
              class="template-card pending"
            >
              <div class="card-status">
                <span class="status-dot pending"></span>
                <span>待审核</span>
              </div>
              <div class="card-content">
                <div class="card-icon">
                  <el-icon :size="28"><Document /></el-icon>
                </div>
                <h3 class="card-title">{{ template.templateName }}</h3>
                <p class="card-desc">{{ template.note ? '审核意见: ' + template.note : '暂无审核意见' }}</p>
                <div class="card-meta">
                  <span class="meta-item">
                    <el-icon><Calendar /></el-icon>
                    {{ formatDate(template.createTime) }}
                  </span>
                </div>
              </div>
              <div class="card-actions">
                <el-button type="primary" size="small" text @click="viewTemplate(template)">
                  查看详情
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 已通过模版 -->
        <div class="template-group" v-if="shouldShowGroup('approved') && approvedTemplates.length > 0">
          <div class="group-header">
            <div class="group-title">
              <el-icon class="group-icon approved"><CircleCheck /></el-icon>
              <span>已通过</span>
              <el-tag type="success" size="small" effect="light">{{ approvedTemplates.length }}</el-tag>
            </div>
          </div>
          <div class="templates-grid">
            <div 
              v-for="template in approvedTemplates" 
              :key="template.templateId"
              class="template-card approved"
            >
              <div class="card-status">
                <span class="status-dot approved"></span>
                <span>已通过</span>
              </div>
              <div class="card-content">
                <div class="card-icon approved">
                  <el-icon :size="28"><Document /></el-icon>
                </div>
                <h3 class="card-title">{{ template.templateName }}</h3>
                <p class="card-desc">{{ template.note ? '审核意见: ' + template.note : '暂无审核意见' }}</p>
                <div class="card-meta">
                  <span class="meta-item">
                    <el-icon><Calendar /></el-icon>
                    {{ formatDate(template.createTime) }}
                  </span>
                </div>
              </div>
              <div class="card-actions">
                <el-button type="primary" size="small" text @click="viewTemplate(template)">
                  查看详情
                </el-button>
                <el-button type="warning" size="small" text @click="applyModify(template)">
                  申请修改
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 已拒绝模版 -->
        <div class="template-group" v-if="shouldShowGroup('rejected') && rejectedTemplates.length > 0">
          <div class="group-header">
            <div class="group-title">
              <el-icon class="group-icon rejected"><CircleClose /></el-icon>
              <span>已拒绝</span>
              <el-tag type="danger" size="small" effect="light">{{ rejectedTemplates.length }}</el-tag>
            </div>
          </div>
          <div class="templates-grid">
            <div 
              v-for="template in rejectedTemplates" 
              :key="template.templateId"
              class="template-card rejected"
            >
              <div class="card-status">
                <span class="status-dot rejected"></span>
                <span>已拒绝</span>
              </div>
              <div class="card-content">
                <div class="card-icon rejected">
                  <el-icon :size="28"><Document /></el-icon>
                </div>
                <h3 class="card-title">{{ template.templateName }}</h3>
                <p class="card-desc">{{ template.note ? '审核意见: ' + template.note : '暂无审核意见' }}</p>
                <div class="card-meta">
                  <span class="meta-item">
                    <el-icon><Calendar /></el-icon>
                    {{ formatDate(template.createTime) }}
                  </span>
                </div>
              </div>
              <div class="card-actions">
                <el-button type="primary" size="small" text @click="viewTemplate(template)">
                  查看详情
                </el-button>
                <el-button type="success" size="small" text @click="resubmit(template)">
                  重新提交
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty 
          v-if="!loading && displayedTemplates.length === 0" 
          :image-size="180"
          class="empty-state"
        >
          <template #description>
            <p class="empty-text">{{ emptyText }}</p>
          </template>
          <el-button type="primary" @click="goToCreate">创建第一个模版</el-button>
        </el-empty>
      </div>
    </div>

    <!-- 模版详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="currentTemplate?.templateName"
      size="520px"
      direction="rtl"
      class="template-drawer"
    >
      <div class="drawer-content" v-if="currentTemplate">
        <div class="detail-header">
          <div class="detail-icon" :class="getStatusClass(currentTemplate.state)">
            <el-icon :size="32"><Document /></el-icon>
          </div>
          <div class="detail-meta">
            <el-tag :type="getStatusType(currentTemplate.state)" effect="light">
              {{ getStatusText(currentTemplate.state) }}
            </el-tag>
          </div>
        </div>

        <div class="detail-section">
          <h4 class="section-title">基本信息</h4>
          <div class="info-list">
            <div class="info-row">
              <span class="label">创建时间</span>
              <span class="value">{{ currentTemplate.createTime || '未知' }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4 class="section-title">审核意见</h4>
          <p class="description-text">{{ currentTemplate.note || '暂无审核意见' }}</p>
        </div>

        <!-- 美化的字段信息展示 - 分区域显示 -->
        <div class="detail-section fields-section" v-if="hasFields">
          <h4 class="section-title">字段信息</h4>
          
          <!-- 对象区域 -->
          <div class="field-area" v-if="processedFields.object.length > 0">
            <div class="area-header object">
              <el-icon><Box /></el-icon>
              <span>对象区域</span>
              <el-tag size="small" type="primary">{{ processedFields.object.length }}</el-tag>
            </div>
            <div class="area-content">
              <template v-for="(item, index) in processedFields.object" :key="index">
                <div v-if="!item.isEnum" class="field-item">
                  <span class="field-name">{{ item.fieldName }}</span>
                  <el-tag size="small" :type="getDataTypeTagType(item.dataType)">{{ item.dataType }}</el-tag>
                </div>
                <div v-else class="enum-group">
                  <div class="enum-header">
                    <span class="enum-name">{{ item.enumName }}</span>
                    <el-tag size="small" type="danger">枚举型</el-tag>
                  </div>
                  <div class="enum-options">
                    <el-tag v-for="opt in item.options" :key="opt" size="small" effect="plain" class="enum-tag">{{ opt }}</el-tag>
                  </div>
                </div>
              </template>
            </div>
          </div>
          
          <!-- 操作区域 -->
          <div class="field-area" v-if="processedFields.operation.length > 0">
            <div class="area-header operation">
              <el-icon><Edit /></el-icon>
              <span>操作区域</span>
              <el-tag size="small" type="success">{{ processedFields.operation.length }}</el-tag>
            </div>
            <div class="area-content">
              <template v-for="(item, index) in processedFields.operation" :key="index">
                <div v-if="!item.isEnum" class="field-item">
                  <span class="field-name">{{ item.fieldName }}</span>
                  <el-tag size="small" :type="getDataTypeTagType(item.dataType)">{{ item.dataType }}</el-tag>
                </div>
                <div v-else class="enum-group">
                  <div class="enum-header">
                    <span class="enum-name">{{ item.enumName }}</span>
                    <el-tag size="small" type="danger">枚举型</el-tag>
                  </div>
                  <div class="enum-options">
                    <el-tag v-for="opt in item.options" :key="opt" size="small" effect="plain" class="enum-tag">{{ opt }}</el-tag>
                  </div>
                </div>
              </template>
            </div>
          </div>
          
          <!-- 结果区域 -->
          <div class="field-area" v-if="processedFields.result.length > 0">
            <div class="area-header result">
              <el-icon><DataLine /></el-icon>
              <span>结果区域</span>
              <el-tag size="small" type="warning">{{ processedFields.result.length }}</el-tag>
            </div>
            <div class="area-content">
              <template v-for="(item, index) in processedFields.result" :key="index">
                <div v-if="!item.isEnum" class="field-item">
                  <span class="field-name">{{ item.fieldName }}</span>
                  <el-tag size="small" :type="getDataTypeTagType(item.dataType)">{{ item.dataType }}</el-tag>
                </div>
                <div v-else class="enum-group">
                  <div class="enum-header">
                    <span class="enum-name">{{ item.enumName }}</span>
                    <el-tag size="small" type="danger">枚举型</el-tag>
                  </div>
                  <div class="enum-options">
                    <el-tag v-for="opt in item.options" :key="opt" size="small" effect="plain" class="enum-tag">{{ opt }}</el-tag>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
        
        <div class="detail-section" v-else-if="currentTemplate.templateFields && currentTemplate.templateFields.length === 0">
          <h4 class="section-title">字段信息</h4>
          <el-empty description="暂无字段信息" :image-size="60" />
        </div>

        <div class="drawer-footer">
          <el-button v-if="currentTemplate.state === 1" type="warning" @click="applyModify(currentTemplate)">
            申请修改
          </el-button>
          <el-button v-if="currentTemplate.state === 2" type="danger" disabled>
            审核中
          </el-button>
        </div>
      </div>
    </el-drawer>

    <!-- 申请修改对话框 -->
    <el-dialog
      v-model="modifyDialogVisible"
      title="申请修改模版"
      width="500px"
    >
      <div class="modify-form">
        <el-alert type="info" :closable="false" class="modify-tip">
          <template #title>
            <span>申请修改后，您的模版将进入审核流程，审核员会处理您的修改请求。</span>
          </template>
        </el-alert>
        <el-form :model="modifyForm" label-position="top">
          <el-form-item label="修改原因">
            <el-input
              v-model="modifyForm.reason"
              type="textarea"
              :rows="4"
              placeholder="请说明您需要修改的内容和原因..."
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="modifyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitModifyRequest" :loading="submitting">
          提交申请
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  User, Plus, Files, Clock, CircleCheck, CircleClose, 
  Search, Refresh, Document, Calendar, ArrowRight, Grid, Box, Edit, DataLine
} from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 状态
const loading = ref(false)
const submitting = ref(false)
const searchKeyword = ref('')
const statusFilter = ref('all')
const drawerVisible = ref(false)
const modifyDialogVisible = ref(false)
const currentTemplate = ref(null)
const modifyTemplate = ref(null)

// 模版数据
const allTemplates = ref([])
const modifyForm = ref({
  reason: ''
})

// 统计数据 (state: 0=未审核, 1=已审核, 2=已拒绝)
const stats = computed(() => {
  const pending = allTemplates.value.filter(t => t.state === 0).length
  const approved = allTemplates.value.filter(t => t.state === 1).length
  const rejected = allTemplates.value.filter(t => t.state === 2).length
  return {
    total: allTemplates.value.length,
    pending,
    approved,
    rejected
  }
})

// 过滤后的模版
const filteredTemplates = computed(() => {
  let result = [...allTemplates.value]
  
  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(t => 
      (t.templateName || '').toLowerCase().includes(keyword) ||
      (t.note || '').toLowerCase().includes(keyword)
    )
  }
  
  return result
})

const displayedTemplates = computed(() => filteredTemplates.value)

const pendingTemplates = computed(() => {
  return filteredTemplates.value.filter(t => t.state === 0)
})

const approvedTemplates = computed(() => {
  return filteredTemplates.value.filter(t => t.state === 1)
})

const rejectedTemplates = computed(() => {
  // 假设 state === 2 或其他值表示已拒绝
  return filteredTemplates.value.filter(t => t.state === 2)
})

const emptyText = computed(() => {
  if (searchKeyword.value) {
    return '没有找到匹配的模版'
  }
  if (statusFilter.value !== 'all') {
    return `暂无${getStatusText(statusFilter.value === 'pending' ? 0 : statusFilter.value === 'approved' ? 1 : 2)}的模版`
  }
  return '您还没有创建任何模版，点击下方按钮开始创建'
})

// 方法
const shouldShowGroup = (status) => {
  if (statusFilter.value === 'all') return true
  return statusFilter.value === status
}

const filterByStatus = (status) => {
  statusFilter.value = status
}

const loadMyTemplates = async () => {
  loading.value = true
  try {
    const username = userStore.userName
    if (!username) {
      ElMessage.warning('请先登录')
      return
    }
    
    // 调用接口获取当前用户的模版
    const response = await request.get(`/template/getTemplateByUsername/${username}`)
    
    if (response.data?.code === 1 || response.data?.code === 0) {
      allTemplates.value = response.data.data || []
    } else {
      allTemplates.value = []
      ElMessage.error(response.data?.message || '获取模版失败')
    }
  } catch (error) {
    console.error('加载我的模版失败:', error)
    ElMessage.error('加载模版失败')
  } finally {
    loading.value = false
  }
}

const viewTemplate = async (template) => {
  // 模版数据中已包含 templateFields 字段信息（来自 getTemplateByUsername 接口）
  currentTemplate.value = template
  console.log('查看模版详情:', template)
  drawerVisible.value = true
}

// 处理当前模版的字段信息 - 将枚举型字段按枚举名分组
const processedFields = computed(() => {
  if (!currentTemplate.value?.templateFields) {
    return { object: [], operation: [], result: [] }
  }
  
  const fields = currentTemplate.value.templateFields
  const result = { object: [], operation: [], result: [] }
  
  // 按区域分组
  const areaMap = { 1: 'object', 2: 'operation', 3: 'result' }
  
  // 临时存储枚举分组
  const enumGroups = { object: {}, operation: {}, result: {} }
  
  fields.forEach(field => {
    const areaKey = areaMap[field.fieldCategory] || 'object'
    const dataType = field.fieldDataType || field.dataType || ''
    const isEnum = dataType === '枚举型' || dataType === 4 || dataType === 5
    
    if (isEnum && field.fieldName && field.fieldName.includes(':')) {
      // 枚举型字段：解析 "枚举名:选项" 格式
      const [enumName, optionValue] = field.fieldName.split(':')
      if (!enumGroups[areaKey][enumName]) {
        enumGroups[areaKey][enumName] = []
      }
      enumGroups[areaKey][enumName].push(optionValue)
    } else {
      // 普通字段
      result[areaKey].push({
        isEnum: false,
        fieldName: field.fieldName,
        dataType: getDataTypeName(dataType)
      })
    }
  })
  
  // 将枚举分组添加到结果中
  Object.keys(enumGroups).forEach(areaKey => {
    Object.keys(enumGroups[areaKey]).forEach(enumName => {
      result[areaKey].push({
        isEnum: true,
        enumName: enumName,
        options: enumGroups[areaKey][enumName]
      })
    })
  })
  
  return result
})

// 获取数据类型对应的标签类型
const getDataTypeTagType = (dataType) => {
  const typeMap = {
    '字符串型': 'info',
    '数值型': 'success',
    '浮点型': 'warning',
    '范围型': 'primary',
    '枚举型': 'danger',
    '图片型': '',
    '文件型': 'info',
    '数组型': 'primary',
    '表格型': 'success',
    '日期型': 'warning'
  }
  return typeMap[dataType] || 'info'
}

// 检查是否有字段信息
const hasFields = computed(() => {
  if (!processedFields.value) return false
  return processedFields.value.object.length > 0 || 
         processedFields.value.operation.length > 0 || 
         processedFields.value.result.length > 0
})

const applyModify = (template) => {
  modifyTemplate.value = template
  modifyForm.value.reason = ''
  modifyDialogVisible.value = true
}

const submitModifyRequest = async () => {
  if (!modifyForm.value.reason.trim()) {
    ElMessage.warning('请填写修改原因')
    return
  }
  
  submitting.value = true
  try {
    // 提交修改申请
    const response = await request.post('/template/applyModify', {
      templateId: modifyTemplate.value.id,
      reason: modifyForm.value.reason
    })
    
    if (response.data?.code === 1) {
      ElMessage.success('修改申请已提交')
      modifyDialogVisible.value = false
      loadMyTemplates()
    } else {
      ElMessage.error(response.data?.message || '提交失败')
    }
  } catch (error) {
    console.error('提交修改申请失败:', error)
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const resubmit = (template) => {
  router.push({
    path: '/tplmanage/create',
    query: { resubmit: template.templateId }
  })
}

const goToCreate = () => {
  router.push('/tplmanage/create')
}

const getStatusType = (state) => {
  const types = { 0: 'warning', 1: 'success', 2: 'danger' }
  return types[state] || 'info'
}

const getStatusText = (state) => {
  const texts = { 0: '待审核', 1: '已通过', 2: '已拒绝' }
  return texts[state] || '未知'
}

const getStatusClass = (state) => {
  const classes = { 0: 'pending', 1: 'approved', 2: 'rejected' }
  return classes[state] || ''
}

const getDataTypeName = (type) => {
  // 如果已经是中文类型名，直接返回
  if (typeof type === 'string') {
    return type
  }
  // 兼容旧的数字类型
  const names = {
    0: '字符串型',
    1: '数值型',
    2: '浮点型',
    3: '日期型',
    4: '枚举型',
    5: '枚举型'
  }
  return names[type] || '未知'
}

const formatDate = (date) => {
  if (!date) return '未知'
  return date.split(' ')[0]
}

onMounted(() => {
  loadMyTemplates()
})
</script>

<style lang="scss" scoped>
.my-templates {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f4f8 0%, #f8fafc 100%);
}

.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 32px 60px;
}

// 页面头部
.page-header {
  position: relative;
  padding: 120px 0 60px;
  margin: 0 -32px;
  overflow: hidden;
}

.header-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 80px;
    background: linear-gradient(to bottom, transparent, #f0f4f8);
  }
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.3;
  
  &.orb-1 {
    width: 300px;
    height: 300px;
    background: rgba(255, 255, 255, 0.4);
    top: -50px;
    left: 10%;
    animation: float 8s ease-in-out infinite;
  }
  
  &.orb-2 {
    width: 200px;
    height: 200px;
    background: rgba(255, 255, 255, 0.3);
    bottom: 20%;
    right: 15%;
    animation: float 6s ease-in-out infinite reverse;
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.05); }
}

.header-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
  text-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  
  .title-icon {
    font-size: 2.5rem;
  }
}

.page-subtitle {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.9);
}

.create-btn {
  height: 52px;
  padding: 0 32px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  color: white;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  }
}

// 统计卡片
.stats-section {
  margin-top: -30px;
  position: relative;
  z-index: 10;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
  }
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  
  &.all {
    background: linear-gradient(135deg, #667eea, #764ba2);
  }
  
  &.pending {
    background: linear-gradient(135deg, #f59e0b, #fbbf24);
  }
  
  &.approved {
    background: linear-gradient(135deg, #10b981, #34d399);
  }
  
  &.rejected {
    background: linear-gradient(135deg, #ef4444, #f87171);
  }
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.9375rem;
  color: #64748b;
  margin-top: 4px;
}

// 搜索筛选
.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 32px 0 24px;
  gap: 16px;
}

.filter-left {
  display: flex;
  gap: 16px;
  flex: 1;
}

.search-input {
  max-width: 360px;
  
  :deep(.el-input__wrapper) {
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }
}

.status-select {
  width: 160px;
  
  :deep(.el-input__wrapper) {
    border-radius: 12px;
  }
}

// 模版组
.template-group {
  margin-bottom: 40px;
}

.group-header {
  margin-bottom: 20px;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  
  .group-icon {
    font-size: 1.25rem;
    
    &.pending { color: #f59e0b; }
    &.approved { color: #10b981; }
    &.rejected { color: #ef4444; }
  }
}

// 模版网格
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.template-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 2px solid transparent;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
  }
  
  &.pending {
    border-left: 4px solid #f59e0b;
  }
  
  &.approved {
    border-left: 4px solid #10b981;
  }
  
  &.rejected {
    border-left: 4px solid #ef4444;
  }
}

.card-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 0.8125rem;
  color: #64748b;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  
  &.pending { background: #f59e0b; }
  &.approved { background: #10b981; }
  &.rejected { background: #ef4444; }
}

.card-content {
  margin-bottom: 16px;
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 16px;
  
  &.approved {
    background: linear-gradient(135deg, #10b981, #34d399);
  }
  
  &.rejected {
    background: linear-gradient(135deg, #ef4444, #f87171);
  }
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-desc {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8125rem;
  color: #94a3b8;
}

.card-actions {
  display: flex;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

// 空状态
.empty-state {
  padding: 80px 0;
}

.empty-text {
  font-size: 1rem;
  color: #64748b;
}

// 抽屉
.drawer-content {
  padding: 0 8px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
}

.detail-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  
  &.approved {
    background: linear-gradient(135deg, #10b981, #34d399);
  }
  
  &.pending {
    background: linear-gradient(135deg, #f59e0b, #fbbf24);
  }
  
  &.rejected {
    background: linear-gradient(135deg, #ef4444, #f87171);
  }
}

.detail-section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 16px;
}

.info-list {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  
  &:not(:last-child) {
    border-bottom: 1px solid #e2e8f0;
  }
  
  .label {
    color: #64748b;
    font-size: 0.9375rem;
  }
  
  .value {
    color: #1e293b;
    font-weight: 500;
    font-size: 0.9375rem;
  }
}

.description-text {
  font-size: 0.9375rem;
  color: #475569;
  line-height: 1.7;
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
}

// 字段信息展示样式
.fields-section {
  .field-area {
    margin-bottom: 16px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  .area-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 10px;
    font-weight: 500;
    font-size: 0.875rem;
    
    &.object {
      background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
      color: #667eea;
    }
    
    &.operation {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(52, 211, 153, 0.1));
      color: #10b981;
    }
    
    &.result {
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(251, 191, 36, 0.1));
      color: #f59e0b;
    }
  }
  
  .area-content {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding-left: 12px;
  }
  
  .field-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    background: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    
    .field-name {
      font-size: 0.8125rem;
      color: #334155;
    }
  }
  
  .enum-group {
    background: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    overflow: hidden;
    
    .enum-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 14px;
      background: linear-gradient(135deg, rgba(236, 72, 153, 0.05), rgba(236, 72, 153, 0.1));
      border-bottom: 1px solid #fce7f3;
      
      .enum-name {
        font-size: 0.8125rem;
        font-weight: 600;
        color: #be185d;
      }
    }
    
    .enum-options {
      padding: 10px 14px;
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      
      .enum-tag {
        background: #fdf2f8;
        border-color: #fbcfe8;
        color: #be185d;
      }
    }
  }
}

.drawer-footer {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  gap: 12px;
}

// 修改申请对话框
.modify-tip {
  margin-bottom: 20px;
}

// 动画
.animate-slide-up {
  animation: slideUp 0.6s ease-out forwards;
  
  &.delay-1 { animation-delay: 0.1s; opacity: 0; }
  &.delay-2 { animation-delay: 0.2s; opacity: 0; }
  &.delay-3 { animation-delay: 0.3s; opacity: 0; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 响应式
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 0 16px 40px;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
    gap: 24px;
  }
  
  .page-title {
    font-size: 2rem;
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-icon {
    width: 48px;
    height: 48px;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-left {
    flex-direction: column;
  }
  
  .search-input {
    max-width: none;
  }
  
  .templates-grid {
    grid-template-columns: 1fr;
  }
}
</style>
