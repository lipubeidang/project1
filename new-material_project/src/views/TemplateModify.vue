<template>
  <div class="upload-data">
    <!-- 顶部导航 -->
    <Navbar />
    <TemplateNavbar @nav-action="handleNavAction" @audit-action="handleAuditAction" />

    <!-- 主容器 -->
    <div class="container">
      <h2 class="title">模版修改</h2>

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

        <!-- 子目录选择 -->
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

        <!-- 修改方式选择 -->
        <div class="form-group">
          <label class="label">修改方式：</label>
          <div class="radio-group">
            <button 
              class="radio-btn" 
              :class="{ active: modifyMode === 'data' }"
              @click="handleDataModifyClick"
              :disabled="!selectedTemplateId"
            >
              修改模板数据
            </button>
            <button 
              class="radio-btn" 
              :class="{ active: modifyMode === 'fields' }"
              @click="handleFieldsModifyClick"
              :disabled="!selectedTemplateId"
            >
              修改模板字段
            </button>
          </div>
        </div>
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
      selectedBigCategory: '',           // 选中的大目录
      parentDirectories: [],             // 父目录列表（保留但不使用）
      childTemplates: [],                // 子模板列表
      selectedParentId: '',              // 选中的父目录ID
      selectedTemplateId: '',            // 选中的模板ID
      loadingParents: false,             // 加载父目录状态（保留但不使用）
      loadingTemplates: false,           // 加载模板状态
      modifyMode: '',                    // 修改方式：'data' 或 'fields'
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
    selectedTemplateName() {
      if (!this.selectedTemplateId || this.childTemplates.length === 0) {
        return '';
      }
      const template = this.childTemplates.find(t => t.id === this.selectedTemplateId);
      return template ? template.name : '';
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
        if (response.data && response.data.code === 0) {
          this.parentDirectories = response.data.module_list || [];
        } else {
          throw new Error(response.data.msg || '获取父目录失败');
        }
      } catch (error) {
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
        if (response.data && response.data.code === 0) {
          this.childTemplates = response.data.moduleList || response.data.module_list || [];
        } else {
          throw new Error(response.data.msg || '获取子模板失败');
        }
      } catch (error) {
        this.$message.error('获取子模板失败: ' + (error.message || '请重试'));
        this.childTemplates = [];
      } finally {
        this.loadingTemplates = false;
      }
    },
    // 修改模板数据
    handleDataModifyClick() {
      if (!this.selectedTemplateId) {
        this.$message.warning('请先选择模板');
        return;
      }
      this.modifyMode = 'data';
      
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
          title: '修改模板内容'
        }
      });
    },
    // 修改模板字段
    handleFieldsModifyClick() {
      if (!this.selectedTemplateId) {
        this.$message.warning('请先选择模板');
        return;
      }
      this.modifyMode = 'fields';
      
      console.log('跳转到字段修改页面，参数:', {
        templateId: this.selectedTemplateId,
        templateName: this.selectedTemplateName
      });
      
      // 跳转到模板字段修改页面
      this.$router.push({
        name: 'TemplateFieldEdit',
        params: {
          templateId: this.selectedTemplateId,
          templateName: this.selectedTemplateName
        }
      });
    }
  },
  async mounted() {
    // 不再需要加载父目录列表，因为使用固定的目录结构
    // await this.fetchParentDirectories();
  }
}
</script>

<style scoped>
@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes glow-pulse {
  0%, 100% {
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
  }
  50% {
    box-shadow: 0 0 35px rgba(102, 126, 234, 0.6);
  }
}

.upload-data {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7474bf 100%);
  background-size: 200% 200%;
  animation: gradientShift 15s ease infinite;
  padding-top: 160px;
  position: relative;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.upload-data::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(139, 92, 246, 0.2) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.container {
  width: 90%;
  max-width: 1100px;
  margin: 40px auto;
  padding: 45px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 12px 50px rgba(0, 0, 0, 0.15),
              0 0 0 1px rgba(255, 255, 255, 0.3) inset;
  border: 2px solid rgba(102, 126, 234, 0.15);
  animation: fadeInScale 0.6s ease;
  position: relative;
  z-index: 1;
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

.title {
  text-align: center;
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 1px;
  position: relative;
  padding-bottom: 15px;
}

.title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
  animation: glow-pulse 2s infinite;
}

.section {
  margin-bottom: 35px;
  padding: 25px;
  background: linear-gradient(135deg, 
    rgba(248, 249, 250, 0.8) 0%, 
    rgba(255, 255, 255, 0.8) 100%);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 2px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
}

.section:hover {
  border-color: rgba(102, 126, 234, 0.25);
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.15);
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.15);
}

.form-group {
  display: flex;
  align-items: center;
  margin-bottom: 22px;
  gap: 15px;
  transition: all 0.3s ease;
}

.form-group:hover {
  transform: translateX(5px);
}

.label {
  min-width: 150px;
  font-weight: 600;
  color: #667eea;
  text-align: right;
  padding-right: 15px;
  font-size: 15px;
}

.required::before {
  content: '*';
  color: #f56c6c;
  margin-right: 5px;
  font-weight: 700;
  font-size: 16px;
}

.select {
  flex: 1;
  padding: 12px 15px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  outline: none;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.select:hover {
  border-color: rgba(102, 126, 234, 0.4);
}

.select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1),
              0 4px 15px rgba(102, 126, 234, 0.2);
  transform: translateY(-1px);
}

.select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: rgba(245, 247, 250, 0.9);
}

.radio-group {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.radio-btn {
  padding: 12px 24px;
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  color: #667eea;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.radio-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.2);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.radio-btn:hover:not(:disabled)::before {
  width: 300px;
  height: 300px;
}

.radio-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.1) 0%, 
    rgba(118, 75, 162, 0.1) 100%);
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

.radio-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(245, 247, 250, 0.9);
  color: #999;
}

.radio-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  transform: scale(1.05);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
  animation: glow-pulse 2s infinite;
}

.radio-btn.active::after {
  content: '✓';
  position: absolute;
  top: -5px;
  right: -5px;
  width: 24px;
  height: 24px;
  background: #67c23a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: white;
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.4);
}

/* 全局滚动条美化 */
::-webkit-scrollbar {
  width: 10px;
}

::-webkit-scrollbar-track {
  background: rgba(245, 247, 250, 0.5);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}
</style>

