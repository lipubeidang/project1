<template>
    <div class="createdataset-page" :key="componentKey">
        <Navbar @dropdown-action="handleDropdownAction" />
        <TemplateNavbar @nav-action="handleNavAction" @audit-action="handleAuditAction" />
        <div class="create-dataset-page">
            <!-- 页面标题 -->
            <h1 class="page-title">创建数据集</h1>

            <!-- 表单 -->
            <form @submit.prevent="handleSubmit">
                <!-- 数据集名称 -->
                <div class="form-item">
                    <label class="label required">数据集名称</label>
                    <div class="input-group">
                        <input
                            v-model="formData.name"
                            type="text"
                            placeholder="请输入数据集名称"
                            maxlength="200"
                            class="input"
                        />
                        <span class="char-count">{{ formData.name.length }}/200</span>
                    </div>
                </div>

                <!-- 数据集摘要 -->
                <div class="form-item">
                    <label class="label required">数据集摘要</label>
                    <div class="input-group">
                        <textarea
                            v-model="formData.description"
                            placeholder="请输入数据集摘要"
                            maxlength="500"
                            class="textarea"
                            rows="4"
                       ></textarea>
                        <span class="char-count">{{ formData.description.length }}/500</span>
                    </div>
                </div>

                <!-- 封面图上传 -->
                <div class="form-item">
                  <label class="label">封面</label>
                  <div class="upload-container" @click="handleUploadClick">
                    <div class="upload-icon">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M12 5V19M5 12H19" stroke="#999" stroke-width="2" stroke-linecap="round" />
                      </svg>
                    </div>
                    <p class="upload-text">请上传226px*170px</p>
                    <p class="upload-subtext">比例的封面图</p>
                    <input
                      type="file"
                      ref="coverFileInput"
                      accept="image/*"
                      style="display: none;"
                      @change="handleCoverUpload"
                    />
                  </div>
                </div>

                <!-- 数据类别 -->
                <div class="form-item">
                  <label class="label required">数据类别</label>
                  <select v-model="formData.category" class="select">
                    <option value="">请选择数据类别</option>
                    <option value="image">图像</option>
                    <option value="text">文本</option>
                    <option value="audio">音频</option>
                    <option value="video">视频</option>
                  </select>
                </div>

                <!-- 数据资源目录 -->
                <div class="form-item">
                  <label class="label required">数据资源目录</label>
                  <select v-model="formData.directory" class="select">
                    <option value="">请选择</option>
                    <option value="public">公开目录</option>
                    <option value="private">私有目录</option>
                    <option value="team">团队目录</option>
                  </select>
                </div>

                <!-- 模板标签 -->
                <div class="form-item">
                  <label class="label required">模板标签</label>
                  <select v-model="formData.templateTag" class="select">
                    <option value="">请选择模板标签</option>
                    <option value="classification">分类</option>
                    <option value="detection">检测</option>
                    <option value="segmentation">分割</option>
                  </select>
                </div>

                <!-- 选择模板 -->
                <div class="form-item">
                  <label class="label required">选择模板</label>

                <!-- 加载中 -->
                <span v-if="loading">加载模板中...</span>

                <!-- 数据加载完成后渲染 select -->
                <select 
                  v-else-if="template.length > 0" 
                  v-model="formData.template" 
                  class="select"
                >
                <option value="">请选择模板</option>
                <option v-for="tag in template" :key="tag.id" :value="tag.id">
                {{ tag.name }}
                </option>
                </select>

  <!-- 无数据 -->
  <span v-else>暂无模板数据</span>
</div>

                <!-- 数据可见范围 -->
                <div class="form-item">
                  <label class="label required">数据可见范围</label>
                  <select v-model="formData.visibility" class="select">
                    <option value="">请选择数据可见范围</option>
                    <option value="public">公开</option>
                    <option value="private">私有</option>
                    <option value="internal">内部</option>
                  </select>
                </div>

                <!-- 提交按钮 -->
                <div class="form-actions">
                  <button type="submit" class="btn-submit">提交</button>
                </div>
            </form>
        </div>
    </div>
</template>
<script>
import Navbar from '../components/Navbar.vue';
import TemplateNavbar from '../components/TemplateNavbar.vue';
import axios from 'axios';

export default {
    name: "CreateDataset",
    components: {
        Navbar,
        TemplateNavbar
    },
    data() {
    return {
      componentKey: 1,
      formData: {
        name: '',
        description: '',
        category: '',
        directory: '',
        templateTag: '',
        template: '',
        selectedDirectory: '', // 绑定下拉框选中的值
        visibility: '',
      },  
      template: [],  
      loading: false,     // 可选：加载状态
      error: null,        // 可选：错误信息
    };
  },
  async mounted() {
    await this.fetchTemplate(); 
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
          break;
        default:
          this.$message.info('功能开发中...');
      }
    },
    
    async fetchTemplate(){
        try {
        const response = await axios.get('/api/basemodule/moduleparent/list');

        // ✅ 使用正确的字段名
        this.template = response.data.module_list;

        console.log('加载的模板:', this.template);
      } catch (error) {
        console.error('请求失败:', error);
        alert('无法连接到后端服务');
      }
    },
    handleUploadClick() {
      this.$refs.coverFileInput?.click();
    },
    handleCoverUpload(event) {
      const file = event.target.files[0];
      if (file) {
        console.log('上传的文件:', file);
        // 可以在这里添加预览逻辑或上传到服务器
      }
    },
    handleSubmit() {
      // 提交前可做简单校验
      if (!this.formData.name.trim()) {
        alert('请填写数据集名称');
        return;
      }
      if (!this.formData.description.trim()) {
        alert('请填写数据集摘要');
        return;
      }
      console.log('提交数据:', this.formData);
      // 调用 API 提交数据
      // axios.post('/api/dataset', this.formData)
    },
  },
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

@keyframes gradientSlide {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

.createdataset-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7474bf 100%);
  background-size: 200% 200%;
  animation: gradientShift 15s ease infinite;
  padding-top: 140px;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.createdataset-page::before {
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
}

/* 自定义外层滚动条样式 */
.createdataset-page::-webkit-scrollbar {
  width: 12px;
}

.createdataset-page::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 6px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.createdataset-page::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.createdataset-page::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
}

.create-dataset-page {
  max-width: 1000px;
  margin: 20px auto 120px auto;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15),
              0 0 0 1px rgba(255, 255, 255, 0.3) inset;
  position: relative;
  z-index: 1;
  animation: fadeInScale 0.6s ease;
}

.create-dataset-page::before {
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

.create-dataset-page::after {
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
  background-size: 200% 100%;
  animation: gradientSlide 3s linear infinite;
  border-radius: 0 0 20px 20px;
}

.page-title {
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 35px;
  letter-spacing: 0.5px;
  position: relative;
  padding-bottom: 15px;
}

.page-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
  animation: pulse-glow 2s infinite;
}

/* 每个表单项：标签 + 输入区 水平排列 */
.form-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 25px;
  padding: 20px;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.95) 0%, 
    rgba(248, 249, 250, 0.95) 100%);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1),
              0 0 0 1px rgba(102, 126, 234, 0.1) inset;
  border: 2px solid rgba(102, 126, 234, 0.15);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  animation: slideDown 0.6s ease;
}

.form-item:hover {
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2),
              0 0 0 1px rgba(102, 126, 234, 0.2) inset;
  transform: translateY(-2px);
}

.label {
  width: 140px;
  font-weight: 600;
  color: #606266;
  text-align: right;
  padding-right: 20px;
  line-height: 36px;
  font-size: 14px;
}

.label.required::before {
  content: '*';
  color: #F56C6C;
  margin-right: 4px;
  font-weight: 700;
}

/* 输入框、下拉框、文本域等容器 */
.input-group,
.select-wrapper {
  flex: 1;
  position: relative;
}

.input {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 10px;
  font-size: 14px;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.95);
  transition: all 0.3s ease;
}

.input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.textarea {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 10px;
  font-size: 14px;
  resize: vertical;
  min-height: 100px;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.95);
  transition: all 0.3s ease;
  font-family: inherit;
}

.textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.char-count {
  position: absolute;
  bottom: 8px;
  right: 10px;
  font-size: 12px;
  color: #909399;
  pointer-events: none;
  font-weight: 500;
}

.upload-container {
  width: 226px;
  height: 170px;
  border: 2px dashed rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  background: linear-gradient(135deg, 
    rgba(249, 249, 249, 0.9) 0%, 
    rgba(245, 247, 250, 0.9) 100%);
}

.upload-container:hover {
  border-color: #667eea;
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.05) 0%, 
    rgba(118, 75, 162, 0.05) 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
}

.upload-icon {
  width: 40px;
  height: 40px;
  margin-bottom: 10px;
}

.upload-text {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  margin-top: 8px;
}

.upload-subtext {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.select {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 10px;
  font-size: 14px;
  background-color: rgba(255, 255, 255, 0.95);
  box-sizing: border-box;
  transition: all 0.3s ease;
  cursor: pointer;
}

.select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.select:disabled {
  background-color: rgba(245, 247, 250, 0.8);
  cursor: not-allowed;
  border-color: rgba(102, 126, 234, 0.1);
}

.form-actions {
  text-align: center;
  margin-top: 40px;
  padding-top: 20px;
}

.btn-submit {
  padding: 12px 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  letter-spacing: 0.5px;
}

.btn-submit:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

</style>