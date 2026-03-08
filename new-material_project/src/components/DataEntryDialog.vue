<template>
    <el-dialog
        :visible.sync="dialogVisible"
        :title="title"
        width="80%"
        :before-close="handleClose"
        top="5vh"
        custom-class="data-entry-dialog"
        v-loading="loading"
        element-loading-text="正在加载数据..."
    >
        <div class="dialog-content">
            <!-- Left Sidebar -->
            <div class="sidebar">
                <el-tree
                    :data="directoryTree"
                    :props="defaultProps"
                    @node-click="handleNodeClick"
                    default-expand-all
                    highlight-current
                ></el-tree>
            </div>

            <!-- Right Content Area -->
            <div class="content-area">
                <div v-if="selectedNodeFields.length > 0">
                    <h3>{{ selectedNode.label }}</h3>
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
                    <p>请从左侧选择一个区域填写数据。</p>
                </div>
            </div>
        </div>
        <span slot="footer" class="dialog-footer">
            <el-button @click="handleClose">取 消</el-button>
            <el-button type="primary" @click="handleSubmit">提 交</el-button>
        </span>
    </el-dialog>
</template>

<script>
import { getEnumConfig, debugEnumConfig } from '@/utils/enumStorage';

export default {
    name: 'DataEntryDialog',
    props: {
        visible: {
            type: Boolean,
            default: false
        },
        title: {
            type: String,
            default: '填写数据'
        },
        moduleId: {
            type: [String, Number],
            default: null
        },
        templateName: {
            type: String,
            default: ''
        }
    },
    data() {
        return {
            dialogVisible: this.visible,
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
    watch: {
        visible(newVal) {
            this.dialogVisible = newVal;
            if (newVal) {
                this.loadColumnInfo();
            }
        }
    },
    methods: {
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
                    // 不显示错误消息，因为这不是致命错误
                }
                
                this.columnInfo = columnInfo;
                
                // 优先使用 prop 传入的模板名称
                const finalTemplateName = this.templateName || backendTemplateName;
                
                console.log('📝 最终使用的模板名称:', finalTemplateName);
                console.log('   - prop传入:', this.templateName);
                console.log('   - 后端返回:', backendTemplateName);
                console.log('🆔 模板ID:', this.moduleId);
                
                // 尝试多个可能的键来加载枚举配置
                // 优先使用模板名称，因为保存时用的是模板名称
                const possibleKeys = [];
                if (finalTemplateName) {
                    possibleKeys.push(finalTemplateName); // 最优先：模板名称
                }
                if (this.moduleId) {
                    possibleKeys.push(this.moduleId);       // 其次：数字ID
                    possibleKeys.push(String(this.moduleId)); // 然后：字符串ID
                    possibleKeys.push(parseInt(this.moduleId)); // 最后：解析后的整数ID
                }
                
                console.log('🔑 尝试以下键加载枚举配置:', possibleKeys);
                
                let foundConfig = false;
                for (const key of possibleKeys) {
                    try {
                        const config = await getEnumConfig(key); // 改为异步await
                        if (config && Object.keys(config).length > 0) {
                            this.enumConfig = config;
                            foundConfig = true;
                            console.log(`✅ 使用键 "${key}" 找到了枚举配置`);
                            console.log('💾 枚举配置内容:', this.enumConfig);
                            
                            // 打印调试信息
                            await debugEnumConfig(key); // 改为异步await
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
                    
                    // 打印服务器中所有可用的枚举配置键
                    try {
                        const { getAllEnumConfigs } = require('@/utils/enumStorage');
                        const allConfigs = await getAllEnumConfigs(); // 改为异步await
                        console.warn('📋 服务器中现有的枚举配置键:', Object.keys(allConfigs));
                        
                        // 详细打印每个配置，帮助调试
                        console.group('🔍 详细配置信息');
                        Object.keys(allConfigs).forEach(key => {
                            console.log(`键: "${key}" (类型: ${typeof key})`);
                            if (allConfigs[key].operation) {
                                const opKeys = Object.keys(allConfigs[key].operation);
                                console.log(`  operation 区域配置键:`, opKeys);
                            }
                        });
                        console.groupEnd();
                    } catch (error) {
                        console.warn('获取所有枚举配置失败:', error);
                    }
                }
                
                // 即使字段信息为空，也尝试构建目录树（可能使用默认结构）
                this.buildDirectoryTree();
            } catch (error) {
                console.error('加载数据时发生未知错误:', error);
                // 只显示警告，不显示错误，因为可能只是接口不存在
                if (error.response && error.response.status !== 404) {
                    this.$message.warning('加载数据时出现问题，部分功能可能不可用');
                }
            } finally {
                this.loading = false;
            }
        },
        handleClose() {
            this.$emit('update:visible', false);
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
            this.fieldSectionMap = {}; // 重置字段映射
            
            // 1. 对象区域
            if (objectFields.length > 0) {
                const processedFields = this.processFieldsWithEnum(objectFields, 'object');
                // 记录字段所属区域
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
                // 记录字段所属区域
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
                // 记录字段所属区域
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
                // 尝试多种字段名属性（按优先级）
                const columnName = field.columnName || field.column_name || field.fieldName || field.name || field.field_name;
                const contribution = field.columnContribution || field.column_contribution || field.contribution || field.type || '';
                
                console.log(`🔍 字段 ${index}: 原始字段对象=`, field);
                console.log(`  - 字段所有键名:`, Object.keys(field));
                console.log(`  - columnName=${columnName}, contribution=${contribution}`);
                
                // 处理枚举类型
                let enumOptions = [];
                if (contribution === '枚举型') {
                    console.log(`📌 字段 ${columnName} 是枚举型，开始查找枚举配置...`);
                    
                    // 从 enumConfig 中获取枚举选项
                    if (this.enumConfig[section]) {
                        const sectionConfig = this.enumConfig[section];
                        console.log(`  ${section} 区域的配置:`, sectionConfig);
                        console.log(`  配置中的所有键:`, Object.keys(sectionConfig));
                        
                        // 标准化当前字段名
                        const normalizedColumnName = columnName.toLowerCase().replace(/[_\s-]/g, '');
                        console.log(`  标准化字段名: "${normalizedColumnName}"`);
                        
                        // 策略1: 使用索引和字段名精确匹配
                        const exactKey = `field_${index}_${columnName}`;
                        console.log(`  尝试策略1 - 精确匹配键: "${exactKey}"`);
                        if (sectionConfig[exactKey]) {
                            enumOptions = sectionConfig[exactKey].options || [];
                            console.log(`  ✅ 策略1成功 - 精确匹配 (${exactKey}):`, enumOptions);
                        }
                        
                        // 策略2: 只使用字段名匹配（不考虑索引）
                        if (enumOptions.length === 0) {
                            const nameKey = `name_${columnName}`;
                            console.log(`  尝试策略2 - 字段名键: "${nameKey}"`);
                            if (sectionConfig[nameKey]) {
                                enumOptions = sectionConfig[nameKey].options || [];
                                console.log(`  ✅ 策略2成功 - 字段名匹配 (${nameKey}):`, enumOptions);
                            }
                        }
                        
                        // 策略3: 使用标准化字段名匹配
                        if (enumOptions.length === 0) {
                            const normalizedKey = `normalized_${normalizedColumnName}`;
                            console.log(`  尝试策略3 - 标准化键: "${normalizedKey}"`);
                            if (sectionConfig[normalizedKey]) {
                                enumOptions = sectionConfig[normalizedKey].options || [];
                                console.log(`  ✅ 策略3成功 - 标准化名称匹配 (${normalizedKey}):`, enumOptions);
                            }
                        }
                        
                        // 策略4: 遍历所有配置，使用 fieldName 属性匹配
                        if (enumOptions.length === 0) {
                            console.log('  尝试策略4 - 遍历所有配置进行字段名匹配...');
                            for (const configKey in sectionConfig) {
                                const configItem = sectionConfig[configKey];
                                console.log(`    检查配置键 "${configKey}":`, configItem);
                                if (configItem.fieldName) {
                                    const configFieldName = configItem.fieldName;
                                    const normalizedConfigName = configFieldName.toLowerCase().replace(/[_\s-]/g, '');
                                    
                                    console.log(`      配置字段名="${configFieldName}", 标准化="${normalizedConfigName}"`);
                                    console.log(`      比较: "${configFieldName}" === "${columnName}" 或 "${normalizedConfigName}" === "${normalizedColumnName}"`);
                                    
                                    // 精确匹配或标准化匹配
                                    if (configFieldName === columnName || normalizedConfigName === normalizedColumnName) {
                                        enumOptions = configItem.options || [];
                                        console.log(`  ✅ 策略4成功 - 字段名属性匹配 (${configKey}, fieldName: ${configFieldName}):`, enumOptions);
                                        break;
                                    }
                                }
                            }
                        }
                        
                        // 策略5: 从旧格式的key中提取字段名进行匹配
                        if (enumOptions.length === 0) {
                            console.log('  尝试策略5 - 从key中提取字段名匹配...');
                            for (const configKey in sectionConfig) {
                                // 匹配 field_数字_字段名 格式
                                const match = configKey.match(/^field_\d+_(.+)$/);
                                if (match) {
                                    const extractedName = match[1];
                                    const normalizedExtracted = extractedName.toLowerCase().replace(/[_\s-]/g, '');
                                    
                                    console.log(`    从 "${configKey}" 提取字段名: "${extractedName}", 标准化="${normalizedExtracted}"`);
                                    
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
                    
                    // 如果所有策略都失败，提供默认选项
                    if (enumOptions.length === 0) {
                        console.warn(`❌ 未找到字段 ${columnName} 的枚举配置，使用默认值`);
                        console.warn(`提示: 请确保在创建模板时保存了枚举配置`);
                        enumOptions = [
                            { label: '选项1', value: '选项1' },
                            { label: '选项2', value: '选项2' }
                        ];
                    }
                }
                
                // 格式化显示名称：字段名 (类型)
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
        // 格式化枚举选项标签显示
        formatEnumLabel(option) {
            // 如果 value 为空或与 label 相同，只显示 label
            if (!option.value || option.value === option.label) {
                return option.label;
            }
            // 否则显示 "A: 固体" 的格式
            return `${option.label}: ${option.value}`;
        },
        async handleSubmit() {
            console.log('========== 开始提交数据 ==========');
            console.log('原始表单数据:', this.formData);
            console.log('字段区域映射:', this.fieldSectionMap);
            
            // 根据区域分类数据
            const object = {};
            const operation = {};
            const result = {};
            
            // 遍历表单数据，根据字段所属区域进行分类
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
            
            // 从对象区域中查找样品编号字段
            // 可能的字段名：样品编号、sample_serial、sampleSerial、样本编号等
            const sampleSerialFieldNames = ['样品编号', 'sample_serial', 'sampleSerial', '样本编号', '样本序列号'];
            let sampleSerial = '';
            
            for (const fieldName of sampleSerialFieldNames) {
                if (object[fieldName]) {
                    sampleSerial = object[fieldName];
                    console.log(`找到样品序列号字段: ${fieldName} = ${sampleSerial}`);
                    break;
                }
            }
            
            // 如果没找到，尝试模糊匹配（字段名包含"样品"或"编号"或"serial"）
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
            
            // 验证样本序列号
            if (!sampleSerial || sampleSerial.trim() === '') {
                this.$message.warning('请在对象区域填写样品编号');
                return;
            }
            
            // 构造请求参数
            const requestData = {
                module_id: this.moduleId,
                sample_serial: sampleSerial,
                object: object,
                operation: operation,
                result: result
            };
            
            console.log('请求参数:', JSON.stringify(requestData, null, 2));
            
            // 调用API接口
            this.loading = true;
            try {
                const response = await this.$request.post(
                    '/basemodule/moduledata/insertsingle',
                    requestData
                );
                
                console.log('API响应:', response.data);
                
                if (response.data && response.data.code === 0) {
                    this.$message.success('数据提交成功！');
                    // 清空表单
                    this.formData = {};
                    this.handleClose();
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
.dialog-content {
    display: flex;
    height: 65vh;
    overflow-x: hidden;
}

.sidebar {
    width: 250px;
    min-width: 250px;
    border-right: 1px solid #e0e0e0;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 10px;
}

.content-area {
    flex: 1;
    min-width: 0;
    padding-left: 20px;
    padding-right: 10px;
    overflow-y: auto;
    overflow-x: hidden;
}

.placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #909399;
}

.data-entry-dialog .el-dialog__body {
    padding: 10px 20px;
    overflow-x: hidden;
}

/* 确保表单元素不会超出容器 */
.content-area >>> .el-form {
    width: 100%;
    max-width: 100%;
}

.content-area >>> .el-form-item__content {
    max-width: 100%;
}

.content-area >>> .el-select,
.content-area >>> .el-input {
    max-width: 100%;
}
</style>

