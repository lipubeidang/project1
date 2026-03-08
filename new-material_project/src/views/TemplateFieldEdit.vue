<template>
  <div class="template-field-edit">
    <!-- 顶部导航 -->
    <Navbar />
    <TemplateNavbar @nav-action="handleNavAction" @audit-action="handleAuditAction" />

    <!-- 主容器 -->
    <div class="container">
      <h2 class="title">模板字段修改</h2>
      
      <!-- 模板信息显示 -->
      <div class="template-info">
        <div class="info-item">
          <span class="label">模板名称：</span>
          <span class="value">{{ templateName || '未知模板' }}</span>
        </div>
        <div class="info-item">
          <span class="label">模板ID：</span>
          <span class="value">{{ templateId }}</span>
        </div>
      </div>

      <!-- 字段列表 -->
      <div class="fields-section" v-loading="loading">
        <h3 class="section-title">字段列表</h3>
        
        <!-- 对象区域 -->
        <div v-if="fieldsBySection.object && fieldsBySection.object.length > 0" class="field-group">
          <h4 class="group-title">对象区域</h4>
          <div class="field-list">
            <div 
              v-for="(field, index) in fieldsBySection.object" 
              :key="`object_${index}`"
              class="field-item"
              :class="{ 'enum-field': getFieldType(field) === '枚举型' }"
            >
              <div class="field-info">
                <span class="field-name">{{ getFieldName(field) }}</span>
                <span class="field-type">{{ getFieldType(field) }}</span>
              </div>
              <div class="field-actions">
                <el-button 
                  v-if="getFieldType(field) === '枚举型'"
                  type="primary" 
                  size="small"
                  @click="editEnumField(field, 'object', index)"
                >
                  编辑枚举
                </el-button>
                <el-button 
                  v-else
                  type="info" 
                  size="small"
                  disabled
                >
                  暂不支持
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作区域 -->
        <div v-if="fieldsBySection.operation && fieldsBySection.operation.length > 0" class="field-group">
          <h4 class="group-title">操作区域</h4>
          <div class="field-list">
            <div 
              v-for="(field, index) in fieldsBySection.operation" 
              :key="`operation_${index}`"
              class="field-item"
              :class="{ 'enum-field': getFieldType(field) === '枚举型' }"
            >
              <div class="field-info">
                <span class="field-name">{{ getFieldName(field) }}</span>
                <span class="field-type">{{ getFieldType(field) }}</span>
              </div>
              <div class="field-actions">
                <el-button 
                  v-if="getFieldType(field) === '枚举型'"
                  type="primary" 
                  size="small"
                  @click="editEnumField(field, 'operation', index)"
                >
                  编辑枚举
                </el-button>
                <el-button 
                  v-else
                  type="info" 
                  size="small"
                  disabled
                >
                  暂不支持
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 结果区域 -->
        <div v-if="fieldsBySection.result && fieldsBySection.result.length > 0" class="field-group">
          <h4 class="group-title">结果区域</h4>
          <div class="field-list">
            <div 
              v-for="(field, index) in fieldsBySection.result" 
              :key="`result_${index}`"
              class="field-item"
              :class="{ 'enum-field': getFieldType(field) === '枚举型' }"
            >
              <div class="field-info">
                <span class="field-name">{{ getFieldName(field) }}</span>
                <span class="field-type">{{ getFieldType(field) }}</span>
              </div>
              <div class="field-actions">
                <el-button 
                  v-if="getFieldType(field) === '枚举型'"
                  type="primary" 
                  size="small"
                  @click="editEnumField(field, 'result', index)"
                >
                  编辑枚举
                </el-button>
                <el-button 
                  v-else
                  type="info" 
                  size="small"
                  disabled
                >
                  暂不支持
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 无字段提示 -->
        <div v-if="!hasAnyFields" class="no-fields">
          <p>该模板暂无字段信息</p>
        </div>
      </div>

      <!-- 返回按钮 -->
      <div class="action-buttons">
        <el-button @click="goBack">返回</el-button>
      </div>
    </div>

    <!-- 枚举编辑对话框 -->
    <el-dialog
      :visible.sync="enumEditDialogVisible"
      :title="`编辑枚举字段: ${currentEditField.columnName}`"
      width="60%"
      :before-close="handleEnumDialogClose"
    >
      <div class="enum-edit-content">
        <div class="field-info-display">
          <p><strong>字段名称：</strong>{{ getFieldName(currentEditField) }}</p>
          <p><strong>所属区域：</strong>{{ currentEditSection }}</p>
          <p><strong>字段类型：</strong>{{ getFieldType(currentEditField) }}</p>
        </div>

        <h4>枚举选项配置</h4>
        <div class="enum-help-text">
          <p><strong>说明：</strong></p>
          <p>• <strong>选项标签</strong>：自动按顺序生成（A、B、C、D...），不可修改</p>
          <p>• <strong>选项内容</strong>：填写选项的具体含义（如：固体、液体、气体等）</p>
          <p>• <strong>显示效果</strong>：如果有内容，显示为"A: 固体"；如果无内容，显示为"A"</p>
        </div>
        <div class="enum-options">
          <div 
            v-for="(option, index) in enumOptions" 
            :key="index"
            class="enum-option-item"
          >
            <div class="option-label">
              {{ option.label }}
            </div>
            <el-input
              v-model="option.value"
              placeholder="请输入选项内容（如：固体、液体等）"
              style="width: 300px; margin-right: 10px;"
            />
            <el-button 
              type="danger" 
              size="small"
              @click="removeEnumOption(index)"
              :disabled="enumOptions.length <= 1"
            >
              删除
            </el-button>
          </div>
        </div>

        <div class="enum-actions">
          <el-button type="success" @click="addEnumOption">添加选项</el-button>
        </div>
      </div>

      <span slot="footer" class="dialog-footer">
        <el-button @click="handleEnumDialogClose">取 消</el-button>
        <el-button type="primary" @click="saveEnumConfig">保 存</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import TemplateNavbar from '../components/TemplateNavbar.vue';
import { getEnumConfig, saveEnumConfig } from '@/utils/enumStorage';

export default {
  name: 'TemplateFieldEdit',
  components: {
    Navbar,
    TemplateNavbar
  },
  data() {
    return {
      templateId: '',
      templateName: '',
      loading: false,
      fieldsBySection: {
        object: [],
        operation: [],
        result: []
      },
      enumEditDialogVisible: false,
      currentEditField: {},
      currentEditSection: '',
      currentEditIndex: -1,
      enumOptions: []
    }
  },
  computed: {
    hasAnyFields() {
      return (this.fieldsBySection.object && this.fieldsBySection.object.length > 0) ||
             (this.fieldsBySection.operation && this.fieldsBySection.operation.length > 0) ||
             (this.fieldsBySection.result && this.fieldsBySection.result.length > 0);
    }
  },
  async mounted() {
    // 从路由参数获取模板信息
    this.templateId = this.$route.params.templateId;
    this.templateName = this.$route.params.templateName;
    
    console.log('页面加载，模板参数:', {
      templateId: this.templateId,
      templateName: this.templateName
    });
    
    if (!this.templateId) {
      this.$message.error('缺少模板ID参数');
      this.goBack();
      return;
    }
    
    await this.loadFieldInfo();
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
    
    // 获取字段名称（尝试多种可能的属性名）
    getFieldName(field) {
      return field.columnName || field.column_name || field.fieldName || field.name || field.field_name || '未知字段';
    },
    
    // 获取字段类型（尝试多种可能的属性名）
    getFieldType(field) {
      const type = field.columnContribution || field.column_contribution || field.contribution || field.type || '';
      return type || '未知类型';
    },
    
    // 生成字母标签（A, B, C, D, ...）
    generateLabel(index) {
      return String.fromCharCode(65 + index); // 65 是 'A' 的 ASCII 码
    },
    
    // 重新生成所有选项的标签
    regenerateLabels() {
      this.enumOptions.forEach((option, index) => {
        option.label = this.generateLabel(index);
      });
    },
    
    async loadFieldInfo() {
      this.loading = true;
      try {
        console.log('加载模板字段信息，模板ID:', this.templateId);
        
        const response = await this.$request.get(`/basemodule/moduledata/getColumnInfo/${this.templateId}`);
        
        if (response.data && response.data.code === 0) {
          const columnInfo = response.data.columnInfo || response.data.data || {};
          
          this.fieldsBySection = {
            object: columnInfo.object || [],
            operation: columnInfo.operation || [],
            result: columnInfo.result || []
          };
          
          console.log('字段信息加载成功:', this.fieldsBySection);
          
          // 调试：打印字段结构
          if (this.fieldsBySection.object && this.fieldsBySection.object.length > 0) {
            console.log('对象区域第一个字段的结构:', this.fieldsBySection.object[0]);
            console.log('对象区域第一个字段的所有属性:', Object.keys(this.fieldsBySection.object[0]));
          }
        } else {
          throw new Error(response.data.msg || '获取字段信息失败');
        }
      } catch (error) {
        console.error('加载字段信息失败:', error);
        this.$message.error('加载字段信息失败: ' + (error.message || '请重试'));
      } finally {
        this.loading = false;
      }
    },
    
    async editEnumField(field, section, index) {
      console.log('编辑枚举字段:', field, section, index);
      
      this.currentEditField = field;
      this.currentEditSection = section;
      this.currentEditIndex = index;
      
      // 加载现有的枚举配置
      try {
        const enumConfig = await getEnumConfig(this.templateName || this.templateId);
        console.log('当前枚举配置:', enumConfig);
        
        // 查找该字段的枚举配置
        let fieldEnumOptions = [];
        if (enumConfig && enumConfig[section]) {
          const sectionConfig = enumConfig[section];
          
          // 尝试多种键名查找配置
          const fieldName = this.getFieldName(field);
          const possibleKeys = [
            `field_${index}_${fieldName}`,
            `name_${fieldName}`,
            fieldName
          ];
          
          for (const key of possibleKeys) {
            if (sectionConfig[key] && sectionConfig[key].options) {
              fieldEnumOptions = sectionConfig[key].options;
              console.log(`找到字段 ${fieldName} 的枚举配置:`, fieldEnumOptions);
              break;
            }
          }
        }
        
        // 如果没有找到配置，提供默认选项
        if (fieldEnumOptions.length === 0) {
          fieldEnumOptions = [
            { label: 'A', value: '' },
            { label: 'B', value: '' }
          ];
          console.log('未找到现有配置，使用默认选项');
        }
        
        this.enumOptions = JSON.parse(JSON.stringify(fieldEnumOptions)); // 深拷贝
        
        // 确保标签按顺序正确（A、B、C、D...）
        this.regenerateLabels();
        this.enumEditDialogVisible = true;
        
      } catch (error) {
        console.error('加载枚举配置失败:', error);
        this.$message.error('加载枚举配置失败');
      }
    },
    
    addEnumOption() {
      const newIndex = this.enumOptions.length;
      this.enumOptions.push({
        label: this.generateLabel(newIndex),
        value: ''
      });
    },
    
    removeEnumOption(index) {
      if (this.enumOptions.length > 1) {
        this.enumOptions.splice(index, 1);
        // 删除后重新生成所有标签，保持 A、B、C、D 的顺序
        this.regenerateLabels();
      }
    },
    
    async saveEnumConfig() {
      // 验证和处理枚举选项
      for (let i = 0; i < this.enumOptions.length; i++) {
        const option = this.enumOptions[i];
        
        // 确保标签正确（自动生成）
        option.label = this.generateLabel(i);
        
        // 如果内容为空，使用标签作为值
        if (!option.value || option.value.trim() === '') {
          option.value = option.label;
        }
      }
      
      try {
        // 获取现有配置
        const templateKey = this.templateName || this.templateId;
        let existingConfig = await getEnumConfig(templateKey) || {};
        
        // 确保区域配置存在
        if (!existingConfig[this.currentEditSection]) {
          existingConfig[this.currentEditSection] = {};
        }
        
        // 保存字段的枚举配置
        const fieldName = this.getFieldName(this.currentEditField);
        const fieldKey = `field_${this.currentEditIndex}_${fieldName}`;
        existingConfig[this.currentEditSection][fieldKey] = {
          fieldName: fieldName,
          options: JSON.parse(JSON.stringify(this.enumOptions))
        };
        
        console.log('保存枚举配置:', existingConfig);
        
        // 保存到存储
        await saveEnumConfig(templateKey, existingConfig);
        
        this.$message.success('枚举配置保存成功！');
        this.enumEditDialogVisible = false;
        
      } catch (error) {
        console.error('保存枚举配置失败:', error);
        this.$message.error('保存枚举配置失败: ' + (error.message || '请重试'));
      }
    },
    
    handleEnumDialogClose() {
      this.enumEditDialogVisible = false;
      this.currentEditField = {};
      this.currentEditSection = '';
      this.currentEditIndex = -1;
      this.enumOptions = [];
    },
    
    goBack() {
      this.$router.go(-1);
    }
  }
}
</script>

<style scoped>
.template-field-edit {
  min-height: 100vh;
  background: #f5f7fa;
  padding-top: 160px;
}

.container {
  width: 90%;
  max-width: 1200px;
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

.template-info {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  border: 1px solid #e9ecef;
}

.info-item {
  display: flex;
  margin-bottom: 10px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item .label {
  font-weight: 500;
  color: #495057;
  min-width: 100px;
}

.info-item .value {
  color: #212529;
  font-weight: 600;
}

.fields-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
}

.field-group {
  margin-bottom: 30px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.group-title {
  background: #667eea;
  color: white;
  padding: 12px 20px;
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.field-list {
  padding: 0;
}

.field-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.field-item:last-child {
  border-bottom: none;
}

.field-item:hover {
  background-color: #f8f9fa;
}

.field-item.enum-field {
  background-color: #f0f8ff;
}

.field-item.enum-field:hover {
  background-color: #e6f3ff;
}

.field-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field-name {
  font-weight: 500;
  font-size: 14px;
  color: #333;
}

.field-type {
  font-size: 12px;
  color: #666;
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 12px;
  align-self: flex-start;
}

.field-actions {
  display: flex;
  gap: 10px;
}

.no-fields {
  text-align: center;
  padding: 40px;
  color: #666;
}

.action-buttons {
  text-align: center;
  margin-top: 30px;
}

/* 枚举编辑对话框样式 */
.enum-edit-content {
  padding: 20px 0;
}

.field-info-display {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.field-info-display p {
  margin: 5px 0;
  color: #495057;
}

.enum-help-text {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
  border-left: 4px solid #007bff;
}

.enum-help-text p {
  margin: 5px 0;
  font-size: 13px;
  color: #495057;
}

.enum-help-text p:first-child {
  font-weight: bold;
  color: #212529;
}

.enum-options {
  margin: 20px 0;
}

.enum-option-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.option-label {
  width: 40px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #007bff;
  color: white;
  font-weight: bold;
  border-radius: 4px;
  margin-right: 10px;
  font-size: 14px;
}

.enum-actions {
  text-align: center;
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .field-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .field-actions {
    align-self: stretch;
    justify-content: flex-end;
  }
  
  .enum-option-item {
    flex-direction: column;
    gap: 10px;
  }
  
  .enum-option-item .el-input {
    width: 100% !important;
  }
}
</style>
