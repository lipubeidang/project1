<template>
  <div class="template-audit">
    <Navbar />
    
    <div class="page-container">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h3>模板分类</h3>
        </div>
        <div class="sidebar-content">
          <el-tree
            ref="treeRef"
            :data="categoryTree"
            :props="{ children: 'children', label: 'name' }"
            node-key="id"
            :default-expanded-keys="['big_cat_1']"
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
        <!-- 页面标题 -->
        <div class="content-header animate-slide-up">
          <div class="header-info">
            <h1 class="page-title">模板审核</h1>
            <p class="page-desc" v-if="currentCategory">
              当前目录：{{ currentCategory.name }}
            </p>
            <p class="page-desc" v-else>请从左侧选择目录查看模板</p>
          </div>
        </div>

        <!-- 搜索栏 -->
        <div class="search-section animate-slide-up delay-1">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索模板名称..."
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
                <!-- 优化性能：保持v-if用于条件渲染 -->
                <div class="templates-grid" v-if="pendingTemplates.length > 0">
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
                        审核模板
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
                <el-empty v-else-if="!loading" description="暂无待审核的模板" :image-size="120" />
                <!-- 分页 -->
                <div v-if="filteredPendingTemplates.length > pageSize" class="pagination-wrap">
                  <el-pagination
                    v-model:current-page="pendingPage"
                    :page-size="pageSize"
                    :total="filteredPendingTemplates.length"
                    layout="prev, pager, next"
                    background
                    small
                  />
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="已通过" name="approved">
              <div class="templates-section" v-loading="loading">
                <!-- 优化性能：保持v-if用于条件渲染 -->
                <div class="templates-grid" v-if="approvedTemplates.length > 0">
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
                      <el-button type="primary" size="small" @click="viewTemplateDetail(template)">
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
                <el-empty v-else-if="!loading" description="暂无已通过的模板" :image-size="120" />
                <!-- 分页 -->
                <div v-if="filteredApprovedTemplates.length > pageSize" class="pagination-wrap">
                  <el-pagination
                    v-model:current-page="approvedPage"
                    :page-size="pageSize"
                    :total="filteredApprovedTemplates.length"
                    layout="prev, pager, next"
                    background
                    small
                  />
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="已拒绝" name="rejected">
              <div class="templates-section" v-loading="loading">
                <!-- 优化性能：保持v-if用于条件渲染 -->
                <div class="templates-grid" v-if="rejectedTemplates.length > 0">
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
                <el-empty v-else-if="!loading" description="暂无已拒绝的模板" :image-size="120" />
                <!-- 分页 -->
                <div v-if="filteredRejectedTemplates.length > pageSize" class="pagination-wrap">
                  <el-pagination
                    v-model:current-page="rejectedPage"
                    :page-size="pageSize"
                    :total="filteredRejectedTemplates.length"
                    layout="prev, pager, next"
                    background
                    small
                  />
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </main>
    </div>

    <!-- 审核详情对话框 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="`审核模板: ${currentReviewTemplate?.name || ''}`"
      width="800px"
      top="5vh"
    >
      <div class="review-content" v-if="currentReviewTemplate" v-loading="loadingFields">
        <div class="review-info">
          <div class="info-row">
            <span class="label">模板名称：</span>
            <span class="value">{{ currentReviewTemplate.name }}</span>
          </div>
          <div class="info-row">
            <span class="label">创建者：</span>
            <span class="value">{{ currentReviewTemplate.creator || '未知' }}</span>
          </div>
          <div class="info-row">
            <span class="label">创建时间：</span>
            <span class="value">{{ formatDate(currentReviewTemplate.createTime) }}</span>
          </div>
          <div class="info-row">
            <span class="label">描述：</span>
            <span class="value">{{ currentReviewTemplate.description || '暂无' }}</span>
          </div>
        </div>
        
        <!-- 字段信息展示 -->
        <div class="fields-preview">
          <h4 class="fields-title">模板字段配置</h4>
          <div class="fields-grid">
            <!-- 对象字段 -->
            <div class="field-section">
              <div class="section-header object">
                <span>对象字段</span>
                <el-tag size="small">{{ templateFields.object.length }} 个</el-tag>
              </div>
              <div class="section-body">
                <div v-for="(field, idx) in templateFields.object" :key="idx" class="field-item">
                  <span class="field-name">{{ field.columnName }}</span>
                  <el-tag size="small" type="info">{{ field.columnContribution }}</el-tag>
                </div>
                <div v-if="templateFields.object.length === 0" class="no-fields">暂无字段</div>
              </div>
            </div>
            <!-- 操作字段 -->
            <div class="field-section">
              <div class="section-header operation">
                <span>操作字段</span>
                <el-tag size="small">{{ templateFields.operation.length }} 个</el-tag>
              </div>
              <div class="section-body">
                <div v-for="(field, idx) in templateFields.operation" :key="idx" class="field-item">
                  <span class="field-name">{{ field.columnName }}</span>
                  <el-tag size="small" type="info">{{ field.columnContribution }}</el-tag>
                </div>
                <div v-if="templateFields.operation.length === 0" class="no-fields">暂无字段</div>
              </div>
            </div>
            <!-- 结果字段 -->
            <div class="field-section">
              <div class="section-header result">
                <span>结果字段</span>
                <el-tag size="small">{{ templateFields.result.length }} 个</el-tag>
              </div>
              <div class="section-body">
                <div v-for="(field, idx) in templateFields.result" :key="idx" class="field-item">
                  <span class="field-name">{{ field.columnName }}</span>
                  <el-tag size="small" type="info">{{ field.columnContribution }}</el-tag>
                </div>
                <div v-if="templateFields.result.length === 0" class="no-fields">暂无字段</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="review-actions">
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Folder, Document, User, Calendar, Search } from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'

const router = useRouter()

// 状态
const loading = ref(false)
const loadingFields = ref(false)
const activeTab = ref('pending')
const currentCategory = ref(null)
const reviewDialogVisible = ref(false)
const currentReviewTemplate = ref(null)
const reviewComment = ref('')
const searchKeyword = ref('')

// 模板字段数据
const templateFields = ref({
  object: [],
  operation: [],
  result: []
})

// 分页变量
const pageSize = 12
const pendingPage = ref(1)
const approvedPage = ref(1)
const rejectedPage = ref(1)

// 模板数据
const pendingTemplates = ref([])
const approvedTemplates = ref([])
const rejectedTemplates = ref([])

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

// 过滤后的模板数量
const filteredPendingTemplates = computed(() => filterByKeyword(pendingTemplates.value))
const filteredApprovedTemplates = computed(() => filterByKeyword(approvedTemplates.value))
const filteredRejectedTemplates = computed(() => filterByKeyword(rejectedTemplates.value))

// 分页计算属性 - 优化：使用浅响应式，减少深度监听
const displayedPendingTemplates = computed(() => {
  const start = (pendingPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredPendingTemplates.value.slice(start, end)
})

const displayedApprovedTemplates = computed(() => {
  const start = (approvedPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredApprovedTemplates.value.slice(start, end)
})

const displayedRejectedTemplates = computed(() => {
  const start = (rejectedPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredRejectedTemplates.value.slice(start, end)
})

// 目录结构
const categoryTree = ref([
  {
    id: 'big_cat_1',
    name: '材料属性',
    children: [
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
    ]
  },
  {
    id: 'big_cat_2',
    name: '数据来源',
    children: [
      { id: 11, name: '文献' },
      { id: 12, name: '计算' },
      { id: 13, name: '实验' },
      { id: 14, name: '研发生产' },
      { id: 15, name: '临床应用' },
      { id: 16, name: '其他数据来源' }
    ]
  },
  {
    id: 'big_cat_3',
    name: '材料功能',
    children: [
      { id: 17, name: '骨科材料' },
      { id: 18, name: '心血管材料' },
      { id: 19, name: '牙科材料' },
      { id: 20, name: '其他材料功能' }
    ]
  }
])

// 防抖计时器
let loadDebounceTimer = null

// 加载模板数据（带防抖）- 优化：只加载当前tab的数据
const loadTemplates = async (parentId = null) => {
  // 如果没有选择具体的子分类，不发起请求
  if (!parentId || typeof parentId !== 'number') {
    pendingTemplates.value = []
    approvedTemplates.value = []
    rejectedTemplates.value = []
    return
  }
  
  // 防抖：取消之前的请求
  if (loadDebounceTimer) {
    clearTimeout(loadDebounceTimer)
  }
  
  loadDebounceTimer = setTimeout(async () => {
    loading.value = true
    try {
      // 只加载当前激活的tab数据
      if (activeTab.value === 'pending') {
        await loadPendingTemplates(parentId)
      } else if (activeTab.value === 'approved') {
        await loadApprovedTemplates(parentId)
      }
      // rejected tab 不主动加载，因为是本地数据
    } catch (error) {
      console.error('加载模板失败:', error)
    } finally {
      loading.value = false
    }
  }, 150) // 减少防抖时间
}

// 待审核模板缓存 - 优化缓存策略
let pendingTemplatesCache = null
let pendingCacheTime = 0
let pendingCategoryId = null
const CACHE_DURATION = 60000 // 增加到60秒缓存

// 加载待审核模板（优化缓存策略）
const loadPendingTemplates = async (parentId = null) => {
  try {
    const now = Date.now()
    
    // 如果缓存有效且分类相同，直接使用缓存数据
    if (pendingTemplatesCache && 
        pendingCategoryId === parentId &&
        (now - pendingCacheTime) < CACHE_DURATION) {
      pendingTemplates.value = pendingTemplatesCache
      return
    }
    
    const response = await request.get('/basemodule/process/list')
    if (response.data?.code === 0) {
      let templates = response.data.data || []
      
      // 在API层面就过滤，减少前端处理
      if (parentId) {
        templates = templates.filter(t => t.parent === parentId || t.parentId === parentId)
      }
      
      // 更新缓存
      pendingTemplatesCache = templates
      pendingCacheTime = now
      pendingCategoryId = parentId
      
      pendingTemplates.value = templates
    }
  } catch (error) {
    console.error('加载待审核模板失败:', error)
    pendingTemplates.value = []
  }
}

// 加载已通过模板
const loadApprovedTemplates = async (parentId = null) => {
  try {
    if (parentId) {
      const response = await request.get(`/basemodule/module/getmodules/${parentId}`)
      if (response.data?.code === 0) {
        approvedTemplates.value = (response.data.module_list || []).filter(t => t.state === 1)
      }
    } else {
      approvedTemplates.value = []
    }
  } catch (error) {
    console.error('加载已通过模板失败:', error)
    approvedTemplates.value = []
  }
}

// 目录点击
const handleCategoryClick = (data) => {
  // 如果是大类，不加载
  if (data.children) {
    return
  }
  currentCategory.value = data
  loadTemplates(data.id)
}

// 标签切换 - 优化：切换时加载对应数据
const handleTabChange = (tabName) => {
  if (!currentCategory.value) return
  
  // 根据tab加载对应数据
  if (tabName === 'pending' && pendingTemplates.value.length === 0) {
    loadPendingTemplates(currentCategory.value.id)
  } else if (tabName === 'approved' && approvedTemplates.value.length === 0) {
    loadApprovedTemplates(currentCategory.value.id)
  }
}

// 审核模板 - 优化：延迟加载字段详情
const reviewTemplate = async (template) => {
  currentReviewTemplate.value = template
  reviewComment.value = ''
  templateFields.value = { object: [], operation: [], result: [] }
  reviewDialogVisible.value = true
  
  // 使用 requestAnimationFrame 延迟加载，让对话框先渲染
  requestAnimationFrame(() => {
    loadTemplateFields(template.id)
  })
}

// 单独的字段加载函数
const loadTemplateFields = async (templateId) => {
  loadingFields.value = true
  try {
    // 待审核模板使用 process/detail 接口
    const response = await request.get(`/basemodule/process/detail/${templateId}`)
    if (response.data?.code === 0) {
      const data = response.data.data || {}
      templateFields.value = {
        object: data.object || [],
        operation: data.operation || [],
        result: data.result || []
      }
    }
  } catch (error) {
    console.error('加载模板字段失败:', error)
    ElMessage.error('加载模板字段信息失败')
  } finally {
    loadingFields.value = false
  }
}

// 通过审核 - 优化性能
const handleApprove = async () => {
  if (!currentReviewTemplate.value) return
  
  const template = currentReviewTemplate.value
  
  try {
    // 验证字段信息是否加载完成
    if (!templateFields.value.object && !templateFields.value.operation && !templateFields.value.result) {
      ElMessage.warning('请等待字段信息加载完成')
      return
    }
    
    // 构建审核通过的请求参数
    const requestData = {
      moduleId: template.id,
      name: template.name ? template.name.toLowerCase().replace(/\s+/g, '_') : 'template',
      columns: {
        object: templateFields.value.object || [],
        operation: templateFields.value.operation || [],
        result: templateFields.value.result || []
      }
    }
    
    console.log('审核通过请求参数:', requestData)
    
    // 调用创建表的接口
    const response = await request.post('/basemodule/process/createtable', requestData)
    
    if (response.data?.code === 0) {
      ElMessage.success('审核通过成功')
      reviewDialogVisible.value = false
      
      // 清除缓存
      clearPendingCache()
      
      // 从待审核列表移除（使用过滤而非splice，性能更好）
      pendingTemplates.value = pendingTemplates.value.filter(t => t.id !== template.id)
      
      // 只在当前是approved tab时才重新加载
      if (activeTab.value === 'approved' && currentCategory.value) {
        loadApprovedTemplates(currentCategory.value.id)
      }
    } else {
      throw new Error(response.data?.msg || '审核失败')
    }
  } catch (error) {
    console.error('审核失败:', error)
    ElMessage.error(error.message || '审核操作失败')
  }
}

// 拒绝审核 - 优化性能
const handleReject = async () => {
  if (!currentReviewTemplate.value) return
  
  const templateId = currentReviewTemplate.value.id
  const template = currentReviewTemplate.value
  
  try {
    const response = await request.post('/basemodule/process/reject', {
      id: templateId,
      comment: reviewComment.value
    })
    
    if (response.data?.code === 0) {
      ElMessage.success('已拒绝该模板')
      reviewDialogVisible.value = false
      
      // 清除缓存
      clearPendingCache()
      
      // 从待审核列表移除并添加到已拒绝列表
      pendingTemplates.value = pendingTemplates.value.filter(t => t.id !== templateId)
      rejectedTemplates.value.unshift(template) // 使用unshift添加到开头
    }
  } catch (error) {
    console.error('拒绝失败:', error)
    ElMessage.error('拒绝操作失败')
  }
}

// 直接拒绝（不弹窗）- 优化：应该也调用API
const rejectTemplate = async (template) => {
  try {
    await ElMessageBox.confirm('确定要拒绝这个模板吗？', '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 调用API接口
    const response = await request.post('/basemodule/process/reject', {
      id: template.id,
      comment: '快速拒绝'
    })
    
    if (response.data?.code === 0) {
      // 清除缓存
      clearPendingCache()
      
      // 从待审核列表移除并添加到已拒绝列表
      pendingTemplates.value = pendingTemplates.value.filter(t => t.id !== template.id)
      rejectedTemplates.value.unshift(template)
      ElMessage.success('已拒绝该模板')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('拒绝失败:', error)
      ElMessage.error('拒绝操作失败')
    }
  }
}

// 撤销审核
const revokeApproval = async (template) => {
  try {
    await ElMessageBox.confirm('确定要撤销这个模板的审核吗？', '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const index = approvedTemplates.value.findIndex(t => t.id === template.id)
    if (index !== -1) {
      approvedTemplates.value.splice(index, 1)
    }
    
    if (currentCategory.value) {
      loadPendingTemplates(currentCategory.value.id)
    }
    ElMessage.success('已撤销审核')
  } catch {
    // 用户取消
  }
}

// 重新审核
const reApprove = (template) => {
  currentReviewTemplate.value = template
  reviewComment.value = ''
  reviewDialogVisible.value = true
}

// 查看详情
const viewTemplateDetail = (template) => {
  router.push({
    path: `/template/detail/${template.id}`,
    query: { name: template.name }
  })
}

// 修改模板字段
const editTemplateFields = (template) => {
  router.push({
    path: `/template/field-edit/${template.id}`,
    query: { templateName: template.name }
  })
}

// 格式化日期 - 优化：使用缓存避免重复计算
const dateCache = new Map()
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  
  // 使用缓存
  if (dateCache.has(dateString)) {
    return dateCache.get(dateString)
  }
  
  try {
    const formatted = new Date(dateString).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
    dateCache.set(dateString, formatted)
    return formatted
  } catch {
    return dateString
  }
}

// 优化清除缓存的函数（只清除时间戳，保留数据供下次对比）
const clearPendingCache = () => {
  pendingCacheTime = 0 // 只重置时间，下次加载会刷新
}

onMounted(() => {
  // 初始化时不加载数据，等待用户选择分类后再加载
  // 避免不必要的API请求，提升页面响应速度
})

// 组件卸载时清理
onUnmounted(() => {
  if (loadDebounceTimer) {
    clearTimeout(loadDebounceTimer)
  }
})
</script>

<style lang="scss" scoped>
.template-audit {
  min-height: 100vh;
  background: #f1f5f9;
}

.page-container {
  display: flex;
  padding-top: 72px;
  min-height: 100vh;
}

// 侧边栏
.sidebar {
  width: 280px;
  background: white;
  margin: 20px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.sidebar-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  
  h3 {
    font-size: 16px;
    font-weight: 600;
    color: #1e293b;
  }
}

.sidebar-content {
  padding: 16px;
  max-height: calc(100vh - 180px);
  overflow-y: auto;
}

.category-tree {
  background: transparent;
  
  :deep(.el-tree-node__content) {
    height: 40px;
    border-radius: 8px;
    margin: 2px 0;
    
    &:hover {
      background: rgba(102, 126, 234, 0.1);
    }
  }
  
  :deep(.el-tree-node.is-current > .el-tree-node__content) {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
    color: #667eea;
  }
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .el-icon {
    color: #667eea;
  }
  
  .node-label {
    font-size: 14px;
  }
}

// 主内容区
.main-content {
  flex: 1;
  padding: 20px;
  padding-right: 40px;
}

.content-header {
  background: white;
  border-radius: 16px;
  padding: 24px 32px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.page-desc {
  color: #64748b;
  font-size: 14px;
}

// 搜索区域
.search-section {
  margin-bottom: 20px;
  
  .search-input {
    max-width: 400px;
    
    :deep(.el-input__wrapper) {
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
      
      &:hover, &:focus-within {
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
      }
    }
  }
}

// 审核标签页
.audit-tabs {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  
  :deep(.el-tabs__header) {
    margin-bottom: 24px;
  }
}

.templates-section {
  min-height: 300px;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.template-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  transition: box-shadow 0.2s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.card-body {
  .info-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #64748b;
    margin-bottom: 8px;
    
    .el-icon {
      color: #94a3b8;
    }
  }
  
  .description {
    font-size: 13px;
    color: #94a3b8;
    line-height: 1.5;
    margin-top: 12px;
  }
}

.card-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

// 审核对话框
.review-content {
  .review-info {
    margin-bottom: 24px;
  }
  
  .info-row {
    display: flex;
    padding: 12px 0;
    border-bottom: 1px solid #f1f5f9;
    
    .label {
      width: 100px;
      color: #64748b;
      flex-shrink: 0;
    }
    
    .value {
      color: #1e293b;
    }
  }
}

// 字段预览
.fields-preview {
  margin: 24px 0;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.fields-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.fields-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.field-section {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.section-header {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 14px;
  
  &.object {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
  }
  
  &.operation {
    background: linear-gradient(135deg, #10b981, #34d399);
    color: white;
  }
  
  &.result {
    background: linear-gradient(135deg, #f59e0b, #fbbf24);
    color: white;
  }
}

.section-body {
  padding: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.field-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
  margin-bottom: 8px;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  .field-name {
    font-size: 13px;
    color: #334155;
  }
}

.no-fields {
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
  padding: 20px 0;
}

// 分页样式
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

// 简化动画 - 移除复杂动画提升性能
.animate-slide-up {
  opacity: 1;
}

.delay-1 {
  opacity: 1;
}
</style>
