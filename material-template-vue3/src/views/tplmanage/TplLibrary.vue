<template>
  <div class="tpl-library">
    <Navbar />
    
    <div class="page-container">
      <!-- 侧边栏 -->
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-header">
          <h3 class="sidebar-title" v-show="!sidebarCollapsed">模版分类</h3>
          <el-button 
            class="collapse-btn" 
            :icon="sidebarCollapsed ? Expand : Fold" 
            text 
            @click="toggleSidebar"
          />
        </div>
        
        <div class="sidebar-content">
          <el-tree
            ref="treeRef"
            :data="categoryTree"
            :props="{ children: 'children', label: 'name' }"
            node-key="id"
            :default-expanded-keys="expandedKeys"
            highlight-current
            @node-click="handleCategoryClick"
            class="category-tree"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <el-icon v-if="data.children">
                  <Folder v-if="!node.expanded" />
                  <FolderOpened v-else />
                </el-icon>
                <el-icon v-else><Document /></el-icon>
                <span class="node-label">{{ node.label }}</span>
                <span v-if="data.count" class="node-count">{{ data.count }}</span>
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
              <el-icon :size="36"><Files /></el-icon>
            </div>
            <div class="banner-info">
              <h1 class="page-title">{{ currentCategory?.name || '模版库' }}</h1>
              <p class="page-desc">
                {{ currentCategory?.description || '浏览所有已发布的数据模版' }}
              </p>
            </div>
            <div class="banner-actions">
              <el-button type="primary" size="large" :icon="Plus" @click="goToCreate">
                创建模版
              </el-button>
            </div>
          </div>
        </div>

        <!-- 搜索和筛选 -->
        <div class="filter-section animate-slide-up delay-1">
          <div class="search-box">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索模版名称..."
              :prefix-icon="Search"
              size="large"
              clearable
              @input="handleSearch"
            />
          </div>
          <div class="filter-actions">
            <el-button :icon="Refresh" @click="handleRefresh">刷新</el-button>
          </div>
        </div>

        <!-- 模版卡片列表 -->
        <div class="template-grid" v-loading="loading">
          <div
            v-for="(template, index) in displayedTemplates"
            :key="template.id"
            class="template-card"
            :style="{ animationDelay: `${index * 0.03}s` }"
            @click="viewTemplate(template)"
          >
              <div class="card-header">
                <div class="card-icon" :style="{ background: getGradient(index) }">
                  <el-icon :size="24"><Document /></el-icon>
                </div>
                <el-tag :type="getStatusType(template.state)" size="small" effect="light">
                  {{ getStatusText(template.state) }}
                </el-tag>
              </div>
              
              <div class="card-body">
                <h3 class="card-title">{{ template.name }}</h3>
                <p class="card-desc">{{ template.description || '暂无描述' }}</p>
              </div>
              
              <div class="card-footer">
                <div class="card-meta">
                  <span class="meta-item">
                    <el-icon><User /></el-icon>
                    {{ template.creator || '未知' }}
                  </span>
                  <span class="meta-item">
                    <el-icon><Calendar /></el-icon>
                    {{ formatDate(template.createTime) }}
                  </span>
                </div>
                <div class="card-actions">
                  <el-button type="primary" text size="small" @click.stop="viewTemplate(template)">
                    查看详情
                    <el-icon class="arrow"><ArrowRight /></el-icon>
                  </el-button>
                </div>
              </div>
          </div>
          
          <!-- 空状态 -->
          <el-empty 
            v-if="!loading && displayedTemplates.length === 0" 
            description="暂无模版"
            :image-size="150"
          >
            <el-button type="primary" @click="goToCreate">创建第一个模版</el-button>
          </el-empty>
        </div>

        <!-- 分页 -->
        <div class="pagination-section" v-if="total > 0">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[12, 24, 48, 96]"
            layout="total, sizes, prev, pager, next, jumper"
            background
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Plus, Search, Refresh, Document, Folder, FolderOpened,
  User, Calendar, ArrowRight, Expand, Fold, Files
} from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'
import { getCategoryTree, defaultExpandedKeys, findCategoryById, getNumericCategoryId } from '@/utils/templateCategories'

const router = useRouter()
const route = useRoute()

// 状态
const loading = ref(false)
const sidebarCollapsed = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

// 数据 - 使用统一的分类配置
const categoryTree = ref(getCategoryTree())

const expandedKeys = ref([...defaultExpandedKeys])
const currentCategory = ref(null)

const templates = ref([])

// 计算属性
const displayedTemplates = computed(() => {
  let result = [...templates.value]
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(t => 
      (t.name || '').toLowerCase().includes(keyword) ||
      (t.description || '').toLowerCase().includes(keyword)
    )
  }
  
  return result
})

// 方法
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleCategoryClick = (data) => {
  console.log('点击分类:', data.id, '数字ID:', getNumericCategoryId(data.id))
  templates.value = []
  total.value = 0
  currentCategory.value = data
  loadTemplates()
}

const loadTemplates = async () => {
  loading.value = true
  try {
    if (currentCategory.value?.id) {
      const numericId = getNumericCategoryId(currentCategory.value.id)
      if (!numericId) {
        templates.value = []
        total.value = 0
        loading.value = false
        return
      }
      console.log('请求接口:', `/template/getTemplateByCategory/${numericId}`)
      const response = await request.get(`/template/getTemplateByCategory/${numericId}`)
      console.log('接口响应:', response)
      if (response.data?.code === 1 || response.data?.code === 0) {
        // 只显示已发布的模板（state === 1）
        const allTemplates = response.data.data || []
        templates.value = allTemplates.filter(t => t.state === 1)
        total.value = templates.value.length
      } else {
        templates.value = []
        total.value = 0
      }
    } else {
      templates.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('加载模板失败:', error)
    templates.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleRefresh = () => {
  loadTemplates()
  ElMessage.success('刷新成功')
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handlePageChange = () => {
  // 分页处理
}

const viewTemplate = (template) => {
  // 跳转到详情页面
  router.push({
    path: `/tplmanage/detail/${template.id}`,
    query: {
      category: currentCategory.value?.id || ''
    }
  })
}

const goToCreate = () => {
  router.push('/tplmanage/create')
}

const getGradient = (index) => {
  const gradients = [
    'linear-gradient(135deg, #667eea, #764ba2)',
    'linear-gradient(135deg, #10b981, #34d399)',
    'linear-gradient(135deg, #f59e0b, #fbbf24)',
    'linear-gradient(135deg, #06b6d4, #22d3ee)',
    'linear-gradient(135deg, #ec4899, #f472b6)',
    'linear-gradient(135deg, #8b5cf6, #a78bfa)'
  ]
  return gradients[index % gradients.length]
}

const getStatusType = (state) => {
  const types = { 0: 'info', 1: 'success', 2: 'warning' }
  return types[state] || 'info'
}

const getStatusText = (state) => {
  const texts = { 0: '草稿', 1: '已发布', 2: '审核中' }
  return texts[state] || '未知'
}

const formatDate = (date) => {
  if (!date) return '未知'
  return date.split(' ')[0]
}

onMounted(() => {
  const categoryId = route.query.category
  if (categoryId) {
    const category = findCategoryById(categoryId)
    if (category) {
      currentCategory.value = category
      if (category.parentId) {
        expandedKeys.value = [...new Set([...expandedKeys.value, category.parentId])]
      }
      loadTemplates()
    }
  } else {
    templates.value = []
    total.value = 0
  }
})
</script>

<style lang="scss" scoped>
.tpl-library {
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    color: rgba(255, 255, 255, 0.85);
    font-size: 0.9375rem;
    margin: 0;
  }
}

.banner-actions {
  flex-shrink: 0;
  
  .el-button {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(10px);
    
    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  }
}

// 侧边栏
.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  
  &.collapsed {
    width: 60px;
    
    .sidebar-content {
      display: none;
    }
  }
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 16px;
  border-bottom: 1px solid #f1f5f9;
}

.sidebar-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.category-tree {
  background: transparent;
  
  :deep(.el-tree-node__content) {
    height: 40px;
    border-radius: 8px;
    
    &:hover {
      background: #f1f5f9;
    }
  }
  
  :deep(.el-tree-node.is-current > .el-tree-node__content) {
    background: linear-gradient(135deg, #667eea15, #764ba215);
    color: #667eea;
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

.node-count {
  background: #f1f5f9;
  color: #64748b;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
}

// 主内容区
.main-content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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
  font-size: 0.9375rem;
}

.filter-section {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.search-box {
  flex: 1;
  max-width: 400px;
}

// 模版卡片网格
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  min-height: 200px;
}

.template-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.card-body {
  margin-bottom: 16px;
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
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

.card-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8125rem;
  color: #94a3b8;
}

.card-actions .arrow {
  transition: transform 0.3s ease;
}

.template-card:hover .arrow {
  transform: translateX(4px);
}

// 分页
.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

// 抽屉
.drawer-content {
  padding: 0 8px;
}

.detail-section {
  margin-bottom: 24px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  .label {
    display: block;
    font-size: 0.8125rem;
    color: #94a3b8;
    margin-bottom: 4px;
  }
  
  .value {
    font-size: 0.9375rem;
    color: #1e293b;
  }
}

.description {
  font-size: 0.9375rem;
  color: #475569;
  line-height: 1.6;
}

// 字段列表样式
.section-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
  
  .el-icon {
    color: #667eea;
  }
}

.fields-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 3px;
    
    &:hover {
      background: #94a3b8;
    }
  }
}

.field-item {
  display: flex;
  gap: 12px;
  padding: 14px 16px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
  
  &:hover {
    background: #f1f5f9;
    border-color: #667eea40;
  }
}

.field-index {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.field-info {
  flex: 1;
  min-width: 0;
}

.field-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9375rem;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 6px;
}

.field-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 0.8125rem;
  color: #64748b;
  
  .field-key {
    color: #667eea;
  }
  
  .field-type {
    color: #94a3b8;
  }
}

.field-desc {
  margin-top: 6px;
  font-size: 0.8125rem;
  color: #94a3b8;
  line-height: 1.4;
}

.drawer-actions {
  margin-top: 32px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

// 动画
.animate-slide-up {
  animation: slideUp 0.5s ease-out;
  
  &.delay-1 { animation-delay: 0.1s; }
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
  .sidebar {
    position: fixed;
    left: 0;
    top: 64px;
    bottom: 0;
    z-index: 100;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .template-grid {
    grid-template-columns: 1fr;
  }
}
</style>
