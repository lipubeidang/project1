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
              <!-- 数据源：读数据表、写数据表、数据集上传（子目录含上传按钮与已上传文件列表） -->
              <el-collapse-item name="comp-datasource">
                <template #title>
                  <div class="collapse-title">
                    <el-icon><component :is="dataSourceCategory.icon" /></el-icon>
                    <span>数据源</span>
                  </div>
                </template>
                <div class="component-list">
                  <div
                    v-for="item in dataSourceComponents"
                    :key="item.id"
                    class="component-item"
                    :class="{ 'component-item-upload': item.id === 'dataset-upload' }"
                    :draggable="item.id !== 'dataset-upload'"
                    @dragstart="item.id !== 'dataset-upload' && onComponentDragStart($event, item)"
                    @dragend="onDragEnd"
                    @click="item.id === 'dataset-upload' && triggerFileUpload()"
                  >
                    <span class="item-color-dot" :style="{ background: item.color }"></span>
                    <div class="item-icon item-icon-unified" :style="{ color: item.color }">
                      <el-icon><component :is="item.icon" /></el-icon>
                    </div>
                    <div class="item-info">
                      <span class="item-name">{{ item.label }}</span>
                      <span class="item-desc">{{ item.description }}</span>
                    </div>
                  </div>
                  <!-- 数据集上传：可展开子目录，内含上传按钮与已上传文件 -->
                  <div class="component-subgroup">
                    <div class="subgroup-title-row subgroup-title-with-icon">
                      <span class="subgroup-title" @click="toggleSubgroupHidden('datasource-upload-files')">
                        <el-icon class="subgroup-chevron" :class="{ collapsed: isSubgroupHidden('datasource-upload-files') }">
                          <ArrowDown v-if="!isSubgroupHidden('datasource-upload-files')" /><ArrowRight v-else />
                        </el-icon>
                        <span class="subgroup-title-icon-wrap">
                          <el-icon :size="22"><Upload /></el-icon>
                        </span>
                        数据集上传
                      </span>
                    </div>
                    <div v-show="!isSubgroupHidden('datasource-upload-files')" class="subgroup-children dataset-in-library">
                      <input
                        ref="fileInputRef"
                        type="file"
                        multiple
                        style="display: none"
                        @change="handleLocalFileSelect"
                      />
                      <el-tooltip content="上传本地文件">
                        <el-button type="primary" size="small" class="upload-file-btn" @click="triggerFileUpload">
                          <el-icon :size="22"><Upload /></el-icon>
                          上传文件
                        </el-button>
                      </el-tooltip>
                      <div
                        v-for="dataset in datasets"
                        :key="dataset.id"
                        class="dataset-item"
                        draggable="true"
                        @dragstart="onDatasetDragStart($event, dataset)"
                        @dragend="onDragEnd"
                      >
                        <span class="item-color-dot" style="background: #8b5cf6"></span>
                        <div class="item-icon item-icon-unified" style="color: #8b5cf6">
                          <el-icon><FolderOpened /></el-icon>
                        </div>
                        <div class="item-info">
                          <span class="item-name">{{ dataset.name }}</span>
                          <span class="item-desc">{{ dataset.files.length }} 个文件</span>
                        </div>
                        <el-dropdown trigger="click" @command="(cmd) => handleDatasetCommand(cmd, dataset)" @click.stop>
                          <el-icon class="more-btn" @click.stop><MoreFilled /></el-icon>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item command="view"><el-icon><View /></el-icon>查看文件</el-dropdown-item>
                              <el-dropdown-item command="rename"><el-icon><Edit /></el-icon>重命名</el-dropdown-item>
                              <el-dropdown-item command="delete" divided><el-icon><Delete /></el-icon>删除</el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                      <div v-if="datasets.length === 0" class="empty-workflows">
                        <p>暂无数据集</p>
                      </div>
                    </div>
                  </div>
                </div>
              </el-collapse-item>
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
                <div class="component-list component-list-tiered">
                  <template v-for="sub in category.children" :key="sub.id">
                    <!-- 模型等：子项仍是分组（分类/回归），再套一层小目录 -->
                    <div v-if="sub.children?.length && sub.children[0]?.children" class="component-subgroup component-subgroup-nested tier-1">
                      <div class="subgroup-title-row">
                        <span class="subgroup-title" @click="toggleSubgroupHidden(sub.id)">
                          <el-icon class="subgroup-chevron" :class="{ collapsed: isSubgroupHidden(sub.id) }">
                            <ArrowDown v-if="!isSubgroupHidden(sub.id)" /><ArrowRight v-else />
                          </el-icon>
                          {{ sub.label }}
                        </span>
                        <el-dropdown trigger="click" @command="(cmd) => handleSubgroupCommand(cmd, sub.id)">
                          <el-button text class="subgroup-dropdown-btn" @click.stop>
                            <el-icon><MoreFilled /></el-icon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item :command="isSubgroupHidden(sub.id) ? 'show' : 'hide'">
                                {{ isSubgroupHidden(sub.id) ? '显示' : '隐藏此组' }}
                              </el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                      <div v-show="!isSubgroupHidden(sub.id)" class="subgroup-children">
                        <template v-for="subChild in sub.children" :key="subChild.id">
                          <div class="component-subgroup subgroup-inner tier-2">
                            <div class="subgroup-title-row">
                              <span class="subgroup-title" @click="toggleSubgroupHidden(subChild.id)">
                                <el-icon class="subgroup-chevron" :class="{ collapsed: isSubgroupHidden(subChild.id) }">
                                  <ArrowDown v-if="!isSubgroupHidden(subChild.id)" /><ArrowRight v-else />
                                </el-icon>
                                {{ subChild.label }}
                              </span>
                              <el-dropdown trigger="click" @command="(cmd) => handleSubgroupCommand(cmd, subChild.id)">
                                <el-button text class="subgroup-dropdown-btn" @click.stop>
                                  <el-icon><MoreFilled /></el-icon>
                                </el-button>
                                <template #dropdown>
                                  <el-dropdown-menu>
                                    <el-dropdown-item :command="isSubgroupHidden(subChild.id) ? 'show' : 'hide'">
                                      {{ isSubgroupHidden(subChild.id) ? '显示' : '隐藏此组' }}
                                    </el-dropdown-item>
                                  </el-dropdown-menu>
                                </template>
                              </el-dropdown>
                            </div>
                            <div v-show="!isSubgroupHidden(subChild.id)" class="subgroup-children">
                              <div
                                v-for="item in subChild.children"
                                :key="item.id"
                                class="component-item"
                                draggable="true"
                                @dragstart="onComponentDragStart($event, item)"
                                @dragend="onDragEnd"
                              >
                                <span class="item-color-dot" :style="{ background: item.color || '#94a3b8' }"></span>
                                <div class="item-icon item-icon-unified" :style="{ color: item.color || '#94a3b8' }">
                                  <el-icon><component :is="item.icon" /></el-icon>
                                </div>
                                <div class="item-info">
                                  <span class="item-name">{{ item.label }}</span>
                                  <span class="item-desc">{{ item.description }}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </template>
                      </div>
                    </div>
                    <!-- 小目录：有 children 且子项为组件（非分组），带下拉可隐藏 -->
                    <div v-else-if="sub.children && sub.children.length" class="component-subgroup tier-1">
                      <div class="subgroup-title-row">
                        <span class="subgroup-title" @click="toggleSubgroupHidden(sub.id)">
                          <el-icon class="subgroup-chevron" :class="{ collapsed: isSubgroupHidden(sub.id) }">
                            <ArrowDown v-if="!isSubgroupHidden(sub.id)" /><ArrowRight v-else />
                          </el-icon>
                          {{ sub.label }}
                        </span>
                        <el-dropdown trigger="click" @command="(cmd) => handleSubgroupCommand(cmd, sub.id)">
                          <el-button text class="subgroup-dropdown-btn" @click.stop>
                            <el-icon><MoreFilled /></el-icon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item :command="isSubgroupHidden(sub.id) ? 'show' : 'hide'">
                                {{ isSubgroupHidden(sub.id) ? '显示' : '隐藏此组' }}
                              </el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                      <div v-show="!isSubgroupHidden(sub.id)" class="subgroup-children">
                        <div
                          v-for="item in sub.children"
                          :key="item.id"
                          class="component-item"
                          draggable="true"
                          @dragstart="onComponentDragStart($event, item)"
                          @dragend="onDragEnd"
                        >
                          <span class="item-color-dot" :style="{ background: item.color || '#94a3b8' }"></span>
                          <div class="item-icon item-icon-unified" :style="{ color: item.color || '#94a3b8' }">
                            <el-icon><component :is="item.icon" /></el-icon>
                          </div>
                          <div class="item-info">
                            <span class="item-name">{{ item.label }}</span>
                            <span class="item-desc">{{ item.description }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <!-- 无 children 则 sub 本身为可拖拽组件 -->
                    <div
                      v-else
                      class="component-item"
                      draggable="true"
                      @dragstart="onComponentDragStart($event, sub)"
                      @dragend="onDragEnd"
                    >
                      <span class="item-color-dot" :style="{ background: sub.color || '#94a3b8' }"></span>
                      <div class="item-icon item-icon-unified" :style="{ color: sub.color || '#94a3b8' }">
                        <el-icon><component :is="sub.icon" /></el-icon>
                      </div>
                      <div class="item-info">
                        <span class="item-name">{{ sub.label }}</span>
                        <span class="item-desc">{{ sub.description }}</span>
                      </div>
                    </div>
                  </template>
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

      <!-- 右侧节点属性面板已废弃：点击节点或右键「配置」将弹出配置窗口 -->
      <aside class="property-panel" v-show="false">
        <template v-if="selectedNode">
          <div class="panel-header"><h3>节点属性</h3></div>
          <el-scrollbar class="panel-body">
            <el-form label-position="top" class="property-form">
              <!-- 占位：实际配置已移至下方节点配置弹窗 -->
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

              <!-- ── 任务类型节点 ── -->
              <template v-if="selectedNode.properties.nodeType === 'task-type'">
                <el-form-item label="任务类型">
                  <el-radio-group v-model="selectedNode.properties.taskType" @change="updateNodeProperty">
                    <el-radio-button value="classification">分类</el-radio-button>
                    <el-radio-button value="regression">回归</el-radio-button>
                  </el-radio-group>
                </el-form-item>
              </template>

              <!-- ── 目标列（输出列）节点 ── -->
              <template v-if="selectedNode.properties.nodeType === 'target-column'">
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
              </template>

              <!-- ── 特征列（输入列）节点 ── -->
              <template v-if="selectedNode.properties.nodeType === 'feature-columns'">
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
              </template>

              <!-- ── 模型选择 / 具体模型节点：仅弹窗配置 ── -->
              <template v-if="selectedNode.properties.nodeType === 'model-select' || selectedNode.properties.nodeType === 'model-concrete'">
                <el-form-item label="参数配置">
                  <el-button type="primary" style="width:100%" @click="showModelConfigDialog = true">
                    在弹窗中配置
                  </el-button>
                </el-form-item>
              </template>

              <!-- ── 特征选择节点：仅弹窗配置 ── -->
              <template v-if="selectedNode.properties.nodeType === 'feature-select'">
                <el-form-item label="参数配置">
                  <el-button type="primary" style="width:100%" @click="openFeatureSelectDialog">
                    在弹窗中配置
                  </el-button>
                </el-form-item>
              </template>

              <!-- ── 数据预处理组件节点（按列分组、聚合统计等）── -->
              <template v-if="preprocessNodeTypes.includes(selectedNode.properties.nodeType)">
                <el-form-item label="参数配置">
                  <el-button type="primary" style="width:100%" @click="openPreprocessConfigForNode(selectedNode.properties.nodeType)">
                    配置参数
                  </el-button>
                </el-form-item>
                <template v-if="selectedNode.properties.config && Object.keys(selectedNode.properties.config).length">
                  <el-descriptions :column="1" size="small" border>
                    <el-descriptions-item v-for="(val, key) in selectedNode.properties.config" :key="key" :label="String(key)">
                      {{ Array.isArray(val) ? val.join(', ') : (typeof val === 'object' ? JSON.stringify(val) : String(val)) }}
                    </el-descriptions-item>
                  </el-descriptions>
                </template>
              </template>

              <!-- ── 列选择节点（兼容旧工作流，含任务类型+目标列+特征列）── -->
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

              <!-- ── 模型训练节点（模型类型从上游「模型选择」节点获取）── -->
              <template v-if="selectedNode.properties.nodeType === 'model-train'">
                <el-form-item label="当前模型">
                  <span style="color:rgba(255,255,255,0.8);font-size:14px">
                    {{ modelTrainResolvedModelLabel || '请连接上游「模型选择」节点或「列选择」节点' }}
                  </span>
                </el-form-item>

                <el-form-item label="测试集比例">
                  <el-slider
                    v-model="selectedNode.properties.testSize"
                    :min="0.1" :max="0.4" :step="0.05"
                    :format-tooltip="v => (v * 100).toFixed(0) + '%'"
                    show-input
                    style="padding:0 8px"
                    @change="updateNodeProperty"
                  />
                </el-form-item>
                <el-form-item label="划分方式">
                  <el-checkbox v-model="selectedNode.properties.randomSplit" @change="updateNodeProperty">
                    每次随机划分（不固定种子，多次训练结果会不同）
                  </el-checkbox>
                  <div v-if="!selectedNode.properties.randomSplit" class="form-tip">未勾选时使用固定种子，相同数据会得到相同准确率</div>
                </el-form-item>

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
                  <el-divider>训练结果 · 评估指标</el-divider>
                  <el-table :data="trainingMetricsTableRows" border size="small" style="width:100%;margin-bottom:12px">
                    <el-table-column prop="name" label="指标" width="120" />
                    <el-table-column prop="train" label="训练集" min-width="90" />
                    <el-table-column prop="test" label="测试集" min-width="90" />
                  </el-table>
                  <div class="metrics-extra" style="font-size:12px;color:rgba(255,255,255,0.7);margin-bottom:8px">
                    训练样本 {{ nodeState.result.train_size }} · 测试样本 {{ nodeState.result.test_size }} · 耗时 {{ nodeState.result.training_time_ms }} ms
                  </div>
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
                  <el-button text type="primary" size="small" style="margin-bottom:8px" @click="openTableBrowserForPredictResult">
                    在表格浏览器中查看
                  </el-button>
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

    <!-- 节点配置弹窗（点击节点或右键「配置」时打开，替代原右侧节点属性面板） -->
    <el-dialog
      v-model="showNodeConfigDialog"
      :title="'配置: ' + (selectedNode?.properties?.label || '节点')"
      width="540px"
      class="create-dialog node-config-dialog"
      destroy-on-close
    >
      <el-form v-if="selectedNode" label-position="top" class="property-form">
        <el-form-item label="节点名称">
          <el-input v-model="selectedNode.properties.label" @change="updateNodeProperty" />
        </el-form-item>
        <el-form-item label="节点描述">
          <el-input v-model="selectedNode.properties.description" type="textarea" :rows="2" @change="updateNodeProperty" />
        </el-form-item>
        <el-divider>参数配置</el-divider>
        <template v-if="selectedNode.properties.nodeType === 'dataset-node'">
          <el-form-item label="关联数据集">
            <el-select v-model="selectedNode.properties.datasetId" style="width:100%" placeholder="请选择数据集" @change="onDatasetNodeChange">
              <el-option v-for="ds in datasets" :key="ds.id" :label="ds.name" :value="ds.id" />
            </el-select>
          </el-form-item>
          <template v-if="selectedNode.properties.columns?.length">
            <el-form-item label="字段列表">
              <div style="display:flex;flex-wrap:wrap;gap:4px"><el-tag v-for="col in selectedNode.properties.columns" :key="col.name" size="small" type="info">{{ col.name }} ({{ col.dtype }})</el-tag></div>
            </el-form-item>
            <el-form-item label="数据规模"><span style="color:rgba(255,255,255,0.6)">{{ selectedNode.properties.rowCount }} 行 × {{ selectedNode.properties.columns.length }} 列</span></el-form-item>
          </template>
          <el-empty v-else description="请先上传数据集后选择" :image-size="40" />
        </template>
        <template v-if="selectedNode.properties.nodeType === 'write-data-table'">
          <el-form-item label="输出表名">
            <el-input v-model="selectedNode.properties.outputTable" placeholder="可选，后端扩展后生效" @change="updateNodeProperty" />
          </el-form-item>
          <p class="form-tip">将上游数据写出到表，具体实现由后端扩展。</p>
        </template>
        <template v-if="selectedNode.properties.nodeType === 'task-type'">
          <el-form-item label="任务类型">
            <el-radio-group v-model="selectedNode.properties.taskType" @change="updateNodeProperty">
              <el-radio-button value="classification">分类</el-radio-button>
              <el-radio-button value="regression">回归</el-radio-button>
            </el-radio-group>
          </el-form-item>
        </template>
        <template v-if="selectedNode.properties.nodeType === 'target-column'">
          <el-form-item label="目标列">
            <el-select v-model="selectedNode.properties.targetCol" style="width:100%" placeholder="请选择目标列" @change="updateNodeProperty">
              <el-option v-for="col in upstreamColumns" :key="col.value" :label="col.label" :value="col.value" />
            </el-select>
          </el-form-item>
        </template>
        <template v-if="selectedNode.properties.nodeType === 'feature-columns'">
          <el-form-item label="特征列">
            <el-select v-model="selectedNode.properties.featureCols" style="width:100%" multiple placeholder="请选择特征列" @change="updateNodeProperty">
              <el-option v-for="col in upstreamColumns" :key="col.value" :label="col.label" :value="col.value" />
            </el-select>
          </el-form-item>
        </template>
        <template v-if="preprocessNodeTypes.includes(selectedNode.properties.nodeType)">
          <el-form-item label="参数配置">
            <el-button type="primary" style="width:100%" @click="openPreprocessConfigForNode(selectedNode.properties.nodeType)">配置参数</el-button>
          </el-form-item>
          <template v-if="selectedNode.properties.config && Object.keys(selectedNode.properties.config).length">
            <el-descriptions :column="1" size="small" border>
              <el-descriptions-item v-for="(val, key) in selectedNode.properties.config" :key="key" :label="String(key)">
                {{ Array.isArray(val) ? val.join(', ') : (typeof val === 'object' ? JSON.stringify(val) : String(val)) }}
              </el-descriptions-item>
            </el-descriptions>
          </template>
        </template>
        <template v-if="selectedNode.properties.nodeType === 'column-select'">
          <el-form-item label="任务类型">
            <el-radio-group v-model="selectedNode.properties.taskType" @change="updateNodeProperty">
              <el-radio-button value="classification">分类</el-radio-button>
              <el-radio-button value="regression">回归</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="目标列">
            <el-select v-model="selectedNode.properties.targetCol" style="width:100%" placeholder="请选择目标列" @change="updateNodeProperty">
              <el-option v-for="col in upstreamColumns" :key="col.value" :label="col.label" :value="col.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="特征列">
            <el-select v-model="selectedNode.properties.featureCols" style="width:100%" multiple placeholder="请选择特征列" @change="updateNodeProperty">
              <el-option v-for="col in upstreamColumns" :key="col.value" :label="col.label" :value="col.value" />
            </el-select>
          </el-form-item>
          <el-button type="primary" style="width:100%;margin-top:8px" :loading="nodeState.status === 'running'" @click="runFeatureSelect">确认选择并预览</el-button>
        </template>
        <template v-if="selectedNode.properties.nodeType === 'model-train'">
          <el-form-item label="当前模型"><span style="color:rgba(255,255,255,0.8)">{{ modelTrainResolvedModelLabel || '请连接上游模型/列选择节点' }}</span></el-form-item>
          <el-form-item label="测试集比例">
            <el-slider v-model="selectedNode.properties.testSize" :min="0.1" :max="0.4" :step="0.05" show-input style="padding:0 8px" @change="updateNodeProperty" />
          </el-form-item>
          <el-button type="primary" style="width:100%" :loading="nodeState.status === 'running'" @click="runTraining">{{ nodeState.status === 'running' ? '训练中...' : '开始训练' }}</el-button>
        </template>
        <template v-if="selectedNode.properties.nodeType === 'result-viz'">
          <el-form-item label="图表类型">
            <el-select v-model="selectedNode.properties.chartType" style="width:100%" @change="updateNodeProperty">
              <el-option label="混淆矩阵" value="confusion_matrix" />
              <el-option label="ROC 曲线" value="roc" />
              <el-option label="特征重要性" value="feature_importance" />
              <el-option label="残差图" value="residuals" />
            </el-select>
          </el-form-item>
          <el-button type="primary" style="width:100%" :loading="isChartLoading" @click="loadChart">生成图表</el-button>
        </template>
        <template v-if="selectedNode.properties.nodeType === 'model-predict'">
          <el-form-item label="预测数据集">
            <el-select v-model="selectedNode.properties.predictDatasetId" style="width:100%" placeholder="选择数据集" clearable @change="updateNodeProperty">
              <el-option v-for="ds in datasets" :key="ds.id" :label="ds.name" :value="ds.files.find(f=>f.datasetServerId)?.datasetServerId" />
            </el-select>
          </el-form-item>
          <el-form-item label="或手动输入 JSON">
            <el-input v-model="selectedNode.properties.manualInput" type="textarea" :rows="3" placeholder='[{"col1": 0.5}]' @change="updateNodeProperty" />
          </el-form-item>
          <el-button type="primary" style="width:100%" :loading="nodeState.status === 'running'" @click="runPredict">执行预测</el-button>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="showNodeConfigDialog = false">关闭</el-button>
      </template>
    </el-dialog>
    
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

    <!-- 模型配置弹窗（模型选择 / 具体模型节点） -->
    <el-dialog v-model="showModelConfigDialog" title="模型参数配置" width="520px" class="create-dialog" destroy-on-close>
      <el-form v-if="selectedNode" label-position="top">
        <el-form-item v-if="selectedNode.properties.nodeType === 'model-select'" label="模型类型">
          <el-select v-model="selectedNode.properties.modelType" style="width:100%">
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
        <el-form-item v-else label="当前模型">
          <span>{{ modelTypeLabel(selectedNode.properties.modelType) }}</span>
        </el-form-item>
        <el-collapse>
          <el-collapse-item title="高级参数配置" name="hyperparams">
            <el-form label-position="top">
              <el-form-item label="核函数 (kernel)" v-if="selectedNode.properties.modelType === 'svm' || selectedNode.properties.modelType === 'svr'">
                <el-select v-model="selectedNode.properties.kernel" style="width:100%">
                  <el-option label="线性核" value="linear" />
                  <el-option label="多项式核" value="poly" />
                  <el-option label="径向基核" value="rbf" />
                  <el-option label="Sigmoid核" value="sigmoid" />
                </el-select>
              </el-form-item>
              <template v-if="['random_forest','gradient_boosting','decision_tree'].includes(selectedNode.properties.modelType)">
                <el-form-item label="树的数量 (n_estimators)">
                  <el-input-number v-model="selectedNode.properties.nEstimators" :min="10" :max="500" :step="10" style="width:100%" />
                </el-form-item>
                <el-form-item label="最大深度 (max_depth)">
                  <el-input-number v-model="selectedNode.properties.maxDepth" :min="1" :max="50" :step="1" style="width:100%" />
                </el-form-item>
                <el-form-item label="最小叶子样本数 (min_samples_leaf)">
                  <el-input-number v-model="selectedNode.properties.minSamplesLeaf" :min="1" :max="20" :step="1" style="width:100%" />
                </el-form-item>
              </template>
              <el-form-item label="正则化参数 C" v-if="selectedNode.properties.modelType === 'svm' || selectedNode.properties.modelType === 'svr'">
                <el-slider v-model="selectedNode.properties.C" :min="0.1" :max="10" :step="0.1" show-input />
              </el-form-item>
              <el-form-item label="正则化强度 α" v-if="selectedNode.properties.modelType === 'ridge' || selectedNode.properties.modelType === 'lasso'">
                <el-slider v-model="selectedNode.properties.alpha" :min="0.01" :max="10" :step="0.01" show-input />
              </el-form-item>
              <el-form-item label="邻居数量 K" v-if="selectedNode.properties.modelType === 'knn'">
                <el-input-number v-model="selectedNode.properties.nNeighbors" :min="1" :max="50" :step="1" style="width:100%" />
              </el-form-item>
              <el-form-item label="学习率" v-if="selectedNode.properties.modelType === 'gradient_boosting'">
                <el-slider v-model="selectedNode.properties.learningRate" :min="0.01" :max="1" :step="0.01" show-input />
              </el-form-item>
              <el-form-item label="最大迭代次数 (max_iter)" v-if="['logistic_regression','svm','svr'].includes(selectedNode.properties.modelType)">
                <el-input-number v-model="selectedNode.properties.maxIter" :min="100" :max="10000" :step="100" style="width:100%" placeholder="默认 2000" />
              </el-form-item>
            </el-form>
          </el-collapse-item>
        </el-collapse>
      </el-form>
      <template #footer>
        <el-button @click="showModelConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmModelConfigDialog">确定</el-button>
      </template>
    </el-dialog>

    <!-- 特征选择弹窗：展示数据集列并选择目标列/特征列 -->
    <el-dialog v-model="showFeatureSelectDialog" title="特征选择" width="560px" class="create-dialog" destroy-on-close>
      <template v-if="selectedNode">
        <div class="feature-select-dialog">
          <el-alert v-if="!featureSelectDialogColumns.length" type="info" :closable="false" show-icon>
            请先连接上游数据集或预处理节点，以加载列列表
          </el-alert>
          <template v-else>
            <el-form label-position="top">
              <el-form-item label="目标列（输出列）">
                <el-select v-model="selectedNode.properties.targetCol" placeholder="选择预测目标列" style="width:100%">
                  <el-option v-for="col in featureSelectDialogColumns" :key="col.value" :label="col.label" :value="col.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="特征列（输入列）">
                <el-select v-model="selectedNode.properties.featureCols" multiple placeholder="选择特征列（可多选）" style="width:100%">
                  <el-option v-for="col in featureSelectDialogColumns" :key="col.value" :label="col.label" :value="col.value" />
                </el-select>
              </el-form-item>
            </el-form>
          </template>
        </div>
      </template>
      <template #footer>
        <el-button @click="showFeatureSelectDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmFeatureSelectDialog">确定</el-button>
      </template>
    </el-dialog>

    <!-- 模型预测配置弹窗：选择预测数据集等 -->
    <el-dialog v-model="showModelPredictConfigDialog" title="配置: 模型预测" width="480px" class="create-dialog" destroy-on-close>
      <el-form v-if="selectedNode?.properties?.nodeType === 'model-predict'" label-position="top">
        <el-form-item label="选择预测数据集">
          <el-select v-model="selectedNode.properties.predictDatasetId" style="width:100%" placeholder="请选择已上传的数据集" clearable @change="updateNodeProperty">
            <el-option v-for="ds in datasets.filter(d => d.files?.some(f => f.datasetServerId))" :key="ds.id" :label="ds.name" :value="ds.files.find(f=>f.datasetServerId)?.datasetServerId" />
          </el-select>
        </el-form-item>
        <el-form-item label="或手动输入 JSON（与特征列一致）">
          <el-input v-model="selectedNode.properties.manualInput" type="textarea" :rows="4" placeholder='[{"col1": 0.5, "col2": 100}]' @change="updateNodeProperty" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showModelPredictConfigDialog = false">关闭</el-button>
        <el-button type="primary" @click="confirmModelPredictConfig">确定</el-button>
      </template>
    </el-dialog>

    <!-- 表格浏览器：结果可视化时上方展示配置的图表（混淆矩阵/ROC/特征重要性/残差图），下方为数据表 -->
    <el-dialog v-model="showTableBrowserDialog" :title="'表格浏览器: ' + tableBrowserData.nodeLabel" width="85%" class="create-dialog table-browser-dialog" destroy-on-close @opened="onTableBrowserOpened" @closed="onTableBrowserClosed">
      <div v-if="tableBrowserData.showChart" ref="tableBrowserChartRef" class="table-browser-chart" style="height:360px;margin-bottom:16px;border-radius:8px;background:rgba(15,23,42,0.6)" />
      <el-table :data="tableBrowserData.rows" border stripe max-height="50vh" style="width:100%">
        <el-table-column v-for="col in tableBrowserData.columns" :key="col.key" :prop="col.key" :label="col.label || col.key" min-width="120" show-overflow-tooltip />
      </el-table>
      <template #footer>
        <el-button @click="showTableBrowserDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 交互浏览器：表格 + 简单图表展示 -->
    <el-dialog v-model="showInteractiveBrowserDialog" :title="'交互浏览器: ' + interactiveBrowserData.nodeLabel" width="90%" class="create-dialog interactive-browser-dialog" destroy-on-close>
      <div class="interactive-browser-body">
        <el-table :data="interactiveBrowserData.rows" border stripe max-height="45vh" style="width:100%">
          <el-table-column v-for="col in interactiveBrowserData.columns" :key="col.key" :prop="col.key" :label="col.label || col.key" min-width="100" show-overflow-tooltip />
        </el-table>
        <div class="interactive-chart-section">
          <div class="chart-section-title">数据分布（选择列查看）</div>
          <el-select v-model="interactiveChartColumn" placeholder="选择列" clearable style="width:200px;margin-bottom:12px" @change="buildInteractiveChartData">
            <el-option v-for="col in interactiveBrowserData.columns" :key="col.key" :label="col.label || col.key" :value="col.key" />
          </el-select>
          <div v-if="interactiveChartBars.length" class="chart-bars">
            <div v-for="(item, i) in interactiveChartBars" :key="i" class="chart-bar-row">
              <span class="chart-bar-label">{{ item.label }}</span>
              <div class="chart-bar-track"><div class="chart-bar-fill" :style="{ width: item.percent + '%' }" /></div>
              <span class="chart-bar-value">{{ item.count }}</span>
            </div>
          </div>
          <div v-else class="chart-placeholder">选择一列后可查看分布</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showInteractiveBrowserDialog = false">关闭</el-button>
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
    
    <!-- 按列分组配置对话框 -->
    <el-dialog v-model="showGroupByDialog" title="按列分组配置" width="500px" class="create-dialog">
      <el-form :model="groupByForm" label-position="top">
        <el-form-item label="选择分组列" required>
          <el-select v-model="groupByForm.columns" multiple placeholder="选择要分组的列" style="width: 100%;">
            <el-option
              v-for="col in upstreamColumns"
              :key="col.value"
              :label="col.label"
              :value="col.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="聚合函数" required>
          <el-select v-model="groupByForm.aggregateFunction" placeholder="选择聚合函数" style="width: 100%;">
            <el-option label="求和" value="sum" />
            <el-option label="平均值" value="mean" />
            <el-option label="计数" value="count" />
            <el-option label="最大值" value="max" />
            <el-option label="最小值" value="min" />
          </el-select>
        </el-form-item>
        <el-form-item label="聚合列" required>
          <el-select v-model="groupByForm.aggregateColumns" multiple placeholder="选择要聚合的列" style="width: 100%;">
            <el-option
              v-for="col in upstreamColumns"
              :key="col.value"
              :label="col.label"
              :value="col.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGroupByDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmGroupByConfig">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 聚合统计配置对话框 -->
    <el-dialog v-model="showAggregateStatsDialog" title="聚合统计配置" width="500px" class="create-dialog">
      <el-form :model="aggregateStatsForm" label-position="top">
        <el-form-item label="选择分组列" required>
          <el-select v-model="aggregateStatsForm.groupColumns" multiple placeholder="选择要分组的列（可选）" style="width: 100%;">
            <el-option
              v-for="col in upstreamColumns"
              :key="col.value"
              :label="col.label"
              :value="col.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="统计列" required>
          <el-select v-model="aggregateStatsForm.statsColumns" multiple placeholder="选择要统计的列" style="width: 100%;">
            <el-option
              v-for="col in upstreamColumns"
              :key="col.value"
              :label="col.label"
              :value="col.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="统计函数" required>
          <el-select v-model="aggregateStatsForm.statsFunctions" multiple placeholder="选择统计函数" style="width: 100%;">
            <el-option label="计数" value="count" />
            <el-option label="求和" value="sum" />
            <el-option label="平均值" value="mean" />
            <el-option label="中位数" value="median" />
            <el-option label="标准差" value="std" />
            <el-option label="最小值" value="min" />
            <el-option label="最大值" value="max" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAggregateStatsDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmAggregateStatsConfig">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 数学计算配置对话框 -->
    <el-dialog v-model="showMathCalcDialog" title="数学计算配置" width="500px" class="create-dialog">
      <el-form :model="mathCalcForm" label-position="top">
        <el-form-item label="新列名" required>
          <el-input v-model="mathCalcForm.newColumnName" placeholder="输入新列名" />
        </el-form-item>
        <el-form-item label="计算公式" required>
          <el-select v-model="mathCalcForm.calcType" placeholder="选择计算类型" style="width: 100%; margin-bottom: 10px;">
            <el-option label="两列运算" value="binary" />
            <el-option label="单列运算" value="unary" />
            <el-option label="常量运算" value="constant" />
          </el-select>
        </el-form-item>
        <template v-if="mathCalcForm.calcType === 'binary'">
          <el-form-item label="第一列" required>
            <el-select v-model="mathCalcForm.column1" placeholder="选择第一列" style="width: 100%;">
              <el-option
                v-for="col in upstreamColumns"
                :key="col.value"
                :label="col.label"
                :value="col.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="运算符" required>
            <el-select v-model="mathCalcForm.operator" placeholder="选择运算符" style="width: 100%;">
              <el-option label="加 (+)" value="+" />
              <el-option label="减 (-)" value="-" />
              <el-option label="乘 (*)" value="*" />
              <el-option label="除 (/)" value="/" />
              <el-option label="幂 (^)" value="**" />
            </el-select>
          </el-form-item>
          <el-form-item label="第二列" required>
            <el-select v-model="mathCalcForm.column2" placeholder="选择第二列" style="width: 100%;">
              <el-option
                v-for="col in upstreamColumns"
                :key="col.value"
                :label="col.label"
                :value="col.value"
              />
            </el-select>
          </el-form-item>
        </template>
        <template v-else-if="mathCalcForm.calcType === 'unary'">
          <el-form-item label="选择列" required>
            <el-select v-model="mathCalcForm.column1" placeholder="选择列" style="width: 100%;">
              <el-option
                v-for="col in upstreamColumns"
                :key="col.value"
                :label="col.label"
                :value="col.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="运算符" required>
            <el-select v-model="mathCalcForm.operator" placeholder="选择运算符" style="width: 100%;">
              <el-option label="平方" value="square" />
              <el-option label="平方根" value="sqrt" />
              <el-option label="对数 (ln)" value="log" />
              <el-option label="对数 (log10)" value="log10" />
              <el-option label="绝对值" value="abs" />
              <el-option label="取整" value="round" />
            </el-select>
          </el-form-item>
        </template>
        <template v-else-if="mathCalcForm.calcType === 'constant'">
          <el-form-item label="选择列" required>
            <el-select v-model="mathCalcForm.column1" placeholder="选择列" style="width: 100%;">
              <el-option
                v-for="col in upstreamColumns"
                :key="col.value"
                :label="col.label"
                :value="col.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="运算符" required>
            <el-select v-model="mathCalcForm.operator" placeholder="选择运算符" style="width: 100%;">
              <el-option label="加 (+)" value="+" />
              <el-option label="减 (-)" value="-" />
              <el-option label="乘 (*)" value="*" />
              <el-option label="除 (/)" value="/" />
            </el-select>
          </el-form-item>
          <el-form-item label="常量值" required>
            <el-input-number v-model="mathCalcForm.constantValue" :precision="4" style="width: 100%;" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="showMathCalcDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmMathCalcConfig">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 列组合配置对话框 -->
    <el-dialog v-model="showColumnCombineDialog" title="列组合配置" width="500px" class="create-dialog">
      <el-form :model="columnCombineForm" label-position="top">
        <el-form-item label="新列名" required>
          <el-input v-model="columnCombineForm.newColumnName" placeholder="输入新列名" />
        </el-form-item>
        <el-form-item label="选择要组合的列" required>
          <el-select v-model="columnCombineForm.columns" multiple placeholder="选择要组合的列" style="width: 100%;">
            <el-option
              v-for="col in upstreamColumns"
              :key="col.value"
              :label="col.label"
              :value="col.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="组合方式" required>
          <el-select v-model="columnCombineForm.combineMethod" placeholder="选择组合方式" style="width: 100%;">
            <el-option label="字符串拼接" value="concat" />
            <el-option label="求和" value="sum" />
            <el-option label="平均值" value="mean" />
            <el-option label="乘积" value="product" />
          </el-select>
        </el-form-item>
        <el-form-item label="分隔符" v-if="columnCombineForm.combineMethod === 'concat'">
          <el-input v-model="columnCombineForm.separator" placeholder="输入分隔符，默认为空格" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showColumnCombineDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmColumnCombineConfig">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 列类型转换配置对话框 -->
    <el-dialog v-model="showTypeConversionDialog" title="列类型转换配置" width="500px" class="create-dialog">
      <el-form :model="typeConversionForm" label-position="top">
        <el-form-item label="转换类型" required>
          <el-select v-model="typeConversionForm.conversionType" placeholder="选择转换类型" style="width: 100%;">
            <el-option label="转数值型" value="to_numeric" />
            <el-option label="转字符串" value="to_string" />
            <el-option label="转日期时间" value="to_datetime" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择列" required>
          <el-select v-model="typeConversionForm.columns" multiple placeholder="选择要转换的列" style="width: 100%;">
            <el-option
              v-for="col in upstreamColumns"
              :key="col.value"
              :label="col.label"
              :value="col.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期时间格式" v-if="typeConversionForm.conversionType === 'to_datetime'">
          <el-input v-model="typeConversionForm.dateFormat" placeholder="输入日期时间格式，如：%Y-%m-%d %H:%M:%S" />
        </el-form-item>
        <el-form-item label="错误处理" v-if="typeConversionForm.conversionType === 'to_numeric'">
          <el-select v-model="typeConversionForm.errorHandling" placeholder="选择错误处理方式" style="width: 100%;">
            <el-option label="忽略错误" value="ignore" />
            <el-option label="设为NaN" value="coerce" />
            <el-option label="设为默认值" value="default" />
          </el-select>
        </el-form-item>
        <el-form-item label="默认值" v-if="typeConversionForm.conversionType === 'to_numeric' && typeConversionForm.errorHandling === 'default'">
          <el-input-number v-model="typeConversionForm.defaultValue" :precision="4" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTypeConversionDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmTypeConversionConfig">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 列转向量配置对话框 -->
    <el-dialog v-model="showToVectorDialog" title="列转向量配置" width="500px" class="create-dialog">
      <el-form :model="toVectorForm" label-position="top">
        <el-form-item label="编码类型" required>
          <el-select v-model="toVectorForm.encodingType" placeholder="选择编码类型" style="width: 100%;">
            <el-option label="One-Hot编码" value="one_hot" />
            <el-option label="Label编码" value="label_encode" />
            <el-option label="TF-IDF" value="tfidf" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择列" required>
          <el-select v-model="toVectorForm.columns" multiple placeholder="选择要编码的列" style="width: 100%;">
            <el-option
              v-for="col in upstreamColumns"
              :key="col.value"
              :label="col.label"
              :value="col.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="前缀" v-if="toVectorForm.encodingType === 'one_hot'">
          <el-input v-model="toVectorForm.prefix" placeholder="输入列名前缀，如：col_" />
        </el-form-item>
        <el-form-item label="最大特征数" v-if="toVectorForm.encodingType === 'tfidf'">
          <el-input-number v-model="toVectorForm.maxFeatures" :min="1" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showToVectorDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmToVectorConfig">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 列重排配置对话框 -->
    <el-dialog v-model="showReorderDialog" title="列重排配置" width="500px" class="create-dialog">
      <el-form :model="reorderForm" label-position="top">
        <el-form-item label="重排类型" required>
          <el-select v-model="reorderForm.reorderType" placeholder="选择重排类型" style="width: 100%;">
            <el-option label="排序" value="sort_by_column" />
            <el-option label="移动列" value="move_column" />
          </el-select>
        </el-form-item>
        <template v-if="reorderForm.reorderType === 'sort_by_column'">
          <el-form-item label="选择排序列" required>
            <el-select v-model="reorderForm.sortColumns" multiple placeholder="选择要排序的列" style="width: 100%;">
              <el-option
                v-for="col in upstreamColumns"
                :key="col.value"
                :label="col.label"
                :value="col.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="排序方式" required>
            <el-select v-model="reorderForm.sortOrder" placeholder="选择排序方式" style="width: 100%;">
              <el-option label="升序" value="asc" />
              <el-option label="降序" value="desc" />
            </el-select>
          </el-form-item>
        </template>
        <template v-else-if="reorderForm.reorderType === 'move_column'">
          <el-form-item label="选择要移动的列" required>
            <el-select v-model="reorderForm.moveColumns" multiple placeholder="选择要移动的列" style="width: 100%;">
              <el-option
                v-for="col in upstreamColumns"
                :key="col.value"
                :label="col.label"
                :value="col.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="目标位置" required>
            <el-input-number v-model="reorderForm.targetPosition" :min="0" style="width: 100%;" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="showReorderDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmReorderConfig">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 删除配置对话框 -->
    <el-dialog v-model="showDeleteDialog" title="删除配置" width="500px" class="create-dialog">
      <el-form :model="deleteForm" label-position="top">
        <el-form-item label="删除类型" required>
          <el-select v-model="deleteForm.deleteType" placeholder="选择删除类型" style="width: 100%;">
            <el-option label="删除行" value="delete_rows" />
            <el-option label="删除列" value="delete_columns" />
            <el-option label="删除缺失值" value="drop_na" />
          </el-select>
        </el-form-item>
        <template v-if="deleteForm.deleteType === 'delete_rows'">
          <el-form-item label="删除条件" required>
            <el-select v-model="deleteForm.conditionType" placeholder="选择删除条件" style="width: 100%;">
              <el-option label="按索引范围" value="index_range" />
              <el-option label="按条件" value="condition" />
            </el-select>
          </el-form-item>
          <el-form-item label="起始索引" v-if="deleteForm.conditionType === 'index_range'">
            <el-input-number v-model="deleteForm.startIndex" :min="0" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="结束索引" v-if="deleteForm.conditionType === 'index_range'">
            <el-input-number v-model="deleteForm.endIndex" :min="0" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="选择列" v-if="deleteForm.conditionType === 'condition'" required>
            <el-select v-model="deleteForm.conditionColumn" placeholder="选择条件列" style="width: 100%;">
              <el-option
                v-for="col in upstreamColumns"
                :key="col.value"
                :label="col.label"
                :value="col.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="运算符" v-if="deleteForm.conditionType === 'condition'" required>
            <el-select v-model="deleteForm.operator" placeholder="选择运算符" style="width: 100%;">
              <el-option label="等于" value="eq" />
              <el-option label="不等于" value="ne" />
              <el-option label="大于" value="gt" />
              <el-option label="小于" value="lt" />
              <el-option label="大于等于" value="ge" />
              <el-option label="小于等于" value="le" />
            </el-select>
          </el-form-item>
          <el-form-item label="比较值" v-if="deleteForm.conditionType === 'condition'" required>
            <el-input v-model="deleteForm.compareValue" placeholder="输入比较值" style="width: 100%;" />
          </el-form-item>
        </template>
        <template v-else-if="deleteForm.deleteType === 'delete_columns'">
          <el-form-item label="选择要删除的列" required>
            <el-select v-model="deleteForm.columns" multiple placeholder="选择要删除的列" style="width: 100%;">
              <el-option
                v-for="col in upstreamColumns"
                :key="col.value"
                :label="col.label"
                :value="col.value"
              />
            </el-select>
          </el-form-item>
        </template>
        <template v-else-if="deleteForm.deleteType === 'drop_na'">
          <el-form-item label="删除方式" required>
            <el-select v-model="deleteForm.dropNaMethod" placeholder="选择删除方式" style="width: 100%;">
              <el-option label="删除所有包含缺失值的行" value="any" />
              <el-option label="删除全部为缺失值的行" value="all" />
            </el-select>
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="showDeleteDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmDeleteConfig">确定</el-button>
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
  Download, VideoPlay, Check, Close, Select, MoreFilled, Edit, ArrowDown, ArrowRight,
  CopyDocument, Delete, Connection, HomeFilled,
  // 组件图标
  Folder, Document, SetUp,
  Cpu, TrendCharts, MagicStick, Histogram,
  Upload, Grid, FolderOpened, View, Sort, Refresh, Calendar
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
const showModelConfigDialog = ref(false)
const showFeatureSelectDialog = ref(false)
const showModelPredictConfigDialog = ref(false)
// 特征选择弹窗使用的列列表：来自「上游预处理之后」的列（删除列等生效后），而非原始数据源列
const featureSelectEffectiveColumns = ref([])
const showTableBrowserDialog = ref(false)
const showInteractiveBrowserDialog = ref(false)
const showNodeConfigDialog = ref(false)
const tableBrowserData = ref({ nodeLabel: '', columns: [], rows: [] })
const interactiveBrowserData = ref({ nodeLabel: '', columns: [], rows: [] })
const interactiveChartColumn = ref('')
const interactiveChartBars = ref([])
const runSteps = ref([])
const activeComponents = ref(['comp-datasource', 'comp-data-processing', 'comp-feature', 'comp-ml']) // 默认展开数据源、数据处理和分析、特征工程、机器学习
const hiddenSubgroupIds = ref([]) // 用户选择隐藏的小目录 id 列表
const isSubgroupHidden = (id) => hiddenSubgroupIds.value.includes(id)
const toggleSubgroupHidden = (id) => {
  const idx = hiddenSubgroupIds.value.indexOf(id)
  if (idx > -1) hiddenSubgroupIds.value = hiddenSubgroupIds.value.filter(x => x !== id)
  else hiddenSubgroupIds.value = [...hiddenSubgroupIds.value, id]
}
const handleSubgroupCommand = (cmd, id) => {
  if (cmd === 'hide' && !hiddenSubgroupIds.value.includes(id)) hiddenSubgroupIds.value = [...hiddenSubgroupIds.value, id]
  if (cmd === 'show') hiddenSubgroupIds.value = hiddenSubgroupIds.value.filter(x => x !== id)
}
const activeHyperparams = ref([]) // 超参配置面板折叠状态
const activePreprocess = ref([]) // 预处理面板折叠状态

// 预处理树形数据
const preprocessTreeData = ref([
  {
    id: 'preprocess',
    label: '预处理',
    icon: markRaw(SetUp),
    children: [
      {
        id: 'grouping',
        label: '分组',
        icon: markRaw(Grid),
        children: [
          { id: 'group_by_column', label: '按列分组', icon: markRaw(Folder) },
          { id: 'aggregate_stats', label: '聚合统计', icon: markRaw(Histogram) }
        ]
      },
      {
        id: 'column_derivation',
        label: '列派生',
        icon: markRaw(Document),
        children: [
          { id: 'math_calc', label: '数学计算', icon: markRaw(TrendCharts) },
          { id: 'column_combine', label: '列组合', icon: markRaw(Connection) }
        ]
      },
      {
        id: 'type_conversion',
        label: '列类型转换',
        icon: markRaw(Refresh),
        children: [
          { id: 'to_numeric', label: '转数值型', icon: markRaw(Sort) },
          { id: 'to_string', label: '转字符串', icon: markRaw(Document) },
          { id: 'to_datetime', label: '转日期时间', icon: markRaw(Calendar) }
        ]
      },
      {
        id: 'to_vector',
        label: '列转向量',
        icon: markRaw(Cpu),
        children: [
          { id: 'one_hot', label: 'One-Hot编码', icon: markRaw(Grid) },
          { id: 'label_encode', label: 'Label编码', icon: markRaw(Document) },
          { id: 'tfidf', label: 'TF-IDF', icon: markRaw(MagicStick) }
        ]
      },
      {
        id: 'reorder',
        label: '列重排',
        icon: markRaw(Sort),
        children: [
          { id: 'sort_by_column', label: '排序', icon: markRaw(Sort) },
          { id: 'move_column', label: '移动列', icon: markRaw(FolderOpened) }
        ]
      },
      {
        id: 'delete',
        label: '删除',
        icon: markRaw(Delete),
        children: [
          { id: 'delete_rows', label: '删除行', icon: markRaw(Close) },
          { id: 'delete_columns', label: '删除列', icon: markRaw(Delete) },
          { id: 'drop_na', label: '删除缺失值', icon: markRaw(Close) }
        ]
      }
    ]
  }
])

// 已应用的预处理步骤
const appliedPreprocessSteps = ref([])

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

// 预处理组件 id 与后端 step id 一致，便于执行时组 preprocess_steps
const PREPROCESS_COLOR = '#14b8a6'
const preprocessNodeTypes = [
  'group_by_column', 'aggregate_stats', 'math_calc', 'column_combine',
  'to_numeric', 'to_string', 'to_datetime', 'one_hot', 'label_encode', 'tfidf',
  'sort_by_column', 'move_column', 'delete_rows', 'delete_columns', 'drop_na'
]
// 具体模型 id 前缀，拖到画布后 nodeType 为 model-concrete，modelType 从 id 解析
const MODEL_NODE_ID_PREFIX = 'model-'
const MODEL_COLOR = '#6366f1'
const classificationModels = [
  { id: 'model-logistic_regression', label: '逻辑回归', icon: markRaw(Cpu), color: MODEL_COLOR, description: '二分类/多分类' },
  { id: 'model-random_forest', label: '随机森林', icon: markRaw(Cpu), color: MODEL_COLOR, description: '集成树模型' },
  { id: 'model-svm', label: '支持向量机', icon: markRaw(Cpu), color: MODEL_COLOR, description: 'SVM 分类' },
  { id: 'model-decision_tree', label: '决策树', icon: markRaw(Cpu), color: MODEL_COLOR, description: '树模型' },
  { id: 'model-gradient_boosting', label: '梯度提升', icon: markRaw(Cpu), color: MODEL_COLOR, description: 'GBDT' },
  { id: 'model-knn', label: 'K近邻', icon: markRaw(Cpu), color: MODEL_COLOR, description: 'KNN 分类' }
]
const regressionModels = [
  { id: 'model-linear_regression', label: '线性回归', icon: markRaw(Cpu), color: MODEL_COLOR, description: '线性模型' },
  { id: 'model-ridge', label: '岭回归', icon: markRaw(Cpu), color: MODEL_COLOR, description: 'L2 正则' },
  { id: 'model-lasso', label: 'Lasso回归', icon: markRaw(Cpu), color: MODEL_COLOR, description: 'L1 正则' },
  { id: 'model-svr', label: '支持向量回归', icon: markRaw(Cpu), color: MODEL_COLOR, description: 'SVR' }
]
const clusteringModels = [
  { id: 'model-kmeans', label: 'kmeans聚类', icon: markRaw(Connection), color: MODEL_COLOR, description: 'K-Means 聚类' },
  { id: 'model-gaussian_mixture', label: '混合高斯', icon: markRaw(TrendCharts), color: MODEL_COLOR, description: '高斯混合模型' },
  { id: 'model-affinity_propagation', label: 'AP传播', icon: markRaw(Connection), color: MODEL_COLOR, description: 'AP 传播聚类' }
]
const timeSeriesModels = [
  { id: 'model-sarima', label: 'Sarima', icon: markRaw(TrendCharts), color: MODEL_COLOR, description: '季节性 ARIMA' }
]

// 数据源分类及组件（读数据表、写数据表、数据集上传）
const dataSourceCategory = { id: 'comp-datasource', label: '数据源', icon: markRaw(FolderOpened) }
const dataSourceComponents = [
  { id: 'dataset-node', label: '读数据表', icon: markRaw(Document), description: '选择已上传的数据集', color: '#3b82f6' },
  { id: 'write-data-table', label: '写数据表', icon: markRaw(Document), description: '写出数据到表', color: '#3b82f6' }
]

// 组件定义：按图设计六大目录，子目录逐层往右；数据预处理放入「数据处理和分析」代替「数据处理」
const preprocessChildren = [
  { id: 'preprocess-grouping', label: '分组', children: [
    { id: 'group_by_column', label: '按列分组', icon: markRaw(Folder), color: PREPROCESS_COLOR, description: '按列分组并聚合' },
    { id: 'aggregate_stats', label: '聚合统计', icon: markRaw(Histogram), color: PREPROCESS_COLOR, description: '多列聚合统计' }
  ]},
  { id: 'preprocess-derivation', label: '列派生', children: [
    { id: 'math_calc', label: '数学计算', icon: markRaw(TrendCharts), color: PREPROCESS_COLOR, description: '列间数学运算' },
    { id: 'column_combine', label: '列组合', icon: markRaw(Connection), color: PREPROCESS_COLOR, description: '多列组合为新列' }
  ]},
  { id: 'preprocess-type', label: '列类型转换', children: [
    { id: 'to_numeric', label: '转数值型', icon: markRaw(Sort), color: PREPROCESS_COLOR, description: '列转为数值类型' },
    { id: 'to_string', label: '转字符串', icon: markRaw(Document), color: PREPROCESS_COLOR, description: '列转为字符串' },
    { id: 'to_datetime', label: '转日期时间', icon: markRaw(Calendar), color: PREPROCESS_COLOR, description: '列转为日期时间' }
  ]},
  { id: 'preprocess-vector', label: '列转向量', children: [
    { id: 'one_hot', label: 'One-Hot编码', icon: markRaw(Grid), color: PREPROCESS_COLOR, description: '类别 One-Hot 编码' },
    { id: 'label_encode', label: 'Label编码', icon: markRaw(Document), color: PREPROCESS_COLOR, description: '类别标签编码' },
    { id: 'tfidf', label: 'TF-IDF', icon: markRaw(MagicStick), color: PREPROCESS_COLOR, description: '文本 TF-IDF 向量' }
  ]},
  { id: 'preprocess-reorder', label: '列重排', children: [
    { id: 'sort_by_column', label: '排序', icon: markRaw(Sort), color: PREPROCESS_COLOR, description: '按列排序' },
    { id: 'move_column', label: '移动列', icon: markRaw(FolderOpened), color: PREPROCESS_COLOR, description: '调整列顺序' }
  ]},
  { id: 'preprocess-delete', label: '删除', children: [
    { id: 'delete_rows', label: '删除行', icon: markRaw(Close), color: PREPROCESS_COLOR, description: '按条件删除行' },
    { id: 'delete_columns', label: '删除列', icon: markRaw(Delete), color: PREPROCESS_COLOR, description: '删除指定列' },
    { id: 'drop_na', label: '删除缺失值', icon: markRaw(Close), color: PREPROCESS_COLOR, description: '删除含缺失值的行' }
  ]}
]

const componentItems = [
  {
    id: 'comp-data-processing',
    label: '数据处理和分析',
    icon: markRaw(TrendCharts),
    children: [
      { id: 'comp-preprocess', label: '数据预处理', children: preprocessChildren },
      { id: 'statistics', label: '统计分析', children: [
        { id: 't_test', label: 'T检验', icon: markRaw(Document), color: '#14b8a6', description: 'T 检验' },
        { id: 'pearson', label: '皮尔森系数', icon: markRaw(Histogram), color: '#14b8a6', description: '皮尔森相关系数' },
        { id: 'table_info_stats', label: '表信息统计', icon: markRaw(Histogram), color: '#14b8a6', description: '表信息统计' }
      ]}
    ]
  },
  {
    id: 'comp-script',
    label: '自定义脚本',
    icon: markRaw(Document),
    children: [
      { id: 'sql_script', label: 'SQL脚本', icon: markRaw(Document), color: '#94a3b8', description: '执行 SQL 脚本' },
      { id: 'python_script', label: 'Python脚本', icon: markRaw(Document), color: '#94a3b8', description: '执行 Python 脚本' }
    ]
  },
  {
    id: 'comp-feature',
    label: '特征工程',
    icon: markRaw(MagicStick),
    children: [
      {
        id: 'feature-process',
        label: '特征处理',
        children: [
          { id: 'fe-type-convert', label: '类型转化', icon: markRaw(Refresh), color: '#8b5cf6', description: '列类型转化' },
          { id: 'fe-normalize', label: '归一化', icon: markRaw(TrendCharts), color: '#8b5cf6', description: '归一化' },
          { id: 'fe-missing-fill', label: '缺失值填充', icon: markRaw(SetUp), color: '#8b5cf6', description: '缺失值填充' },
          { id: 'fe-standardize', label: '标准化', icon: markRaw(Histogram), color: '#8b5cf6', description: '标准化' },
          { id: 'fe-onehot', label: 'oneHot编码', icon: markRaw(Grid), color: '#8b5cf6', description: 'One-Hot 编码' },
          { id: 'fe-pca', label: 'pca主成分分析', icon: markRaw(TrendCharts), color: '#8b5cf6', description: 'PCA 主成分分析' },
          { id: 'feature-scale', label: '特征尺度变换', icon: markRaw(SetUp), color: '#8b5cf6', description: '特征尺度变换' },
          { id: 'fe-label-encode', label: 'label编码', icon: markRaw(Document), color: '#8b5cf6', description: 'Label 编码' },
          { id: 'fe-column-split', label: '列拆分', icon: markRaw(Folder), color: '#8b5cf6', description: '列拆分' },
          { id: 'fe-random-sample', label: '随机采样', icon: markRaw(Histogram), color: '#8b5cf6', description: '随机采样' },
          { id: 'fe-smote', label: 'smote采样', icon: markRaw(MagicStick), color: '#8b5cf6', description: 'SMOTE 采样' }
        ]
      },
      {
        id: 'ml-feature',
        label: '特征选择',
        children: [
          { id: 'feature-select', label: '特征选择', icon: markRaw(Select), color: '#8b5cf6', description: '选择目标列与特征列' },
          { id: 'fe-forward-select', label: '前向特征选择', icon: markRaw(Connection), color: '#8b5cf6', description: '前向特征选择' },
          { id: 'fe-backward-select', label: '后向特征选择', icon: markRaw(Connection), color: '#8b5cf6', description: '后向特征选择' },
          { id: 'fe-label-relevance', label: '标签相关性特征筛选', icon: markRaw(Document), color: '#8b5cf6', description: '标签相关性特征筛选' },
          { id: 'fe-condition-filter', label: '特征条件筛选', icon: markRaw(SetUp), color: '#8b5cf6', description: '特征条件筛选' }
        ]
      },
      {
        id: 'feature-generation',
        label: '特征生成',
        children: [
          { id: 'fe-agg-func', label: '聚合函数', icon: markRaw(Histogram), color: '#8b5cf6', description: '聚合函数' },
          { id: 'fe-window-func', label: '窗口函数', icon: markRaw(Grid), color: '#8b5cf6', description: '窗口函数' },
          { id: 'fe-lfe-auto', label: 'LFE自动特征构建', icon: markRaw(MagicStick), color: '#8b5cf6', description: 'LFE 自动特征构建' }
        ]
      },
      {
        id: 'feature-transform',
        label: '特征变换',
        children: [
          { id: 'fe-outlier', label: '异常值处理', icon: markRaw(Close), color: '#8b5cf6', description: '异常值处理' },
          { id: 'fe-unsupervised-bin', label: '非监督分箱', icon: markRaw(Folder), color: '#8b5cf6', description: '非监督分箱' },
          { id: 'fe-chi2-bin', label: '卡方分箱', icon: markRaw(Grid), color: '#8b5cf6', description: '卡方分箱' },
          { id: 'fe-optimal-ks-bin', label: '最优KS值分箱', icon: markRaw(TrendCharts), color: '#8b5cf6', description: '最优 KS 值分箱' },
          { id: 'fe-woe', label: 'WOE值转化', icon: markRaw(Document), color: '#8b5cf6', description: 'WOE 值转化' }
        ]
      }
    ]
  },
  {
    id: 'comp-ml',
    label: '机器学习',
    icon: markRaw(Cpu),
    children: [
      { id: 'ml-models-cls', label: '分类', children: [...classificationModels] },
      { id: 'ml-models-reg', label: '回归', children: [...regressionModels] },
      { id: 'ml-models-cluster', label: '聚类', children: [...clusteringModels] },
      { id: 'ml-models-timeseries', label: '时间序列', children: [...timeSeriesModels] }
    ]
  },
  {
    id: 'comp-modeling-tools',
    label: '建模工具',
    icon: markRaw(SetUp),
    children: [
      { id: 'model-eval', label: '模型评估', children: [
        { id: 'eval-binary', label: '二分类评估', icon: markRaw(TrendCharts), color: '#94a3b8', description: '二分类评估' },
        { id: 'eval-regression', label: '回归模型评估', icon: markRaw(Refresh), color: '#94a3b8', description: '回归模型评估' },
        { id: 'eval-clustering', label: '聚类模型评估', icon: markRaw(Connection), color: '#94a3b8', description: '聚类模型评估' },
        { id: 'eval-confusion', label: '混淆矩阵', icon: markRaw(Grid), color: '#94a3b8', description: '混淆矩阵' },
        { id: 'eval-scorecard', label: '评分卡分数转化', icon: markRaw(MagicStick), color: '#94a3b8', description: '评分卡分数转化' }
      ]},
      { id: 'model-select-tools', label: '模型选择', children: [
        { id: 'split', label: '拆分', icon: markRaw(Folder), color: '#94a3b8', description: '训练/测试拆分' }
      ]},
      { id: 'ml-train', label: '训练与结果', children: [
        { id: 'model-train', label: '模型训练', icon: markRaw(TrendCharts), color: '#667eea', description: '训练机器学习模型' },
        { id: 'result-viz', label: '结果可视化', icon: markRaw(Histogram), color: '#f97316', description: '可视化训练结果' },
        { id: 'model-predict', label: '模型预测', icon: markRaw(MagicStick), color: '#6366f1', description: '使用模型进行预测' }
      ]}
    ]
  },
  {
    id: 'comp-nlp',
    label: '自然语言处理',
    icon: markRaw(Document),
    children: [
      { id: 'word_segment', label: '分词', icon: markRaw(Document), color: '#94a3b8', description: '中文分词' },
      { id: 'word_freq', label: '词频统计', icon: markRaw(Histogram), color: '#94a3b8', description: '词频统计' },
      { id: 'tfidf_nlp', label: 'TF-IDF', icon: markRaw(MagicStick), color: '#94a3b8', description: 'TF-IDF' },
      { id: 'ngram', label: 'N-GRAM', icon: markRaw(Document), color: '#94a3b8', description: 'N-GRAM' },
      { id: 'lda', label: 'LDA', icon: markRaw(Document), color: '#94a3b8', description: 'LDA 主题' }
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
    
    // 自定义节点：白底、浅蓝边框、左侧图标、中间名称、右侧状态（与参考图一致）
    const getNodeIconSvg = (nodeType) => {
      const icons = {
        'dataset-node': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/></svg>',
        'write-data-table': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>',
        'feature-select': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
        'model-train': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/></svg>',
        'result-viz': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
        'model-predict': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>'
      }
      if (icons[nodeType]) return icons[nodeType]
      if (nodeType && (nodeType.startsWith('model-') || nodeType === 'model-concrete')) return icons['model-train']
      const preprocess = ['group_by_column', 'aggregate_stats', 'math_calc', 'column_combine', 'to_numeric', 'to_string', 'to_datetime', 'one_hot', 'label_encode', 'tfidf', 'sort_by_column', 'move_column', 'delete_rows', 'delete_columns', 'drop_na']
      if (preprocess.some(p => nodeType === p)) return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>'
      return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>'
    }
    class ColorNode extends HtmlNode {
      setHtml(rootEl) {
        const { properties } = this.props.model
        const label = properties.label || '节点'
        const nodeType = properties.nodeType || ''
        const status = properties.executionStatus || '' // success | error | running

        rootEl.innerHTML = ''
        const container = document.createElement('div')
        container.className = 'custom-node custom-node-card'
        container.setAttribute('data-node-type', nodeType)

        const iconWrap = document.createElement('span')
        iconWrap.className = 'node-icon-wrap'
        iconWrap.innerHTML = getNodeIconSvg(nodeType)
        container.appendChild(iconWrap)

        const labelEl = document.createElement('span')
        labelEl.className = 'node-label'
        labelEl.textContent = label
        container.appendChild(labelEl)

        const statusWrap = document.createElement('span')
        statusWrap.className = 'node-status-wrap'
        if (status === 'success') statusWrap.innerHTML = '<span class="node-status node-status-success" title="执行成功">✓</span>'
        else if (status === 'error') statusWrap.innerHTML = '<span class="node-status node-status-error" title="执行失败">✕</span>'
        else if (status === 'running') statusWrap.innerHTML = '<span class="node-status node-status-running" title="执行中">⋯</span>'
        else statusWrap.innerHTML = '<span class="node-status node-status-none"></span>'
        container.appendChild(statusWrap)

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
        visible: false,
        type: 'dot',
        config: {
          color: 'rgba(0, 0, 0, 0.06)'
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
          stroke: '#bae6fd',
          strokeWidth: 1
        },
        bezier: {
          stroke: '#64748b',
          strokeWidth: 1.5
        },
        polyline: {
          stroke: '#64748b',
          strokeWidth: 1.5
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
    
    // 配置节点右键菜单。LogicFlow 的 menu 扩展要求 nodeMenu 为数组，不能为函数，否则会报 list.forEach is not a function
    const nodeMenuItems = [
      {
        text: '执行',
        callback: (node) => {
          runNode(node.id)
        }
      },
      {
        text: '表格浏览器',
        callback: async (node) => {
          const loading = ElMessage({ message: '加载数据中…', type: 'info', duration: 0 })
          const data = await getNodePreviewDataOrFetch(node)
          loading.close()
          if (!data) {
            if (node.properties?.nodeType === 'dataset-node') {
              ElMessage.warning('请先在属性面板关联已上传的数据集；若已关联仍报错，请重新上传数据并再次关联')
            } else {
              ElMessage.info('请先执行该节点或构建缓存')
            }
            return
          }
          const label = node.properties?.label || node.id
          const isResultViz = node.properties?.nodeType === 'result-viz' || (node.properties?.nodeType === 'model-concrete' && node.properties?.label === '结果可视化')
          const chartModelId = isResultViz ? getAllUpstreamNodes(node.id).find(n => n.properties?.modelId)?.properties?.modelId : null
          tableBrowserData.value = {
            nodeLabel: label,
            columns: data.columns,
            rows: data.rows,
            showChart: !!chartModelId,
            chartModelId: chartModelId || '',
            chartType: node.properties?.chartType || 'confusion_matrix'
          }
          showTableBrowserDialog.value = true
        }
      },
      {
        text: '构建缓存',
        callback: (node) => {
          runNode(node.id)
          ElMessage.success('执行完成后结果将可用于表格浏览器与导出')
        }
      },
      {
        text: '表格数据导出',
        callback: async (node) => {
          const loading = ElMessage({ message: '加载数据中…', type: 'info', duration: 0 })
          const data = await getNodePreviewDataOrFetch(node)
          loading.close()
          if (!data || !data.rows.length) {
            if (node.properties?.nodeType === 'dataset-node') {
              ElMessage.warning('请先在属性面板关联已上传的数据集')
            } else {
              ElMessage.info('请先执行该节点或构建缓存')
            }
            return
          }
          const label = (node.properties?.label || node.id).replace(/[/\\?*:[\]]/g, '_')
          const headers = data.columns.map(c => c.label || c.key)
          const csv = [headers.join(',')].concat(
            data.rows.map(row => headers.map(h => {
              const v = row[h]
              const s = v == null ? '' : String(v)
              return s.includes(',') || s.includes('"') ? `"${s.replace(/"/g, '""')}"` : s
            }).join(','))
          ).join('\n')
          const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `${label}_导出.csv`
          a.click()
          URL.revokeObjectURL(url)
          ElMessage.success('已导出为 CSV')
        }
      },
      {
        text: '交互浏览器',
        callback: async (node) => {
          const loading = ElMessage({ message: '加载数据中…', type: 'info', duration: 0 })
          const data = await getNodePreviewDataOrFetch(node)
          loading.close()
          if (!data) {
            if (node.properties?.nodeType === 'dataset-node') {
              ElMessage.warning('请先在属性面板关联已上传的数据集')
            } else {
              ElMessage.info('请先执行该节点或构建缓存')
            }
            return
          }
          const label = node.properties?.label || node.id
          interactiveBrowserData.value = { nodeLabel: label, columns: data.columns, rows: data.rows }
          interactiveChartColumn.value = ''
          interactiveChartBars.value = []
          showInteractiveBrowserDialog.value = true
        }
      },
      {
        text: '配置',
        callback: async (n) => {
          if (n.properties?.nodeType === 'dataset-node') {
            ElMessage.info('数据集节点无需配置')
            return
          }
          selectedNode.value = JSON.parse(JSON.stringify(n))
          const nt = n.properties?.nodeType
          if (nt === 'model-select' || nt === 'model-concrete') {
            showModelConfigDialog.value = true
          } else if (nt === 'feature-select') {
            await openFeatureSelectDialog()
          } else if (nt === 'model-predict') {
            showModelPredictConfigDialog.value = true
          } else if (preprocessNodeTypes.includes(nt)) {
            openPreprocessConfigForNode(nt)
          } else {
            showNodeConfigDialog.value = true
          }
        }
      },
      {
        text: '重命名',
        callback: (node) => {
          ElMessageBox.prompt('请输入节点名称', '重命名', {
            inputValue: node.properties?.label || node.id,
            confirmButtonText: '确定',
            cancelButtonText: '取消'
          }).then(({ value }) => {
            lf.value.setProperties(node.id, { ...node.properties, label: value })
            ElMessage.success('已重命名')
            isSaved.value = false
          }).catch(() => {})
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
      },
      {
        text: '删除节点',
        callback: (node) => {
          lf.value.deleteNode(node.id)
          if (selectedNode.value?.id === node.id) {
            selectedNode.value = null
          }
          ElMessage.success('节点已删除')
        }
      }
    ]
    lf.value.extension.menu.setMenuConfig({
      nodeMenu: nodeMenuItems,
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
      // 左键仅选中节点，不自动弹窗；配置请右键选择「配置」
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
    if (preprocessNodeTypes.includes(nodeType)) {
      Object.assign(defaultProps, { preprocessId: nodeType, config: {} })
    } else if (nodeType && nodeType.startsWith(MODEL_NODE_ID_PREFIX)) {
      const modelType = nodeType.slice(MODEL_NODE_ID_PREFIX.length)
      Object.assign(defaultProps, {
        nodeType: 'model-concrete',
        modelType,
        taskType: ['logistic_regression','random_forest','svm','decision_tree','gradient_boosting','knn'].includes(modelType) ? 'classification' : 'regression',
        kernel: 'rbf',
        nEstimators: 100,
        maxDepth: 10,
        minSamplesLeaf: 3,
        C: 1.0,
        alpha: 1.0,
        nNeighbors: 5,
        learningRate: 0.1,
        maxIter: 2000,
      })
    } else {
      switch (nodeType) {
        case 'task-type':
          Object.assign(defaultProps, { taskType: 'classification' })
          break
        case 'feature-select':
          Object.assign(defaultProps, { taskType: 'classification', targetCol: '', featureCols: [], selectionId: null })
          break
        case 'target-column':
          Object.assign(defaultProps, { targetCol: '' })
          break
        case 'feature-columns':
          Object.assign(defaultProps, { featureCols: [] })
          break
        case 'model-select':
          Object.assign(defaultProps, {
            taskType: 'classification',
            modelType: 'random_forest',
            kernel: 'rbf',
            nEstimators: 100,
            maxDepth: 10,
            minSamplesLeaf: 3,
            C: 1.0,
            alpha: 1.0,
            nNeighbors: 5,
            learningRate: 0.1,
            maxIter: 2000,
          })
          break
        case 'column-select':
          Object.assign(defaultProps, { taskType: 'classification', targetCol: '', featureCols: [], selectionId: null })
          break
        case 'model-train':
          Object.assign(defaultProps, {
            testSize: 0.2,
            randomSplit: true,
            modelId: null,
            taskType: null,
            modelType: null,
          })
          break
        case 'result-viz':
          Object.assign(defaultProps, { chartType: 'confusion_matrix' })
          break
        case 'model-predict':
          Object.assign(defaultProps, { predictDatasetId: null, manualInput: '' })
          break
        case 'write-data-table':
          Object.assign(defaultProps, { outputTable: '' })
          break
      }
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

// 是否为数据/表格输出型节点（可查看表格、导出、交互浏览器）
const isDataModificationNode = (properties) => {
  if (!properties?.nodeType) return false
  const nt = properties.nodeType
  return nt === 'dataset-node' || nt === 'column-select' || nt === 'feature-select' ||
    preprocessNodeTypes.includes(nt)
}

// 获取节点表格预览数据（来自执行结果），无则返回 null
const getNodePreviewData = (nodeId) => {
  const state = mlStore.getNodeState(nodeId)
  const result = state?.result
  if (!result) return null
  if (result.preview && Array.isArray(result.preview)) {
    const rows = result.preview
    const columns = rows.length && typeof rows[0] === 'object'
      ? Object.keys(rows[0]).map(k => ({ key: k, label: k }))
      : []
    return { columns, rows }
  }
  return null
}

// 获取节点预览：数据集节点请求原始预览；预处理节点请求 /ml/preprocess 得到处理后的预览；其他节点用执行结果缓存
const getNodePreviewDataOrFetch = async (node) => {
  const nodeType = node.properties?.nodeType

  // 1) 数据集节点：直接拉取原始数据预览
  if (nodeType === 'dataset-node' && node.properties?.datasetServerId) {
    try {
      const res = await mlApi.getDatasetPreview(node.properties.datasetServerId)
      const columns = (res.data.columns || []).map(c => ({ key: c.name, label: c.name }))
      return { columns, rows: res.data.preview || [] }
    } catch (e) {
      const status = e.response?.status
      const msg = e.response?.data?.detail || e.message || '获取数据集预览失败'
      if (status === 404) {
        ElMessage.error('数据集不存在或会话已过期，请重新上传数据并在属性面板重新关联该数据集')
      } else {
        ElMessage.error(msg)
      }
      return null
    }
  }

  // 2) 预处理节点（如删除列、分组、聚合等）：按「数据源 + 到该节点为止的预处理链」调用 /ml/preprocess，得到处理后的预览
  if (preprocessNodeTypes.includes(nodeType)) {
    const { dataSourceNode, preprocessSteps, targetCol } = getPreprocessChainAndDataSource(node.id)
    const datasetServerId = dataSourceNode?.properties?.datasetServerId
    if (!datasetServerId) {
      ElMessage.warning('请先连接上游数据集节点并确保数据集已上传')
      return null
    }
    try {
      const payload = {
        dataset_id: datasetServerId,
        preprocess_steps: preprocessSteps,
      }
      if (targetCol) payload.target_col = targetCol
      const res = await mlApi.preprocess(payload)
      const columns = (res.data.columns || []).map(c => ({ key: c.name, label: c.name }))
      return { columns, rows: res.data.preview || [] }
    } catch (e) {
      const msg = e.response?.data?.detail || e.message || '预处理预览失败'
      ElMessage.error(msg)
      return null
    }
  }

  // 3) 结果可视化：请求可视化接口，将混淆矩阵等转为表格供表格浏览器展示
  const isResultViz = nodeType === 'result-viz' || (nodeType === 'model-concrete' && node.properties?.label === '结果可视化')
  if (isResultViz) {
    const upstreams = getAllUpstreamNodes(node.id)
    const trainNode = upstreams.find(n => n.properties?.modelId)
    const modelId = trainNode?.properties?.modelId
    if (!modelId) return null
    try {
      const chartType = node.properties?.chartType || 'confusion_matrix'
      const res = await mlApi.getVisualization(modelId, chartType)
      const opt = res.data?.echarts_option
      if (!opt) return null
      const columns = [{ key: 'true_label', label: '真实值' }, { key: 'pred_label', label: '预测值' }, { key: 'count', label: '数量' }]
      let rows = []
      if (chartType === 'confusion_matrix' && opt.series?.[0]?.data && opt.xAxis?.data && opt.yAxis?.data) {
        const xLabels = opt.xAxis.data
        const yLabels = opt.yAxis.data
        for (const [j, i, count] of opt.series[0].data) {
          rows.push({ true_label: yLabels[i], pred_label: xLabels[j], count })
        }
      } else if (chartType === 'feature_importance' && opt.series?.[0]?.data && opt.yAxis?.data) {
        const cols = [{ key: 'feature', label: '特征' }, { key: 'importance', label: '重要性' }]
        const names = opt.yAxis.data
        const values = opt.series[0].data
        const r = names.map((name, idx) => ({ feature: name, importance: values[idx] ?? '—' }))
        return { columns: cols, rows: r }
      } else {
        rows = [{ true_label: '—', pred_label: '该图表类型暂不支持表格展示', count: '—' }]
      }
      return { columns, rows }
    } catch (e) {
      return null
    }
  }

  // 4) 模型预测：用执行结果中的 predictions 转为表格
  const isModelPredict = nodeType === 'model-predict' || (nodeType === 'model-concrete' && node.properties?.label === '模型预测')
  if (isModelPredict) {
    const state = mlStore.getNodeState(node.id)
    const predictions = state?.result?.predictions
    if (!predictions || !Array.isArray(predictions) || predictions.length === 0) return null
    const columns = [{ key: 'index', label: '序号' }, { key: 'prediction', label: '预测值' }]
    const rows = predictions.map((p, i) => ({ index: i + 1, prediction: p }))
    return { columns, rows }
  }

  // 5) 其他节点（特征选择、模型训练等）：用执行结果中的缓存
  return getNodePreviewData(node.id)
}

// 交互浏览器：根据选中列统计分布并生成柱状数据
const buildInteractiveChartData = () => {
  const col = interactiveChartColumn.value
  const { rows } = interactiveBrowserData.value
  if (!col || !rows?.length) {
    interactiveChartBars.value = []
    return
  }
  const count = {}
  for (const row of rows) {
    const v = row[col]
    const key = v == null ? '(空)' : String(v)
    count[key] = (count[key] || 0) + 1
  }
  const total = rows.length
  const arr = Object.entries(count)
    .map(([label, cnt]) => ({ label, count: cnt, percent: total ? (cnt / total * 100) : 0 }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 30)
  interactiveChartBars.value = arr
}

// 获取工作流拓扑序（Kahn），若指定 nodeId 则返回到该节点（含）为止的节点 id 列表
const getTopologicalOrder = (upToNodeId = null) => {
  if (!lf.value) return []
  const { nodes, edges } = lf.value.getGraphData()
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
    if (upToNodeId && nid === upToNodeId) return order
    for (const next of (adj[nid] || [])) {
      inDegree[next]--
      if (inDegree[next] === 0) queue.push(next)
    }
  }
  return order
}

// 右键「单独执行」：执行当前节点及其前序节点
const runNode = async (nodeId) => {
  if (!lf.value || !currentWorkflow.value) {
    ElMessage.warning('请先选择或创建工作流')
    return
  }
  const { nodes } = lf.value.getGraphData()
  const order = getTopologicalOrder(nodeId)
  if (order.length === 0) {
    ElMessage.warning('工作流为空或存在环')
    return
  }
  if (!order.includes(nodeId)) {
    ElMessage.warning('该节点不在当前工作流拓扑中')
    return
  }
  showLogPanel.value = true
  addLog('——— 新一轮运行 ———', 'separator')
  addLog(`执行节点及前序: ${order.length} 个节点`, 'info')
  for (const nid of order) {
    const freshNode = lf.value.getGraphData().nodes.find(n => n.id === nid)
    if (!freshNode) continue
    selectedNode.value = JSON.parse(JSON.stringify(freshNode))
    const nodeType = freshNode.properties?.nodeType
    addLog(`▶ 执行节点: ${freshNode.properties?.label || nid}`, 'info')
    try {
      switch (nodeType) {
        case 'dataset-node':
          if (!freshNode.properties?.datasetServerId) {
            addLog(`  ⚠ 数据集节点未关联已上传数据，跳过`, 'warning')
          } else {
            addLog(`  ✓ 数据集已就绪`, 'success')
          }
          break
        case 'column-select':
        case 'feature-select': await runFeatureSelect(); break
        case 'model-train': await runTraining(); break
        case 'result-viz': await loadChart(); break
        case 'model-predict': await runPredict(); break
        case 'task-type':
        case 'target-column':
        case 'feature-columns':
        case 'model-select':
          addLog(`  ✓ 配置节点已就绪`, 'success')
          break
        case 'model-concrete':
          if (freshNode.properties?.label === '模型训练') {
            await runTraining()
          } else if (freshNode.properties?.label === '结果可视化') {
            await loadChart()
          } else if (freshNode.properties?.label === '模型预测') {
            await runPredict()
          } else {
            addLog(`  ✓ 配置节点已就绪`, 'success')
          }
          break
        default:
          if (preprocessNodeTypes.includes(nodeType)) {
            addLog(`  ✓ 预处理节点已就绪`, 'success')
          } else {
            addLog(`  ⏭ 跳过节点: ${nodeType}`, 'info')
          }
      }
    } catch (err) {
      addLog(`  ✗ 节点执行失败: ${err.message}`, 'error')
    }
  }
  addLog('执行完成', 'success')
  ElMessage.success('节点执行完成')
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

  const order = getTopologicalOrder()
  if (order.length !== nodes.length) {
    ElMessage.error('工作流中存在环形依赖，无法运行')
    return
  }

  // ── 按拓扑顺序依次执行 ──
  showLogPanel.value = true
  addLog('——— 新一轮运行 ———', 'separator')
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
        case 'column-select':
        case 'feature-select': await runFeatureSelect(); break
        case 'model-train':    await runTraining(); break
        case 'result-viz':     await loadChart(); break
        case 'model-predict':  await runPredict(); break
        case 'task-type':
        case 'target-column':
        case 'feature-columns':
        case 'model-select':
          addLog(`  ✓ 配置节点已就绪`, 'success')
          break
        case 'model-concrete':
          if (freshNode.properties?.label === '模型训练') {
            await runTraining()
          } else if (freshNode.properties?.label === '结果可视化') {
            await loadChart()
          } else if (freshNode.properties?.label === '模型预测') {
            await runPredict()
          } else {
            addLog(`  ✓ 配置节点已就绪`, 'success')
          }
          break
        default:
          if (preprocessNodeTypes.includes(nodeType)) {
            addLog(`  ✓ 预处理节点已就绪`, 'success')
          } else {
            addLog(`  ⏭ 跳过节点: ${nodeType}（无自动执行逻辑）`, 'info')
          }
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

// Get all direct upstream nodes (for nodes that may have multiple inputs, e.g. model-train)
const getUpstreamNodes = (nodeId) => {
  if (!lf.value) return []
  const { nodes, edges } = lf.value.getGraphData()
  const inEdges = edges.filter(e => e.targetNodeId === nodeId)
  return inEdges.map(e => nodes.find(n => n.id === e.sourceNodeId)).filter(Boolean)
}

// 获取所有上游节点（沿边反向递归），用于从「模型训练」沿 随机森林→特征选择 找到特征选择
const getAllUpstreamNodes = (nodeId) => {
  if (!lf.value) return []
  const { nodes, edges } = lf.value.getGraphData()
  const nodeMap = new Map(nodes.map(n => [n.id, n]))
  const inEdgeMap = new Map()
  edges.forEach(e => {
    if (!inEdgeMap.has(e.targetNodeId)) inEdgeMap.set(e.targetNodeId, [])
    inEdgeMap.get(e.targetNodeId).push(e.sourceNodeId)
  })
  const result = []
  const seen = new Set()
  const queue = [nodeId]
  while (queue.length) {
    const curId = queue.shift()
    const inIds = inEdgeMap.get(curId) || []
    for (const id of inIds) {
      if (seen.has(id)) continue
      seen.add(id)
      const n = nodeMap.get(id)
      if (n) {
        result.push(n)
        queue.push(id)
      }
    }
  }
  return result
}

// Walk back to find the data source node (has columns or datasetServerId) for column list
const getDataSourceNode = (nodeId) => {
  let cur = getUpstreamNode(nodeId)
  while (cur) {
    const cols = cur.properties?.columns
    if (cols && Array.isArray(cols) && cols.length > 0) return cur
    if (cur.properties?.datasetServerId) return cur
    cur = getUpstreamNode(cur.id)
  }
  return null
}

// 从某节点往回走到数据源，收集路径上的预处理节点（用于执行时组 preprocess_steps）
// 多上游时优先沿“数据”上游走（有 selectionId/columns/datasetServerId 的一侧）
const getPreprocessChainAndDataSource = (nodeId) => {
  if (!lf.value) return { dataSourceNode: null, preprocessSteps: [] }
  const { nodes, edges } = lf.value.getGraphData()
  const nodeMap = new Map(nodes.map(n => [n.id, n]))
  const inEdgeMap = new Map()
  edges.forEach(e => {
    if (!inEdgeMap.has(e.targetNodeId)) inEdgeMap.set(e.targetNodeId, [])
    inEdgeMap.get(e.targetNodeId).push(e.sourceNodeId)
  })
  const path = []
  let curId = nodeId
  while (curId) {
    const node = nodeMap.get(curId)
    if (!node) break
    path.unshift(node)
    const inIds = inEdgeMap.get(curId) || []
    if (inIds.length === 0) break
    if (inIds.length === 1) {
      curId = inIds[0]
    } else {
      const dataUp = inIds.find(id => {
        const n = nodeMap.get(id)
        return n?.properties?.datasetServerId || n?.properties?.selectionId || (n?.properties?.columns?.length > 0)
      })
      curId = dataUp != null ? dataUp : inIds[0]
    }
  }
  const dataSourceIndex = path.findIndex(n => n.properties?.datasetServerId)
  if (dataSourceIndex < 0) return { dataSourceNode: null, preprocessSteps: [] }
  const dataSourceNode = path[dataSourceIndex]
  const configNodeTypes = ['task-type', 'target-column', 'feature-columns', 'feature-select', 'column-select', 'model-select', 'model-concrete', 'model-train', 'result-viz', 'model-predict']
  const preprocessSteps = []
  let targetCol = null
  for (let i = dataSourceIndex + 1; i < path.length; i++) {
    const n = path[i]
    const nt = n.properties?.nodeType
    if (configNodeTypes.includes(nt)) {
      if (!targetCol && (nt === 'target-column' || nt === 'feature-select' || nt === 'column-select') && n.properties?.targetCol) {
        targetCol = n.properties.targetCol
      }
      continue
    }
    if (preprocessNodeTypes.includes(nt) && n.properties?.config && Object.keys(n.properties.config).length > 0) {
      preprocessSteps.push({ id: nt, config: n.properties.config })
    }
  }
  return { dataSourceNode, preprocessSteps, targetCol }
}

// Column list from the data source in the upstream chain
const upstreamColumns = computed(() => {
  if (!selectedNode.value) return []
  const source = getDataSourceNode(selectedNode.value.id)
  return (source?.properties?.columns || []).map(c => ({
    label: `${c.name} (${c.dtype})`,
    value: c.name
  }))
})

// 训练结果指标表格行（分类：准确率、F1、精确率、召回率；回归：R²、RMSE、MAE）
const trainingMetricsTableRows = computed(() => {
  const res = nodeState.value?.result
  if (!res?.test_metrics) return []
  const isClass = res.task_type === 'classification'
  const labels = isClass
    ? { accuracy: '准确率', f1_weighted: 'F1 (weighted)', precision_weighted: '精确率', recall_weighted: '召回率' }
    : { r2: 'R²', rmse: 'RMSE', mae: 'MAE' }
  const rows = []
  for (const [key, label] of Object.entries(labels)) {
    const trainVal = res.train_metrics?.[key]
    const testVal = res.test_metrics?.[key]
    if (trainVal === undefined && testVal === undefined) continue
    const format = (v) => key === 'accuracy' && v != null ? (v * 100).toFixed(1) + '%' : (v != null ? String(v) : '—')
    rows.push({ name: label, train: format(trainVal), test: format(testVal) })
  }
  return rows
})

// 模型训练节点显示用的模型标签（从上游模型选择或列选择节点解析）
const modelTrainResolvedModelLabel = computed(() => {
  if (!selectedNode.value || selectedNode.value.properties?.nodeType !== 'model-train') return ''
  const upstreams = getUpstreamNodes(selectedNode.value.id)
  const modelSelectNode = upstreams.find(n => n.properties?.nodeType === 'model-select')
  const modelConcreteNode = upstreams.find(n => n.properties?.nodeType === 'model-concrete')
  const columnSelectNode = upstreams.find(n => n.properties?.nodeType === 'column-select')
  const taskType = modelSelectNode?.properties?.taskType || modelConcreteNode?.properties?.taskType || columnSelectNode?.properties?.taskType || 'classification'
  const modelType = modelConcreteNode?.properties?.modelType || modelSelectNode?.properties?.modelType || columnSelectNode?.properties?.modelType || (taskType === 'classification' ? 'random_forest' : 'linear_regression')
  const labels = {
    logistic_regression: '逻辑回归', random_forest: '随机森林', svm: '支持向量机',
    decision_tree: '决策树', gradient_boosting: '梯度提升', knn: 'K近邻',
    linear_regression: '线性回归', ridge: '岭回归', lasso: 'Lasso回归', svr: '支持向量回归'
  }
  return labels[modelType] || modelType
})

// Current node's ML execution state (reactive proxy from store)
const nodeState = computed(() => {
  if (!selectedNode.value) return { status: 'idle', result: null, error: null }
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

// Run feature selection for the column-select node（预处理步骤从画布上的预处理节点链收集）
const runFeatureSelect = async () => {
  const nodeId = selectedNode.value.id
  const { dataSourceNode, preprocessSteps } = getPreprocessChainAndDataSource(nodeId)
  const datasetServerId = dataSourceNode?.properties?.datasetServerId
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
    const params = {
      dataset_id: datasetServerId,
      feature_cols: featureCols,
      target_col: targetCol,
      task_type: taskType || 'classification',
      preprocess_steps: preprocessSteps
    }
    
    const res = await mlApi.selectFeatures(params)
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

// Run model training for the model-train node（从多上游收集：数据源/selectionId、任务类型、目标列、特征列、模型选择）
const runTraining = async () => {
  const nodeId = selectedNode.value.id
  const directUpstreams = getUpstreamNodes(nodeId)
  if (directUpstreams.length === 0) {
    ElMessage.warning('请先连接上游节点（列选择或 任务类型+目标列+特征列+模型选择）')
    return
  }
  // 沿链路收集所有上游（特征选择→随机森林→模型训练 时，模型训练仅直连随机森林，需从整条链找特征选择）
  const upstreams = getAllUpstreamNodes(nodeId)
  const columnSelectNode = upstreams.find(n => n.properties?.nodeType === 'column-select')
  const featureSelectNode = upstreams.find(n => n.properties?.nodeType === 'feature-select')
  const taskTypeNode = upstreams.find(n => n.properties?.nodeType === 'task-type')
  const targetColNode = upstreams.find(n => n.properties?.nodeType === 'target-column')
  const featureColsNode = upstreams.find(n => n.properties?.nodeType === 'feature-columns')
  const modelSelectNode = upstreams.find(n => n.properties?.nodeType === 'model-select')
  const modelConcreteNode = upstreams.find(n => n.properties?.nodeType === 'model-concrete')

  let taskType = featureSelectNode?.properties?.taskType || columnSelectNode?.properties?.taskType || taskTypeNode?.properties?.taskType || 'classification'
  let targetCol = featureSelectNode?.properties?.targetCol || columnSelectNode?.properties?.targetCol || targetColNode?.properties?.targetCol
  let featureCols = featureSelectNode?.properties?.featureCols || columnSelectNode?.properties?.featureCols || featureColsNode?.properties?.featureCols
  if (!targetCol || !featureCols?.length) {
    ElMessage.warning('未找到特征列/目标列配置，请连接「目标列」「特征列」节点或「列选择」节点')
    return
  }

  const modelType = modelConcreteNode?.properties?.modelType || modelSelectNode?.properties?.modelType || columnSelectNode?.properties?.modelType || (taskType === 'classification' ? 'random_forest' : 'linear_regression')
  const modelLabels = {
    'logistic_regression': '逻辑回归', 'random_forest': '随机森林', 'svm': '支持向量机',
    'decision_tree': '决策树', 'gradient_boosting': '梯度提升', 'knn': 'K近邻',
    'linear_regression': '线性回归', 'ridge': '岭回归', 'lasso': 'Lasso回归', 'svr': '支持向量回归'
  }
  const modelLabel = modelLabels[modelType] || (taskType === 'classification' ? '随机森林' : '线性回归')
  const testSize = selectedNode.value.properties.testSize || 0.2

  let datasetId = featureSelectNode?.properties?.selectionId || columnSelectNode?.properties?.selectionId
  if (!datasetId) {
    const { dataSourceNode, preprocessSteps } = getPreprocessChainAndDataSource(nodeId)
    if (!dataSourceNode?.properties?.datasetServerId) {
      ElMessage.warning('未找到上游数据源，请连接数据集或预处理链')
      return
    }
    mlStore.setNodeState(nodeId, { status: 'running', result: null, error: null })
    showLogPanel.value = true
    addLog('📋 正在执行数据准备（预处理+列选择）…', 'info')
    try {
      const prepRes = await mlApi.selectFeatures({
        dataset_id: dataSourceNode.properties.datasetServerId,
        feature_cols: featureCols,
        target_col: targetCol,
        task_type: taskType,
        preprocess_steps: preprocessSteps
      })
      datasetId = prepRes.data.selection_id
      const nodeToStore = featureSelectNode || columnSelectNode
      if (nodeToStore) {
        const graph = lf.value.getGraphData()
        const idx = graph.nodes.findIndex(n => n.id === nodeToStore.id)
        if (idx > -1) {
          graph.nodes[idx].properties.selectionId = datasetId
          lf.value.render(graph)
        }
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message
      mlStore.setNodeState(nodeId, { status: 'error', error: msg, result: null })
      addLog(`❌ 数据准备失败: ${msg}`, 'error')
      return
    }
  }

  selectedNode.value.properties.taskType = taskType
  updateNodeProperty()

  mlStore.setNodeState(nodeId, { status: 'running', result: null, error: null })
  showLogPanel.value = true
  addLog(`🤖 开始训练模型: ${modelLabel}（${taskType}）`, 'info')

  const hyperparams = { test_size: testSize, scale_features: true }
  // 勾选「每次随机划分」时传 null，两次运行结果会不同；不勾选时固定种子 42，结果可复现
  hyperparams.random_state = selectedNode.value.properties.randomSplit !== false ? null : 42
  // 从上游「随机森林/模型选择」节点读取最新配置（与画布一致），改参数后无需重新拖节点
  const props = modelConcreteNode?.properties || modelSelectNode?.properties || selectedNode.value.properties
  if (props.kernel != null) hyperparams.kernel = props.kernel
  if (props.nEstimators != null) hyperparams.n_estimators = props.nEstimators
  if (props.maxDepth != null) hyperparams.max_depth = props.maxDepth
  if (props.minSamplesLeaf != null) hyperparams.min_samples_leaf = props.minSamplesLeaf
  if (props.C != null) hyperparams.C = props.C
  if (props.alpha != null) hyperparams.alpha = props.alpha
  if (props.nNeighbors != null) hyperparams.n_neighbors = props.nNeighbors
  if (props.learningRate != null) hyperparams.learning_rate = props.learningRate
  if (props.maxIter != null) hyperparams.max_iter = props.maxIter

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

// 表格浏览器内嵌图表实例（结果可视化时使用）
let tableBrowserChartInstance = null
const tableBrowserChartRef = ref(null)
const onTableBrowserOpened = async () => {
  if (!tableBrowserData.showChart || !tableBrowserData.chartModelId || !tableBrowserChartRef.value) return
  try {
    const res = await mlApi.getVisualization(tableBrowserData.chartModelId, tableBrowserData.chartType)
    await nextTick()
    if (!tableBrowserChartRef.value) return
    const echarts = await import('echarts')
    if (tableBrowserChartInstance) tableBrowserChartInstance.dispose()
    tableBrowserChartInstance = echarts.init(tableBrowserChartRef.value, null, { renderer: 'canvas' })
    tableBrowserChartInstance.setOption(res.data.echarts_option)
  } catch (_) {
    // 图表加载失败时仅表格仍可查看
  }
}
const onTableBrowserClosed = () => {
  if (tableBrowserChartInstance) {
    tableBrowserChartInstance.dispose()
    tableBrowserChartInstance = null
  }
}

// Load ECharts visualization for the result-viz node（沿整条上游链路查找带 modelId 的节点）
const isChartLoading = ref(false)
const loadChart = async () => {
  const nodeId = selectedNode.value.id
  const upstreams = getAllUpstreamNodes(nodeId)
  const trainNode = upstreams.find(n => n.properties?.modelId)
  const modelId = trainNode?.properties?.modelId
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

// 从画布上的预处理节点打开配置对话框（参数存于节点 properties.config）
const openPreprocessConfigForNode = (nodeType) => {
  if (!selectedNode.value || selectedNode.value.properties?.nodeType !== nodeType) return
  const config = selectedNode.value.properties.config || {}
  const cols = upstreamColumns.value
  if (cols.length === 0 && (nodeType === 'group_by_column' || nodeType === 'aggregate_stats' || nodeType === 'math_calc' || nodeType === 'column_combine')) {
    ElMessage.warning('请先连接上游数据集或预处理节点以获取列列表')
    return
  }
  if (nodeType === 'group_by_column') {
    groupByForm.columns = config.columns || []
    groupByForm.aggregateFunction = config.aggregateFunction || 'sum'
    groupByForm.aggregateColumns = config.aggregateColumns || []
    showGroupByDialog.value = true
  } else if (nodeType === 'aggregate_stats') {
    aggregateStatsForm.groupColumns = config.groupColumns || []
    aggregateStatsForm.statsColumns = config.statsColumns || []
    aggregateStatsForm.statsFunctions = config.statsFunctions || []
    showAggregateStatsDialog.value = true
  } else if (nodeType === 'math_calc') {
    Object.assign(mathCalcForm, {
      newColumnName: config.newColumnName || '',
      calcType: config.calcType || 'binary',
      column1: config.column1 || '',
      column2: config.column2 || '',
      operator: config.operator || '+',
      constantValue: config.constantValue ?? 0
    })
    showMathCalcDialog.value = true
  } else if (nodeType === 'column_combine') {
    columnCombineForm.newColumnName = config.newColumnName || ''
    columnCombineForm.columns = config.columns || []
    columnCombineForm.combineMethod = config.combineMethod || 'concat'
    columnCombineForm.separator = config.separator != null ? config.separator : ' '
    showColumnCombineDialog.value = true
  } else if (['to_numeric', 'to_string', 'to_datetime'].includes(nodeType)) {
    typeConversionForm.conversionType = config.conversionType || nodeType
    typeConversionForm.columns = config.columns || []
    typeConversionForm.dateFormat = config.dateFormat || ''
    typeConversionForm.errorHandling = config.errorHandling || 'coerce'
    typeConversionForm.defaultValue = config.defaultValue ?? 0
    showTypeConversionDialog.value = true
  } else if (['one_hot', 'label_encode', 'tfidf'].includes(nodeType)) {
    toVectorForm.encodingType = config.encodingType || nodeType
    toVectorForm.columns = config.columns || []
    toVectorForm.prefix = config.prefix != null ? config.prefix : 'col_'
    toVectorForm.maxFeatures = config.maxFeatures ?? 1000
    showToVectorDialog.value = true
  } else if (['sort_by_column', 'move_column'].includes(nodeType)) {
    reorderForm.reorderType = config.reorderType || nodeType
    reorderForm.sortColumns = config.sortColumns || []
    reorderForm.sortOrder = config.sortOrder || 'asc'
    reorderForm.moveColumns = config.moveColumns || []
    reorderForm.targetPosition = config.targetPosition ?? 0
    showReorderDialog.value = true
  } else if (['delete_rows', 'delete_columns', 'drop_na'].includes(nodeType)) {
    deleteForm.deleteType = config.deleteType || nodeType
    deleteForm.columns = config.columns || []
    deleteForm.conditionType = config.conditionType || 'index_range'
    deleteForm.startIndex = config.startIndex ?? 0
    deleteForm.endIndex = config.endIndex ?? 0
    deleteForm.conditionColumn = config.conditionColumn || ''
    deleteForm.operator = config.operator || 'eq'
    deleteForm.compareValue = config.compareValue ?? ''
    deleteForm.dropNaMethod = config.dropNaMethod || 'any'
    showDeleteDialog.value = true
  } else if (nodeType === 'write-data-table') {
    ElMessage.info('请在右侧属性面板配置输出表名')
  } else {
    ElMessage.info(`该组件「${nodeType}」暂不支持在面板中配置，请在后端扩展`)
  }
}

const onModelSelectTaskTypeChange = () => {
  const t = selectedNode.value?.properties?.taskType
  if (t === 'regression') {
    if (!['linear_regression','ridge','lasso','random_forest','svr','gradient_boosting'].includes(selectedNode.value.properties.modelType)) {
      selectedNode.value.properties.modelType = 'linear_regression'
    }
  } else {
    if (!['logistic_regression','random_forest','svm','decision_tree','gradient_boosting','knn'].includes(selectedNode.value.properties.modelType)) {
      selectedNode.value.properties.modelType = 'random_forest'
    }
  }
  updateNodeProperty()
}

const modelTypeLabel = (modelType) => {
  const labels = {
    logistic_regression: '逻辑回归', random_forest: '随机森林', svm: '支持向量机',
    decision_tree: '决策树', gradient_boosting: '梯度提升', knn: 'K近邻',
    linear_regression: '线性回归', ridge: '岭回归', lasso: 'Lasso回归', svr: '支持向量回归'
  }
  return labels[modelType] || modelType || ''
}

const confirmModelConfigDialog = () => {
  updateNodeProperty()
  showModelConfigDialog.value = false
  ElMessage.success('模型参数已保存')
}

// 特征选择弹窗的列：使用「预处理后的列」ref，这样删除列等步骤后的列会正确显示
const featureSelectDialogColumns = computed(() => {
  if (!selectedNode.value || selectedNode.value.properties?.nodeType !== 'feature-select') return []
  return featureSelectEffectiveColumns.value
})

// 加载「到当前特征选择节点为止」的预处理链输出列（用于特征选择弹窗，避免仍显示已删除的列）
const loadEffectiveColumnsForFeatureSelect = async () => {
  if (!selectedNode.value || selectedNode.value.properties?.nodeType !== 'feature-select') return
  const { dataSourceNode, preprocessSteps } = getPreprocessChainAndDataSource(selectedNode.value.id)
  const datasetServerId = dataSourceNode?.properties?.datasetServerId
  if (!datasetServerId) {
    featureSelectEffectiveColumns.value = []
    return
  }
  try {
    if (preprocessSteps.length > 0) {
      const res = await mlApi.preprocess({
        dataset_id: datasetServerId,
        preprocess_steps: preprocessSteps
      })
      const cols = res.data.columns || []
      featureSelectEffectiveColumns.value = cols.map(c => ({
        label: `${c.name} (${c.dtype || ''})`,
        value: c.name
      }))
    } else {
      const cols = dataSourceNode?.properties?.columns || []
      featureSelectEffectiveColumns.value = cols.map(c => ({
        label: `${c.name} (${c.dtype || ''})`,
        value: c.name
      }))
    }
  } catch (e) {
    const msg = e.response?.data?.detail || e.message || '获取列列表失败'
    ElMessage.warning(msg)
    featureSelectEffectiveColumns.value = []
  }
}

// 打开特征选择配置弹窗前先加载「预处理后」的列列表
const openFeatureSelectDialog = async () => {
  await loadEffectiveColumnsForFeatureSelect()
  showFeatureSelectDialog.value = true
}

const confirmFeatureSelectDialog = () => {
  if (!selectedNode.value?.properties?.targetCol || !selectedNode.value?.properties?.featureCols?.length) {
    ElMessage.warning('请选择目标列和至少一个特征列')
    return
  }
  updateNodeProperty()
  showFeatureSelectDialog.value = false
  ElMessage.success('特征选择已保存')
}

const confirmModelPredictConfig = () => {
  updateNodeProperty()
  showModelPredictConfigDialog.value = false
  ElMessage.success('模型预测配置已保存')
}

// 按列分组配置对话框状态
const showGroupByDialog = ref(false)
const groupByForm = reactive({
  columns: [],
  aggregateFunction: 'sum',
  aggregateColumns: []
})

// 处理按列分组操作
const handleGroupByColumn = () => {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择一个数据预处理节点')
    return
  }
  
  const columns = upstreamColumns.value
  if (columns.length === 0) {
    ElMessage.warning('请先连接上游数据集节点')
    return
  }
  
  // 重置表单
  groupByForm.columns = []
  groupByForm.aggregateFunction = 'sum'
  groupByForm.aggregateColumns = []
  
  // 打开配置对话框
  showGroupByDialog.value = true
}

// 确认按列分组配置
const confirmGroupByConfig = () => {
  if (groupByForm.columns.length === 0) {
    ElMessage.warning('请选择至少一个分组列')
    return
  }
  if (groupByForm.aggregateColumns.length === 0) {
    ElMessage.warning('请选择至少一个聚合列')
    return
  }
  const config = {
    columns: [...groupByForm.columns],
    aggregateFunction: groupByForm.aggregateFunction,
    aggregateColumns: [...groupByForm.aggregateColumns]
  }
  if (selectedNode.value?.properties?.nodeType === 'group_by_column') {
    selectedNode.value.properties.config = config
    updateNodeProperty()
    showGroupByDialog.value = false
    ElMessage.success('参数已保存到节点')
    return
  }
  const step = { id: 'group_by_column', label: '按列分组', config }
  const existingIndex = appliedPreprocessSteps.value.findIndex(s => s.id === 'group_by_column')
  if (existingIndex > -1) appliedPreprocessSteps.value[existingIndex] = step
  else appliedPreprocessSteps.value.push(step)
  ElMessage.success('按列分组配置已应用')
  showGroupByDialog.value = false
}

// 聚合统计配置对话框状态
const showAggregateStatsDialog = ref(false)
const aggregateStatsForm = reactive({
  groupColumns: [],
  statsColumns: [],
  statsFunctions: []
})

// 处理聚合统计操作
const handleAggregateStats = () => {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择一个数据预处理节点')
    return
  }
  
  const columns = upstreamColumns.value
  if (columns.length === 0) {
    ElMessage.warning('请先连接上游数据集节点')
    return
  }
  
  // 重置表单
  aggregateStatsForm.groupColumns = []
  aggregateStatsForm.statsColumns = []
  aggregateStatsForm.statsFunctions = []
  
  // 打开配置对话框
  showAggregateStatsDialog.value = true
}

// 确认聚合统计配置
const confirmAggregateStatsConfig = () => {
  if (aggregateStatsForm.statsColumns.length === 0) {
    ElMessage.warning('请选择至少一个统计列')
    return
  }
  if (aggregateStatsForm.statsFunctions.length === 0) {
    ElMessage.warning('请选择至少一个统计函数')
    return
  }
  const config = {
    groupColumns: [...aggregateStatsForm.groupColumns],
    statsColumns: [...aggregateStatsForm.statsColumns],
    statsFunctions: [...aggregateStatsForm.statsFunctions]
  }
  if (selectedNode.value?.properties?.nodeType === 'aggregate_stats') {
    selectedNode.value.properties.config = config
    updateNodeProperty()
    showAggregateStatsDialog.value = false
    ElMessage.success('参数已保存到节点')
    return
  }
  const step = { id: 'aggregate_stats', label: '聚合统计', config }
  const existingIndex = appliedPreprocessSteps.value.findIndex(s => s.id === 'aggregate_stats')
  if (existingIndex > -1) appliedPreprocessSteps.value[existingIndex] = step
  else appliedPreprocessSteps.value.push(step)
  ElMessage.success('聚合统计配置已应用')
  showAggregateStatsDialog.value = false
}

// 数学计算配置对话框状态
const showMathCalcDialog = ref(false)
const mathCalcForm = reactive({
  newColumnName: '',
  calcType: 'binary',
  column1: '',
  column2: '',
  operator: '+',
  constantValue: 0
})

// 处理数学计算操作
const handleMathCalc = () => {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择一个数据预处理节点')
    return
  }
  
  const columns = upstreamColumns.value
  if (columns.length === 0) {
    ElMessage.warning('请先连接上游数据集节点')
    return
  }
  
  // 重置表单
  mathCalcForm.newColumnName = ''
  mathCalcForm.calcType = 'binary'
  mathCalcForm.column1 = ''
  mathCalcForm.column2 = ''
  mathCalcForm.operator = '+'
  mathCalcForm.constantValue = 0
  
  // 打开配置对话框
  showMathCalcDialog.value = true
}

// 确认数学计算配置
const confirmMathCalcConfig = () => {
  // 验证输入
  if (!mathCalcForm.newColumnName.trim()) {
    ElMessage.warning('请输入新列名')
    return
  }
  if (!mathCalcForm.column1) {
    ElMessage.warning('请选择第一列')
    return
  }
  if (mathCalcForm.calcType === 'binary' && !mathCalcForm.column2) {
    ElMessage.warning('请选择第二列')
    return
  }
  
  // 构建配置
  const config = {
    newColumnName: mathCalcForm.newColumnName.trim(),
    calcType: mathCalcForm.calcType,
    column1: mathCalcForm.column1,
    operator: mathCalcForm.operator
  }
  
  if (mathCalcForm.calcType === 'binary') {
    config.column2 = mathCalcForm.column2
  } else if (mathCalcForm.calcType === 'constant') {
    config.constantValue = mathCalcForm.constantValue
  }
  if (selectedNode.value?.properties?.nodeType === 'math_calc') {
    selectedNode.value.properties.config = config
    updateNodeProperty()
    showMathCalcDialog.value = false
    ElMessage.success('参数已保存到节点')
    return
  }
  const step = { id: 'math_calc', label: '数学计算', config }
  const existingIndex = appliedPreprocessSteps.value.findIndex(s => s.id === 'math_calc')
  if (existingIndex > -1) appliedPreprocessSteps.value[existingIndex] = step
  else appliedPreprocessSteps.value.push(step)
  ElMessage.success('数学计算配置已应用')
  showMathCalcDialog.value = false
}

// 列组合配置对话框状态
const showColumnCombineDialog = ref(false)
const columnCombineForm = reactive({
  newColumnName: '',
  columns: [],
  combineMethod: 'concat',
  separator: ''
})

// 处理列组合操作
const handleColumnCombine = () => {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择一个数据预处理节点')
    return
  }
  
  const columns = upstreamColumns.value
  if (columns.length === 0) {
    ElMessage.warning('请先连接上游数据集节点')
    return
  }
  
  // 重置表单
  columnCombineForm.newColumnName = ''
  columnCombineForm.columns = []
  columnCombineForm.combineMethod = 'concat'
  columnCombineForm.separator = ''
  
  // 打开配置对话框
  showColumnCombineDialog.value = true
}

// 确认列组合配置
const confirmColumnCombineConfig = () => {
  // 验证输入
  if (!columnCombineForm.newColumnName.trim()) {
    ElMessage.warning('请输入新列名')
    return
  }
  if (columnCombineForm.columns.length === 0) {
    ElMessage.warning('请选择至少一列')
    return
  }
  if (columnCombineForm.columns.length < 2 && columnCombineForm.combineMethod !== 'concat') {
    ElMessage.warning('数学组合方式需要至少选择两列')
    return
  }
  const config = {
    newColumnName: columnCombineForm.newColumnName.trim(),
    columns: [...columnCombineForm.columns],
    combineMethod: columnCombineForm.combineMethod,
    separator: columnCombineForm.separator != null ? columnCombineForm.separator : ' '
  }
  if (selectedNode.value?.properties?.nodeType === 'column_combine') {
    selectedNode.value.properties.config = config
    updateNodeProperty()
    showColumnCombineDialog.value = false
    ElMessage.success('参数已保存到节点')
    return
  }
  const step = { id: 'column_combine', label: '列组合', config }
  const existingIndex = appliedPreprocessSteps.value.findIndex(s => s.id === 'column_combine')
  if (existingIndex > -1) appliedPreprocessSteps.value[existingIndex] = step
  else appliedPreprocessSteps.value.push(step)
  ElMessage.success('列组合配置已应用')
  showColumnCombineDialog.value = false
}

// 列类型转换配置对话框状态
const showTypeConversionDialog = ref(false)
const typeConversionForm = reactive({
  conversionType: 'to_numeric',
  columns: [],
  dateFormat: '%Y-%m-%d %H:%M:%S',
  errorHandling: 'coerce',
  defaultValue: 0
})

// 处理列类型转换操作
const handleTypeConversion = () => {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择一个数据预处理节点')
    return
  }
  
  const columns = upstreamColumns.value
  if (columns.length === 0) {
    ElMessage.warning('请先连接上游数据集节点')
    return
  }
  
  // 重置表单
  typeConversionForm.conversionType = 'to_numeric'
  typeConversionForm.columns = []
  typeConversionForm.dateFormat = '%Y-%m-%d %H:%M:%S'
  typeConversionForm.errorHandling = 'coerce'
  typeConversionForm.defaultValue = 0
  
  // 打开配置对话框
  showTypeConversionDialog.value = true
}

// 确认列类型转换配置
const confirmTypeConversionConfig = () => {
  // 验证输入
  if (typeConversionForm.columns.length === 0) {
    ElMessage.warning('请选择至少一列')
    return
  }
  if (typeConversionForm.conversionType === 'to_datetime' && !typeConversionForm.dateFormat.trim()) {
    ElMessage.warning('请输入日期时间格式')
    return
  }
  
  // 构建配置
  const config = {
    conversionType: typeConversionForm.conversionType,
    columns: [...typeConversionForm.columns]
  }
  
  if (typeConversionForm.conversionType === 'to_datetime') {
    config.dateFormat = typeConversionForm.dateFormat.trim()
  } else   if (typeConversionForm.conversionType === 'to_numeric') {
    config.errorHandling = typeConversionForm.errorHandling
    if (typeConversionForm.errorHandling === 'default') {
      config.defaultValue = typeConversionForm.defaultValue
    }
  }
  if (selectedNode.value?.properties?.nodeType === typeConversionForm.conversionType) {
    selectedNode.value.properties.config = config
    updateNodeProperty()
    showTypeConversionDialog.value = false
    ElMessage.success('参数已保存到节点')
    return
  }
  const step = {
    id: typeConversionForm.conversionType,
    label: typeConversionForm.conversionType === 'to_numeric' ? '转数值型' : typeConversionForm.conversionType === 'to_string' ? '转字符串' : '转日期时间',
    config
  }
  const existingIndex = appliedPreprocessSteps.value.findIndex(s => s.id === typeConversionForm.conversionType)
  if (existingIndex > -1) appliedPreprocessSteps.value[existingIndex] = step
  else appliedPreprocessSteps.value.push(step)
  ElMessage.success('列类型转换配置已应用')
  showTypeConversionDialog.value = false
}

// 列转向量配置对话框状态
const showToVectorDialog = ref(false)
const toVectorForm = reactive({
  encodingType: 'one_hot',
  columns: [],
  prefix: '',
  maxFeatures: 100
})

// 处理列转向量操作
const handleToVector = () => {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择一个数据预处理节点')
    return
  }
  
  const columns = upstreamColumns.value
  if (columns.length === 0) {
    ElMessage.warning('请先连接上游数据集节点')
    return
  }
  
  // 重置表单
  toVectorForm.encodingType = 'one_hot'
  toVectorForm.columns = []
  toVectorForm.prefix = ''
  toVectorForm.maxFeatures = 100
  
  // 打开配置对话框
  showToVectorDialog.value = true
}

// 确认列转向量配置
const confirmToVectorConfig = () => {
  // 验证输入
  if (toVectorForm.columns.length === 0) {
    ElMessage.warning('请选择至少一列')
    return
  }
  
  // 构建配置
  const config = {
    encodingType: toVectorForm.encodingType,
    columns: [...toVectorForm.columns]
  }
  
  if (toVectorForm.encodingType === 'one_hot') {
    config.prefix = toVectorForm.prefix
  } else if (toVectorForm.encodingType === 'tfidf') {
    config.maxFeatures = toVectorForm.maxFeatures
  }
  if (selectedNode.value?.properties?.nodeType === toVectorForm.encodingType) {
    selectedNode.value.properties.config = config
    updateNodeProperty()
    showToVectorDialog.value = false
    ElMessage.success('参数已保存到节点')
    return
  }
  const step = {
    id: toVectorForm.encodingType,
    label: toVectorForm.encodingType === 'one_hot' ? 'One-Hot编码' : toVectorForm.encodingType === 'label_encode' ? 'Label编码' : 'TF-IDF',
    config
  }
  const existingIndex = appliedPreprocessSteps.value.findIndex(s => s.id === toVectorForm.encodingType)
  if (existingIndex > -1) appliedPreprocessSteps.value[existingIndex] = step
  else appliedPreprocessSteps.value.push(step)
  ElMessage.success('列转向量配置已应用')
  showToVectorDialog.value = false
}

// 列重排配置对话框状态
const showReorderDialog = ref(false)
const reorderForm = reactive({
  reorderType: 'sort_by_column',
  sortColumns: [],
  sortOrder: 'asc',
  moveColumns: [],
  targetPosition: 0
})

// 处理列重排操作
const handleReorder = () => {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择一个数据预处理节点')
    return
  }
  
  const columns = upstreamColumns.value
  if (columns.length === 0) {
    ElMessage.warning('请先连接上游数据集节点')
    return
  }
  
  // 重置表单
  reorderForm.reorderType = 'sort_by_column'
  reorderForm.sortColumns = []
  reorderForm.sortOrder = 'asc'
  reorderForm.moveColumns = []
  reorderForm.targetPosition = 0
  
  // 打开配置对话框
  showReorderDialog.value = true
}

// 确认列重排配置
const confirmReorderConfig = () => {
  // 验证输入
  if (reorderForm.reorderType === 'sort_by_column' && reorderForm.sortColumns.length === 0) {
    ElMessage.warning('请选择至少一列进行排序')
    return
  }
  if (reorderForm.reorderType === 'move_column' && reorderForm.moveColumns.length === 0) {
    ElMessage.warning('请选择至少一列进行移动')
    return
  }
  
  // 构建配置
  const config = {
    reorderType: reorderForm.reorderType
  }
  
  if (reorderForm.reorderType === 'sort_by_column') {
    config.sortColumns = [...reorderForm.sortColumns]
    config.sortOrder = reorderForm.sortOrder
  } else if (reorderForm.reorderType === 'move_column') {
    config.moveColumns = [...reorderForm.moveColumns]
    config.targetPosition = reorderForm.targetPosition
  }
  if (selectedNode.value?.properties?.nodeType === reorderForm.reorderType) {
    selectedNode.value.properties.config = config
    updateNodeProperty()
    showReorderDialog.value = false
    ElMessage.success('参数已保存到节点')
    return
  }
  const step = {
    id: reorderForm.reorderType,
    label: reorderForm.reorderType === 'sort_by_column' ? '排序' : '移动列',
    config
  }
  const existingIndex = appliedPreprocessSteps.value.findIndex(s => s.id === reorderForm.reorderType)
  if (existingIndex > -1) appliedPreprocessSteps.value[existingIndex] = step
  else appliedPreprocessSteps.value.push(step)
  ElMessage.success('列重排配置已应用')
  showReorderDialog.value = false
}

// 删除配置对话框状态
const showDeleteDialog = ref(false)
const deleteForm = reactive({
  deleteType: 'delete_rows',
  conditionType: 'index_range',
  startIndex: 0,
  endIndex: 0,
  conditionColumn: '',
  operator: 'eq',
  compareValue: '',
  columns: [],
  dropNaMethod: 'any'
})

// 处理删除操作
const handleDelete = () => {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择一个数据预处理节点')
    return
  }
  
  const columns = upstreamColumns.value
  if (columns.length === 0) {
    ElMessage.warning('请先连接上游数据集节点')
    return
  }
  
  // 重置表单
  deleteForm.deleteType = 'delete_rows'
  deleteForm.conditionType = 'index_range'
  deleteForm.startIndex = 0
  deleteForm.endIndex = 0
  deleteForm.conditionColumn = ''
  deleteForm.operator = 'eq'
  deleteForm.compareValue = ''
  deleteForm.columns = []
  deleteForm.dropNaMethod = 'any'
  
  // 打开配置对话框
  showDeleteDialog.value = true
}

// 确认删除配置
const confirmDeleteConfig = () => {
  // 验证输入
  if (deleteForm.deleteType === 'delete_rows') {
    if (deleteForm.conditionType === 'index_range') {
      if (deleteForm.startIndex < 0 || deleteForm.endIndex < 0) {
        ElMessage.warning('请输入有效的索引范围')
        return
      }
      if (deleteForm.startIndex > deleteForm.endIndex) {
        ElMessage.warning('起始索引不能大于结束索引')
        return
      }
    } else if (deleteForm.conditionType === 'condition') {
      if (!deleteForm.conditionColumn) {
        ElMessage.warning('请选择条件列')
        return
      }
      if (!deleteForm.compareValue && deleteForm.compareValue !== 0) {
        ElMessage.warning('请输入比较值')
        return
      }
    }
  } else if (deleteForm.deleteType === 'delete_columns' && deleteForm.columns.length === 0) {
    ElMessage.warning('请选择至少一列')
    return
  }
  
  // 构建配置
  const config = {
    deleteType: deleteForm.deleteType
  }
  
  if (deleteForm.deleteType === 'delete_rows') {
    config.conditionType = deleteForm.conditionType
    if (deleteForm.conditionType === 'index_range') {
      config.startIndex = deleteForm.startIndex
      config.endIndex = deleteForm.endIndex
    } else if (deleteForm.conditionType === 'condition') {
      config.conditionColumn = deleteForm.conditionColumn
      config.operator = deleteForm.operator
      config.compareValue = deleteForm.compareValue
    }
  } else if (deleteForm.deleteType === 'delete_columns') {
    config.columns = [...deleteForm.columns]
  } else if (deleteForm.deleteType === 'drop_na') {
    config.dropNaMethod = deleteForm.dropNaMethod
  }
  if (selectedNode.value?.properties?.nodeType === deleteForm.deleteType) {
    selectedNode.value.properties.config = config
    updateNodeProperty()
    showDeleteDialog.value = false
    ElMessage.success('参数已保存到节点')
    return
  }
  const step = {
    id: deleteForm.deleteType,
    label: deleteForm.deleteType === 'delete_rows' ? '删除行' : deleteForm.deleteType === 'delete_columns' ? '删除列' : '删除缺失值',
    config
  }
  const existingIndex = appliedPreprocessSteps.value.findIndex(s => s.id === deleteForm.deleteType)
  if (existingIndex > -1) appliedPreprocessSteps.value[existingIndex] = step
  else appliedPreprocessSteps.value.push(step)
  ElMessage.success('删除配置已应用')
  showDeleteDialog.value = false
}

// 检查预处理是否已应用
const isPreprocessApplied = (preprocessId) => {
  return appliedPreprocessSteps.value.some(step => step.id === preprocessId)
}

// 删除已应用的预处理步骤
const removePreprocessStep = (preprocessId) => {
  ElMessageBox.confirm('确定要撤回这个预处理操作吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = appliedPreprocessSteps.value.findIndex(step => step.id === preprocessId)
    if (index > -1) {
      const removedStep = appliedPreprocessSteps.value[index]
      appliedPreprocessSteps.value.splice(index, 1)
      ElMessage.success(`已撤回: ${removedStep.label}`)
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 在表格浏览器中打开当前节点的预测结果
const openTableBrowserForPredictResult = () => {
  const predictions = nodeState.value?.result?.predictions
  if (!predictions?.length) {
    ElMessage.warning('暂无预测结果，请先执行预测')
    return
  }
  const label = selectedNode.value?.properties?.label || '模型预测'
  const columns = [{ key: 'index', label: '序号' }, { key: 'prediction', label: '预测值' }]
  const rows = predictions.map((p, i) => ({ index: i + 1, prediction: p }))
  tableBrowserData.value = { nodeLabel: label + ' 结果', columns, rows }
  showTableBrowserDialog.value = true
}

// Run prediction for the model-predict node（沿整条上游链路查找带 modelId 的节点）
const runPredict = async () => {
  const nodeId = selectedNode.value.id
  const upstreams = getAllUpstreamNodes(nodeId)
  const trainNode = upstreams.find(n => n.properties?.modelId)
  const modelId = trainNode?.properties?.modelId
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
    const label = selectedNode.value.properties?.label || '模型预测'
    const columns = [{ key: 'index', label: '序号' }, { key: 'prediction', label: '预测值' }]
    const rows = (res.data.predictions || []).map((p, i) => ({ index: i + 1, prediction: p }))
    tableBrowserData.value = { nodeLabel: label + ' 结果', columns, rows }
    showTableBrowserDialog.value = true
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
.dataset-in-library .empty-workflows {
  padding: 8px 0;
  text-align: center;
}
.dataset-in-library .empty-workflows p {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* 上传文件按钮：图标与读数据表一致大小 */
.upload-file-btn {
  width: 100%;
  margin-bottom: 10px;
  .el-icon {
    font-size: 22px;
    margin-right: 6px;
  }
}

/* 数据集上传子目录标题前的图标，与读数据表同风格 */
.subgroup-title-with-icon .subgroup-title-icon-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 6px;
  color: #10b981;
  .el-icon {
    font-size: 22px;
  }
}

.component-subgroup {
  margin-bottom: 12px;
  &:last-child { margin-bottom: 0; }
}

/* 层级缩进：大目录下子目录逐层往右 */
.component-list-tiered > .component-subgroup.tier-1 {
  padding-left: 14px;
  border-left: 1px solid rgba(255, 255, 255, 0.06);
  margin-left: 4px;
}
.component-subgroup .subgroup-inner.tier-2 {
  padding-left: 12px;
  margin-left: 4px;
  border-left: 1px solid rgba(255, 255, 255, 0.05);
}
.component-subgroup-nested .subgroup-children {
  padding-left: 12px;
}

.subgroup-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
  padding-left: 4px;
  min-height: 24px;
}
.subgroup-title {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  user-select: none;
  flex: 1;
  min-width: 0;
  &:hover {
    color: rgba(255, 255, 255, 0.75);
  }
}
.subgroup-chevron {
  font-size: 12px;
  transition: transform 0.2s;
  &.collapsed {
    opacity: 0.8;
  }
}
.component-subgroup-nested .subgroup-children {
  padding-left: 16px;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  margin-left: 6px;
}
.subgroup-inner {
  margin-bottom: 8px;
  .subgroup-title { font-size: 11px; }
  .subgroup-children { padding-left: 12px; }
}
.subgroup-dropdown-btn {
  padding: 2px 4px;
  color: rgba(255, 255, 255, 0.4);
  &:hover {
    color: rgba(255, 255, 255, 0.8);
  }
}
.subgroup-children {
  padding-left: 8px;
}

.feature-select-dialog .column-tags {
  max-height: 120px;
  overflow-y: auto;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
}

.preprocess-tree-panel {
  background: rgba(15, 23, 42, 0.6);
  border-radius: 8px;
  padding: 12px;
  margin-top: 8px;
  max-height: 400px;
  overflow-y: auto;
  
  :deep(.el-tree-node) {
    padding: 4px 0;
  }
  
  :deep(.el-tree-node__content) {
    height: 32px;
    align-items: center;
  }
  
  :deep(.el-tree-node.is-current > .el-tree-node__content) {
    background-color: rgba(20, 184, 166, 0.2);
    color: #14b8a6;
  }
  
  :deep(.el-tree-node__expand-icon) {
    color: rgba(255, 255, 255, 0.4);
  }
  
  .custom-tree-node {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

.component-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
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

.component-item-upload {
  cursor: pointer;
  &:active {
    transform: scale(0.98);
  }
}

/* 组件图标：小尺寸无背景色，颜色由行内 style 控制 */
.item-icon {
  width: 22px;
  height: 22px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 15px;
}

.item-icon-unified {
  background: transparent !important;
}

/* 组件名称左侧的小色点指示器 */
.item-color-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
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
  gap: 8px;
  padding: 8px 10px;
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
    width: 22px;
    height: 22px;
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

.form-tip {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
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

// 表格浏览器 / 交互浏览器
.table-browser-dialog .el-table { font-size: 12px; }
.interactive-browser-dialog .el-dialog__body { padding-top: 12px; }
.interactive-browser-body { display: flex; flex-direction: column; gap: 20px; }
.interactive-chart-section {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.chart-section-title { font-size: 14px; color: rgba(255, 255, 255, 0.9); margin-bottom: 12px; }
.chart-bars { display: flex; flex-direction: column; gap: 8px; max-height: 280px; overflow-y: auto; }
.chart-bar-row {
  display: flex; align-items: center; gap: 12px; font-size: 12px;
  .chart-bar-label { flex: 0 0 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: rgba(255,255,255,0.85); }
  .chart-bar-track { flex: 1; height: 20px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; }
  .chart-bar-fill { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 4px; transition: width 0.3s; }
  .chart-bar-value { flex: 0 0 50px; text-align: right; color: rgba(255,255,255,0.6); }
}
.chart-placeholder { color: rgba(255,255,255,0.4); font-size: 13px; padding: 20px; text-align: center; }

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

/* 自定义节点样式 - 白底、浅蓝边框、左侧图标、中间名称、右侧状态（与参考图一致） */
:global(.custom-node) {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  min-width: 140px;
  height: 100%;
  cursor: move;
  transition: all 0.2s ease;
  position: relative;
  z-index: 1;
  box-sizing: border-box;
}

:global(.custom-node.custom-node-card) {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 8px 12px;
  gap: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

:global(.custom-node.custom-node-card:hover) {
  border-color: #7dd3fc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  z-index: 2;
}

:global(.custom-node .node-icon-wrap) {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0ea5e9;
}
:global(.custom-node .node-icon-wrap svg) {
  width: 100%;
  height: 100%;
}

:global(.custom-node .node-label) {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
}

:global(.custom-node .node-status-wrap) {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
:global(.custom-node .node-status) {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  font-size: 12px;
  line-height: 18px;
  text-align: center;
  font-weight: 600;
}
:global(.custom-node .node-status-success) {
  background: #22c55e;
  color: #fff;
}
:global(.custom-node .node-status-error) {
  background: #ef4444;
  color: #fff;
}
:global(.custom-node .node-status-running) {
  background: #f59e0b;
  color: #fff;
}
:global(.custom-node .node-status-none) {
  background: transparent;
  border: 1px solid rgba(0, 0, 0, 0.08);
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
  gap: 8px;
  padding: 8px 10px;
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
    width: 22px;
    height: 22px;
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
  min-height: 0;
}

.log-item {
  display: flex;
  gap: 12px;
  padding: 4px 0;
  
  &.separator {
    color: rgba(102, 126, 234, 0.9);
    font-weight: 600;
    margin: 6px 0 2px;
  }
  
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

// 预处理树形面板样式
.preprocess-tree-panel {
  background: rgba(30, 41, 59, 0.5);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  max-height: 300px;
  overflow-y: auto;

  :deep(.el-tree) {
    background: transparent;
    color: rgba(255, 255, 255, 0.85);

    .el-tree-node__content {
      height: 32px;
      border-radius: 4px;

      &:hover {
        background: rgba(102, 126, 234, 0.2);
      }
    }

    .el-tree-node__expand-icon {
      color: rgba(255, 255, 255, 0.5);

      &.is-leaf {
        color: transparent;
      }
    }

    .custom-tree-node {
      display: flex;
      align-items: center;
      flex: 1;
      font-size: 14px;
      flex-wrap: nowrap;
      overflow: hidden;

      .el-icon {
        font-size: 16px;
        color: #14b8a6;
      }

      .el-button {
        flex-shrink: 0;
        padding: 4px;
        height: auto;
      }
    }

    .el-tree-node.is-current > .el-tree-node__content {
      background: rgba(102, 126, 234, 0.3);
    }
  }
}
</style>
