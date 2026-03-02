<template>
  <div class="tpl-detail">
    <Navbar />
    
    <div class="page-container">
      <!-- 内容区 -->
      <div class="content-wrapper" v-loading="loading">
        <!-- 基本信息卡片 -->
        <div class="info-card animate-slide-up delay-1">
          <div class="card-header">
            <el-icon class="card-icon"><InfoFilled /></el-icon>
            <h3>基本信息</h3>
          </div>
          <div class="card-body">
            <div class="info-grid">
              <div class="info-item">
                <span class="label">模版ID</span>
                <span class="value">{{ templateInfo.id }}</span>
              </div>
              <div class="info-item">
                <span class="label">模版名称</span>
                <span class="value">{{ templateInfo.name || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="label">创建者</span>
                <span class="value">{{ templateInfo.creator || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="label">创建时间</span>
                <span class="value">{{ formatDate(templateInfo.createTime) }}</span>
              </div>
              <div class="info-item">
                <span class="label">分类</span>
                <span class="value">{{ categoryName }}</span>
              </div>
              <div class="info-item">
                <span class="label">状态</span>
                <span class="value">
                  <el-tag :type="getStatusType(templateInfo.state)" size="small">
                    {{ getStatusText(templateInfo.state) }}
                  </el-tag>
                </span>
              </div>
            </div>
            <div class="info-description">
              <span class="label">描述</span>
              <p class="value">{{ templateInfo.description || '暂无描述信息' }}</p>
            </div>
          </div>
        </div>

        <!-- 字段信息卡片 -->
        <div class="fields-card animate-slide-up delay-2">
          <div class="card-header">
            <el-icon class="card-icon"><List /></el-icon>
            <h3>字段列表</h3>
            <el-tag size="small" type="info" class="field-count">
              共 {{ templateFields.length }} 个字段
            </el-tag>
          </div>
          <div class="card-body">
            <!-- 美化的分区展示 -->
            <div class="fields-display" v-if="hasProcessedFields">
              <!-- 对象区域 -->
              <div class="field-area" v-if="processedFields.object.length > 0">
                <div class="area-header object">
                  <el-icon><Box /></el-icon>
                  <span>对象区域</span>
                  <el-tag size="small" type="primary">{{ processedFields.object.length }} 个字段</el-tag>
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
                  <el-tag size="small" type="success">{{ processedFields.operation.length }} 个字段</el-tag>
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
                  <el-tag size="small" type="warning">{{ processedFields.result.length }} 个字段</el-tag>
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
            <el-empty v-else description="暂无字段信息" :image-size="100">
              <el-button type="primary" @click="goToFieldEdit" v-if="canEdit">
                添加字段
              </el-button>
            </el-empty>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, Edit, Upload, InfoFilled, List, Grid, Box, DataLine
} from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'
import { findCategoryById, getNumericCategoryId } from '@/utils/templateCategories'

const router = useRouter()
const route = useRoute()

// 状态
const loading = ref(false)

// 模版信息
const templateInfo = ref({
  id: '',
  name: '',
  description: '',
  creator: '',
  createTime: '',
  state: 0,
  categoryId: null
})

// 模版字段
const templateFields = ref([])

// 分类名称
const categoryName = computed(() => {
  if (templateInfo.value.categoryId) {
    const category = findCategoryById(templateInfo.value.categoryId)
    return category?.name || '未知分类'
  }
  return '未知分类'
})

// 是否可编辑（根据需要调整权限逻辑）
const canEdit = computed(() => {
  return true
})

// 处理字段信息 - 将枚举型字段按枚举名分组
const processedFields = computed(() => {
  if (!templateFields.value || templateFields.value.length === 0) {
    return { object: [], operation: [], result: [] }
  }
  
  const fields = templateFields.value
  const result = { object: [], operation: [], result: [] }
  
  // 按区域分组
  const areaMap = { 1: 'object', 2: 'operation', 3: 'result' }
  
  // 临时存储枚举分组
  const enumGroups = { object: {}, operation: {}, result: {} }
  
  fields.forEach(field => {
    const areaKey = areaMap[field.fieldCategory] || 'object'
    const dataType = field.fieldDataType || field.dataType || ''
    const dataTypeName = getDataTypeName(dataType)
    const isEnum = dataTypeName === '枚举型' || dataTypeName.includes('枚举')
    
    if (isEnum && field.fieldName && field.fieldName.includes(':')) {
      // 枚举型字段：解析 "枚举名:选项" 格式
      const colonIndex = field.fieldName.indexOf(':')
      const enumName = field.fieldName.substring(0, colonIndex)
      const optionValue = field.fieldName.substring(colonIndex + 1)
      if (!enumGroups[areaKey][enumName]) {
        enumGroups[areaKey][enumName] = []
      }
      enumGroups[areaKey][enumName].push(optionValue)
    } else {
      // 普通字段
      result[areaKey].push({
        isEnum: false,
        fieldName: field.fieldName,
        dataType: dataTypeName
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

// 检查是否有字段信息
const hasProcessedFields = computed(() => {
  if (!processedFields.value) return false
  return processedFields.value.object.length > 0 || 
         processedFields.value.operation.length > 0 || 
         processedFields.value.result.length > 0
})

// 获取数据类型对应的标签类型
const getDataTypeTagType = (dataType) => {
  const typeMap = {
    '字符串型': 'info',
    '字符串': 'info',
    '数值型': 'success',
    '数字': 'success',
    '浮点型': 'warning',
    '范围型': 'primary',
    '枚举型': 'danger',
    '图片型': '',
    '文件型': 'info',
    '数组型': 'primary',
    '表格型': 'success',
    '日期型': 'warning',
    '日期': 'warning',
    '文本': 'info'
  }
  return typeMap[dataType] || 'info'
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 跳转到上传数据页面
const goToUpload = () => {
  router.push({
    path: '/tplmanage/upload',
    query: {
      template: templateInfo.value.id,
      category: templateInfo.value.categoryId
    }
  })
}

// 跳转到字段编辑页面
const goToFieldEdit = () => {
  router.push(`/tplmanage/field-edit/${templateInfo.value.id}`)
}

// 状态类型
const getStatusType = (state) => {
  const types = { 0: 'info', 1: 'success', 2: 'warning' }
  return types[state] || 'info'
}

// 状态文本
const getStatusText = (state) => {
  const texts = { 0: '待审核', 1: '已发布', 2: '审核中' }
  return texts[state] || '未知'
}

// 字段类别类型
const getFieldCategoryType = (category) => {
  const types = {
    1: 'danger',   // 必填
    2: 'warning',  // 选填
    3: 'success'   // 自动
  }
  return types[category] || 'info'
}

// 字段类别名称
const getFieldCategoryName = (category) => {
  const names = {
    1: '对象字段',
    2: '操作字段',
    3: '结果字段'
  }
  return names[category] || `类型${category}`
}

// 数据类型名称 - 支持中文类型名
const getDataTypeName = (dataType) => {
  // 如果已经是中文类型名，直接返回
  if (typeof dataType === 'string') {
    return dataType
  }
  // 兼容旧的数字类型
  const typeMap = {
    0: '字符串型',
    1: '数值型',
    2: '浮点型',
    3: '日期型',
    4: '枚举型',
    5: '枚举型'
  }
  return typeMap[dataType] !== undefined ? typeMap[dataType] : `类型${dataType}`
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '未知'
  return date.split(' ')[0]
}

// 加载模版信息
const loadTemplateInfo = async () => {
  const templateId = route.params.templateId
  const categoryId = route.query.category
  
  if (!templateId) {
    ElMessage.error('模版ID不存在')
    router.back()
    return
  }
  
  loading.value = true
  
  try {
    // 如果有分类ID，尝试从分类接口获取模版信息
    if (categoryId) {
      const numericCategoryId = getNumericCategoryId(categoryId)
      if (numericCategoryId > 0) {
        // 获取简要信息
        const response = await request.get(`/template/getTemplateByCategory/${numericCategoryId}`)
        if (response.data?.code === 1) {
          const templates = response.data.data || []
          const template = templates.find(t => String(t.id) === String(templateId))
          if (template) {
            templateInfo.value = {
              ...template,
              categoryId: categoryId
            }
          }
        }
        
        // 获取详细信息（包含字段）
        const detailResponse = await request.get(`/template/getDetailedTemplateByCategory/${numericCategoryId}`)
        if (detailResponse.data?.code === 1 || detailResponse.data?.code === 0) {
          const detailedTemplates = detailResponse.data.data || []
          const detailedTemplate = detailedTemplates.find(t => String(t.templateId) === String(templateId))
          if (detailedTemplate && detailedTemplate.templateFields) {
            templateFields.value = detailedTemplate.templateFields
            // 如果之前没有获取到基本信息，使用详细信息
            if (!templateInfo.value.name && detailedTemplate.templateName) {
              templateInfo.value.name = detailedTemplate.templateName
            }
          }
        }
      }
    }
    
    // 如果还没有获取到字段信息，尝试从审核接口获取
    if (templateFields.value.length === 0) {
      try {
        const auditResponse = await request.get('/audit/getTemp')
        if (auditResponse.data?.code === 1) {
          const auditTemplates = auditResponse.data.data || []
          const auditTemplate = auditTemplates.find(t => String(t.templateId) === String(templateId))
          if (auditTemplate && auditTemplate.templateFields) {
            templateFields.value = auditTemplate.templateFields
          }
        }
      } catch (error) {
        console.error('从审核接口获取字段失败:', error)
      }
    }
    
    // 如果仍然没有基本信息，尝试遍历所有分类获取
    if (!templateInfo.value.name) {
      await loadTemplateFromAllCategories(templateId)
    }
    
  } catch (error) {
    console.error('加载模版信息失败:', error)
    ElMessage.error('加载模版信息失败')
  } finally {
    loading.value = false
  }
}

// 从所有分类中查找模版
const loadTemplateFromAllCategories = async (templateId) => {
  const allCategoryIds = [1, ...Array.from({length: 24}, (_, i) => i + 9)]
  
  for (const catId of allCategoryIds) {
    try {
      const response = await request.get(`/template/getTemplateByCategory/${catId}`)
      if (response.data?.code === 1) {
        const templates = response.data.data || []
        const template = templates.find(t => String(t.id) === String(templateId))
        if (template) {
          templateInfo.value = {
            ...template,
            categoryId: catId
          }
          
          // 获取字段信息
          if (templateFields.value.length === 0) {
            const detailResponse = await request.get(`/template/getDetailedTemplateByCategory/${catId}`)
            if (detailResponse.data?.code === 1 || detailResponse.data?.code === 0) {
              const detailedTemplates = detailResponse.data.data || []
              const detailedTemplate = detailedTemplates.find(t => String(t.templateId) === String(templateId))
              if (detailedTemplate && detailedTemplate.templateFields) {
                templateFields.value = detailedTemplate.templateFields
              }
            }
          }
          
          break
        }
      }
    } catch (error) {
      // 继续尝试下一个分类
    }
  }
}

onMounted(() => {
  loadTemplateInfo()
})
</script>

<style lang="scss" scoped>
.tpl-detail {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f4f8 0%, #f8fafc 100%);
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-card,
.fields-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  
  .card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 20px 24px;
    border-bottom: 1px solid #f0f0f0;
    background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
    
    .card-icon {
      font-size: 20px;
      color: #667eea;
    }
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: #1a1a2e;
      margin: 0;
      flex: 1;
    }
    
    .field-count {
      margin-left: auto;
    }
  }
  
  .card-body {
    padding: 24px;
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
  
  .info-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
    
    .label {
      font-size: 13px;
      color: #6b7280;
    }
    
    .value {
      font-size: 15px;
      color: #1a1a2e;
      font-weight: 500;
    }
  }
}

.info-description {
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
  
  .label {
    display: block;
    font-size: 13px;
    color: #6b7280;
    margin-bottom: 8px;
  }
  
  .value {
    font-size: 14px;
    color: #374151;
    line-height: 1.6;
    margin: 0;
  }
}

.fields-table {
  :deep(.el-table) {
    border-radius: 8px;
    overflow: hidden;
    
    th {
      background: #f8fafc !important;
      color: #374151;
      font-weight: 600;
    }
    
    .field-name {
      font-weight: 500;
      color: #1a1a2e;
    }
  }
}

// 美化的字段展示样式
.fields-display {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.field-area {
  .area-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 12px;
    font-weight: 600;
    font-size: 0.9375rem;
    
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
    gap: 10px;
    padding-left: 16px;
  }
  
  .field-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: #f8fafc;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    transition: all 0.2s ease;
    
    &:hover {
      border-color: #667eea;
      box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    }
    
    .field-name {
      font-size: 0.9375rem;
      color: #334155;
      font-weight: 500;
    }
  }
  
  .enum-group {
    background: #f8fafc;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    overflow: hidden;
    transition: all 0.2s ease;
    
    &:hover {
      border-color: #ec4899;
      box-shadow: 0 2px 8px rgba(236, 72, 153, 0.1);
    }
    
    .enum-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      background: linear-gradient(135deg, rgba(236, 72, 153, 0.05), rgba(236, 72, 153, 0.1));
      border-bottom: 1px solid #fce7f3;
      
      .enum-name {
        font-size: 0.9375rem;
        font-weight: 600;
        color: #be185d;
      }
    }
    
    .enum-options {
      padding: 12px 16px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      
      .enum-tag {
        background: #fdf2f8;
        border-color: #fbcfe8;
        color: #be185d;
      }
    }
  }
}

// 动画
.animate-slide-up {
  animation: slideUp 0.5s ease-out forwards;
  opacity: 0;
  
  &.delay-1 {
    animation-delay: 0.1s;
  }
  
  &.delay-2 {
    animation-delay: 0.2s;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 响应式
@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
