<template>
    <div class="data-entry-page">
        <!-- 顶部导航 -->
        <Navbar @dropdown-action="handleDropdownAction" />
        <TemplateNavbar @nav-action="handleNavAction" @audit-action="handleAuditAction" />

        <!-- 主容器 -->
        <div class="container" v-loading="loading" element-loading-text="正在加载数据...">
            <div class="page-header">
                <el-button icon="el-icon-arrow-left" @click="goBack" class="back-btn">返回</el-button>
                <h2>{{ title }}</h2>
            </div>

            <div class="content-wrapper">
                <!-- 左侧分类菜单 -->
                <div class="sidebar">
                    <el-tree
                        :data="directoryTree"
                        :props="defaultProps"
                        @node-click="handleNodeClick"
                        default-expand-all
                        highlight-current
                    ></el-tree>
                </div>

                <!-- 右侧表单区域 -->
                <div class="form-area">
                    <div v-if="selectedNodeFields.length > 0">
                        <h3 class="section-title">{{ selectedNode.label }}</h3>
                        <el-form :model="formData" label-width="200px">
                            <el-form-item 
                                v-for="field in selectedNodeFields" 
                                :key="field.columnName"
                                :label="field.displayName"
                            >
                                <!-- 枚举类型：下拉框 -->
                                <el-select 
                                    v-if="field.columnContribution === '枚举型'"
                                    v-model="formData[field.columnName]"
                                    placeholder="请选择"
                                    style="width: 100%"
                                >
                                    <el-option
                                        v-for="option in field.enumOptions"
                                        :key="option.value"
                                        :label="formatEnumLabel(option)"
                                        :value="option.value"
                                    ></el-option>
                                </el-select>
                                
                                <!-- 普通类型：输入框 -->
                                <el-input 
                                    v-else
                                    v-model="formData[field.columnName]"
                                    :placeholder="`请输入${field.displayName}`"
                                ></el-input>
                            </el-form-item>
                        </el-form>
                    </div>
                    <div v-else class="placeholder">
                        <el-empty description="请从左侧选择一个区域填写数据"></el-empty>
                    </div>
                </div>
            </div>

            <!-- 底部操作按钮 -->
            <div class="footer-actions">
                <el-button @click="goBack">取 消</el-button>
                <el-button type="primary" @click="handleSubmit">提 交</el-button>
            </div>
        </div>
    </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import TemplateNavbar from '../components/TemplateNavbar.vue';
import { getEnumConfig, debugEnumConfig } from '@/utils/enumStorage';

export default {
    name: 'DataEntryPage',
    components: {
        Navbar,
        TemplateNavbar
    },
    data() {
        return {
            title: '填写数据',
            moduleId: null,
            templateName: '',
            directoryTree: [],
            defaultProps: {
                children: 'children',
                label: 'label'
            },
            selectedNode: {},
            selectedNodeFields: [],
            columnInfo: {},
            loading: false,
            formData: {},
            enumConfig: {},
            fieldSectionMap: {} // 字段到区域的映射 { fieldName: 'object'|'operation'|'result' }
        };
    },
    mounted() {
        // 从路由参数获取模板信息
        this.moduleId = this.$route.params.moduleId || this.$route.query.moduleId;
        this.templateName = this.$route.params.templateName || this.$route.query.templateName || '';
        this.title = this.$route.params.title || this.$route.query.title || '填写数据';
        
        if (!this.moduleId) {
            this.$message.error('缺少模板ID参数');
            this.goBack();
            return;
        }
        
        this.loadColumnInfo();
    },
    methods: {
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
        handleNavAction(action) {
            switch (action) {
                case 'create':
                    this.$router.push('/template-create').catch(() => {});
                    break;
            }
        },
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
        goBack() {
            this.$router.go(-1);
        },
        async loadColumnInfo() {
            if (!this.moduleId) {
                this.$message.warning('缺少必要的参数来加载数据');
                return;
            }
            this.loading = true;
            try {
                console.log('========== 开始加载字段信息 ==========');
                console.log('📋 模板ID:', this.moduleId);
                console.log('📝 传入的模板名称 (prop):', this.templateName);
                
                // 获取字段信息 - 使用try-catch包裹，404时不阻止流程
                let columnInfo = {};
                let backendTemplateName = '';
                
                try {
                    const columnResponse = await this.$request.get(`/basemodule/moduledata/getColumnInfo/${this.moduleId}`);
                    console.log('📥 后端返回的字段信息:', columnResponse.data);
                    
                    if (columnResponse.data && columnResponse.data.code === 0) {
                        const rawColumnInfo = columnResponse.data.columnInfo || columnResponse.data.data || {};
                        columnInfo = rawColumnInfo;
                        
                        console.log('📊 解析后的columnInfo:', columnInfo);
                        
                        // 从多个来源获取模板名称（优先级：prop > 后端响应）
                        backendTemplateName = columnResponse.data.templateName ||
                                           (columnResponse.data.columnInfo && columnResponse.data.columnInfo.templateName) ||
                                           columnResponse.data.name || 
                                           columnResponse.data.moduleName || 
                                           (columnResponse.data.data && columnResponse.data.data.name) ||
                                           (columnResponse.data.data && columnResponse.data.data.templateName) ||
                                           '';
                    }
                } catch (columnError) {
                    // 404或其他错误时，只警告，不阻止流程
                    console.warn('⚠️ 获取字段信息失败（接口可能不存在）:', columnError);
                    if (columnError.response && columnError.response.status === 404) {
                        console.warn('   接口 /basemodule/moduledata/getColumnInfo/' + this.moduleId + ' 不存在（404）');
                        console.warn('   将使用空字段信息继续流程');
                    } else {
                        console.warn('   错误详情:', columnError.message);
                    }
                }
                
                this.columnInfo = columnInfo;
                
                // 优先使用 prop 传入的模板名称
                const finalTemplateName = this.templateName || backendTemplateName;
                
                console.log('📝 最终使用的模板名称:', finalTemplateName);
                console.log('   - prop传入:', this.templateName);
                console.log('   - 后端返回:', backendTemplateName);
                console.log('🆔 模板ID:', this.moduleId);
                
                // 尝试多个可能的键来加载枚举配置
                const possibleKeys = [];
                if (finalTemplateName) {
                    possibleKeys.push(finalTemplateName);
                }
                if (this.moduleId) {
                    possibleKeys.push(this.moduleId);
                    possibleKeys.push(String(this.moduleId));
                    possibleKeys.push(parseInt(this.moduleId));
                }
                
                console.log('🔑 尝试以下键加载枚举配置:', possibleKeys);
                
                let foundConfig = false;
                for (const key of possibleKeys) {
                    try {
                        const config = await getEnumConfig(key);
                        if (config && Object.keys(config).length > 0) {
                            this.enumConfig = config;
                            foundConfig = true;
                            console.log(`✅ 使用键 "${key}" 找到了枚举配置`);
                            console.log('💾 枚举配置内容:', this.enumConfig);
                            await debugEnumConfig(key);
                            break;
                        }
                    } catch (enumError) {
                        console.warn(`尝试键 "${key}" 时出错:`, enumError);
                        continue;
                    }
                }
                
                if (!foundConfig) {
                    this.enumConfig = {};
                    console.warn('⚠️ 未找到该模板的枚举配置');
                    console.warn('   尝试的所有键:', possibleKeys);
                    console.warn('💡 提示: 如果该模板包含枚举字段，请在模板创建/编辑页面重新保存');
                }
                
                this.buildDirectoryTree();
            } catch (error) {
                console.error('加载数据时发生未知错误:', error);
                if (error.response && error.response.status !== 404) {
                    this.$message.warning('加载数据时出现问题，部分功能可能不可用');
                }
            } finally {
                this.loading = false;
            }
        },
        buildDirectoryTree() {
            console.log('========== 构建表单树结构 ==========');
            console.log('完整的columnInfo:', JSON.parse(JSON.stringify(this.columnInfo)));
            console.log('当前模板ID:', this.moduleId);
            
            const objectFields = this.columnInfo.object || [];
            const operationFields = this.columnInfo.operation || [];
            const resultFields = this.columnInfo.result || [];
            
            console.log('对象区域字段数量:', objectFields.length);
            console.log('对象区域字段详情:', JSON.parse(JSON.stringify(objectFields)));
            console.log('操作区域字段数量:', operationFields.length);
            console.log('结果区域字段数量:', resultFields.length);
            
            this.directoryTree = [];
            this.fieldSectionMap = {};
            
            // 1. 对象区域
            if (objectFields.length > 0) {
                const processedFields = this.processFieldsWithEnum(objectFields, 'object');
                processedFields.forEach(field => {
                    this.fieldSectionMap[field.columnName] = 'object';
                });
                const objectNode = {
                    id: 'object_area',
                    label: '对象区域',
                    section: 'object',
                    fields: processedFields,
                    children: []
                };
                this.directoryTree.push(objectNode);
            }
            
            // 2. 操作区域
            if (operationFields.length > 0) {
                const processedFields = this.processFieldsWithEnum(operationFields, 'operation');
                processedFields.forEach(field => {
                    this.fieldSectionMap[field.columnName] = 'operation';
                });
                const operationNode = {
                    id: 'operation_area',
                    label: '操作区域',
                    section: 'operation',
                    fields: processedFields,
                    children: []
                };
                this.directoryTree.push(operationNode);
            }
            
            // 3. 结果区域
            if (resultFields.length > 0) {
                const processedFields = this.processFieldsWithEnum(resultFields, 'result');
                processedFields.forEach(field => {
                    this.fieldSectionMap[field.columnName] = 'result';
                });
                const resultNode = {
                    id: 'result_area',
                    label: '结果区域',
                    section: 'result',
                    fields: processedFields,
                    children: []
                };
                this.directoryTree.push(resultNode);
            }
            
            console.log('字段到区域的映射:', this.fieldSectionMap);
            
            // 默认选中第一个节点
            if (this.directoryTree.length > 0) {
                this.handleNodeClick(this.directoryTree[0]);
            }
        },
        processFieldsWithEnum(fields, section) {
            console.log('========== processFieldsWithEnum ==========');
            console.log('section:', section);
            console.log('fields:', fields);
            console.log('enumConfig:', this.enumConfig);
            
            return fields.map((field, index) => {
                const columnName = field.columnName || field.column_name || field.fieldName || field.name || field.field_name;
                const contribution = field.columnContribution || field.column_contribution || field.contribution || field.type || '';
                
                console.log(`🔍 字段 ${index}: 原始字段对象=`, field);
                console.log(`  - columnName=${columnName}, contribution=${contribution}`);
                
                let enumOptions = [];
                if (contribution === '枚举型') {
                    console.log(`📌 字段 ${columnName} 是枚举型，开始查找枚举配置...`);
                    
                    if (this.enumConfig[section]) {
                        const sectionConfig = this.enumConfig[section];
                        console.log(`  ${section} 区域的配置:`, sectionConfig);
                        
                        const normalizedColumnName = columnName.toLowerCase().replace(/[_\s-]/g, '');
                        console.log(`  标准化字段名: "${normalizedColumnName}"`);
                        
                        // 策略1-5：与DataEntryDialog相同的匹配逻辑
                        const exactKey = `field_${index}_${columnName}`;
                        if (sectionConfig[exactKey]) {
                            enumOptions = sectionConfig[exactKey].options || [];
                            console.log(`  ✅ 策略1成功 - 精确匹配 (${exactKey}):`, enumOptions);
                        }
                        
                        if (enumOptions.length === 0) {
                            const nameKey = `name_${columnName}`;
                            if (sectionConfig[nameKey]) {
                                enumOptions = sectionConfig[nameKey].options || [];
                                console.log(`  ✅ 策略2成功 - 字段名匹配 (${nameKey}):`, enumOptions);
                            }
                        }
                        
                        if (enumOptions.length === 0) {
                            const normalizedKey = `normalized_${normalizedColumnName}`;
                            if (sectionConfig[normalizedKey]) {
                                enumOptions = sectionConfig[normalizedKey].options || [];
                                console.log(`  ✅ 策略3成功 - 标准化名称匹配 (${normalizedKey}):`, enumOptions);
                            }
                        }
                        
                        if (enumOptions.length === 0) {
                            for (const configKey in sectionConfig) {
                                const configItem = sectionConfig[configKey];
                                if (configItem.fieldName) {
                                    const configFieldName = configItem.fieldName;
                                    const normalizedConfigName = configFieldName.toLowerCase().replace(/[_\s-]/g, '');
                                    
                                    if (configFieldName === columnName || normalizedConfigName === normalizedColumnName) {
                                        enumOptions = configItem.options || [];
                                        console.log(`  ✅ 策略4成功 - 字段名属性匹配 (${configKey}):`, enumOptions);
                                        break;
                                    }
                                }
                            }
                        }
                        
                        if (enumOptions.length === 0) {
                            for (const configKey in sectionConfig) {
                                const match = configKey.match(/^field_\d+_(.+)$/);
                                if (match) {
                                    const extractedName = match[1];
                                    const normalizedExtracted = extractedName.toLowerCase().replace(/[_\s-]/g, '');
                                    
                                    if (extractedName === columnName || normalizedExtracted === normalizedColumnName) {
                                        const configItem = sectionConfig[configKey];
                                        enumOptions = configItem.options || [];
                                        console.log(`  ✅ 策略5成功 - key提取匹配 (${configKey}):`, enumOptions);
                                        break;
                                    }
                                }
                            }
                        }
                    } else {
                        console.warn(`  ⚠️ enumConfig 中没有 "${section}" 区域的配置`);
                    }
                    
                    if (enumOptions.length === 0) {
                        console.warn(`❌ 未找到字段 ${columnName} 的枚举配置，使用默认值`);
                        enumOptions = [
                            { label: '选项1', value: '选项1' },
                            { label: '选项2', value: '选项2' }
                        ];
                    }
                }
                
                const formattedDisplayName = contribution 
                    ? `${columnName} (${contribution})`
                    : columnName;
                
                return {
                    columnName,
                    displayName: formattedDisplayName,
                    columnContribution: contribution,
                    enumOptions
                };
            });
        },
        handleNodeClick(node) {
            console.log('点击节点:', node);
            if (node.fields && node.fields.length > 0) {
                this.selectedNode = node;
                this.selectedNodeFields = node.fields;
            } else {
                this.selectedNode = {};
                this.selectedNodeFields = [];
            }
        },
        formatEnumLabel(option) {
            if (!option.value || option.value === option.label) {
                return option.label;
            }
            return `${option.label}: ${option.value}`;
        },
        async handleSubmit() {
            console.log('========== 开始提交数据 ==========');
            console.log('原始表单数据:', this.formData);
            console.log('字段区域映射:', this.fieldSectionMap);
            
            const object = {};
            const operation = {};
            const result = {};
            
            for (const fieldName in this.formData) {
                const value = this.formData[fieldName];
                const section = this.fieldSectionMap[fieldName];
                
                if (section === 'object') {
                    object[fieldName] = value;
                } else if (section === 'operation') {
                    operation[fieldName] = value;
                } else if (section === 'result') {
                    result[fieldName] = value;
                }
            }
            
            console.log('对象区域数据:', object);
            
            const sampleSerialFieldNames = ['样品编号', 'sample_serial', 'sampleSerial', '样本编号', '样本序列号'];
            let sampleSerial = '';
            
            for (const fieldName of sampleSerialFieldNames) {
                if (object[fieldName]) {
                    sampleSerial = object[fieldName];
                    console.log(`找到样品序列号字段: ${fieldName} = ${sampleSerial}`);
                    break;
                }
            }
            
            if (!sampleSerial) {
                for (const fieldName in object) {
                    const lowerFieldName = fieldName.toLowerCase();
                    if (lowerFieldName.includes('样品') || 
                        lowerFieldName.includes('编号') || 
                        lowerFieldName.includes('serial') ||
                        lowerFieldName.includes('sample')) {
                        sampleSerial = object[fieldName];
                        console.log(`模糊匹配到样品序列号字段: ${fieldName} = ${sampleSerial}`);
                        break;
                    }
                }
            }
            
            if (!sampleSerial || sampleSerial.trim() === '') {
                this.$message.warning('请在对象区域填写样品编号');
                return;
            }
            
            const requestData = {
                module_id: this.moduleId,
                sample_serial: sampleSerial,
                object: object,
                operation: operation,
                result: result
            };
            
            console.log('请求参数:', JSON.stringify(requestData, null, 2));
            
            this.loading = true;
            try {
                const response = await this.$request.post(
                    '/basemodule/moduledata/insertsingle',
                    requestData
                );
                
                console.log('API响应:', response.data);
                
                if (response.data && response.data.code === 0) {
                    this.$message.success('数据提交成功！');
                    this.formData = {};
                    this.goBack();
                } else {
                    throw new Error(response.data.msg || '提交失败');
                }
            } catch (error) {
                console.error('提交数据失败:', error);
                this.$message.error('提交数据失败: ' + (error.message || '请重试'));
            } finally {
                this.loading = false;
            }
        }
    }
};
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

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.data-entry-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7474bf 100%);
    background-size: 200% 200%;
    animation: gradientShift 15s ease infinite;
    padding-top: 140px;
    position: relative;
}

.data-entry-page::before {
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

.container {
    width: 90%;
    max-width: 1400px;
    margin: 40px auto;
    padding: 30px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15),
                0 0 0 1px rgba(255, 255, 255, 0.3) inset;
    position: relative;
    z-index: 1;
    animation: fadeInScale 0.6s ease;
}

.page-header {
    display: flex;
    align-items: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid rgba(102, 126, 234, 0.15);
}

.back-btn {
    margin-right: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
}

.back-btn:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: translateX(-3px);
}

.page-header h2 {
    font-size: 28px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    font-weight: 700;
}

.content-wrapper {
    display: flex;
    gap: 30px;
    min-height: 60vh;
}

.sidebar {
    width: 280px;
    min-width: 280px;
    background: rgba(248, 249, 250, 0.8);
    border-radius: 12px;
    padding: 20px;
    border: 2px solid rgba(102, 126, 234, 0.1);
    overflow-y: auto;
    max-height: 65vh;
}

.form-area {
    flex: 1;
    background: rgba(248, 249, 250, 0.8);
    border-radius: 12px;
    padding: 30px;
    border: 2px solid rgba(102, 126, 234, 0.1);
    overflow-y: auto;
    max-height: 65vh;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 25px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding-bottom: 10px;
    border-bottom: 2px solid rgba(102, 126, 234, 0.15);
}

.placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 300px;
}

.footer-actions {
    margin-top: 30px;
    text-align: center;
    padding-top: 20px;
    border-top: 2px solid rgba(102, 126, 234, 0.15);
}

.footer-actions .el-button {
    min-width: 120px;
    margin: 0 10px;
}

.footer-actions .el-button--primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
}

.footer-actions .el-button--primary:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

/* 美化 el-tree */
.sidebar >>> .el-tree {
    background: transparent;
    font-size: 15px;
}

.sidebar >>> .el-tree-node__content {
    height: 42px;
    line-height: 42px;
    padding: 0 12px;
    border-radius: 8px;
    margin-bottom: 4px;
    transition: all 0.3s ease;
}

.sidebar >>> .el-tree-node__content:hover {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.1) 0%, 
        rgba(118, 75, 162, 0.1) 100%);
    color: #667eea;
}

.sidebar >>> .el-tree-node.is-current > .el-tree-node__content {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.15) 0%, 
        rgba(118, 75, 162, 0.15) 100%);
    color: #667eea;
    font-weight: 600;
}

/* 滚动条样式 */
.sidebar::-webkit-scrollbar,
.form-area::-webkit-scrollbar {
    width: 8px;
}

.sidebar::-webkit-scrollbar-thumb,
.form-area::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    border-radius: 4px;
    border: 2px solid rgba(255, 255, 255, 0.3);
}

.sidebar::-webkit-scrollbar-thumb:hover,
.form-area::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.sidebar::-webkit-scrollbar-track,
.form-area::-webkit-scrollbar-track {
    background: rgba(245, 247, 250, 0.5);
    border-radius: 4px;
}
</style>

