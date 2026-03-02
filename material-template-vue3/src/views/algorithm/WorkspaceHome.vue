<template>
  <div class="workspace-container">
    <!-- 顶部导航栏 -->
    <header class="workspace-header">
      <div class="header-left">
        <el-tooltip content="返回首页">
          <el-button class="home-btn" @click="goHome">
            <el-icon><HomeFilled /></el-icon>
          </el-button>
        </el-tooltip>
        <el-divider direction="vertical" />
        <div class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <ellipse cx="24" cy="12" rx="16" ry="6" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M8 12v24c0 3.3 7.2 6 16 6s16-2.7 16-6V12" stroke="currentColor" stroke-width="2" fill="none"/>
              <circle cx="24" cy="24" r="4" fill="currentColor"/>
            </svg>
          </div>
          <span class="logo-text">算法工作台</span>
        </div>
      </div>
      
      <div class="header-center">
        <div class="workflow-title" v-if="currentWorkflow">
          <input 
            v-model="currentWorkflow.name" 
            class="title-input"
            @blur="saveCurrentWorkflow"
          />
          <span class="save-status" :class="{ saved: isSaved }">
            {{ isSaved ? '已保存' : '未保存' }}
          </span>
        </div>
        <div v-else class="no-workflow-hint">
          请选择或新建一个工作流
        </div>
      </div>
      
      <div class="header-right">
        <template v-if="currentWorkflow">
          <el-button-group class="toolbar-group">
            <el-tooltip content="撤销">
              <el-button :icon="RefreshLeft" @click="undo" :disabled="!canUndo" />
            </el-tooltip>
            <el-tooltip content="重做">
              <el-button :icon="RefreshRight" @click="redo" :disabled="!canRedo" />
            </el-tooltip>
          </el-button-group>
          
          <el-button-group class="toolbar-group">
            <el-tooltip content="放大">
              <el-button :icon="ZoomIn" @click="zoomIn" />
            </el-tooltip>
            <el-tooltip content="缩小">
              <el-button :icon="ZoomOut" @click="zoomOut" />
            </el-tooltip>
            <el-tooltip content="适应画布">
              <el-button :icon="FullScreen" @click="fitView" />
            </el-tooltip>
          </el-button-group>
          
          <el-divider direction="vertical" />
          
          <el-button @click="exportWorkflow">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
          <el-button type="success" @click="runWorkflow">
            <el-icon><VideoPlay /></el-icon>
            运行
          </el-button>
          <el-button type="primary" @click="saveCurrentWorkflow">
            <el-icon><Check /></el-icon>
            保存
          </el-button>
        </template>
        
        <el-dropdown trigger="click" @command="handleUserCommand">
          <el-avatar :size="36" class="user-avatar">
            {{ userInitial }}
          </el-avatar>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="home">返回首页</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <div class="workspace-main">
      <!-- 左侧目录面板 -->
      <aside class="sidebar">
        <el-scrollbar class="sidebar-scroll">
          <!-- 组件库 -->
          <div class="sidebar-section">
            <div class="section-title">
              <div class="title-icon" style="background: linear-gradient(135deg, #667eea, #764ba2)">
                <el-icon><Grid /></el-icon>
              </div>
              <span>组件库</span>
            </div>
            
            <el-collapse v-model="activeComponents" class="component-collapse">
              <el-collapse-item 
                v-for="category in componentItems" 
                :key="category.id"
                :name="category.id"
              >
                <template #title>
                  <div class="collapse-title">
                    <el-icon><component :is="category.icon" /></el-icon>
                    <span>{{ category.label }}</span>
                  </div>
                </template>
                
                <div class="component-list">
                  <div 
                    v-for="item in category.children" 
                    :key="item.id"
                    class="component-item"
                    draggable="true"
                    @dragstart="onComponentDragStart($event, item)"
                    @dragend="onDragEnd"
                  >
                    <div class="item-icon" :style="{ background: item.color }">
                      <el-icon><component :is="item.icon" /></el-icon>
                    </div>
                    <div class="item-info">
                      <span class="item-name">{{ item.label }}</span>
                      <span class="item-desc">{{ item.description }}</span>
                    </div>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
          
          <!-- 工作空间 -->
          <div class="sidebar-section">
            <div class="section-title">
              <div class="title-icon" style="background: linear-gradient(135deg, #10b981, #34d399)">
                <el-icon><Folder /></el-icon>
              </div>
              <span>工作空间</span>
              <el-tooltip content="新建工作流">
                <el-button 
                  :icon="Plus" 
                  size="small" 
                  circle 
                  class="add-btn"
                  @click="createWorkflow"
                />
              </el-tooltip>
            </div>
            
            <div class="workflow-list">
              <div 
                v-for="workflow in workflows" 
                :key="workflow.id"
                class="workflow-item"
                :class="{ active: currentWorkflow?.id === workflow.id }"
                @click="openWorkflow(workflow)"
              >
                <div class="item-icon" style="background: rgba(102, 126, 234, 0.2); color: #667eea">
                  <el-icon><Connection /></el-icon>
                </div>
                <span class="item-name">{{ workflow.name }}</span>
                <el-dropdown 
                  trigger="click" 
                  @command="(cmd) => handleWorkflowCommand(cmd, { data: workflow })"
                  @click.stop
                >
                  <el-icon class="more-btn" @click.stop><MoreFilled /></el-icon>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="rename">
                        <el-icon><Edit /></el-icon>重命名
                      </el-dropdown-item>
                      <el-dropdown-item command="copy">
                        <el-icon><CopyDocument /></el-icon>复制
                      </el-dropdown-item>
                      <el-dropdown-item command="export">
                        <el-icon><Download /></el-icon>导出
                      </el-dropdown-item>
                      <el-dropdown-item command="delete" divided>
                        <el-icon><Delete /></el-icon>删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
              
              <div v-if="workflows.length === 0" class="empty-workflows">
                <p>暂无工作流</p>
                <el-button type="primary" size="small" @click="createWorkflow">
                  <el-icon><Plus /></el-icon>
                  新建
                </el-button>
              </div>
            </div>
          </div>
          
          <!-- 数据集目录 -->
          <div class="sidebar-section">
            <div class="section-title">
              <div class="title-icon" style="background: linear-gradient(135deg, #f59e0b, #f97316)">
                <el-icon><FolderOpened /></el-icon>
              </div>
              <span>数据集</span>
              <el-tooltip content="上传本地文件">
                <el-button 
                  :icon="Upload" 
                  size="small" 
                  circle 
                  class="add-btn"
                  @click="triggerFileUpload"
                />
              </el-tooltip>
            </div>
            
            <!-- 隐藏的文件上传input -->
            <input 
              ref="fileInputRef"
              type="file" 
              multiple 
              style="display: none"
              @change="handleLocalFileSelect"
            />
            
            <div class="dataset-list">
              <div 
                v-for="dataset in datasets" 
                :key="dataset.id"
                class="dataset-item"
                draggable="true"
                @dragstart="onDatasetDragStart($event, dataset)"
                @dragend="onDragEnd"
              >
                <div class="item-icon" style="background: rgba(245, 158, 11, 0.2); color: #f59e0b">
                  <el-icon><FolderOpened /></el-icon>
                </div>
                <div class="item-info">
                  <span class="item-name">{{ dataset.name }}</span>
                  <span class="item-desc">{{ dataset.files.length }} 个文件</span>
                </div>
                <el-dropdown 
                  trigger="click" 
                  @command="(cmd) => handleDatasetCommand(cmd, dataset)"
                  @click.stop
                >
                  <el-icon class="more-btn" @click.stop><MoreFilled /></el-icon>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="view">
                        <el-icon><View /></el-icon>查看文件
                      </el-dropdown-item>
                      <el-dropdown-item command="rename">
                        <el-icon><Edit /></el-icon>重命名
                      </el-dropdown-item>
                      <el-dropdown-item command="delete" divided>
                        <el-icon><Delete /></el-icon>删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
              
              <div v-if="datasets.length === 0" class="empty-workflows">
                <p>暂无数据集</p>
                <el-button type="primary" size="small" @click="triggerFileUpload">
                  <el-icon><Upload /></el-icon>
                  上传文件
                </el-button>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </aside>

      <!-- 右侧画布区域 -->
      <main class="canvas-area">
        <div v-if="currentWorkflow" class="canvas-wrapper">
          <div ref="canvasRef" class="lf-canvas"></div>
          
          <!-- 缩放显示 -->
          <div class="zoom-indicator">
            {{ Math.round(zoomLevel * 100) }}%
          </div>
          
          <!-- 小地图 -->
          <div v-show="showMinimap" ref="minimapRef" class="minimap"></div>
        </div>
        
        <!-- 空状态 -->
        <div v-else class="empty-state">
          <div class="empty-icon">
            <el-icon :size="80"><Connection /></el-icon>
          </div>
          <h2>开始构建您的工作流</h2>
          <p>从左侧选择一个工作流，或创建新的工作流</p>
          <el-button type="primary" size="large" @click="createWorkflow">
            <el-icon><Plus /></el-icon>
            新建工作流
          </el-button>
        </div>
      </main>

      <!-- 右侧属性面板 -->
      <aside class="property-panel" :class="{ visible: selectedNode }">
        <template v-if="selectedNode">
          <div class="panel-header">
            <h3>节点属性</h3>
            <el-button text :icon="Close" @click="selectedNode = null" />
          </div>
          
          <el-scrollbar class="panel-body">
            <el-form label-position="top" class="property-form">
              <el-form-item label="节点名称">
                <el-input v-model="selectedNode.properties.label" @change="updateNodeProperty" />
              </el-form-item>
              
              <el-form-item label="节点描述">
                <el-input 
                  v-model="selectedNode.properties.description" 
                  type="textarea" 
                  :rows="2"
                  @change="updateNodeProperty" 
                />
              </el-form-item>
              
              <el-divider>参数配置</el-divider>
              
              <!-- 数据源节点 -->
              <template v-if="selectedNode.properties.nodeType === 'data-source'">
                <el-form-item label="数据源类型">
                  <el-select v-model="selectedNode.properties.sourceType" style="width: 100%">
                    <el-option label="模板数据" value="template" />
                    <el-option label="上传文件" value="file" />
                    <el-option label="数据库" value="database" />
                  </el-select>
                </el-form-item>
                <el-form-item label="选择模板" v-if="selectedNode.properties.sourceType === 'template'">
                  <el-select v-model="selectedNode.properties.templateId" style="width: 100%" placeholder="请选择">
                    <el-option label="材料基础信息模板" value="1" />
                    <el-option label="力学性能测试模板" value="2" />
                    <el-option label="生物相容性模板" value="3" />
                  </el-select>
                </el-form-item>
              </template>
              
              <!-- 数据处理节点 -->
              <template v-if="selectedNode.properties.nodeType === 'data-clean'">
                <el-form-item label="清洗规则">
                  <el-checkbox-group v-model="selectedNode.properties.cleanRules">
                    <el-checkbox label="remove-null">移除空值</el-checkbox>
                    <el-checkbox label="remove-duplicate">移除重复</el-checkbox>
                    <el-checkbox label="fix-format">修复格式</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
              </template>
              
              <!-- 数据转换节点 -->
              <template v-if="selectedNode.properties.nodeType === 'data-transform'">
                <el-form-item label="转换操作">
                  <el-select v-model="selectedNode.properties.operation" style="width: 100%">
                    <el-option label="字段映射" value="mapping" />
                    <el-option label="数据聚合" value="aggregate" />
                    <el-option label="数据拆分" value="split" />
                    <el-option label="格式转换" value="format" />
                  </el-select>
                </el-form-item>
              </template>
              
              <!-- 机器学习节点 -->
              <template v-if="selectedNode.properties.nodeType === 'ml-model'">
                <el-form-item label="模型类型">
                  <el-select v-model="selectedNode.properties.modelType" style="width: 100%">
                    <el-option label="线性回归" value="linear" />
                    <el-option label="随机森林" value="random-forest" />
                    <el-option label="神经网络" value="neural-network" />
                    <el-option label="支持向量机" value="svm" />
                    <el-option label="XGBoost" value="xgboost" />
                  </el-select>
                </el-form-item>
                <el-form-item label="训练轮次">
                  <el-input-number v-model="selectedNode.properties.epochs" :min="1" :max="1000" style="width: 100%" />
                </el-form-item>
                <el-form-item label="学习率">
                  <el-input-number v-model="selectedNode.properties.learningRate" :min="0.0001" :max="1" :step="0.001" :precision="4" style="width: 100%" />
                </el-form-item>
              </template>
              
              <!-- 输出节点 -->
              <template v-if="selectedNode.properties.nodeType === 'data-output'">
                <el-form-item label="输出格式">
                  <el-select v-model="selectedNode.properties.format" style="width: 100%">
                    <el-option label="JSON" value="json" />
                    <el-option label="CSV" value="csv" />
                    <el-option label="Excel" value="excel" />
                  </el-select>
                </el-form-item>
                <el-form-item label="文件名">
                  <el-input v-model="selectedNode.properties.fileName" placeholder="输出文件名" />
                </el-form-item>
              </template>
            </el-form>
          </el-scrollbar>
        </template>
        
        <div v-else class="empty-panel">
          <el-icon :size="40"><Select /></el-icon>
          <p>选择节点查看属性</p>
        </div>
      </aside>
    </div>
    
    <!-- 新建工作流对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建工作流" width="450px" class="create-dialog">
      <el-form :model="newWorkflowForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="newWorkflowForm.name" placeholder="请输入工作流名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newWorkflowForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmCreateWorkflow">创建</el-button>
      </template>
    </el-dialog>
    
    <!-- 运行结果抽屉 -->
    <el-drawer v-model="showRunDrawer" title="运行结果" size="400px" direction="rtl">
      <el-timeline>
        <el-timeline-item
          v-for="(step, index) in runSteps"
          :key="index"
          :type="step.status"
          :timestamp="step.time"
        >
          <h4>{{ step.name }}</h4>
          <p>{{ step.message }}</p>
          <el-progress 
            v-if="step.status === 'primary'" 
            :percentage="step.progress" 
            :stroke-width="6"
          />
        </el-timeline-item>
      </el-timeline>
    </el-drawer>
    
    <!-- 查看文件对话框 -->
    <el-dialog v-model="showFilesDialog" :title="currentViewDataset?.name + ' - 文件列表'" width="600px" class="create-dialog">
      <el-table :data="currentViewDataset?.files || []" style="width: 100%" max-height="400">
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="size" label="大小" width="100">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="uploadTime" label="上传时间" width="180" />
        <el-table-column label="操作" width="80">
          <template #default="{ row, $index }">
            <el-button type="danger" size="small" text @click="removeFileFromDataset($index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="showFilesDialog = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <!-- 底部日志面板 -->
    <transition name="slide-up">
      <div v-if="showLogPanel" class="log-panel">
        <div class="log-header">
          <div class="log-title">
            <el-icon><Document /></el-icon>
            <span>运行日志</span>
            <el-tag v-if="isUploading" type="warning" size="small">上传中...</el-tag>
            <el-tag v-else-if="uploadSuccess" type="success" size="small">完成</el-tag>
          </div>
          <div class="log-actions">
            <el-button text size="small" @click="clearLogs">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
            <el-button text size="small" @click="showLogPanel = false">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>
        <div class="log-content" ref="logContentRef">
          <div v-for="(log, index) in logs" :key="index" class="log-item" :class="log.type">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
          <div v-if="logs.length === 0" class="log-empty">暂无日志</div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted, nextTick, shallowRef, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import {
  Plus, RefreshLeft, RefreshRight, ZoomIn, ZoomOut, FullScreen,
  Download, VideoPlay, Check, Close, Select, MoreFilled, Edit,
  CopyDocument, Delete, Connection, HomeFilled, ArrowLeft,
  // 组件图标
  Folder, Document, DataLine, DataBoard, DataAnalysis,
  Filter, Operation, ScaleToOriginal, Coin, SetUp,
  Cpu, TrendCharts, MagicStick, Histogram, PieChart,
  Upload, Box, CircleCheck, Bell, Grid, FolderOpened, View
} from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()

// Refs
const canvasRef = ref(null)
const minimapRef = ref(null)
const lf = shallowRef(null)

// User
const userInitial = computed(() => (userStore.userName || 'U').charAt(0).toUpperCase())

// State
const currentWorkflow = ref(null)
const selectedNode = ref(null)
const isSaved = ref(true)
const canUndo = ref(false)
const canRedo = ref(false)
const zoomLevel = ref(1)
const showMinimap = ref(false)
const showCreateDialog = ref(false)
const showRunDrawer = ref(false)
const runSteps = ref([])
const activeComponents = ref(['comp-datasource', 'comp-process']) // 默认展开的分类

const newWorkflowForm = reactive({
  name: '',
  description: ''
})

// 数据集相关
const datasets = ref([])
const showFilesDialog = ref(false)
const currentViewDataset = ref(null)
const fileInputRef = ref(null)

// 日志面板相关
const showLogPanel = ref(false)
const logs = ref([])
const logContentRef = ref(null)
const isUploading = ref(false)
const uploadSuccess = ref(false)

// 工作流列表
const workflows = ref([])

// 组件定义
const componentItems = [
  {
    id: 'comp-datasource',
    label: '数据源',
    icon: markRaw(Folder),
    isCategory: true,
    children: [
      { id: 'data-source', label: '数据输入', icon: markRaw(Document), isComponent: true, color: '#667eea', description: '从模板或文件读取数据' },
      { id: 'database-query', label: '数据库查询', icon: markRaw(DataBoard), isComponent: true, color: '#06b6d4', description: '从数据库查询数据' },
      { id: 'api-fetch', label: 'API数据', icon: markRaw(DataLine), isComponent: true, color: '#8b5cf6', description: '从API接口获取数据' }
    ]
  },
  {
    id: 'comp-process',
    label: '数据处理',
    icon: markRaw(Operation),
    isCategory: true,
    children: [
      { id: 'data-clean', label: '数据清洗', icon: markRaw(Filter), isComponent: true, color: '#10b981', description: '清理缺失值和异常值' },
      { id: 'data-transform', label: '数据转换', icon: markRaw(ScaleToOriginal), isComponent: true, color: '#f59e0b', description: '转换数据格式和结构' },
      { id: 'data-filter', label: '数据过滤', icon: markRaw(Filter), isComponent: true, color: '#ec4899', description: '按条件筛选数据' },
      { id: 'data-merge', label: '数据合并', icon: markRaw(Coin), isComponent: true, color: '#ef4444', description: '合并多个数据源' }
    ]
  },
  {
    id: 'comp-algorithm',
    label: '算法模型',
    icon: markRaw(Cpu),
    isCategory: true,
    children: [
      { id: 'feature-extract', label: '特征工程', icon: markRaw(SetUp), isComponent: true, color: '#14b8a6', description: '提取和选择特征' },
      { id: 'ml-model', label: '机器学习', icon: markRaw(TrendCharts), isComponent: true, color: '#667eea', description: '训练机器学习模型' },
      { id: 'model-predict', label: '模型预测', icon: markRaw(MagicStick), isComponent: true, color: '#6366f1', description: '使用模型进行预测' }
    ]
  },
  {
    id: 'comp-visual',
    label: '可视化',
    icon: markRaw(PieChart),
    isCategory: true,
    children: [
      { id: 'chart-bindata', label: '图表展示', icon: markRaw(Histogram), isComponent: true, color: '#f97316', description: '生成数据可视化图表' },
      { id: 'report-gen', label: '报告生成', icon: markRaw(Document), isComponent: true, color: '#84cc16', description: '生成分析报告' }
    ]
  },
  {
    id: 'comp-output',
    label: '输出',
    icon: markRaw(Upload),
    isCategory: true,
    children: [
      { id: 'data-output', label: '数据导出', icon: markRaw(Download), isComponent: true, color: '#0ea5e9', description: '导出处理后的数据' },
      { id: 'data-save', label: '数据保存', icon: markRaw(Box), isComponent: true, color: '#a855f7', description: '保存到数据库' },
      { id: 'notify', label: '通知', icon: markRaw(Bell), isComponent: true, color: '#22c55e', description: '发送完成通知' }
    ]
  }
]

// 组件拖拽开始
const onComponentDragStart = (e, data) => {
  e.dataTransfer.effectAllowed = 'copy'
  e.dataTransfer.setData('node-type', data.id)
  e.dataTransfer.setData('node-data', JSON.stringify({
    type: data.id,
    name: data.label,
    description: data.description,
    color: data.color
  }))
  // 设置拖拽图像
  const dragImage = e.target.cloneNode(true)
  dragImage.style.position = 'absolute'
  dragImage.style.top = '-1000px'
  document.body.appendChild(dragImage)
  e.dataTransfer.setDragImage(dragImage, 0, 0)
  setTimeout(() => document.body.removeChild(dragImage), 0)
}

const onDragEnd = () => {
  // 拖拽结束
}

// 创建工作流
const createWorkflow = () => {
  newWorkflowForm.name = ''
  newWorkflowForm.description = ''
  showCreateDialog.value = true
}

const confirmCreateWorkflow = () => {
  if (!newWorkflowForm.name.trim()) {
    ElMessage.warning('请输入工作流名称')
    return
  }
  
  const newWf = {
    id: 'wf-' + Date.now(),
    name: newWorkflowForm.name,
    description: newWorkflowForm.description,
    data: { nodes: [], edges: [] },
    createTime: new Date().toISOString(),
    updateTime: new Date().toISOString()
  }
  
  workflows.value.push(newWf)
  saveWorkflowsToStorage()
  showCreateDialog.value = false
  
  // 打开新创建的工作流
  openWorkflow(newWf)
  ElMessage.success('创建成功')
}

// 打开工作流
const openWorkflow = async (workflow) => {
  // 保存当前工作流
  if (currentWorkflow.value && !isSaved.value) {
    try {
      await ElMessageBox.confirm('当前工作流未保存，是否保存？', '提示', {
        distinguishCancelAndClose: true,
        confirmButtonText: '保存',
        cancelButtonText: '不保存'
      })
      saveCurrentWorkflow()
    } catch (action) {
      if (action === 'close') return
    }
  }
  
  currentWorkflow.value = workflow
  selectedNode.value = null
  isSaved.value = true
  
  await nextTick()
  
  if (lf.value) {
    lf.value.render(workflow.data || {})
  } else {
    initLogicFlow()
  }
}

// 初始化 LogicFlow
const initLogicFlow = async () => {
  if (!canvasRef.value) return
  
  try {
    const LogicFlow = (await import('@logicflow/core')).default
    const { HtmlNode, HtmlNodeModel } = await import('@logicflow/core')
    await import('@logicflow/core/dist/index.css')
    
    const { SelectionSelect, Menu, Snapshot } = await import('@logicflow/extension')
    await import('@logicflow/extension/dist/index.css')
    
    // 节点图标 SVG 映射
    const nodeIcons = {
      'data-source': `<path d="M12 2C6.48 2 2 4.69 2 8v8c0 3.31 4.48 6 10 6s10-2.69 10-6V8c0-3.31-4.48-6-10-6zm0 2c4.42 0 8 1.79 8 4s-3.58 4-8 4-8-1.79-8-4 3.58-4 8-4z"/>`,
      'data-clean': `<path d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"/>`,
      'data-process': `<path d="M14 4l2.29 2.29-2.88 2.88 1.42 1.42 2.88-2.88L20 10V4h-6zm-4 0H4v6l2.29-2.29 4.71 4.7V20h2v-8.41l-5.29-5.3L10 4z"/>`,
      'feature-eng': `<path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>`,
      'model-train': `<path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>`,
      'model-eval': `<path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>`,
      'data-export': `<path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>`,
      'default': `<circle cx="12" cy="12" r="8"/>`
    }
    
    // 自定义带颜色的节点
    class ColorNode extends HtmlNode {
      setHtml(rootEl) {
        const { properties } = this.props.model
        const color = properties.color || '#667eea'
        const label = properties.label || '节点'
        
        rootEl.innerHTML = `
          <div class="custom-node" style="border-color: ${color}; background: ${color}">
            <span class="node-label">${label}</span>
          </div>
        `
      }
    }
    
    class ColorNodeModel extends HtmlNodeModel {
      setAttributes() {
        this.width = 140
        this.height = 40
        this.text.editable = false
      }
      
      getDefaultAnchor() {
        const { x, y, width, height } = this
        return [
          { x: x - width / 2, y, type: 'left', id: `${this.id}_left` },
          { x: x + width / 2, y, type: 'right', id: `${this.id}_right` },
          { x, y: y - height / 2, type: 'top', id: `${this.id}_top` },
          { x, y: y + height / 2, type: 'bottom', id: `${this.id}_bottom` }
        ]
      }
    }
    
    LogicFlow.use(SelectionSelect)
    LogicFlow.use(Menu)
    LogicFlow.use(Snapshot)
    
    lf.value = new LogicFlow({
      container: canvasRef.value,
      grid: {
        size: 20,
        visible: true,
        type: 'dot',
        config: {
          color: 'rgba(102, 126, 234, 0.2)'
        }
      },
      background: {
        backgroundColor: '#0f172a'
      },
      keyboard: {
        enabled: true
      },
      edgeType: 'bezier',
      style: {
        rect: {
          radius: 8,
          stroke: 'rgba(102, 126, 234, 0.6)',
          strokeWidth: 2
        },
        bezier: {
          stroke: 'rgba(102, 126, 234, 0.8)',
          strokeWidth: 2
        },
        polyline: {
          stroke: 'rgba(102, 126, 234, 0.8)',
          strokeWidth: 2
        },
        nodeText: {
          color: '#fff',
          fontSize: 14
        },
        edgeText: {
          color: '#fff',
          fontSize: 12
        }
      }
    })
    
    // 配置节点右键菜单
    lf.value.extension.menu.setMenuConfig({
      nodeMenu: [
        {
          text: '删除节点',
          callback: (node) => {
            lf.value.deleteNode(node.id)
            if (selectedNode.value?.id === node.id) {
              selectedNode.value = null
            }
            ElMessage.success('节点已删除')
          }
        },
        {
          text: '复制节点',
          callback: (node) => {
            const newNode = {
              ...node,
              id: 'node_' + Date.now(),
              x: node.x + 50,
              y: node.y + 50
            }
            lf.value.addNode(newNode)
            ElMessage.success('节点已复制')
          }
        }
      ],
      edgeMenu: [
        {
          text: '删除连线',
          callback: (edge) => {
            lf.value.deleteEdge(edge.id)
            ElMessage.success('连线已删除')
          }
        }
      ],
      graphMenu: []
    })
    
    // 注册自定义节点
    lf.value.register({
      type: 'color-node',
      view: ColorNode,
      model: ColorNodeModel
    })
    
    // 渲染数据
    if (currentWorkflow.value?.data) {
      lf.value.render(currentWorkflow.value.data)
    } else {
      lf.value.render({})
    }
    
    // 监听事件
    lf.value.on('node:click', ({ data }) => {
      selectedNode.value = JSON.parse(JSON.stringify(data))
    })
    
    lf.value.on('blank:click', () => {
      selectedNode.value = null
    })
    
    lf.value.on('history:change', ({ data }) => {
      canUndo.value = data.undoAble
      canRedo.value = data.redoAble
      isSaved.value = false
    })
    
    lf.value.on('node:add', () => {
      isSaved.value = false
    })
    
    lf.value.on('edge:add', () => {
      isSaved.value = false
    })
    
    lf.value.on('node:delete', () => {
      isSaved.value = false
    })
    
    lf.value.on('edge:delete', () => {
      isSaved.value = false
    })
    
    lf.value.on('graph:transform', ({ transform }) => {
      zoomLevel.value = transform.SCALE_X
    })
    
    // 监听画布拖放
    canvasRef.value.addEventListener('drop', onDrop)
    canvasRef.value.addEventListener('dragover', (e) => e.preventDefault())
    
    zoomLevel.value = lf.value.getTransform().SCALE_X
    
  } catch (error) {
    console.error('LogicFlow 初始化失败:', error)
    ElMessage.error('工作流编辑器加载失败')
  }
}

// 拖放到画布
const onDrop = (e) => {
  e.preventDefault()
  if (!lf.value || !currentWorkflow.value) return
  
  const nodeType = e.dataTransfer.getData('node-type')
  const nodeDataStr = e.dataTransfer.getData('node-data')
  
  if (!nodeType || !nodeDataStr) return
  
  const nodeData = JSON.parse(nodeDataStr)
  const { domOverlayPosition } = lf.value.getPointByClient(e.clientX, e.clientY)
  
  // 创建带颜色的节点
  const nodeId = 'node_' + Date.now()
  
  // 数据集节点
  if (nodeType === 'dataset-node') {
    lf.value.addNode({
      id: nodeId,
      type: 'color-node',
      x: domOverlayPosition.x,
      y: domOverlayPosition.y,
      properties: {
        nodeType: nodeType,
        label: nodeData.name,
        description: nodeData.description,
        color: nodeData.color,
        datasetId: nodeData.datasetId
      }
    })
  } else {
    lf.value.addNode({
      id: nodeId,
      type: 'color-node',
      x: domOverlayPosition.x,
      y: domOverlayPosition.y,
      properties: {
        nodeType: nodeType,
        label: nodeData.name,
        description: nodeData.description,
        color: nodeData.color,
        // 默认属性
        sourceType: 'template',
        templateId: '',
        cleanRules: [],
        operation: 'mapping',
        modelType: 'linear',
        epochs: 100,
        learningRate: 0.001,
        format: 'json',
        fileName: 'output'
      }
    })
  }
  
  isSaved.value = false
}

// 更新节点属性
const updateNodeProperty = () => {
  if (selectedNode.value && lf.value) {
    lf.value.setProperties(selectedNode.value.id, selectedNode.value.properties)
    // 更新节点文本
    lf.value.updateText(selectedNode.value.id, selectedNode.value.properties.label)
    isSaved.value = false
  }
}

// 保存当前工作流
const saveCurrentWorkflow = () => {
  if (!currentWorkflow.value || !lf.value) return
  
  currentWorkflow.value.data = lf.value.getGraphData()
  currentWorkflow.value.updateTime = new Date().toISOString()
  
  // 更新列表中的工作流
  const index = workflows.value.findIndex(w => w.id === currentWorkflow.value.id)
  if (index > -1) {
    workflows.value[index] = { ...currentWorkflow.value }
  }
  
  saveWorkflowsToStorage()
  isSaved.value = true
  ElMessage.success('保存成功')
}

// 保存到本地存储
const saveWorkflowsToStorage = () => {
  localStorage.setItem('algorithm_workflows', JSON.stringify(workflows.value))
}

// 从本地存储加载
const loadWorkflowsFromStorage = () => {
  const saved = localStorage.getItem('algorithm_workflows')
  if (saved) {
    try {
      workflows.value = JSON.parse(saved)
    } catch (e) {
      workflows.value = []
    }
  }
}

// 工作流操作
const handleWorkflowCommand = (command, data) => {
  const workflow = data.data || workflows.value.find(w => w.id === data.id)
  if (!workflow) return
  
  switch (command) {
    case 'rename':
      ElMessageBox.prompt('请输入新名称', '重命名', {
        inputValue: workflow.name,
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }).then(({ value }) => {
        workflow.name = value
        if (currentWorkflow.value?.id === workflow.id) {
          currentWorkflow.value.name = value
        }
        saveWorkflowsToStorage()
        ElMessage.success('重命名成功')
      }).catch(() => {})
      break
      
    case 'copy':
      const copied = {
        ...JSON.parse(JSON.stringify(workflow)),
        id: 'wf-' + Date.now(),
        name: workflow.name + ' (副本)',
        createTime: new Date().toISOString(),
        updateTime: new Date().toISOString()
      }
      workflows.value.push(copied)
      saveWorkflowsToStorage()
      ElMessage.success('复制成功')
      break
      
    case 'export':
      const blob = new Blob([JSON.stringify(workflow, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${workflow.name}.json`
      a.click()
      URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
      break
      
    case 'delete':
      ElMessageBox.confirm('确定要删除该工作流吗？', '提示', {
        type: 'warning'
      }).then(() => {
        const index = workflows.value.findIndex(w => w.id === workflow.id)
        if (index > -1) {
          workflows.value.splice(index, 1)
          saveWorkflowsToStorage()
          
          if (currentWorkflow.value?.id === workflow.id) {
            currentWorkflow.value = null
            if (lf.value) {
              lf.value.render({})
            }
          }
          ElMessage.success('删除成功')
        }
      }).catch(() => {})
      break
  }
}

// 工具栏操作
const undo = () => lf.value?.undo()
const redo = () => lf.value?.redo()
const zoomIn = () => lf.value?.zoom(true)
const zoomOut = () => lf.value?.zoom(false)
const fitView = () => lf.value?.fitView()

const exportWorkflow = () => {
  if (!currentWorkflow.value) return
  handleWorkflowCommand('export', { data: currentWorkflow.value })
}

const runWorkflow = async () => {
  if (!lf.value || !currentWorkflow.value) {
    ElMessage.warning('请先选择或创建工作流')
    return
  }
  
  const graphData = lf.value.getGraphData()
  const { nodes, edges } = graphData
  
  if (nodes.length === 0) {
    ElMessage.warning('工作流中没有节点')
    return
  }
  
  // 查找数据集节点
  const datasetNodes = nodes.filter(n => n.properties?.nodeType === 'dataset-node')
  
  // 检查数据集节点是否有连线
  const connectedDatasetNodes = datasetNodes.filter(dsNode => {
    return edges.some(edge => edge.sourceNodeId === dsNode.id || edge.targetNodeId === dsNode.id)
  })
  
  // 显示日志面板
  showLogPanel.value = true
  clearLogs()
  
  addLog('🚀 开始运行工作流...', 'info')
  addLog(`📋 工作流名称: ${currentWorkflow.value.name}`, 'info')
  addLog(`📊 节点数: ${nodes.length}, 连线数: ${edges.length}`, 'info')
  
  // 如果有已连线的数据集节点，上传文件
  if (connectedDatasetNodes.length > 0) {
    addLog(`📂 发现 ${connectedDatasetNodes.length} 个已连接的数据集节点`, 'info')
    
    for (const dsNode of connectedDatasetNodes) {
      const datasetId = dsNode.properties?.datasetId
      const dataset = datasets.value.find(d => d.id === datasetId)
      
      if (dataset) {
        addLog(`📤 处理数据集: ${dataset.name}`, 'info')
        await uploadFilesToServer(dataset)
      } else {
        addLog(`⚠️ 数据集不存在: ${dsNode.properties?.label}`, 'warning')
      }
    }
  } else if (datasetNodes.length > 0) {
    addLog('⚠️ 数据集节点未连接到其他节点，跳过文件上传', 'warning')
  }
  
  // 显示运行抽屉
  showRunDrawer.value = true
  runSteps.value = [
    { name: '初始化', message: '正在准备运行环境...', status: 'success', time: '00:00' }
  ]
  
  // 模拟运行过程
  setTimeout(() => {
    runSteps.value.push({ name: '数据加载', message: '正在加载数据...', status: 'primary', progress: 0, time: '00:01' })
    
    let progress = 0
    const interval = setInterval(() => {
      progress += 20
      runSteps.value[1].progress = progress
      
      if (progress >= 100) {
        clearInterval(interval)
        runSteps.value[1].status = 'success'
        runSteps.value[1].message = '数据加载完成'
        
        setTimeout(() => {
          runSteps.value.push(
            { name: '数据处理', message: '处理完成', status: 'success', time: '00:03' },
            { name: '执行完成', message: '工作流运行成功', status: 'success', time: '00:05' }
          )
          addLog('✅ 工作流运行完成', 'success')
          ElMessage.success('工作流运行完成')
        }, 500)
      }
    }, 200)
  }, 500)
}

// 用户菜单
const handleUserCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'home':
      router.push('/template')
      break
    case 'logout':
      userStore.logout()
      router.push('/login')
      break
  }
}

const goHome = () => {
  router.push('/template')
}

// 数据集相关函数
// 触发文件上传
const triggerFileUpload = () => {
  fileInputRef.value?.click()
}

// 处理本地文件选择
const handleLocalFileSelect = (e) => {
  const files = e.target.files
  if (!files || files.length === 0) return
  
  // 创建新数据集，使用第一个文件名作为数据集名称
  const firstFileName = files[0].name
  const datasetName = files.length === 1 
    ? firstFileName.replace(/\.[^/.]+$/, '') 
    : `数据集_${new Date().toLocaleString().replace(/[/:]/g, '-')}`
  
  const newFiles = Array.from(files).map(f => ({
    name: f.name,
    size: f.size,
    uploadTime: new Date().toLocaleString(),
    file: f
  }))
  
  const newDs = {
    id: 'ds-' + Date.now(),
    name: datasetName,
    description: '',
    files: newFiles,
    createTime: new Date().toISOString(),
    updateTime: new Date().toISOString()
  }
  
  datasets.value.push(newDs)
  saveDatasetsToStorage()
  ElMessage.success(`成功添加 ${files.length} 个文件`)
  
  // 清空input值，允许重复选择同一文件
  e.target.value = ''
}

const handleDatasetCommand = (command, dataset) => {
  switch (command) {
    case 'view':
      currentViewDataset.value = dataset
      showFilesDialog.value = true
      break
      
    case 'rename':
      ElMessageBox.prompt('请输入新名称', '重命名', {
        inputValue: dataset.name,
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }).then(({ value }) => {
        dataset.name = value
        saveDatasetsToStorage()
        ElMessage.success('重命名成功')
      }).catch(() => {})
      break
      
    case 'delete':
      ElMessageBox.confirm('确定要删除该数据集吗？', '提示', {
        type: 'warning'
      }).then(() => {
        const index = datasets.value.findIndex(d => d.id === dataset.id)
        if (index > -1) {
          datasets.value.splice(index, 1)
          saveDatasetsToStorage()
          ElMessage.success('删除成功')
        }
      }).catch(() => {})
      break
  }
}

const removeFileFromDataset = (index) => {
  if (currentViewDataset.value) {
    currentViewDataset.value.files.splice(index, 1)
    saveDatasetsToStorage()
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return '未知'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const saveDatasetsToStorage = () => {
  // 存储时不保存文件对象，只保存元信息
  const dataToSave = datasets.value.map(ds => ({
    ...ds,
    files: ds.files.map(f => ({ name: f.name, size: f.size, uploadTime: f.uploadTime }))
  }))
  localStorage.setItem('algorithm_datasets', JSON.stringify(dataToSave))
}

const loadDatasetsFromStorage = () => {
  const saved = localStorage.getItem('algorithm_datasets')
  if (saved) {
    try {
      datasets.value = JSON.parse(saved)
    } catch (e) {
      datasets.value = []
    }
  }
}

// 数据集拖拽
const onDatasetDragStart = (e, dataset) => {
  e.dataTransfer.effectAllowed = 'copy'
  e.dataTransfer.setData('node-type', 'dataset-node')
  e.dataTransfer.setData('node-data', JSON.stringify({
    type: 'dataset-node',
    name: dataset.name,
    description: `数据集: ${dataset.files.length} 个文件`,
    color: '#f59e0b',
    datasetId: dataset.id,
    files: dataset.files
  }))
}

// 日志相关函数
const addLog = (message, type = 'info') => {
  const now = new Date()
  const time = now.toLocaleTimeString()
  logs.value.push({ time, message, type })
  
  // 自动滚动到底部
  nextTick(() => {
    if (logContentRef.value) {
      logContentRef.value.scrollTop = logContentRef.value.scrollHeight
    }
  })
}

const clearLogs = () => {
  logs.value = []
  uploadSuccess.value = false
}

// 上传文件到服务器
const uploadFilesToServer = async (dataset) => {
  showLogPanel.value = true
  isUploading.value = true
  uploadSuccess.value = false
  
  const files = dataset.files.filter(f => f.file) // 只上传有file对象的
  
  if (files.length === 0) {
    addLog('⚠️ 数据集中没有可上传的文件（文件可能已从本地存储恢复，需要重新添加）', 'warning')
    isUploading.value = false
    return
  }
  
  addLog(`📂 开始处理数据集: ${dataset.name}`, 'info')
  addLog(`📋 共 ${files.length} 个文件待上传`, 'info')
  
  try {
    if (files.length === 1) {
      // 单文件上传
      const file = files[0]
      addLog(`📤 正在上传单个文件: ${file.name}`, 'info')
      
      const formData = new FormData()
      formData.append('file', file.file)
      
      const response = await axios.post('http://localhost:8000/upload-single', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          addLog(`⏳ 上传进度: ${percent}%`, 'info')
        }
      })
      
      addLog(`✅ 文件上传成功: ${file.name}`, 'success')
      addLog(`📨 服务器响应: ${JSON.stringify(response.data)}`, 'success')
      
    } else {
      // 多文件上传
      addLog(`📤 正在批量上传 ${files.length} 个文件...`, 'info')
      
      const formData = new FormData()
      files.forEach((file, index) => {
        formData.append('files', file.file)
        addLog(`  📎 添加文件 ${index + 1}: ${file.name}`, 'info')
      })
      
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          addLog(`⏳ 批量上传进度: ${percent}%`, 'info')
        }
      })
      
      addLog(`✅ 批量上传成功！共 ${files.length} 个文件`, 'success')
      addLog(`📨 服务器响应: ${JSON.stringify(response.data)}`, 'success')
    }
    
    uploadSuccess.value = true
    ElMessage.success('文件上传成功')
    
  } catch (error) {
    addLog(`❌ 上传失败: ${error.message}`, 'error')
    if (error.response) {
      addLog(`❌ 服务器错误: ${JSON.stringify(error.response.data)}`, 'error')
    }
    ElMessage.error('文件上传失败')
  } finally {
    isUploading.value = false
    addLog('🏁 上传任务结束', 'info')
  }
}

// 生命周期
onMounted(() => {
  loadWorkflowsFromStorage()
  loadDatasetsFromStorage()
})

onUnmounted(() => {
  if (canvasRef.value) {
    canvasRef.value.removeEventListener('drop', onDrop)
  }
})
</script>

<style lang="scss" scoped>
.workspace-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0f172a;
  color: #fff;
  overflow: hidden;
}

// 顶部导航
.workspace-header {
  height: 56px;
  background: rgba(30, 41, 59, 0.98);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  flex-shrink: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .home-btn {
    background: rgba(102, 126, 234, 0.2);
    border: 1px solid rgba(102, 126, 234, 0.4);
    color: #667eea;
    border-radius: 8px;
    width: 40px;
    height: 40px;
    
    &:hover {
      background: rgba(102, 126, 234, 0.4);
      border-color: #667eea;
      color: #fff;
    }
    
    .el-icon {
      font-size: 18px;
    }
  }
  
  .el-divider--vertical {
    height: 24px;
    border-left-color: rgba(255, 255, 255, 0.2);
  }
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  
  &:hover .logo-icon {
    transform: scale(1.05);
  }
}

.logo-icon {
  width: 36px;
  height: 36px;
  color: #14b8a6;
  transition: transform 0.3s;
}

.logo-text {
  font-size: 1.1rem;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea, #14b8a6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.workflow-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-input {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  text-align: center;
  outline: none;
  min-width: 200px;
  
  &:hover, &:focus {
    border-color: rgba(102, 126, 234, 0.5);
    background: rgba(255, 255, 255, 0.05);
  }
}

.save-status {
  font-size: 0.75rem;
  color: #f59e0b;
  
  &.saved {
    color: #10b981;
  }
}

.no-workflow-hint {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.9rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .toolbar-group {
    .el-button {
      background: rgba(255, 255, 255, 0.05);
      border-color: rgba(255, 255, 255, 0.1);
      color: #fff;
      
      &:hover {
        background: rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.5);
      }
      
      &.is-disabled {
        opacity: 0.4;
      }
    }
  }
  
  .el-divider {
    border-color: rgba(255, 255, 255, 0.1);
  }
  
  .el-button {
    border-radius: 8px;
  }
}

.user-avatar {
  cursor: pointer;
  background: linear-gradient(135deg, #667eea, #764ba2);
}

// 主区域
.workspace-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

// 左侧边栏
.sidebar {
  width: 300px;
  background: rgba(30, 41, 59, 0.95);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}

.sidebar-scroll {
  flex: 1;
}

.sidebar-section {
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #fff;
  
  .title-icon {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
  }
  
  .add-btn {
    margin-left: auto;
    background: rgba(102, 126, 234, 0.2);
    border: none;
    color: #fff;
    
    &:hover {
      background: rgba(102, 126, 234, 0.4);
    }
  }
}

.component-collapse {
  border: none;
  background: transparent;
  
  :deep(.el-collapse-item__header) {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.8);
    font-size: 0.9rem;
    height: 40px;
    padding: 0 8px;
    border-radius: 6px;
    
    &:hover {
      background: rgba(255, 255, 255, 0.05);
    }
  }
  
  :deep(.el-collapse-item__wrap) {
    background: transparent;
    border: none;
  }
  
  :deep(.el-collapse-item__content) {
    padding: 8px 0;
    background: transparent;
  }
  
  :deep(.el-collapse-item__arrow) {
    color: rgba(255, 255, 255, 0.4);
  }
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.component-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.component-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  cursor: grab;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.15);
    border-color: rgba(102, 126, 234, 0.3);
    transform: translateX(4px);
  }
  
  &:active {
    cursor: grabbing;
    transform: scale(0.98);
  }
}

.item-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
  flex: 1;
}

.item-name {
  font-size: 0.85rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.item-desc {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.4);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.workflow-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.workflow-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.1);
    border-color: rgba(102, 126, 234, 0.2);
    
    .more-btn {
      opacity: 1;
    }
  }
  
  &.active {
    background: rgba(102, 126, 234, 0.2);
    border-color: rgba(102, 126, 234, 0.4);
    
    .item-name {
      color: #667eea;
      font-weight: 600;
    }
  }
  
  .item-icon {
    width: 28px;
    height: 28px;
  }
  
  .item-name {
    flex: 1;
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.8);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .more-btn {
    opacity: 0;
    padding: 4px;
    color: rgba(255, 255, 255, 0.5);
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      color: #fff;
    }
  }
}

.empty-workflows {
  text-align: center;
  padding: 24px 16px;
  color: rgba(255, 255, 255, 0.4);
  
  p {
    margin-bottom: 12px;
    font-size: 0.85rem;
  }
}

// 画布区域
.canvas-area {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #0f172a;
}

.canvas-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.lf-canvas {
  width: 100%;
  height: 100%;
}

.zoom-indicator {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(30, 41, 59, 0.9);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.minimap {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 200px;
  height: 150px;
  background: rgba(30, 41, 59, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

// 空状态
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  
  .empty-icon {
    color: rgba(102, 126, 234, 0.3);
    margin-bottom: 24px;
  }
  
  h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 12px;
  }
  
  p {
    color: rgba(255, 255, 255, 0.5);
    margin-bottom: 32px;
  }
}

// 属性面板
.property-panel {
  width: 0;
  background: rgba(30, 41, 59, 0.95);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  transition: width 0.3s ease;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  
  &.visible {
    width: 300px;
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
  
  h3 {
    font-size: 1rem;
    font-weight: 600;
    margin: 0;
  }
}

.panel-body {
  flex: 1;
  overflow: hidden;
}

.property-form {
  padding: 16px;
  width: 300px;
  
  :deep(.el-form-item__label) {
    color: rgba(255, 255, 255, 0.7);
  }
  
  :deep(.el-input__wrapper),
  :deep(.el-textarea__inner),
  :deep(.el-select__wrapper) {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
    box-shadow: none;
  }
  
  :deep(.el-input__inner),
  :deep(.el-textarea__inner) {
    color: #fff;
  }
  
  :deep(.el-input-number) {
    width: 100%;
    
    .el-input__wrapper {
      background: rgba(255, 255, 255, 0.05);
    }
  }
  
  :deep(.el-divider__text) {
    background: #1e293b;
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.8rem;
  }
  
  :deep(.el-checkbox__label) {
    color: rgba(255, 255, 255, 0.8);
  }
}

.empty-panel {
  height: 100%;
  width: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.3);
  
  p {
    margin-top: 12px;
    font-size: 0.9rem;
  }
}

// 对话框
.create-dialog {
  :deep(.el-dialog) {
    background: #1e293b;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    
    .el-dialog__header {
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .el-dialog__title {
      color: #fff;
    }
    
    .el-form-item__label {
      color: rgba(255, 255, 255, 0.7);
    }
    
    .el-input__wrapper,
    .el-textarea__inner {
      background: rgba(255, 255, 255, 0.05);
      border-color: rgba(255, 255, 255, 0.1);
      box-shadow: none;
    }
    
    .el-input__inner,
    .el-textarea__inner {
      color: #fff;
    }
  }
}

/* 自定义节点样式 - 需要使用全局样式 */
:global(.custom-node) {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #667eea;
  border-radius: 8px;
  padding: 10px 16px;
  min-width: 120px;
  height: 100%;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
  cursor: move;
  transition: all 0.2s ease;
  position: relative;
  z-index: 1;
}

:global(.custom-node:hover) {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  transform: scale(1.02);
  z-index: 2;
}

:global(.custom-node .node-label) {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

// 数据集列表
.dataset-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.dataset-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  cursor: grab;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(245, 158, 11, 0.1);
    border-color: rgba(245, 158, 11, 0.3);
    transform: translateX(4px);
    
    .more-btn {
      opacity: 1;
    }
  }
  
  &:active {
    cursor: grabbing;
    transform: scale(0.98);
  }
  
  .item-icon {
    width: 28px;
    height: 28px;
  }
  
  .item-info {
    flex: 1;
    min-width: 0;
  }
  
  .more-btn {
    opacity: 0;
    padding: 4px;
    color: rgba(255, 255, 255, 0.5);
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      color: #fff;
    }
  }
}

// 上传区域
.upload-container {
  .upload-area {
    width: 100%;
    
    :deep(.el-upload-dragger) {
      background: rgba(255, 255, 255, 0.05);
      border-color: rgba(255, 255, 255, 0.2);
      
      &:hover {
        border-color: #667eea;
      }
    }
    
    :deep(.el-icon--upload) {
      color: #667eea;
      font-size: 48px;
      margin-bottom: 12px;
    }
    
    :deep(.el-upload__text) {
      color: rgba(255, 255, 255, 0.7);
      
      em {
        color: #667eea;
      }
    }
    
    :deep(.el-upload__tip) {
      color: rgba(255, 255, 255, 0.4);
    }
    
    :deep(.el-upload-list__item) {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 6px;
      
      .el-upload-list__item-name {
        color: rgba(255, 255, 255, 0.8);
      }
    }
  }
}

// 底部日志面板
.log-panel {
  position: fixed;
  bottom: 0;
  left: 300px;
  right: 0;
  height: 240px;
  background: rgba(15, 23, 42, 0.98);
  border-top: 1px solid rgba(102, 126, 234, 0.3);
  display: flex;
  flex-direction: column;
  z-index: 200;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3);
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: rgba(30, 41, 59, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.log-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
  
  .el-icon {
    color: #667eea;
  }
}

.log-actions {
  display: flex;
  gap: 8px;
  
  .el-button {
    color: rgba(255, 255, 255, 0.6);
    
    &:hover {
      color: #fff;
    }
  }
}

.log-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.8rem;
  line-height: 1.6;
}

.log-item {
  display: flex;
  gap: 12px;
  padding: 4px 0;
  
  &.info {
    color: rgba(255, 255, 255, 0.7);
  }
  
  &.success {
    color: #10b981;
  }
  
  &.warning {
    color: #f59e0b;
  }
  
  &.error {
    color: #ef4444;
  }
}

.log-time {
  color: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

.log-message {
  word-break: break-all;
}

.log-empty {
  color: rgba(255, 255, 255, 0.3);
  text-align: center;
  padding: 40px;
}

// 日志面板滑入动画
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
