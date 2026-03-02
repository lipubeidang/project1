<template>
  <div class="tpl-create">
    <Navbar />
    
    <div class="page-container">
      <!-- 步骤导航 -->
      <div class="steps-header animate-slide-up">
        <div class="steps-container">
          <div 
            v-for="(step, index) in steps" 
            :key="step.title"
            class="step-item"
            :class="{ 
              active: currentStep === index,
              completed: currentStep > index
            }"
          >
            <div class="step-circle">
              <el-icon v-if="currentStep > index"><Check /></el-icon>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <div class="step-info">
              <span class="step-title">{{ step.title }}</span>
              <span class="step-desc">{{ step.desc }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤内容 -->
      <div class="step-content">
        <!-- 步骤1: 基础设置 -->
        <Transition name="fade" mode="out-in">
          <div v-if="currentStep === 0" class="form-section animate-scale-in">
            <div class="section-card">
              <div class="card-header">
                <div class="header-icon">
                  <el-icon :size="28"><Setting /></el-icon>
                </div>
                <div class="header-info">
                  <h2>基础设置</h2>
                  <p>设置模版的基本信息和分类</p>
                </div>
              </div>
              
              <el-form 
                ref="basicFormRef" 
                :model="templateForm" 
                :rules="basicRules"
                label-position="top"
                class="template-form"
              >
                <div class="form-grid">
                  <el-form-item label="模版目录" prop="bigCategory">
                    <el-select 
                      v-model="templateForm.bigCategory" 
                      placeholder="请选择模版目录"
                      size="large"
                      @change="handleBigCategoryChange"
                    >
                      <el-option 
                        v-for="cat in bigCategories" 
                        :key="cat.id" 
                        :label="cat.name" 
                        :value="cat.id" 
                      />
                    </el-select>
                  </el-form-item>

                  <el-form-item v-if="hasSubCategories" label="子目录" prop="parent">
                    <el-select 
                      v-model="templateForm.parent" 
                      placeholder="请先选择大目录"
                      size="large"
                      :disabled="!templateForm.bigCategory"
                    >
                      <el-option 
                        v-for="sub in currentSubCategories" 
                        :key="sub.id" 
                        :label="sub.name" 
                        :value="sub.id"
                      />
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item v-else class="form-placeholder">
                    <template #label><span style="color: #909399">子目录</span></template>
                    <el-tag type="info" size="large">该分类无子目录</el-tag>
                  </el-form-item>
                </div>

                <el-form-item label="模版名称" prop="name">
                  <el-input 
                    v-model="templateForm.name" 
                    placeholder="请输入模版名称"
                    size="large"
                  />
                </el-form-item>

                <el-form-item label="模版说明" prop="description">
                  <el-input
                    v-model="templateForm.description"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入模版说明，帮助其他用户了解此模版的用途"
                    resize="none"
                  />
                </el-form-item>
              </el-form>
            </div>
          </div>

          <!-- 步骤2: 模板设计 -->
          <div v-else-if="currentStep === 1" class="design-section animate-scale-in">
            <div class="design-layout">
              <!-- 左侧字段类型工具栏 -->
              <div class="toolbar-sidebar">
                <div class="toolbar-card">
                  <h3 class="toolbar-title">
                    <el-icon><Grid /></el-icon>
                    字段类型
                  </h3>
                  <div class="field-types">
                    <div 
                      v-for="type in fieldTypes" 
                      :key="type.value"
                      class="field-type-chip"
                      draggable="true"
                      @dragstart="handleDragStart($event, type)"
                    >
                      <el-icon :style="{ color: type.color }">
                        <component :is="type.icon" />
                      </el-icon>
                      <span>{{ type.label }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 右侧设计区域 -->
              <div class="design-main">
                <div class="design-grid">
                  <div 
                    v-for="area in designAreas" 
                    :key="area.key"
                    class="design-area"
                    :class="{ 'drag-over': dragOverArea === area.key }"
                    @dragover.prevent
                    @dragenter="handleDragEnter(area.key)"
                    @dragleave="handleDragLeave"
                    @drop="handleDrop(area.key)"
                  >
                    <div class="area-header" :style="{ background: area.gradient }">
                      <el-icon><component :is="area.icon" /></el-icon>
                      <span>{{ area.label }}</span>
                      <el-tooltip :content="area.tip" placement="top">
                        <el-icon class="help-icon"><QuestionFilled /></el-icon>
                      </el-tooltip>
                    </div>
                    
                    <div class="area-content">
                      <TransitionGroup name="field-list">
                        <div 
                          v-for="(field, index) in getAreaFields(area.key)" 
                          :key="field.id"
                          class="field-item"
                        >
                          <div class="field-header">
                            <el-icon :style="{ color: getFieldColor(field.type) }">
                              <component :is="getFieldIcon(field.type)" />
                            </el-icon>
                            <span class="field-type-label">{{ getFieldTypeLabel(field.type) }}</span>
                            <el-button 
                              type="danger" 
                              :icon="Delete" 
                              circle 
                              size="small"
                              @click="removeField(area.key, index)"
                            />
                          </div>
                          
                          <el-input 
                            v-model="field.name" 
                            placeholder="输入字段名称"
                            size="default"
                          />
                          
                          <!-- 枚举选项 -->
                          <div v-if="field.type === 'enum'" class="enum-options">
                            <div class="enum-title">枚举选项</div>
                            <div 
                              v-for="(opt, optIndex) in field.enumOptions" 
                              :key="optIndex"
                              class="enum-item"
                            >
                              <span class="opt-label">{{ opt.label }}</span>
                              <el-input v-model="opt.value" size="small" placeholder="选项值" />
                              <el-button 
                                type="danger" 
                                :icon="Close" 
                                circle 
                                size="small"
                                @click="removeEnumOption(field, optIndex)"
                              />
                            </div>
                            <el-button 
                              type="primary" 
                              :icon="Plus" 
                              size="small" 
                              text
                              @click="addEnumOption(field)"
                            >
                              添加选项
                            </el-button>
                          </div>
                        </div>
                      </TransitionGroup>
                      
                      <div v-if="getAreaFields(area.key).length === 0" class="empty-area">
                        <el-icon :size="32"><Upload /></el-icon>
                        <p>拖拽字段到这里</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 步骤3: 预览确认 -->
          <div v-else-if="currentStep === 2" class="preview-section animate-scale-in">
            <div class="preview-card">
              <div class="preview-header">
                <h2>模版预览</h2>
                <p>请确认以下信息无误后提交</p>
              </div>
              
              <div class="preview-content">
                <div class="preview-block">
                  <h3>基本信息</h3>
                  <div class="info-list">
                    <div class="info-row">
                      <span class="label">模版名称</span>
                      <span class="value">{{ templateForm.name }}</span>
                    </div>
                    <div class="info-row">
                      <span class="label">所属目录</span>
                      <span class="value">{{ getTemplateCategoryPath() }}</span>
                    </div>
                    <div class="info-row">
                      <span class="label">模版说明</span>
                      <span class="value">{{ templateForm.description || '无' }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="preview-block">
                  <h3>字段配置</h3>
                  <div class="fields-summary">
                    <div 
                      v-for="area in designAreas" 
                      :key="area.key"
                      class="area-summary"
                    >
                      <div class="summary-header" :style="{ borderColor: area.color }">
                        <span>{{ area.label }}</span>
                        <el-tag size="small">{{ getAreaFields(area.key).length }} 个字段</el-tag>
                      </div>
                      <div class="summary-fields">
                        <el-tag 
                          v-for="field in getAreaFields(area.key)" 
                          :key="field.id"
                          type="info"
                          effect="plain"
                        >
                          {{ field.name || '未命名' }}
                        </el-tag>
                        <span v-if="getAreaFields(area.key).length === 0" class="no-fields">
                          暂无字段
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <!-- 底部操作栏 -->
      <div class="action-bar">
        <el-button 
          v-if="currentStep > 0" 
          size="large"
          @click="prevStep"
        >
          <el-icon><ArrowLeft /></el-icon>
          上一步
        </el-button>
        
        <el-button 
          v-if="currentStep < steps.length - 1"
          type="primary" 
          size="large"
          @click="nextStep"
        >
          下一步
          <el-icon><ArrowRight /></el-icon>
        </el-button>
        
        <el-button 
          v-if="currentStep === steps.length - 1"
          type="primary" 
          size="large"
          :loading="submitting"
          @click="submitTemplate"
        >
          <el-icon><Check /></el-icon>
          提交模版
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, markRaw, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Check, Setting, Grid, QuestionFilled, Delete, Close, Plus, Upload,
  ArrowLeft, ArrowRight, Document, Edit, DataLine, List, Calendar,
  PictureFilled, Box, Key
} from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'
import { useUserStore } from '@/stores/user'
import { getBigCategories, getSubCategories, getCategoryPath, findCategoryById, getNumericCategoryId } from '@/utils/templateCategories'

const router = useRouter()
const userStore = useUserStore()

// 步骤配置
const steps = [
  { title: '基础设置', desc: '设置模版基本信息' },
  { title: '模版结构设计', desc: '添加和配置字段' },
  { title: '预览确认', desc: '确认并提交' }
]

const currentStep = ref(0)
const submitting = ref(false)
const basicFormRef = ref(null)

// 表单数据
const templateForm = reactive({
  bigCategory: '',
  parent: '',
  name: '',
  description: ''
})

// 使用统一的分类配置
const bigCategories = getBigCategories()

// 动态获取子目录
const currentSubCategories = computed(() => {
  if (!templateForm.bigCategory) return []
  const category = findCategoryById(templateForm.bigCategory)
  if (category && !category.hasChildren) return []
  return getSubCategories(templateForm.bigCategory)
})

// 判断当前选中的大类是否有子目录
const hasSubCategories = computed(() => {
  if (!templateForm.bigCategory) return true
  const category = findCategoryById(templateForm.bigCategory)
  return category?.hasChildren !== false
})

// 动态验证规则
const basicRules = computed(() => ({
  bigCategory: [{ required: true, message: '请选择大目录', trigger: 'change' }],
  parent: hasSubCategories.value 
    ? [{ required: true, message: '请选择子目录', trigger: 'change' }]
    : [],
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }]
}))

const handleBigCategoryChange = () => {
  templateForm.parent = ''
}

// 字段类型
const fieldTypes = [
  { value: 'string', label: '字符串型', icon: markRaw(Document), color: '#667eea' },
  { value: 'number', label: '数值型', icon: markRaw(Key), color: '#10b981' },
  { value: 'float', label: '浮点型', icon: markRaw(DataLine), color: '#f59e0b' },
  { value: 'range', label: '范围型', icon: markRaw(Edit), color: '#06b6d4' },
  { value: 'enum', label: '枚举型', icon: markRaw(List), color: '#ec4899' },
  { value: 'image', label: '图片型', icon: markRaw(PictureFilled), color: '#f97316' },
  { value: 'file', label: '文件型', icon: markRaw(Document), color: '#64748b' },
  { value: 'array', label: '数组型', icon: markRaw(Grid), color: '#0ea5e9' },
  { value: 'table', label: '表格型', icon: markRaw(Grid), color: '#14b8a6' },
  { value: 'date', label: '日期型', icon: markRaw(Calendar), color: '#06b6d4' }
]

// 设计区域
const designAreas = [
  { 
    key: 'object', 
    label: '对象区域', 
    icon: markRaw(Box), 
    gradient: 'linear-gradient(135deg, #667eea, #764ba2)',
    color: '#667eea',
    tip: '用于描述实验对象的相关属性'
  },
  { 
    key: 'operation', 
    label: '操作区域', 
    icon: markRaw(Edit), 
    gradient: 'linear-gradient(135deg, #10b981, #34d399)',
    color: '#10b981',
    tip: '用于记录实验操作的相关参数'
  },
  { 
    key: 'result', 
    label: '结果区域', 
    icon: markRaw(DataLine), 
    gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)',
    color: '#f59e0b',
    tip: '用于存储实验结果数据'
  }
]

// 字段数据
const fields = reactive({
  object: [],
  operation: [],
  result: []
})

// 拖拽相关
const dragOverArea = ref('')
const dragType = ref(null)

const handleDragStart = (event, type) => {
  dragType.value = type
  event.dataTransfer.effectAllowed = 'copy'
}

const handleDragEnter = (area) => {
  dragOverArea.value = area
}

const handleDragLeave = () => {
  dragOverArea.value = ''
}

const handleDrop = (area) => {
  dragOverArea.value = ''
  if (dragType.value) {
    const newField = {
      id: Date.now() + Math.random(),
      type: dragType.value.value,
      name: '',
      enumOptions: dragType.value.value === 'enum' ? [{ label: 'A', value: '' }] : []
    }
    fields[area].push(newField)
    
    // 自动滚动到新添加的字段
    nextTick(() => {
      // 找到对应区域的容器
      const areaIndex = designAreas.findIndex(a => a.key === area)
      const allAreas = document.querySelectorAll('.design-area')
      const targetArea = allAreas[areaIndex]
      
      if (targetArea) {
        // 找到该区域内最后一个字段元素（新添加的字段）
        const fieldItems = targetArea.querySelectorAll('.field-item')
        const lastFieldItem = fieldItems[fieldItems.length - 1]
        
        if (lastFieldItem) {
          // 滚动到新添加的字段，使其在视口中可见，留一点空间在下面
          lastFieldItem.scrollIntoView({ behavior: 'smooth', block: 'center' })
          
          // 聚焦到新字段的输入框
          setTimeout(() => {
            const input = lastFieldItem.querySelector('input')
            if (input) {
              input.focus()
            }
          }, 300)
        } else {
          // 如果没有找到字段，滚动到区域本身
          targetArea.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }
    })
  }
  dragType.value = null
}

const getAreaFields = (area) => fields[area]

const removeField = (area, index) => {
  fields[area].splice(index, 1)
}

const addEnumOption = (field) => {
  // 使用 A、B、C、D... 作为标签
  const labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  const index = field.enumOptions.length
  const label = index < 26 ? labels[index] : `选项${index + 1}`
  field.enumOptions.push({ label, value: '' })
}

const removeEnumOption = (field, index) => {
  if (field.enumOptions.length > 1) {
    field.enumOptions.splice(index, 1)
  } else {
    ElMessage.warning('至少保留一个枚举选项')
  }
}

const getFieldIcon = (type) => {
  const found = fieldTypes.find(t => t.value === type)
  return found?.icon || Document
}

const getFieldColor = (type) => {
  const found = fieldTypes.find(t => t.value === type)
  return found?.color || '#667eea'
}

const getFieldTypeLabel = (type) => {
  const found = fieldTypes.find(t => t.value === type)
  return found?.label || type
}

// 字段类型到 fieldDataType 的映射 - 使用中文类型名
const fieldTypeToDataType = {
  'string': '字符串型',
  'number': '数值型',
  'float': '浮点型',
  'range': '范围型',
  'enum': '枚举型',
  'image': '图片型',
  'file': '文件型',
  'array': '数组型',
  'table': '表格型',
  'date': '日期型'
}

// 区域到 fieldCategory 的映射
// 根据后端 TemplateFieldCategoryConstant: 1=对象, 2=操作, 3=结果
const areaToFieldCategory = {
  'object': 1,
  'operation': 2,
  'result': 3
}

// 步骤控制
const nextStep = async () => {
  if (currentStep.value === 0) {
    if (!basicFormRef.value) return
    await basicFormRef.value.validate((valid) => {
      if (valid) {
        currentStep.value++
      }
    })
  } else {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const getTemplateCategoryPath = () => {
  if (hasSubCategories.value && templateForm.parent) {
    return getCategoryPath(templateForm.parent)
  }
  return getCategoryPath(templateForm.bigCategory)
}

const submitTemplate = async () => {
  const totalFields = fields.object.length + fields.operation.length + fields.result.length
  if (totalFields === 0) {
    ElMessage.warning('请至少添加一个字段')
    return
  }

  const allFields = [...fields.object, ...fields.operation, ...fields.result]
  for (const field of allFields) {
    if (!field.name) {
      ElMessage.error('请填写所有字段的名称')
      return
    }
    // 验证字段名不能是纯数字（会导致数据库SQL语法错误）
    if (/^\d+$/.test(field.name.trim())) {
      ElMessage.error(`字段名 "${field.name}" 不能是纯数字，请修改`)
      return
    }
  }

  submitting.value = true
  try {
    // 确定 categoryId - 优先使用子目录，如果没有子目录则使用大目录
    const categoryId = hasSubCategories.value && templateForm.parent 
      ? templateForm.parent 
      : templateForm.bigCategory
    
    // 将分类ID转换为数字ID
    const finalCategoryId = getNumericCategoryId(categoryId)
    
    if (finalCategoryId === 0) {
      ElMessage.error('无法确定分类ID，请重新选择分类')
      return
    }

    // 构建 templateFieldDtos 数组
    const templateFieldDtos = []
    
    // 处理字段的通用函数 - 枚举型按选项拆分生成多个字段
    const processField = (field, fieldCategory) => {
      if (field.type === 'enum' && field.enumOptions && field.enumOptions.length > 0) {
        // 枚举型：每个选项生成一个独立字段，格式为 "枚举名:选项值"
        field.enumOptions.forEach(opt => {
          if (opt.value) {
            templateFieldDtos.push({
              fieldName: `${field.name}:${opt.value}`,
              fieldCategory: fieldCategory,
              fieldDataType: '枚举型'
            })
          }
        })
      } else {
        // 非枚举型：正常处理
        templateFieldDtos.push({
          fieldName: field.name,
          fieldCategory: fieldCategory,
          fieldDataType: fieldTypeToDataType[field.type] ?? '字符串型'
        })
      }
    }
    
    // 处理对象区域字段
    fields.object.forEach(field => {
      processField(field, areaToFieldCategory.object)
    })
    
    // 处理操作区域字段
    fields.operation.forEach(field => {
      processField(field, areaToFieldCategory.operation)
    })
    
    // 处理结果区域字段
    fields.result.forEach(field => {
      processField(field, areaToFieldCategory.result)
    })

    // 构造请求数据
    const data = {
      name: templateForm.name,
      categoryId: finalCategoryId,
      description: templateForm.description || '',
      creator: userStore.userName || 'anonymous',
      templateFieldDtos: templateFieldDtos
    }
    
    console.log('提交模板数据:', data)
    
    const response = await request.post('/template/create', data)
    console.log('后端响应:', response.data)
    
    if (response.data?.code === 0 || response.data?.code === 1) {
      ElMessage.success('模版创建成功')
      router.push('/tplmanage/library')
    } else {
      ElMessage.error(response.data?.msg || response.data?.message || '创建失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(error.response?.data?.msg || error.message || '提交失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss" scoped>
.tpl-create {
  min-height: 100vh;
  background: #f5f7fa;
}

.page-container {
  padding-top: 64px;
  max-width: 1400px;
  margin: 0 auto;
  padding-left: 32px;
  padding-right: 32px;
  padding-bottom: 100px;
}

// 步骤导航
.steps-header {
  padding: 32px 0;
}

.steps-container {
  display: flex;
  justify-content: center;
  gap: 80px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 16px;
  
  &.completed .step-circle {
    background: #10b981;
  }
  
  &.active .step-circle {
    background: linear-gradient(135deg, #667eea, #764ba2);
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  }
  
  &.active .step-title {
    color: #667eea;
  }
}

.step-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 1.125rem;
  transition: all 0.3s ease;
}

.step-info {
  display: flex;
  flex-direction: column;
}

.step-title {
  font-weight: 600;
  color: #1e293b;
}

.step-desc {
  font-size: 0.875rem;
  color: #64748b;
}

// 表单区域
.section-card {
  background: white;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f1f5f9;
}

.header-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-info h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.header-info p {
  color: #64748b;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

// 设计区域
.design-layout {
  display: flex;
  gap: 24px;
}

.toolbar-sidebar {
  width: 200px;
  flex-shrink: 0;
}

.toolbar-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  position: sticky;
  top: 80px;
}

.toolbar-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.field-types {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-type-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
  cursor: grab;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  
  &:hover {
    background: #f1f5f9;
    transform: translateX(4px);
  }
  
  &:active {
    cursor: grabbing;
  }
}

.design-main {
  flex: 1;
}

.design-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.design-area {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  min-height: 300px;
  transition: box-shadow 0.3s ease;
  
  &.drag-over {
    box-shadow: 0 0 0 3px #667eea40;
  }
}

.area-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-weight: 600;
}

.help-icon {
  margin-left: auto;
  opacity: 0.8;
  cursor: help;
}

.area-content {
  padding: 16px;
  min-height: 240px;
}

.field-item {
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}

.field-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.field-type-label {
  flex: 1;
  font-size: 0.8125rem;
  color: #64748b;
}

.enum-options {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #e2e8f0;
}

.enum-title {
  font-size: 0.8125rem;
  color: #64748b;
  margin-bottom: 8px;
}

.enum-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.opt-label {
  font-size: 0.8125rem;
  color: #94a3b8;
  min-width: 50px;
}

.empty-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #94a3b8;
  
  p {
    margin-top: 8px;
    font-size: 0.875rem;
  }
}

// 预览区域
.preview-card {
  background: white;
  border-radius: 20px;
  padding: 32px;
}

.preview-header {
  text-align: center;
  margin-bottom: 32px;
  
  h2 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 8px;
  }
  
  p {
    color: #64748b;
  }
}

.preview-block {
  margin-bottom: 32px;
  
  h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f1f5f9;
  }
}

.info-list {
  display: grid;
  gap: 16px;
}

.info-row {
  display: flex;
  
  .label {
    width: 120px;
    color: #64748b;
    flex-shrink: 0;
  }
  
  .value {
    color: #1e293b;
    font-weight: 500;
  }
}

.fields-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.area-summary {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 2px solid;
  font-weight: 600;
  color: #1e293b;
}

.summary-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.no-fields {
  color: #94a3b8;
  font-size: 0.875rem;
}

// 底部操作栏
.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 16px 32px;
  display: flex;
  justify-content: center;
  gap: 16px;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.08);
  z-index: 100;
}

// 动画
.animate-slide-up {
  animation: slideUp 0.5s ease-out;
}

.animate-scale-in {
  animation: scaleIn 0.4s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.field-list-enter-active {
  transition: all 0.3s ease;
}

.field-list-leave-active {
  transition: all 0.2s ease;
}

.field-list-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.field-list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

// 响应式
@media (max-width: 1024px) {
  .design-grid {
    grid-template-columns: 1fr;
  }
  
  .design-layout {
    flex-direction: column;
  }
  
  .toolbar-sidebar {
    width: 100%;
  }
  
  .toolbar-card {
    position: static;
  }
  
  .field-types {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .fields-summary {
    grid-template-columns: 1fr;
  }
}
</style>
