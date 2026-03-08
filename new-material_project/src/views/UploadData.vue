<template>
  <div class="upload-data">
    <!-- 顶部导航 -->
    <Navbar @dropdown-action="handleDropdownAction" />
    <TemplateNavbar @nav-action="handleNavAction" @audit-action="handleAuditAction" />

    <!-- 主容器 -->
    <div class="container">
      <div class="header-with-action">
        <h2 class="title">上传数据</h2>
        <button class="audit-link-btn" @click="goToAudit" v-if="isAdmin">
          <i class="el-icon-s-check"></i>
          前往模板审核
        </button>
      </div>

      <!-- 第一部分：选择信息 -->
      <div class="section">
        <h3 class="section-title">选择信息</h3>

        <!-- 大目录选择 -->
        <div class="form-group">
          <label class="label required">数据资源目录：</label>
          <select v-model="selectedBigCategory" @change="handleBigCategoryChange" class="select">
            <option value="">请选择大目录</option>
            <option value="big_cat_1">材料属性</option>
            <option value="big_cat_2">数据来源</option>
            <option value="big_cat_3">材料功能</option>
          </select>
        </div>

        <!-- 小目录选择 -->
        <div class="form-group">
          <label class="label required">子目录：</label>
          <select v-model="selectedParentId" @change="handleParentChange" class="select" :disabled="!selectedBigCategory">
            <option value="">请先选择大目录</option>
            <option 
              v-for="subCat in currentSubCategories" 
              :key="subCat.id"
              :value="subCat.id"
            >
              {{ subCat.name }}
            </option>
          </select>
        </div>

        <!-- 选择模板 -->
        <div class="form-group">
          <label class="label required">选择模板：</label>
          
          <!-- 加载中 -->
          <span v-if="loadingTemplates">加载模板中...</span>
          
          <!-- 已选择目录，且有匹配模板 -->
          <select 
            v-else-if="selectedParentId && childTemplates.length > 0"
            v-model="selectedTemplateId" 
            class="select"
          >
            <option value="">请选择模板</option>
            <option 
              v-for="template in childTemplates" 
              :key="template.id"
              :value="template.id"
            >
              {{ template.name }}
            </option>
          </select>

          <!-- 未选择目录 -->
          <span v-else-if="!selectedParentId">请先选择数据资源目录</span>

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
              @click="handleOnlineClick"
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

      <!-- 第二部分：批量上传 -->
      <div class="section" v-if="uploadMode === 'batch'">
        <h3 class="section-title">数据信息</h3>
        
        <div class="batch-upload">
          <!-- 标题栏 -->
          <div class="upload-header">
            <span class="title">上传写好的数据文件</span>
            <button 
              class="download-link" 
              @click="downloadTemplate" 
              :disabled="!selectedTemplateId"
            >
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

      <!-- 提交按钮（仅在批量上传模式显示）-->
      <div class="submit-container" v-if="uploadMode === 'batch'">
        <button class="submit-btn" @click="submitBatchUpload">提交</button>
      </div>
    </div>

  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import TemplateNavbar from '../components/TemplateNavbar.vue';

export default {
  components: {
    Navbar,
    TemplateNavbar
  },
  data() {
    return {
      uploadMode: '',                    // 上传方式
      selectedBigCategory: '',           // 选中的大目录
      parentDirectories: [],             // 父目录列表
      childTemplates: [],                // 子模板列表
      selectedParentId: '',              // 选中的父目录ID
      selectedTemplateId: '',            // 选中的模板ID
      loadingParents: false,             // 加载父目录状态
      loadingTemplates: false,           // 加载模板状态
      selectedFile: null,                // 用户选择的文件
      fileError: '',                     // 文件错误信息
      isAdmin: false,                    // 是否为管理员
      // 三个大目录的小目录配置（固定）
      directoryStructure: {
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
      },
      currentSubCategories: []           // 当前显示的小目录列表
    }
  },
  computed: {
    // 获取选中模板的名称
    selectedTemplateName() {
      if (!this.selectedTemplateId || this.childTemplates.length === 0) {
        return '';
      }
      const template = this.childTemplates.find(t => t.id === this.selectedTemplateId);
      const templateName = template ? template.name : '';
      console.log('📝 用户选择的模板名称:', templateName, '模板ID:', this.selectedTemplateId);
      return templateName;
    }
  },
  methods: {
    // 处理Navbar下拉菜单事件
    handleDropdownAction(action) {
      switch (action) {
        case 'profile':
          this.$router.push('/person').catch(() => {});
          break;
        case 'logout':
          this.$router.push('/login').catch(() => {});
          break;
      }
    },
    
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
          // TODO: 跳转到模版停用页面
          break;
        default:
          this.$message.info('功能开发中...');
      }
    },
    
    // 大目录改变时更新小目录列表
    handleBigCategoryChange() {
      this.currentSubCategories = this.directoryStructure[this.selectedBigCategory] || [];
      // 清空子目录和模板选择
      this.selectedParentId = '';
      this.selectedTemplateId = '';
      this.childTemplates = [];
    },

    // 获取父目录列表（保留但不再使用）
    async fetchParentDirectories() {
      this.loadingParents = true;
      try {
        const response = await this.$request.get('/basemodule/moduleparent/list');
        console.log('父目录响应:', response.data);
        
        if (response.data && response.data.code === 0) {
          // 使用正确的字段名
          this.parentDirectories = response.data.module_list || [];
          console.log('父目录列表:', this.parentDirectories);
        } else {
          throw new Error(response.data.msg || '获取父目录失败');
        }
      } catch (error) {
        console.error('获取父目录失败:', error);
        this.$message.error('获取父目录失败: ' + (error.message || '请重试'));
      } finally {
        this.loadingParents = false;
      }
    },

    // 父目录改变时的处理
    async handleParentChange() {
      if (!this.selectedParentId) {
        this.childTemplates = [];
        this.selectedTemplateId = '';
        return;
      }
      
      this.loadingTemplates = true;
      this.selectedTemplateId = '';
      
      try {
        const response = await this.$request.get(`/basemodule/module/getmodules/${this.selectedParentId}`);
        console.log('子模板响应:', response.data);
        
        if (response.data && response.data.code === 0) {
          // 尝试多个可能的字段名
          this.childTemplates = response.data.moduleList || response.data.module_list || [];
          console.log('子模板列表:', this.childTemplates);
        } else {
          throw new Error(response.data.msg || '获取子模板失败');
        }
      } catch (error) {
        console.error('获取子模板失败:', error);
        this.$message.error('获取子模板失败: ' + (error.message || '请重试'));
        this.childTemplates = [];
      } finally {
        this.loadingTemplates = false;
      }
    },

    // 点击在线填写
    handleOnlineClick() {
      if (!this.selectedTemplateId) {
        this.$message.warning('请先选择模板');
        return;
      }
      
      this.uploadMode = 'online';
      
      console.log('跳转到数据填写页面，参数:', {
        moduleId: this.selectedTemplateId,
        templateName: this.selectedTemplateName
      });
      
      // 跳转到数据填写页面
      this.$router.push({
        name: 'DataEntryPage',
        params: {
          moduleId: this.selectedTemplateId,
          templateName: this.selectedTemplateName
        },
        query: {
          title: '在线填写数据'
        }
      });
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
      // 重置 input 的 value，避免重复选同一个文件不触发 change
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = '';
      }
    },

    // 提交批量上传
    async submitBatchUpload() {
      if (!this.selectedFile) {
        this.$message.warning('请先选择要上传的文件');
        return;
      }

      if (this.fileError) {
        this.$message.error(this.fileError);
        return;
      }

      // 创建 FormData（后端只需要 file 参数）
      const formData = new FormData();
      formData.append('file', this.selectedFile);

      try {
        const response = await this.$request.post(
          `/basemodule/moduledata/upload/${this.selectedTemplateId}`,
          formData
          // 不设置 headers，让拦截器和浏览器自动处理 FormData
        );
        
        if (response.data && response.data.code === 0) {
          this.$message.success('批量上传成功！');
          console.log('上传响应:', response.data);
          // 清空文件
          this.clearFile();
        } else {
          throw new Error(response.data.msg || '上传失败');
        }
      } catch (error) {
        console.error('上传失败:', error);
        this.$message.error('上传失败，请检查网络或文件格式');
      }
    },

    // 下载模板
    async downloadTemplate() {
      console.log('【DEBUG】downloadTemplate 被调用了！selectedTemplateId =', this.selectedTemplateId);
      
      if (!this.selectedTemplateId) {
        this.$message.warning('请先选择一个模板');
        return;
      }

      try {
        // 使用 window.open 直接打开下载链接
        // 这样可以避免 axios 拦截器的影响，让浏览器直接处理文件下载
        const downloadUrl = `http://localhost:8083/basemodule/moduledata/downloadmodule/${this.selectedTemplateId}`;
        
        // 创建隐藏的 iframe 来触发下载（避免打开新标签页）
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = downloadUrl;
        document.body.appendChild(iframe);
        
        // 3秒后移除 iframe
        setTimeout(() => {
          document.body.removeChild(iframe);
        }, 3000);
        
        this.$message.success('模板下载已开始');
      } catch (error) {
        console.error('下载模板失败:', error);
        this.$message.error('下载失败，请检查网络或联系管理员');
      }
    },
    
    // 检查管理员权限
    checkAdminPermission() {
      try {
        const userData = JSON.parse(localStorage.getItem('xm-user') || '{}');
        const userRole = userData.role || userData.logininfo?.type || userData.logininfo?.userType || userData.logininfo?.role || 1;
        this.isAdmin = userRole === 2;
      } catch (error) {
        console.error('获取用户权限失败:', error);
        this.isAdmin = false;
      }
    },
    
    // 跳转到模板审核页面
    goToAudit() {
      this.$router.push('/template-audit').catch(() => {});
    }
  },
  async mounted() {
    // 不再需要加载父目录列表，因为使用固定的目录结构
    // await this.fetchParentDirectories();
    
    // 检查是否为管理员
    this.checkAdminPermission();
  }
}
</script>
<style scoped>
@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.4);
  }
  50% {
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.8);
  }
}

.upload-data {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7474bf 100%);
  background-size: 100% 100%;
  background-attachment: fixed;
  padding-top: 140px;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  scroll-behavior: smooth;
  /* GPU硬件加速 */
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

.upload-data::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 15% 25%, rgba(102, 126, 234, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 85% 75%, rgba(139, 92, 246, 0.2) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
  /* 静态背景，不添加动画 */
  transform: translate3d(0, 0, 0);
  will-change: auto;
}

/* 自定义外层滚动条样式 */
.upload-data::-webkit-scrollbar {
  width: 12px;
}

.upload-data::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 6px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.upload-data::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.upload-data::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
}

.container {
  width: 90%;
  max-width: 1000px;
  margin: 20px auto 120px auto;
  padding: 40px;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  position: relative;
  z-index: 1;
  animation: fadeInScale 0.3s ease;
  /* GPU硬件加速 */
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

.container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 200px;
  background: linear-gradient(180deg, 
    rgba(102, 126, 234, 0.05) 0%, 
    transparent 100%);
  border-radius: 20px 20px 0 0;
  pointer-events: none;
}

.container::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, 
    #667eea 0%, 
    #764ba2 50%, 
    #667eea 100%);
  background-size: 100% 100%;
  border-radius: 0 0 20px 20px;
  /* 移除动画以提升性能 */
  transform: translate3d(0, 0, 0);
}

@keyframes gradientSlide {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

.header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 35px;
}

.title {
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0;
  letter-spacing: 0.5px;
  position: relative;
  padding-bottom: 15px;
  flex: 1;
}

.audit-link-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  white-space: nowrap;
}

.audit-link-btn:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.audit-link-btn i {
  font-size: 16px;
}

.title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%) translate3d(0, 0, 0);
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
  /* 简化动画，使用opacity替代box-shadow动画 */
  opacity: 0.9;
}

.section {
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.98);
  padding: 25px;
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  border: 2px solid rgba(102, 126, 234, 0.15);
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), 
              box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  animation: slideDown 0.3s ease;
  /* GPU硬件加速 */
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

.section:hover {
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.22);
  transform: translate3d(0, -2px, 0);
  will-change: transform, box-shadow;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
  letter-spacing: 0.5px;
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
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 10px;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.95);
}

.select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.select:disabled {
  background-color: rgba(245, 247, 250, 0.8);
  cursor: not-allowed;
  border-color: rgba(102, 126, 234, 0.1);
}

.radio-group {
  display: flex;
  gap: 12px;
}

.radio-btn {
  padding: 10px 20px;
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  transition: transform 0.2s ease-out, 
              box-shadow 0.2s ease-out,
              background 0.2s ease-out;
  position: relative;
  overflow: hidden;
  /* GPU硬件加速 */
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

.radio-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(102, 126, 234, 0.1) 50%, 
    transparent 100%);
  transition: left 0.5s ease;
}

.radio-btn:hover:not(:disabled)::before {
  left: 100%;
}

.radio-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.1) 0%, 
    rgba(118, 75, 162, 0.1) 100%);
  border-color: #667eea;
  color: #667eea;
  transform: translate3d(0, -2px, 0);
  box-shadow: 0 5px 18px rgba(102, 126, 234, 0.3);
  will-change: transform, box-shadow;
}

.radio-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.radio-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  box-shadow: 0 5px 18px rgba(102, 126, 234, 0.3);
  transform: translate3d(0, -2px, 0);
}

.batch-tip {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  text-align: center;
  color: #666;
}

.batch-tip p {
  margin-bottom: 20px;
}

.upload-demo {
  margin-top: 20px;
}

/* 批量上传样式 */
.batch-upload {
  margin-top: 20px;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.95) 0%, 
    rgba(248, 249, 250, 0.95) 100%);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 2px solid rgba(102, 126, 234, 0.15);
  padding: 25px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1),
              0 0 0 1px rgba(102, 126, 234, 0.1) inset;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.batch-upload:hover {
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2),
              0 0 0 1px rgba(102, 126, 234, 0.2) inset;
  transform: translateY(-2px);
}

.upload-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.15);
  margin-bottom: 20px;
}

.upload-header .title {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
  text-align: left;
  letter-spacing: 0.5px;
}

.download-link {
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 10px 20px;
  border-radius: 10px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.download-link:hover:not(:disabled) {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.download-link:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #c0c4cc;
  box-shadow: none;
}

.upload-btn-container {
  text-align: center;
  margin: 20px 0;
}

.upload-btn {
  padding: 12px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.upload-btn:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.upload-tips {
  margin-top: 20px;
  padding: 15px;
  background: linear-gradient(135deg, 
    rgba(249, 249, 249, 0.9) 0%, 
    rgba(245, 247, 250, 0.9) 100%);
  border-radius: 10px;
  border: 2px solid rgba(102, 126, 234, 0.1);
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
}

.upload-tips p {
  margin: 8px 0;
  padding-left: 8px;
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
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.08) 0%, 
    rgba(118, 75, 162, 0.08) 100%);
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 10px;
  font-size: 14px;
  color: #333;
  margin-top: 12px;
  transition: all 0.3s ease;
}

.selected-file-info:hover {
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.15);
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
  padding: 10px 12px;
  background: rgba(245, 108, 108, 0.1);
  border: 2px solid rgba(245, 108, 108, 0.3);
  border-radius: 8px;
  color: #F56C6C;
  font-size: 13px;
  font-weight: 500;
}

/* 提交按钮容器 */
.submit-container {
  text-align: center;
  margin-top: 40px;
}

.submit-btn {
  padding: 12px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.submit-btn:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}
</style>