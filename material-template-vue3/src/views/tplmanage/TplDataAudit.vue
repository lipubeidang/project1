<template>
  <div class="tpl-data-audit">
    <Navbar />
    
    <div class="page-container">
      <!-- 侧边栏 - 模板分类 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="sidebar-title-wrap">
            <el-icon class="sidebar-icon"><DataBoard /></el-icon>
            <h3>模板分类</h3>
          </div>
        </div>
        <div class="sidebar-content">
          <el-tree
            ref="treeRef"
            :data="categoryTree"
            :props="{ children: 'children', label: 'name' }"
            node-key="id"
            :default-expanded-keys="defaultExpandedKeys"
            highlight-current
            @node-click="handleCategoryClick"
            class="category-tree"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <el-icon v-if="data.children"><Folder /></el-icon>
                <el-icon v-else><Document /></el-icon>
                <span class="node-label">{{ node.label }}</span>
              </div>
            </template>
          </el-tree>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="main-content">
        <!-- 页面头部 banner -->
        <div class="page-banner animate-slide-up">
          <div class="banner-bg">
            <div class="banner-pattern"></div>
          </div>
          <div class="banner-content">
            <div class="banner-icon">
              <el-icon :size="36"><DataAnalysis /></el-icon>
            </div>
            <div class="banner-info">
              <h1 class="page-title">数据审核</h1>
              <p class="page-desc" v-if="selectedTemplate">
                当前模板：{{ selectedTemplate.name }}
              </p>
              <p class="page-desc" v-else-if="currentCategory">
                当前目录：{{ currentCategory.name }} - 请选择模板
              </p>
              <p class="page-desc" v-else>审核员专属功能，审核模板数据上传</p>
            </div>
            <div class="banner-badge">
              <el-tag type="danger" effect="dark" size="large">
                <el-icon><User /></el-icon>
                审核员专用
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 步骤导航 -->
        <div class="steps-nav animate-slide-up delay-1">
          <div class="step" :class="{ active: step >= 1, done: step > 1 }">
            <div class="step-number">1</div>
            <span class="step-label">选择分类</span>
          </div>
          <div class="step-line" :class="{ active: step > 1 }"></div>
          <div class="step" :class="{ active: step >= 2, done: step > 2 }">
            <div class="step-number">2</div>
            <span class="step-label">选择模板</span>
          </div>
          <div class="step-line" :class="{ active: step > 2 }"></div>
          <div class="step" :class="{ active: step >= 3 }">
            <div class="step-number">3</div>
            <span class="step-label">审核数据</span>
          </div>
        </div>

        <!-- 模板选择区域 (step 2) -->
        <div class="template-section animate-slide-up delay-2" v-if="step === 2" v-loading="loadingTemplates">
          <div class="section-header">
            <h3><el-icon><Files /></el-icon> 选择模板</h3>
            <el-button text @click="step = 1; currentCategory = null; templates = []">
              <el-icon><ArrowLeft /></el-icon> 返回选择分类
            </el-button>
          </div>
          
          <div class="templates-grid" v-if="templates.length > 0">
            <div 
              v-for="template in templates" 
              :key="template.id"
              class="template-card"
              :class="{ selected: selectedTemplate?.id === template.id }"
              @click="selectTemplate(template)"
            >
              <div class="card-icon">
                <el-icon :size="28"><Document /></el-icon>
              </div>
              <div class="card-info">
                <h4>{{ template.name }}</h4>
                <p>{{ template.description || '暂无描述' }}</p>
              </div>
              <div class="card-meta">
                <span class="creator">
                  <el-icon><User /></el-icon>
                  {{ template.creator || '未知' }}
                </span>
              </div>
            </div>
          </div>
          <el-empty v-else description="该分类下暂无模板" :image-size="120" />
        </div>

        <!-- 数据审核区域 (step 3) -->
        <div class="data-section animate-slide-up delay-2" v-if="step === 3" v-loading="loadingData">
          <div class="section-header">
            <h3><el-icon><DataBoard /></el-icon> 待审核数据</h3>
            <div class="header-actions">
              <el-tag type="info" size="large">共 {{ pendingData.length }} 条待审核</el-tag>
              <el-button text @click="goBackToTemplates">
                <el-icon><ArrowLeft /></el-icon> 返回选择模板
              </el-button>
            </div>
          </div>

          <!-- 数据卡片列表 -->
          <div class="data-cards" v-if="pendingData.length > 0">
            <div 
              v-for="(item, index) in pendingData" 
              :key="item.id"
              class="data-card"
              :style="{ animationDelay: `${index * 0.05}s` }"
            >
              <div class="card-header">
                <div class="card-id">
                  <el-tag type="primary" effect="plain"># {{ item.id }}</el-tag>
                  <el-tag v-if="item.status === 0" type="warning" effect="light">待审核</el-tag>
                </div>
              </div>

              <div class="card-body">
                <!-- 按分类展示字段：对象区域、操作区域、结果区域 -->
                <template v-for="(categoryData, categoryName) in getFieldsByCategory(item)" :key="categoryName">
                  <div v-if="categoryData.length > 0" class="field-category-section">
                    <div class="category-header">
                      <el-tag 
                        :type="categoryName === 'object' ? 'primary' : categoryName === 'operation' ? 'warning' : 'success'"
                        effect="dark"
                        size="large"
                      >
                        {{ categoryName === 'object' ? '对象区域' : categoryName === 'operation' ? '操作区域' : '结果区域' }}
                      </el-tag>
                    </div>
                    <div class="fields-grid">
                      <template v-for="field in categoryData" :key="field.name">
                        <div class="field-item" :class="{ 'file-field': isFileField(field.name, field.value) }">
                          <label class="field-label">{{ field.name }}</label>
                          
                          <!-- 文件类型 - 图片 -->
                          <div v-if="isFileField(field.name, field.value) && isImageField(field.name)" class="field-value file-value image-field">
                            <!-- 图片缩略图预览 -->
                            <div class="thumbnail-wrapper" @click="previewFile(field.value, field.name)">
                              <el-image 
                                v-if="getThumbnailUrl(field.value)"
                                :src="getThumbnailUrl(field.value)" 
                                fit="cover"
                                class="thumbnail-image"
                              >
                                <template #error>
                                  <div class="thumbnail-error">
                                    <el-icon><Picture /></el-icon>
                                  </div>
                                </template>
                              </el-image>
                              <div v-else class="thumbnail-loading">
                                <el-icon class="is-loading"><Loading /></el-icon>
                              </div>
                            </div>
                            <div class="file-actions">
                              <el-button type="primary" size="small" @click="previewFile(field.value, field.name)">
                                <el-icon><ZoomIn /></el-icon> 预览
                              </el-button>
                              <el-button type="info" size="small" plain @click="downloadFile(field.value)">
                                <el-icon><Download /></el-icon> 下载
                              </el-button>
                            </div>
                          </div>
                          
                          <!-- 文件类型 - 非图片 -->
                          <div v-else-if="isFileField(field.name, field.value)" class="field-value file-value">
                            <div class="file-icon-wrapper">
                              <el-icon :size="24"><Document /></el-icon>
                              <span class="file-id">{{ field.value.substring(0, 8) }}...</span>
                            </div>
                            <div class="file-actions">
                              <el-button 
                                type="primary" 
                                size="small" 
                                @click="previewFile(field.value, field.name)"
                              >
                                <el-icon><View /></el-icon> 预览
                              </el-button>
                              <el-button type="info" size="small" plain @click="downloadFile(field.value)">
                                <el-icon><Download /></el-icon> 下载
                              </el-button>
                            </div>
                          </div>
                          
                          <!-- 日期类型 -->
                          <div v-else-if="isDateValue(field.value)" class="field-value">
                            {{ formatDate(field.value) }}
                          </div>
                          
                          <!-- 数组类型 -->
                          <div v-else-if="Array.isArray(field.value)" class="field-value">
                            <el-tag 
                              v-for="(v, i) in field.value" 
                              :key="i" 
                              size="small" 
                              effect="plain"
                              class="array-tag"
                            >
                              {{ v }}
                            </el-tag>
                          </div>
                          
                          <!-- 普通值 -->
                          <div v-else class="field-value">
                            {{ field.value ?? '-' }}
                          </div>
                        </div>
                      </template>
                    </div>
                  </div>
                </template>
              </div>

              <div class="card-footer">
                <el-button type="success" @click="approveData(item)">
                  <el-icon><Check /></el-icon> 通过
                </el-button>
                <el-button type="danger" plain @click="rejectData(item)">
                  <el-icon><Close /></el-icon> 拒绝
                </el-button>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无待审核数据" :image-size="120" />
        </div>

        <!-- 初始状态提示 (step 1) -->
        <div class="welcome-section animate-slide-up delay-2" v-if="step === 1">
          <div class="welcome-card">
            <div class="welcome-icon">
              <el-icon :size="64"><Pointer /></el-icon>
            </div>
            <h2>请从左侧选择模板分类</h2>
            <p>选择分类后，将展示该分类下的所有模板，然后您可以选择要审核的模板数据</p>
          </div>
        </div>
      </main>
    </div>

    <!-- 文件预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      :title="'预览: ' + previewTitle"
      :width="previewType === 'image' ? 'auto' : '900px'"
      top="3vh"
      class="preview-dialog"
      :class="{ 'image-dialog': previewType === 'image' }"
      destroy-on-close
      @closed="onPreviewDialogClosed"
    >
      <div class="preview-content" v-loading="previewLoading" element-loading-text="加载中...">
        <!-- 加载完成后显示内容 -->
        <template v-if="!previewLoading && previewUrl">
          <!-- 图片预览 -->
          <div v-if="previewType === 'image'" class="image-preview">
            <img 
              :src="previewUrl" 
              class="preview-image"
              @error="onImageError"
            />
          </div>
          
          <!-- 通用文件预览（使用iframe嵌入显示） -->
          <div v-else class="iframe-preview">
            <iframe 
              :src="previewUrl" 
              class="preview-iframe"
              @load="onIframeLoad"
              @error="onIframeError"
            ></iframe>
          </div>
        </template>
      </div>
      
      <!-- 底部操作按钮 -->
      <template #footer>
        <div class="preview-footer">
          <el-button @click="openInNewTab" :disabled="previewLoading || !previewUrl">
            <el-icon><View /></el-icon> 新窗口打开
          </el-button>
          <el-button type="primary" @click="downloadFile()" :disabled="previewLoading">
            <el-icon><Download /></el-icon> 下载文件
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 拒绝原因对话框 -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="拒绝原因"
      width="500px"
      class="reject-dialog"
    >
      <el-form>
        <el-form-item label="请输入拒绝原因">
          <el-input
            v-model="rejectReason"
            type="textarea"
            :rows="4"
            placeholder="请说明拒绝该数据的原因..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Folder, Document, User, Search, DataAnalysis, DataBoard,
  Files, ArrowLeft, Check, Close, Picture, Download, Pointer,
  ZoomIn, View, Loading
} from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'
import { getCategoryTree, defaultExpandedKeys as defaultKeys, getNumericCategoryId } from '@/utils/templateCategories'
import { useUserStore } from '@/stores/user'
import UTIF from 'utif2'

const router = useRouter()
const userStore = useUserStore()

// 树组件引用
const treeRef = ref(null)

// 步骤控制
const step = ref(1)

// 加载状态
const loadingTemplates = ref(false)
const loadingData = ref(false)

// 分类相关
const currentCategory = ref(null)
const categoryTree = ref(getCategoryTree())
const defaultExpandedKeys = ref([...defaultKeys])

// 模板相关
const templates = ref([])
const selectedTemplate = ref(null)
const templateFields = ref([]) // 模板字段信息

// 待审核数据
const pendingData = ref([])

// 预加载的缩略图 URL 缓存
const thumbnailCache = ref({})

// 文件预览相关
const previewDialogVisible = ref(false)
const previewType = ref('file')
const previewUrl = ref('')
const previewTitle = ref('')
const currentFileId = ref('')

// 获取缩略图 URL（优先使用缓存）
const getThumbnailUrl = (fileId) => {
  return thumbnailCache.value[fileId] || ''
}

// 预加载缩略图
const preloadThumbnails = async (data) => {
  for (const item of data) {
    for (const [key, value] of Object.entries(item)) {
      if (isFileField(key, value) && isImageField(key)) {
        // 如果缓存中没有，则加载
        if (!thumbnailCache.value[value]) {
          try {
            const blobUrl = await getFileBlobUrl(value)
            if (blobUrl) {
              thumbnailCache.value[value] = blobUrl
            }
          } catch (error) {
            console.error('预加载缩略图失败:', error)
          }
        }
      }
    }
  }
}

// 拒绝相关
const rejectDialogVisible = ref(false)
const rejectReason = ref('')
const currentRejectItem = ref(null)

// 处理分类点击
const handleCategoryClick = (data) => {
  // 如果是有子目录的大类，不加载数据
  if (data.children && Array.isArray(data.children) && data.children.length > 0) {
    return
  }
  
  currentCategory.value = data
  selectedTemplate.value = null
  pendingData.value = []
  step.value = 2
  loadTemplates()
}

// 加载模板列表
const loadTemplates = async () => {
  if (!currentCategory.value?.id) return
  
  loadingTemplates.value = true
  try {
    const numericCategoryId = getNumericCategoryId(currentCategory.value.id)
    if (numericCategoryId > 0) {
      const response = await request.get(`/template/getTemplateByCategory/${numericCategoryId}`)
      if (response.data?.code === 1) {
        // 只显示已通过审核的模板 (state === 1)
        templates.value = (response.data.data || []).filter(t => t.state === 1)
      } else {
        templates.value = []
      }
    } else {
      templates.value = []
    }
  } catch (error) {
    console.error('加载模板失败:', error)
    ElMessage.error('加载模板失败')
    templates.value = []
  } finally {
    loadingTemplates.value = false
  }
}

// 选择模板
const selectTemplate = async (template) => {
  selectedTemplate.value = template
  step.value = 3
  // 先加载模板字段信息
  await loadTemplateFields()
  // 再加载待审核数据
  await loadPendingData()
}

// 加载模板字段信息
const loadTemplateFields = async () => {
  if (!selectedTemplate.value?.id) return
  
  try {
    const numericCategoryId = getNumericCategoryId(currentCategory.value?.id)
    if (numericCategoryId > 0) {
      const response = await request.get(`/template/getDetailedTemplateByCategory/${numericCategoryId}`)
      if (response.data?.code === 1 || response.data?.code === 0) {
        const detailedTemplates = response.data.data || []
        const detailedTemplate = detailedTemplates.find(t => t.templateId === selectedTemplate.value.id)
        if (detailedTemplate && detailedTemplate.templateFields) {
          // 按照字段顺序排序（保持创建时的顺序）
          templateFields.value = detailedTemplate.templateFields.sort((a, b) => {
            // 先按分类排序：对象(1) -> 操作(2) -> 结果(3)
            if (a.fieldCategory !== b.fieldCategory) {
              return (a.fieldCategory || 0) - (b.fieldCategory || 0)
            }
            // 同分类内按ID排序（假设ID反映创建顺序）
            return (a.id || 0) - (b.id || 0)
          })
        } else {
          templateFields.value = []
        }
      }
    }
  } catch (error) {
    console.error('加载模板字段失败:', error)
    templateFields.value = []
  }
}

// 加载待审核数据
const loadPendingData = async () => {
  if (!selectedTemplate.value?.id) return
  
  loadingData.value = true
  try {
    const response = await request.get(`/audit/getTempData/${selectedTemplate.value.id}`)
    if (response.data?.code === 1) {
      // 只显示待审核的数据 (status === 0)
      const data = (response.data.data || []).filter(item => item.status === 0)
      pendingData.value = data
      
      // 异步预加载缩略图（不阻塞UI）
      preloadThumbnails(data)
    } else {
      pendingData.value = []
    }
  } catch (error) {
    console.error('加载待审核数据失败:', error)
    ElMessage.error('加载待审核数据失败')
    pendingData.value = []
  } finally {
    loadingData.value = false
  }
}

// 返回模板选择
const goBackToTemplates = () => {
  step.value = 2
  selectedTemplate.value = null
  pendingData.value = []
}

// 获取显示字段（按照模板字段顺序和分类组织）
const getDisplayFields = (item) => {
  if (!templateFields.value || templateFields.value.length === 0) {
    // 如果没有字段信息，使用原来的方式（过滤掉id和status）
    const result = {}
    for (const [key, value] of Object.entries(item)) {
      if (key !== 'id' && key !== 'status') {
        result[key] = value
      }
    }
    return result
  }
  
  // 按照模板字段顺序组织数据
  const result = {}
  templateFields.value.forEach(field => {
    const fieldName = field.fieldName
    if (item.hasOwnProperty(fieldName)) {
      result[fieldName] = item[fieldName]
    }
  })
  
  return result
}

// 获取按分类分组的字段
const getFieldsByCategory = (item) => {
  if (!templateFields.value || templateFields.value.length === 0) {
    return { object: [], operation: [], result: [] }
  }
  
  const categories = {
    object: [], // 对象区域 (fieldCategory = 1)
    operation: [], // 操作区域 (fieldCategory = 2)
    result: [] // 结果区域 (fieldCategory = 3)
  }
  
  // 记录已处理的枚举字段名，避免重复
  const processedEnumNames = new Set()
  
  templateFields.value.forEach(field => {
    const fieldName = field.fieldName
    const category = field.fieldCategory
    const dataType = field.dataType
    
    // 判断是否为枚举类型
    const isEnum = dataType === '枚举型' || (typeof dataType === 'string' && dataType.includes('枚举'))
    
    if (isEnum && fieldName.includes(':')) {
      // 枚举类型：字段名格式为 "枚举名:选项值"，数据库中存储的是 "枚举名"
      const enumName = fieldName.split(':')[0]
      
      // 避免重复添加同一个枚举字段
      if (processedEnumNames.has(enumName)) {
        return
      }
      
      if (item.hasOwnProperty(enumName)) {
        processedEnumNames.add(enumName)
        const fieldData = {
          name: enumName,
          value: item[enumName],
          category: category
        }
        
        if (category === 1) {
          categories.object.push(fieldData)
        } else if (category === 2) {
          categories.operation.push(fieldData)
        } else if (category === 3) {
          categories.result.push(fieldData)
        }
      }
    } else if (item.hasOwnProperty(fieldName)) {
      // 普通字段
      const fieldData = {
        name: fieldName,
        value: item[fieldName],
        category: category
      }
      
      if (category === 1) {
        categories.object.push(fieldData)
      } else if (category === 2) {
        categories.operation.push(fieldData)
      } else if (category === 3) {
        categories.result.push(fieldData)
      }
    }
  })
  
  return categories
}

// 判断是否为文件字段
const isFileField = (key, value) => {
  // MongoDB ObjectId 格式：24位十六进制字符串
  if (typeof value === 'string' && /^[0-9a-fA-F]{24}$/.test(value)) {
    return true
  }
  // 或者字段名包含"文件"或"图片"
  const fileKeywords = ['文件', '图片', 'file', 'image', 'File', 'Image', 'attachment', '附件']
  return fileKeywords.some(keyword => key.includes(keyword))
}

// 判断是否为图片字段
const isImageField = (key) => {
  const imageKeywords = ['图片', 'image', 'Image', '照片', 'photo', 'Photo', '图像']
  return imageKeywords.some(keyword => key.includes(keyword))
}

// 判断是否为日期值
const isDateValue = (value) => {
  if (typeof value === 'string') {
    // ISO 日期格式
    return /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?/.test(value)
  }
  return false
}

// 格式化日期
const formatDate = (value) => {
  if (!value) return '-'
  try {
    const date = new Date(value)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch {
    return value
  }
}

// 获取文件URL（直接URL，不带认证）
const getFileUrl = (fileId) => {
  return `/api/templateData/getFile/${fileId}`
}

// 获取文件 Blob URL（带认证，用于预览）
const getFileBlobUrl = async (fileId) => {
  try {
    const response = await request.get(`/templateData/getFile/${fileId}`, {
      responseType: 'blob'
    })
    return URL.createObjectURL(response.data)
  } catch (error) {
    console.error('获取文件失败:', error)
    ElMessage.error('获取文件失败')
    return null
  }
}

// 判断是否为可预览的文件类型（PDF、文本等）
const isPreviewableFile = (key) => {
  const previewableKeywords = ['pdf', 'PDF', '文档', 'doc', 'txt', '报告']
  return previewableKeywords.some(keyword => key.includes(keyword))
}

// 判断是否为PDF文件
const isPdfFile = (fieldName) => {
  if (!fieldName) return false
  const pdfKeywords = ['pdf', 'PDF']
  return pdfKeywords.some(keyword => fieldName.toLowerCase().includes(keyword.toLowerCase()))
}

// 判断是否为 TIF/TIFF 文件（通过文件名）
const isTifFile = (fieldName) => {
  if (!fieldName) return false
  const tifKeywords = ['tif', 'tiff', 'TIF', 'TIFF']
  return tifKeywords.some(keyword => fieldName.toLowerCase().includes(keyword.toLowerCase()))
}

// 通过文件内容的魔数检测 TIF 文件
const detectTifByContent = async (blob) => {
  try {
    const arrayBuffer = await blob.slice(0, 8).arrayBuffer()
    const view = new Uint8Array(arrayBuffer)
    // TIF 文件魔数: II (Intel) 或 MM (Motorola)
    // II 42 00 00 或 MM 00 42 00
    if (view.length >= 4) {
      const isIntel = view[0] === 0x49 && view[1] === 0x49 && view[2] === 0x2A && view[3] === 0x00
      const isMotorola = view[0] === 0x4D && view[1] === 0x4D && view[2] === 0x00 && view[3] === 0x2A
      return isIntel || isMotorola
    }
  } catch (error) {
    console.error('检测 TIF 文件失败:', error)
  }
  return false
}

// 将 TIF 文件转换为 PNG Blob URL
const convertTifToPng = async (blob) => {
  try {
    const arrayBuffer = await blob.arrayBuffer()
    const ifds = UTIF.decode(arrayBuffer)
    if (ifds.length === 0) {
      throw new Error('TIF 文件解析失败：未找到图像数据')
    }
    
    // 解码第一页
    UTIF.decodeImage(arrayBuffer, ifds[0])
    const firstPage = ifds[0]
    
    if (!firstPage.width || !firstPage.height) {
      throw new Error('TIF 文件解析失败：无效的图像尺寸')
    }
    
    const rgba = UTIF.toRGBA8(firstPage)
    
    // 创建 Canvas 并绘制图像
    const canvas = document.createElement('canvas')
    canvas.width = firstPage.width
    canvas.height = firstPage.height
    const ctx = canvas.getContext('2d')
    const imageData = ctx.createImageData(firstPage.width, firstPage.height)
    imageData.data.set(rgba)
    ctx.putImageData(imageData, 0, 0)
    
    // 转换为 Blob URL
    return new Promise((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(URL.createObjectURL(blob))
        } else {
          reject(new Error('TIF 转换为 PNG 失败'))
        }
      }, 'image/png')
    })
  } catch (error) {
    console.error('TIF 转换失败:', error)
    throw error
  }
}

// 在新窗口打开文件
const openInNewTab = () => {
  if (previewUrl.value) {
    window.open(previewUrl.value, '_blank')
  }
}

// 关闭预览弹窗时清理资源
const onPreviewDialogClosed = () => {
  if (previewUrl.value && previewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(previewUrl.value)
  }
  previewUrl.value = ''
  previewType.value = 'file'
  currentFileId.value = ''
  previewTitle.value = ''
}

// iframe 加载完成
const onIframeLoad = () => {
  console.log('文件预览加载完成')
}

// iframe 加载错误
const onIframeError = () => {
  console.error('文件预览加载失败')
  ElMessage.warning('文件预览加载失败，请尝试下载查看')
}

// 图片加载错误
const onImageError = () => {
  ElMessage.error('图片加载失败')
}

// 预览加载状态
const previewLoading = ref(false)

// 预览文件
const previewFile = async (fileId, fieldName) => {
  currentFileId.value = fileId
  previewTitle.value = fieldName
  previewLoading.value = true
  previewDialogVisible.value = true
  
  // 清除之前的 Blob URL
  if (previewUrl.value && previewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(previewUrl.value)
  }
  previewUrl.value = ''
  
  if (isImageField(fieldName)) {
    previewType.value = 'image'
  } else {
    previewType.value = 'file'
  }
  
  try {
    // 获取文件 Blob
    const response = await request.get(`/templateData/getFile/${fileId}`, {
      responseType: 'blob'
    })
    const blob = response.data
    
    // 检测是否为 TIF 文件（通过文件名、Content-Type 或文件内容）
    const isTifByName = isTifFile(fieldName)
    const isTifByType = blob.type === 'image/tiff' || blob.type === 'image/tif'
    const isTifByContent = await detectTifByContent(blob)
    
    // 如果是 TIF/TIFF 文件，进行转换
    if (isTifByName || isTifByType || isTifByContent) {
      previewType.value = 'image'
      try {
        const pngUrl = await convertTifToPng(blob)
        previewUrl.value = pngUrl
      } catch (convertError) {
        console.error('TIF 转换失败:', convertError)
        ElMessage.warning('TIF 文件预览转换失败，请尝试下载查看。错误：' + (convertError.message || '未知错误'))
        // 如果转换失败，尝试直接显示（虽然浏览器可能不支持）
        previewUrl.value = URL.createObjectURL(blob)
      }
    } else {
      previewUrl.value = URL.createObjectURL(blob)
    }
  } catch (error) {
    console.error('预览文件失败:', error)
    ElMessage.error('预览文件失败，请尝试下载查看')
    previewDialogVisible.value = false
  }
  previewLoading.value = false
}

// 下载文件（支持传入 fileId 参数或使用当前选中的文件）
const downloadFile = async (fileId) => {
  const id = fileId || currentFileId.value
  try {
    const response = await request.get(`/templateData/getFile/${id}`, {
      responseType: 'blob'
    })
    
    // 从响应头获取文件名
    const contentDisposition = response.headers['content-disposition']
    let filename = '下载文件'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename\*?=(?:UTF-8'')?([^;\n]+)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = decodeURIComponent(filenameMatch[1].replace(/"/g, ''))
      }
    }
    
    // 创建下载链接
    const blobUrl = URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(blobUrl)
    
    ElMessage.success('文件下载成功')
  } catch (error) {
    console.error('下载文件失败:', error)
    ElMessage.error('下载文件失败')
  }
}

// 审核通过
const approveData = async (item) => {
  try {
    await ElMessageBox.confirm('确定要通过该数据的审核吗？', '确认通过', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    })
    
    // 获取审核员ID
    let auditorId = 0
    try {
      if (userStore.userName) {
        const userInfoResponse = await request.get(`/user/info/${userStore.userName}`)
        if (userInfoResponse.data?.code === 1 && userInfoResponse.data.data?.id) {
          auditorId = userInfoResponse.data.data.id
        }
      }
    } catch (error) {
      console.warn('获取用户ID失败:', error)
    }
    
    // 调用审核通过接口（后端期望数组格式，auditResult: 1=通过, 0=不通过）
    const response = await request.post('/audit/auditTemplateData', [{
      templateId: selectedTemplate.value.id,
      templateDataId: item.id,
      auditorId: auditorId,
      auditResult: 1, // 1=通过
      note: '审核通过'
    }])
    
    if (response.data?.code === 1) {
      ElMessage.success('审核通过')
      // 从列表中移除该数据
      pendingData.value = pendingData.value.filter(d => d.id !== item.id)
    } else {
      ElMessage.error(response.data?.message || '操作失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审核失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 拒绝数据
const rejectData = (item) => {
  currentRejectItem.value = item
  rejectReason.value = ''
  rejectDialogVisible.value = true
}

// 确认拒绝
const confirmReject = async () => {
  if (!currentRejectItem.value) return
  
  try {
    // 获取审核员ID
    let auditorId = 0
    try {
      if (userStore.userName) {
        const userInfoResponse = await request.get(`/user/info/${userStore.userName}`)
        if (userInfoResponse.data?.code === 1 && userInfoResponse.data.data?.id) {
          auditorId = userInfoResponse.data.data.id
        }
      }
    } catch (error) {
      console.warn('获取用户ID失败:', error)
    }
    
    // 调用审核拒绝接口（后端期望数组格式，auditResult: 1=通过, 0=不通过）
    const response = await request.post('/audit/auditTemplateData', [{
      templateId: selectedTemplate.value.id,
      templateDataId: currentRejectItem.value.id,
      auditorId: auditorId,
      auditResult: 0, // 0=不通过
      note: rejectReason.value || '审核未通过'
    }])
    
    if (response.data?.code === 1) {
      ElMessage.success('已拒绝')
      // 从列表中移除该数据
      pendingData.value = pendingData.value.filter(d => d.id !== currentRejectItem.value.id)
      rejectDialogVisible.value = false
    } else {
      ElMessage.error(response.data?.message || '操作失败')
    }
  } catch (error) {
    console.error('拒绝失败:', error)
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  // 页面初始化
})
</script>

<style lang="scss" scoped>
.tpl-data-audit {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
}

.page-container {
  display: flex;
  min-height: calc(100vh - 64px);
  padding-top: 64px;
}

// 页面头部 banner
.page-banner {
  position: relative;
  border-radius: 24px;
  padding: 32px 40px;
  margin-bottom: 28px;
  overflow: hidden;
  background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #6366f1 100%);
}

.banner-bg {
  position: absolute;
  inset: 0;
  
  .banner-pattern {
    position: absolute;
    inset: 0;
    opacity: 0.1;
    background-image: 
      radial-gradient(circle at 20% 80%, rgba(255,255,255,0.3) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(255,255,255,0.3) 0%, transparent 50%);
  }
}

.banner-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 24px;
}

.banner-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.banner-info {
  flex: 1;
  
  .page-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: white;
    margin-bottom: 8px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .page-desc {
    color: rgba(255, 255, 255, 0.9);
    font-size: 0.9375rem;
    margin: 0;
  }
}

.banner-badge {
  flex-shrink: 0;
  
  .el-tag {
    padding: 12px 20px;
    font-size: 0.9375rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

// 步骤导航
.steps-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.step {
  display: flex;
  align-items: center;
  gap: 12px;
  opacity: 0.5;
  transition: all 0.3s ease;
  
  &.active {
    opacity: 1;
    
    .step-number {
      background: linear-gradient(135deg, #ec4899, #8b5cf6);
      color: white;
      transform: scale(1.1);
    }
    
    .step-label {
      color: #1e293b;
      font-weight: 600;
    }
  }
  
  &.done {
    .step-number {
      background: #10b981;
      color: white;
    }
  }
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.step-label {
  font-size: 0.9375rem;
  color: #94a3b8;
  transition: all 0.3s ease;
}

.step-line {
  width: 80px;
  height: 3px;
  background: #e2e8f0;
  margin: 0 16px;
  border-radius: 2px;
  transition: all 0.3s ease;
  
  &.active {
    background: linear-gradient(90deg, #10b981, #34d399);
  }
}

// 侧边栏
.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid #f1f5f9;
}

.sidebar-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  
  .sidebar-icon {
    font-size: 1.25rem;
    color: #ec4899;
  }
  
  h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }
}

.sidebar-content {
  padding: 16px;
  overflow-y: auto;
  max-height: calc(100vh - 160px);
}

.category-tree {
  background: transparent;
  
  :deep(.el-tree-node__content) {
    height: 40px;
    border-radius: 8px;
    
    &:hover {
      background: #fdf2f8;
    }
  }
  
  :deep(.el-tree-node.is-current > .el-tree-node__content) {
    background: linear-gradient(135deg, rgba(236, 72, 153, 0.1), rgba(139, 92, 246, 0.1));
    color: #ec4899;
  }
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

// 主内容区
.main-content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
}

// 模板选择区域
.template-section,
.data-section {
  background: white;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f1f5f9;
  
  h3 {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
    
    .el-icon {
      color: #ec4899;
    }
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

// 模板网格
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.template-card {
  background: #f8fafc;
  border: 2px solid transparent;
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #fdf2f8;
    border-color: #f9a8d4;
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(236, 72, 153, 0.15);
  }
  
  &.selected {
    background: linear-gradient(135deg, rgba(236, 72, 153, 0.1), rgba(139, 92, 246, 0.1));
    border-color: #ec4899;
  }
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, #ec4899, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 16px;
}

.card-info {
  margin-bottom: 12px;
  
  h4 {
    font-size: 1.0625rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0 0 8px;
  }
  
  p {
    font-size: 0.875rem;
    color: #64748b;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

.card-meta {
  .creator {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.8125rem;
    color: #94a3b8;
  }
}

// 数据卡片
.data-cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.data-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: fadeInUp 0.4s ease forwards;
  opacity: 0;
  
  &:hover {
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    border-color: #cbd5e1;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.data-card .card-header {
  padding: 16px 24px;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border-bottom: 1px solid #e2e8f0;
}

.card-id {
  display: flex;
  align-items: center;
  gap: 12px;
}

.data-card .card-body {
  padding: 24px;
}

.field-category-section {
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.category-header {
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
}

.field-category-section {
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.category-header {
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
}

.fields-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.field-item {
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  
  &.file-field {
    background: linear-gradient(135deg, #fdf2f8, #fce7f3);
    border-color: #f9a8d4;
  }
}

.field-label {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 6px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.field-value {
  font-size: 0.9375rem;
  color: #1e293b;
  word-break: break-word;
  
  &.file-value {
    margin-top: 4px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  &.image-field {
    align-items: flex-start;
  }
}

// 缩略图预览
.thumbnail-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #ec4899;
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(236, 72, 153, 0.25);
  }
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-loading {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  color: #94a3b8;
}

.thumbnail-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  color: #94a3b8;
}

// 文件图标
.file-icon-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 6px;
  
  .el-icon {
    color: #ec4899;
  }
  
  .file-id {
    font-size: 0.75rem;
    color: #64748b;
    font-family: monospace;
  }
}

// 文件操作按钮
.file-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.array-tag {
  margin: 2px 4px 2px 0;
}

.data-card .card-footer {
  padding: 16px 24px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

// 欢迎卡片
.welcome-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.welcome-card {
  text-align: center;
  padding: 60px 80px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.welcome-icon {
  width: 120px;
  height: 120px;
  margin: 0 auto 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fdf2f8, #fce7f3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ec4899;
}

.welcome-card h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.welcome-card p {
  font-size: 1rem;
  color: #64748b;
  max-width: 400px;
  line-height: 1.6;
}

// 文件预览对话框
.preview-dialog {
  &.image-dialog {
    :deep(.el-dialog) {
      max-width: 95vw;
      width: auto !important;
      margin: 0 auto;
    }
    
    :deep(.el-dialog__body) {
      padding: 20px;
      overflow: visible;
    }
  }
  
  .preview-content {
    min-height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: visible;
  }
  
  .image-preview {
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .preview-image {
      max-width: 90vw;
      max-height: 70vh;
      width: auto;
      height: auto;
      border-radius: 8px;
      object-fit: contain;
      display: block;
    }
  }
  
  .image-error {
    padding: 60px;
    color: #94a3b8;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }
  
  .iframe-preview {
    width: 100%;
    height: 70vh;
    
    .preview-iframe {
      width: 100%;
      height: 100%;
      border: none;
      border-radius: 8px;
      background: #f5f7fa;
    }
  }
  
  .image-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 60px;
    color: #909399;
  }
  
  .preview-footer {
    display: flex;
    justify-content: center;
    gap: 12px;
  }
  
  .file-preview-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
  }
  
  .file-info {
    margin-bottom: 24px;
    
    .file-icon {
      color: #ec4899;
      margin-bottom: 16px;
    }
    
    h3 {
      font-size: 1.25rem;
      color: #1e293b;
      margin-bottom: 8px;
    }
    
    p {
      font-size: 0.875rem;
      color: #64748b;
    }
  }
}

// 动画
.animate-slide-up {
  animation: slideUp 0.5s ease-out;
  
  &.delay-1 { animation-delay: 0.1s; opacity: 0; animation-fill-mode: forwards; }
  &.delay-2 { animation-delay: 0.2s; opacity: 0; animation-fill-mode: forwards; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

// 响应式
@media (max-width: 768px) {
  .page-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .sidebar-content {
    max-height: 200px;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .page-banner {
    padding: 24px 20px;
    border-radius: 0;
    margin: 0 -16px 20px;
  }
  
  .banner-content {
    flex-direction: column;
    text-align: center;
  }
  
  .steps-nav {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .step-line {
    width: 40px;
  }
  
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .fields-grid {
    grid-template-columns: 1fr;
  }
}
</style>

