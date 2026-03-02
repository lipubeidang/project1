<template>
  <div class="tpl-upload">
    <Navbar />
    
    <div class="page-container">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h3>模版分类</h3>
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
        <!-- 页面标题 -->
        <div class="content-header animate-slide-up">
          <div class="header-info">
            <h1 class="page-title">模版数据上传</h1>
            <p class="page-desc" v-if="currentCategory">
              当前目录：{{ currentCategory.name }}
            </p>
            <p class="page-desc" v-else>请从左侧选择目录后上传数据</p>
          </div>
        </div>

        <!-- 步骤指示器 -->
        <div class="steps-container animate-slide-up" v-if="currentCategory">
          <el-steps :active="currentStep" align-center finish-status="success">
            <el-step title="选择模版" description="选择数据对应的模版" />
            <el-step title="选择上传方式" description="批量上传或单条录入" />
            <el-step title="上传数据" description="提交数据" />
          </el-steps>
        </div>

        <!-- 步骤1: 选择模版 -->
        <div class="template-select-section animate-slide-up delay-1" v-if="currentCategory && currentStep === 0">
          <div class="section-header">
            <h3 class="section-title">
              <el-icon><Collection /></el-icon>
              选择模版
            </h3>
            <span class="section-desc">请选择您要上传数据对应的模版</span>
          </div>
          
          <!-- 搜索框 -->
          <div class="template-search">
            <el-input
              v-model="templateSearch"
              placeholder="搜索模版名称..."
              clearable
              :prefix-icon="Search"
            />
          </div>
          
          <div class="template-list" v-loading="loadingTemplates">
            <div 
              v-for="tpl in filteredTemplates" 
              :key="tpl.id"
              class="template-item"
              :class="{ active: selectedTemplate?.id === tpl.id }"
              @click="selectTemplate(tpl)"
            >
              <div class="template-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="template-info">
                <h4>{{ tpl.name }}</h4>
                <p>{{ tpl.description || '暂无描述' }}</p>
                <div class="template-meta">
                  <span class="meta-item">
                    <el-icon><Calendar /></el-icon>
                    {{ tpl.createTime || '2024-01-01' }}
                  </span>
                </div>
              </div>
              <div class="template-check" v-if="selectedTemplate?.id === tpl.id">
                <el-icon class="check-icon"><CircleCheck /></el-icon>
              </div>
            </div>
            <el-empty v-if="!loadingTemplates && filteredTemplates.length === 0" description="该目录下暂无可用模版" />
          </div>
          
          <div class="step-actions">
            <el-button type="primary" size="large" :disabled="!selectedTemplate" @click="goToStep(1)">
              下一步：选择上传方式
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 步骤2: 选择上传方式 -->
        <div class="upload-mode-section animate-slide-up" v-if="currentCategory && currentStep === 1">
          <div class="section-header">
            <h3 class="section-title">
              <el-icon><Operation /></el-icon>
              选择上传方式
            </h3>
            <span class="section-desc">
              当前模版：<el-tag type="primary">{{ selectedTemplate?.name }}</el-tag>
            </span>
          </div>
          
          <div class="upload-mode-cards">
            <!-- 批量上传卡片 -->
            <div 
              class="mode-card"
              :class="{ active: uploadMode === 'batch' }"
              @click="selectUploadMode('batch')"
            >
              <div class="mode-icon batch">
                <el-icon :size="40"><Files /></el-icon>
              </div>
              <div class="mode-content">
                <h4>批量上传</h4>
                <p>通过Excel文件批量导入多条数据，适合大量数据录入</p>
                <ul class="mode-features">
                  <li><el-icon><Check /></el-icon> 支持Excel格式(.xlsx, .xls)</li>
                  <li><el-icon><Check /></el-icon> 单次可导入多条数据</li>
                  <li><el-icon><Check /></el-icon> 提供模版下载</li>
                </ul>
              </div>
              <div class="mode-badge" v-if="uploadMode === 'batch'">
                <el-icon><CircleCheck /></el-icon>
              </div>
            </div>
            
            <!-- 单条上传卡片 -->
            <div 
              class="mode-card"
              :class="{ active: uploadMode === 'single' }"
              @click="selectUploadMode('single')"
            >
              <div class="mode-icon single">
                <el-icon :size="40"><EditPen /></el-icon>
              </div>
              <div class="mode-content">
                <h4>单条录入</h4>
                <p>通过表单逐条录入数据，适合少量数据或精确录入</p>
                <ul class="mode-features">
                  <li><el-icon><Check /></el-icon> 表单化录入更直观</li>
                  <li><el-icon><Check /></el-icon> 实时校验数据格式</li>
                  <li><el-icon><Check /></el-icon> 支持保存为草稿</li>
                </ul>
              </div>
              <div class="mode-badge" v-if="uploadMode === 'single'">
                <el-icon><CircleCheck /></el-icon>
              </div>
            </div>
          </div>
          
          <div class="step-actions">
            <el-button size="large" @click="goToStep(0)">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button type="primary" size="large" :disabled="!uploadMode" @click="goToStep(2)">
              下一步：{{ uploadMode === 'batch' ? '批量上传' : '数据录入' }}
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 步骤3: 批量上传 -->
        <div class="upload-section animate-slide-up" v-if="currentCategory && currentStep === 2 && uploadMode === 'batch'">
          <div class="section-header">
            <h3 class="section-title">
              <el-icon><UploadFilled /></el-icon>
              批量上传数据
            </h3>
            <span class="section-desc">
              当前模版：<el-tag type="primary">{{ selectedTemplate?.name }}</el-tag>
            </span>
          </div>
          
          <!-- 下载模版提示卡片 -->
          <div class="download-template-card">
            <div class="card-icon">
              <el-icon :size="32"><Download /></el-icon>
            </div>
            <div class="card-content">
              <h4>第一步：下载数据模版</h4>
              <p>请先下载Excel模版，按照模版格式填写数据后再上传</p>
            </div>
            <el-button type="primary" @click="downloadTemplate" :loading="downloadingTemplate">
              <el-icon><Download /></el-icon>
              下载模版
            </el-button>
          </div>

          <div class="upload-area-wrapper">
            <h4 class="upload-title">第二步：上传Excel数据文件</h4>
            <div class="upload-area">
              <el-upload
                ref="excelUploadRef"
                class="upload-dragger"
                drag
                :auto-upload="false"
                :limit="1"
                accept=".xlsx,.xls,.csv"
                :on-change="handleBatchExcelChange"
                :on-remove="removeBatchExcel"
                :file-list="batchExcelFile ? [{ name: batchExcelFile.name, raw: batchExcelFile }] : []"
              >
                <div class="upload-content">
                  <div class="upload-icon-wrapper">
                    <el-icon class="upload-icon"><UploadFilled /></el-icon>
                  </div>
                  <div class="upload-text">
                    <p class="main-text">将Excel文件拖到此处，或<em>点击选择</em></p>
                    <p class="sub-text">支持 .xlsx, .xls, .csv 格式，单个文件不超过 50MB</p>
                  </div>
                </div>
              </el-upload>
            </div>
            
            <!-- 已选择的Excel文件 -->
            <div class="selected-excel" v-if="batchExcelFile">
              <el-tag type="success" closable @close="removeBatchExcel">
                <el-icon><Document /></el-icon>
                {{ batchExcelFile.name }} ({{ formatFileSize(batchExcelFile.size) }})
              </el-tag>
            </div>
          </div>

          <!-- 附件上传区域（当模板包含文件型/图片型字段时显示） -->
          <div class="upload-area-wrapper" v-if="hasFileTypeFields">
            <h4 class="upload-title">
              第三步：上传附件文件
              <el-tooltip content="Excel中的图片型和文件型字段填写的是文件名，请在这里上传对应的文件" placement="top">
                <el-icon class="help-icon"><QuestionFilled /></el-icon>
              </el-tooltip>
            </h4>
            <el-alert 
              title="推荐：选择包含所有附件的文件夹，系统会自动匹配Excel中的文件路径" 
              type="success" 
              :closable="false"
              show-icon
              style="margin-bottom: 16px"
            />
            
            <!-- 上传方式切换 -->
            <div class="upload-mode-toggle" style="margin-bottom: 16px">
              <el-radio-group v-model="attachmentUploadMode" size="small">
                <el-radio-button value="folder">
                  <el-icon><FolderOpened /></el-icon>
                  选择文件夹（推荐）
                </el-radio-button>
                <el-radio-button value="files">
                  <el-icon><Document /></el-icon>
                  选择多个文件
                </el-radio-button>
              </el-radio-group>
            </div>
            
            <!-- 文件夹上传 -->
            <div class="upload-area" v-if="attachmentUploadMode === 'folder'">
              <div 
                class="folder-upload-dragger"
                @click="triggerFolderSelect"
                @dragover.prevent
                @drop.prevent="handleFolderDrop"
              >
                <input
                  ref="folderInputRef"
                  type="file"
                  webkitdirectory
                  directory
                  multiple
                  style="display: none"
                  @change="handleFolderSelect"
                />
                <div class="upload-content">
                  <div class="upload-icon-wrapper" style="background: linear-gradient(135deg, #10b981, #059669)">
                    <el-icon class="upload-icon"><FolderOpened /></el-icon>
                  </div>
                  <div class="upload-text">
                    <p class="main-text">点击选择文件夹，或将文件夹拖到此处</p>
                    <p class="sub-text">系统会自动扫描文件夹内的所有文件，并匹配Excel中的路径</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 多文件上传 -->
            <div class="upload-area" v-else>
              <el-upload
                ref="attachmentUploadRef"
                class="upload-dragger"
                drag
                multiple
                :auto-upload="false"
                :on-change="handleBatchAttachmentChange"
                :on-remove="removeBatchAttachment"
              >
                <div class="upload-content">
                  <div class="upload-icon-wrapper" style="background: linear-gradient(135deg, #f59e0b, #f97316)">
                    <el-icon class="upload-icon"><Picture /></el-icon>
                  </div>
                  <div class="upload-text">
                    <p class="main-text">将附件文件拖到此处，或<em>点击选择</em></p>
                    <p class="sub-text">支持图片、文档等多种格式，可选择多个文件</p>
                  </div>
                </div>
              </el-upload>
            </div>
            
            <!-- 已选择的附件文件列表 -->
            <div class="selected-attachments" v-if="batchAttachmentFiles.length > 0">
              <h5>已选择 {{ batchAttachmentFiles.length }} 个附件文件：</h5>
              <div class="attachment-tags">
                <el-tag 
                  v-for="(file, index) in batchAttachmentFiles" 
                  :key="index"
                  type="info" 
                  closable 
                  @close="removeBatchAttachment(file)"
                  style="margin: 4px"
                >
                  <el-icon><Document /></el-icon>
                  {{ file.name }} ({{ formatFileSize(file.size) }})
                </el-tag>
              </div>
            </div>
          </div>

          <!-- 上传进度 -->
          <div class="upload-progress" v-if="batchUploading">
            <el-progress :percentage="uploadProgress" :status="uploadStatus" :stroke-width="10" />
            <p class="progress-text">{{ uploadStatusText }}</p>
          </div>
          
          <div class="step-actions">
            <el-button size="large" @click="goToStep(1)">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button type="success" size="large" :disabled="!batchExcelFile" :loading="batchUploading" @click="submitBatchUpload">
              <el-icon><CircleCheck /></el-icon>
              提交上传
            </el-button>
          </div>
        </div>

        <!-- 步骤3: 单条录入 -->
        <div class="single-entry-section animate-slide-up" v-if="currentCategory && currentStep === 2 && uploadMode === 'single'">
          <div class="section-header">
            <h3 class="section-title">
              <el-icon><EditPen /></el-icon>
              单条数据录入
            </h3>
            <span class="section-desc">
              当前模版：<el-tag type="primary">{{ selectedTemplate?.id }}</el-tag>
            </span>
          </div>
          
          <div class="form-container">
            <el-form 
              ref="singleFormRef"
              :model="singleFormData" 
              :rules="singleFormRules"
              label-width="120px"
              label-position="top"
              class="single-form"
            >
              <!-- 对象字段区域 -->
              <div class="field-area" v-if="processedFieldGroups.object.length > 0">
                <div class="area-header">
                  <span class="area-title">对象</span>
                  <span class="area-count">{{ processedFieldGroups.object.length }} 个字段</span>
                </div>
                <div class="form-grid">
                  <template v-for="field in processedFieldGroups.object" :key="field.name">
                    <!-- 枚举型字段 - 下拉框 -->
                    <el-form-item 
                      v-if="field.isEnum"
                      :label="field.enumName"
                      :prop="field.name"
                      :required="field.required"
                      class="enum-field"
                    >
                      <template #label>
                        <span class="field-label-with-type">
                          <span class="required-star" v-if="field.required">*</span>
                          <span>{{ field.enumName }}</span>
                          <el-tag size="small" :type="getDataTypeTagType('枚举型')">枚举型</el-tag>
                        </span>
                      </template>
                      <el-select v-model="singleFormData[field.name]" :placeholder="'请选择' + field.enumName" style="width: 100%">
                        <el-option 
                          v-for="opt in field.options" 
                          :key="typeof opt === 'object' ? opt.value : opt" 
                          :label="typeof opt === 'object' ? opt.label : opt" 
                          :value="typeof opt === 'object' ? opt.value : opt" 
                        />
                      </el-select>
                    </el-form-item>
                    <!-- 普通字段 -->
                    <el-form-item 
                      v-else
                      :prop="field.name"
                      :required="field.required"
                    >
                      <template #label>
                        <span class="field-label-with-type">
                          <span class="required-star" v-if="field.required">*</span>
                          <span>{{ field.label }}</span>
                          <el-tag size="small" :type="getDataTypeTagType(field.dataType)">{{ field.dataType }}</el-tag>
                        </span>
                      </template>
                      <!-- 文件型/图片型字段 -->
                      <template v-if="isFileType(field.dataType)">
                        <div class="file-upload-field">
                          <el-input
                            v-model="singleFormData[field.name]"
                            :placeholder="'请输入文件名，如: example' + (field.dataType === '图片型' ? '.png' : '.txt')"
                            style="flex: 1"
                          >
                            <template #prefix>
                              <el-icon v-if="field.dataType === '图片型'"><Picture /></el-icon>
                              <el-icon v-else><Document /></el-icon>
                            </template>
                          </el-input>
                          <input
                            type="file"
                            :id="'file-input-' + field.name"
                            :accept="getFileAccept(field.dataType)"
                            style="display: none"
                            @change="(e) => handleFileSelect(e, field.name)"
                          />
                          <el-button 
                            type="primary" 
                            @click="triggerFileSelect(field.name)"
                          >
                            <el-icon><Upload /></el-icon>
                            选择文件
                          </el-button>
                        </div>
                        <div class="file-status" v-if="getSelectedFile(field.name)">
                          <el-tag type="success" closable @close="removeSelectedFile(field.name)">
                            <el-icon><Document /></el-icon>
                            {{ getSelectedFile(field.name).name }} ({{ formatFileSize(getSelectedFile(field.name).size) }})
                          </el-tag>
                        </div>
                        <div class="file-hint" v-else>
                          <span class="hint-text">请先输入文件名，再选择对应的本地文件</span>
                        </div>
                      </template>
                      <template v-else-if="field.type === 'date'">
                        <el-date-picker
                          v-model="singleFormData[field.name]"
                          type="date"
                          :placeholder="'请选择' + field.label"
                          style="width: 100%"
                        />
                      </template>
                      <template v-else-if="field.type === 'textarea'">
                        <el-input
                          v-model="singleFormData[field.name]"
                          type="textarea"
                          :rows="3"
                          :placeholder="'请输入' + field.label"
                        />
                      </template>
                      <template v-else-if="field.type === 'number'">
                        <el-input-number
                          v-model="singleFormData[field.name]"
                          :placeholder="'请输入' + field.label"
                          style="width: 100%"
                        />
                      </template>
                      <template v-else>
                        <el-input
                          v-model="singleFormData[field.name]"
                          :placeholder="'请输入' + field.label"
                        />
                      </template>
                    </el-form-item>
                  </template>
                </div>
              </div>

              <!-- 操作字段区域 -->
              <div class="field-area" v-if="processedFieldGroups.operation.length > 0">
                <div class="area-header">
                  <span class="area-title">操作</span>
                  <span class="area-count">{{ processedFieldGroups.operation.length }} 个字段</span>
                </div>
                <div class="form-grid">
                  <template v-for="field in processedFieldGroups.operation" :key="field.name">
                    <!-- 枚举型字段 - 下拉框 -->
                    <el-form-item 
                      v-if="field.isEnum"
                      :label="field.enumName"
                      :prop="field.name"
                      :required="field.required"
                      class="enum-field"
                    >
                      <template #label>
                        <span class="field-label-with-type">
                          <span class="required-star" v-if="field.required">*</span>
                          <span>{{ field.enumName }}</span>
                          <el-tag size="small" :type="getDataTypeTagType('枚举型')">枚举型</el-tag>
                        </span>
                      </template>
                      <el-select v-model="singleFormData[field.name]" :placeholder="'请选择' + field.enumName" style="width: 100%">
                        <el-option 
                          v-for="opt in field.options" 
                          :key="typeof opt === 'object' ? opt.value : opt" 
                          :label="typeof opt === 'object' ? opt.label : opt" 
                          :value="typeof opt === 'object' ? opt.value : opt" 
                        />
                      </el-select>
                    </el-form-item>
                    <!-- 普通字段 -->
                    <el-form-item 
                      v-else
                      :prop="field.name"
                      :required="field.required"
                    >
                      <template #label>
                        <span class="field-label-with-type">
                          <span class="required-star" v-if="field.required">*</span>
                          <span>{{ field.label }}</span>
                          <el-tag size="small" :type="getDataTypeTagType(field.dataType)">{{ field.dataType }}</el-tag>
                        </span>
                      </template>
                      <!-- 文件型/图片型字段 -->
                      <template v-if="isFileType(field.dataType)">
                        <div class="file-upload-field">
                          <el-input
                            v-model="singleFormData[field.name]"
                            :placeholder="'请输入文件名，如: example' + (field.dataType === '图片型' ? '.png' : '.txt')"
                            style="flex: 1"
                          >
                            <template #prefix>
                              <el-icon v-if="field.dataType === '图片型'"><Picture /></el-icon>
                              <el-icon v-else><Document /></el-icon>
                            </template>
                          </el-input>
                          <input
                            type="file"
                            :id="'file-input-' + field.name"
                            :accept="getFileAccept(field.dataType)"
                            style="display: none"
                            @change="(e) => handleFileSelect(e, field.name)"
                          />
                          <el-button 
                            type="primary" 
                            @click="triggerFileSelect(field.name)"
                          >
                            <el-icon><Upload /></el-icon>
                            选择文件
                          </el-button>
                        </div>
                        <div class="file-status" v-if="getSelectedFile(field.name)">
                          <el-tag type="success" closable @close="removeSelectedFile(field.name)">
                            <el-icon><Document /></el-icon>
                            {{ getSelectedFile(field.name).name }} ({{ formatFileSize(getSelectedFile(field.name).size) }})
                          </el-tag>
                        </div>
                        <div class="file-hint" v-else>
                          <span class="hint-text">请先输入文件名，再选择对应的本地文件</span>
                        </div>
                      </template>
                      <template v-else-if="field.type === 'date'">
                        <el-date-picker
                          v-model="singleFormData[field.name]"
                          type="date"
                          :placeholder="'请选择' + field.label"
                          style="width: 100%"
                        />
                      </template>
                      <template v-else-if="field.type === 'textarea'">
                        <el-input
                          v-model="singleFormData[field.name]"
                          type="textarea"
                          :rows="3"
                          :placeholder="'请输入' + field.label"
                        />
                      </template>
                      <template v-else-if="field.type === 'number'">
                        <el-input-number
                          v-model="singleFormData[field.name]"
                          :placeholder="'请输入' + field.label"
                          style="width: 100%"
                        />
                      </template>
                      <template v-else>
                        <el-input
                          v-model="singleFormData[field.name]"
                          :placeholder="'请输入' + field.label"
                        />
                      </template>
                    </el-form-item>
                  </template>
                </div>
              </div>

              <!-- 结果字段区域 -->
              <div class="field-area" v-if="processedFieldGroups.result.length > 0">
                <div class="area-header">
                  <span class="area-title">结果</span>
                  <span class="area-count">{{ processedFieldGroups.result.length }} 个字段</span>
                </div>
                <div class="form-grid">
                  <template v-for="field in processedFieldGroups.result" :key="field.name">
                    <!-- 枚举型字段 - 下拉框 -->
                    <el-form-item 
                      v-if="field.isEnum"
                      :label="field.enumName"
                      :prop="field.name"
                      :required="field.required"
                      class="enum-field"
                    >
                      <template #label>
                        <span class="field-label-with-type">
                          <span class="required-star" v-if="field.required">*</span>
                          <span>{{ field.enumName }}</span>
                          <el-tag size="small" :type="getDataTypeTagType('枚举型')">枚举型</el-tag>
                        </span>
                      </template>
                      <el-select v-model="singleFormData[field.name]" :placeholder="'请选择' + field.enumName" style="width: 100%">
                        <el-option 
                          v-for="opt in field.options" 
                          :key="typeof opt === 'object' ? opt.value : opt" 
                          :label="typeof opt === 'object' ? opt.label : opt" 
                          :value="typeof opt === 'object' ? opt.value : opt" 
                        />
                      </el-select>
                    </el-form-item>
                    <!-- 普通字段 -->
                    <el-form-item 
                      v-else
                      :prop="field.name"
                      :required="field.required"
                    >
                      <template #label>
                        <span class="field-label-with-type">
                          <span class="required-star" v-if="field.required">*</span>
                          <span>{{ field.label }}</span>
                          <el-tag size="small" :type="getDataTypeTagType(field.dataType)">{{ field.dataType }}</el-tag>
                        </span>
                      </template>
                      <!-- 文件型/图片型字段 -->
                      <template v-if="isFileType(field.dataType)">
                        <div class="file-upload-field">
                          <el-input
                            v-model="singleFormData[field.name]"
                            :placeholder="'请输入文件名，如: example' + (field.dataType === '图片型' ? '.png' : '.txt')"
                            style="flex: 1"
                          >
                            <template #prefix>
                              <el-icon v-if="field.dataType === '图片型'"><Picture /></el-icon>
                              <el-icon v-else><Document /></el-icon>
                            </template>
                          </el-input>
                          <input
                            type="file"
                            :id="'file-input-' + field.name"
                            :accept="getFileAccept(field.dataType)"
                            style="display: none"
                            @change="(e) => handleFileSelect(e, field.name)"
                          />
                          <el-button 
                            type="primary" 
                            @click="triggerFileSelect(field.name)"
                          >
                            <el-icon><Upload /></el-icon>
                            选择文件
                          </el-button>
                        </div>
                        <div class="file-status" v-if="getSelectedFile(field.name)">
                          <el-tag type="success" closable @close="removeSelectedFile(field.name)">
                            <el-icon><Document /></el-icon>
                            {{ getSelectedFile(field.name).name }} ({{ formatFileSize(getSelectedFile(field.name).size) }})
                          </el-tag>
                        </div>
                        <div class="file-hint" v-else>
                          <span class="hint-text">请先输入文件名，再选择对应的本地文件</span>
                        </div>
                      </template>
                      <template v-else-if="field.type === 'date'">
                        <el-date-picker
                          v-model="singleFormData[field.name]"
                          type="date"
                          :placeholder="'请选择' + field.label"
                          style="width: 100%"
                        />
                      </template>
                      <template v-else-if="field.type === 'textarea'">
                        <el-input
                          v-model="singleFormData[field.name]"
                          type="textarea"
                          :rows="3"
                          :placeholder="'请输入' + field.label"
                        />
                      </template>
                      <template v-else-if="field.type === 'number'">
                        <el-input-number
                          v-model="singleFormData[field.name]"
                          :placeholder="'请输入' + field.label"
                          style="width: 100%"
                        />
                      </template>
                      <template v-else>
                        <el-input
                          v-model="singleFormData[field.name]"
                          :placeholder="'请输入' + field.label"
                        />
                      </template>
                    </el-form-item>
                  </template>
                </div>
              </div>
            </el-form>
          </div>
          
          <div class="step-actions">
            <el-button size="large" @click="goToStep(1)">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button size="large" @click="resetSingleForm">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
            <el-button type="primary" size="large" @click="saveDraft">
              <el-icon><DocumentAdd /></el-icon>
              保存草稿
            </el-button>
            <el-button type="success" size="large" @click="submitSingleEntry">
              <el-icon><CircleCheck /></el-icon>
              提交数据
            </el-button>
          </div>
        </div>

        <!-- 空状态 -->
        <div class="empty-state animate-slide-up" v-if="!currentCategory">
          <div class="empty-content">
            <div class="empty-icon">
              <el-icon :size="80"><FolderOpened /></el-icon>
            </div>
            <h3>请选择分类目录</h3>
            <p>从左侧选择一个模版分类，开始上传数据</p>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Folder, Document, Check, UploadFilled, 
  Delete, Download, FolderOpened, Files, EditPen,
  ArrowRight, ArrowLeft, CircleCheck, Collection,
  Operation, Calendar, Search, DocumentChecked,
  Refresh, DocumentAdd, Upload, Picture, QuestionFilled
} from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'
import axios from 'axios'
import { getCategoryTree, defaultExpandedKeys as defaultKeys, getNumericCategoryId } from '@/utils/templateCategories'
import * as XLSX from 'xlsx'

const router = useRouter()

// 文件上传相关
const uploadedFilesMap = ref({}) // 存储字段名到文件的映射 { fieldName: File }
const fileInputRefs = ref({}) // 存储每个文件字段的input引用

// 批量上传相关
const batchExcelFile = ref(null) // 存储选择的Excel文件
const batchAttachmentFiles = ref([]) // 存储选择的附件文件列表
const batchUploading = ref(false) // 批量上传中状态
const excelFilePathPrefixes = ref({}) // 存储从Excel中解析出的文件路径前缀 { 纯文件名: 前缀路径 }
const attachmentUploadMode = ref('folder') // 附件上传模式: 'folder' | 'files'
const folderInputRef = ref(null) // 文件夹选择input引用
const excelFullFilePaths = ref([]) // 存储Excel中所有的完整文件路径
const commonFilePathPrefix = ref('') // 存储通用的文件路径前缀（大多数文件共用的前缀）

// 状态
const loadingTemplates = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const uploadStatusText = ref('')
const currentCategory = ref(null)
const selectedTemplate = ref(null)
const availableTemplates = ref([])
const categoryDetailedTemplates = ref([]) // 存储分类下的详细模版信息（包含字段）
const fileList = ref([])
const uploadedFiles = ref([])
const downloadingTemplate = ref(false)

// 步骤控制
const currentStep = ref(0)
const uploadMode = ref('') // 'batch' or 'single'
const templateSearch = ref('')

// 单条录入表单
const singleFormRef = ref(null)
const singleFormData = reactive({})
const singleFormRules = reactive({})

// 模版字段（根据模版动态生成）
const templateFields = ref([
  { name: 'name', label: '名称', type: 'text', required: true },
  { name: 'code', label: '编码', type: 'text', required: true },
  { name: 'description', label: '描述', type: 'textarea', required: false },
  { name: 'category', label: '分类', type: 'select', required: true, options: [
    { label: '类型A', value: 'typeA' },
    { label: '类型B', value: 'typeB' },
    { label: '类型C', value: 'typeC' }
  ]},
  { name: 'date', label: '日期', type: 'date', required: false },
  { name: 'amount', label: '数量', type: 'number', required: false }
])

// 目录结构
const categoryTree = ref(getCategoryTree())
const defaultExpandedKeys = ref([...defaultKeys])

// 过滤模版
const filteredTemplates = computed(() => {
  if (!templateSearch.value) return availableTemplates.value
  const search = templateSearch.value.toLowerCase()
  return availableTemplates.value.filter(tpl => 
    tpl.name.toLowerCase().includes(search) || 
    (tpl.description && tpl.description.toLowerCase().includes(search))
  )
})

// 处理字段分组 - 按区域(对象/操作/结果)分组，并将枚举型字段按枚举名分组
const processedFieldGroups = computed(() => {
  const result = { object: [], operation: [], result: [] }
  
  if (!templateFields.value || templateFields.value.length === 0) {
    return result
  }
  
  // 区域映射：1=对象, 2=操作, 3=结果
  const areaMap = { 1: 'object', 2: 'operation', 3: 'result' }
  
  // 临时存储枚举分组
  const enumGroups = { object: {}, operation: {}, result: {} }
  
  templateFields.value.forEach(field => {
    const areaKey = areaMap[field.fieldCategory] || 'object'
    const dataType = field.dataType || ''
    const dataTypeName = getDataTypeName(dataType)
    const isEnum = dataTypeName === '枚举型' || (typeof dataTypeName === 'string' && dataTypeName.includes('枚举'))
    
    if (isEnum && field.name && field.name.includes(':')) {
      // 枚举型字段：解析 "枚举名:选项" 格式
      const colonIndex = field.name.indexOf(':')
      const enumName = field.name.substring(0, colonIndex)
      const optionValue = field.name.substring(colonIndex + 1)
      
      if (!enumGroups[areaKey][enumName]) {
        enumGroups[areaKey][enumName] = {
          isEnum: true,
          enumName: enumName,
          name: enumName, // 表单绑定用的字段名
          options: [],
          required: field.required,
          fieldCategory: field.fieldCategory
        }
      }
      // 为枚举选项添加A、B、C、D等前缀（显示用），但存储值还是原值
      const optionIndex = enumGroups[areaKey][enumName].options.length
      const prefix = String.fromCharCode(65 + optionIndex) // A=65, B=66, C=67...
      enumGroups[areaKey][enumName].options.push({
        label: prefix + ' ' + optionValue, // 显示：A 选项值（带空格）
        value: optionValue // 存储：选项值（不带前缀）
      })
    } else {
      // 普通字段
      result[areaKey].push({
        isEnum: false,
        name: field.name,
        label: field.label,
        type: field.type,
        dataType: dataTypeName,
        required: field.required,
        fieldCategory: field.fieldCategory
      })
    }
  })
  
  // 将枚举分组添加到结果中
  Object.keys(enumGroups).forEach(areaKey => {
    Object.keys(enumGroups[areaKey]).forEach(enumName => {
      result[areaKey].push(enumGroups[areaKey][enumName])
    })
  })
  
  return result
})

// 获取数据类型名称 - 支持中文类型名
const getDataTypeName = (dataType) => {
  // 如果已经是中文类型名，直接返回
  if (typeof dataType === 'string') {
    return dataType
  }
  // 兼容旧的数字类型
  const typeMap = {
    0: '字符串型',
    1: '数值型',
    2: '浮点型',
    3: '日期型',
    4: '枚举型',
    5: '枚举型'
  }
  return typeMap[dataType] !== undefined ? typeMap[dataType] : `类型${dataType}`
}

// 获取数据类型对应的标签类型
const getDataTypeTagType = (dataType) => {
  const typeMap = {
    '字符串型': 'info',
    '字符串': 'info',
    '数值型': 'success',
    '数字': 'success',
    '浮点型': 'warning',
    '范围型': 'primary',
    '枚举型': 'danger',
    '图片型': '',
    '文件型': 'info',
    '数组型': 'primary',
    '表格型': 'success',
    '日期型': 'warning',
    '日期': 'warning',
    '文本': 'info'
  }
  return typeMap[dataType] || 'info'
}

// 判断是否是文件类型字段
const isFileType = (dataType) => {
  return dataType === '文件型' || dataType === '图片型'
}

// 触发文件选择
const triggerFileSelect = (fieldName) => {
  const input = document.getElementById(`file-input-${fieldName}`)
  if (input) {
    input.click()
  }
}

// 处理文件选择
const handleFileSelect = (event, fieldName) => {
  const file = event.target.files[0]
  if (file) {
    // 检查文件名是否与输入的文件名匹配
    const expectedFileName = singleFormData[fieldName]
    if (expectedFileName && file.name !== expectedFileName) {
      ElMessage.warning(`选择的文件名"${file.name}"与输入的文件名"${expectedFileName}"不一致，将使用选择的文件名`)
      singleFormData[fieldName] = file.name
    } else if (!expectedFileName) {
      // 如果没有输入文件名，使用选择的文件名
      singleFormData[fieldName] = file.name
    }
    // 存储文件
    uploadedFilesMap.value[fieldName] = file
    ElMessage.success(`文件 ${file.name} 已选择`)
  }
}

// 移除已选文件
const removeSelectedFile = (fieldName) => {
  delete uploadedFilesMap.value[fieldName]
  singleFormData[fieldName] = ''
  // 清空input
  const input = document.getElementById(`file-input-${fieldName}`)
  if (input) {
    input.value = ''
  }
}

// 获取已选文件信息
const getSelectedFile = (fieldName) => {
  return uploadedFilesMap.value[fieldName]
}

// 获取文件类型接受的格式
const getFileAccept = (dataType) => {
  if (dataType === '图片型') {
    return 'image/*'
  }
  return '*/*'
}

// 检查当前模板是否包含文件型/图片型字段
const hasFileTypeFields = computed(() => {
  if (!templateFields.value || templateFields.value.length === 0) {
    return false
  }
  return templateFields.value.some(field => {
    const dataType = field.dataType || ''
    return dataType === '文件型' || dataType === '图片型'
  })
})

// 处理批量上传Excel文件选择
const handleBatchExcelChange = async (file) => {
  batchExcelFile.value = file.raw
  
  // 解析Excel文件，提取文件/图片路径前缀
  try {
    await parseExcelFilePathPrefixes(file.raw)
  } catch (error) {
    console.error('解析Excel文件路径前缀失败:', error)
  }
  
  return false // 阻止自动上传
}

// 解析Excel文件，提取文件型/图片型字段的路径前缀
const parseExcelFilePathPrefixes = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })
        
        if (jsonData.length < 2) {
          resolve()
          return
        }
        
        const headers = jsonData[0] // 第一行是表头
        const prefixMap = {}
        
        // 获取文件型/图片型字段的列索引
        const fileTypeFieldIndices = []
        if (templateFields.value && templateFields.value.length > 0) {
          templateFields.value.forEach((field, idx) => {
            const dataType = field.dataType || ''
            if (dataType === '文件型' || dataType === '图片型') {
              // 在表头中查找对应的列
              const headerIdx = headers.findIndex(h => h === field.name || h === field.label)
              if (headerIdx !== -1) {
                fileTypeFieldIndices.push(headerIdx)
              }
            }
          })
        }
        
        // 如果没有找到文件型字段，尝试检测所有可能包含文件路径的列
        if (fileTypeFieldIndices.length === 0) {
          headers.forEach((header, idx) => {
            if (header && (header.includes('文件') || header.includes('图片') || header.includes('附件') || header.includes('路径'))) {
              fileTypeFieldIndices.push(idx)
            }
          })
        }
        
        // 如果还是没有，则检查所有列
        const columnsToCheck = fileTypeFieldIndices.length > 0 ? fileTypeFieldIndices : headers.map((_, idx) => idx)
        
        // 遍历数据行，提取文件路径前缀
        const allPrefixes = [] // 收集所有发现的前缀
        const allFullPaths = [] // 收集所有完整路径
        for (let rowIdx = 1; rowIdx < jsonData.length; rowIdx++) {
          const row = jsonData[rowIdx]
          columnsToCheck.forEach(colIdx => {
            const cellValue = row[colIdx]
            if (cellValue && typeof cellValue === 'string') {
              // 检查是否是文件路径格式（包含斜杠或反斜杠）
              const pathMatch = cellValue.match(/^(.+[\\\/])([^\\\/]+)$/)
              if (pathMatch) {
                const prefix = pathMatch[1] // 前缀路径，如 "源数据\\"
                const fileName = pathMatch[2] // 纯文件名，如 "b73b62f0498e0dbdf86d7fbd302662a1.jpg"
                prefixMap[fileName] = prefix
                allPrefixes.push(prefix)
                allFullPaths.push(cellValue) // 存储完整路径
                console.log(`解析到文件路径: ${cellValue}, 前缀: ${prefix}, 文件名: ${fileName}`)
              }
            }
          })
        }
        
        excelFilePathPrefixes.value = prefixMap
        excelFullFilePaths.value = allFullPaths
        
        // 计算最常见的前缀作为通用前缀
        if (allPrefixes.length > 0) {
          const prefixCount = {}
          allPrefixes.forEach(p => {
            prefixCount[p] = (prefixCount[p] || 0) + 1
          })
          // 找出出现次数最多的前缀
          let maxCount = 0
          let mostCommonPrefix = ''
          Object.entries(prefixCount).forEach(([prefix, count]) => {
            if (count > maxCount) {
              maxCount = count
              mostCommonPrefix = prefix
            }
          })
          commonFilePathPrefix.value = mostCommonPrefix
          console.log('最常见的文件路径前缀:', mostCommonPrefix, '出现次数:', maxCount)
        }
        
        console.log('Excel文件路径前缀映射:', prefixMap)
        
        if (Object.keys(prefixMap).length > 0) {
          ElMessage.success(`已解析Excel中的${Object.keys(prefixMap).length}个文件路径前缀`)
        }
        
        resolve()
      } catch (error) {
        console.error('解析Excel失败:', error)
        reject(error)
      }
    }
    
    reader.onerror = (error) => {
      reject(error)
    }
    
    reader.readAsArrayBuffer(file)
  })
}

// 移除批量上传的Excel文件
const removeBatchExcel = () => {
  batchExcelFile.value = null
  excelFilePathPrefixes.value = {} // 清空文件路径前缀映射
  excelFullFilePaths.value = [] // 清空完整路径列表
  commonFilePathPrefix.value = '' // 清空通用前缀
}

// 处理批量上传附件文件选择
const handleBatchAttachmentChange = (file, fileList) => {
  batchAttachmentFiles.value = fileList.map(f => f.raw || f)
  return false // 阻止自动上传
}

// 移除批量上传的附件文件
const removeBatchAttachment = (file) => {
  const index = batchAttachmentFiles.value.findIndex(f => 
    (f.name || f.raw?.name) === (file.name || file.raw?.name)
  )
  if (index > -1) {
    batchAttachmentFiles.value.splice(index, 1)
  }
}

// 触发文件夹选择
const triggerFolderSelect = () => {
  folderInputRef.value?.click()
}

// 处理文件夹选择
const handleFolderSelect = (event) => {
  const files = Array.from(event.target.files || [])
  processFolderFiles(files)
}

// 处理文件夹拖放
const handleFolderDrop = async (event) => {
  const items = event.dataTransfer?.items
  if (!items) return
  
  const files = []
  
  // 递归读取文件夹内容
  const readEntry = async (entry, path = '') => {
    if (entry.isFile) {
      return new Promise((resolve) => {
        entry.file((file) => {
          // 保存相对路径信息
          file.relativePath = path + file.name
          files.push(file)
          resolve()
        })
      })
    } else if (entry.isDirectory) {
      const reader = entry.createReader()
      return new Promise((resolve) => {
        reader.readEntries(async (entries) => {
          for (const subEntry of entries) {
            await readEntry(subEntry, path + entry.name + '/')
          }
          resolve()
        })
      })
    }
  }
  
  // 处理拖放的项目
  for (const item of items) {
    const entry = item.webkitGetAsEntry?.()
    if (entry) {
      await readEntry(entry)
    }
  }
  
  if (files.length > 0) {
    processFolderFiles(files)
  }
}

// 处理文件夹中的文件
const processFolderFiles = (files) => {
  if (!files || files.length === 0) {
    ElMessage.warning('未选择任何文件')
    return
  }
  
  console.log('文件夹中的文件列表:')
  files.forEach(file => {
    // webkitRelativePath 包含相对于选择的文件夹的路径
    const relativePath = file.webkitRelativePath || file.relativePath || file.name
    console.log(`  ${relativePath}`)
  })
  
  // 如果已解析Excel路径，尝试自动匹配
  if (excelFullFilePaths.value.length > 0) {
    const matchedFiles = []
    const unmatchedExcelPaths = [...excelFullFilePaths.value]
    
    files.forEach(file => {
      const relativePath = file.webkitRelativePath || file.relativePath || file.name
      const fileName = file.name
      
      // 尝试匹配Excel中的路径
      let matched = false
      for (let i = 0; i < unmatchedExcelPaths.length; i++) {
        const excelPath = unmatchedExcelPaths[i]
        // 获取Excel路径中的纯文件名
        const excelFileName = excelPath.split(/[\\\/]/).pop()
        
        // 匹配条件：文件名相同，或相对路径包含Excel路径
        if (fileName === excelFileName || 
            relativePath.endsWith(excelPath.replace(/\\/g, '/')) ||
            relativePath.includes(excelFileName)) {
          matchedFiles.push({
            file: file,
            excelPath: excelPath,
            relativePath: relativePath
          })
          unmatchedExcelPaths.splice(i, 1)
          matched = true
          console.log(`匹配成功: ${fileName} -> ${excelPath}`)
          break
        }
      }
      
      if (!matched) {
        // 即使没有匹配到Excel路径，也保留文件（可能Excel中没有记录所有文件）
        matchedFiles.push({
          file: file,
          excelPath: null,
          relativePath: relativePath
        })
      }
    })
    
    // 更新附件文件列表
    batchAttachmentFiles.value = matchedFiles.map(m => {
      const file = m.file
      // 如果匹配到了Excel路径，使用Excel路径作为文件名
      if (m.excelPath) {
        // 创建新的File对象，使用Excel中的完整路径作为文件名
        return new File([file], m.excelPath, { type: file.type })
      }
      return file
    })
    
    const matchedCount = matchedFiles.filter(m => m.excelPath).length
    ElMessage.success(`已从文件夹中选择 ${files.length} 个文件，其中 ${matchedCount} 个匹配到Excel路径`)
  } else {
    // 没有Excel路径信息，直接使用文件
    batchAttachmentFiles.value = files
    ElMessage.success(`已从文件夹中选择 ${files.length} 个文件`)
  }
}

// 上传配置 - 调用批量上传接口
const uploadUrl = '/templateData/addTemplateDataBatch'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))
const uploadData = computed(() => ({
  templateId: selectedTemplate.value?.id
}))

// 步骤控制
const goToStep = (step) => {
  currentStep.value = step
}

// 目录点击
const handleCategoryClick = (data) => {
  currentCategory.value = data
  selectedTemplate.value = null
  currentStep.value = 0
  uploadMode.value = ''
  availableTemplates.value = []
  categoryDetailedTemplates.value = []
  loadTemplates()
}

// 加载模版 - 使用与模板库相同的逻辑
const loadTemplates = async () => {
  if (!currentCategory.value?.id) return
  
  const numericId = getNumericCategoryId(currentCategory.value.id)
  if (!numericId) {
    availableTemplates.value = []
    return
  }
  
  loadingTemplates.value = true
  try {
    // 先获取分类下的模版列表
    const response = await request.get(`/template/getTemplateByCategory/${numericId}`)
    console.log('模版列表响应:', response)
    if (response.data?.code === 1 || response.data?.code === 0) {
      // 只显示审核通过的模板 (state === 1)
      const allTemplates = response.data.data || []
      availableTemplates.value = allTemplates.filter(tpl => tpl.state === 1)
      console.log('过滤后的已审核模板:', availableTemplates.value)
    } else {
      availableTemplates.value = []
    }
    
    // 同时获取详细模版信息（包含字段）
    const detailResponse = await request.get(`/template/getDetailedTemplateByCategory/${numericId}`)
    console.log('详细模版响应:', detailResponse)
    if (detailResponse.data?.code === 1 || detailResponse.data?.code === 0) {
      // 只保留审核通过的模板的详细信息
      const allDetailedTemplates = detailResponse.data.data || []
      const approvedTemplateIds = availableTemplates.value.map(t => t.id)
      categoryDetailedTemplates.value = allDetailedTemplates.filter(t => 
        approvedTemplateIds.includes(t.templateId)
      )
    } else {
      categoryDetailedTemplates.value = []
    }
  } catch (error) {
    console.error('加载模版失败:', error)
    availableTemplates.value = []
    categoryDetailedTemplates.value = []
  } finally {
    loadingTemplates.value = false
  }
}

// 选择模版
const selectTemplate = (tpl) => {
  selectedTemplate.value = tpl
  fileList.value = []
  uploadedFiles.value = []
  // 从已加载的详细模版信息中筛选出当前模版的字段
  loadTemplateFieldsFromCache(tpl.id)
}

// 从缓存的详细模版信息中加载字段
const loadTemplateFieldsFromCache = (templateId) => {
  // 从categoryDetailedTemplates中查找对应模版的字段信息
  // 接口返回结构: { templateId, templateName, templateFields: [...] }
  const detailedTemplate = categoryDetailedTemplates.value.find(t => t.templateId === templateId)
  
  console.log('查找模版ID:', templateId, '详细模版列表:', categoryDetailedTemplates.value)
  console.log('找到的模版:', detailedTemplate)
  
  if (detailedTemplate && detailedTemplate.templateFields && detailedTemplate.templateFields.length > 0) {
    // 将接口返回的字段格式转换为表单需要的格式
    templateFields.value = detailedTemplate.templateFields.map(field => ({
      name: field.fieldName,
      label: field.fieldName, // 接口没有返回label，用fieldName作为显示名
      type: mapDataType(field.dataType),
      dataType: field.dataType, // 保留原始数据类型用于显示
      required: field.required || false,
      options: [],
      fieldCategory: field.fieldCategory // 1=对象, 2=操作, 3=结果
    }))
    console.log('加载模版字段:', templateFields.value)
  } else {
    // 如果没有找到，尝试从接口获取
    loadTemplateFieldsFromApi(templateId)
  }
  
  // 初始化表单数据和规则
  initSingleForm()
}

// 字段类型映射 - 支持中文类型名和数字类型
const mapDataType = (dataType) => {
  // 如果是中文类型名
  if (typeof dataType === 'string') {
    const typeMap = {
      '字符串型': 'text',
      '数值型': 'number',
      '浮点型': 'number',
      '范围型': 'text',
      '枚举型': 'select',
      '图片型': 'file',
      '文件型': 'file',
      '数组型': 'textarea',
      '表格型': 'textarea',
      '日期型': 'date'
    }
    return typeMap[dataType] || 'text'
  }
  // 兼容旧的数字类型
  const numTypeMap = {
    0: 'text',
    1: 'number',
    2: 'text',
    3: 'date',
    4: 'select',
    5: 'textarea'
  }
  return numTypeMap[dataType] || 'text'
}

// 获取数据类型的显示文本
const getDataTypeText = (dataType) => {
  // 如果已经是中文类型名，直接返回
  if (typeof dataType === 'string') {
    return dataType
  }
  // 兼容旧的数字类型
  const typeMap = {
    0: '文本',
    1: '数字',
    2: '文本',
    3: '日期',
    4: '选择',
    5: '长文本'
  }
  return typeMap[dataType] || '文本'
}

// 从API加载模版字段（备用方案）
const loadTemplateFieldsFromApi = async (templateId) => {
  try {
    const numericId = getNumericCategoryId(currentCategory.value?.id)
    if (!numericId) return
    
    const response = await request.get(`/template/getDetailedTemplateByCategory/${numericId}`)
    console.log('备用API响应:', response)
    
    if ((response.data?.code === 1 || response.data?.code === 0) && response.data.data) {
      const detailedTemplate = response.data.data.find(t => t.templateId === templateId)
      if (detailedTemplate && detailedTemplate.templateFields) {
        templateFields.value = detailedTemplate.templateFields.map(field => ({
          name: field.fieldName,
          label: field.fieldName,
          type: mapDataType(field.dataType),
          dataType: field.dataType, // 保留原始数据类型用于显示
          required: field.required || false,
          options: [],
          fieldCategory: field.fieldCategory // 1=对象, 2=操作, 3=结果
        }))
        console.log('从API加载的字段:', templateFields.value)
      }
    }
  } catch (error) {
    console.error('加载模版字段失败:', error)
  }
  initSingleForm()
}

// 初始化单条录入表单 - 根据处理后的字段分组初始化
const initSingleForm = () => {
  // 清空之前的数据
  Object.keys(singleFormData).forEach(key => {
    delete singleFormData[key]
  })
  Object.keys(singleFormRules).forEach(key => {
    delete singleFormRules[key]
  })
  
  // 遍历所有区域的字段
  const allFields = [
    ...processedFieldGroups.value.object,
    ...processedFieldGroups.value.operation,
    ...processedFieldGroups.value.result
  ]
  
  allFields.forEach(field => {
    // 初始化表单数据
    if (field.isEnum) {
      // 枚举字段
      singleFormData[field.name] = ''
      if (field.required) {
        singleFormRules[field.name] = [
          { required: true, message: `请选择${field.enumName}`, trigger: 'change' }
        ]
      }
    } else {
      // 普通字段
      singleFormData[field.name] = field.type === 'number' ? null : ''
      if (field.required) {
        singleFormRules[field.name] = [
          { required: true, message: `请输入${field.label}`, trigger: 'blur' }
        ]
      }
    }
  })
}

// 选择上传方式
const selectUploadMode = (mode) => {
  uploadMode.value = mode
}

// 上传前校验
const beforeUpload = (file) => {
  const isValidType = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                       'application/vnd.ms-excel', 
                       'text/csv'].includes(file.type) ||
                      file.name.endsWith('.xlsx') || 
                      file.name.endsWith('.xls') || 
                      file.name.endsWith('.csv')
  
  if (!isValidType) {
    ElMessage.error('只支持 Excel 或 CSV 格式的文件')
    return false
  }
  
  const isLt50M = file.size / 1024 / 1024 < 50
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  
  uploading.value = true
  uploadProgress.value = 0
  uploadStatusText.value = '正在上传...'
  return true
}

// 上传进度
const handleUploadProgress = (event) => {
  uploadProgress.value = Math.round(event.percent)
  uploadStatusText.value = `正在上传... ${uploadProgress.value}%`
}

// 上传成功
const handleUploadSuccess = (response, file) => {
  uploading.value = false
  uploadProgress.value = 100
  uploadStatus.value = 'success'
  uploadStatusText.value = '上传成功'
  
  uploadedFiles.value.push({
    id: response.data?.id || Date.now(),
    name: file.name,
    size: file.size,
    status: 'success'
  })
  
  ElMessage.success(`${file.name} 上传成功`)
}

// 上传失败
const handleUploadError = (error, file) => {
  uploading.value = false
  uploadStatus.value = 'exception'
  uploadStatusText.value = '上传失败'
  
  uploadedFiles.value.push({
    id: Date.now(),
    name: file.name,
    size: file.size,
    status: 'error'
  })
  
  ElMessage.error(`${file.name} 上传失败`)
}

// 移除文件
const removeFile = (file) => {
  uploadedFiles.value = uploadedFiles.value.filter(f => f.id !== file.id)
}

// 下载模版 - 使用指定接口
const downloadTemplate = async () => {
  if (!selectedTemplate.value) return
  
  downloadingTemplate.value = true
  try {
    // 使用指定的模版下载接口（通过代理）
    const response = await fetch(`/template/getTemplateExcel/${selectedTemplate.value.id}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error('下载失败')
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${selectedTemplate.value.name}_模版.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('模版下载成功')
  } catch (error) {
    console.error('下载模版失败:', error)
    ElMessage.error('下载模版失败，请稍后重试')
  } finally {
    downloadingTemplate.value = false
  }
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / 1024 / 1024).toFixed(1) + ' MB'
}

// 完成批量上传
const submitBatchUpload = async () => {
  if (!batchExcelFile.value) {
    ElMessage.warning('请先选择Excel文件')
    return
  }
  
  // 如果模板包含文件型字段，检查是否上传了附件
  if (hasFileTypeFields.value && batchAttachmentFiles.value.length === 0) {
    try {
      await ElMessageBox.confirm(
        '当前模板包含文件型/图片型字段，但您未上传任何附件文件。确定继续提交吗？',
        '提示',
        { type: 'warning', confirmButtonText: '继续提交', cancelButtonText: '返回上传' }
      )
    } catch {
      return
    }
  }
  
  batchUploading.value = true
  uploadProgress.value = 0
  uploadStatusText.value = '正在上传...'
  
  try {
    const formData = new FormData()
    
    // 添加模板ID
    formData.append('templateId', selectedTemplate.value.id)
    
    // 添加Excel文件
    formData.append('excel', batchExcelFile.value)
    
    // 添加附件文件（为文件名添加Excel中解析出的前缀路径）
    batchAttachmentFiles.value.forEach(file => {
      const originalFileName = file.name
      
      // 如果是文件夹上传模式，文件名可能已经是完整路径（在processFolderFiles中处理过）
      // 检查文件名是否已经包含路径分隔符
      const hasPathSeparator = originalFileName.includes('\\') || originalFileName.includes('/')
      
      if (hasPathSeparator) {
        // 文件名已经包含路径，直接使用
        formData.append('files', file)
        console.log(`文件名已包含路径: ${originalFileName}`)
      } else {
        // 普通文件上传模式，需要匹配Excel路径
        
        // 策略1: 优先精确匹配 - 上传的文件名正好等于Excel中解析出的纯文件名
        let matchedFullPath = null
        if (excelFilePathPrefixes.value[originalFileName]) {
          matchedFullPath = excelFilePathPrefixes.value[originalFileName] + originalFileName
        }
        
        // 策略2: 模糊匹配 - 查找Excel完整路径中以上传文件名结尾的路径
        if (!matchedFullPath) {
          matchedFullPath = excelFullFilePaths.value.find(fullPath => {
            // 检查完整路径是否以上传的文件名结尾
            return fullPath.endsWith(originalFileName) || 
                   fullPath.endsWith('\\' + originalFileName) || 
                   fullPath.endsWith('/' + originalFileName)
          })
        }
        
        // 策略3: 更宽松的匹配 - 检查上传文件名是否包含Excel中某个纯文件名
        if (!matchedFullPath) {
          for (const [pureFileName, prefix] of Object.entries(excelFilePathPrefixes.value)) {
            // 如果上传的文件名包含Excel中的纯文件名（去掉可能的前缀）
            if (originalFileName.includes(pureFileName) || pureFileName.includes(originalFileName)) {
              // 使用Excel中的完整路径
              matchedFullPath = prefix + pureFileName
              console.log(`模糊匹配: ${originalFileName} 匹配到 ${matchedFullPath}`)
              break
            }
          }
        }
        
        if (matchedFullPath) {
          // 使用匹配到的Excel完整路径作为新文件名
          const renamedFile = new File([file], matchedFullPath, { type: file.type })
          formData.append('files', renamedFile)
          console.log(`文件名匹配: ${originalFileName} -> ${matchedFullPath}`)
        } else if (commonFilePathPrefix.value) {
          // 如果没有匹配到，但有通用前缀，则添加通用前缀
          const newFileName = commonFilePathPrefix.value + originalFileName
          const renamedFile = new File([file], newFileName, { type: file.type })
          formData.append('files', renamedFile)
          console.log(`文件名添加通用前缀: ${originalFileName} -> ${newFileName}`)
        } else {
          // 没有找到任何前缀，使用原文件名
          formData.append('files', file)
          console.log(`文件名无前缀: ${originalFileName}`)
        }
      }
    })
    
    console.log('批量上传FormData内容:')
    console.log('templateId:', selectedTemplate.value.id)
    console.log('excel:', batchExcelFile.value.name)
    console.log('files:', batchAttachmentFiles.value.map(f => f.name))
    console.log('文件路径前缀映射:', excelFilePathPrefixes.value)
    console.log('Excel完整路径列表:', excelFullFilePaths.value)
    console.log('通用前缀:', commonFilePathPrefix.value)
    
    const response = await axios.post('/templateData/addTemplateDataBatch', formData, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        uploadProgress.value = percent
        uploadStatusText.value = `正在上传... ${percent}%`
      }
    })
    
    if (response.data?.code === 0 || response.data?.code === 1 || response.status === 200) {
      uploadProgress.value = 100
      uploadStatus.value = 'success'
      uploadStatusText.value = '上传成功'
      ElMessage.success('批量数据上传成功！')
      
      // 重置状态
      setTimeout(() => {
        currentStep.value = 0
        uploadMode.value = ''
        batchExcelFile.value = null
        batchAttachmentFiles.value = []
        selectedTemplate.value = null
        batchUploading.value = false
      }, 1000)
    } else {
      throw new Error(response.data?.message || '上传失败')
    }
  } catch (error) {
    console.error('批量上传失败:', error)
    uploadStatus.value = 'exception'
    uploadStatusText.value = '上传失败'
    ElMessage.error(error.message || '批量上传失败，请稍后重试')
    batchUploading.value = false
  }
}

// 重置单条表单
const resetSingleForm = () => {
  if (singleFormRef.value) {
    singleFormRef.value.resetFields()
  }
  templateFields.value.forEach(field => {
    singleFormData[field.name] = field.type === 'number' ? null : ''
  })
  // 清空上传的文件
  uploadedFilesMap.value = {}
  // 清空文件input
  const allFields = [
    ...processedFieldGroups.value.object,
    ...processedFieldGroups.value.operation,
    ...processedFieldGroups.value.result
  ]
  allFields.forEach(field => {
    if (isFileType(field.dataType)) {
      const input = document.getElementById(`file-input-${field.name}`)
      if (input) {
        input.value = ''
      }
    }
  })
}

// 保存草稿
const saveDraft = async () => {
  try {
    // 这里调用保存草稿接口
    ElMessage.success('草稿保存成功')
  } catch (error) {
    ElMessage.error('保存草稿失败')
  }
}

// 提交单条数据
const submitSingleEntry = async () => {
  if (!singleFormRef.value) return
  
  await singleFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 默认表单字段，需要排除（这些是初始化时的默认字段，不是模版定义的）
        const defaultFields = ['name', 'code', 'description', 'category', 'date', 'amount']
        
        // 获取所有字段（包括枚举字段）
        const allFields = [
          ...processedFieldGroups.value.object,
          ...processedFieldGroups.value.operation,
          ...processedFieldGroups.value.result
        ]
        
        // 检查文件型字段是否已上传文件
        const fileFields = allFields.filter(field => isFileType(field.dataType))
        for (const field of fileFields) {
          const fileName = singleFormData[field.name]
          if (fileName && !uploadedFilesMap.value[field.name]) {
            ElMessage.warning(`请为字段"${field.label}"选择对应的文件`)
            return
          }
        }
        
        // 构建模板数据对象数组
        const templateDataDtos = allFields
          .filter(field => {
            // 排除默认字段
            return !defaultFields.includes(field.name)
          })
          .map(field => {
            let fieldValue = singleFormData[field.name]
            let fieldDataType = field.dataType
            
            // 如果是枚举类型字段，需要找到对应的选项，使用带前缀的label
            if (field.isEnum && field.options && field.options.length > 0) {
              // 找到选中的选项
              const selectedOption = field.options.find(opt => {
                const optValue = typeof opt === 'object' ? opt.value : opt
                return optValue === fieldValue
              })
              
              if (selectedOption) {
                // 使用带前缀的label作为提交值
                fieldValue = typeof selectedOption === 'object' ? selectedOption.label : selectedOption
              }
              fieldDataType = '枚举型'
            }
            
            return {
              templateId: selectedTemplate.value.id,
              fieldName: field.name,
              fieldDataType: fieldDataType,
              fieldValue: fieldValue !== null && fieldValue !== undefined 
                ? String(fieldValue) 
                : ''
            }
          })
        
        console.log('模版字段:', templateFields.value)
        console.log('表单数据:', JSON.parse(JSON.stringify(singleFormData)))
        console.log('提交的数据:', templateDataDtos)
        console.log('上传的文件:', uploadedFilesMap.value)
        
        // 检查是否有文件需要上传
        const hasFiles = Object.keys(uploadedFilesMap.value).length > 0
        
        // 始终使用 FormData 格式发送数据（后端期望 multipart/form-data）
        const formData = new FormData()
        
        // 添加 templateData 参数（JSON字符串）
        formData.append('templateData', JSON.stringify(templateDataDtos))
        
        // 如果有文件，添加文件
        if (hasFiles) {
          Object.keys(uploadedFilesMap.value).forEach(fieldName => {
            const file = uploadedFilesMap.value[fieldName]
            if (file) {
              formData.append('files', file)
            }
          })
        }
        
        console.log('FormData 内容:')
        for (let [key, value] of formData.entries()) {
          console.log(key, value)
        }
        
        const response = await axios.post('/templateData/addATemplateData', formData, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
            // 不要手动设置 Content-Type，让浏览器自动设置 multipart/form-data 并生成 boundary
          }
        })
        
        if (response.data?.code === 0 || response.data?.code === 1 || response.status === 200) {
          ElMessage.success('数据提交成功')
          // 清空上传的文件
          uploadedFilesMap.value = {}
          resetSingleForm()
          // 跳转到数据上传页面
          router.push('/tplmanage/upload')
        } else {
          ElMessage.error(response.data?.message || '提交失败')
        }
      } catch (error) {
        console.error('提交数据失败:', error)
        ElMessage.error('提交数据失败，请稍后重试')
      }
    } else {
      ElMessage.warning('请填写完整必填信息')
    }
  })
}

onMounted(() => {
  initSingleForm()
})
</script>

<style lang="scss" scoped>
.tpl-upload {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f1 100%);
}

.page-container {
  display: flex;
  min-height: calc(100vh - 64px);
  padding-top: 64px;
}

// 侧边栏
.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e5e7eb;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.04);
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid #f1f5f9;
  
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

// 步骤指示器
.steps-container {
  background: white;
  border-radius: 16px;
  padding: 24px 32px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

// 区块通用样式
.section-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  
  .el-icon {
    color: #667eea;
  }
}

.section-desc {
  color: #64748b;
  font-size: 0.875rem;
}

// 模版选择
.template-select-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.template-search {
  margin-bottom: 20px;
  max-width: 400px;
}

.template-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.template-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  border: 2px solid #e5e7eb;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  
  &:hover {
    border-color: #667eea;
    background: #f8f9ff;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  }
  
  &.active {
    border-color: #667eea;
    background: linear-gradient(135deg, #667eea08, #764ba208);
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
  }
}

.template-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
  flex-shrink: 0;
}

.template-info {
  flex: 1;
  
  h4 {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 6px;
  }
  
  p {
    font-size: 0.875rem;
    color: #64748b;
    margin: 0 0 10px 0;
    line-height: 1.5;
  }
}

.template-meta {
  display: flex;
  gap: 16px;
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.75rem;
    color: #94a3b8;
  }
}

.template-check {
  position: absolute;
  top: 12px;
  right: 12px;
}

.check-icon {
  color: #667eea;
  font-size: 24px;
}

// 上传方式选择
.upload-mode-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.upload-mode-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.mode-card {
  position: relative;
  padding: 32px;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  
  &:hover {
    border-color: #667eea;
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(102, 126, 234, 0.15);
  }
  
  &.active {
    border-color: #667eea;
    background: linear-gradient(135deg, #667eea05, #764ba205);
    
    .mode-icon {
      transform: scale(1.1);
    }
  }
}

.mode-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  transition: transform 0.3s ease;
  
  &.batch {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
  }
  
  &.single {
    background: linear-gradient(135deg, #11998e, #38ef7d);
    color: white;
  }
}

.mode-content {
  h4 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 8px;
  }
  
  p {
    font-size: 0.875rem;
    color: #64748b;
    margin-bottom: 16px;
    line-height: 1.6;
  }
}

.mode-features {
  list-style: none;
  padding: 0;
  margin: 0;
  
  li {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.875rem;
    color: #475569;
    margin-bottom: 8px;
    
    .el-icon {
      color: #10b981;
      font-size: 16px;
    }
  }
}

.mode-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  color: #667eea;
  font-size: 28px;
}

// 上传区域
.upload-section,
.single-entry-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

// 下载模版卡片
.download-template-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  background: linear-gradient(135deg, #667eea08, #764ba208);
  border: 1px solid #667eea30;
  border-radius: 16px;
  margin-bottom: 24px;
  
  .card-icon {
    width: 64px;
    height: 64px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    flex-shrink: 0;
  }
  
  .card-content {
    flex: 1;
    
    h4 {
      font-size: 1rem;
      font-weight: 600;
      color: #1e293b;
      margin-bottom: 4px;
    }
    
    p {
      font-size: 0.875rem;
      color: #64748b;
      margin: 0;
    }
  }
}

.upload-area-wrapper {
  margin-bottom: 24px;
  
  .upload-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 16px;
  }
}

.upload-area {
  margin-bottom: 20px;
}

.upload-dragger {
  width: 100%;
  
  :deep(.el-upload-dragger) {
    border: 2px dashed #d1d5db;
    border-radius: 16px;
    padding: 48px;
    transition: all 0.3s ease;
    background: #fafbfc;
    
    &:hover {
      border-color: #667eea;
      background: #f8f9ff;
    }
  }
}

.upload-content {
  text-align: center;
}

.upload-icon-wrapper {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea15, #764ba215);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-icon {
  font-size: 40px;
  color: #667eea;
}

.upload-text {
  .main-text {
    font-size: 1.125rem;
    color: #1e293b;
    margin-bottom: 8px;
    
    em {
      color: #667eea;
      font-style: normal;
      font-weight: 600;
    }
  }
  
  .sub-text {
    font-size: 0.875rem;
    color: #94a3b8;
    margin: 0;
  }
}

// 上传进度
.upload-progress {
  margin-bottom: 24px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  
  .progress-text {
    font-size: 0.875rem;
    color: #64748b;
    margin-top: 12px;
    text-align: center;
  }
}

// 已上传文件
.uploaded-files {
  margin-bottom: 24px;
  
  h4 {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 16px;
    
    .el-icon {
      color: #10b981;
    }
  }
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.file-icon {
  color: #667eea;
  font-size: 22px;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  
  .file-name {
    font-size: 0.875rem;
    font-weight: 500;
    color: #1e293b;
  }
  
  .file-size {
    font-size: 0.75rem;
    color: #94a3b8;
  }
}

// 单条录入表单
.form-container {
  background: #fafbfc;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
}

// 字段区域
.field-area {
  margin-bottom: 32px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.area-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.area-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  
  &::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 18px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 2px;
    margin-right: 10px;
    vertical-align: middle;
  }
}

.area-count {
  font-size: 0.75rem;
  color: #94a3b8;
  background: #f1f5f9;
  padding: 4px 10px;
  border-radius: 12px;
}

// 字段标签带类型标记
.field-label-with-type {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  
  .required-star {
    color: #ef4444;
    font-weight: bold;
  }
  
  .el-tag {
    font-size: 0.7rem;
    padding: 0 6px;
    height: 20px;
    line-height: 18px;
  }
}

.single-form {
  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }
  
  :deep(.el-form-item__label) {
    font-weight: 500;
    color: #374151;
  }
}

// 步骤操作按钮
.step-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
  margin-top: 24px;
}

// 文件上传字段样式
.file-upload-field {
  display: flex;
  gap: 8px;
  width: 100%;
  align-items: center;
}

.file-status {
  margin-top: 8px;
  
  .el-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }
}

.file-hint {
  margin-top: 6px;
  
  .hint-text {
    font-size: 12px;
    color: #909399;
  }
}

// 批量上传 - 已选择的Excel文件
.selected-excel {
  margin-top: 12px;
  
  .el-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    font-size: 14px;
  }
}

// 批量上传 - 已选择的附件文件
.selected-attachments {
  margin-top: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  
  h5 {
    margin: 0 0 12px 0;
    font-size: 14px;
    font-weight: 500;
    color: #475569;
  }
  
  .attachment-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    
    .el-tag {
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
  }
}

// 帮助图标
.help-icon {
  color: #909399;
  cursor: help;
  margin-left: 4px;
  
  &:hover {
    color: #667eea;
  }
}

// 空状态
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 500px;
}

.empty-content {
  text-align: center;
  
  .empty-icon {
    width: 120px;
    height: 120px;
    margin: 0 auto 24px;
    background: linear-gradient(135deg, #667eea15, #764ba215);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #667eea;
  }
  
  h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 8px;
  }
  
  p {
    color: #64748b;
    font-size: 0.875rem;
  }
}

// 动画
.animate-slide-up {
  animation: slideUp 0.5s ease-out;
  
  &.delay-1 { animation-delay: 0.1s; }
  &.delay-2 { animation-delay: 0.2s; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

// 文件夹上传区域样式
.folder-upload-dragger {
  width: 100%;
  min-height: 180px;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  background: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #10b981;
    background: #ecfdf5;
  }
  
  .upload-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 24px;
    
    .upload-icon-wrapper {
      width: 64px;
      height: 64px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16px;
      
      .upload-icon {
        font-size: 32px;
        color: white;
      }
    }
    
    .upload-text {
      text-align: center;
      
      .main-text {
        font-size: 16px;
        color: #374151;
        margin-bottom: 8px;
      }
      
      .sub-text {
        font-size: 13px;
        color: #9ca3af;
      }
    }
  }
}

// 上传模式切换
.upload-mode-toggle {
  display: flex;
  justify-content: center;
  
  .el-radio-button {
    .el-icon {
      margin-right: 4px;
    }
  }
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
  
  .main-content {
    padding: 16px;
  }
  
  .template-list {
    grid-template-columns: 1fr;
  }
  
  .upload-mode-cards {
    grid-template-columns: 1fr;
  }
  
  .download-template-card {
    flex-direction: column;
    text-align: center;
  }
  
  .step-actions {
    flex-wrap: wrap;
  }
}
</style>
