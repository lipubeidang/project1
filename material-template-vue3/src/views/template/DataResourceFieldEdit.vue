<template>
  <div class="template-field-edit">
    <Navbar />
    
    <div class="page-container">
      <!-- 页面头部 -->
      <div class="page-header animate-slide-up">
        <div class="header-content">
          <el-button :icon="ArrowLeft" text @click="goBack">返回</el-button>
          <div class="header-info">
            <h1 class="page-title">模板字段修改</h1>
            <span class="template-name">{{ templateName }}</span>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" :icon="Refresh" @click="loadFieldInfo">刷新</el-button>
        </div>
      </div>

      <!-- 模板信息 -->
      <div class="info-card animate-slide-up delay-1">
        <div class="info-grid">
          <div class="info-item">
            <span class="label">模板名称</span>
            <span class="value">{{ templateName || '未知模板' }}</span>
          </div>
          <div class="info-item">
            <span class="label">模板ID</span>
            <span class="value">{{ templateId }}</span>
          </div>
        </div>
      </div>

      <!-- 字段列表 -->
      <div class="fields-container animate-slide-up delay-2" v-loading="loading">
        <!-- 对象区域 -->
        <div class="field-section" v-if="fieldsBySection.object.length > 0">
          <div class="section-header" style="background: linear-gradient(135deg, #667eea, #764ba2)">
            <el-icon><Box /></el-icon>
            <span>对象区域</span>
            <el-tag size="small" effect="plain">{{ fieldsBySection.object.length }} 个字段</el-tag>
          </div>
          <div class="section-body">
            <div 
              v-for="(field, index) in fieldsBySection.object" 
              :key="`object_${index}`"
              class="field-item"
              :class="{ 'is-enum': isEnumField(field) }"
            >
              <div class="field-info">
                <span class="field-name">{{ getFieldName(field) }}</span>
                <el-tag size="small" :type="isEnumField(field) ? 'danger' : 'info'">
                  {{ getFieldType(field) }}
                </el-tag>
              </div>
              <div class="field-actions">
                <el-button 
                  v-if="isEnumField(field)"
                  type="primary" 
                  size="small"
                  :icon="Edit"
                  @click="editEnumField(field, 'object', index)"
                >
                  编辑枚举
                </el-button>
                <el-button 
                  v-else
                  type="info" 
                  size="small"
                  disabled
                >
                  暂不支持
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作区域 -->
        <div class="field-section" v-if="fieldsBySection.operation.length > 0">
          <div class="section-header" style="background: linear-gradient(135deg, #10b981, #34d399)">
            <el-icon><Setting /></el-icon>
            <span>操作区域</span>
            <el-tag size="small" effect="plain">{{ fieldsBySection.operation.length }} 个字段</el-tag>
          </div>
          <div class="section-body">
            <div 
              v-for="(field, index) in fieldsBySection.operation" 
              :key="`operation_${index}`"
              class="field-item"
              :class="{ 'is-enum': isEnumField(field) }"
            >
              <div class="field-info">
                <span class="field-name">{{ getFieldName(field) }}</span>
                <el-tag size="small" :type="isEnumField(field) ? 'danger' : 'info'">
                  {{ getFieldType(field) }}
                </el-tag>
              </div>
              <div class="field-actions">
                <el-button 
                  v-if="isEnumField(field)"
                  type="primary" 
                  size="small"
                  :icon="Edit"
                  @click="editEnumField(field, 'operation', index)"
                >
                  编辑枚举
                </el-button>
                <el-button 
                  v-else
                  type="info" 
                  size="small"
                  disabled
                >
                  暂不支持
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 结果区域 -->
        <div class="field-section" v-if="fieldsBySection.result.length > 0">
          <div class="section-header" style="background: linear-gradient(135deg, #f59e0b, #fbbf24)">
            <el-icon><DataLine /></el-icon>
            <span>结果区域</span>
            <el-tag size="small" effect="plain">{{ fieldsBySection.result.length }} 个字段</el-tag>
          </div>
          <div class="section-body">
            <div 
              v-for="(field, index) in fieldsBySection.result" 
              :key="`result_${index}`"
              class="field-item"
              :class="{ 'is-enum': isEnumField(field) }"
            >
              <div class="field-info">
                <span class="field-name">{{ getFieldName(field) }}</span>
                <el-tag size="small" :type="isEnumField(field) ? 'danger' : 'info'">
                  {{ getFieldType(field) }}
                </el-tag>
              </div>
              <div class="field-actions">
                <el-button 
                  v-if="isEnumField(field)"
                  type="primary" 
                  size="small"
                  :icon="Edit"
                  @click="editEnumField(field, 'result', index)"
                >
                  编辑枚举
                </el-button>
                <el-button 
                  v-else
                  type="info" 
                  size="small"
                  disabled
                >
                  暂不支持
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 无字段提示 -->
        <el-empty 
          v-if="!loading && !hasAnyFields" 
          description="该模板暂无字段信息"
          :image-size="120"
        />
      </div>
    </div>

    <!-- 枚举编辑对话框 -->
    <el-dialog
      v-model="enumDialogVisible"
      :title="`编辑枚举字段: ${currentEditField.columnName || getFieldName(currentEditField)}`"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="enum-edit-content">
        <!-- 字段信息 -->
        <div class="field-info-display">
          <div class="info-row">
            <span class="label">字段名称：</span>
            <span class="value">{{ getFieldName(currentEditField) }}</span>
          </div>
          <div class="info-row">
            <span class="label">所属区域：</span>
            <span class="value">{{ getSectionLabel(currentEditSection) }}</span>
          </div>
          <div class="info-row">
            <span class="label">字段类型：</span>
            <span class="value">{{ getFieldType(currentEditField) }}</span>
          </div>
        </div>

        <!-- 帮助提示 -->
        <el-alert type="info" :closable="false" class="help-alert">
          <template #title>
            <strong>配置说明</strong>
          </template>
          <p>• <strong>选项标签</strong>：自动按顺序生成（A、B、C、D...），不可修改</p>
          <p>• <strong>选项内容</strong>：填写选项的具体含义（如：固体、液体、气体等）</p>
          <p>• <strong>显示效果</strong>：如果有内容，显示为"A: 固体"；如果无内容，显示为"A"</p>
        </el-alert>

        <!-- 枚举选项列表 -->
        <div class="enum-options">
          <div 
            v-for="(option, index) in enumOptions" 
            :key="index"
            class="enum-option-item"
          >
            <div class="option-label">{{ option.label }}</div>
            <el-input
              v-model="option.value"
              placeholder="请输入选项内容"
              style="flex: 1"
            />
            <el-button 
              type="danger" 
              :icon="Delete"
              circle
              size="small"
              @click="removeEnumOption(index)"
              :disabled="enumOptions.length <= 1"
            />
          </div>
        </div>

        <!-- 添加按钮 -->
        <div class="enum-add-action">
          <el-button type="success" :icon="Plus" @click="addEnumOption">添加选项</el-button>
        </div>
      </div>

      <template #footer>
        <el-button @click="enumDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveEnumConfig">保存配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, Refresh, Edit, Delete, Plus, Box, Setting, DataLine 
} from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()

// 基础数据
const templateId = ref('')
const templateName = ref('')
const loading = ref(false)
const saving = ref(false)

// 字段数据
const fieldsBySection = reactive({
  object: [],
  operation: [],
  result: []
})

// 枚举编辑相关
const enumDialogVisible = ref(false)
const currentEditField = ref({})
const currentEditSection = ref('')
const currentEditIndex = ref(-1)
const enumOptions = ref([])

// 计算属性
const hasAnyFields = computed(() => {
  return fieldsBySection.object.length > 0 ||
         fieldsBySection.operation.length > 0 ||
         fieldsBySection.result.length > 0
})

// 获取字段名称
const getFieldName = (field) => {
  return field.columnName || field.column_name || field.fieldName || field.name || '未知字段'
}

// 获取字段类型
const getFieldType = (field) => {
  return field.columnContribution || field.column_contribution || field.contribution || field.type || '未知类型'
}

// 判断是否为枚举字段
const isEnumField = (field) => {
  const type = getFieldType(field)
  return type === '枚举型' || type === '枚举' || type === 'enum'
}

// 获取区域标签
const getSectionLabel = (section) => {
  const labels = {
    object: '对象区域',
    operation: '操作区域',
    result: '结果区域'
  }
  return labels[section] || section
}

// 生成字母标签
const generateLabel = (index) => {
  return String.fromCharCode(65 + index)
}

// 重新生成所有标签
const regenerateLabels = () => {
  enumOptions.value.forEach((option, index) => {
    option.label = generateLabel(index)
  })
}

// 加载字段信息
const loadFieldInfo = async () => {
  if (!templateId.value) {
    ElMessage.warning('缺少模板ID参数')
    return
  }

  loading.value = true
  try {
    console.log('加载模板字段信息，模板ID:', templateId.value)
    
    const response = await request.get(`/basemodule/moduledata/getColumnInfo/${templateId.value}`)
    console.log('📥 后端返回的字段信息:', response.data)
    
    if (response.data?.code === 0) {
      const columnInfo = response.data.columnInfo || response.data.data || {}
      
      // 从后端响应中获取模板名称（与 DataEntry.vue 一致）
      const backendTemplateName = response.data.templateName || 
                                  response.data.name || 
                                  response.data.moduleName || ''
      
      if (backendTemplateName && !templateName.value) {
        templateName.value = backendTemplateName
        console.log('📝 从后端获取到模板名称:', templateName.value)
      }
      
      fieldsBySection.object = columnInfo.object || []
      fieldsBySection.operation = columnInfo.operation || []
      fieldsBySection.result = columnInfo.result || []
      
      console.log('字段信息加载成功:', fieldsBySection)
      console.log('📋 模板名称:', templateName.value)
      console.log('🆔 模板ID:', templateId.value)
    } else {
      throw new Error(response.data?.msg || '获取字段信息失败')
    }
  } catch (error) {
    console.error('加载字段信息失败:', error)
    ElMessage.error('加载字段信息失败: ' + (error.message || '请重试'))
  } finally {
    loading.value = false
  }
}

// 编辑枚举字段
const editEnumField = (field, section, index) => {
  console.log('编辑枚举字段:', field, section, index)
  
  currentEditField.value = field
  currentEditSection.value = section
  currentEditIndex.value = index
  
  // 使用字段中已有的枚举选项，如果没有则使用默认选项
  const fieldEnumOptions = field.enumOptions || [
    { label: 'A', value: '' },
    { label: 'B', value: '' }
  ]
  
  enumOptions.value = JSON.parse(JSON.stringify(fieldEnumOptions))
  regenerateLabels()
  enumDialogVisible.value = true
}

// 添加枚举选项
const addEnumOption = () => {
  enumOptions.value.push({
    label: generateLabel(enumOptions.value.length),
    value: ''
  })
}

// 删除枚举选项
const removeEnumOption = (index) => {
  if (enumOptions.value.length > 1) {
    enumOptions.value.splice(index, 1)
    regenerateLabels()
  }
}

// 保存枚举配置
const saveEnumConfig = () => {
  // 验证和处理枚举选项
  enumOptions.value.forEach((option, index) => {
    option.label = generateLabel(index)
    if (!option.value || option.value.trim() === '') {
      option.value = option.label
    }
  })
  
  // 直接更新字段中的枚举选项
  if (currentEditField.value) {
    currentEditField.value.enumOptions = JSON.parse(JSON.stringify(enumOptions.value))
  }
  
  ElMessage.success('枚举配置保存成功！')
  enumDialogVisible.value = false
}

// 返回上一页
const goBack = () => {
  router.go(-1)
}

// 初始化
onMounted(() => {
  templateId.value = route.params.templateId || route.query.templateId || ''
  templateName.value = route.params.templateName || route.query.templateName || ''
  
  console.log('页面加载，模板参数:', {
    templateId: templateId.value,
    templateName: templateName.value
  })
  
  if (!templateId.value) {
    ElMessage.error('缺少模板ID参数')
    goBack()
    return
  }
  
  loadFieldInfo()
})
</script>

<style lang="scss" scoped>
.template-field-edit {
  min-height: 100vh;
  background: #f1f5f9;
}

.page-container {
  padding-top: 72px;
  min-height: 100vh;
  max-width: 1000px;
  margin: 0 auto;
  padding-left: 24px;
  padding-right: 24px;
}

// 页面头部
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 0;
  
  .header-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .header-info {
    .page-title {
      font-size: 1.5rem;
      font-weight: 700;
      color: #1e293b;
      margin: 0;
    }
    
    .template-name {
      font-size: 0.875rem;
      color: #64748b;
    }
  }
}

// 信息卡片
.info-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  
  .info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }
  
  .info-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    
    .label {
      font-size: 0.875rem;
      color: #64748b;
    }
    
    .value {
      font-size: 1rem;
      font-weight: 600;
      color: #1e293b;
    }
  }
}

// 字段容器
.fields-container {
  margin-bottom: 48px;
}

// 字段区域
.field-section {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  
  .section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 24px;
    color: white;
    font-weight: 600;
    
    .el-tag {
      margin-left: auto;
      background: rgba(255, 255, 255, 0.2);
      border: none;
      color: white;
    }
  }
  
  .section-body {
    padding: 0;
  }
}

// 字段项
.field-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #f1f5f9;
  transition: all 0.2s ease;
  
  &:last-child {
    border-bottom: none;
  }
  
  &:hover {
    background: #f8fafc;
  }
  
  &.is-enum {
    background: linear-gradient(90deg, rgba(236, 72, 153, 0.05) 0%, transparent 100%);
    
    &:hover {
      background: linear-gradient(90deg, rgba(236, 72, 153, 0.1) 0%, transparent 100%);
    }
  }
  
  .field-info {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .field-name {
      font-weight: 500;
      color: #1e293b;
    }
  }
}

// 枚举编辑内容
.enum-edit-content {
  .field-info-display {
    background: #f8fafc;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 16px;
    
    .info-row {
      display: flex;
      margin-bottom: 8px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .label {
        color: #64748b;
        min-width: 80px;
      }
      
      .value {
        color: #1e293b;
        font-weight: 500;
      }
    }
  }
  
  .help-alert {
    margin-bottom: 20px;
    
    p {
      margin: 4px 0;
      font-size: 0.875rem;
    }
  }
}

// 枚举选项
.enum-options {
  margin: 16px 0;
}

.enum-option-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 12px;
  
  .option-label {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    font-weight: 700;
    border-radius: 10px;
    font-size: 1rem;
  }
}

.enum-add-action {
  text-align: center;
  padding-top: 8px;
}

// 动画
.animate-slide-up {
  animation: slideUp 0.4s ease;
}

.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.2s; }

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
</style>
