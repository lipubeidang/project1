<template>
  <div class="tpl-edit">
    <Navbar />
    
    <div class="page-container">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="sidebar-title-wrap">
            <el-icon class="sidebar-icon"><EditPen /></el-icon>
            <h3>修改分类</h3>
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
              <el-icon :size="36"><EditPen /></el-icon>
            </div>
            <div class="banner-info">
              <h1 class="page-title">模版修改</h1>
              <p class="page-desc" v-if="currentCategory">
                当前目录：{{ currentCategory.name }}
              </p>
              <p class="page-desc" v-else>审核员专属功能，处理模版修改申请</p>
            </div>
            <div class="banner-badge">
              <el-tag type="danger" effect="dark" size="large">
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

        <!-- 模版列表 -->
        <div class="templates-section animate-slide-up delay-2" v-loading="loading">
          <div class="templates-grid" v-if="displayedTemplates.length > 0">
            <div 
              v-for="template in displayedTemplates" 
              :key="template.id"
              class="template-card"
              @click="selectTemplate(template)"
              :class="{ active: selectedTemplate?.id === template.id }"
            >
              <div class="card-header">
                <h4 class="card-title">{{ template.name }}</h4>
                <el-tag 
                  :type="getStatusType(template.status)" 
                  effect="light"
                >
                  {{ getStatusText(template.status) }}
                </el-tag>
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
                <el-button type="primary" size="small" @click.stop="editTemplate(template)">
                  编辑模版
                </el-button>
                <el-button type="success" size="small" plain @click.stop="editFields(template)">
                  修改字段
                </el-button>
                <el-button type="danger" size="small" plain @click.stop="deleteTemplate(template)">
                  删除
                </el-button>
              </div>
            </div>
          </div>
          <el-empty v-else-if="!loading && currentCategory" description="该目录下暂无模版" :image-size="120" />
          <el-empty v-else-if="!loading" description="请选择左侧目录查看模版" :image-size="120" />
        </div>
      </main>
    </div>

    <!-- 编辑模版抽屉 -->
    <el-drawer
      v-model="editDrawerVisible"
      :title="`编辑模版: ${editingTemplate?.name || ''}`"
      direction="rtl"
      size="600px"
    >
      <div class="edit-form-container" v-if="editingTemplate">
        <el-form :model="editForm" label-width="100px" label-position="top">
          <el-form-item label="模版名称" required>
            <el-input v-model="editForm.name" placeholder="请输入模版名称" />
          </el-form-item>
          
          <el-form-item label="所属大类">
            <el-select v-model="editForm.bigCategory" placeholder="请选择大类" @change="handleBigCategoryChange">
              <el-option
                v-for="cat in bigCategories"
                :key="cat.id"
                :label="cat.name"
                :value="cat.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="所属小类" v-if="availableSubCategories.length > 0">
            <el-select v-model="editForm.subCategory" placeholder="请选择小类">
              <el-option
                v-for="cat in availableSubCategories"
                :key="cat.id"
                :label="cat.name"
                :value="cat.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="模版描述">
            <el-input
              v-model="editForm.description"
              type="textarea"
              :rows="4"
              placeholder="请输入模版描述"
            />
          </el-form-item>
          
          <el-form-item label="版本号">
            <el-input v-model="editForm.version" placeholder="如: v1.0.0" />
          </el-form-item>
          
          <el-form-item label="状态">
            <el-radio-group v-model="editForm.status">
              <el-radio label="draft">草稿</el-radio>
              <el-radio label="pending">待审核</el-radio>
              <el-radio label="published">已发布</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
        
        <div class="drawer-footer">
          <el-button @click="editDrawerVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTemplate" :loading="saving">保存修改</el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Folder, Document, User, Calendar, Search, EditPen } from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'
import { 
  getCategoryTree, 
  getBigCategories, 
  getSubCategories,
  defaultExpandedKeys as defaultKeys 
} from '@/utils/templateCategories'

const router = useRouter()
const route = useRoute()

// 状态
const loading = ref(false)
const saving = ref(false)
const currentCategory = ref(null)
const searchKeyword = ref('')
const editDrawerVisible = ref(false)
const editingTemplate = ref(null)
const selectedTemplate = ref(null)

// 模板数据
const templates = ref([])

// 分类数据
const categoryTree = ref(getCategoryTree())
const defaultExpandedKeys = ref([...defaultKeys])
const bigCategories = getBigCategories()

// 编辑表单
const editForm = ref({
  name: '',
  bigCategory: '',
  subCategory: '',
  description: '',
  version: '',
  status: 'draft'
})

// 获取可用子分类
const availableSubCategories = computed(() => {
  if (!editForm.value.bigCategory) return []
  return getSubCategories(editForm.value.bigCategory)
})

// 搜索过滤
const displayedTemplates = computed(() => {
  if (!searchKeyword.value) return templates.value
  const keyword = searchKeyword.value.toLowerCase()
  return templates.value.filter(t =>
    (t.name || '').toLowerCase().includes(keyword) ||
    (t.description || '').toLowerCase().includes(keyword)
  )
})

// 处理大类切换
const handleBigCategoryChange = () => {
  editForm.value.subCategory = ''
}

// 目录点击
const handleCategoryClick = (data) => {
  currentCategory.value = data
  loadTemplates()
}

// 加载模版
const loadTemplates = async () => {
  if (!currentCategory.value?.id) return
  
  loading.value = true
  try {
    const response = await request.get(`/tplmanage/templates/list/${currentCategory.value.id}`)
    if (response.data?.code === 0) {
      templates.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载模版失败:', error)
    // 使用模拟数据
    templates.value = []
  } finally {
    loading.value = false
  }
}

// 选择模板
const selectTemplate = (template) => {
  selectedTemplate.value = template
}

// 编辑模版
const editTemplate = (template) => {
  editingTemplate.value = template
  editForm.value = {
    name: template.name || '',
    bigCategory: template.bigCategory || '',
    subCategory: template.subCategory || '',
    description: template.description || '',
    version: template.version || 'v1.0.0',
    status: template.status || 'draft'
  }
  editDrawerVisible.value = true
}

// 编辑字段
const editFields = (template) => {
  router.push(`/tplmanage/field-edit/${template.id}`)
}

// 保存模版
const saveTemplate = async () => {
  if (!editForm.value.name) {
    ElMessage.warning('请输入模版名称')
    return
  }
  
  saving.value = true
  try {
    await request.put(`/tplmanage/templates/${editingTemplate.value.id}`, editForm.value)
    ElMessage.success('保存成功')
    editDrawerVisible.value = false
    loadTemplates()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 删除模版
const deleteTemplate = async (template) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模版"${template.name}"吗？此操作不可恢复。`,
      '删除确认',
      { type: 'warning' }
    )
    
    await request.delete(`/tplmanage/templates/${template.id}`)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 状态相关
const getStatusType = (status) => {
  const types = {
    draft: 'info',
    pending: 'warning',
    approved: 'success',
    published: 'success',
    rejected: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    draft: '草稿',
    pending: '待审核',
    approved: '已通过',
    published: '已发布',
    rejected: '已拒绝'
  }
  return texts[status] || '未知'
}

const formatDate = (date) => {
  if (!date) return '未知'
  return date.split(' ')[0]
}

onMounted(() => {
  // 如果URL带有模版ID参数，加载对应模版
  const templateId = route.params.templateId
  if (templateId) {
    loadTemplateById(templateId)
  }
})

const loadTemplateById = async (id) => {
  try {
    const response = await request.get(`/tplmanage/templates/${id}`)
    if (response.data?.code === 0) {
      const template = response.data.data
      editTemplate(template)
    }
  } catch (error) {
    console.error('加载模版详情失败:', error)
  }
}
</script>

<style lang="scss" scoped>
.tpl-edit {
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
  background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
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
}

.category-tree {
  background: transparent;
  
  :deep(.el-tree-node__content) {
    height: 40px;
    border-radius: 8px;
    
    &:hover {
      background: #fce7f3;
    }
  }
  
  :deep(.el-tree-node.is-current > .el-tree-node__content) {
    background: linear-gradient(135deg, rgba(236, 72, 153, 0.1), rgba(244, 114, 182, 0.1));
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
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
  }
  
  &.active {
    border-color: #ec4899;
    box-shadow: 0 12px 40px rgba(236, 72, 153, 0.15);
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

// 编辑抽屉
.edit-form-container {
  padding: 0 8px;
}

.drawer-footer {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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
</style>
