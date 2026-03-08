<template>
  <div class="template-create">
    <Navbar @dropdown-action="handleDropdownAction" />
    <TemplateNavbar @nav-action="handleNavAction" @audit-action="handleAuditAction" />
    
    <!-- 步骤导航 -->
    <div class="steps-nav">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="基础设置"></el-step>
        <el-step title="模板设计"></el-step>
      </el-steps>
    </div>

    <!-- 基础设置表单 -->
    <div v-if="currentStep === 0" class="form-container">
      <div class="form-header">
        <h2>创建模板</h2>
      </div>

      <el-form :model="templateForm" :rules="rules" ref="templateForm" label-width="120px" class="template-form">
        <!-- 模板库目录选择 -->
        <el-form-item label="模板库目录" prop="bigCategory">
          <el-select v-model="templateForm.bigCategory" placeholder="请选择大目录" @change="handleBigCategoryChange">
            <el-option label="材料属性" value="big_cat_1"></el-option>
            <el-option label="数据来源" value="big_cat_2"></el-option>
            <el-option label="材料功能" value="big_cat_3"></el-option>
          </el-select>
        </el-form-item>

        <!-- 小目录选择 -->
        <el-form-item label="子目录" prop="parent">
          <el-select v-model="templateForm.parent" placeholder="请先选择大目录" :disabled="!templateForm.bigCategory">
            <el-option 
              v-for="subCat in currentSubCategories" 
              :key="subCat.id" 
              :label="subCat.name" 
              :value="subCat.id">
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 模板名称 -->
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="templateForm.name" placeholder="请输入模板名称"></el-input>
        </el-form-item>

        <!-- 模板说明 -->
        <el-form-item label="模板说明" prop="description">
          <el-input
            type="textarea"
            v-model="templateForm.description"
            :rows="4"
            placeholder="请输入模板说明"
          ></el-input>
        </el-form-item>
      </el-form>

      <!-- 底部按钮 -->
      <div class="form-footer">
        <el-button type="primary" @click="nextStep">下一步</el-button>
      </div>
    </div>

      <!-- 模板设计步骤 -->
    <div v-else-if="currentStep === 1" class="design-container">
      <div class="design-header">
        <h2>模板设计</h2>
      </div>

      <div class="design-content">
        <!-- 字段类型工具栏 -->
        <div class="field-types-toolbar">
          <div class="toolbar-title">字段类型</div>
          <div class="field-types">
            <div v-for="type in fieldTypes" 
                 :key="type.value" 
                 class="field-type-item"
                 draggable="true"
                 @dragstart="handleDragStart($event, type)"
                 :class="type.icon">
              <i :class="type.icon"></i>
              <span>{{ type.label }}</span>
            </div>
          </div>
        </div>

        <!-- 设计区域 -->
        <div class="design-areas">
          <!-- 对象区域 -->
          <div class="design-area">
            <div class="area-header">
              <span class="area-title">对象</span>
              <el-tooltip content="用于描述实验对象的相关属性" placement="top">
                <i class="el-icon-question"></i>
              </el-tooltip>
            </div>
            <div class="area-content"
                 @dragover.prevent
                 @drop="handleDrop($event, 'object')"
                 :class="{ 'drag-over': isDragOver === 'object' }"
                 @dragenter="handleDragEnter($event, 'object')"
                 @dragleave="handleDragLeave">
              <div v-for="(field, index) in objectFields" 
                   :key="index" 
                   class="field-item">
                <div class="field-item-header">
                  <i :class="getFieldIcon(field.type)"></i>
                  <span class="field-name">{{ getFieldTypeLabel(field.type) }}</span>
                  <el-button type="text" 
                           icon="el-icon-delete" 
                           @click="removeField('object', index)">
                  </el-button>
                </div>
                <div class="field-item-body">
                  <el-input v-model="field.name" 
                           size="small"
                           placeholder="请输入字段名称"
                           style="margin-bottom: 10px"></el-input>
                  
                  <!-- 枚举型特殊编辑界面 -->
                  <div v-if="field.type === 'enum'" class="enum-options-container">
                    <div class="enum-section-title">枚举选项</div>
                    <div v-for="(option, optIndex) in field.enumOptions" 
                         :key="optIndex" 
                         class="enum-option-item">
                      <span class="enum-label">{{ option.label }}</span>
                      <el-input v-model="option.value" 
                               size="small"
                               :placeholder="'请输入选项' + option.label + '的值'"
                               class="enum-input"></el-input>
                      <el-button type="text" 
                               icon="el-icon-close" 
                               @click="removeEnumOption(field, optIndex)"
                               class="enum-delete-btn">
                      </el-button>
                    </div>
                    <div class="enum-actions">
                      <el-button size="small" 
                               icon="el-icon-plus" 
                               @click="addEnumOption(field)">
                        添加选项
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="objectFields.length === 0" class="empty-tip">
                拖拽字段到这里
              </div>
            </div>
          </div>

          <!-- 操作区域 -->
          <div class="design-area">
            <div class="area-header">
              <span class="area-title">操作</span>
              <el-tooltip content="用于记录实验操作的相关参数" placement="top">
                <i class="el-icon-question"></i>
              </el-tooltip>
            </div>
            <div class="area-content"
                 @dragover.prevent
                 @drop="handleDrop($event, 'operation')"
                 :class="{ 'drag-over': isDragOver === 'operation' }"
                 @dragenter="handleDragEnter($event, 'operation')"
                 @dragleave="handleDragLeave">
              <div v-for="(field, index) in operationFields" 
                   :key="index" 
                   class="field-item">
                <div class="field-item-header">
                  <i :class="getFieldIcon(field.type)"></i>
                  <span class="field-name">{{ getFieldTypeLabel(field.type) }}</span>
                  <el-button type="text" 
                           icon="el-icon-delete" 
                           @click="removeField('operation', index)">
                  </el-button>
                </div>
                <div class="field-item-body">
                  <el-input v-model="field.name" 
                           size="small"
                           placeholder="请输入字段名称"
                           style="margin-bottom: 10px"></el-input>
                  
                  <!-- 枚举型特殊编辑界面 -->
                  <div v-if="field.type === 'enum'" class="enum-options-container">
                    <div class="enum-section-title">枚举选项</div>
                    <div v-for="(option, optIndex) in field.enumOptions" 
                         :key="optIndex" 
                         class="enum-option-item">
                      <span class="enum-label">{{ option.label }}</span>
                      <el-input v-model="option.value" 
                               size="small"
                               :placeholder="'请输入选项' + option.label + '的值'"
                               class="enum-input"></el-input>
                      <el-button type="text" 
                               icon="el-icon-close" 
                               @click="removeEnumOption(field, optIndex)"
                               class="enum-delete-btn">
                      </el-button>
                    </div>
                    <div class="enum-actions">
                      <el-button size="small" 
                               icon="el-icon-plus" 
                               @click="addEnumOption(field)">
                        添加选项
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="operationFields.length === 0" class="empty-tip">
                拖拽字段到这里
              </div>
            </div>
          </div>

          <!-- 结果区域 -->
          <div class="design-area">
            <div class="area-header">
              <span class="area-title">结果</span>
              <el-tooltip content="用于记录实验结果的相关数据" placement="top">
                <i class="el-icon-question"></i>
              </el-tooltip>
            </div>
            <div class="area-content"
                 @dragover.prevent
                 @drop="handleDrop($event, 'result')"
                 :class="{ 'drag-over': isDragOver === 'result' }"
                 @dragenter="handleDragEnter($event, 'result')"
                 @dragleave="handleDragLeave">
              <div v-for="(field, index) in resultFields" 
                   :key="index" 
                   class="field-item">
                <div class="field-item-header">
                  <i :class="getFieldIcon(field.type)"></i>
                  <span class="field-name">{{ getFieldTypeLabel(field.type) }}</span>
                  <el-button type="text" 
                           icon="el-icon-delete" 
                           @click="removeField('result', index)">
                  </el-button>
                </div>
                <div class="field-item-body">
                  <el-input v-model="field.name" 
                           size="small"
                           placeholder="请输入字段名称"
                           style="margin-bottom: 10px"></el-input>
                  
                  <!-- 枚举型特殊编辑界面 -->
                  <div v-if="field.type === 'enum'" class="enum-options-container">
                    <div class="enum-section-title">枚举选项</div>
                    <div v-for="(option, optIndex) in field.enumOptions" 
                         :key="optIndex" 
                         class="enum-option-item">
                      <span class="enum-label">{{ option.label }}</span>
                      <el-input v-model="option.value" 
                               size="small"
                               :placeholder="'请输入选项' + option.label + '的值'"
                               class="enum-input"></el-input>
                      <el-button type="text" 
                               icon="el-icon-close" 
                               @click="removeEnumOption(field, optIndex)"
                               class="enum-delete-btn">
                      </el-button>
                    </div>
                    <div class="enum-actions">
                      <el-button size="small" 
                               icon="el-icon-plus" 
                               @click="addEnumOption(field)">
                        添加选项
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="resultFields.length === 0" class="empty-tip">
                拖拽字段到这里
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="design-footer">
        <el-button @click="prevStep">上一步</el-button>
        <el-button type="primary" @click="submitTemplate">完成</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue'
import TemplateNavbar from '../components/TemplateNavbar.vue'
import { saveTemplateEnumConfig, loadTemplateEnumConfig, getEnumConfig } from '@/utils/enumStorage'

export default {
  name: 'TemplateCreate',
  components: {
    Navbar,
    TemplateNavbar
  },
  data() {
    // 检查是否有暂存的表单数据
    const savedFormData = sessionStorage.getItem('templateFormData');
    const initialForm = savedFormData ? JSON.parse(savedFormData) : {
      name: '',
      parent: null,  // 改为null，与el-select的默认值保持一致
      bigCategory: '',
      description: '',
      creator: ''
    };
    
    return {
      currentStep: 0,
      templateForm: initialForm,
      isDragOver: null,
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
      currentSubCategories: [],
      fieldTypes: [
        { label: '字符串型', value: 'string', icon: 'el-icon-edit-outline' },
        { label: '数值型', value: 'number', icon: 'el-icon-tickets' },
        { label: '浮点型', value: 'float', icon: 'el-icon-coin' },
        { label: '范围型', value: 'range', icon: 'el-icon-sort' },
        { label: '候选型', value: 'select', icon: 'el-icon-menu' },
        { label: '枚举型', value: 'enum', icon: 'el-icon-s-operation' },
        { label: '图片型', value: 'image', icon: 'el-icon-picture' },
        { label: '文件型', value: 'file', icon: 'el-icon-document' },
        { label: '数组型', value: 'array', icon: 'el-icon-s-grid' },
        { label: '表格型', value: 'table', icon: 'el-icon-s-order' },
        { label: '容器型', value: 'container', icon: 'el-icon-folder' },
        { label: '生成器型', value: 'generator', icon: 'el-icon-magic-stick' }
      ],
      objectFields: [],    // 对象区域字段
      operationFields: [], // 操作区域字段
      resultFields: [],    // 结果区域字段
      moduleId: null,      // 当前模板ID（用于编辑时加载配置）
      saveTimer: null,     // 自动保存定时器
      rules: {
        bigCategory: [
          { required: true, message: '请选择大目录', trigger: 'change' }
        ],
        parent: [
          { 
            required: true, 
            message: '请选择子目录', 
            trigger: 'change',
            validator: (rule, value, callback) => {
              if (value === null || value === undefined || value === '') {
                callback(new Error('请选择子目录'));
              } else {
                callback();
              }
            }
          }
        ],
        name: [
          { required: true, message: '请输入模板名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        description: [
          { required: true, message: '请输入模板说明', trigger: 'blur' }
        ]
      }
    }
  },
  mounted() {
    // 如果是编辑模式，从路由参数中获取moduleId
    this.moduleId = this.$route.query.moduleId || this.$route.params.moduleId;
    if (this.moduleId) {
      this.loadEnumConfigFromStorage();
    }
    // 如果已经选择了大目录，初始化小目录列表
    if (this.templateForm.bigCategory) {
      this.handleBigCategoryChange(this.templateForm.bigCategory);
    }
  },
  beforeDestroy() {
    // 清除定时器
    if (this.saveTimer) {
      clearTimeout(this.saveTimer);
    }
  },
  watch: {
    // 监听 currentStep 变化（仅用于调试）
    currentStep: {
      handler(newStep, oldStep) {
        console.log(`📍 步骤变化: ${oldStep} → ${newStep}`);
        if (newStep === 0 && oldStep === 1) {
          console.error('⚠️ 意外跳回到基础设置页面！');
          console.trace('调用堆栈:');
        }
      }
    }
  },
  methods: {
    handleDropdownAction(action) {
      switch (action) {
        case 'profile':
          this.$router.push('/person')
          break
        case 'logout':
          this.$router.push('/login')
          break
      }
    },
    handleNavAction(action) {
      if (action === 'create') {
        this.$router.push('/template-create').catch(() => {})
      }
    },
    handleAuditAction(action) {
      switch (action) {
        case 'templateAudit':
          this.$router.push('/template-audit').catch(() => {})
          break
        case 'templateStop':
          this.$message.info('模版停用功能开发中')
          break
        default:
          this.$message.info('功能开发中...')
      }
    },
    // 大目录改变时更新小目录列表
    handleBigCategoryChange(bigCategory) {
      console.log('🔄 大目录改变:', bigCategory);
      this.currentSubCategories = this.directoryStructure[bigCategory] || [];
      console.log('📋 当前子目录列表:', this.currentSubCategories);
      // 清空子目录选择
      this.templateForm.parent = null;  // 改为null，与初始值保持一致
      console.log('🧹 已清空子目录选择');
    },
    nextStep() {
      // 调试：打印当前表单数据
      console.log('🔍 表单验证前的数据:', this.templateForm);
      console.log('🔍 bigCategory:', this.templateForm.bigCategory);
      console.log('🔍 parent:', this.templateForm.parent);
      console.log('🔍 currentSubCategories:', this.currentSubCategories);
      
      this.$refs.templateForm.validate((valid) => {
        console.log('🔍 表单验证结果:', valid);
        if (valid) {
          const userData = JSON.parse(localStorage.getItem('xm-user') || '{}')
          const creatorName = userData.username || userData.logininfo?.username
          
          if (!creatorName) {
            this.$message.error('获取用户信息失败，请重新登录')
            this.$router.push('/login')
            return
          }

          // 暂存表单数据到 sessionStorage
          // 注意：bigCategory用于前端显示子目录列表，需要保存；但提交给后端时不传递
          const formData = {
            name: this.templateForm.name,
            parent: this.templateForm.parent,
            bigCategory: this.templateForm.bigCategory,  // 保存用于恢复UI状态
            description: this.templateForm.description,
            creator: creatorName
          };
          sessionStorage.setItem('templateFormData', JSON.stringify(formData));
          console.log('✅ 暂存的表单数据:', formData);
          this.currentStep++;
        } else {
          console.error('❌ 表单验证失败');
          this.$message.error('请完整填写表单信息');
        }
      })
    },
    prevStep() {
      this.currentStep--
    },
    // 拖拽开始
    handleDragStart(event, type) {
      event.dataTransfer.setData('fieldType', JSON.stringify(type));
      event.dataTransfer.effectAllowed = 'copy';
    },

    // 拖拽进入区域
    handleDragEnter(event, area) {
      this.isDragOver = area;
    },

    // 拖拽离开区域
    handleDragLeave(event) {
      if (!event.relatedTarget || !event.currentTarget.contains(event.relatedTarget)) {
        this.isDragOver = null;
      }
    },

    // 拖拽放置
    handleDrop(event, area) {
      const typeData = JSON.parse(event.dataTransfer.getData('fieldType'));
      const newField = {
        type: typeData.value,
        name: '',
        description: ''
      };

      // 如果是枚举型，添加枚举选项数组
      if (typeData.value === 'enum') {
        newField.enumOptions = [
          { label: 'A', value: '' }
        ];
      }

      switch (area) {
        case 'object':
          this.objectFields.push(newField);
          break;
        case 'operation':
          this.operationFields.push(newField);
          break;
        case 'result':
          this.resultFields.push(newField);
          break;
      }

      this.isDragOver = null;
    },

    // 删除字段
    removeField(area, index) {
      switch (area) {
        case 'object':
          this.objectFields.splice(index, 1);
          break;
        case 'operation':
          this.operationFields.splice(index, 1);
          break;
        case 'result':
          this.resultFields.splice(index, 1);
          break;
      }
    },

    // 获取字段图标
    getFieldIcon(type) {
      const fieldType = this.fieldTypes.find(t => t.value === type);
      return fieldType ? fieldType.icon : 'el-icon-document';
    },

    // 获取字段类型标签
    getFieldTypeLabel(type) {
      const fieldType = this.fieldTypes.find(t => t.value === type);
      return fieldType ? fieldType.label : '未知类型';
    },

    // 添加枚举选项
    addEnumOption(field) {
      if (!field.enumOptions) {
        field.enumOptions = [];
      }
      const labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];
      const nextLabel = labels[field.enumOptions.length] || `选项${field.enumOptions.length + 1}`;
      field.enumOptions.push({ label: nextLabel, value: '' });
      this.$forceUpdate();
    },

    // 删除枚举选项
    removeEnumOption(field, index) {
      if (field.enumOptions && field.enumOptions.length > 1) {
        field.enumOptions.splice(index, 1);
        this.$forceUpdate();
      } else {
        this.$message.warning('至少保留一个枚举选项');
      }
    },

    // 从服务器加载枚举配置
    async loadEnumConfigFromStorage() {
      // 优先使用模板名称，如果没有则使用moduleId
      const configKey = this.templateForm.name || this.moduleId;
      if (configKey) {
        console.log('🔄 从服务器加载枚举配置，使用键:', configKey);
        await loadTemplateEnumConfig(
          configKey,
          this.objectFields,
          this.operationFields,
          this.resultFields
        );
        this.$forceUpdate();
      }
    },

    async submitTemplate() {
      console.log('🚀 submitTemplate 被调用！');
      console.trace('调用堆栈:');
      
      // 获取暂存的表单数据
      const formData = sessionStorage.getItem('templateFormData');
      console.log('📋 sessionStorage 中的表单数据:', formData);
      
      if (!formData) {
        console.error('❌ 未找到表单数据，将跳回基础设置页面');
        this.$message.error('未找到表单数据，请重新填写');
        this.currentStep = 0;
        return;
      }

      // 验证字段
      const allFields = [
        ...this.objectFields,
        ...this.operationFields,
        ...this.resultFields
      ];

      if (allFields.length === 0) {
        this.$message.error('请至少添加一个字段');
        return;
      }

      // 🔍 调试：打印准备保存的字段信息
      console.log('========== 准备提交模板 ==========');
      console.log('对象区域字段:', JSON.parse(JSON.stringify(this.objectFields)));
      console.log('操作区域字段:', JSON.parse(JSON.stringify(this.operationFields)));
      console.log('结果区域字段:', JSON.parse(JSON.stringify(this.resultFields)));

      for (const field of allFields) {
        if (!field.name) {
          this.$message.error('请填写所有字段的名称');
          return;
        }
        // 设置 contribution 为字段类型的标签
        const fieldType = this.fieldTypes.find(t => t.value === field.type);
        field.contribution = fieldType ? fieldType.label : field.type;
        
        // 🔍 调试：打印枚举字段信息
        if (field.type === 'enum') {
          console.log(`枚举字段 "${field.name}":`, field.enumOptions);
        }
      }

      // 构造提交数据，确保各区域字段数组不会为 null
      const parsedForm = JSON.parse(formData);
      const mapField = (field) => ({
        columnName: field.name,
        columnContribution: field.contribution,
        columnType: field.type
      });
      const objectArray = this.objectFields.map(mapField);
      const operationArray = this.operationFields.map(mapField);
      const resultArray = this.resultFields.map(mapField);

      // 只传子目录ID，不传大目录参数
      const templateData = {
        name: parsedForm.name,
        parent: parsedForm.parent,  // 只传子目录ID
        description: parsedForm.description,
        creator: parsedForm.creator,
        objectArray,
        operationArray,
        resultArray,
        columns: {
          object: objectArray,
          operation: operationArray,
          result: resultArray
        }
      };

      try {
        // 第一步：提交模板数据到Java后端
        console.log('📤 第一步：提交模板数据到Java后端:', templateData);
        const response = await this.$request.post('/basemodule/module/create', templateData);
        
        console.log('📥 Java后端完整响应:', response);
        console.log('📥 Java后端响应数据:', response.data);
        
        if (response.data.code === 0) {
          // 使用模板名称作为存储键
          const templateName = parsedForm.name;
          console.log('✅ 模板创建成功（Java后端）');
          console.log('📝 模板名称:', templateName);
          
          // 尝试从响应中获取模板ID
          const moduleId = response.data.moduleId || 
                          response.data.id || 
                          (response.data.data && response.data.data.moduleId) ||
                          (response.data.data && response.data.data.id);
          console.log('🆔 模板ID:', moduleId);
          
          // 第二步：保存枚举配置到Node.js服务器
          console.log('💾 第二步：开始保存枚举配置到Node.js服务器...');
          
          try {
            // 策略1: 使用模板名称保存（主要方式）
            const savedByName = await saveTemplateEnumConfig(
              templateName,
              this.objectFields,
              this.operationFields,
              this.resultFields
            );
            
            if (savedByName) {
              console.log('✅ 使用模板名称保存枚举配置成功！键:', templateName);
            } else {
              console.error('❌ 使用模板名称保存枚举配置失败！');
            }
            
            // 策略2: 如果有模板ID，也用模板ID保存一份（确保兼容性）
            if (moduleId) {
              const savedById = await saveTemplateEnumConfig(
                moduleId,
                this.objectFields,
                this.operationFields,
                this.resultFields
              );
              
              if (savedById) {
                console.log('✅ 使用模板ID保存枚举配置成功！键:', moduleId);
                // 验证保存结果
                const savedConfig = await getEnumConfig(moduleId);
                console.log('🔍 验证模板ID配置:', savedConfig);
              } else {
                console.error('❌ 使用模板ID保存枚举配置失败！');
              }
            } else {
              console.warn('⚠️ 未获取到模板ID，仅使用模板名称保存');
            }
            
            // 提交成功后清除暂存数据
            sessionStorage.removeItem('templateFormData');
            this.$message.success(`模板"${templateName}"创建成功，枚举配置已保存`);
            this.$router.push({ name: 'TemplateLibrary' });
          } catch (enumError) {
            console.error('❌ 保存枚举配置失败:', enumError);
            // 即使枚举配置保存失败，模板已经创建成功，给用户提示
            sessionStorage.removeItem('templateFormData');
            this.$message.warning(`模板"${templateName}"创建成功，但枚举配置保存失败，请稍后重试`);
            this.$router.push({ name: 'TemplateLibrary' });
          }
        } else {
          throw new Error(response.data.msg || '创建失败');
        }
      } catch (error) {
        console.error('❌ 创建模板失败:', error);
        this.$message.error(error.message || '创建模板失败，请重试');
      }
    }
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

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

@keyframes glow-border {
  0%, 100% {
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.4);
  }
  50% {
    box-shadow: 0 0 35px rgba(102, 126, 234, 0.7);
  }
}

.template-create {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7474bf 100%);
  background-size: 200% 200%;
  animation: gradientShift 15s ease infinite;
  padding-top: 140px;
  position: relative;
  overflow-x: hidden;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.template-create::before {
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

.steps-nav {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  padding: 40px 30px;
  margin-bottom: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15),
              0 0 0 1px rgba(255, 255, 255, 0.3) inset;
  border-radius: 16px;
  margin-left: 20px;
  margin-right: 20px;
  position: relative;
  z-index: 1;
  animation: slideDown 0.6s ease;
}

.steps-nav::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, 
    #667eea 0%, 
    #764ba2 50%, 
    #667eea 100%);
  background-size: 200% 100%;
  animation: gradientSlide 3s linear infinite;
  border-radius: 0 0 16px 16px;
}

@keyframes gradientSlide {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

.form-container, .design-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  margin: 20px;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15),
              0 0 0 1px rgba(255, 255, 255, 0.3) inset;
  position: relative;
  z-index: 1;
  animation: fadeInScale 0.6s ease;
}

.form-container::before, .design-container::before {
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

.form-header, .design-header {
  margin-bottom: 35px;
  position: relative;
  padding-bottom: 15px;
}

.form-header::after, .design-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
  animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.4);
  }
  50% {
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.8);
  }
}

.form-header h2, .design-header h2 {
  font-size: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.type-selection {
  margin-bottom: 30px;
}

.type-selection .label {
  font-size: 14px;
  color: #606266;
  margin-right: 15px;
}

.template-form {
  max-width: 800px;
}

.form-footer, .design-footer {
  margin-top: 40px;
  text-align: center;
}

.design-content {
  padding: 20px;
  display: flex;
  gap: 20px;
  min-height: 600px;
}

.field-types-toolbar {
  width: 220px;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.95) 0%, 
    rgba(248, 249, 250, 0.95) 100%);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12),
              0 0 0 1px rgba(102, 126, 234, 0.1) inset;
  padding: 20px;
  position: sticky;
  top: 20px;
}

.toolbar-title {
  font-size: 17px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
  letter-spacing: 0.5px;
}

.field-types {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 5px;
}

.field-types::-webkit-scrollbar {
  width: 5px;
}

.field-types::-webkit-scrollbar-track {
  background: rgba(245, 247, 250, 0.5);
  border-radius: 10px;
}

.field-types::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
}

.field-type-item {
  padding: 12px 14px;
  border: 2px solid rgba(102, 126, 234, 0.15);
  border-radius: 10px;
  cursor: move;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  background: rgba(255, 255, 255, 0.9);
  position: relative;
  overflow: hidden;
}

.field-type-item::before {
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

.field-type-item:hover::before {
  left: 100%;
}

.field-type-item:hover {
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.1) 0%, 
    rgba(118, 75, 162, 0.1) 100%);
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px) scale(1.03);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
  animation: bounce 0.6s ease;
}

.field-type-item:active {
  transform: scale(0.98);
}

.field-type-item i {
  font-size: 20px;
  transition: transform 0.3s ease;
}

.field-type-item:hover i {
  transform: rotate(10deg) scale(1.2);
}

.design-areas {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: calc(100vh - 260px);
  overflow-y: auto;
  padding-right: 10px;
  box-sizing: border-box;
}

.design-area {
  flex: 1;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.95) 0%, 
    rgba(248, 249, 250, 0.95) 100%);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1),
              0 0 0 1px rgba(255, 255, 255, 0.3) inset;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.design-area:hover {
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.2);
}

.area-header {
  padding: 18px 20px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.05) 0%, 
    rgba(118, 75, 162, 0.05) 100%);
  border-radius: 16px 16px 0 0;
}

.area-title {
  font-size: 17px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
}

.area-content {
  flex: 1;
  padding: 18px;
  min-height: 150px;
  background: linear-gradient(135deg, 
    rgba(249, 249, 249, 0.8) 0%, 
    rgba(245, 247, 250, 0.8) 100%);
  border-radius: 0 0 16px 16px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
}

.area-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent 10px,
      rgba(102, 126, 234, 0.02) 10px,
      rgba(102, 126, 234, 0.02) 20px
    );
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  border-radius: 0 0 16px 16px;
}

.area-content.drag-over {
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.15) 0%, 
    rgba(118, 75, 162, 0.15) 100%);
  border: 3px dashed #667eea;
  transform: scale(1.02);
  animation: glow-border 1.5s infinite;
}

.area-content.drag-over::before {
  opacity: 1;
}

.empty-tip {
  height: 100%;
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 14px;
}

.field-item {
  background: rgba(255, 255, 255, 0.95);
  border: 2px solid rgba(102, 126, 234, 0.15);
  border-radius: 12px;
  margin-bottom: 12px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  animation: fadeInScale 0.4s ease;
}

.field-item:hover {
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.2);
  transform: translateY(-3px);
  border-color: #667eea;
}

.field-item-header {
  padding: 12px 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.08) 0%, 
    rgba(118, 75, 162, 0.08) 100%);
  border-radius: 12px 12px 0 0;
}

.field-item-header i {
  color: #667eea;
  font-size: 18px;
  transition: transform 0.3s ease;
}

.field-item:hover .field-item-header i {
  transform: rotate(10deg) scale(1.1);
}

.field-name {
  flex: 1;
  color: #667eea;
  font-weight: 600;
  font-size: 14px;
}

.field-item-body {
  padding: 15px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 0 0 12px 12px;
}

.enum-options-container {
  margin-top: 12px;
  padding: 15px;
  background: linear-gradient(135deg, 
    rgba(249, 249, 249, 0.9) 0%, 
    rgba(245, 247, 250, 0.9) 100%);
  backdrop-filter: blur(5px);
  border-radius: 10px;
  border: 2px solid rgba(102, 126, 234, 0.15);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) inset;
}

.enum-section-title {
  font-size: 14px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 10px;
  margin-top: 12px;
  letter-spacing: 0.3px;
}

.enum-section-title:first-child {
  margin-top: 0;
}

.enum-option-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
  background: rgba(255, 255, 255, 0.95);
  padding: 10px 12px;
  border-radius: 8px;
  border: 2px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.enum-option-item:hover {
  background: rgba(255, 255, 255, 1);
  border-color: #667eea;
  transform: translateX(5px);
  box-shadow: 0 3px 15px rgba(102, 126, 234, 0.15);
}

.enum-label {
  font-weight: 700;
  color: #667eea;
  min-width: 30px;
  text-align: center;
  font-size: 15px;
  padding: 4px 8px;
  border-radius: 6px;
  background: rgba(102, 126, 234, 0.1);
  border: 2px solid rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.enum-option-item:hover .enum-label {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  transform: scale(1.05);
}

.enum-input {
  flex: 1;
}

.enum-delete-btn {
  color: #F56C6C;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.enum-delete-btn:hover {
  color: #fff;
  background: linear-gradient(135deg, #F56C6C 0%, #c45656 100%);
  transform: scale(1.1);
  box-shadow: 0 3px 10px rgba(245, 108, 108, 0.4);
}

.enum-actions {
  margin-top: 12px;
  text-align: center;
}

.enum-actions .el-button {
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.1) 0%, 
    rgba(118, 75, 162, 0.1) 100%);
  border: 2px solid rgba(102, 126, 234, 0.3);
  color: #667eea;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.enum-actions .el-button:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.el-radio {
  margin-right: 20px;
}

.el-input, .el-select {
  width: 100%;
}
</style>
