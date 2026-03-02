<template>
  <div class="template-library">
    <Navbar />
    
    <div class="page-container">
      <!-- 侧边栏 -->
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-header">
          <h3 class="sidebar-title" v-show="!sidebarCollapsed">数据资源分类</h3>
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
        <!-- 面包屑导航 -->
        <div class="breadcrumb-nav" v-if="breadcrumbs.length > 0">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item 
              v-for="(crumb, index) in breadcrumbs" 
              :key="index"
              @click="handleBreadcrumbClick(crumb, index)"
            >
              <span :class="{ 'crumb-link': index < breadcrumbs.length - 1 }">
                {{ crumb.name }}
              </span>
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <!-- 页面标题 -->
        <div class="content-header animate-slide-up">
          <div class="header-info">
            <h1 class="page-title">{{ pageTitle }}</h1>
            <p class="page-desc">{{ pageDescription }}</p>
          </div>
          <div class="header-actions">
            <el-button v-if="currentViewLevel === 'templates'" type="primary" :icon="Plus" @click="goToCreate">
              创建数据集
            </el-button>
            <el-button v-if="currentViewLevel !== 'categories'" :icon="Back" @click="goBack">
              返回上一级
            </el-button>
          </div>
        </div>

        <!-- 搜索和筛选 (仅在模板列表视图显示) -->
        <div class="filter-section animate-slide-up delay-1" v-if="currentViewLevel === 'templates'">
          <div class="search-box">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索数据资源名称..."
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

        <!-- 8个模版库目录模块 (大目录视图) -->
        <div class="module-grid" v-if="currentViewLevel === 'categories'" v-loading="loading">
          <div
            v-for="(category, index) in templateCategoriesData"
            :key="category.id"
            class="module-card"
            :style="{ animationDelay: `${index * 0.05}s` }"
            @click="handleCategoryModuleClick(category)"
          >
            <div class="module-icon" :style="{ background: getCategoryGradient(index) }">
              <el-icon :size="32"><component :is="category.iconComponent" /></el-icon>
            </div>
            <div class="module-info">
              <h3 class="module-title">{{ category.name }}</h3>
              <p class="module-desc">{{ category.description }}</p>
              <div class="module-meta">
                <span v-if="category.hasChildren" class="sub-count">
                  <el-icon><FolderOpened /></el-icon>
                  {{ category.children.length }} 个子目录
                </span>
                <span v-else class="no-sub">
                  <el-icon><Document /></el-icon>
                  直接包含模版
                </span>
              </div>
            </div>
            <div class="module-arrow">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>

        <!-- 子目录模块 (子目录视图) -->
        <div class="submodule-grid" v-if="currentViewLevel === 'subcategories'" v-loading="loading">
          <div
            v-for="(subcat, index) in currentSubcategories"
            :key="subcat.id"
            class="submodule-card"
            :style="{ animationDelay: `${index * 0.05}s` }"
            @click="handleSubcategoryClick(subcat)"
          >
            <div class="submodule-icon" :style="{ background: getSubcategoryGradient(index) }">
              <el-icon :size="28"><Document /></el-icon>
            </div>
            <div class="submodule-info">
              <h3 class="submodule-title">{{ subcat.name }}</h3>
            </div>
            <div class="submodule-arrow">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>

        <!-- 数据资源卡片列表 (模板列表视图) -->
        <div class="template-grid" v-if="currentViewLevel === 'templates'" v-loading="loading">
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
                <h3 class="card-title">{{ template.name || template.sample_serial }}</h3>
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
            description="暂无数据资源"
            :image-size="150"
          >
            <el-button type="primary" @click="goToCreate">创建第一个数据集</el-button>
          </el-empty>
        </div>

        <!-- 分页 -->
        <div class="pagination-section" v-if="currentViewLevel === 'templates' && total > 0">
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

    <!-- 模板详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="currentTemplate?.name"
      size="480px"
      direction="rtl"
    >
      <div class="drawer-content" v-if="currentTemplate">
        <div class="detail-section">
          <h4 class="section-label">基本信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">数据资源ID</span>
              <span class="value">{{ currentTemplate.id }}</span>
            </div>
            <div class="info-item">
              <span class="label">创建者</span>
              <span class="value">{{ currentTemplate.creator || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="label">创建时间</span>
              <span class="value">{{ currentTemplate.createTime || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="label">状态</span>
              <el-tag :type="getStatusType(currentTemplate.state)" size="small">
                {{ getStatusText(currentTemplate.state) }}
              </el-tag>
            </div>
          </div>
        </div>
        
        <div class="detail-section">
          <h4 class="section-label">数据资源描述</h4>
          <p class="description">{{ currentTemplate.description || '暂无描述信息' }}</p>
        </div>

        <div class="drawer-actions">
          <el-button type="primary" size="large" @click="goToDetail">
            查看完整详情
          </el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Plus, Search, Refresh, Document, Folder, FolderOpened,
  User, Calendar, ArrowRight, Expand, Fold, Back,
  Cpu, SetUp, DataLine, FirstAidKit, Aim, Checked
} from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'
import { templateCategories, getNumericCategoryId } from '@/utils/templateCategories'

const router = useRouter()

// 状态
const loading = ref(false)
const sidebarCollapsed = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
const drawerVisible = ref(false)

// 视图层级: 'categories' | 'subcategories' | 'templates'
const currentViewLevel = ref('categories')
const currentDataCategory = ref(null)  // 当前选中的数据资源分类（左侧树）
const currentBigCategory = ref(null)   // 当前选中的大目录（模版库8个目录）
const currentSubcategory = ref(null)   // 当前选中的子目录

// 图标映射
const iconMap = {
  'Document': Document,
  'Cpu': Cpu,
  'SetUp': SetUp,
  'DataLine': DataLine,
  'FirstAidKit': FirstAidKit,
  'Aim': Aim,
  'User': User,
  'Checked': Checked
}

// 模版库8个大目录数据（从templateCategories转换）
const templateCategoriesData = computed(() => {
  return templateCategories.map(cat => ({
    ...cat,
    iconComponent: markRaw(iconMap[cat.icon] || Document)
  }))
})

// 当前子目录列表
const currentSubcategories = computed(() => {
  if (currentBigCategory.value && currentBigCategory.value.children) {
    return currentBigCategory.value.children
  }
  return []
})

// 面包屑导航
const breadcrumbs = computed(() => {
  const crumbs = []
  if (currentDataCategory.value) {
    crumbs.push({ 
      name: currentDataCategory.value.name, 
      level: 'categories',
      data: currentDataCategory.value
    })
  }
  if (currentBigCategory.value) {
    crumbs.push({ 
      name: currentBigCategory.value.name, 
      level: currentBigCategory.value.hasChildren ? 'subcategories' : 'templates',
      data: currentBigCategory.value
    })
  }
  if (currentSubcategory.value) {
    crumbs.push({ 
      name: currentSubcategory.value.name, 
      level: 'templates',
      data: currentSubcategory.value
    })
  }
  return crumbs
})

// 页面标题
const pageTitle = computed(() => {
  if (currentViewLevel.value === 'templates') {
    if (currentSubcategory.value) {
      return currentSubcategory.value.name
    }
    if (currentBigCategory.value) {
      return currentBigCategory.value.name
    }
  }
  if (currentViewLevel.value === 'subcategories' && currentBigCategory.value) {
    return currentBigCategory.value.name + ' - 子目录'
  }
  if (currentDataCategory.value) {
    return currentDataCategory.value.name 
  }
  return '请选择数据资源分类'
})

// 页面描述
const pageDescription = computed(() => {
  if (currentViewLevel.value === 'categories') {
    if (currentDataCategory.value) {
      return '点击下方模块查看对应的模版资源'
    }
    return '请在左侧选择一个数据资源分类'
  }
  if (currentViewLevel.value === 'subcategories' && currentBigCategory.value) {
    return currentBigCategory.value.description || '选择子目录查看模版'
  }
  if (currentViewLevel.value === 'templates') {
    return '浏览和管理数据资源模版'
  }
  return ''
})

// 数据
const categoryTree = ref([
  {
    id: 'big_cat_1',
    name: '材料属性',
    children: [
      { id: 1, name: '医用金属材料', count: 0 },
      { id: 2, name: '医用无机材料', count: 0 },
      { id: 3, name: '医用高分子材料', count: 0 },
      { id: 4, name: '生物复合材料', count: 0 },
      { id: 5, name: '生物衍生材料', count: 0 },
      { id: 6, name: '医用纳米材料', count: 0 },
      { id: 7, name: '组织诱导性生物材料', count: 0 },
      { id: 8, name: '组织工程材料', count: 0 },
      { id: 9, name: '生物传感器材料', count: 0 },
      { id: 10, name: '其他材料属性', count: 0 }
    ]
  },
  {
    id: 'big_cat_2',
    name: '数据来源',
    children: [
      { id: 11, name: '文献', count: 0 },
      { id: 12, name: '计算', count: 0 },
      { id: 13, name: '实验', count: 0 },
      { id: 14, name: '研发生产', count: 0 },
      { id: 15, name: '临床应用', count: 0 },
      { id: 16, name: '其他数据来源', count: 0 }
    ]
  },
  {
    id: 'big_cat_3',
    name: '材料功能',
    children: [
      { id: 17, name: '骨科材料', count: 0 },
      { id: 18, name: '心血管材料', count: 0 },
      { id: 19, name: '牙科材料', count: 0 },
      { id: 20, name: '其他材料功能', count: 0 }
    ]
  }
])

const expandedKeys = ref(['big_cat_1'])
const currentCategory = ref(null)
const currentTemplate = ref(null)

const templates = ref([])

// 计算属性
const displayedTemplates = computed(() => {
  let result = [...templates.value]
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(t => 
      (t.name || t.sample_serial || '').toLowerCase().includes(keyword) ||
      (t.description || '').toLowerCase().includes(keyword)
    )
  }
  
  return result
})

// 方法
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 左侧树形目录点击
const handleCategoryClick = (data) => {
  currentDataCategory.value = data
  currentBigCategory.value = null
  currentSubcategory.value = null
  currentViewLevel.value = 'categories'
  templates.value = []
  total.value = 0
}

// 点击8个大目录模块
const handleCategoryModuleClick = (category) => {
  currentBigCategory.value = category
  currentSubcategory.value = null
  
  if (category.hasChildren && category.children.length > 0) {
    // 有子目录，显示子目录视图
    currentViewLevel.value = 'subcategories'
  } else {
    // 没有子目录（如材料基本信息），直接显示模版列表
    currentViewLevel.value = 'templates'
    loadTemplates(category.id)
  }
}

// 点击子目录
const handleSubcategoryClick = (subcat) => {
  currentSubcategory.value = subcat
  currentViewLevel.value = 'templates'
  loadTemplates(subcat.id)
}

// 面包屑点击
const handleBreadcrumbClick = (crumb, index) => {
  if (index >= breadcrumbs.value.length - 1) return // 最后一个不可点击
  
  if (index === 0) {
    // 点击第一级（数据资源分类）
    currentBigCategory.value = null
    currentSubcategory.value = null
    currentViewLevel.value = 'categories'
    templates.value = []
  } else if (index === 1 && crumb.level === 'subcategories') {
    // 点击第二级（大目录，且有子目录）
    currentSubcategory.value = null
    currentViewLevel.value = 'subcategories'
    templates.value = []
  }
}

// 返回上一级
const goBack = () => {
  if (currentViewLevel.value === 'templates') {
    if (currentSubcategory.value) {
      // 从模版列表返回到子目录
      currentSubcategory.value = null
      currentViewLevel.value = 'subcategories'
      templates.value = []
    } else if (currentBigCategory.value) {
      // 从模版列表返回到大目录
      currentBigCategory.value = null
      currentViewLevel.value = 'categories'
      templates.value = []
    }
  } else if (currentViewLevel.value === 'subcategories') {
    // 从子目录返回到大目录
    currentBigCategory.value = null
    currentViewLevel.value = 'categories'
  }
}

const loadTemplates = async (categoryId) => {
  loading.value = true
  try {
    const numericId = getNumericCategoryId(categoryId)
    if (numericId > 0) {
      const response = await request.get(`/basemodule/module/getmodules/${numericId}`)
      if (response.data?.code === 0) {
        templates.value = (response.data.module_list || []).filter(t => t.state === 1)
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
  if (currentSubcategory.value) {
    loadTemplates(currentSubcategory.value.id)
  } else if (currentBigCategory.value && !currentBigCategory.value.hasChildren) {
    loadTemplates(currentBigCategory.value.id)
  }
  ElMessage.success('刷新成功')
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handlePageChange = () => {
  // 分页处理
}

const viewTemplate = (template) => {
  currentTemplate.value = template
  drawerVisible.value = true
}

const goToCreate = () => {
  router.push('/template/create')
}

const goToDetail = () => {
  if (currentTemplate.value) {
    router.push({
      path: `/template/detail/${currentTemplate.value.id}`,
      query: {
        name: currentTemplate.value.name || currentTemplate.value.sample_serial
      }
    })
  }
}

// 渐变色
const getCategoryGradient = (index) => {
  const gradients = [
    'linear-gradient(135deg, #667eea, #764ba2)',
    'linear-gradient(135deg, #f093fb, #f5576c)',
    'linear-gradient(135deg, #4facfe, #00f2fe)',
    'linear-gradient(135deg, #43e97b, #38f9d7)',
    'linear-gradient(135deg, #fa709a, #fee140)',
    'linear-gradient(135deg, #a8edea, #fed6e3)',
    'linear-gradient(135deg, #d299c2, #fef9d7)',
    'linear-gradient(135deg, #89f7fe, #66a6ff)'
  ]
  return gradients[index % gradients.length]
}

const getSubcategoryGradient = (index) => {
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
  templates.value = []
  total.value = 0
})
</script>

<style lang="scss" scoped>
.template-library {
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
  border-right: 1px solid #e2e8f0;
  position: fixed;
  top: 72px;
  bottom: 0;
  left: 0;
  transition: all 0.3s ease;
  z-index: 100;
  
  &.collapsed {
    width: 60px;
    
    .sidebar-title,
    .node-label,
    .node-count {
      display: none;
    }
    
    .tree-node {
      justify-content: center;
    }
  }
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.sidebar-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
}

.collapse-btn {
  flex-shrink: 0;
}

.sidebar-content {
  padding: 16px;
  overflow-y: auto;
  height: calc(100% - 70px);
}

.category-tree {
  :deep(.el-tree-node__content) {
    height: 44px;
    border-radius: 8px;
    transition: all 0.2s ease;
    
    &:hover {
      background: #f1f5f9;
    }
  }
  
  :deep(.el-tree-node.is-current > .el-tree-node__content) {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
  }
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  
  .el-icon {
    color: #94a3b8;
  }
}

.node-label {
  flex: 1;
  font-size: 0.875rem;
}

.node-count {
  font-size: 0.75rem;
  color: #94a3b8;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 10px;
}

// 主内容区
.main-content {
  flex: 1;
  margin-left: 280px;
  padding: 32px;
  transition: margin-left 0.3s ease;
  
  .sidebar.collapsed + & {
    margin-left: 60px;
  }
}

// 面包屑导航
.breadcrumb-nav {
  margin-bottom: 20px;
  
  .crumb-link {
    cursor: pointer;
    color: #667eea;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.page-desc {
  font-size: 0.95rem;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 12px;
}

// 筛选区
.filter-section {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
}

.search-box {
  flex: 1;
  max-width: 400px;
  
  :deep(.el-input__wrapper) {
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }
}

// 8个大目录模块网格
.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  min-height: 300px;
}

.module-card {
  background: white;
  border-radius: 20px;
  padding: 28px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  gap: 20px;
  animation: fadeInUp 0.4s ease forwards;
  opacity: 0;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.12);
    
    &::before {
      opacity: 1;
    }
    
    .module-arrow {
      transform: translateX(6px);
      opacity: 1;
    }
  }
  
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
}

.module-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.25);
}

.module-info {
  flex: 1;
  min-width: 0;
}

.module-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.module-desc {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 12px;
  line-height: 1.5;
}

.module-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .sub-count, .no-sub {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.8rem;
    color: #94a3b8;
    background: #f1f5f9;
    padding: 4px 10px;
    border-radius: 12px;
    
    .el-icon {
      font-size: 14px;
    }
  }
}

.module-arrow {
  color: #94a3b8;
  opacity: 0.5;
  transition: all 0.3s ease;
  
  .el-icon {
    font-size: 20px;
  }
}

// 子目录模块网格
.submodule-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  min-height: 200px;
}

.submodule-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  gap: 16px;
  animation: fadeInUp 0.3s ease forwards;
  opacity: 0;
  
  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.1);
    
    .submodule-arrow {
      transform: translateX(4px);
      opacity: 1;
    }
  }
}

.submodule-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.submodule-info {
  flex: 1;
  min-width: 0;
}

.submodule-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
}

.submodule-arrow {
  color: #94a3b8;
  opacity: 0.5;
  transition: all 0.3s ease;
  
  .el-icon {
    font-size: 18px;
  }
}

// 模板网格
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  min-height: 300px;
}

.template-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  animation: fadeInUp 0.3s ease forwards;
  opacity: 0;
  
  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
    
    .arrow {
      transform: translateX(4px);
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.card-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.card-body {
  margin-bottom: 20px;
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
  font-size: 0.75rem;
  color: #94a3b8;
  
  .el-icon {
    font-size: 14px;
  }
}

.arrow {
  transition: transform 0.3s ease;
}

// 分页
.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

// 抽屉
.drawer-content {
  padding: 0 20px;
}

.detail-section {
  margin-bottom: 32px;
}

.section-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  .label {
    display: block;
    font-size: 0.75rem;
    color: #94a3b8;
    margin-bottom: 4px;
  }
  
  .value {
    font-size: 0.95rem;
    color: #1e293b;
    font-weight: 500;
  }
}

.description {
  font-size: 0.95rem;
  color: #475569;
  line-height: 1.6;
}

.drawer-actions {
  margin-top: 40px;
  
  .el-button {
    width: 100%;
  }
}

// 动画
.animate-slide-up {
  animation: slideUp 0.5s ease forwards;
}

.delay-1 {
  animation-delay: 0.1s;
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
@media (max-width: 1200px) {
  .module-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}

@media (max-width: 1024px) {
  .sidebar {
    transform: translateX(-100%);
    
    &:not(.collapsed) {
      transform: translateX(0);
    }
  }
  
  .main-content {
    margin-left: 0;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 20px;
  }
  
  .module-grid {
    grid-template-columns: 1fr;
  }
  
  .submodule-grid {
    grid-template-columns: 1fr;
  }
  
  .template-grid {
    grid-template-columns: 1fr;
  }
  
  .content-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .module-card {
    padding: 20px;
  }
  
  .module-icon {
    width: 56px;
    height: 56px;
  }
}
</style>
