<template>
  <div class="upload-data">
    <Navbar />
    
    <div class="page-container">
      <div class="content-wrapper animate-slide-up">
        <!-- 页面标题 -->
        <div class="page-header">
          <h1 class="page-title">
            <el-icon><Upload /></el-icon>
            上传数据
          </h1>
          <p class="page-desc">选择数据资源并上传数据，支持在线填写和批量导入</p>
        </div>

        <!-- 选择信息区域 -->
        <div class="section">
          <div class="section-header">
            <el-icon><Folder /></el-icon>
            <h3>选择信息</h3>
          </div>
          
          <div class="form-grid">
            <!-- 大目录选择 -->
            <div class="form-item">
              <label class="form-label required">数据资源目录</label>
              <el-select 
                v-model="selectedBigCategory" 
                placeholder="请选择大目录"
                @change="handleBigCategoryChange"
                size="large"
              >
                <el-option value="big_cat_1" label="材料属性" />
                <el-option value="big_cat_2" label="数据来源" />
                <el-option value="big_cat_3" label="材料功能" />
              </el-select>
            </div>

            <!-- 小目录选择 -->
            <div class="form-item">
              <label class="form-label required">子目录</label>
              <el-select 
                v-model="selectedParentId" 
                placeholder="请先选择大目录"
                :disabled="!selectedBigCategory"
                @change="handleParentChange"
                size="large"
              >
                <el-option 
                  v-for="subCat in currentSubCategories" 
                  :key="subCat.id"
                  :value="subCat.id"
                  :label="subCat.name"
                />
              </el-select>
            </div>

            <!-- 选择模板 -->
            <div class="form-item">
              <label class="form-label required">选择数据资源</label>
              <el-select 
                v-model="selectedTemplateId" 
                placeholder="请选择数据资源"
                :disabled="!selectedParentId || loadingTemplates"
                :loading="loadingTemplates"
                size="large"
              >
                <el-option 
                  v-for="template in childTemplates" 
                  :key="template.id"
                  :value="template.id"
                  :label="template.name"
                />
              </el-select>
              <span v-if="selectedParentId && !loadingTemplates && childTemplates.length === 0" class="form-tip">
                该目录下暂无数据资源
              </span>
            </div>
          </div>

          <!-- 上传方式选择 -->
          <div class="upload-mode-section">
            <label class="form-label">上传方式</label>
            <div class="mode-cards">
              <div 
                class="mode-card" 
                :class="{ active: uploadMode === 'online' }"
                @click="handleOnlineClick"
              >
                <div class="mode-icon">
                  <el-icon :size="32"><Edit /></el-icon>
                </div>
                <div class="mode-info">
                  <h4>在线填写</h4>
                  <p>逐条填写数据，适合少量数据录入</p>
                </div>
              </div>
              <div 
                class="mode-card" 
                :class="{ active: uploadMode === 'batch' }"
                @click="uploadMode = 'batch'"
              >
                <div class="mode-icon">
                  <el-icon :size="32"><DocumentAdd /></el-icon>
                </div>
                <div class="mode-info">
                  <h4>批量上传</h4>
                  <p>上传Excel文件，适合大批量数据导入</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 批量上传区域 -->
        <Transition name="fade-slide">
          <div class="section" v-if="uploadMode === 'batch'">
            <div class="section-header">
              <el-icon><DocumentAdd /></el-icon>
              <h3>数据信息</h3>
            </div>

            <div class="batch-upload">
              <!-- 标题栏 -->
              <div class="upload-header">
                <span class="upload-title">上传数据文件</span>
                <el-button 
                  type="primary" 
                  link
                  :icon="Download"
                  :disabled="!selectedTemplateId"
                  @click="downloadTemplate"
                >
                  下载数据模板
                </el-button>
              </div>

              <!-- 上传区域 -->
              <el-upload
                ref="uploadRef"
                class="upload-area"
                drag
                action="#"
                :auto-upload="false"
                :limit="1"
                :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                accept=".xls,.xlsx,.csv"
              >
                <div class="upload-content">
                  <el-icon class="upload-icon"><UploadFilled /></el-icon>
                  <div class="upload-text">
                    <p>将文件拖到此处，或<em>点击上传</em></p>
                    <span>支持 XLS、XLSX、CSV 格式，最大 1GB</span>
                  </div>
                </div>
              </el-upload>

              <!-- 提示说明 -->
              <div class="upload-tips">
                <div class="tip-item">
                  <el-icon><InfoFilled /></el-icon>
                  <span>请选择一个文件上传，支持格式: XLS、XLSX 和 CSV</span>
                </div>
                <div class="tip-item">
                  <el-icon><InfoFilled /></el-icon>
                  <span>若需要导入数据及附件，请将导入数据及附件压缩成RAR或ZIP文件后进行上传</span>
                </div>
                <div class="tip-item">
                  <el-icon><InfoFilled /></el-icon>
                  <span>仅支持上传1GB以内文件</span>
                </div>
              </div>
            </div>

            <!-- 提交按钮 -->
            <div class="submit-section">
              <el-button size="large" @click="resetForm">重置</el-button>
              <el-button 
                type="primary" 
                size="large" 
                :icon="Upload"
                :loading="uploading"
                @click="submitBatchUpload"
              >
                提交上传
              </el-button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Upload, Folder, Edit, DocumentAdd, Download, UploadFilled, InfoFilled
} from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'

const router = useRouter()

// 状态
const uploadMode = ref('')
const selectedBigCategory = ref('')
const selectedParentId = ref('')
const selectedTemplateId = ref('')
const loadingTemplates = ref(false)
const uploading = ref(false)
const uploadRef = ref(null)
const selectedFile = ref(null)

// 目录结构
const directoryStructure = {
  big_cat_1: [
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
  ],
  big_cat_2: [
    { id: 11, name: '文献' },
    { id: 12, name: '计算' },
    { id: 13, name: '实验' },
    { id: 14, name: '研发生产' },
    { id: 15, name: '临床应用' },
    { id: 16, name: '其他数据来源' }
  ],
  big_cat_3: [
    { id: 17, name: '骨科材料' },
    { id: 18, name: '心血管材料' },
    { id: 19, name: '牙科材料' },
    { id: 20, name: '其他材料功能' }
  ]
}

const currentSubCategories = ref([])
const childTemplates = ref([])

// 计算选中的模板名称
const selectedTemplateName = computed(() => {
  if (!selectedTemplateId.value || childTemplates.value.length === 0) return ''
  const template = childTemplates.value.find(t => t.id === selectedTemplateId.value)
  return template ? template.name : ''
})

// 大目录改变
const handleBigCategoryChange = () => {
  currentSubCategories.value = directoryStructure[selectedBigCategory.value] || []
  selectedParentId.value = ''
  selectedTemplateId.value = ''
  childTemplates.value = []
}

// 小目录改变
const handleParentChange = async () => {
  if (!selectedParentId.value) {
    childTemplates.value = []
    selectedTemplateId.value = ''
    return
  }

  loadingTemplates.value = true
  selectedTemplateId.value = ''

  try {
    const response = await request.get(`/basemodule/module/getmodules/${selectedParentId.value}`)
    if (response.data?.code === 0) {
      childTemplates.value = response.data.moduleList || response.data.module_list || []
    } else {
      throw new Error(response.data?.msg || '获取模板失败')
    }
  } catch (error) {
    console.error('获取模板失败:', error)
    ElMessage.error('获取模板列表失败')
    childTemplates.value = []
  } finally {
    loadingTemplates.value = false
  }
}

// 点击在线填写
const handleOnlineClick = () => {
  if (!selectedTemplateId.value) {
    ElMessage.warning('请先选择数据资源')
    return
  }
  
  uploadMode.value = 'online'
  
  // 跳转到数据填写页面
  router.push({
    name: 'DataEntry',
    params: {
      moduleId: selectedTemplateId.value
    },
    query: {
      templateName: selectedTemplateName.value
    }
  })
}

// 文件选择
const handleFileChange = (file) => {
  // 检查文件大小（1GB）
  if (file.size > 1 * 1024 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 1GB')
    uploadRef.value?.clearFiles()
    return
  }
  selectedFile.value = file.raw
}

// 文件移除
const handleFileRemove = () => {
  selectedFile.value = null
}

// 下载模板
const downloadTemplate = () => {
  if (!selectedTemplateId.value) {
    ElMessage.warning('请先选择一个数据资源')
    return
  }

  // 使用 iframe 下载
  const downloadUrl = `http://localhost:8083/basemodule/moduledata/downloadmodule/${selectedTemplateId.value}`
  const iframe = document.createElement('iframe')
  iframe.style.display = 'none'
  iframe.src = downloadUrl
  document.body.appendChild(iframe)
  
  setTimeout(() => {
    document.body.removeChild(iframe)
  }, 3000)
  
  ElMessage.success('数据模板下载已开始')
}

// 提交批量上传
const submitBatchUpload = async () => {
  if (!selectedTemplateId.value) {
    ElMessage.warning('请先选择数据资源')
    return
  }
  
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }

  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await request.post(
      `/basemodule/moduledata/upload/${selectedTemplateId.value}`,
      formData
    )
    
    if (response.data?.code === 0) {
      ElMessage.success('批量上传成功！')
      resetForm()
    } else {
      throw new Error(response.data?.msg || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('上传失败，请检查网络或文件格式')
  } finally {
    uploading.value = false
  }
}

// 重置表单
const resetForm = () => {
  selectedBigCategory.value = ''
  selectedParentId.value = ''
  selectedTemplateId.value = ''
  uploadMode.value = ''
  currentSubCategories.value = []
  childTemplates.value = []
  selectedFile.value = null
  uploadRef.value?.clearFiles()
}
</script>

<style lang="scss" scoped>
.upload-data {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7474bf 100%);
  background-attachment: fixed;
}

.page-container {
  padding: 100px 24px 48px;
  min-height: 100vh;
}

.content-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

// 页面标题
.page-header {
  text-align: center;
  margin-bottom: 32px;
  
  .page-title {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    font-size: 28px;
    font-weight: 600;
    color: white;
    margin-bottom: 8px;
    
    .el-icon {
      font-size: 32px;
    }
  }
  
  .page-desc {
    color: rgba(255, 255, 255, 0.8);
    font-size: 16px;
  }
}

// 区块
.section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  
  .section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
    
    .el-icon {
      font-size: 24px;
      color: #667eea;
    }
    
    h3 {
      font-size: 18px;
      font-weight: 600;
      color: #1e293b;
    }
  }
}

// 表单网格
.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 32px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  
  .el-select {
    width: 100%;
  }
  
  .form-tip {
    font-size: 12px;
    color: #94a3b8;
  }
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  
  &.required::before {
    content: '*';
    color: #ef4444;
    margin-right: 4px;
  }
}

// 上传方式选择
.upload-mode-section {
  .form-label {
    display: block;
    margin-bottom: 16px;
  }
}

.mode-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  
  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
}

.mode-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #667eea;
    background: #f0f4ff;
    transform: translateY(-2px);
  }
  
  &.active {
    border-color: #667eea;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    
    .mode-icon {
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: white;
    }
  }
  
  .mode-icon {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    background: #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748b;
    transition: all 0.3s ease;
  }
  
  .mode-info {
    flex: 1;
    
    h4 {
      font-size: 16px;
      font-weight: 600;
      color: #1e293b;
      margin-bottom: 4px;
    }
    
    p {
      font-size: 13px;
      color: #64748b;
    }
  }
}

// 批量上传
.batch-upload {
  .upload-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    .upload-title {
      font-size: 14px;
      font-weight: 500;
      color: #475569;
    }
  }
}

.upload-area {
  width: 100%;
  
  :deep(.el-upload-dragger) {
    width: 100%;
    height: 180px;
    border-radius: 12px;
    border: 2px dashed #d1d5db;
    background: #f9fafb;
    transition: all 0.3s ease;
    
    &:hover {
      border-color: #667eea;
      background: #f0f4ff;
    }
  }
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  
  .upload-icon {
    font-size: 48px;
    color: #9ca3af;
    margin-bottom: 16px;
  }
  
  .upload-text {
    text-align: center;
    
    p {
      font-size: 14px;
      color: #6b7280;
      margin-bottom: 4px;
      
      em {
        color: #667eea;
        font-style: normal;
      }
    }
    
    span {
      font-size: 12px;
      color: #9ca3af;
    }
  }
}

.upload-tips {
  margin-top: 20px;
  
  .tip-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 0;
    color: #64748b;
    font-size: 13px;
    
    .el-icon {
      color: #94a3b8;
    }
  }
}

.submit-section {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

// 动画
.animate-slide-up {
  animation: slideUp 0.5s ease forwards;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
