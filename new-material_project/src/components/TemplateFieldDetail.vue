<template>
  <el-dialog
    title="模版字段详情"
    :visible="dialogVisible"
    @update:visible="updateVisible"
    width="80%"
    :before-close="handleClose"
    :close-on-click-modal="false"
    :modal="false"
    :append-to-body="true"
    :lock-scroll="false"
    :close-on-press-escape="true"
    :modal-append-to-body="false"
    class="template-field-dialog"
  >
    <div class="template-field-detail">
      <!-- 模版基本信息 -->
      <div class="template-basic-info">
        <div class="info-header">
          <i class="el-icon-s-order"></i>
          <h3>{{ templateInfo.name || '模版详情' }}</h3>
        </div>
        <div class="info-content">
          <div class="info-row">
            <div class="info-item">
              <i class="el-icon-user"></i>
              <span><strong>创建者：</strong>{{ templateInfo.creator || '未知' }}</span>
            </div>
            <div class="info-item">
              <i class="el-icon-time"></i>
              <span><strong>创建时间：</strong>{{ formatDate(templateInfo.createTime) }}</span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item full-width">
              <i class="el-icon-document"></i>
              <span><strong>描述：</strong>{{ templateInfo.description || '暂无描述' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 字段信息展示 -->
      <div class="fields-container">
        <!-- 对象字段 -->
        <div class="field-section">
          <div class="section-header">
            <i class="el-icon-files"></i>
            <h4>对象字段</h4>
            <span class="field-count">{{ fields.object.length }} 个字段</span>
          </div>
          <div class="fields-grid">
            <div 
              v-for="(field, index) in fields.object" 
              :key="field.id || index"
              class="field-item"
            >
              <div class="field-icon">
                <i class="el-icon-document"></i>
              </div>
              <div class="field-content">
                <div class="field-info">
                  <label>字段名称</label>
                  <span class="field-value">{{ field.columnName }}</span>
                </div>
                <div class="field-info">
                  <label>字段类型</label>
                  <span class="field-type">{{ field.columnContribution }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="fields.object.length === 0" class="empty-tip">
            <i class="el-icon-folder-opened"></i>
            <p>暂无对象字段</p>
          </div>
        </div>

        <!-- 操作字段 -->
        <div class="field-section">
          <div class="section-header">
            <i class="el-icon-setting"></i>
            <h4>操作字段</h4>
            <span class="field-count">{{ fields.operation.length }} 个字段</span>
          </div>
          <div class="fields-grid">
            <div 
              v-for="(field, index) in fields.operation" 
              :key="field.id || index"
              class="field-item"
            >
              <div class="field-icon">
                <i class="el-icon-s-operation"></i>
              </div>
              <div class="field-content">
                <div class="field-info">
                  <label>字段名称</label>
                  <span class="field-value">{{ field.columnName }}</span>
                </div>
                <div class="field-info">
                  <label>字段类型</label>
                  <span class="field-type">{{ field.columnContribution }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="fields.operation.length === 0" class="empty-tip">
            <i class="el-icon-folder-opened"></i>
            <p>暂无操作字段</p>
          </div>
        </div>

        <!-- 结果字段 -->
        <div class="field-section">
          <div class="section-header">
            <i class="el-icon-data-analysis"></i>
            <h4>结果字段</h4>
            <span class="field-count">{{ fields.result.length }} 个字段</span>
          </div>
          <div class="fields-grid">
            <div 
              v-for="(field, index) in fields.result" 
              :key="field.id || index"
              class="field-item"
            >
              <div class="field-icon">
                <i class="el-icon-s-data"></i>
              </div>
              <div class="field-content">
                <div class="field-info">
                  <label>字段名称</label>
                  <span class="field-value">{{ field.columnName }}</span>
                </div>
                <div class="field-info">
                  <label>字段类型</label>
                  <span class="field-type">{{ field.columnContribution }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="fields.result.length === 0" class="empty-tip">
            <i class="el-icon-folder-opened"></i>
            <p>暂无结果字段</p>
          </div>
        </div>
      </div>
    </div>

    <span slot="footer" class="dialog-footer">
      <el-button @click="handleClose" class="close-btn">关闭</el-button>
      <el-button 
        v-if="isEditable && isPendingTemplate" 
        type="primary" 
        @click="approveTemplate"
        :loading="approving"
        class="approve-btn"
      >
        <i class="el-icon-check"></i>
        审核通过
      </el-button>
    </span>
  </el-dialog>
</template>

<script>
export default {
  name: 'TemplateFieldDetail',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    templateInfo: {
      type: Object,
      default: () => ({})
    },
    templateFields: {
      type: Object,
      default: () => ({
        object: [],
        operation: [],
        result: []
      })
    },
    isEditable: {
      type: Boolean,
      default: false
    },
    isPendingTemplate: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      fields: {
        object: [],
        operation: [],
        result: []
      },
      approving: false,
      nextId: 1
    }
  },
  computed: {
    dialogVisible() {
      return this.visible;
    }
  },
  watch: {
    templateFields: {
      handler(newFields) {
        if (newFields) {
          this.fields = {
            object: [...(newFields.object || [])],
            operation: [...(newFields.operation || [])],
            result: [...(newFields.result || [])]
          };
          
          // 计算下一个ID
          let maxId = 0;
          Object.values(this.fields).forEach(fieldArray => {
            fieldArray.forEach(field => {
              if (field.id && field.id > maxId) {
                maxId = field.id;
              }
            });
          });
          this.nextId = maxId + 1;
        }
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    updateVisible(value) {
      this.$emit('update:visible', value);
    },
    handleClose() {
      this.updateVisible(false);
    },
    async approveTemplate() {
      try {
        this.approving = true;
        
        // 验证必要字段
        if (!this.templateInfo.id) {
          throw new Error('模版ID不能为空');
        }
        
        // 构建createtable接口的请求参数
        // 后端 DynamicTableService 期望的数据结构包含 columns 对象
        const normalizeField = (field) => ({
          ...field,
          columnType: field.columnType || field.type || ''
        });
        const objectArray = (this.fields.object || []).map(normalizeField);
        const operationArray = (this.fields.operation || []).map(normalizeField);
        const resultArray = (this.fields.result || []).map(normalizeField);

        const requestData = {
          moduleId: this.templateInfo.id,
          name: this.templateInfo.name ? this.templateInfo.name.toLowerCase().replace(/\s+/g, '_') : 'template',
          objectArray,
          operationArray,
          resultArray,
          columns: {
            object: objectArray,
            operation: operationArray,
            result: resultArray
          }
        };
        
        console.log('发送审核数据:', requestData);
        console.log('对象字段数量:', objectArray.length);
        console.log('操作字段数量:', operationArray.length);
        console.log('结果字段数量:', resultArray.length);
        
        // 调用createtable接口
        const response = await this.$request.post('http://localhost:8083/basemodule/process/createtable', requestData);
        
        console.log('审核接口响应:', response);
        
        if (response.data && response.data.code === 0) {
          const approvedTemplate = {
            ...this.templateInfo,
            state: 1
          };
          
          this.$message.success('模版审核通过，数据表创建成功');
          this.$emit('template-approved', approvedTemplate);
          this.handleClose();
        } else {
          throw new Error(response.data.msg || '创建数据表失败');
        }
      } catch (error) {
        console.error('审核通过失败:', error);
        console.error('错误详情:', error.response?.data);
        this.$message.error('审核通过失败: ' + (error.response?.data?.msg || error.message));
      } finally {
        this.approving = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '未知';
      try {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
      } catch (error) {
        return dateString;
      }
    }
  }
}
</script>

<style scoped>
.template-field-detail {
  max-height: 70vh;
  overflow-y: auto;
  /* 🚀 滚动性能优化 - 使用GPU加速 */
  -webkit-overflow-scrolling: touch;
  scroll-behavior: smooth;
  /* 强制GPU硬件加速 */
  -webkit-transform: translate3d(0, 0, 0);
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  /* 优化渲染性能 */
  contain: layout style paint;
}

/* 滚动条样式 */
.template-field-detail::-webkit-scrollbar {
  width: 10px;
}

.template-field-detail::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 5px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  /* GPU加速滚动条 */
  transform: translate3d(0, 0, 0);
}

.template-field-detail::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
  /* 简化阴影提升性能 */
  box-shadow: 0 0 8px rgba(102, 126, 234, 0.4);
}

.template-field-detail::-webkit-scrollbar-track {
  background: rgba(245, 247, 250, 0.5);
  border-radius: 5px;
}

.template-basic-info {
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.98);
  /* 🚀 性能优化：移除backdrop-filter（性能杀手） */
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  border-radius: 16px;
  /* 简化阴影提升性能 */
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  border: 2px solid rgba(102, 126, 234, 0.15);
  overflow: hidden;
  /* 🚀 优化动画时长到0.25s（60fps黄金时长） */
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), 
              box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeIn 0.3s ease;
  /* GPU硬件加速 */
  -webkit-transform: translate3d(0, 0, 0);
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  contain: layout style paint;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.template-basic-info:hover {
  /* 简化阴影提升性能 */
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.22);
  border-color: rgba(102, 126, 234, 0.3);
  will-change: transform, box-shadow;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 25px;
  background: linear-gradient(135deg, 
      rgba(102, 126, 234, 0.08) 0%, 
      rgba(118, 75, 162, 0.08) 100%);
  border-bottom: 2px solid rgba(102, 126, 234, 0.15);
}

.info-header i {
  font-size: 28px;
  color: #667eea;
}

.info-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
}

.info-content {
  padding: 20px 25px;
}

.info-row {
  display: flex;
  gap: 30px;
  margin-bottom: 12px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  /* 🚀 优化动画时长 */
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), 
              box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  /* GPU硬件加速 */
  -webkit-transform: translate3d(0, 0, 0);
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

.info-item:hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateX(3px) translate3d(0, 0, 0);
  box-shadow: 0 3px 10px rgba(102, 126, 234, 0.15);
  will-change: transform;
}

.info-item.full-width {
  flex: 1 1 100%;
}

.info-item i {
  font-size: 18px;
  color: #667eea;
}

.info-item span {
  color: #606266;
  font-size: 14px;
}

.info-item strong {
  color: #667eea;
  margin-right: 5px;
}

.fields-container {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.field-section {
  background: rgba(255, 255, 255, 0.98);
  /* 🚀 性能优化：移除backdrop-filter */
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  border-radius: 16px;
  /* 简化阴影提升性能 */
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  border: 2px solid rgba(102, 126, 234, 0.15);
  overflow: hidden;
  /* 🚀 优化动画时长到0.25s */
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), 
              box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeIn 0.3s ease;
  /* GPU硬件加速 */
  -webkit-transform: translate3d(0, 0, 0);
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  contain: layout style paint;
}

.field-section:hover {
  /* 简化阴影提升性能 */
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.22);
  transform: translateY(-2px) translate3d(0, 0, 0);
  border-color: rgba(102, 126, 234, 0.3);
  will-change: transform, box-shadow;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 25px;
  background: linear-gradient(135deg, 
      rgba(102, 126, 234, 0.08) 0%, 
      rgba(118, 75, 162, 0.08) 100%);
  border-bottom: 2px solid rgba(102, 126, 234, 0.15);
}

.section-header i {
  font-size: 22px;
  color: #667eea;
}

.section-header h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
  flex: 1;
}

.field-count {
  font-size: 13px;
  color: #909399;
  background: rgba(255, 255, 255, 0.8);
  padding: 4px 12px;
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.2);
  font-weight: 600;
}

.fields-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: 15px;
  padding: 20px;
}

.field-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  /* 🚀 优化动画时长到0.25s */
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), 
              box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  animation: slideIn 0.25s ease;
  /* GPU硬件加速 */
  -webkit-transform: translate3d(0, 0, 0);
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  contain: layout style paint;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.field-item:hover {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-3px) translate3d(0, 0, 0);
  /* 简化阴影提升性能 */
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.22);
  will-change: transform, box-shadow;
}

.field-icon {
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, 
      rgba(102, 126, 234, 0.1) 0%, 
      rgba(118, 75, 162, 0.1) 100%);
  border-radius: 10px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  /* 🚀 优化动画时长 */
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  /* GPU硬件加速 */
  -webkit-transform: translate3d(0, 0, 0);
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

.field-item:hover .field-icon {
  background: linear-gradient(135deg, 
      rgba(102, 126, 234, 0.2) 0%, 
      rgba(118, 75, 162, 0.2) 100%);
  border-color: rgba(102, 126, 234, 0.4);
  transform: rotate(10deg) scale(1.1) translate3d(0, 0, 0);
  will-change: transform;
}

.field-icon i {
  font-size: 22px;
  color: #667eea;
}

.field-content {
  flex: 1;
  display: flex;
  gap: 20px;
}

.field-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-info label {
  font-weight: 600;
  color: #909399;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.field-value {
  color: #303133;
  font-size: 15px;
  font-weight: 600;
  padding: 6px 0;
}

.field-type {
  color: #667eea;
  font-size: 14px;
  font-weight: 500;
  padding: 4px 10px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 6px;
  display: inline-block;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.empty-tip {
  padding: 60px 20px;
  text-align: center;
  color: #909399;
}

.empty-tip i {
  font-size: 48px;
  color: #dcdfe6;
  margin-bottom: 15px;
}

.empty-tip p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .fields-grid {
    grid-template-columns: 1fr;
  }
  
  .field-content {
    flex-direction: column;
    gap: 12px;
  }
  
  .info-row {
    flex-direction: column;
    gap: 12px;
  }
}
</style>

<style>
/* 弹窗基础样式 */
.template-field-dialog {
  margin-top: 5vh !important;
  margin-bottom: 5vh !important;
}

.template-field-dialog .el-dialog {
  background: rgba(255, 255, 255, 0.98);
  /* 🚀 性能优化：移除backdrop-filter（性能杀手） */
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  border-radius: 20px;
  /* 简化阴影提升性能 */
  box-shadow: 0 20px 50px rgba(102, 126, 234, 0.25);
  border: 2px solid rgba(102, 126, 234, 0.2);
  /* GPU硬件加速 */
  -webkit-transform: translate3d(0, 0, 0);
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

.template-field-dialog .el-dialog__header {
  background: linear-gradient(135deg, 
      rgba(102, 126, 234, 0.05) 0%, 
      rgba(118, 75, 162, 0.05) 100%);
  border-radius: 20px 20px 0 0;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
  padding: 25px 30px;
}

.template-field-dialog .el-dialog__title {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
}

.template-field-dialog .el-dialog__body {
  padding: 25px 30px;
  overflow-y: auto;
  max-height: calc(90vh - 180px);
  /* 🚀 滚动性能优化 - 使用GPU加速 */
  -webkit-overflow-scrolling: touch;
  scroll-behavior: smooth;
  /* 强制GPU硬件加速 */
  -webkit-transform: translate3d(0, 0, 0);
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  contain: layout style paint;
}

.template-field-dialog .el-dialog__footer {
  border-top: 2px solid rgba(102, 126, 234, 0.1);
  padding: 20px 30px;
}

/* 按钮样式 */
.close-btn {
  padding: 10px 24px;
  font-weight: 600;
  border: 2px solid rgba(102, 126, 234, 0.3);
  color: #667eea;
  background: rgba(255, 255, 255, 0.9);
  /* 🚀 优化动画时长 */
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), 
              box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  /* GPU硬件加速 */
  -webkit-transform: translate3d(0, 0, 0);
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

.close-btn:hover {
  background: linear-gradient(135deg, 
      rgba(102, 126, 234, 0.1) 0%, 
      rgba(118, 75, 162, 0.1) 100%);
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px) translate3d(0, 0, 0);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.25);
  will-change: transform;
}

.approve-btn {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  border: none;
  color: white;
  padding: 10px 24px;
  font-weight: 600;
  /* 🚀 优化动画时长 */
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), 
              box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  /* GPU硬件加速 */
  -webkit-transform: translate3d(0, 0, 0);
  transform: translate3d(0, 0, 0);
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

.approve-btn:hover {
  background: linear-gradient(135deg, #85ce61 0%, #67c23a 100%);
  transform: translateY(-2px) translate3d(0, 0, 0);
  box-shadow: 0 6px 20px rgba(103, 194, 58, 0.4);
  will-change: transform;
}

.approve-btn i {
  margin-right: 5px;
}
</style>

