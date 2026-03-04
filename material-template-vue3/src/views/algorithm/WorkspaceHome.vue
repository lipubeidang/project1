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
              
              <!-- ── 数据集节点（从侧边栏拖入）── -->
              <template v-if="selectedNode.properties.nodeType === 'dataset-node'">
                <el-form-item label="关联数据集">
                  <el-select
                    v-model="selectedNode.properties.datasetId"
                    style="width:100%"
                    placeholder="请选择数据集"
                    @change="onDatasetNodeChange"
                  >
                    <el-option
                      v-for="ds in datasets"
                      :key="ds.id"
                      :label="ds.name"
                      :value="ds.id"
                    />
                  </el-select>
                </el-form-item>
                <template v-if="selectedNode.properties.columns?.length">
                  <el-form-item label="字段列表">
                    <div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:4px">
                      <el-tag
                        v-for="col in selectedNode.properties.columns"
                        :key="col.name"
                        size="small"
                        type="info"
                      >
                        {{ col.name }}<span style="opacity:0.6;margin-left:2px">({{ col.dtype }})</span>
                      </el-tag>
                    </div>
                  </el-form-item>
                  <el-form-item label="数据规模">
                    <span style="color:rgba(255,255,255,0.6)">{{ selectedNode.properties.rowCount }} 行 × {{ selectedNode.properties.columns.length }} 列</span>
                  </el-form-item>
                </template>
                <el-empty v-else description="请在左侧上传数据集后选择" :image-size="50" />
              </template>

              <!-- ── 选择列节点 ── -->
              <template v-if="selectedNode.properties.nodeType === 'column-select'">
                <el-form-item label="任务类型">
                  <el-radio-group v-model="selectedNode.properties.taskType" @change="updateNodeProperty">
                    <el-radio-button value="classification">分类</el-radio-button>
                    <el-radio-button value="regression">回归</el-radio-button>
                  </el-radio-group>
                </el-form-item>
                <el-form-item label="目标列（预测值）">
                  <el-select
                    v-model="selectedNode.properties.targetCol"
                    style="width:100%"
                    placeholder="请选择目标列"
                    @change="updateNodeProperty"
                  >
                    <el-option
                      v-for="col in upstreamColumns"
                      :key="col.value"
                      :label="col.label"
                      :value="col.value"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="特征列（输入变量）">
                  <el-select
                    v-model="selectedNode.properties.featureCols"
                    style="width:100%"
                    multiple
                    placeholder="请选择特征列（可多选）"
                    @change="updateNodeProperty"
                  >
                    <el-option
                      v-for="col in upstreamColumns"
                      :key="col.value"
                      :label="col.label"
                      :value="col.value"
                    />
                  </el-select>
                </el-form-item>
                <el-button
                  type="primary"
                  style="width:100%;margin-bottom:12px"
                  :loading="nodeState.status === 'running'"
                  @click="runFeatureSelect"
                >
                  确认选择并预览
                </el-button>
                <el-alert v-if="nodeState.error" :title="nodeState.error" type="error" :closable="false" show-icon />
                <template v-if="nodeState.result">
                  <el-divider>数据预览</el-divider>
                  <el-descriptions :column="1" size="small" border>
                    <el-descriptions-item label="有效行数">{{ nodeState.result.row_count }}</el-descriptions-item>
                    <el-descriptions-item
                      v-if="nodeState.result.target_info?.distribution"
                      label="类别分布"
                    >
                      <span
                        v-for="(cnt, cls) in nodeState.result.target_info.distribution"
                        :key="cls"
                        style="margin-right:8px"
                      >
                        {{ cls }}: {{ cnt }}
                      </span>
                    </el-descriptions-item>
                    <el-descriptions-item
                      v-if="nodeState.result.target_info?.mean !== undefined"
                      label="目标均值"
                    >
                      {{ nodeState.result.target_info.mean }}
                    </el-descriptions-item>
                  </el-descriptions>
                  <el-table
                    :data="nodeState.result.preview"
                    size="small"
                    style="margin-top:8px"
                    max-height="200"
                  >
                    <el-table-column
                      v-for="col in selectedNode.properties.featureCols?.slice(0,4)"
                      :key="col"
                      :prop="col"
                      :label="col"
                      min-width="80"
                    />
                    <el-table-column
                      :prop="selectedNode.properties.targetCol"
                      :label="selectedNode.properties.targetCol"
                      min-width="80"
                    />
                  </el-table>
                </template>
              </template>

              <!-- ── 模型训练节点 ── -->
              <template v-if="selectedNode.properties.nodeType === 'model-train'">
                <el-form-item label="模型类型" v-if="selectedNode.properties.taskType">
                  <el-select 
                    v-model="selectedNode.properties.modelType"
                    style="width:100%"
                    @change="handleModelTypeChange"
                  >
                    <template v-if="selectedNode.properties.taskType === 'classification'">
                      <el-option label="逻辑回归" value="logistic_regression" />
                      <el-option label="随机森林" value="random_forest" />
                      <el-option label="支持向量机" value="svm" />
                      <el-option label="决策树" value="decision_tree" />
                      <el-option label="梯度提升" value="gradient_boosting" />
                      <el-option label="K近邻" value="knn" />
                    </template>
                    <template v-else>
                      <el-option label="线性回归" value="linear_regression" />
                      <el-option label="岭回归" value="ridge" />
                      <el-option label="Lasso回归" value="lasso" />
                      <el-option label="随机森林" value="random_forest" />
                      <el-option label="支持向量回归" value="svr" />
                      <el-option label="梯度提升" value="gradient_boosting" />
                    </template>
                  </el-select>
                </el-form-item>
                <el-form-item label="当前模型" v-else>
                  <span style="color:rgba(255,255,255,0.8);font-size:14px">
                    请先在上游选择列节点设置任务类型
                  </span>
                </el-form-item>

                <el-form-item label="测试集比例">
                  <el-slider
                    v-model="selectedNode.properties.testSize"
                    :min="0.1" :max="0.4" :step="0.05"
                    :format-tooltip="v => (v * 100).toFixed(0) + '%'"
                    show-input
                    style="padding:0 8px"
                  />
                </el-form-item>
                
                <!-- 超参配置面板 -->
                <el-collapse v-model="activeHyperparams" style="margin: 12px 0;">
                  <el-collapse-item title="高级参数配置" name="hyperparams">
                    <div style="max-height: 200px; overflow-y: auto; padding-right: 8px; display: block; position: relative; width: 100%;">
                    <el-form label-position="top" class="hyperparam-form">
                    <!-- 核函数配置（SVM和SVR模型） -->
                    <el-form-item label="核函数 (kernel)" v-if="selectedNode.properties.modelType === 'svm' || selectedNode.properties.modelType === 'svr'">
                      <el-select 
                        v-model="selectedNode.properties.kernel"
                        style="width:100%"
                        @change="updateNodeProperty"
                      >
                        <el-option label="线性核" value="linear" />
                        <el-option label="多项式核" value="poly" />
                        <el-option label="径向基核" value="rbf" />
                        <el-option label="Sigmoid核" value="sigmoid" />
                      </el-select>
                    </el-form-item>

                    <!-- 随机森林和梯度提升树参数 -->
                    <template v-if="selectedNode.properties.modelType === 'random_forest' || selectedNode.properties.modelType === 'gradient_boosting' || selectedNode.properties.modelType === 'decision_tree'">
                      <el-form-item label="树的数量 (n_estimators)" class="hyperparam-form" style="display: block !important; margin-bottom: 18px !important;">
                        <el-input-number 
                          v-model="selectedNode.properties.nEstimators" 
                          :min="10" :max="500" :step="10"
                          style="width:100% !important; display: block !important;"
                          @change="updateNodeProperty"
                        />
                      </el-form-item>
                      <el-form-item label="最大深度 (max_depth)" class="hyperparam-form" style="display: block !important; margin-bottom: 18px !important;">
                        <el-input-number 
                          v-model="selectedNode.properties.maxDepth" 
                          :min="1" :max="50" :step="1"
                          style="width:100% !important; display: block !important;"
                          @change="updateNodeProperty"
                        />
                      </el-form-item>
                      <el-form-item label="最小叶子样本数 (min_samples_leaf)" class="hyperparam-form" style="display: block !important; margin-bottom: 18px !important;">
                        <el-input-number 
                          v-model="selectedNode.properties.minSamplesLeaf" 
                          :min="1" :max="20" :step="1"
                          style="width:100% !important; display: block !important;"
                          @change="updateNodeProperty"
                        />
                      </el-form-item>
                    </template>

                    <!-- SVM/SVR参数 -->
                    <template v-if="selectedNode.properties.modelType === 'svm' || selectedNode.properties.modelType === 'svr'">
                      <el-form-item label="正则化参数 C (C)">
                        <el-slider
                          v-model="selectedNode.properties.C"
                          :min="0.1" :max="10" :step="0.1"
                          show-input
                          style="padding:0 8px"
                        />
                      </el-form-item>
                    </template>

                    <!-- 岭回归/Lasso参数 -->
                    <template v-if="selectedNode.properties.modelType === 'ridge' || selectedNode.properties.modelType === 'lasso'">
                      <el-form-item label="正则化强度 α (alpha)">
                        <el-slider
                          v-model="selectedNode.properties.alpha"
                          :min="0.01" :max="10" :step="0.01"
                          show-input
                          style="padding:0 8px"
                        />
                      </el-form-item>
                    </template>

                    <!-- K近邻参数 -->
                    <template v-if="selectedNode.properties.modelType === 'knn'">
                      <el-form-item label="邻居数量 K (n_neighbors)">
                        <el-input-number 
                          v-model="selectedNode.properties.nNeighbors" 
                          :min="1" :max="50" :step="1"
                          style="width:100%"
                          @change="updateNodeProperty"
                        />
                      </el-form-item>
                    </template>

                    <!-- 梯度提升学习率 -->
                    <template v-if="selectedNode.properties.modelType === 'gradient_boosting'">
                      <el-form-item label="学习率 (learning_rate)">
                        <el-slider
                          v-model="selectedNode.properties.learningRate"
                          :min="0.01" :max="1" :step="0.01"
                          show-input
                          style="padding:0 8px"
                        />
                      </el-form-item>
                    </template>
                    </el-form>
                    </div>

                  </el-collapse-item>
                </el-collapse>

                <el-button
                  type="primary"
                  style="width:100%;margin-bottom:12px"
                  :loading="nodeState.status === 'running'"
                  @click="runTraining"
                >
                  {{ nodeState.status === 'running' ? '训练中...' : '开始训练' }}
                </el-button>

                <el-alert v-if="nodeState.error" :title="nodeState.error" type="error" :closable="false" show-icon />

                <template v-if="nodeState.result?.test_metrics">
                  <el-divider>训练结果</el-divider>
                  <el-descriptions :column="2" size="small" border>
                    <template v-if="nodeState.result.task_type === 'classification'">
                      <el-descriptions-item label="训练集准确率">
                        {{ (nodeState.result.train_metrics.accuracy * 100).toFixed(1) }}%
                      </el-descriptions-item>
                      <el-descriptions-item label="测试集准确率">
                        {{ (nodeState.result.test_metrics.accuracy * 100).toFixed(1) }}%
                      </el-descriptions-item>
                      <el-descriptions-item label="训练集 F1">
                        {{ nodeState.result.train_metrics.f1_weighted }}
                      </el-descriptions-item>
                      <el-descriptions-item label="测试集 F1">
                        {{ nodeState.result.test_metrics.f1_weighted }}
                      </el-descriptions-item>
                    </template>
                    <template v-else>
                      <el-descriptions-item label="测试集 R²">{{ nodeState.result.test_metrics.r2 }}</el-descriptions-item>
                      <el-descriptions-item label="测试集 RMSE">{{ nodeState.result.test_metrics.rmse }}</el-descriptions-item>
                      <el-descriptions-item label="测试集 MAE">{{ nodeState.result.test_metrics.mae }}</el-descriptions-item>
                      <el-descriptions-item label="训练集 R²">{{ nodeState.result.train_metrics.r2 }}</el-descriptions-item>
                    </template>
                    <el-descriptions-item label="训练样本">{{ nodeState.result.train_size }}</el-descriptions-item>
                    <el-descriptions-item label="测试样本">{{ nodeState.result.test_size }}</el-descriptions-item>
                    <el-descriptions-item label="训练耗时">{{ nodeState.result.training_time_ms }} ms</el-descriptions-item>
                  </el-descriptions>
                  <el-alert
                    v-for="(w, wi) in (nodeState.result.warnings || [])"
                    :key="wi"
                    :title="w"
                    type="warning"
                    :closable="false"
                    show-icon
                    style="margin-top:8px"
                  />
                </template>
              </template>

              <!-- ── 结果可视化节点 ── -->
              <template v-if="selectedNode.properties.nodeType === 'result-viz'">
                <el-form-item label="图表类型">
                  <el-select
                    v-model="selectedNode.properties.chartType"
                    style="width:100%"
                    @change="updateNodeProperty"
                  >
                    <el-option label="混淆矩阵" value="confusion_matrix" />
                    <el-option label="ROC 曲线" value="roc" />
                    <el-option label="特征重要性" value="feature_importance" />
                    <el-option label="残差图" value="residuals" />
                  </el-select>
                </el-form-item>
                <el-button
                  type="primary"
                  style="width:100%;margin-bottom:12px"
                  :loading="isChartLoading"
                  @click="loadChart"
                >
                  生成图表
                </el-button>
                <el-alert v-if="nodeState.error" :title="nodeState.error" type="error" :closable="false" show-icon />
                <div
                  ref="chartDomRef"
                  style="height:300px;border-radius:8px;overflow:hidden;background:rgba(15,23,42,0.6)"
                />
              </template>

              <!-- ── 模型预测节点 ── -->
              <template v-if="selectedNode.properties.nodeType === 'model-predict'">
                <el-form-item label="选择预测数据集">
                  <el-select
                    v-model="selectedNode.properties.predictDatasetId"
                    style="width:100%"
                    placeholder="选择已上传的数据集"
                    clearable
                    @change="updateNodeProperty"
                  >
                    <el-option
                      v-for="ds in datasets"
                      :key="ds.id"
                      :label="ds.name"
                      :value="ds.files.find(f=>f.datasetServerId)?.datasetServerId"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="或手动输入 JSON">
                  <el-input
                    v-model="selectedNode.properties.manualInput"
                    type="textarea"
                    :rows="4"
                    placeholder='[{"col1": 0.5, "col2": 100}]'
                    @change="updateNodeProperty"
                  />
                </el-form-item>
                <el-button
                  type="primary"
                  style="width:100%;margin-bottom:12px"
                  :loading="nodeState.status === 'running'"
                  @click="runPredict"
                >
                  执行预测
                </el-button>
                <el-alert v-if="nodeState.error" :title="nodeState.error" type="error" :closable="false" show-icon />
                <template v-if="nodeState.result?.predictions">
                  <el-divider>预测结果</el-divider>
                  <div style="max-height:200px;overflow-y:auto">
                    <el-tag
                      v-for="(p, i) in nodeState.result.predictions.slice(0,50)"
                      :key="i"
                      size="small"
                      type="success"
                      style="margin:2px"
                    >
                      {{ p }}
                    </el-tag>
                    <div v-if="nodeState.result.predictions.length > 50" style="color:rgba(255,255,255,0.4);font-size:0.75rem;margin-top:4px">
                      仅显示前 50 条，共 {{ nodeState.result.predictions.length }} 条
                    </div>
                  </div>
                </template>
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
  CopyDocument, Delete, Connection, HomeFilled,
  // 组件图标
  Folder, Document, SetUp,
  Cpu, TrendCharts, MagicStick, Histogram,
  Upload, Grid, FolderOpened, View
} from '@element-plus/icons-vue'
import { useMlWorkflowStore } from '@/stores/mlWorkflow'
import { mlApi, getSessionId } from '@/utils/mlApi'

const router = useRouter()
const userStore = useUserStore()
const mlStore = useMlWorkflowStore()

// ECharts state
const chartDomRef = ref(null)
let chartInstance = null
let beforeUnloadHandler = null

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
const activeComponents = ref(['comp-ml']) // 默认展开ML工作流分类
const activeHyperparams = ref([]) // 超参配置面板折叠状态





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
    id: 'comp-ml',
    label: 'ML 工作流',
    icon: markRaw(Cpu),
    isCategory: true,
    children: [
      { id: 'column-select', label: '选择列', icon: markRaw(SetUp), isComponent: true, color: '#14b8a6', description: '选择特征列和目标列' },
      { id: 'model-train', label: '模型训练', icon: markRaw(TrendCharts), isComponent: true, color: '#667eea', description: '训练机器学习模型' },
      { id: 'result-viz', label: '结果可视化', icon: markRaw(Histogram), isComponent: true, color: '#f97316', description: '可视化训练结果' },
      { id: 'model-predict', label: '模型预测', icon: markRaw(MagicStick), isComponent: true, color: '#6366f1', description: '使用模型进行预测' }
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
    
    // 自定义带颜色的节点
    class ColorNode extends HtmlNode {
      setHtml(rootEl) {
        const { properties } = this.props.model
        const color = properties.color || '#667eea'
        const label = properties.label || '节点'

        // 每次清空并重建，避免重复叠加导致重影
        rootEl.innerHTML = ''

        const container = document.createElement('div')
        container.className = 'custom-node'
        container.style.borderColor = color
        container.style.background = color

        const labelEl = document.createElement('span')
        labelEl.className = 'node-label'
        labelEl.textContent = label

        container.appendChild(labelEl)
        rootEl.appendChild(container)
      }
    }
    
    class ColorNodeModel extends HtmlNodeModel {
      setAttributes() {
        this.width = 140
        this.height = 40
        this.text.editable = false
        this.text.value = ''
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
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      background: {
        backgroundColor: '#ffffff'
      },
      keyboard: {
        enabled: true
      },
      edgeType: 'polyline',
      style: {
        rect: {
          radius: 8,
          stroke: '#667eea',
          strokeWidth: 2
        },
        bezier: {
          stroke: '#667eea',
          strokeWidth: 2
        },
        polyline: {
          stroke: '#667eea',
          strokeWidth: 2
        },
        nodeText: {
          color: '#333',
          fontSize: 14
        },
        edgeText: {
          color: '#333',
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
    
    zoomLevel.value = lf.value.getTransform().SCALE_X
    
    // 设置拖放事件监听器（延迟执行，确保画布已完全渲染）
    nextTick(() => {
      setupDropListeners()
    })
    
    // 监听数据集变化，确保事件监听器始终存在（当上传数据集后可能触发重新渲染）
    watch(() => datasets.value.length, () => {
      nextTick(() => {
        setupDropListeners()
      })
    })
    
  } catch (error) {
    console.error('LogicFlow 初始化失败:', error)
    ElMessage.error('工作流编辑器加载失败')
  }
}

// 拖放事件处理函数（定义在组件作用域外部，便于清理）
const handleDragOver = (e) => {
  e.preventDefault()
  e.dataTransfer.dropEffect = 'copy'
}

// 设置拖放事件监听器
const setupDropListeners = () => {
  if (canvasRef.value) {
    // 先移除旧的监听器（如果存在），避免重复绑定
    canvasRef.value.removeEventListener('drop', onDrop)
    canvasRef.value.removeEventListener('dragover', handleDragOver)
    // 重新绑定
    canvasRef.value.addEventListener('drop', onDrop)
    canvasRef.value.addEventListener('dragover', handleDragOver)
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

  // getPointByClient 返回画布模型坐标，addNode 需要的就是这个坐标系
  const point = lf.value.getPointByClient(e.clientX, e.clientY)
  const canvasPos = point.canvasOverlayPosition || { x: point.x, y: point.y }

  // 创建带颜色的节点
  const nodeId = 'node_' + Date.now()
  
  // 数据集节点
  if (nodeType === 'dataset-node') {
    lf.value.addNode({
      id: nodeId,
      type: 'color-node',
      x: canvasPos.x,
      y: canvasPos.y,
      properties: {
        nodeType: nodeType,
        label: nodeData.name,
        description: nodeData.description,
        color: nodeData.color,
        datasetId: nodeData.datasetId,
        datasetServerId: nodeData.datasetServerId || null,
        columns: nodeData.columns || [],
        rowCount: nodeData.rowCount || 0
      }
    })
  } else {
    const defaultProps = {
      nodeType: nodeType,
      label: nodeData.name,
      description: nodeData.description,
      color: nodeData.color,
    }
    // 按节点类型设置合理的默认属性
    switch (nodeType) {
      case 'column-select':
        Object.assign(defaultProps, { taskType: 'classification', targetCol: '', featureCols: [], selectionId: null })
        break
      case 'model-train':
        Object.assign(defaultProps, {
          testSize: 0.2,
          modelId: null, taskType: null, modelType: 'random_forest',
          // 超参数默认值
          kernel: 'rbf',
          nEstimators: 100,
          maxDepth: 10,
          minSamplesLeaf: 3,
          C: 1.0,
          alpha: 1.0,
          nNeighbors: 5,
          learningRate: 0.1,
        })
        break
      case 'result-viz':
        Object.assign(defaultProps, { chartType: 'confusion_matrix' })
        break
      case 'model-predict':
        Object.assign(defaultProps, { predictDatasetId: null, manualInput: '' })
        break
    }
    lf.value.addNode({
      id: nodeId,
      type: 'color-node',
      x: canvasPos.x,
      y: canvasPos.y,
      properties: defaultProps,
    })
  }
  
  isSaved.value = false
}

// 更新节点属性
const updateNodeProperty = () => {
  if (selectedNode.value && lf.value) {
    lf.value.setProperties(selectedNode.value.id, selectedNode.value.properties)
    // 不调用 updateText —— HtmlNode 的文本由 setHtml 渲染，
    // updateText 会额外创建原生 SVG 文字层导致重影
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

  const { nodes, edges } = lf.value.getGraphData()
  if (nodes.length === 0) {
    ElMessage.warning('工作流中没有节点')
    return
  }

  // ── Kahn 拓扑排序 ──
  const inDegree = {}
  const adj = {}
  for (const n of nodes) { inDegree[n.id] = 0; adj[n.id] = [] }
  for (const e of edges) {
    adj[e.sourceNodeId].push(e.targetNodeId)
    inDegree[e.targetNodeId] = (inDegree[e.targetNodeId] || 0) + 1
  }
  const queue = nodes.filter(n => inDegree[n.id] === 0).map(n => n.id)
  const order = []
  while (queue.length) {
    const nid = queue.shift()
    order.push(nid)
    for (const next of (adj[nid] || [])) {
      inDegree[next]--
      if (inDegree[next] === 0) queue.push(next)
    }
  }
  if (order.length !== nodes.length) {
    ElMessage.error('工作流中存在环形依赖，无法运行')
    return
  }

  // ── 按拓扑顺序依次执行 ──
  showLogPanel.value = true
  clearLogs()
  addLog(`开始运行工作流: ${currentWorkflow.value.name}（${nodes.length} 个节点）`, 'info')

  for (const nodeId of order) {
    // 每次从画布重新读取节点，确保拿到上游更新后的属性
    const freshNode = lf.value.getGraphData().nodes.find(n => n.id === nodeId)
    if (!freshNode) continue
    selectedNode.value = JSON.parse(JSON.stringify(freshNode))
    const nodeType = freshNode.properties?.nodeType
    addLog(`▶ 执行节点: ${freshNode.properties?.label || nodeId}`, 'info')

    try {
      switch (nodeType) {
        case 'dataset-node': {
          if (!freshNode.properties?.datasetServerId) {
            addLog(`  ⚠ 数据集节点未关联已上传数据，跳过`, 'warning')
          } else {
            addLog(`  ✓ 数据集已就绪`, 'success')
          }
          break
        }
        case 'column-select': await runFeatureSelect(); break
        case 'model-train':    await runTraining(); break
        case 'result-viz':     await loadChart(); break
        case 'model-predict':   await runPredict(); break
        default:
          addLog(`  ⏭ 跳过节点: ${nodeType}（无自动执行逻辑）`, 'info')
      }
    } catch (err) {
      addLog(`  ✗ 节点执行失败: ${err.message}`, 'error')
    }
  }

  addLog('工作流运行完成', 'success')
  ElMessage.success('工作流运行完成')
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

// 处理本地文件选择 - 立即上传到后端 ML 服务
const handleLocalFileSelect = async (e) => {
  const files = e.target.files
  if (!files || files.length === 0) return

  const firstFileName = files[0].name
  const datasetName = files.length === 1
    ? firstFileName.replace(/\.[^/.]+$/, '')
    : `数据集_${new Date().toLocaleString().replace(/[/:]/g, '-')}`

  showLogPanel.value = true
  isUploading.value = true
  uploadSuccess.value = false
  addLog(`📂 开始上传数据集: ${datasetName}（共 ${files.length} 个文件）`, 'info')

  const uploadedFiles = []
  let datasetColumns = []
  let datasetRowCount = 0

  for (const file of Array.from(files)) {
    try {
      addLog(`📤 正在上传: ${file.name}`, 'info')
      const res = await mlApi.uploadDataset(file)
      uploadedFiles.push({
        name: file.name,
        size: file.size,
        uploadTime: new Date().toLocaleString(),
        datasetServerId: res.data.dataset_id
      })
      if (datasetColumns.length === 0) {
        datasetColumns = res.data.columns
        datasetRowCount = res.data.row_count
      }
      addLog(`✅ ${file.name} 上传成功（${res.data.row_count} 行 × ${res.data.col_count} 列）`, 'success')
    } catch (err) {
      const msg = err.response?.data?.detail || err.message
      addLog(`❌ ${file.name} 上传失败: ${msg}`, 'error')
      uploadedFiles.push({
        name: file.name,
        size: file.size,
        uploadTime: new Date().toLocaleString(),
        error: msg
      })
    }
  }

  isUploading.value = false
  uploadSuccess.value = uploadedFiles.some(f => !f.error)

  const newDs = {
    id: 'ds-' + Date.now(),
    name: datasetName,
    description: '',
    files: uploadedFiles,
    columns: datasetColumns,
    rowCount: datasetRowCount,
    createTime: new Date().toISOString(),
    updateTime: new Date().toISOString()
  }

  datasets.value.push(newDs)
  saveDatasetsToStorage()

  const successCount = uploadedFiles.filter(f => !f.error).length
  if (successCount > 0) {
    ElMessage.success(`成功上传 ${successCount} 个文件`)
  } else {
    ElMessage.error('所有文件上传失败，请检查后端服务')
  }

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
      }).then(async () => {
        const index = datasets.value.findIndex(d => d.id === dataset.id)
        if (index > -1) {
          // Delete server-side parquet files
          for (const f of dataset.files) {
            if (f.datasetServerId) {
              mlApi.deleteDataset(f.datasetServerId).catch(() => {})
            }
          }
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
  // Store metadata only (no File objects), use sessionStorage for Tab-level isolation
  const dataToSave = datasets.value.map(ds => ({
    ...ds,
    files: ds.files.map(f => ({
      name: f.name,
      size: f.size,
      uploadTime: f.uploadTime,
      datasetServerId: f.datasetServerId || null,
      error: f.error || null
    }))
  }))
  sessionStorage.setItem('algorithm_datasets', JSON.stringify(dataToSave))
}

const loadDatasetsFromStorage = () => {
  const saved = sessionStorage.getItem('algorithm_datasets')
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
  const firstFile = dataset.files.find(f => f.datasetServerId)
  e.dataTransfer.setData('node-data', JSON.stringify({
    type: 'dataset-node',
    name: dataset.name,
    description: `数据集: ${dataset.files.length} 个文件`,
    color: '#f59e0b',
    datasetId: dataset.id,
    datasetServerId: firstFile?.datasetServerId || null,
    columns: dataset.columns || [],
    rowCount: dataset.rowCount || 0,
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

// ─── ML Pipeline Helpers ─────────────────────────────────────────────────────

// Get the single upstream node connected to current node's input port
const getUpstreamNode = (nodeId) => {
  if (!lf.value) return null
  const { nodes, edges } = lf.value.getGraphData()
  const inEdge = edges.find(e => e.targetNodeId === nodeId)
  if (!inEdge) return null
  return nodes.find(n => n.id === inEdge.sourceNodeId) || null
}

// Column list from the upstream node, used for feature/target dropdowns
const upstreamColumns = computed(() => {
  if (!selectedNode.value) return []
  const upstream = getUpstreamNode(selectedNode.value.id)
  return (upstream?.properties?.columns || []).map(c => ({
    label: `${c.name} (${c.dtype})`,
    value: c.name
  }))
})

// Current node's ML execution state (reactive proxy from store)
const nodeState = computed(() => {
  if (!selectedNode.value) return { status: 'idle', result: null, error: null }
  // 当选择模型训练节点时，自动从上游节点获取taskType
  if (selectedNode.value.properties.nodeType === 'model-train') {
    const upstream = getUpstreamNode(selectedNode.value.id)
    if (upstream?.properties?.taskType) {
      // 当任务类型改变时，重置模型类型为默认值
      if (selectedNode.value.properties.taskType !== upstream.properties.taskType) {
        selectedNode.value.properties.taskType = upstream.properties.taskType
        // 根据任务类型设置默认模型类型
        if (upstream.properties.taskType === 'classification') {
          selectedNode.value.properties.modelType = 'random_forest'
        } else {
          selectedNode.value.properties.modelType = 'linear_regression'
        }
        updateNodeProperty()
      }
    }
    
    // 确保超参数有默认值
    const props = selectedNode.value.properties
    if (!props.kernel) props.kernel = 'rbf'
    if (props.nEstimators === undefined) props.nEstimators = 100
    if (props.maxDepth === undefined) props.maxDepth = 10
    if (props.minSamplesLeaf === undefined) props.minSamplesLeaf = 3
    if (props.C === undefined) props.C = 1.0
    if (props.alpha === undefined) props.alpha = 1.0
    if (props.nNeighbors === undefined) props.nNeighbors = 5
    if (props.learningRate === undefined) props.learningRate = 0.1
  }
  return mlStore.getNodeState(selectedNode.value.id)
})

// Called when user picks a dataset for a dataset-node via the property panel dropdown
const onDatasetNodeChange = () => {
  const datasetId = selectedNode.value.properties.datasetId
  const dataset = datasets.value.find(d => d.id === datasetId)
  if (dataset) {
    const firstFile = dataset.files.find(f => f.datasetServerId)
    selectedNode.value.properties.datasetServerId = firstFile?.datasetServerId || null
    selectedNode.value.properties.columns = dataset.columns || []
    selectedNode.value.properties.rowCount = dataset.rowCount || 0
    updateNodeProperty()
  }
}

// Run feature selection for the column-select node
const runFeatureSelect = async () => {
  const nodeId = selectedNode.value.id
  const upstream = getUpstreamNode(nodeId)
  const datasetServerId = upstream?.properties?.datasetServerId
  if (!datasetServerId) {
    ElMessage.warning('上游数据集节点尚未上传到服务器，请先在侧边栏上传文件')
    return
  }
  const { taskType, targetCol, featureCols } = selectedNode.value.properties
  if (!targetCol || !featureCols?.length) {
    ElMessage.warning('请选择目标列和特征列')
    return
  }
  mlStore.setNodeState(nodeId, { status: 'running', result: null, error: null })
  try {
    const res = await mlApi.selectFeatures({
      dataset_id: datasetServerId,
      feature_cols: featureCols,
      target_col: targetCol,
      task_type: taskType || 'classification'
    })
    selectedNode.value.properties.selectionId = res.data.selection_id
    updateNodeProperty()
    mlStore.setNodeState(nodeId, { status: 'completed', result: res.data, error: null })
    addLog(`✅ 列选择完成: ${res.data.row_count} 行有效数据${res.data.warnings?.length ? '，' + res.data.warnings.join('；') : ''}`, 'success')
  } catch (err) {
    const msg = err.response?.data?.detail || err.message
    const isNotFound = err.response?.status === 404
    const hint = isNotFound ? '（服务端数据集已失效，请在侧边栏重新上传文件）' : ''
    mlStore.setNodeState(nodeId, { status: 'error', error: msg + hint, result: null })
    addLog(`❌ 列选择失败: ${msg}${hint}`, 'error')
  }
}

// Run model training for the model-train node
const runTraining = async () => {
  const nodeId = selectedNode.value.id
  const upstream = getUpstreamNode(nodeId)
  if (!upstream) {
    ElMessage.warning('请先连接上游选择列节点')
    return
  }
  const datasetId = upstream.properties?.selectionId || upstream.properties?.datasetServerId
  const taskType = upstream.properties?.taskType || selectedNode.value.properties.taskType
  const targetCol = upstream.properties?.targetCol
  const featureCols = upstream.properties?.featureCols
  if (!datasetId) {
    ElMessage.warning('上游节点尚未执行，请先运行选择列节点')
    return
  }
  if (!targetCol || !featureCols?.length) {
    ElMessage.warning('未找到特征列/目标列配置，请先运行选择列节点')
    return
  }
  // 使用用户选择的模型类型，或默认值
  const modelType = selectedNode.value.properties.modelType || (taskType === 'classification' ? 'random_forest' : 'linear_regression')
  // 模型标签映射
  const modelLabels = {
    'logistic_regression': '逻辑回归',
    'random_forest': '随机森林',
    'svm': '支持向量机',
    'decision_tree': '决策树',
    'gradient_boosting': '梯度提升',
    'knn': 'K近邻',
    'linear_regression': '线性回归',
    'ridge': '岭回归',
    'lasso': 'Lasso回归',
    'svr': '支持向量回归'
  }
  const modelLabel = modelLabels[modelType] || (taskType === 'classification' ? '随机森林' : '线性回归')
  const testSize = selectedNode.value.properties.testSize || 0.2

  // 同步 taskType 到当前节点，供面板显示
  selectedNode.value.properties.taskType = taskType
  updateNodeProperty()

  mlStore.setNodeState(nodeId, { status: 'running', result: null, error: null })
  showLogPanel.value = true
  addLog(`🤖 开始训练模型: ${modelLabel}（${taskType}）`, 'info')
  
  // 构建超参数对象
  const hyperparams = {
    test_size: testSize,
    random_state: 42,
    scale_features: true
  }
  
  // 根据模型类型添加对应的超参数
  const props = selectedNode.value.properties
  if (props.kernel) hyperparams.kernel = props.kernel
  if (props.nEstimators !== undefined) hyperparams.n_estimators = props.nEstimators
  if (props.maxDepth !== undefined) hyperparams.max_depth = props.maxDepth
  if (props.minSamplesLeaf !== undefined) hyperparams.min_samples_leaf = props.minSamplesLeaf
  if (props.C !== undefined) hyperparams.C = props.C
  if (props.alpha !== undefined) hyperparams.alpha = props.alpha
  if (props.nNeighbors !== undefined) hyperparams.n_neighbors = props.nNeighbors
  if (props.learningRate !== undefined) hyperparams.learning_rate = props.learningRate
  
  try {
    const res = await mlApi.train({
      dataset_id: datasetId,
      feature_cols: featureCols,
      target_col: targetCol,
      task_type: taskType || 'classification',
      model_type: modelType,
      hyperparams: hyperparams
    })
    selectedNode.value.properties.modelId = res.data.model_id
    selectedNode.value.properties.taskType = res.data.task_type
    updateNodeProperty()
    mlStore.setNodeState(nodeId, { status: 'completed', result: res.data, error: null })
    const m = res.data.test_metrics
    const metricStr = res.data.task_type === 'classification'
      ? `准确率 ${(m.accuracy * 100).toFixed(1)}%`
      : `R² ${m.r2}  RMSE ${m.rmse}`
    addLog(`✅ 训练完成（${res.data.training_time_ms}ms）— 测试集 ${metricStr}`, 'success')
    if (res.data.warnings?.length) {
      res.data.warnings.forEach(w => addLog(`⚠️ ${w}`, 'warning'))
    }
  } catch (err) {
    const msg = err.response?.data?.detail || err.message
    mlStore.setNodeState(nodeId, { status: 'error', error: msg, result: null })
    addLog(`❌ 训练失败: ${msg}`, 'error')
  }
}

// Load ECharts visualization for the result-viz node
const isChartLoading = ref(false)
const loadChart = async () => {
  const nodeId = selectedNode.value.id
  const upstream = getUpstreamNode(nodeId)
  const modelId = upstream?.properties?.modelId
  if (!modelId) {
    ElMessage.warning('请先连接并运行上游模型训练节点')
    return
  }
  const chartType = selectedNode.value.properties.chartType || 'confusion_matrix'
  isChartLoading.value = true
  try {
    const res = await mlApi.getVisualization(modelId, chartType)
    mlStore.setNodeState(nodeId, { status: 'completed', result: res.data, error: null })
    // Lazy-load echarts and render
    await nextTick()
    if (!chartDomRef.value) return
    const echarts = await import('echarts')
    if (chartInstance) chartInstance.dispose()
    chartInstance = echarts.init(chartDomRef.value, null, { renderer: 'canvas' })
    chartInstance.setOption(res.data.echarts_option)
  } catch (err) {
    const msg = err.response?.data?.detail || err.message
    ElMessage.error(`加载图表失败: ${msg}`)
  } finally {
    isChartLoading.value = false
  }
}

// 处理模型类型改变
const handleModelTypeChange = () => {
  // 确保超参数有默认值
  const props = selectedNode.value.properties
  if (!props.kernel) props.kernel = 'rbf'
  if (props.nEstimators === undefined) props.nEstimators = 100
  if (props.maxDepth === undefined) props.maxDepth = 10
  if (props.minSamplesLeaf === undefined) props.minSamplesLeaf = 3
  if (props.C === undefined) props.C = 1.0
  if (props.alpha === undefined) props.alpha = 1.0
  if (props.nNeighbors === undefined) props.nNeighbors = 5
  if (props.learningRate === undefined) props.learningRate = 0.1
  updateNodeProperty()
}

// Run prediction for the model-predict node
const runPredict = async () => {
  const nodeId = selectedNode.value.id
  const upstream = getUpstreamNode(nodeId)
  const modelId = upstream?.properties?.modelId
  if (!modelId) {
    ElMessage.warning('请先连接并运行上游模型训练节点')
    return
  }
  const predictDatasetId = selectedNode.value.properties.predictDatasetId
  const manualInput = selectedNode.value.properties.manualInput
  if (!predictDatasetId && !manualInput) {
    ElMessage.warning('请选择预测数据集或手动输入数据')
    return
  }
  mlStore.setNodeState(nodeId, { status: 'running', result: null, error: null })
  try {
    let payload = { model_id: modelId }
    if (predictDatasetId) {
      payload.dataset_id = predictDatasetId
    } else {
      payload.data = JSON.parse(manualInput)
    }
    const res = await mlApi.predict(payload)
    mlStore.setNodeState(nodeId, { status: 'completed', result: res.data, error: null })
    addLog(`✓ 预测完成: ${res.data.count} 条结果`, 'success')
  } catch (err) {
    const msg = err.response?.data?.detail || err.message
    mlStore.setNodeState(nodeId, { status: 'error', error: msg, result: null })
    addLog(`✗ 预测失败: ${msg}`, 'error')
  }
}

// ─── Lifecycle ───────────────────────────────────────────────────────────────

// Validate local dataset metadata against the server; remove stale entries
const validateDatasetsWithServer = async () => {
  if (datasets.value.length === 0) return
  try {
    const res = await mlApi.listDatasets()
    const serverIds = new Set((res.data || []).map(d => d.dataset_id))

    let staleCount = 0
    datasets.value = datasets.value.filter(ds => {
      const hasValid = ds.files.some(f => f.datasetServerId && serverIds.has(f.datasetServerId))
      if (!hasValid) staleCount++
      return hasValid
    })
    if (staleCount > 0) {
      saveDatasetsToStorage()
      ElMessage.warning(`${staleCount} 个数据集已失效（服务端数据不存在），请重新上传`)
    }
  } catch {
    // Server unreachable — keep local data as-is
  }
}

// 生命周期
onMounted(async () => {
  loadWorkflowsFromStorage()
  loadDatasetsFromStorage()
  await validateDatasetsWithServer()

  // Register cleanup on tab/browser close
  beforeUnloadHandler = () => {
    const sessionId = getSessionId()
    if (sessionId) mlApi.cleanSession(sessionId)
  }
  window.addEventListener('beforeunload', beforeUnloadHandler)
})

onUnmounted(() => {
  if (canvasRef.value) {
    canvasRef.value.removeEventListener('drop', onDrop)
    canvasRef.value.removeEventListener('dragover', handleDragOver)
  }
  if (beforeUnloadHandler) {
    window.removeEventListener('beforeunload', beforeUnloadHandler)
  }
  mlStore.stopAllPolling()
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
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
  background: #ffffff;
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
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  color: #555;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
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
    color: #333;
  }

  p {
    color: #999;
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
    width: 420px;
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
  width: 420px;
  
  :deep(.el-form-item__label) {
    color: rgba(255, 255, 255, 0.7);
  }
  
  /* 只修改超参配置面板中的参数名称颜色 */
  :deep(.hyperparam-form .el-form-item__label) {
    color: #000 !important;
  }
  
  /* 只修改超参配置面板中的输入控件文字颜色 */
  :deep(.hyperparam-form .el-input__inner),
  :deep(.hyperparam-form .el-textarea__inner),
  :deep(.hyperparam-form .el-select__input),
  :deep(.hyperparam-form .el-slider__input-inner),
  :deep(.hyperparam-form .el-input-number .el-input__inner) {
    color: #000 !important;
  }
  
  /* 确保超参配置面板中的输入控件正常显示 */
  :deep(.hyperparam-form .el-input-number) {
    width: 100% !important;
    display: block !important;
  }
  
  :deep(.hyperparam-form .el-input-number__decrease),
  :deep(.hyperparam-form .el-input-number__increase) {
    color: #000 !important;
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
  width: 420px;
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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* LogicFlow 右键菜单样式 */
:global(.lf-menu) {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 4px 0;
  min-width: 120px;
}

:global(.lf-menu-item) {
  padding: 8px 16px;
  color: #333;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s;
}

:global(.lf-menu-item:hover) {
  background: #f0f2ff;
  color: #667eea;
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
