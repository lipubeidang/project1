<template>
  <div class="upload-data">
    <!-- 顶部导航 -->
    <Navbar />
    <TemplateNavbar @nav-action="handleNavAction" @audit-action="handleAuditAction" />

    <!-- 主容器 -->
    <div class="container">
      <h2 class="title">上传数据</h2>

      <!-- 第一部分：选择信息 -->
      <div class="section">
        <h3 class="section-title">选择信息</h3>

        <!-- 数据资源目录 -->
      <div class="form-group">
        <label class="label required">数据资源目录：</label>
        <select v-model="resourceDir" class="select">
          <option value="">请选择</option>
          <option 
            v-for="dir in resourceDirs" 
            :key="dir.id" 
            :value="dir.id"
          >
          {{ dir.name }}
          </option>
        </select>
      </div>

        <!-- 选择模板（根据 resourceDir 动态过滤）-->
        <div class="form-group">
          <label class="label required">选择模板：</label>
          
          <!-- 加载中 -->
          <span v-if="loading">加载模板中...</span>
          
          <!-- 已选择目录，且有匹配模板 -->
          <select 
            v-else-if="resourceDir && getFilteredTemplates().length > 0"
            v-model="dataset" 
            class="select"
          >
            <option value="">请选择数据集</option>
            <option 
              v-for="template in getFilteredTemplates()" 
              :key="template.id"
              :value="template.id"
            >
              {{ template.name }}
            </option>
          </select>

          <!-- 未选择目录 -->
          <span v-else-if="!resourceDir">请先选择目录</span>

          <!-- 该目录下无模板 -->
          <span v-else>该目录下暂无模板</span>
        </div>

        <!-- 上传方式（在线填写 / 批量上传）-->
        <div class="form-group">
          <label class="label">上传方式：</label>
          <div class="radio-group">
            <button 
              class="radio-btn" 
              :class="{ active: uploadMode === 'online' }"
              @click="uploadMode = 'online'"
            >
              在线填写
            </button>
            <button 
              class="radio-btn" 
              :class="{ active: uploadMode === 'batch' }"
              @click="uploadMode = 'batch'"
            >
              批量上传
            </button>
          </div>
        </div>
      </div>

      <!-- 第二部分：数据信息（仅在“在线填写”时显示）-->
      <div class="section">
        <h3 class="section-title">数据信息</h3>

        <!-- 只有“在线填写”模式才显示此表单 -->
        <div v-if="uploadMode === 'online'" class="data-form">
          <!-- 对象区域 -->
          <div class="form-group">
            <div class="group-header">对象区域</div>
            <div class="form-item">
              <label class="label required">* 合金成分</label>
              <div class="input-wrapper">
                <input 
                  type="text" 
                  v-model="alloyComposition" 
                  class="input-field"
                placeholder="请输入合金成分"
              />
              <button class="icon-btn">
                <i class="icon">📋</i> <!-- 可替换为实际图标 -->
              </button>
              </div>
              </div>
          </div>
          <!-- 操作区域 -->
          <div class="form-group">
            <div class="group-header">操作区域</div>
            <div class="form-item">
              <label class="label required">* 工艺类型</label>
              <div class="input-wrapper">
                <input 
              type="text" 
              v-model="processType" 
              class="input-field"
              placeholder="请输入工艺类型"
            />
            <button class="icon-btn">
              <i class="icon">📋</i>  
            </button>
              </div>
            </div>

          </div>
          <!-- 时效条件（可展开） -->
          <div class="form-group">
            <div class="expand-header" @click="agingConditionExpanded = !agingConditionExpanded">
              <span class="header-title">时效条件</span>
              <span class="arrow">{{ agingConditionExpanded ? '↓' : '↑' }}</span>
            </div>
            <div v-show="agingConditionExpanded" class="expand-content">
              <div class="dropdown-group">
                <select v-model="agingCondition" class="select">
                    <option value="">请选择</option>
                    <option value="type1">类型一</option>
                    <option value="type2">类型二</option>
                </select>
                <span class="hint">选取一种类型以生成对应的表单</span>    
              </div>
            </div>

          </div>
        </div>

        <!-- 如果是“批量上传”模式，可以提示用户 -->
        
        <div v-else-if="uploadMode === 'batch'" class="batch-upload">
          <!-- 标题栏 -->
          <div class="upload-header">
            <span class="title">上传写好的数据文件</span>
            <button class="download-link" @click="downloadTemplate" :disabled="!dataset">
              📥 下载模板
            </button>
          </div>

          <!-- 上传按钮与文件显示 -->
          <div class="upload-area">
            <!-- 上传按钮 -->
            <div class="upload-btn-container">
              <input
              type="file"
              ref="fileInput"
              accept=".xls,.xlsx,.csv"
              @change="handleFileChange"
              style="display: none;"
              />
              <button class="upload-btn" @click="$refs.fileInput.click()">
                上传
              </button>
            </div>

          <!-- 已选文件显示区 -->
          <div v-if="selectedFile" class="selected-file-info">
            <span class="file-name">{{ selectedFile.name }}</span>
            <span class="file-size">({{ formatFileSize(selectedFile.size) }})</span>
            <button class="remove-file-btn" @click="clearFile">
              ✕
            </button>
          </div>

          <!-- 错误提示 -->
          <div v-if="fileError" class="error-tip">
            {{ fileError }}
          </div>
        </div>

          <!-- 提示说明 -->
          <div class="upload-tips">
            <p>1. 请选择一个文件上传，支持格式: XLS、XLSX和CSV</p>
            <p>2. 若需要导入数据及附件，请将导入数据及附件压缩成RAR或ZIP文件后进行上传</p>
            <p>3. 仅支持上传1GB以内文件</p>
          </div>
        </div>
      </div>
      
      

      <!-- 提交按钮 -->                                                                                                                                                                                                                                                                                                                                     
      <div class="submit-container">
        <button class="submit-btn" @click="submit">提交</button>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import TemplateNavbar from '../components/TemplateNavbar.vue';
import axios from 'axios'; // 别忘了引入 axios

export default {
  components: {
    Navbar,
    TemplateNavbar
  },
  data() {
    return {
      resourceDir: '',           // 当前选择的目录
      dataset: '',               // 选中的模板 ID
      uploadMode: '',      // 上传方式
      allTemplates: [],          // 所有从后端获取的模板
      loading: false,
      agingConditionExpanded: false,            // 加载状态
      selectedFile: null,           // 用户选择的文件
      fileError: '', 

      // 前端写死：每个目录对应哪些模板 ID
      dirTemplateMap: {
        dir1: [1, 2, 3],         // 目录一 → 模板 id 1,2,3
        dir2: [4, 5, 6]          // 目录二 → 模板 id 4,5,6
      },
      resourceDirs: [],

      // 表单字段
      alloyComposition: '',
      processType: '',
      agingCondition: '',
      description: ''
    }
  },
  methods: {
    // 处理TemplateNavbar导航事件
    handleNavAction(action) {
      switch (action) {
        case 'create':
          this.$router.push('/template-create').catch(() => {});
          break;
      }
    },
    
    // 处理TemplateNavbar审核管理事件
    handleAuditAction(action) {
      switch (action) {
        case 'templateAudit':
          this.$router.push('/template-audit').catch(() => {});
          break;
        case 'templateStop':
          this.$message.info('进入模版停用页面');
          break;
        default:
          this.$message.info('功能开发中...');
      }
    },
    
    // 筛选出当前目录对应的模板
    getFilteredTemplates() {
    return this.allTemplates;
  },    
    // 处理文件选择
    handleFileChange(event) {
    const file = event.target.files[0];
    if (!file) return;

    // 检查文件类型（只允许 .xls, .xlsx, .csv）
    const allowedTypes = ['.xls', '.xlsx', '.csv'];
    const ext = file.name.toLowerCase().split('.').pop();
    if (!allowedTypes.includes('.' + ext)) {
      this.fileError = '不支持的文件格式，请上传 XLS、XLSX 或 CSV 文件';
      return;
    }

    // 检查文件大小（1GB）
    if (file.size > 1 * 1024 * 1024 * 1024) {
      this.fileError = '文件大小不能超过 1GB';
      return;
    }

    this.selectedFile = file;
    this.fileError = '';
  },

    // 提交表单
    async submit() {
  // 情况 1：批量上传
  if (this.uploadMode === 'batch') {
    if (!this.selectedFile) {
      alert('请先选择要上传的文件');
      return;
    }

    if (this.fileError) {
      alert(this.fileError);
      return;
    }

    // 创建 FormData
    const formData = new FormData();
    formData.append('file', this.selectedFile);
    formData.append('resourceDir', this.resourceDir);
    formData.append('dataset', this.dataset);

    try {
      const response = await axios.post(`/api/moduledata/upload/${this.dataset}`, formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  }
});
      alert('批量上传成功！');
      console.log('上传响应:', response.data);
    } catch (error) {
      console.error('上传失败:', error);
      alert('上传失败，请检查网络或文件格式');
    }

  // 情况 2：在线填写
  } else if (this.uploadMode === 'online') {
    // ✅ 你已有的在线填写提交逻辑
    // 例如：校验表单、收集数据、调用另一个接口
    if (!this.alloyComposition) {
      alert('请填写合金成分');
      return;
    }
    if (!this.processType) {
      alert('请填写工艺类型');
      return;
    }

    try {
      const response = await axios.post('/api/online-submit', {
        resourceDir: this.resourceDir,
        dataset: this.dataset,
        form: {
          alloyComposition: this.alloyComposition,
          processType: this.processType,
          agingCondition: this.agingCondition,
          description: this.description
        }
      });
      alert('在线填写提交成功！');
      console.log('提交响应:', response.data);
    } catch (error) {
      console.error('提交失败:', error);
      alert('提交失败，请重试');
    }

  // 情况 3：未选择上传方式
  } else {
    alert('请选择上传方式（在线填写 或 批量上传）');
  }
},
async downloadTemplate() {
  console.log('【DEBUG】downloadTemplate 被调用了！dataset =', this.dataset); 
  if (!this.dataset) {
    alert('请先选择一个模板');
    return;
  }

  try {
    // 使用 window.open 直接打开下载链接
    // 这样可以避免 axios 拦截器的影响，让浏览器直接处理文件下载
    const downloadUrl = `http://localhost:8083/basemodule/moduledata/downloadmodule/${this.dataset}`;
    
    // 创建隐藏的 iframe 来触发下载（避免打开新标签页）
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = downloadUrl;
    document.body.appendChild(iframe);
    
    // 3秒后移除 iframe
    setTimeout(() => {
      document.body.removeChild(iframe);
    }, 3000);
    
    alert('模板下载已开始');
  } catch (error) {
    console.error('下载模板失败:', error);
    alert('下载失败，请检查网络或联系管理员');
  }
},
// 格式化文件大小：bytes → KB/MB/GB
  formatFileSize(bytes) {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  // 清除已选文件
  clearFile() {
    this.selectedFile = null;
    this.fileError = '';
    // 可选：重置 input 的 value，避免重复选同一个文件不触发 change
    if (this.$refs.fileInput) {
      this.$refs.fileInput.value = '';
    }
  },
  },
  async mounted() {
  this.loading = true;
  try {
    const response = await axios.get('/api/moduleparent/list');
    if (response.data && Array.isArray(response.data.moduleParentList)) {
      this.resourceDirs = response.data.moduleParentList;
    } else {
      console.error('目录数据格式错误:', response.data);
      this.resourceDirs = [];
    }
  } catch (error) {
    console.error('获取数据资源目录失败:', error);
    alert('无法加载数据资源目录');
    this.resourceDirs = [];
  } finally {
    this.loading = false;
  }
},
  watch: {
  async resourceDir(newVal) {
    if (!newVal) {
      this.allTemplates = [];
      this.dataset = '';
      return;
    }

    this.loading = true;
    try {
      const response = await axios.get(`/api/module/getmodules/${newVal}`);
      this.allTemplates = response.data.module_list || [];
    } catch (error) {
      console.error('获取模板失败:', error);
      alert('无法加载该目录下的模板');
      this.allTemplates = [];
    } finally {
      this.loading = false;
    }
  }
},

}
</script>
<style scoped>
/* 上面的 CSS 可以直接复制进来 */
.data-form {
  margin-top: 20px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  padding: 20px;
}
.form-group {
  margin-bottom: 20px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  padding: 16px;
  background: #f9f9f9;
}
.form-item {
  margin-bottom: 16px;
}

.label {
  display: block;
  font-size: 14px;
  color: #333;
  margin-bottom: 6px;
}

.required::before {
  content: "*";
  color: red;
  margin-right: 4px;
}

.input-wrapper {
  position: relative;
  width: 100%;
}

.input-field {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
}

.icon-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 4px;
  color: #666;
  font-size: 14px;
}

.icon-btn:hover {
  background: #f0f0f0;
}

.expand-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  padding: 12px 0;
  border-bottom: 1px solid #ddd;
}

.expand-header:hover {
  background: #f5f5f5;
}

.arrow {
  font-size: 16px;
  transition: transform 0.2s;
}

.expand-content {
  padding: 12px 0;
  border-top: 1px solid #eee;
}

.dropdown-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
}

.hint {
  color: #666;
  font-size: 12px;
}
.container {
  width: 90%;
  max-width: 1000px;
  margin: 40px auto;
  padding: 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.title {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  color: #1a1a1a;
}

.section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 16px;
  color: #333;
}

.form-group {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 12px;
}

.label {
  min-width: 140px;
  font-weight: 500;
  color: #333;
  text-align: right;
  padding-right: 12px;
}

.required::before {
  content: '*';
  color: red;
  margin-right: 4px;
}

.select {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease;
}

.select:focus {
  border-color: #007bff;
}

.radio-group {
  display: flex;
  gap: 12px;
}

.radio-btn {
  padding: 8px 16px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.radio-btn:hover {
  background: #f5f5f5;
}

.radio-btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.submit-container {
  text-align: center;
  margin-top: 40px;
}

.submit-btn {
  padding: 12px 32px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.submit-btn:hover {
  background: #0056b3;
}

/* 批量上传样式 */
.batch-upload {
  margin-top: 20px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  padding: 20px;
}

.upload-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}

.upload-header .title {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.download-link {
  color: #0066cc;
  text-decoration: none;
  font-size: 14px;
}

.download-link:hover {
  text-decoration: underline;
}

.upload-btn-container {
  text-align: center;
  margin: 20px 0;
}

.upload-btn {
  padding: 12px 32px;
  background-color: #0066cc;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.upload-btn:hover {
  background-color: #0052a3;
}

.upload-tips {
  margin-top: 20px;
  font-size: 14px;
  color: #666;
  line-height: 1.8;
}

.upload-tips p {
  margin: 8px 0;
}
/* 上传区域整体样式 */
.upload-area {
  margin: 20px 0;
}

/* 已选文件信息展示 */
.selected-file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background-color: #f0f8ff;
  border: 1px solid #bee1ff;
  border-radius: 6px;
  font-size: 14px;
  color: #333;
  margin-top: 12px;
}

.file-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.file-size {
  color: #666;
  font-size: 12px;
}

.remove-file-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #999;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-file-btn:hover {
  color: #d9534f;
}

/* 错误提示样式 */
.error-tip {
  margin-top: 8px;
  color: #d9534f;
  font-size: 13px;
}
</style>