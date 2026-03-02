<template>
  <div class="template-create">
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
                  <p>设置数据资源的基本信息和分类</p>
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
                  <el-form-item label="数据资源目录" prop="bigCategory">
                    <el-select 
                      v-model="templateForm.bigCategory" 
                      placeholder="请选择资源目录"
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

                  <el-form-item label="数据子目录" prop="parent">
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
                </div>

                <el-form-item label="数据资源名称" prop="name">
                  <el-input 
                    v-model="templateForm.name" 
                    placeholder="请输入数据资源名称"
                    size="large"
                  />
                </el-form-item>

                <el-form-item label="数据资源说明" prop="description">
                  <el-input
                    v-model="templateForm.description"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入数据资源说明，帮助其他用户了解此数据资源的用途"
                    resize="none"
                  />
                </el-form-item>
              </el-form>
            </div>
          </div>

          <!-- 步骤2: 模板设计 -->
          <div v-else-if="currentStep === 1" class="design-section animate-scale-in">
            <div class="design-layout">
              <!-- 左侧字段类型工具栏 - 固定 -->
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
                <h2>数据资源预览</h2>
                <p>请确认以下信息无误后提交</p>
              </div>
              
              <div class="preview-content">
                <div class="preview-block">
                  <h3>基本信息</h3>
                  <div class="info-list">
                    <div class="info-row">
                      <span class="label">数据资源名称</span>
                      <span class="value">{{ templateForm.name }}</span>
                    </div>
                    <div class="info-row">
                      <span class="label">所属目录</span>
                      <span class="value">{{ getCategoryPath() }}</span>
                    </div>
                    <div class="info-row">
                      <span class="label">数据资源说明</span>
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
          提交数据资源
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, markRaw } from 'vue'
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


const router = useRouter()
const userStore = useUserStore()

// 步骤配置
const steps = [
  { title: '基础设置', desc: '设置数据资源基本信息' },
  { title: '数据结构设计', desc: '添加和配置字段' },
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

const basicRules = {
  bigCategory: [{ required: true, message: '请选择大目录', trigger: 'change' }],
  parent: [{ required: true, message: '请选择子目录', trigger: 'change' }],
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }]
}

// 大目录数据
const bigCategories = [
  { id: 'big_cat_1', name: '材料属性' },
  { id: 'big_cat_2', name: '数据来源' },
  { id: 'big_cat_3', name: '材料功能' }
]

// 子目录数据（与模板库保持一致）
const subCategories = {
  big_cat_1: [
    { id: 1, name: '医用金属材料' },
    { id: 2, name: '医用无机材料' },
    { id: 3, name: '医用高分子材料' },
    { id: 4, name: '生物复合材料' },
    { id: 5, name: '生物衍生材料' },
    { id: 6, name: '医用纳米材料' },
    { id: 7, name: '组织诱导性生物材料' },
    { id: 8, name: '组织工程材料' },
    { id: 9, name: '生物传感器材料' },
    { id: 10, name: '其他材料属性' }
  ],
  big_cat_2: [
    { id: 11, name: '文献' },
    { id: 12, name: '计算' },
    { id: 13, name: '实验' },
    { id: 14, name: '研发生产' },
    { id: 15, name: '临床应用' },
    { id: 16, name: '其他数据来源' }
  ],
  big_cat_3: [
    { id: 17, name: '骨科材料' },
    { id: 18, name: '心血管材料' },
    { id: 19, name: '牙科材料' },
    { id: 20, name: '其他材料功能' }
  ]
}

const currentSubCategories = computed(() => {
  return subCategories[templateForm.bigCategory] || []
})

const handleBigCategoryChange = () => {
  templateForm.parent = ''
}

// 字段类型 - 与原项目保持一致
const fieldTypes = [
  { value: 'string', label: '字符串型', icon: markRaw(Document), color: '#667eea' },
  { value: 'number', label: '数值型', icon: markRaw(Key), color: '#10b981' },
  { value: 'float', label: '浮点型', icon: markRaw(DataLine), color: '#f59e0b' },
  { value: 'range', label: '范围型', icon: markRaw(Edit), color: '#06b6d4' },
  { value: 'select', label: '候选型', icon: markRaw(List), color: '#8b5cf6' },
  { value: 'enum', label: '枚举型', icon: markRaw(List), color: '#ec4899' },
  { value: 'image', label: '图片型', icon: markRaw(PictureFilled), color: '#f97316' },
  { value: 'file', label: '文件型', icon: markRaw(Document), color: '#64748b' },
  { value: 'array', label: '数组型', icon: markRaw(Grid), color: '#0ea5e9' },
  { value: 'table', label: '表格型', icon: markRaw(Grid), color: '#14b8a6' },
  { value: 'container', label: '容器型', icon: markRaw(Box), color: '#a855f7' },
  { value: 'generator', label: '生成器型', icon: markRaw(Setting), color: '#f43f5e' },
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
    tip: '用于记录实验结果的相关数据'
  }
]

// 字段数据
const fields = reactive({
  object: [],
  operation: [],
  result: []
})

let fieldIdCounter = 0

// 拖拽相关
const dragOverArea = ref(null)
const currentDragType = ref(null)

const handleDragStart = (event, type) => {
  currentDragType.value = type
  event.dataTransfer.effectAllowed = 'copy'
}

const handleDragEnter = (area) => {
  dragOverArea.value = area
}

const handleDragLeave = () => {
  dragOverArea.value = null
}

const handleDrop = (area) => {
  if (currentDragType.value) {
    const newField = {
      id: `field_${++fieldIdCounter}`,
      type: currentDragType.value.value,
      name: '',
      enumOptions: currentDragType.value.value === 'enum' ? [{ label: 'A', value: '' }] : undefined
    }
    fields[area].push(newField)
    ElMessage.success(`已添加${currentDragType.value.label}字段`)
  }
  dragOverArea.value = null
  currentDragType.value = null
}

const getAreaFields = (area) => fields[area]

const removeField = (area, index) => {
  fields[area].splice(index, 1)
}

const addEnumOption = (field) => {
  if (!field.enumOptions) field.enumOptions = []
  const labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
  const nextLabel = labels[field.enumOptions.length] || `选项${field.enumOptions.length + 1}`
  field.enumOptions.push({ label: nextLabel, value: '' })
}

const removeEnumOption = (field, index) => {
  if (field.enumOptions && field.enumOptions.length > 1) {
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

const getCategoryPath = () => {
  const bigCat = bigCategories.find(c => c.id === templateForm.bigCategory)
  const bigName = bigCat?.name || ''
  const subCat = currentSubCategories.value.find(s => s.id === templateForm.parent)
  return subCat ? `${bigName} / ${subCat.name}` : bigName
}

const submitTemplate = async () => {
  // 验证是否有字段
  const totalFields = fields.object.length + fields.operation.length + fields.result.length
  if (totalFields === 0) {
    ElMessage.warning('请至少添加一个字段')
    return
  }

  // 验证所有字段都有名称
  const allFields = [...fields.object, ...fields.operation, ...fields.result]
  for (const field of allFields) {
    if (!field.name) {
      ElMessage.error('请填写所有字段的名称')
      return
    }
    // 设置 contribution 为字段类型的标签
    const fieldType = fieldTypes.find(t => t.value === field.type)
    field.contribution = fieldType ? fieldType.label : field.type
    
    // 🔍 调试：打印枚举字段信息
    if (field.type === 'enum') {
      console.log(`枚举字段 "${field.name}":`, field.enumOptions)
    }
  }

  submitting.value = true
  try {
    console.log('========== 准备提交模板 ==========')
    console.log('对象区域字段:', JSON.parse(JSON.stringify(fields.object)))
    console.log('操作区域字段:', JSON.parse(JSON.stringify(fields.operation)))
    console.log('结果区域字段:', JSON.parse(JSON.stringify(fields.result)))

    // 构造提交数据
    const mapField = (field) => ({
      columnName: field.name,
      columnContribution: field.contribution,
      columnType: field.type
    })

    const templateData = {
      name: templateForm.name,
      description: templateForm.description,
      creator: userStore.userName || 'anonymous',
      parent: templateForm.parent,
      columns: {
        object: fields.object.map(mapField),
        operation: fields.operation.map(mapField),
        result: fields.result.map(mapField)
      }
    }

    console.log('📤 提交模板数据:', templateData)
    
    // 第一步：提交模板数据到后端
    const response = await request.post('/basemodule/module/create', templateData)
    console.log('📥 后端响应:', response.data)
    
    if (response.data?.code === 0) {
      const templateName = templateForm.name
      console.log('✅ 模板创建成功')
      console.log('📝 模板名称:', templateName)
      
      // 获取模板ID
      const moduleId = response.data.moduleId || 
                      response.data.id || 
                      response.data.data?.moduleId ||
                      response.data.data?.id
      console.log('🆔 模板ID:', moduleId)
      
      ElMessage.success(`模板"${templateName}"创建成功！`)
      router.push('/template/library')
    } else {
      throw new Error(response.data?.msg || '创建失败')
    }
  } catch (error) {
    console.error('创建模板失败:', error)
    ElMessage.error(error.message || '创建模板失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss" scoped>
.template-create {
  min-height: 100vh;
  background: #f1f5f9;
}

.page-container {
  padding-top: 72px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

// 步骤头部
.steps-header {
  background: white;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.steps-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 24px;
    left: 60px;
    right: 60px;
    height: 2px;
    background: #e2e8f0;
  }
}

.step-item {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  z-index: 1;
  
  &.active .step-circle {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    transform: scale(1.1);
  }
  
  &.completed .step-circle {
    background: #10b981;
    color: white;
  }
  
  &.active .step-title {
    color: #667eea;
  }
}

.step-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: white;
  border: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.125rem;
  color: #94a3b8;
  transition: all 0.3s ease;
}

.step-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.step-title {
  font-weight: 600;
  color: #1e293b;
  transition: color 0.3s ease;
}

.step-desc {
  font-size: 0.875rem;
  color: #94a3b8;
}

// 步骤内容
.step-content {
  flex: 1;
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

// 基础设置
.section-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 40px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f1f5f9;
}

.header-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-info {
  h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 4px;
  }
  
  p {
    color: #64748b;
  }
}

.template-form {
  max-width: 600px;
  
  :deep(.el-form-item__label) {
    font-weight: 500;
    color: #334155;
  }
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

// 模板设计
.design-section {
  width: 100%;
}

.design-layout {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

// 左侧工具栏 - 固定定位
.toolbar-sidebar {
  width: 200px;
  flex-shrink: 0;
  position: sticky;
  top: 100px;
  align-self: flex-start;
}

.toolbar-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
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
  gap: 10px;
}

.field-type-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  cursor: grab;
  transition: all 0.3s ease;
  user-select: none;
  
  &:hover {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2);
  }
  
  &:active {
    cursor: grabbing;
    transform: scale(0.98);
  }
  
  span {
    font-size: 0.875rem;
    color: #475569;
  }
}

// 右侧设计主区域
.design-main {
  flex: 1;
  min-width: 0;
}

.design-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.design-area {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  
  &.drag-over {
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
    transform: scale(1.02);
  }
}

.area-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  color: white;
  font-weight: 600;
  
  .help-icon {
    margin-left: auto;
    opacity: 0.8;
    cursor: help;
  }
}

.area-content {
  padding: 20px;
  min-height: 150px;
}

.field-item {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  }
}

.field-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.field-type-label {
  flex: 1;
  font-size: 0.875rem;
  color: #64748b;
}

.enum-options {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #e2e8f0;
}

.enum-title {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.enum-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  
  .opt-label {
    font-size: 0.75rem;
    color: #94a3b8;
    min-width: 50px;
  }
  
  .el-input {
    flex: 1;
  }
}

.empty-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #94a3b8;
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  transition: all 0.3s ease;
  
  p {
    margin-top: 12px;
    font-size: 0.875rem;
  }
  
  .drag-over & {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.05);
    color: #667eea;
  }
}

// 预览确认
.preview-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.preview-header {
  text-align: center;
  margin-bottom: 40px;
  
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
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid #f1f5f9;
  }
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  
  .label {
    width: 100px;
    flex-shrink: 0;
    color: #64748b;
    font-size: 0.875rem;
  }
  
  .value {
    flex: 1;
    color: #1e293b;
    font-weight: 500;
  }
}

.fields-summary {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.area-summary {
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border-left: 4px solid;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  
  span {
    font-weight: 600;
    color: #1e293b;
  }
}

.summary-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.no-fields {
  font-size: 0.875rem;
  color: #94a3b8;
}

// 操作栏
.action-bar {
  background: white;
  padding: 20px 32px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: center;
  gap: 16px;
  
  .el-button {
    min-width: 140px;
  }
}

// 字段列表动画
.field-list-enter-active,
.field-list-leave-active {
  transition: all 0.3s ease;
}

.field-list-enter-from,
.field-list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

// 响应式
@media (max-width: 1024px) {
  .design-grid {
    grid-template-columns: 1fr;
  }
  
  .steps-container {
    flex-direction: column;
    gap: 24px;
    
    &::before {
      display: none;
    }
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .step-content {
    padding: 20px;
  }
  
  .section-card,
  .preview-card {
    padding: 24px;
  }
}
</style>
