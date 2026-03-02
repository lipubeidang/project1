<template>
  <div class="data-entry">
    <Navbar />
    
    <div class="page-container">
      <!-- 页面头部 -->
      <div class="page-header animate-slide-up">
        <div class="header-content">
          <el-button :icon="ArrowLeft" text @click="goBack">返回</el-button>
          <div class="header-info">
            <h1 class="page-title">在线填写数据</h1>
            <span class="template-name">{{ templateName }}</span>
          </div>
        </div>
        <div class="header-actions">
          <el-button @click="resetForm">重置</el-button>
          <el-button type="primary" :icon="Check" :loading="submitting" @click="submitData">
            提交数据
          </el-button>
        </div>
      </div>

      <!-- 表单内容 -->
      <div class="content-wrapper" v-loading="loading">
        <!-- 对象区域 -->
        <div class="form-section animate-slide-up delay-1" v-if="objectFields.length > 0">
          <div class="section-header">
            <div class="section-icon" style="background: linear-gradient(135deg, #667eea, #764ba2)">
              <el-icon><Box /></el-icon>
            </div>
            <div class="section-info">
              <h3>对象区域</h3>
              <p>填写样本基本信息</p>
            </div>
          </div>
          
          <el-form :model="objectForm" label-width="160px" class="data-form">
            <el-row :gutter="24">
              <el-col :span="12" v-for="field in objectFields" :key="field.columnName">
                <el-form-item :label="field.displayName || field.columnName">
                  <el-select 
                    v-if="field.isEnum" 
                    v-model="objectForm[field.columnName]"
                    :placeholder="`请选择${field.displayName || field.columnName}`"
                    style="width: 100%"
                    filterable
                    clearable
                  >
                    <el-option 
                      v-for="opt in field.enumOptions" 
                      :key="opt.value" 
                      :label="opt.value ? `${opt.label}: ${opt.value}` : opt.label" 
                      :value="opt.value || opt.label"
                    />
                  </el-select>
                  <el-input-number 
                    v-else-if="field.columnContribution === '数值型' || field.columnContribution === 'number' || field.columnContribution === '整数'" 
                    v-model="objectForm[field.columnName]"
                    style="width: 100%"
                    controls-position="right"
                  />
                  <el-input 
                    v-else 
                    v-model="objectForm[field.columnName]"
                    :placeholder="`请输入${field.displayName || field.columnName}`"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <!-- 操作区域 -->
        <div class="form-section animate-slide-up delay-2" v-if="operationFields.length > 0">
          <div class="section-header">
            <div class="section-icon" style="background: linear-gradient(135deg, #10b981, #34d399)">
              <el-icon><Setting /></el-icon>
            </div>
            <div class="section-info">
              <h3>操作区域</h3>
              <p>填写测试方法和操作参数</p>
            </div>
          </div>
          
          <el-form :model="operationForm" label-width="160px" class="data-form">
            <el-row :gutter="24">
              <el-col :span="12" v-for="field in operationFields" :key="field.columnName">
                <el-form-item :label="field.displayName || field.columnName">
                  <el-select 
                    v-if="field.isEnum" 
                    v-model="operationForm[field.columnName]"
                    :placeholder="`请选择${field.displayName || field.columnName}`"
                    style="width: 100%"
                    filterable
                    clearable
                  >
                    <el-option 
                      v-for="opt in field.enumOptions" 
                      :key="opt.value" 
                      :label="opt.value ? `${opt.label}: ${opt.value}` : opt.label" 
                      :value="opt.value || opt.label"
                    />
                  </el-select>
                  <el-input-number 
                    v-else-if="field.columnContribution === '数值型' || field.columnContribution === 'number' || field.columnContribution === '整数'" 
                    v-model="operationForm[field.columnName]"
                    style="width: 100%"
                    controls-position="right"
                  />
                  <el-input 
                    v-else 
                    v-model="operationForm[field.columnName]"
                    :placeholder="`请输入${field.displayName || field.columnName}`"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <!-- 结果区域 -->
        <div class="form-section animate-slide-up delay-3" v-if="resultFields.length > 0">
          <div class="section-header">
            <div class="section-icon" style="background: linear-gradient(135deg, #f59e0b, #fbbf24)">
              <el-icon><DataLine /></el-icon>
            </div>
            <div class="section-info">
              <h3>结果区域</h3>
              <p>填写测试结果数据</p>
            </div>
          </div>
          
          <el-form :model="resultForm" label-width="160px" class="data-form">
            <el-row :gutter="24">
              <el-col :span="12" v-for="field in resultFields" :key="field.columnName">
                <el-form-item :label="field.displayName || field.columnName">
                  <el-select 
                    v-if="field.isEnum" 
                    v-model="resultForm[field.columnName]"
                    :placeholder="`请选择${field.displayName || field.columnName}`"
                    style="width: 100%"
                    filterable
                    clearable
                  >
                    <el-option 
                      v-for="opt in field.enumOptions" 
                      :key="opt.value" 
                      :label="opt.value ? `${opt.label}: ${opt.value}` : opt.label" 
                      :value="opt.value || opt.label"
                    />
                  </el-select>
                  <el-input-number 
                    v-else-if="field.columnContribution === '数值型' || field.columnContribution === 'number' || field.columnContribution === '整数'" 
                    v-model="resultForm[field.columnName]"
                    style="width: 100%"
                    controls-position="right"
                  />
                  <el-input 
                    v-else 
                    v-model="resultForm[field.columnName]"
                    :placeholder="`请输入${field.displayName || field.columnName}`"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
        
        <!-- 无字段提示 -->
        <el-empty 
          v-if="!loading && objectFields.length === 0 && operationFields.length === 0 && resultFields.length === 0"
          description="未获取到模板字段信息"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Check, Box, Setting, DataLine } from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()

const moduleId = ref('')
const templateName = ref('')
const loading = ref(false)
const submitting = ref(false)

// 表单数据
const objectForm = reactive({})
const operationForm = reactive({})
const resultForm = reactive({})

// 字段配置 - 从API获取
const objectFields = ref([])
const operationFields = ref([])
const resultFields = ref([])


// 加载模板字段信息
const loadColumnInfo = async () => {
  if (!moduleId.value) {
    ElMessage.warning('缺少模板ID参数')
    return
  }

  loading.value = true
  try {
    console.log('========== 开始加载字段信息 ==========')
    console.log('📋 模板ID:', moduleId.value)
    console.log('📝 传入的模板名称:', templateName.value)
    
    // 获取字段信息
    let columnInfo = {}
    let backendTemplateName = ''
    
    try {
      const response = await request.get(`/basemodule/moduledata/getColumnInfo/${moduleId.value}`)
      console.log('📥 后端返回的字段信息:', response.data)
      
      if (response.data?.code === 0) {
        columnInfo = response.data.columnInfo || response.data.data || {}
        backendTemplateName = response.data.templateName || 
                            response.data.name || 
                            response.data.moduleName || ''
        
        if (response.data.templateName) {
          templateName.value = response.data.templateName
        }
      }
    } catch (columnError) {
      console.warn('⚠️ 获取字段信息失败:', columnError)
      if (columnError.response?.status === 404) {
        console.warn('接口可能不存在，将使用空字段信息继续流程')
      }
    }
    
    // 处理各区域字段
    if (columnInfo.object && Array.isArray(columnInfo.object)) {
      objectFields.value = processFieldsWithEnum(columnInfo.object, 'object')
      objectFields.value.forEach(f => {
        objectForm[f.columnName] = ''
      })
    }
    
    if (columnInfo.operation && Array.isArray(columnInfo.operation)) {
      operationFields.value = processFieldsWithEnum(columnInfo.operation, 'operation')
      operationFields.value.forEach(f => {
        operationForm[f.columnName] = ''
      })
    }
    
    if (columnInfo.result && Array.isArray(columnInfo.result)) {
      resultFields.value = processFieldsWithEnum(columnInfo.result, 'result')
      resultFields.value.forEach(f => {
        resultForm[f.columnName] = ''
      })
    }
    
  } catch (error) {
    console.error('加载数据时发生未知错误:', error)
    ElMessage.warning('加载数据时出现问题，部分功能可能不可用')
  } finally {
    loading.value = false
  }
}

// 处理字段
const processFieldsWithEnum = (fields, section) => {
  return fields.map((field, index) => {
    const columnName = field.columnName || field.column_name || field.fieldName || field.name || ''
    const contribution = field.columnContribution || field.column_contribution || field.contribution || field.type || ''
    const displayName = field.displayName || field.display_name || columnName
    
    let enumOptions = []
    // 同时支持 'enum'（字段类型值）和 '枚举型'（字段类型标签）和 '枚举' 三种判断
    const isEnum = contribution === '枚举型' || contribution === '枚举' || contribution === 'enum'
    
    if (isEnum) {
      // 使用字段中已有的枚举选项，如果没有则使用默认值
      enumOptions = field.enumOptions || [
        { label: '选项1', value: '选项1' },
        { label: '选项2', value: '选项2' }
      ]
    }
    
    return {
      columnName,
      displayName: contribution ? `${displayName} (${contribution})` : displayName,
      columnContribution: contribution,
      isEnum,
      enumOptions
    }
  })
}

// 返回
const goBack = () => {
  router.push('/template/upload')
}

// 重置表单
const resetForm = () => {
  objectFields.value.forEach(f => objectForm[f.columnName] = '')
  operationFields.value.forEach(f => operationForm[f.columnName] = '')
  resultFields.value.forEach(f => resultForm[f.columnName] = '')
}

// 构建提交数据结构
const buildSubmitData = () => {
  const object = {}
  const operation = {}
  const result = {}
  
  objectFields.value.forEach(f => {
    if (objectForm[f.columnName] !== '' && objectForm[f.columnName] !== null) {
      object[f.columnName] = objectForm[f.columnName]
    }
  })
  
  operationFields.value.forEach(f => {
    if (operationForm[f.columnName] !== '' && operationForm[f.columnName] !== null) {
      operation[f.columnName] = operationForm[f.columnName]
    }
  })
  
  resultFields.value.forEach(f => {
    if (resultForm[f.columnName] !== '' && resultForm[f.columnName] !== null) {
      result[f.columnName] = resultForm[f.columnName]
    }
  })
  
  return {
    module_id: moduleId.value,
    sample_serial: objectForm.sample_serial || objectForm.sampleSerial || `SAMPLE_${Date.now()}`,
    object,
    operation,
    result
  }
}

// 提交数据
const submitData = async () => {
  const hasObjectData = Object.keys(objectForm).some(k => objectForm[k])
  const hasOperationData = Object.keys(operationForm).some(k => operationForm[k])
  const hasResultData = Object.keys(resultForm).some(k => resultForm[k])
  
  if (!hasObjectData && !hasOperationData && !hasResultData) {
    ElMessage.warning('请至少填写一项数据')
    return
  }

  submitting.value = true

  try {
    const data = buildSubmitData()
    const response = await request.post('/basemodule/moduledata/insertsingle', data)
    
    if (response.data?.code === 0) {
      ElMessage.success('数据提交成功！')
      resetForm()
    } else {
      throw new Error(response.data?.msg || '提交失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  moduleId.value = route.params.moduleId || ''
  templateName.value = route.query.templateName || route.query.name || '数据模板'
  
  // 加载模板字段
  loadColumnInfo()
})
</script>

<style lang="scss" scoped>
.data-entry {
  min-height: 100vh;
  background: #f1f5f9;
}

.page-container {
  padding-top: 72px;
  min-height: 100vh;
}

// 页面头部
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 32px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-info {
  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 4px;
  }
  
  .template-name {
    font-size: 14px;
    color: #64748b;
  }
}

.header-actions {
  display: flex;
  gap: 12px;
}

// 内容区域
.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px;
}

// 表单区块
.form-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.section-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  
  .el-icon {
    font-size: 24px;
  }
}

.section-info {
  h3 {
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 4px;
  }
  
  p {
    font-size: 14px;
    color: #64748b;
  }
}

.data-form {
  :deep(.el-form-item) {
    margin-bottom: 24px;
  }
  
  :deep(.el-form-item__label) {
    font-weight: 500;
    color: #475569;
  }
}

// 动画
.animate-slide-up {
  animation: slideUp 0.5s ease forwards;
}

.delay-1 { animation-delay: 0.1s; opacity: 0; }
.delay-2 { animation-delay: 0.2s; opacity: 0; }
.delay-3 { animation-delay: 0.3s; opacity: 0; }

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
</style>
