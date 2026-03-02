<template>
  <div class="template-detail">
    <Navbar />
    
    <div class="page-container">
      <!-- 页面头部 -->
      <div class="page-header animate-slide-up">
        <div class="header-content">
          <el-button :icon="ArrowLeft" text @click="goBack">返回列表</el-button>
          <div class="header-info">
            <h1 class="page-title">{{ templateInfo.name || '数据资源详情' }}</h1>
            <el-tag :type="getStatusType(templateInfo.state)" effect="plain">
              {{ getStatusText(templateInfo.state) }}
            </el-tag>
          </div>
        </div>
        <div class="header-actions">
          <el-button :icon="FullScreen" @click="toggleFullscreen">全屏</el-button>
        </div>
      </div>

      <!-- 内容区：仅保留数据预览 + 数据详情 -->
      <div class="content-wrapper">
        <div class="detail-panel animate-slide-right">
          <el-tabs v-model="activeTab" class="detail-tabs">
            <!-- 数据预览 -->
            <el-tab-pane label="数据预览" name="data">
              <div class="tab-content">
                <div class="data-section">
                  <div class="data-header">
                    <h3>数据列表 ({{ filteredSampleData.length }}/{{ sampleData.length }}条)</h3>
                    <div class="data-actions">
                      <el-input
                        v-model="sampleSearchKeyword"
                        placeholder="搜索样品编号..."
                        :prefix-icon="Search"
                        size="small"
                        clearable
                        class="sample-search-input"
                      />
                      <el-button size="small" :icon="Refresh" @click="loadTemplateData">刷新</el-button>
                      <el-button type="primary" size="small" :icon="Plus" @click="goToUpload">
                        添加数据
                      </el-button>
                    </div>
                  </div>
                  
                  <el-table :data="filteredSampleData" stripe style="width: 100%" v-loading="loading">
                    <el-table-column type="index" label="序号" width="60" />
                    <el-table-column prop="sampleSerial" label="样本编号" min-width="200">
                      <template #default="{ row }">
                        <span class="sample-serial">{{ row.sampleSerial }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="createTime" label="创建时间" width="160" />
                    <el-table-column prop="creator" label="创建者" width="100" />
                    <el-table-column label="操作" width="180" fixed="right">
                      <template #default="{ row }">
                        <el-button type="primary" link size="small" @click="viewDataDetail(row)">查看</el-button>
                        <el-button type="primary" link size="small">编辑</el-button>
                        <el-button type="danger" link size="small">删除</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                  
                  <el-empty v-if="!loading && sampleData.length === 0" description="暂无数据，请先上传数据">
                    <el-button type="primary" @click="goToUpload">上传数据</el-button>
                  </el-empty>
                  <el-empty
                    v-else-if="!loading && sampleData.length > 0 && filteredSampleData.length === 0"
                    description="未找到匹配的样品编号"
                  />
                </div>
              </div>
            </el-tab-pane>

            <!-- 数据详情（单条样品，字段为表头） -->
            <el-tab-pane label="数据详情" name="detail">
              <div class="tab-content">
                <div class="data-detail-section">
                  <div class="data-header">
                    <h3>数据详情</h3>
                    <span v-if="currentSampleSerial" class="data-subtitle">
                      当前样品：{{ currentSampleSerial }}
                    </span>
                  </div>

                  <el-empty
                    v-if="!currentSampleSerial"
                    description="请在“数据预览”中点击【查看】，选择一条数据查看详情"
                  />

                  <div v-else class="data-detail-table">
                    <el-table :data="dataDetailRows" border style="width: 100%" v-loading="detailLoading">
                      <el-table-column type="index" label="#" width="60" />
                      <el-table-column
                        v-for="col in dataDetailColumns"
                        :key="col.key"
                        :prop="col.key"
                        :label="col.label"
                        min-width="120"
                        show-overflow-tooltip
                      />
                    </el-table>
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, FullScreen, InfoFilled, Document, DataLine,
  Folder, List, Download, Plus, Box, Setting, Refresh, Search
} from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()

// Tab
const activeTab = ref('data')

// 顶部数据资源信息（仅用于标题和状态）
const templateInfo = reactive({
  id: '',
  name: '',
  description: '',
  creator: '',
  createTime: '',
  updateTime: '',
  state: 1,
  dataCount: 0,
  downloadCount: 0
})

// 字段配置信息（对象/操作/结果三块），用于构建“数据详情”表头
const columnInfo = ref({
  object: [],
  operation: [],
  result: []
})

// 数据列表
const sampleData = ref([])
const loading = ref(false)
const sampleSearchKeyword = ref('')

const filteredSampleData = computed(() => {
  if (!sampleSearchKeyword.value) return sampleData.value
  const keyword = sampleSearchKeyword.value.toLowerCase()
  return sampleData.value.filter(item => 
    (item.sampleSerial || '').toLowerCase().includes(keyword)
  )
})

// 单条数据详情
const detailLoading = ref(false)
const currentSampleSerial = ref('')
const dataDetailRows = ref([])

// 所有字段（列）= 对象 + 操作 + 结果 的字段名合集
const dataDetailColumns = computed(() => {
  const cols = []
  const existed = new Set()

  const addColsFrom = (list) => {
    if (!Array.isArray(list)) return
    list.forEach(col => {
      const name = col.column_name || col.columnName
      if (name && !existed.has(name)) {
        existed.add(name)
        cols.push({ key: name, label: name })
      }
    })
  }

  addColsFrom(columnInfo.value.object)
  addColsFrom(columnInfo.value.operation)
  addColsFrom(columnInfo.value.result)

  return cols
})

// 加载字段信息（只用来构建 dataDetailColumns）
const loadColumnInfo = async () => {
  const id = route.params.id
  if (!id) return
  
  try {
    const response = await request.get(`/basemodule/moduledata/getColumnInfo/${id}`)
    if (response.data?.code === 0 && response.data?.columnInfo) {
      columnInfo.value = response.data.columnInfo
      if (response.data.templateName) {
        templateInfo.name = response.data.templateName
      }
    } else {
      console.warn('获取字段信息返回非成功状态:', response.data)
    }
  } catch (error) {
    console.error('加载字段信息失败:', error)
  }
}

// 加载数据列表
const loadTemplateData = async () => {
  const id = route.params.id
  if (!id) return
  
  loading.value = true
  try {
    const response = await request.get(`/basemodule/moduledata/list/${id}`)
    if (response.data?.code === 0) {
      const dataList = response.data.moduleData || []
      sampleData.value = dataList.map(item => ({
        id: item.id,
        sampleSerial: item.sample_serial || item.sampleSerial || '-',
        createTime: item.createTime || item.create_time || '-',
        creator: item.creator || '-',
        rawData: item
      }))
      templateInfo.dataCount = sampleData.value.length
    } else {
      sampleData.value = []
      templateInfo.dataCount = 0
    }
  } catch (error) {
    console.error('加载模板数据失败:', error)
    sampleData.value = []
    templateInfo.dataCount = 0
  } finally {
    loading.value = false
  }
}

// 点击“查看” -> 加载单条数据详情并切到“数据详情”Tab
const viewDataDetail = async (row) => {
  const moduleId = route.params.id
  const sampleSerial = row.sampleSerial
  
  if (!moduleId || !sampleSerial || sampleSerial === '-') {
    ElMessage.warning('缺少必要参数，无法查看详情')
    return
  }
  
  detailLoading.value = true
  currentSampleSerial.value = sampleSerial
  
  try {
    const response = await request.post('/basemodule/moduledata/getdetail', {
      sampleSerial: sampleSerial,
      moduleId: String(moduleId)
    })
    
    if (response.data?.code === 0) {
      const moduleData = response.data.moduleData || {
        objectList: [],
        operationList: [],
        resultList: []
      }
      buildDataDetailRows(moduleData)
      activeTab.value = 'detail'
      ElMessage.success('数据加载成功')
    } else {
      ElMessage.error(response.data?.msg || '获取数据详情失败')
    }
  } catch (error) {
    console.error('获取数据详情失败:', error)
    ElMessage.error('获取数据详情失败')
  } finally {
    detailLoading.value = false
  }
}

// 根据详情接口 + 字段配置，构建“数据详情”一行数据
const buildDataDetailRows = (moduleData) => {
  const { objectList = [], operationList = [], resultList = [] } = moduleData

  const row = {}

  // 汇总所有来源对象，按字段名做智能匹配
  const allSources = [
    ...(objectList.length ? [objectList[0]] : []),
    ...(operationList.length ? [operationList[0]] : []),
    ...(resultList.length ? [resultList[0]] : [])
  ]

  const findValueByColumnName = (columnName) => {
    for (const item of allSources) {
      if (!item) continue

      if (item[columnName] !== undefined && item[columnName] !== null && item[columnName] !== '') {
        return item[columnName]
      }

      const snakeCase = columnName.replace(/([A-Z])/g, '_$1').toLowerCase()
      if (item[snakeCase] !== undefined && item[snakeCase] !== null && item[snakeCase] !== '') {
        return item[snakeCase]
      }

      const camelCase = columnName.replace(/_([a-z])/g, (g) => g[1].toUpperCase())
      if (item[camelCase] !== undefined && item[camelCase] !== null && item[camelCase] !== '') {
        return item[camelCase]
      }

      const lowerKey = columnName.toLowerCase()
      for (const key in item) {
        if (key.toLowerCase() === lowerKey && item[key] !== null && item[key] !== '') {
          return item[key]
        }
      }
    }
    return '-'
  }

  dataDetailColumns.value.forEach(col => {
    row[col.key] = findValueByColumnName(col.key)
  })

  dataDetailRows.value = [row]
}

const goBack = () => {
  router.push('/template/library')
}

const goToUpload = () => {
  router.push('/template/upload')
}

const toggleFullscreen = () => {
  if (document.fullscreenElement) {
    document.exitFullscreen()
  } else {
    document.documentElement.requestFullscreen()
  }
}

const getStatusType = (state) => {
  const types = { 0: 'info', 1: 'success', 2: 'warning' }
  return types[state] || 'info'
}

const getStatusText = (state) => {
  const texts = { 0: '草稿', 1: '已发布', 2: '审核中' }
  return texts[state] || '未知'
}

onMounted(() => {
  const id = route.params.id
  const name = route.query.name
  if (id) {
    templateInfo.id = id
    if (name) templateInfo.name = name
    loadColumnInfo()
    loadTemplateData()
  }
})
</script>

<style lang="scss" scoped>
.template-detail {
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
  padding: 24px 32px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.header-actions {
  display: flex;
  gap: 12px;
}

// 内容区
.content-wrapper {
  display: flex;
  padding: 24px;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.detail-panel {
  flex: 1;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.detail-tabs {
  :deep(.el-tabs__header) {
    margin: 0;
    padding: 0 24px;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
  }
  
  :deep(.el-tabs__nav-wrap::after) {
    display: none;
  }
  
  :deep(.el-tabs__item) {
    height: 56px;
    font-weight: 500;
  }
}

.tab-content {
  padding: 32px;
}

// 数据预览
.data-section {
  .data-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h3 {
      font-size: 1rem;
      font-weight: 600;
      color: #1e293b;
    }
    
    .data-actions {
      display: flex;
      gap: 12px;
      align-items: center;
      
      .sample-search-input {
        width: 200px;
        
        :deep(.el-input__wrapper) {
          border-radius: 8px;
        }
      }
    }
  }
}

// 数据详情
.data-detail-section {
  .data-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h3 {
      font-size: 1rem;
      font-weight: 600;
      color: #1e293b;
    }
    
    .data-subtitle {
      font-size: 0.875rem;
      color: #64748b;
    }
  }
}

// 响应式
@media (max-width: 1024px) {
  .content-wrapper {
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>


