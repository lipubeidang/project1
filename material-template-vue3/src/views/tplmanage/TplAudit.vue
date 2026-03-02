<template>
  <div class="tpl-audit">
    <Navbar />
    
    <div class="page-container">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="sidebar-title-wrap">
            <el-icon class="sidebar-icon"><Checked /></el-icon>
            <h3>审核分类</h3>
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
              <el-icon :size="36"><Checked /></el-icon>
            </div>
            <div class="banner-info">
              <h1 class="page-title">模版审核</h1>
              <p class="page-desc" v-if="currentCategory">
                当前目录：{{ currentCategory.name }}
              </p>
              <p class="page-desc" v-else>审核员专属功能，管理模版审核流程</p>
            </div>
            <div class="banner-badge">
              <el-tag type="warning" effect="dark" size="large">
                <el-icon><User /></el-icon>
                审核员专用
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 搜索栏 -->
        <div class="search-section animate-slide-up delay-1">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索模版名称..."
            :prefix-icon="Search"
            size="large"
            clearable
            class="search-input"
          />
        </div>

        <!-- 审核状态切换 -->
        <div class="audit-tabs animate-slide-up delay-2">
          <el-tabs v-model="activeTab" @tab-change="handleTabChange">
            <el-tab-pane label="待审核" name="pending">
              <div class="templates-section" v-loading="loading">
                <div class="templates-grid" v-if="displayedPendingTemplates.length > 0">
                  <div 
                    v-for="template in displayedPendingTemplates" 
                    :key="template.id"
                    class="template-card pending"
                  >
                    <div class="card-header">
                      <h4 class="card-title">{{ template.name }}</h4>
                      <el-tag type="warning" effect="light">待审核</el-tag>
                    </div>
                    <div class="card-body">
                      <div class="info-item">
                        <el-icon><User /></el-icon>
                        <span>创建者：{{ template.creator || '未知' }}</span>
                      </div>
                      <div class="info-item">
                        <el-icon><Calendar /></el-icon>
                        <span>{{ formatDate(template.createTime) }}</span>
                      </div>
                      <p class="description">{{ template.description || '暂无描述' }}</p>
                    </div>
                    <div class="card-actions">
                      <el-button type="primary" size="small" @click="reviewTemplate(template)">
                        审核模版
                      </el-button>
                      <el-button type="success" size="small" plain @click="editTemplateFields(template)">
                        修改字段
                      </el-button>
                      <el-button type="danger" size="small" plain @click="rejectTemplate(template)">
                        拒绝
                      </el-button>
                    </div>
                  </div>
                </div>
                <el-empty v-else-if="!loading" description="暂无待审核的模版" :image-size="120" />
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="已通过" name="approved">
              <div class="templates-section" v-loading="loading">
                <div class="templates-grid" v-if="displayedApprovedTemplates.length > 0">
                  <div 
                    v-for="template in displayedApprovedTemplates" 
                    :key="template.id"
                    class="template-card approved"
                  >
                    <div class="card-header">
                      <h4 class="card-title">{{ template.name }}</h4>
                      <el-tag type="success" effect="light">已通过</el-tag>
                    </div>
                    <div class="card-body">
                      <div class="info-item">
                        <el-icon><User /></el-icon>
                        <span>创建者：{{ template.creator || '未知' }}</span>
                      </div>
                      <div class="info-item">
                        <el-icon><Calendar /></el-icon>
                        <span>{{ formatDate(template.createTime) }}</span>
                      </div>
                      <p class="description">{{ template.description || '暂无描述' }}</p>
                    </div>
                    <div class="card-actions">
                      <el-button type="primary" size="small" @click="viewTemplateFields(template)">
                        查看详情
                      </el-button>
                      <el-button type="success" size="small" plain @click="editTemplateFields(template)">
                        修改字段
                      </el-button>
                      <el-button type="warning" size="small" plain @click="revokeApproval(template)">
                        撤销
                      </el-button>
                    </div>
                  </div>
                </div>
                <el-empty v-else-if="!loading" description="暂无已通过的模版" :image-size="120" />
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="已拒绝" name="rejected">
              <div class="templates-section" v-loading="loading">
                <div class="templates-grid" v-if="displayedRejectedTemplates.length > 0">
                  <div 
                    v-for="template in displayedRejectedTemplates" 
                    :key="template.id"
                    class="template-card rejected"
                  >
                    <div class="card-header">
                      <h4 class="card-title">{{ template.name }}</h4>
                      <el-tag type="danger" effect="light">已拒绝</el-tag>
                    </div>
                    <div class="card-body">
                      <div class="info-item">
                        <el-icon><User /></el-icon>
                        <span>创建者：{{ template.creator || '未知' }}</span>
                      </div>
                      <div class="info-item">
                        <el-icon><Calendar /></el-icon>
                        <span>{{ formatDate(template.createTime) }}</span>
                      </div>
                      <p class="description">{{ template.description || '暂无描述' }}</p>
                    </div>
                    <div class="card-actions">
                      <el-button type="primary" size="small" @click="reApprove(template)">
                        重新审核
                      </el-button>
                    </div>
                  </div>
                </div>
                <el-empty v-else-if="!loading" description="暂无已拒绝的模版" :image-size="120" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </main>
    </div>

    <!-- 审核详情对话框 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="`审核模版: ${currentReviewTemplate?.name || ''}`"
      width="900px"
      top="5vh"
      class="review-dialog"
    >
      <div class="review-content" v-if="currentReviewTemplate">
        <!-- 基本信息卡片 -->
        <div class="info-card">
          <div class="info-card-header">
            <el-icon><Document /></el-icon>
            <span>基本信息</span>
          </div>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">模版名称</span>
              <span class="info-value">{{ currentReviewTemplate.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建者</span>
              <span class="info-value">{{ currentReviewTemplate.creator || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{ formatDate(currentReviewTemplate.createTime) }}</span>
            </div>
            <div class="info-item full-width">
              <span class="info-label">描述</span>
              <span class="info-value">{{ currentReviewTemplate.description || '暂无' }}</span>
            </div>
          </div>
        </div>
        
        <!-- 字段信息展示 - 分区域展示 -->
        <div class="fields-card" v-if="processedFields && (processedFields.object.length > 0 || processedFields.operation.length > 0 || processedFields.result.length > 0)">
          <div class="info-card-header">
            <el-icon><Grid /></el-icon>
            <span>模版字段信息</span>
          </div>
          
          <!-- 对象区域 -->
          <div class="field-section" v-if="processedFields.object.length > 0">
            <div class="section-header object">
              <el-icon><Box /></el-icon>
              <span>对象区域</span>
              <el-tag size="small" type="primary">{{ processedFields.object.length }} 个字段</el-tag>
            </div>
            <div class="field-list">
              <template v-for="(item, index) in processedFields.object" :key="index">
                <!-- 普通字段 -->
                <div v-if="!item.isEnum" class="field-item">
                  <span class="field-name">{{ item.fieldName }}</span>
                  <el-tag size="small" :type="getDataTypeTagType(item.dataType)">{{ item.dataType }}</el-tag>
                </div>
                <!-- 枚举字段组 -->
                <div v-else class="enum-group">
                  <div class="enum-header">
                    <span class="enum-name">{{ item.enumName }}</span>
                    <el-tag size="small" type="danger">枚举型</el-tag>
                  </div>
                  <div class="enum-options">
                    <el-tag v-for="opt in item.options" :key="opt" size="small" effect="plain">{{ opt }}</el-tag>
                  </div>
                </div>
              </template>
            </div>
          </div>
          
          <!-- 操作区域 -->
          <div class="field-section" v-if="processedFields.operation.length > 0">
            <div class="section-header operation">
              <el-icon><Edit /></el-icon>
              <span>操作区域</span>
              <el-tag size="small" type="success">{{ processedFields.operation.length }} 个字段</el-tag>
            </div>
            <div class="field-list">
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
                    <el-tag v-for="opt in item.options" :key="opt" size="small" effect="plain">{{ opt }}</el-tag>
                  </div>
                </div>
              </template>
            </div>
          </div>
          
          <!-- 结果区域 -->
          <div class="field-section" v-if="processedFields.result.length > 0">
            <div class="section-header result">
              <el-icon><DataLine /></el-icon>
              <span>结果区域</span>
              <el-tag size="small" type="warning">{{ processedFields.result.length }} 个字段</el-tag>
            </div>
            <div class="field-list">
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
                    <el-tag v-for="opt in item.options" :key="opt" size="small" effect="plain">{{ opt }}</el-tag>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
        <div class="no-fields" v-else>
          <el-empty description="暂无字段信息" :image-size="60" />
        </div>
        
        <!-- 审核意见 -->
        <div class="comment-card">
          <div class="info-card-header">
            <el-icon><ChatDotRound /></el-icon>
            <span>审核意见</span>
          </div>
          <el-input
            v-model="reviewComment"
            type="textarea"
            :rows="3"
            placeholder="请输入审核意见（可选）"
          />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="handleReject">拒绝</el-button>
        <el-button type="primary" @click="handleApprove">通过审核</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Folder, Document, User, Calendar, Search, Checked, Grid, Box, Edit, DataLine, ChatDotRound } from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'
import { getCategoryTree, defaultExpandedKeys as defaultKeys, getNumericCategoryId } from '@/utils/templateCategories'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 树组件引用
const treeRef = ref(null)

// 状态
const loading = ref(false)
const activeTab = ref('pending')
const currentCategory = ref(null)
const reviewDialogVisible = ref(false)
const currentReviewTemplate = ref(null)
const reviewComment = ref('')
const searchKeyword = ref('')

// 分页变量
const pageSize = 12

// 模板数据
const pendingTemplates = ref([])
const approvedTemplates = ref([])
const rejectedTemplates = ref([])

// 模板详细信息缓存（包含字段信息）
const templateDetailsMap = ref({})

// 目录结构 - 使用统一的分类配置，并在第一行添加"所有模版"选项
const categoryTree = ref([
  {
    id: 'all_pending',
    name: '所有模版',
    description: '显示所有模版',
    icon: 'Document',
    hasChildren: false,
    children: undefined
  },
  ...getCategoryTree()
])
const defaultExpandedKeys = ref([...defaultKeys])

// 搜索过滤函数
const filterByKeyword = (templates) => {
  if (!searchKeyword.value) return templates
  const keyword = searchKeyword.value.toLowerCase()
  return templates.filter(t => 
    (t.name || '').toLowerCase().includes(keyword) ||
    (t.description || '').toLowerCase().includes(keyword) ||
    (t.creator || '').toLowerCase().includes(keyword)
  )
}

// 处理字段信息 - 将枚举型字段按枚举名分组
const processedFields = computed(() => {
  if (!currentReviewTemplate.value?.templateFields) {
    return { object: [], operation: [], result: [] }
  }
  
  const fields = currentReviewTemplate.value.templateFields
  const result = { object: [], operation: [], result: [] }
  
  // 按区域分组
  const areaMap = { 1: 'object', 2: 'operation', 3: 'result' }
  
  // 临时存储枚举分组
  const enumGroups = { object: {}, operation: {}, result: {} }
  
  fields.forEach(field => {
    const areaKey = areaMap[field.fieldCategory] || 'object'
    const dataType = field.fieldDataType || field.dataType || ''
    const isEnum = dataType === '枚举型' || dataType === 4
    
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

// 过滤后的模板
const displayedPendingTemplates = computed(() => filterByKeyword(pendingTemplates.value))
const displayedApprovedTemplates = computed(() => filterByKeyword(approvedTemplates.value))
const displayedRejectedTemplates = computed(() => filterByKeyword(rejectedTemplates.value))

const handleCategoryClick = (data) => {
  console.log('点击分类:', data)
  // 如果是有子目录的大类，不加载数据
  // 检查是否有 children 属性且不为空
  if (data.children && Array.isArray(data.children) && data.children.length > 0) {
    console.log('点击的是大类，不加载数据')
    return
  }
  currentCategory.value = data
  console.log('设置当前分类:', currentCategory.value)
  loadTemplates()
}

const handleTabChange = () => {
  loadTemplates()
}

const loadTemplates = async () => {
  loading.value = true
  try {
    // 待审核状态
    if (activeTab.value === 'pending') {
      // 1. 先获取详细模板信息（包含字段），用于缓存
      const detailResponse = await request.get('/audit/getTemp')
      if (detailResponse.data?.code === 1) {
        const detailTemplates = detailResponse.data.data || []
        // 缓存详细信息，以 templateId 为 key
        detailTemplates.forEach(item => {
          templateDetailsMap.value[item.templateId] = item
        })
        console.log('缓存详细模板信息:', templateDetailsMap.value)
      }
      
      // 2. 根据分类获取简要模板信息
      if (currentCategory.value?.id && currentCategory.value.id !== 'all_pending') {
        // 具体分类：调用分类接口获取简要信息
        const numericCategoryId = getNumericCategoryId(currentCategory.value.id)
        console.log('分类ID:', currentCategory.value.id, '转换为数字ID:', numericCategoryId)
        
        if (numericCategoryId > 0) {
          const response = await request.get(`/template/getTemplateByCategory/${numericCategoryId}`)
          console.log('获取分类模板响应:', response.data)
          if (response.data?.code === 1) {
            let allTemplates = response.data.data || []
            // 筛选 state 为 0（未审核）的模板
            allTemplates = allTemplates.filter(t => t.state === 0)
            pendingTemplates.value = allTemplates
            console.log('获取到的待审核模板:', pendingTemplates.value)
          } else {
            pendingTemplates.value = []
          }
        } else {
          pendingTemplates.value = []
        }
      } else {
        // "所有待审核"：先获取详细信息，再根据 categoryId 调用分类接口获取简要信息
        console.log('显示所有待审核模板')
        const detailTemplates = Object.values(templateDetailsMap.value)
        
        if (detailTemplates.length > 0) {
          // 获取所有待审核模板的 templateId 列表
          const pendingTemplateIds = detailTemplates.map(item => item.templateId)
          console.log('待审核模板ID列表:', pendingTemplateIds)
          
          // 并发请求所有可能的分类ID（1, 9-32）
          const allCategoryIds = [1, ...Array.from({length: 24}, (_, i) => i + 9)]
          
          const requests = allCategoryIds.map(catId => 
            request.get(`/template/getTemplateByCategory/${catId}`).catch(() => null)
          )
          
          const responses = await Promise.all(requests)
          const allSimpleTemplates = []
          
          responses.forEach(response => {
            if (response?.data?.code === 1 && response.data.data) {
              const templates = response.data.data.filter(t => 
                t.state === 0 && pendingTemplateIds.includes(t.id)
              )
              allSimpleTemplates.push(...templates)
            }
          })
          
          pendingTemplates.value = allSimpleTemplates
          console.log('所有待审核模板简要信息:', pendingTemplates.value)
        } else {
          pendingTemplates.value = []
        }
      }
    } else if (activeTab.value === 'approved') {
      // 已通过状态：根据分类获取 state === 1 的模板
      if (currentCategory.value?.id && currentCategory.value.id !== 'all_pending') {
        // 具体分类
        const numericCategoryId = getNumericCategoryId(currentCategory.value.id)
        if (numericCategoryId > 0) {
          const response = await request.get(`/template/getTemplateByCategory/${numericCategoryId}`)
          if (response.data?.code === 1) {
            let allTemplates = response.data.data || []
            // 筛选 state 为 1（已通过）的模板
            allTemplates = allTemplates.filter(t => t.state === 1)
            approvedTemplates.value = allTemplates
            console.log('获取到的已通过模板:', approvedTemplates.value)
          } else {
            approvedTemplates.value = []
          }
        } else {
          approvedTemplates.value = []
        }
      } else {
        // "所有"：并发请求所有分类，筛选 state === 1
        console.log('显示所有已通过模板')
        const allCategoryIds = [1, ...Array.from({length: 24}, (_, i) => i + 9)]
        
        const requests = allCategoryIds.map(catId => 
          request.get(`/template/getTemplateByCategory/${catId}`).catch(() => null)
        )
        
        const responses = await Promise.all(requests)
        const allApprovedTemplates = []
        
        responses.forEach(response => {
          if (response?.data?.code === 1 && response.data.data) {
            const templates = response.data.data.filter(t => t.state === 1)
            allApprovedTemplates.push(...templates)
          }
        })
        
        approvedTemplates.value = allApprovedTemplates
        console.log('所有已通过模板:', approvedTemplates.value)
      }
    } else {
      // 已拒绝状态（暂时保持原有逻辑，如有需要可类似修改）
      if (!currentCategory.value?.id) {
        rejectedTemplates.value = []
        return
      }
      const categoryId = currentCategory.value.id
      const response = await request.get(`/tplmanage/templates/audit/${categoryId}`, {
        params: { status: activeTab.value }
      })
      // 后端成功状态码是 1
      if (response.data?.code === 1) {
        rejectedTemplates.value = response.data.data || []
      }
    }
  } catch (error) {
    console.error('加载模版失败:', error)
    ElMessage.error('加载模版失败')
  } finally {
    loading.value = false
  }
}

const reviewTemplate = async (template) => {
  // 获取模板详细信息（包含字段）
  const templateId = template.id
  const categoryId = template.categoryId // 模板所属的分类目录ID
  let detailInfo = templateDetailsMap.value[templateId]
  
  // 如果缓存中没有，调用 getDetailedTemplateByCategory 接口获取
  if (!detailInfo) {
    try {
      // 使用分类目录ID调用详细信息接口（不是模板ID）
      if (categoryId) {
        const response = await request.get(`/template/getDetailedTemplateByCategory/${categoryId}`)
        console.log('获取模板详细信息响应:', response.data)
        
        if (response.data?.code === 1 || response.data?.code === 0) {
          const templates = response.data.data || []
          // 缓存所有返回的模板信息
          templates.forEach(t => {
            templateDetailsMap.value[t.templateId] = t
          })
          // 找到匹配的模板
          detailInfo = templateDetailsMap.value[templateId]
        }
      }
      
      // 如果仍然没有，尝试从 audit/getTemp 获取
      if (!detailInfo) {
        const auditResponse = await request.get('/audit/getTemp')
        if (auditResponse.data?.code === 1) {
          const detailTemplates = auditResponse.data.data || []
          detailTemplates.forEach(item => {
            templateDetailsMap.value[item.templateId] = item
          })
          detailInfo = templateDetailsMap.value[templateId]
        }
      }
    } catch (error) {
      console.error('获取模板详细信息失败:', error)
    }
  }
  
  // 合并简要信息和详细信息
  currentReviewTemplate.value = {
    ...template,
    templateFields: detailInfo?.templateFields || []
  }
  reviewComment.value = ''
  reviewDialogVisible.value = true
}

const handleApprove = async () => {
  if (!currentReviewTemplate.value) return
  
  try {
    // 获取当前用户ID（审核员ID）
    let auditorId = 0
    try {
      if (userStore.userName) {
        const userInfoResponse = await request.get(`/user/info/${userStore.userName}`)
        if (userInfoResponse.data?.code === 1 && userInfoResponse.data.data?.id) {
          auditorId = userInfoResponse.data.data.id
        }
      }
    } catch (error) {
      console.warn('获取用户ID失败，使用默认值0:', error)
    }
    
    // 调用审核接口
    const response = await request.post('/audit/auditNewTemplate', {
      auditorId: auditorId,
      auditResult: 1, // 1=通过，0=拒绝
      note: reviewComment.value || '',
      templateId: currentReviewTemplate.value.id
    })
    
    if (response.data?.code === 1) {
      ElMessage.success('审核通过')
      reviewDialogVisible.value = false
      loadTemplates()
    } else {
      ElMessage.error(response.data?.message || '审核失败')
    }
  } catch (error) {
    console.error('审核失败:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

const handleReject = async () => {
  if (!currentReviewTemplate.value) return
  
  try {
    // 获取当前用户ID（审核员ID）
    let auditorId = 0
    try {
      if (userStore.userName) {
        const userInfoResponse = await request.get(`/user/info/${userStore.userName}`)
        if (userInfoResponse.data?.code === 1 && userInfoResponse.data.data?.id) {
          auditorId = userInfoResponse.data.data.id
        }
      }
    } catch (error) {
      console.warn('获取用户ID失败，使用默认值0:', error)
    }
    
    // 调用审核接口
    const response = await request.post('/audit/auditNewTemplate', {
      auditorId: auditorId,
      auditResult: 0, // 1=通过，0=拒绝
      note: reviewComment.value || '',
      templateId: currentReviewTemplate.value.id
    })
    
    if (response.data?.code === 1) {
      ElMessage.success('已拒绝')
      reviewDialogVisible.value = false
      loadTemplates()
    } else {
      ElMessage.error(response.data?.message || '操作失败')
    }
  } catch (error) {
    console.error('拒绝失败:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

const rejectTemplate = async (template) => {
  try {
    await ElMessageBox.confirm('确定要拒绝该模版吗？', '提示', { type: 'warning' })
    
    // 获取当前用户ID（审核员ID）
    let auditorId = 0
    try {
      if (userStore.userName) {
        const userInfoResponse = await request.get(`/user/info/${userStore.userName}`)
        if (userInfoResponse.data?.code === 1 && userInfoResponse.data.data?.id) {
          auditorId = userInfoResponse.data.data.id
        }
      }
    } catch (error) {
      console.warn('获取用户ID失败，使用默认值0:', error)
    }
    
    // 调用审核接口
    const response = await request.post('/audit/auditNewTemplate', {
      auditorId: auditorId,
      auditResult: 0, // 1=通过，0=拒绝
      note: '拒绝审核',
      templateId: template.id
    })
    
    if (response.data?.code === 1) {
      ElMessage.success('已拒绝')
      loadTemplates()
    } else {
      ElMessage.error(response.data?.message || '操作失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('拒绝失败:', error)
      ElMessage.error(error.response?.data?.message || '操作失败')
    }
  }
}

const revokeApproval = async (template) => {
  try {
    await ElMessageBox.confirm('确定要撤销该模版的审核状态吗？', '提示', { type: 'warning' })
    await request.post(`/tplmanage/templates/revoke/${template.id}`)
    ElMessage.success('已撤销')
    loadTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const reApprove = (template) => {
  currentReviewTemplate.value = template
  reviewComment.value = ''
  reviewDialogVisible.value = true
}

const viewTemplateDetail = (template) => {
  router.push(`/tplmanage/edit/${template.id}`)
}

// 查看模板字段详情（已通过模板使用）
const viewTemplateFields = (template) => {
  // 跳转到详情页面
  router.push({
    path: `/tplmanage/detail/${template.id}`,
    query: {
      category: currentCategory.value?.id || ''
    }
  })
}

const editTemplateFields = (template) => {
  router.push(`/tplmanage/field-edit/${template.id}`)
}

const formatDate = (date) => {
  if (!date) return '未知'
  return date.split(' ')[0]
}

// 字段类别名称映射
const getFieldCategoryName = (category) => {
  const categoryMap = {
    1: '对象字段',
    2: '操作字段',
    3: '结果字段'
  }
  return categoryMap[category] || '未知'
}

// 字段类别标签类型
const getFieldCategoryType = (category) => {
  const typeMap = {
    1: 'primary',
    2: 'success',
    3: 'warning'
  }
  return typeMap[category] || 'info'
}

// 数据类型名称映射 - 支持中文类型名和数字类型
const getDataTypeName = (dataType) => {
  // 如果已经是中文类型名，直接返回
  if (typeof dataType === 'string') {
    return dataType
  }
  // 兼容旧的数字类型
  const dataTypeMap = {
    0: '字符串',
    1: '整数',
    2: '浮点数',
    3: '日期',
    4: '布尔值',
    5: '文件'
  }
  return dataTypeMap[dataType] || '未知'
}

onMounted(() => {
  // 页面加载时自动加载模板，默认选择"所有模版"
  if (activeTab.value === 'pending') {
    // 默认选择"所有模版"分类
    currentCategory.value = {
      id: 'all_pending',
      name: '所有模版',
      description: '显示所有模版',
      hasChildren: false
    }
    // 等待 DOM 更新后设置树组件选中状态
    nextTick(() => {
      if (treeRef.value) {
        treeRef.value.setCurrentKey('all_pending')
      }
    })
    loadTemplates()
  }
})
</script>

<style lang="scss" scoped>
.tpl-audit {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f4f8 0%, #f8fafc 100%);
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
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
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

// 侧边栏
.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e5e7eb;
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
    color: #f59e0b;
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
}

.category-tree {
  background: transparent;
  
  :deep(.el-tree-node__content) {
    height: 40px;
    border-radius: 8px;
    
    &:hover {
      background: #fef3c7;
    }
  }
  
  :deep(.el-tree-node.is-current > .el-tree-node__content) {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(249, 115, 22, 0.1));
    color: #f59e0b;
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

.content-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.page-desc {
  color: #64748b;
}

.search-section {
  margin-bottom: 24px;
}

.search-input {
  max-width: 400px;
  
  :deep(.el-input__wrapper) {
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }
}

// 审核状态切换
.audit-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 24px;
  }
  
  :deep(.el-tabs__item) {
    font-size: 1rem;
    font-weight: 500;
  }
}

// 模版卡片
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.template-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
  }
  
  &.pending {
    border-left: 5px solid #f59e0b;
    
    &:hover {
      box-shadow: 0 12px 40px rgba(245, 158, 11, 0.15);
    }
  }
  
  &.approved {
    border-left: 5px solid #10b981;
    
    &:hover {
      box-shadow: 0 12px 40px rgba(16, 185, 129, 0.15);
    }
  }
  
  &.rejected {
    border-left: 5px solid #ef4444;
    
    &:hover {
      box-shadow: 0 12px 40px rgba(239, 68, 68, 0.15);
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.card-body {
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 10px;
}

.description {
  font-size: 0.875rem;
  color: #94a3b8;
  margin-top: 14px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

// 审核对话框
.review-content {
  padding: 0 8px;
}

.review-info {
  margin-bottom: 24px;
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
}

.info-row {
  display: flex;
  margin-bottom: 12px;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  .label {
    width: 100px;
    color: #64748b;
    flex-shrink: 0;
    font-size: 0.9375rem;
  }
  
  .value {
    color: #1e293b;
    font-size: 0.9375rem;
    font-weight: 500;
  }
}

// 字段信息展示
.fields-section {
  margin: 24px 0;
  
  .fields-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid #f59e0b;
    display: inline-block;
  }
}

.no-fields {
  margin: 24px 0;
  padding: 24px;
  background: #f8fafc;
  border-radius: 12px;
}

.review-actions {
  margin-top: 20px;
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
  
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .page-banner {
    padding: 24px 20px;
    margin: 0 -16px 20px;
    border-radius: 0;
  }
  
  .banner-content {
    flex-direction: column;
    text-align: center;
  }
  
  .banner-info {
    .page-title {
      font-size: 1.5rem;
    }
  }
}

// 审核对话框美化样式
.review-dialog {
  .el-dialog__body {
    padding: 20px 24px;
  }
}

.review-content {
  .info-card,
  .fields-card,
  .comment-card {
    background: #f8fafc;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  .info-card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid #667eea;
    
    .el-icon {
      color: #667eea;
    }
  }
  
  .info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    
    .info-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
      
      &.full-width {
        grid-column: 1 / -1;
      }
      
      .info-label {
        font-size: 0.8125rem;
        color: #64748b;
      }
      
      .info-value {
        font-size: 0.9375rem;
        color: #1e293b;
        font-weight: 500;
      }
    }
  }
  
  .field-section {
    margin-bottom: 20px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .section-header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 16px;
      border-radius: 8px;
      margin-bottom: 12px;
      font-weight: 500;
      
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
    
    .field-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding-left: 16px;
    }
    
    .field-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 16px;
      background: white;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
      
      .field-name {
        font-size: 0.875rem;
        color: #334155;
      }
    }
    
    .enum-group {
      background: white;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
      overflow: hidden;
      
      .enum-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 16px;
        background: linear-gradient(135deg, rgba(236, 72, 153, 0.05), rgba(236, 72, 153, 0.1));
        border-bottom: 1px solid #fce7f3;
        
        .enum-name {
          font-size: 0.875rem;
          font-weight: 600;
          color: #be185d;
        }
      }
      
      .enum-options {
        padding: 12px 16px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        
        .el-tag {
          background: #fdf2f8;
          border-color: #fbcfe8;
          color: #be185d;
        }
      }
    }
  }
  
  .no-fields {
    margin: 0;
    padding: 24px;
    background: #f8fafc;
    border-radius: 12px;
  }
}
</style>
