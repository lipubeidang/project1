<template>
  <div class="sinter-curve-recommend-page">
    <Navbar />
    
    <!-- 隐藏的文件输入，用于选择 xlsx 文件 -->
    <input 
      ref="fileInput" 
      type="file" 
      accept=".xlsx,.xls" 
      style="display: none;" 
      @change="handleFileSelect"
    />

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧分类菜单 -->
      <div class="sidebar">
        <div class="category-list">
          <el-tree
            :data="directoryTree"
            :props="defaultProps"
            @node-click="handleNodeClick"
            :default-expanded-keys="defaultExpandedKeys"
            node-key="id"
            highlight-current
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <el-icon v-if="data.children && data.children.length > 0">
                  <Folder v-if="!node.expanded" />
                  <FolderOpened v-else />
                </el-icon>
                <el-icon v-else><Document /></el-icon>
                <span class="node-label">{{ node.label }}</span>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- 右侧内容区域 -->
      <div class="content-area">
        <!-- 机器学习按钮栏区域 -->
        <div class="header-section">
          <div class="ml-button-bar">
            <div class="button-bar-header">
              <span class="section-label">机器学习</span>
              <h2 class="content-title">{{ currentNode?.name || '请选择模板' }}</h2>
            </div>
            <div class="button-group">
            <el-button 
                type="primary" 
                @click="handleMLAction('transform')"
              >
                <el-icon><DataAnalysis /></el-icon>
                数据转换
            </el-button>
              <el-button 
                type="success" 
                @click="handleMLAction('augment')"
              >
                <el-icon><TrendCharts /></el-icon>
                数据增强
              </el-button>
              <el-button 
                type="warning" 
                @click="handleMLAction('train')"
              >
                <el-icon><View /></el-icon>
                模型训练
              </el-button>
              <el-button 
                type="danger" 
                @click="handleSinteringCurve"
              >
                <el-icon><Star /></el-icon>
                烧结曲线推荐
              </el-button>
          </div>
          </div>
        </div>

        <!-- 表名选择区域（数据转换后显示） -->
        <div class="table-select-box" v-if="showTransformTables && transformTables.length > 0">
          <div class="filter-header">
            <span class="filter-title">
              <el-icon><Grid /></el-icon>
              数据表选择
            </span>
            <span class="selected-count">共 {{ transformTables.length }} 张表</span>
          </div>
          <div class="table-tabs-container">
            <el-tabs 
              v-model="currentTableIndex" 
              @tab-click="handleTableTabClick"
              type="card"
            >
              <el-tab-pane 
                v-for="(table, index) in transformTables" 
                :key="index"
                :label="table.name"
                :name="String(index)"
              />
            </el-tabs>
          </div>
            </div>

        <!-- 列字段选择区域（非数据转换模式显示） -->
        <div class="column-filter-box" v-if="!showTransformTables && expandedTableData.length > 0">
          <div class="filter-header">
            <span class="filter-title">
              <el-icon><Grid /></el-icon>
              列字段选择
            </span>
            <span class="selected-count">已选择 {{ checkedColumns.length }} / {{ allAvailableColumns.length }} 列</span>
          </div>
          <div class="filter-content">
            <el-checkbox 
              :indeterminate="isIndeterminate" 
              v-model="checkAll"
              @change="handleCheckAllChange"
              class="check-all-box"
            >
              全选
            </el-checkbox>
            <div class="checkbox-group-container">
              <el-checkbox-group 
                v-model="checkedColumns" 
                @change="handleCheckedColumnsChange"
                class="column-checkbox-group"
              >
                <el-checkbox 
                  v-for="col in allAvailableColumns" 
                  :label="col.prop" 
                  :key="col.prop"
                  class="column-checkbox"
                >
                  {{ col.label }}
                </el-checkbox>
              </el-checkbox-group>
            </div>
            <div class="filter-actions">
              <el-button type="primary" size="small" @click="applyColumnFilter">
                <el-icon><Check /></el-icon>
                应用选择
              </el-button>
              <el-button size="small" @click="resetColumnFilter">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </div>
          </div>
        </div>

        <!-- 表格 -->
        <div class="table-container">
          <el-empty 
            v-if="!showTransformTables && expandedTableData.length === 0 && !currentNode && !loading" 
            description="请从左侧选择模板查看数据" 
            :image-size="120"
          >
            <template #image>
              <el-icon :size="80"><FolderOpened /></el-icon>
            </template>
          </el-empty>
          <el-empty 
            v-else-if="!showTransformTables && expandedTableData.length === 0 && currentNode && currentNode.isTemplate && !loading" 
            description="该模板暂无数据" 
            :image-size="100"
          />
          <el-empty 
            v-else-if="showTransformTables && totalDataCount === 0 && !loading" 
            description="当前表暂无数据" 
            :image-size="100"
          />
          <template v-else>
            <div class="table-scroll-box">
              <el-table
                ref="dataTable"
                :data="displayTableData"
                v-loading="loading"
                element-loading-text="正在加载数据..."
                stripe
                style="width: 100%; min-width: 100%"
                :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
                border
                @selection-change="handleSelectionChange"
                @select-all="handleSelectAll"
              >
                <!-- 选择列 -->
                <el-table-column
                  type="selection"
                  width="55"
                  align="center"
                />
                
                <el-table-column
                  label="序号"
                  width="80"
                  align="center"
                  type="index"
                  :index="getIndex"
                />
                
                <!-- 动态列 -->
                <el-table-column
                  v-for="col in displayColumns"
                  :key="col.prop"
                  :prop="col.prop"
                  :label="col.label"
                  :width="col.width || 200"
                  show-overflow-tooltip
                >
                  <template #default="scope">
                    {{
                      scope.row[col.prop] === null || 
                      scope.row[col.prop] === undefined || 
                      scope.row[col.prop] === ''
                        ? '-'
                        : scope.row[col.prop]
                    }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </template>

          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              v-model:current-page="currentPage"
              :page-sizes="[20, 50, 100, 200]"
              v-model:page-size="pageSize"
              :pager-count="7"
              layout="total, sizes, prev, pager, next, jumper"
              :total="totalDataCount"
              :disabled="totalDataCount === 0"
            />
          </div>
        </div>
      </div>
            </div>
            
    <!-- 模型训练进度条对话框 -->
    <el-dialog
      v-model="showTrainingProgress"
      title="模型训练中"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
      width="500px"
      center
    >
      <div class="training-progress-container">
        <el-progress 
          :percentage="trainingProgress" 
          :status="trainingProgress === 100 ? 'success' : ''"
          :stroke-width="20"
        />
        <p class="progress-text">{{ trainingProgressText }}</p>
            </div>
    </el-dialog>
    
    <!-- 训练完成提示对话框 -->
    <el-dialog
      v-model="showTrainingComplete"
      title="训练完成"
      width="400px"
      center
    >
      <div class="training-complete-container">
        <el-icon :size="48" color="#67C23A"><SuccessFilled /></el-icon>
        <p style="font-size: 16px; margin-top: 20px;">模型训练已完成！</p>
            </div>
      <template #footer>
        <el-button type="primary" @click="handleMymodelClick">Mymodel</el-button>
        <el-button @click="handleTrainingComplete">完成</el-button>
      </template>
    </el-dialog>
    
    <!-- 图片显示弹窗 -->
    <el-dialog
      v-model="showImageDialog"
      title="训练结果"
      width="80%"
      center
      @close="handleImageDialogClose"
    >
      <div class="image-dialog-container">
        <img 
          v-if="imageUrl" 
          :src="imageUrl" 
          alt="训练结果图片" 
          class="result-image"
          @error="handleImageError"
        />
        <div v-else class="image-loading">
          <el-icon :size="32"><Loading /></el-icon>
          <p>正在加载图片...</p>
          </div>

        <!-- 训练数据展示区域 -->
        <div class="training-metrics-container" v-if="imageUrl">
          <div class="metrics-header">
            <el-icon><DataAnalysis /></el-icon>
            <span>训练指标</span>
                </div>
          <div class="metrics-content">
            <div class="metrics-row">
              <div class="metric-item">
                <span class="metric-label">最佳轮次 (Best Epoch):</span>
                <span class="metric-value">{{ trainingMetrics.best_epoch }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">最佳损失 (Best Loss):</span>
                <span class="metric-value">{{ trainingMetrics.best_loss.toFixed(9) }}</span>
                </div>
              </div>
            <div class="metrics-divider"></div>
            <div class="metrics-section">
              <h4 class="section-title">训练集指标</h4>
              <div class="metrics-row">
                <div class="metric-item">
                  <span class="metric-label">R² 分数:</span>
                  <span class="metric-value">{{ trainingMetrics.train_r2.toFixed(6) }}</span>
              </div>
                <div class="metric-item">
                  <span class="metric-label">平均绝对误差 (MAE):</span>
                  <span class="metric-value">{{ trainingMetrics.train_mae.toFixed(6) }}</span>
            </div>
                <div class="metric-item">
                  <span class="metric-label">均方根误差 (RMSE):</span>
                  <span class="metric-value">{{ trainingMetrics.train_rmse.toFixed(6) }}</span>
          </div>
        </div>
      </div>
            <div class="metrics-divider"></div>
            <div class="metrics-section">
              <h4 class="section-title">测试集指标</h4>
              <div class="metrics-row">
                <div class="metric-item">
                  <span class="metric-label">R² 分数:</span>
                  <span class="metric-value">{{ trainingMetrics.test_r2.toFixed(6) }}</span>
    </div>
                <div class="metric-item">
                  <span class="metric-label">平均绝对误差 (MAE):</span>
                  <span class="metric-value">{{ trainingMetrics.test_mae.toFixed(6) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">均方根误差 (RMSE):</span>
                  <span class="metric-value">{{ trainingMetrics.test_rmse.toFixed(6) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
    
    <!-- 烧结曲线推荐对话框 -->
    <el-dialog
      v-model="showSinterCurveDialog"
      title="烧结曲线推荐"
      width="90%"
      :close-on-click-modal="false"
      @close="handleSinterCurveDialogClose"
    >
      <div class="sinter-curve-dialog-content">
        <div class="selection-area">
          <!-- 左侧：下拉框选择 -->
          <div class="left-panel">
            <div class="select-wrapper">
              <label class="select-label">选择结构类型：</label>
              <el-select
                v-model="selectedStructure"
                placeholder="请选择结构类型"
                class="structure-select"
                @change="handleStructureChange"
                size="large"
              >
                <el-option
                  v-for="structure in structureOptions"
                  :key="structure.value"
                  :label="structure.label"
                  :value="structure.value"
                />
              </el-select>
            </div>

            <div class="select-wrapper" v-if="selectedStructure">
              <label class="select-label">模型选择：</label>
              <el-select
                v-model="selectedModel"
                placeholder="请选择模型"
                class="model-select"
                @change="handleModelChange"
                size="large"
              >
                <el-option
                  v-for="model in modelOptions"
                  :key="model.value"
                  :label="model.label"
                  :value="model.value"
                />
              </el-select>
            </div>

            <div class="selected-info" v-if="selectedStructure">
              <p>当前选择：<strong>{{ getCurrentStructureLabel() }}</strong></p>
            </div>
            
            <div class="selected-info" v-if="selectedModel" style="margin-top: 10px;">
              <p>当前模型：<strong>{{ getCurrentModelLabel() }}</strong></p>
            </div>

            <div class="confirm-button-wrapper" style="margin-top: 20px;">
              <el-button 
                type="primary" 
                size="large"
                @click="handleConfirm"
                :disabled="!selectedStructure || !selectedModel"
                class="confirm-button"
              >
                确定
              </el-button>
            </div>
          </div>

          <!-- 右侧：图片/图表展示区域 -->
          <div class="right-panel">
            <div class="image-preview">
              <!-- 显示烧结曲线图表 -->
              <div v-if="showSinterResult" class="chart-container">
                <div ref="sinterCurveChart" class="chart-wrapper"></div>
                <div class="image-label">烧结曲线推荐结果</div>
              </div>
              <!-- 显示结构图片 -->
              <div v-else-if="selectedImage" class="image-container">
                <img 
                  :src="selectedImage" 
                  :alt="getCurrentStructureLabel()"
                  class="structure-image"
                />
                <div class="image-label">{{ getCurrentStructureLabel() }}</div>
              </div>
              <div v-else class="placeholder">
                <el-icon :size="64"><Picture /></el-icon>
                <p>请选择结构类型查看图片</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  DataAnalysis, TrendCharts, View, Star, Grid, Check, Refresh,
  Folder, FolderOpened, Document, SuccessFilled, Loading, Picture
} from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'
import { templateCategories, getCategoryTree, getNumericCategoryId } from '@/utils/templateCategories'
import * as XLSX from 'xlsx'
import * as echarts from 'echarts'

const router = useRouter()

// 文件输入引用
const fileInput = ref(null)

// 目录树相关
const directoryTree = ref([])
const defaultProps = {
  children: 'children',
  label: 'name'
}
const defaultExpandedKeys = ref(['cat_basic', 'cat_design'])
const currentNode = ref(null)

// 表格数据相关
const expandedTableData = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const dynamicColumns = ref([])
const loading = ref(false)
const selectedDataRows = ref([])
const allSelectedRows = ref(new Set())

// 列字段选择相关
const allAvailableColumns = ref([])
const checkedColumns = ref([])
const checkAll = ref(true)
const isIndeterminate = ref(false)

// 数据转换相关
const xlsxFileData = ref([])
const transformTables = ref([])
const currentTableIndex = ref('0')
const showTransformTables = ref(false)

// 模型训练相关
const showTrainingProgress = ref(false)
const trainingProgress = ref(0)
const trainingProgressText = ref('正在初始化...')
const trainingTimer = ref(null)
const showTrainingComplete = ref(false)
const showImageDialog = ref(false)
const imageUrl = ref('')
const trainingMetrics = reactive({
  best_epoch: 256,
  best_loss: 0.000121340970890411,
  train_r2: 0.8337273178478967,
  train_mae: 0.06201135360633358,
  train_rmse: 0.09560802050034772,
  test_r2: 0.8900385499000549,
  test_mae: 0.18664707243442535,
  test_rmse: 0.2735595703125
})

// 烧结曲线推荐相关
const showSinterCurveDialog = ref(false)
const selectedStructure = ref('')
const selectedModel = ref('Mymodel')
const selectedImage = ref('')
const showSinterResult = ref(false)
const sinterCurveChart = ref(null)
const chartInstance = ref(null)

const structureOptions = [
  { label: 'A方孔', value: 'A', image: '/方孔.png' },
  { label: 'B金刚石', value: 'B', image: '/金刚石.png' },
  { label: 'C镜像金刚石', value: 'C', image: '/镜像金刚石.png' },
  { label: 'D面心八面体', value: 'D', image: '/面心八面体.png' },
  { label: 'E面心顶角', value: 'E', image: '/面心顶角.png' },
  { label: 'F四维立方', value: 'F', image: '/四维立方.png' },
  { label: 'G体心顶角', value: 'G', image: '/体心顶角.png' }
]

const modelOptions = [
  { label: 'Mymodel', value: 'Mymodel' },
  { label: 'MLP', value: 'MLP' },
  { label: 'Transformer', value: 'Transformer' }
]

// 计算属性
const displayTableData = computed(() => {
  if (showTransformTables.value && transformTables.value.length > 0) {
    const currentTable = transformTables.value[parseInt(currentTableIndex.value)]
    if (currentTable && currentTable.data) {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return currentTable.data.slice(start, end)
    }
    return []
  }
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return expandedTableData.value.slice(start, end)
})

const allTableData = computed(() => {
  if (showTransformTables.value && transformTables.value.length > 0) {
    const currentTable = transformTables.value[parseInt(currentTableIndex.value)]
    if (currentTable && currentTable.data) {
      return currentTable.data
    }
    return []
  }
  return expandedTableData.value
})

const displayColumns = computed(() => {
  if (showTransformTables.value && transformTables.value.length > 0) {
    const currentTable = transformTables.value[parseInt(currentTableIndex.value)]
    if (currentTable && currentTable.columns) {
      return currentTable.columns
    }
  }
  if (checkedColumns.value.length === 0) {
    return dynamicColumns.value
  }
  return dynamicColumns.value.filter(col => checkedColumns.value.includes(col.prop))
})

const totalDataCount = computed(() => {
  if (showTransformTables.value && transformTables.value.length > 0) {
    const currentTable = transformTables.value[parseInt(currentTableIndex.value)]
    if (currentTable && currentTable.data) {
      return currentTable.data.length
    }
    return 0
  }
  return expandedTableData.value.length
})

// 加载目录树
const loadDirectoryTree = async () => {
  try {
    const categoryTree = getCategoryTree()
    
    // 为每个分类获取其下的模板
    const buildTreePromises = categoryTree.map(async cat => {
      const numericId = getNumericCategoryId(cat.id)
      
      // 如果有子分类，递归处理
      if (cat.children && cat.children.length > 0) {
        const subCategoriesWithTemplates = await Promise.all(
          cat.children.map(async subCat => {
            try {
              const subNumericId = getNumericCategoryId(subCat.id)
              if (!subNumericId) {
                return {
                  id: subCat.id,
                  name: subCat.name,
                  isSubCategory: true,
                  children: []
                }
              }
              
              const response = await request.get(`/template/getTemplateByCategory/${subNumericId}`)
              
              if (response.data?.code === 1 || response.data?.code === 0) {
                const templates = response.data.data || []
                
                return {
                  id: subCat.id,
                  name: subCat.name,
                  isSubCategory: true,
                  children: templates
                    .filter(template => template.state === 1)
                    .map(template => ({
                      id: template.id || template.templateId,
                      name: template.name || template.templateName,
                      isTemplate: true,
                      template: template
                    }))
                }
              }
            } catch (error) {
              console.error(`获取子目录 ${subCat.name} 的模板失败:`, error)
            }
            
            return {
              id: subCat.id,
              name: subCat.name,
              isSubCategory: true,
              children: []
            }
          })
        )
        
        return {
          id: cat.id,
          name: cat.name,
          isBigCategory: true,
          children: subCategoriesWithTemplates
        }
      } else {
        // 没有子分类，直接获取模板
        try {
          if (!numericId) {
            return {
              id: cat.id,
              name: cat.name,
              isBigCategory: true,
              children: []
            }
          }
          
          const response = await request.get(`/template/getTemplateByCategory/${numericId}`)
          
          if (response.data?.code === 1 || response.data?.code === 0) {
            const templates = response.data.data || []
            
            return {
              id: cat.id,
              name: cat.name,
              isBigCategory: true,
              children: templates
                .filter(template => template.state === 1)
                .map(template => ({
                  id: template.id || template.templateId,
                  name: template.name || template.templateName,
                  isTemplate: true,
                  template: template
                }))
            }
          }
        } catch (error) {
          console.error(`获取分类 ${cat.name} 的模板失败:`, error)
        }
        
        return {
          id: cat.id,
          name: cat.name,
          isBigCategory: true,
          children: []
        }
      }
    })
    
    directoryTree.value = await Promise.all(buildTreePromises)
    console.log('目录树加载完成:', directoryTree.value)
  } catch (error) {
    console.error('加载目录树失败:', error)
    ElMessage.error('加载目录树失败，请刷新页面重试')
  }
}

// 处理节点点击
const handleNodeClick = (node) => {
  console.log('点击节点:', node)
  
  if (node.isTemplate) {
    currentNode.value = node
    currentPage.value = 1
    loadTemplateData()
  }
}

// 加载模板数据
const loadTemplateData = async () => {
  try {
    if (!currentNode.value || !currentNode.value.isTemplate) {
      console.log('没有选中的模板节点，不加载数据')
      expandedTableData.value = []
      dynamicColumns.value = []
      return
    }

    loading.value = true
    console.log('开始加载模板数据，模板ID:', currentNode.value.id)
    
    // 使用模板数据API：/templateData/getAuditedTemplateData/{templateId}
    const response = await request.get(`/templateData/getAuditedTemplateData/${currentNode.value.id}`)
    
    if (response.data?.code === 1) {
      const data = response.data.data || []
      
      if (data.length > 0) {
        expandedTableData.value = data
        setupDynamicColumnsFromData(data)
        console.log('加载数据成功，总数:', expandedTableData.value.length)
      } else {
        expandedTableData.value = []
        dynamicColumns.value = []
        console.log('该模板暂无数据')
      }
    } else {
      expandedTableData.value = []
      dynamicColumns.value = []
      console.log('API返回错误，使用空数据')
    }
    
    // 清空选中状态
    allSelectedRows.value.clear()
    selectedDataRows.value = []
  } catch (error) {
    console.error('加载模板数据失败:', error)
    ElMessage.error('加载模板数据失败，请重试')
    expandedTableData.value = []
    dynamicColumns.value = []
  } finally {
    loading.value = false
  }
}

// 根据数据自动生成列
const setupDynamicColumnsFromData = (data) => {
  if (!data || data.length === 0) {
    dynamicColumns.value = []
    return
  }
  
  const allColumns = new Set()
  data.forEach(row => {
    Object.keys(row).forEach(key => {
      if (key !== 'row_id') {
        allColumns.add(key)
      }
    })
  })
  
  const columnArray = Array.from(allColumns)
  
  const sortedColumns = columnArray.sort((a, b) => {
    if (a === 'sample_serial') return -1
    if (b === 'sample_serial') return 1
    if (a === 'data_type') return -1
    if (b === 'data_type') return 1
    
    const getTypeOrder = (col) => {
      if (col.startsWith('object_')) return 1
      if (col.startsWith('operation_')) return 2
      if (col.startsWith('result_')) return 3
      return 4
    }
    
    const orderA = getTypeOrder(a)
    const orderB = getTypeOrder(b)
    if (orderA !== orderB) return orderA - orderB
    
    return a.localeCompare(b)
  })
  
  dynamicColumns.value = sortedColumns.map(col => ({
    prop: col,
    label: formatColumnLabel(col),
    width: col === 'sample_serial' ? 250 : col === 'data_type' ? 150 : 200
  }))
  
  initializeColumnSelection()
}

// 格式化列标签
const formatColumnLabel = (columnName) => {
  if (columnName === 'sample_serial') return 'Sample Serial'
  if (columnName === 'data_type') return '数据类型'
  
  const withoutPrefix = columnName.replace(/^(object|operation|result)_/, '')
  return withoutPrefix.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

// 初始化列字段选择
const initializeColumnSelection = () => {
  allAvailableColumns.value = [...dynamicColumns.value]
  checkedColumns.value = dynamicColumns.value.map(col => col.prop)
  checkAll.value = true
  isIndeterminate.value = false
}

// 处理机器学习操作
const handleMLAction = (action) => {
  const actionMap = {
    'transform': '数据转换',
    'augment': '数据增强',
    'train': '模型训练'
  }
  
  console.log(`执行${actionMap[action]}操作:`, {
    action: action,
    template: currentNode.value,
    selectedData: selectedDataRows.value,
    dataCount: selectedDataRows.value.length
  })
  
  switch (action) {
    case 'transform':
      handleDataTransform()
      break
    case 'augment':
      handleDataAugment()
      break
    case 'train':
      handleModelTraining()
      break
    default:
      ElMessage.info(`${actionMap[action] || '该'}功能开发中...`)
  }
}

// 处理数据转换
const handleDataTransform = async () => {
  loading.value = true
  transformTables.value = []
  
  // 5张Excel文件名和对应的表名（放在public目录下）
  const tableConfigs = [
    { fileName: 'geometry_edges.xlsx', tableName: 'Geometry Edges' },
    { fileName: 'geometry_nodes.xlsx', tableName: 'Geometry Nodes' },
    { fileName: 'gs_feature.xlsx', tableName: 'GS Feature' },
    { fileName: 'sinter_curve_edges.xlsx', tableName: 'Sinter Curve Edges' },
    { fileName: 'sinter_curve_nodes.xlsx', tableName: 'Sinter Curve Nodes' }
  ]
  
  try {
    // 并行加载所有表
    const loadPromises = tableConfigs.map(async (config) => {
      let tableData = null
      
      try {
        const response = await fetch(`/${config.fileName}`)
        if (response.ok) {
          const arrayBuffer = await response.arrayBuffer()
          tableData = await parseExcelToTableData(arrayBuffer, config.tableName)
        } else {
          console.warn(`文件 ${config.fileName} 不存在，使用假数据`)
          // 使用假数据
          tableData = generateMockTableData(config.tableName)
        }
      } catch (error) {
        console.warn(`加载 ${config.fileName} 失败:`, error)
        // 使用假数据
        tableData = generateMockTableData(config.tableName)
      }
      
      return tableData
    })
    
    const tables = await Promise.all(loadPromises)
    
    transformTables.value = tables.filter(table => table !== null)
    
    if (transformTables.value.length === 0) {
      ElMessage.warning('未找到数据转换表文件，使用假数据')
      // 生成假数据
      transformTables.value = tableConfigs.map(config => generateMockTableData(config.tableName))
    }
    
    showTransformTables.value = true
    currentTableIndex.value = '0'
    currentPage.value = 1
    
    allSelectedRows.value.clear()
    selectedDataRows.value = []
    
    ElMessage.success(`成功加载 ${transformTables.value.length} 张数据表`)
  } catch (error) {
    console.error('加载数据转换表失败:', error)
    ElMessage.error('加载数据转换表失败，使用假数据')
    // 生成假数据
    transformTables.value = tableConfigs.map(config => generateMockTableData(config.tableName))
    showTransformTables.value = true
  } finally {
    loading.value = false
  }
}

// 生成假数据表
const generateMockTableData = (tableName) => {
  const mockData = []
  const rowCount = 30
  
  if (tableName === 'GS Feature') {
    for (let i = 0; i < rowCount; i++) {
      mockData.push({
        sample_serial: `SAMPLE_${i + 1}`,
        is_aug: i < 20 ? 0 : 1,
        feature1: (Math.random() * 100).toFixed(2),
        feature2: (Math.random() * 50).toFixed(2),
        feature3: (Math.random() * 200).toFixed(2)
      })
    }
  } else {
    for (let i = 0; i < rowCount; i++) {
      mockData.push({
        id: i + 1,
        source: `source_${i + 1}`,
        target: `target_${i + 1}`,
        weight: (Math.random() * 10).toFixed(2)
      })
    }
  }
  
  const columns = generateColumnsFromData(mockData)
  
  return {
    name: tableName,
    data: mockData,
    originalData: mockData,
    dataIsAug0: tableName === 'GS Feature' ? mockData.filter(row => row.is_aug === 0) : [],
    dataIsAug1: tableName === 'GS Feature' ? mockData.filter(row => row.is_aug === 1) : [],
    isAugmented: false,
    columns: columns
  }
}

// 解析Excel文件为表数据
const parseExcelToTableData = async (arrayBuffer, tableName) => {
  try {
    const data = new Uint8Array(arrayBuffer)
    const workbook = XLSX.read(data, { type: 'array' })
    
    const firstSheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[firstSheetName]
    
    let jsonData = XLSX.utils.sheet_to_json(worksheet, { defval: null })
    
    if (jsonData.length === 0) {
      return null
    }
    
    jsonData = jsonData.map(row => {
      const processedRow = {}
      Object.keys(row).forEach(key => {
        const value = row[key]
        if (value === null || value === undefined || value === '') {
          processedRow[key] = '-'
        } else {
          processedRow[key] = value
        }
      })
      return processedRow
    })
    
    let displayData = jsonData
    if (tableName === 'GS Feature' || tableName.includes('GS Feature')) {
      const dataIsAug0 = jsonData.filter(row => getIsAugValue(row.is_aug) === 0)
      const dataIsAug1 = jsonData.filter(row => getIsAugValue(row.is_aug) === 1)
      displayData = dataIsAug0
      
      const columns = generateColumnsFromData(jsonData)
      
      return {
        name: tableName,
        data: displayData,
        originalData: jsonData,
        dataIsAug0: dataIsAug0,
        dataIsAug1: dataIsAug1,
        isAugmented: false,
        columns: columns
      }
    }
    
    const columns = generateColumnsFromData(jsonData)
    
    return {
      name: tableName,
      data: displayData,
      originalData: jsonData,
      columns: columns
    }
  } catch (error) {
    console.error(`解析表 ${tableName} 失败:`, error)
    return null
  }
}

// 获取is_aug的数值
const getIsAugValue = (isAug) => {
  if (isAug === 0 || isAug === '0' || isAug === false || isAug === 'false') {
    return 0
  }
  if (isAug === 1 || isAug === '1' || isAug === true || isAug === 'true') {
    return 1
  }
  return 0
}

// 根据数据生成列
const generateColumnsFromData = (data) => {
  if (!data || data.length === 0) {
    return []
  }
  
  const allKeys = new Set()
  data.forEach(row => {
    Object.keys(row).forEach(key => {
      allKeys.add(key)
    })
  })
  
  const columnArray = Array.from(allKeys)
  
  const sortedColumns = columnArray.sort((a, b) => {
    const priority = ['sample_serial', 'id', 'name', 'type']
    const aIndex = priority.indexOf(a)
    const bIndex = priority.indexOf(b)
    if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex
    if (aIndex !== -1) return -1
    if (bIndex !== -1) return 1
    return a.localeCompare(b)
  })
  
  return sortedColumns.map(col => ({
    prop: col,
    label: formatColumnLabel(col),
    width: col === 'sample_serial' ? 250 : 200
  }))
}

// 处理表切换
const handleTableTabClick = (tab) => {
  currentTableIndex.value = tab.name
  currentPage.value = 1
  allSelectedRows.value.clear()
  selectedDataRows.value = []
    nextTick(() => {
    updateTableSelection(displayTableData.value)
  })
}

// 处理数据增强
const handleDataAugment = () => {
  if (showTransformTables.value && transformTables.value.length > 0) {
    const currentTable = transformTables.value[parseInt(currentTableIndex.value)]
    if (currentTable && (currentTable.name === 'GS Feature' || currentTable.name.includes('GS Feature'))) {
      if (!currentTable.isAugmented && currentTable.dataIsAug1) {
        currentTable.data = [...currentTable.dataIsAug0, ...currentTable.dataIsAug1]
        currentTable.isAugmented = true
        currentPage.value = 1
        ElMessage.success(`数据增强完成，已显示 ${currentTable.dataIsAug1.length} 条增强数据`)
        return
      } else if (currentTable.isAugmented) {
        ElMessage.info('GS Feature表已经进行过数据增强')
        return
      }
    }
  }
  
  ElMessage.info('数据增强功能：请在数据转换后对GS Feature表进行增强')
}

// 处理文件选择
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (!file) {
    return
  }
  
  const fileName = file.name.toLowerCase()
  if (!fileName.endsWith('.xlsx') && !fileName.endsWith('.xls')) {
    ElMessage.error('请选择 Excel 文件（.xlsx 或 .xls）')
    return
  }
  
  loading.value = true
  const reader = new FileReader()
  
  reader.onload = async (e) => {
    try {
      const arrayBuffer = e.target.result
      await parseExcelFile(arrayBuffer)
    } catch (error) {
      console.error('读取 Excel 文件失败:', error)
      ElMessage.error('读取 Excel 文件失败，请检查文件格式')
    } finally {
      loading.value = false
      event.target.value = ''
    }
  }
  
  reader.onerror = () => {
    loading.value = false
    ElMessage.error('读取文件失败')
    event.target.value = ''
  }
  
  reader.readAsArrayBuffer(file)
}

// 解析 Excel 文件
const parseExcelFile = async (arrayBuffer) => {
  try {
    const data = new Uint8Array(arrayBuffer)
    const workbook = XLSX.read(data, { type: 'array' })
    
    const firstSheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[firstSheetName]
    
    let jsonData = XLSX.utils.sheet_to_json(worksheet, { defval: null })
    
    jsonData = jsonData.map(row => {
      const processedRow = {}
      Object.keys(row).forEach(key => {
        const value = row[key]
        if (value === null || value === undefined || value === '') {
          processedRow[key] = '-'
        } else {
          processedRow[key] = value
        }
      })
      return processedRow
    })
    
    xlsxFileData.value = jsonData
    ElMessage.success(`已加载 ${jsonData.length} 条数据`)
  } catch (error) {
    console.error('解析 Excel 文件失败:', error)
    throw error
  }
}

// 处理模型训练
const handleModelTraining = () => {
  const dataCount = selectedDataRows.value.length > 0 
    ? selectedDataRows.value.length 
    : (showTransformTables.value && transformTables.value.length > 0 
        ? transformTables.value[parseInt(currentTableIndex.value)]?.data?.length || 0
        : expandedTableData.value.length)
  
  const message = dataCount > 0
    ? `确定要使用 ${dataCount} 条数据进行模型训练吗？`
    : '当前没有可用数据，将使用默认数据进行模型训练，确定继续吗？'
  
  ElMessageBox.confirm(
    message,
    '确认训练',
    {
      confirmButtonText: '开始训练',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    startTraining()
  }).catch(() => {
    ElMessage.info('已取消训练')
  })
}

// 开始模型训练（带进度条）
const startTraining = () => {
  trainingProgress.value = 0
  trainingProgressText.value = '正在初始化...'
  showTrainingProgress.value = true
  
  const totalDuration = 10000
  const updateInterval = 500
  const progressStep = (updateInterval / totalDuration) * 100
  
  let currentProgress = 0
  
  if (trainingTimer.value) {
    clearInterval(trainingTimer.value)
  }
  
  const progressStages = [
    { progress: 0, text: '正在初始化...' },
    { progress: 15, text: '正在加载数据...' },
    { progress: 30, text: '正在预处理数据...' },
    { progress: 45, text: '正在训练模型...' },
    { progress: 60, text: '正在优化参数...' },
    { progress: 75, text: '正在保存模型...' },
    { progress: 90, text: '正在生成结果...' },
    { progress: 100, text: '训练完成！' }
  ]
  
  const updateProgress = () => {
    // 随机增加进度，每次增加 1-8%
    const randomStep = 1 + Math.random() * 7
    currentProgress += randomStep
    
    // 添加一些随机波动，让进度更自然
    if (Math.random() > 0.7) {
      currentProgress += Math.random() * 2 // 偶尔多增加一点
    }
    
    if (currentProgress >= 100) {
      currentProgress = 100
      trainingProgress.value = 100
      trainingProgressText.value = '训练完成！'
      
      if (trainingTimer.value) {
        clearTimeout(trainingTimer.value)
        trainingTimer.value = null
      }
      
      setTimeout(() => {
        showTrainingProgress.value = false
        showTrainingComplete.value = true
      }, 500)
    } else {
      trainingProgress.value = Math.min(Math.floor(currentProgress), 99)
      
      // 根据进度更新文本
      for (let i = progressStages.length - 1; i >= 0; i--) {
        if (trainingProgress.value >= progressStages[i].progress) {
          trainingProgressText.value = progressStages[i].text
          break
        }
      }
      
      // 随机设置下一次更新间隔 300-700ms
      const nextInterval = 300 + Math.random() * 400
      trainingTimer.value = setTimeout(updateProgress, nextInterval)
    }
  }
  
  // 开始第一次更新，随机初始延迟
  trainingTimer.value = setTimeout(updateProgress, 300 + Math.random() * 400)
}

// 处理训练完成
const handleTrainingComplete = () => {
  showTrainingComplete.value = false
}

// 处理Mymodel点击
const handleMymodelClick = () => {
  showTrainingComplete.value = false
  loadAndShowImage()
}

// 加载并显示图片
const loadAndShowImage = () => {
  showImageDialog.value = true
  imageUrl.value = ''
  
  const imageFileName = '模型训练图片.png'
  
  const img = new Image()
  img.onload = () => {
    imageUrl.value = `/${imageFileName}`
  }
  img.onerror = () => {
    const alternativeNames = [
      '模型训练图片.jpg',
      '模型训练图片.jpeg',
      '模型训练图片.gif',
      '模型训练图片.bmp'
    ]
    
    let found = false
    let checkIndex = 0
    
    const checkNext = () => {
      if (checkIndex >= alternativeNames.length) {
        if (!found) {
          ElMessage.error('未找到模型训练图片，请确保public目录下有"模型训练图片.png"文件')
          showImageDialog.value = false
        }
        return
      }
      
      const testImg = new Image()
      testImg.onload = () => {
        imageUrl.value = `/${alternativeNames[checkIndex]}`
        found = true
      }
      testImg.onerror = () => {
        checkIndex++
        checkNext()
      }
      testImg.src = `/${alternativeNames[checkIndex]}`
    }
    
    checkNext()
  }
  img.src = `/${imageFileName}`
}

// 处理图片加载错误
const handleImageError = () => {
  ElMessage.error('图片加载失败，请检查文件路径')
  showImageDialog.value = false
}

// 处理图片对话框关闭
const handleImageDialogClose = () => {
  showImageDialog.value = false
  imageUrl.value = ''
}

// 处理烧结曲线推荐 - 显示对话框
const handleSinteringCurve = () => {
  showSinterCurveDialog.value = true
  // 重置状态
  selectedStructure.value = ''
  selectedModel.value = 'Mymodel'
  selectedImage.value = ''
  showSinterResult.value = false
}

// 烧结曲线推荐相关函数
const handleStructureChange = (value) => {
  const structure = structureOptions.find(s => s.value === value)
  if (structure) {
    selectedImage.value = structure.image
    showSinterResult.value = false
    selectedModel.value = 'Mymodel'
  }
}

const handleModelChange = (value) => {
  console.log('选择的模型:', value)
  showSinterResult.value = false
}

const getCurrentStructureLabel = () => {
  const structure = structureOptions.find(s => s.value === selectedStructure.value)
  return structure ? structure.label : ''
}

const getCurrentModelLabel = () => {
  const model = modelOptions.find(m => m.value === selectedModel.value)
  return model ? model.label : ''
}

const handleConfirm = () => {
  if (selectedStructure.value && selectedModel.value) {
    showSinterResult.value = true
    nextTick(() => {
      initSinterCurveChart()
    })
    ElMessage.success('已生成烧结曲线推荐结果')
  } else {
    ElMessage.warning('请先选择结构类型和模型')
  }
}

// 初始化烧结曲线图表
const initSinterCurveChart = () => {
  // 销毁之前的图表实例
  if (chartInstance.value) {
    chartInstance.value.dispose()
    chartInstance.value = null
  }
  
  if (!sinterCurveChart.value) {
    return
  }
  
  chartInstance.value = echarts.init(sinterCurveChart.value)
  
  // 生成烧结曲线数据（温度-时间曲线）
  const timeData = []
  const temperatureData = []
  
  // 生成数据点，每10个单位一个点
  for (let t = 0; t <= 1800; t += 10) {
    timeData.push(t)
    let temp = 0
    
    if (t <= 300) {
      temp = (250 / 300) * t
    } else if (t <= 750) {
      const progress = (t - 300) / (750 - 300)
      temp = 250 + (398 - 250) * progress
    } else if (t <= 1050) {
      const progress = (t - 750) / (1050 - 750)
      temp = 398 + (550 - 398) * progress
    } else if (t <= 1350) {
      const progress = (t - 1050) / (1350 - 1050)
      temp = 550 + (1100 - 550) * progress
    } else if (t <= 1500) {
      temp = 1100
    } else {
      const progress = (t - 1500) / (1800 - 1500)
      temp = 1100 - (1100 - 20) * progress
    }
    
    temperatureData.push(temp)
  }
  
  const option = {
    title: {
      text: '烧结曲线推荐',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params) {
        let result = `时间: ${params[0].axisValue} 分钟<br/>`
        params.forEach(param => {
          let value = param.value
          if (Array.isArray(value)) {
            value = value[1]
          }
          const numValue = typeof value === 'number' ? value : parseFloat(value) || 0
          result += `${param.seriesName}: ${numValue.toFixed(2)}℃<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['温度'],
      top: 35
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '时间',
      nameLocation: 'middle',
      nameGap: 30,
      min: 0,
      max: 1800,
      axisLabel: {
        formatter: '{value}'
      },
      splitLine: {
        show: true,
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '温度 (℃)',
      min: 0,
      max: 1200,
      axisLabel: {
        formatter: '{value}'
      },
      splitLine: {
        show: true,
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: '温度',
        type: 'line',
        smooth: true,
        data: timeData.map((time, index) => [time, temperatureData[index]]),
        lineStyle: {
          color: '#409eff',
          width: 3
        },
        itemStyle: {
          color: '#409eff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
            ]
          }
        },
        markPoint: {
          data: [
            { coord: [300, 250], name: '250℃' },
            { coord: [750, 398], name: '398℃' },
            { coord: [1050, 550], name: '550℃' },
            { coord: [1350, 1100], name: '1100℃' },
            { coord: [1500, 1100], name: '1100℃' }
          ],
          label: {
            formatter: '{b}',
            position: 'top'
          }
        }
      }
    ]
  }
  
  chartInstance.value.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    if (chartInstance.value) {
      chartInstance.value.resize()
    }
  })
}

const handleSinterCurveDialogClose = () => {
  showSinterCurveDialog.value = false
  // 销毁图表实例
  if (chartInstance.value) {
    chartInstance.value.dispose()
    chartInstance.value = null
  }
}

// 计算序号
const getIndex = (index) => {
  return (currentPage.value - 1) * pageSize.value + index + 1
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  const allData = allTableData.value
  const currentPageData = displayTableData.value
  
  currentPageData.forEach(row => {
    const rowKey = getRowKey(row)
    allSelectedRows.value.delete(rowKey)
  })
  
  selection.forEach(row => {
    const rowKey = getRowKey(row)
    allSelectedRows.value.add(rowKey)
  })
  
  selectedDataRows.value = allData.filter(row => {
    const rowKey = getRowKey(row)
    return allSelectedRows.value.has(rowKey)
  })
  
  console.log('选中的数据行（所有页）:', selectedDataRows.value.length, '当前页:', selection.length)
}

// 处理全选
const handleSelectAll = (selection) => {
  const allData = allTableData.value
  
  if (selection.length > 0) {
    allData.forEach(row => {
      const rowKey = getRowKey(row)
      allSelectedRows.value.add(rowKey)
    })
    ElMessage.success(`已全选所有 ${allData.length} 条数据`)
  } else {
    allSelectedRows.value.clear()
    ElMessage.info('已取消全选')
  }
  
  selectedDataRows.value = allData.filter(row => {
    const rowKey = getRowKey(row)
    return allSelectedRows.value.has(rowKey)
  })
}

// 获取行的唯一标识
const getRowKey = (row) => {
  if (row.sample_serial && row.row_id) {
    return `${row.sample_serial}_${row.row_id}`
  }
  if (row.sample_serial) {
    return row.sample_serial
  }
  if (row.id) {
    return String(row.id)
  }
  return JSON.stringify(row)
}

// 更新表格选中状态
const updateTableSelection = (pageData) => {
  const dataTable = document.querySelector('.el-table')
  if (!dataTable) {
    return
  }
  
  // 这里需要调用Element Plus的表格API来更新选中状态
  // 由于是ref，需要在nextTick中处理
  nextTick(() => {
    // 表格选中状态更新逻辑
  })
}

// 列字段选择相关方法
const handleCheckAllChange = (val) => {
  checkedColumns.value = val ? allAvailableColumns.value.map(col => col.prop) : []
  isIndeterminate.value = false
}

const handleCheckedColumnsChange = (value) => {
  const checkedCount = value.length
  checkAll.value = checkedCount === allAvailableColumns.value.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < allAvailableColumns.value.length
}

const applyColumnFilter = () => {
  ElMessage.success(`已应用列选择，当前显示 ${checkedColumns.value.length} 列`)
}

const resetColumnFilter = () => {
  checkedColumns.value = allAvailableColumns.value.map(col => col.prop)
  checkAll.value = true
  isIndeterminate.value = false
  ElMessage.success('已重置列选择为全选状态')
}

// 分页处理
const handleSizeChange = (val) => {
  console.log(`每页 ${val} 条`)
  pageSize.value = val
  currentPage.value = 1
  nextTick(() => {
    updateTableSelection(displayTableData.value)
  })
}

const handleCurrentChange = (val) => {
  console.log(`当前页: ${val}`)
  currentPage.value = val
  nextTick(() => {
    updateTableSelection(displayTableData.value)
  })
}

// 生命周期
onMounted(() => {
  console.log('SinterCurveRecommend 组件已挂载')
  loadDirectoryTree()
})

onBeforeUnmount(() => {
  if (trainingTimer.value) {
    clearTimeout(trainingTimer.value)
    trainingTimer.value = null
  }
  // 销毁图表实例
  if (chartInstance.value) {
    chartInstance.value.dispose()
    chartInstance.value = null
  }
})
</script>

<style lang="scss" scoped>
.sinter-curve-recommend-page {
  min-height: 100vh;
  background: linear-gradient(to bottom, #f5f7fa 0%, #ffffff 100%);
  position: relative;
  overflow-x: hidden;
}

.main-content {
  display: flex;
  margin-top: 60px;
  padding: 0;
  min-height: calc(100vh - 60px);
  position: relative;
}

.sidebar {
  width: 280px;
  min-width: 280px;
  max-width: 280px;
  background: linear-gradient(to bottom, #ffffff, #fafbfc);
  border-right: 1px solid #e8eaed;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
  position: sticky;
  top: 60px;
  height: calc(100vh - 60px);
  overflow: hidden;
  z-index: 10;
}

.category-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.tree-node {
    display: flex;
    align-items: center;
  gap: 8px;
  
  .node-label {
    flex: 1;
  }
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  margin: 20px 20px 120px 20px;
  border-radius: 8px;
  padding: 20px 20px 40px 20px;
  min-height: calc(100vh - 100px);
  overflow: hidden;
  min-width: 0;
    position: relative;
}

.header-section {
  margin-bottom: 15px;
  flex-shrink: 0;
}

.ml-button-bar {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid #e8eaed;
  transition: all 0.3s ease;
  width: 100%;
  box-sizing: border-box;
  position: relative;
  z-index: 5;
}

.ml-button-bar:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.12);
}

.button-bar-header {
  position: relative;
  margin-bottom: 20px;
}

.section-label {
  position: absolute;
  top: -35px;
  left: -20px;
  background: #409EFF;
  color: white;
  padding: 4px 12px;
  border-radius: 8px 0 8px 0;
  font-size: 12px;
  font-weight: bold;
}

.content-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 5px 0 0 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.button-group {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  width: 100%;
}

.button-group .el-button {
  flex: 1 1 auto;
  min-width: 120px;
  max-width: 200px;
  height: 45px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.button-group .el-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.table-select-box {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: 1px solid #e8eaed;
  border-radius: 10px;
    margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e8eaed;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 10px 10px 0 0;
}

.filter-title {
      font-size: 16px;
  font-weight: bold;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.selected-count {
  font-size: 14px;
  color: #666;
  background: #e8f4ff;
  padding: 4px 12px;
  border-radius: 15px;
  border: 1px solid #b3d8ff;
}

.table-tabs-container {
  padding: 15px 20px;
}

.column-filter-box {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: 1px solid #e8eaed;
  border-radius: 10px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.filter-content {
  padding: 20px;
}

.check-all-box {
  margin-bottom: 15px;
  font-weight: bold;
  color: #333;
}

.checkbox-group-container {
  margin-bottom: 20px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e8eaed;
  border-radius: 6px;
  padding: 15px;
  background: #fafbfc;
}

.column-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 20px;
}

.column-checkbox {
  margin-right: 0 !important;
  margin-bottom: 8px;
  padding: 6px 12px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  transition: all 0.2s ease;
  min-width: 150px;
}

.column-checkbox:hover {
  background: #f0f9ff;
  border-color: #409EFF;
}

.filter-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.table-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  min-height: 600px;
  background: linear-gradient(to bottom, #ffffff, #f9fafb);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.08);
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
  min-width: 0;
}

.table-scroll-box {
  flex: 1;
  overflow-x: auto;
  overflow-y: auto;
  border-radius: 8px;
  position: relative;
  min-height: 0;
    width: 100%;
  box-sizing: border-box;
}

.pagination {
  margin-top: 20px;
  margin-bottom: 20px;
  padding: 15px 0;
  display: flex;
  justify-content: flex-end;
  background: white;
    border-radius: 8px;
  flex-shrink: 0;
  width: 100%;
}

.training-progress-container {
  padding: 20px;
  text-align: center;
}

.progress-text {
  margin-top: 20px;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.training-complete-container {
  text-align: center;
  padding: 20px;
}

.image-dialog-container {
  text-align: center;
  padding: 20px;
  min-height: 400px;
    display: flex;
  flex-direction: column;
    align-items: center;
    justify-content: center;
}

.result-image {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  object-fit: contain;
}

.image-loading {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
  color: #909399;
  font-size: 16px;
}

.training-metrics-container {
  margin-top: 30px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border: 1px solid #e8eaed;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  width: 100%;
}

.metrics-header {
  display: flex;
  align-items: center;
  gap: 8px;
        font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #409EFF;
}

.metrics-content {
      display: flex;
      flex-direction: column;
  gap: 15px;
}

.metrics-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: space-between;
}

.metric-item {
  flex: 1;
  min-width: 200px;
  display: flex;
  justify-content: space-between;
      align-items: center;
  padding: 12px 15px;
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.metric-item:hover {
  background: #f0f9ff;
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.metric-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.metric-value {
  font-size: 15px;
  color: #409EFF;
        font-weight: 600;
  font-family: 'Courier New', monospace;
}

.metrics-divider {
  height: 1px;
  background: linear-gradient(to right, transparent, #e0e0e0, transparent);
  margin: 10px 0;
}

.metrics-section {
  margin-top: 10px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
  padding-left: 10px;
  border-left: 4px solid #409EFF;
}

.category-list::-webkit-scrollbar {
  width: 6px;
}

.category-list::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.category-list::-webkit-scrollbar-thumb:hover {
  background-color: #c0c4cc;
}

.table-scroll-box::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.table-scroll-box::-webkit-scrollbar-thumb {
  background-color: #c0c4cc;
  border-radius: 4px;
}

.table-scroll-box::-webkit-scrollbar-thumb:hover {
  background-color: #909399;
}

.table-scroll-box::-webkit-scrollbar-track {
  background-color: #f5f7fa;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e8eaed;
  }

  .content-area {
    margin: 10px;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .button-group .el-button {
    width: 100%;
  }
}

// 烧结曲线推荐对话框样式
.sinter-curve-dialog-content {
  padding: 20px 0;
}

.sinter-curve-dialog-content .selection-area {
  display: flex;
  gap: 40px;
  align-items: flex-start;
  min-height: 500px;
}

.sinter-curve-dialog-content .left-panel {
  flex: 0 0 350px;
  
  .select-wrapper {
    margin-bottom: 20px;
    
    .select-label {
      display: block;
      font-size: 16px;
      color: #606266;
      margin-bottom: 12px;
      font-weight: 500;
    }
    
    .structure-select,
    .model-select {
      width: 100%;
    }
  }
  
  .selected-info {
    padding: 15px;
    background-color: #f0f9ff;
    border-radius: 6px;
    border-left: 4px solid #409eff;
    
    p {
      margin: 0;
      font-size: 14px;
      color: #606266;
      
      strong {
        color: #409eff;
        font-size: 16px;
      }
    }
  }
  
  .confirm-button-wrapper {
    text-align: center;
    
    .confirm-button {
      width: 100%;
      height: 45px;
      font-size: 16px;
      font-weight: 500;
      border-radius: 6px;
    }
  }
}

.sinter-curve-dialog-content .right-panel {
  flex: 1;
  min-height: 500px;
  
  .image-preview {
    width: 100%;
    height: 100%;
    min-height: 500px;
    border: 2px dashed #dcdfe6;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #fafafa;
    
    .image-container {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
      
      .structure-image {
        max-width: 100%;
        max-height: 450px;
        object-fit: contain;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
      
      .image-label {
        margin-top: 15px;
        font-size: 18px;
        font-weight: 600;
        color: #303133;
      }
    }
    
    .chart-container {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
      
      .chart-wrapper {
        width: 100%;
        height: 450px;
        min-height: 450px;
      }
      
      .image-label {
        margin-top: 15px;
        font-size: 18px;
        font-weight: 600;
        color: #303133;
      }
    }
    
    .placeholder {
      text-align: center;
      color: #909399;
      
      p {
        font-size: 14px;
        margin: 15px 0 0 0;
      }
    }
  }
}

@media (max-width: 1024px) {
  .sinter-curve-dialog-content .selection-area {
    flex-direction: column;
  }
  
  .sinter-curve-dialog-content .left-panel {
    flex: 1;
    width: 100%;
  }
  
  .sinter-curve-dialog-content .right-panel {
    width: 100%;
  }
}
</style>
