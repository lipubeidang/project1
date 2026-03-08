<template>
    <el-dialog
        :visible.sync="dialogVisible"
        :title="title"
        width="80%"
        :before-close="handleClose"
        custom-class="template-detail-dialog"
        :close-on-click-modal="false"
        :modal="false"
        :append-to-body="true"
        :lock-scroll="false"
        :close-on-press-escape="true"
        :modal-append-to-body="false"
        v-loading="loading"
        element-loading-text="正在加载数据..."
    >
        <div class="dialog-content">
            <!-- Left Sidebar -->
            <div class="sidebar">
                <div class="sidebar-title">数据结构</div>
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
                <div v-if="selectedNodeData.length > 0" class="data-display">
                    <div class="data-header">
                        <i class="el-icon-document"></i>
                        <h3>{{ selectedNode.label }}</h3>
                    </div>
                    <el-table :data="selectedNodeData" border style="width: 100%">
                        <el-table-column prop="label" label="字段" width="200"></el-table-column>
                        <el-table-column prop="value" label="值"></el-table-column>
                    </el-table>
                </div>
                <div v-else class="placeholder">
                    <i class="el-icon-info"></i>
                    <p>请从左侧选择一个节点查看详细信息</p>
                </div>
            </div>
        </div>
        <span slot="footer" class="dialog-footer">
            <el-button @click="handleClose" class="close-btn">关 闭</el-button>
        </span>
    </el-dialog>
</template>

<script>
export default {
    name: 'TemplateDetailDialog',
    props: {
        visible: {
            type: Boolean,
            default: false
        },
        title: {
            type: String,
            default: '数据详情'
        },
        moduleId: {
            type: [String, Number],
            default: null
        },
        sampleSerial: {
            type: String,
            default: null
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
            selectedNodeData: [],
            moduleData: {},
            columnInfo: {},
            loading: false
        };
    },
    watch: {
        visible(newVal) {
            this.dialogVisible = newVal;
            if (newVal) {
                this.loadDetailData();
            }
        }
    },
    methods: {
        async loadDetailData() {
            if (!this.moduleId || !this.sampleSerial) {
                this.$message.warning('缺少必要的参数来加载数据');
                return;
            }
            this.loading = true;
            try {
                // Fetch column info
                let columnInfo = {};
                try {
                    const columnResponse = await this.$request.get(`/basemodule/moduledata/getColumnInfo/${this.moduleId}`);
                    if (columnResponse.data && columnResponse.data.code === 0) {
                        const rawColumnInfo = columnResponse.data.columnInfo || columnResponse.data.data || {};
                        // columnInfo 可以是对象 {object: [], operation: [], result: []} 或数组
                        columnInfo = rawColumnInfo;
                    }
                } catch (columnError) {
                    console.warn('获取字段信息失败:', columnError);
                }
                this.columnInfo = columnInfo;

                // Fetch detail data
                console.log('========== 请求详情数据 ==========');
                console.log('请求参数:', { sampleSerial: this.sampleSerial, moduleId: String(this.moduleId) });
                
                const response = await this.$request.post('/basemodule/moduledata/getdetail', {
                    sampleSerial: this.sampleSerial,
                    moduleId: String(this.moduleId)
                });

                console.log('详情数据响应:', response.data);

                if (response.data && response.data.code === 0) {
                    this.moduleData = response.data.moduleData;
                    console.log('设置 moduleData 后:', this.moduleData);
                    this.buildDirectoryTree();
                } else {
                    console.error('❌ 响应错误:', response.data);
                    throw new Error(response.data.msg || '获取详细数据失败');
                }
            } catch (error) {
                console.error('获取详细数据失败:', error);
                this.$message.error('获取详细数据失败: ' + (error.message || '请重试'));
            } finally {
                this.loading = false;
            }
        },
        handleClose() {
            this.$emit('update:visible', false);
        },
        buildDirectoryTree() {
            console.log('========== buildDirectoryTree 开始 ==========');
            console.log('moduleId:', this.moduleId);
            console.log('sampleSerial:', this.sampleSerial);
            console.log('完整的 moduleData:', this.moduleData);
            console.log('完整的 columnInfo:', this.columnInfo);
            
            // 确保 columnInfo 存在
            if (!this.columnInfo) {
                this.columnInfo = {};
            }

            const { objectList = [], operationList = [], resultList = [] } = this.moduleData;
            
            console.log('objectList 长度:', objectList.length, '内容:', objectList);
            console.log('operationList 长度:', operationList.length, '内容:', operationList);
            console.log('resultList 长度:', resultList.length, '内容:', resultList);

            if (objectList.length === 0) {
                console.warn('❌ objectList 为空，无法构建树形结构');
                this.directoryTree = [];
                return;
            }

            const formatDataForDisplay = (item, type) => {
                // 从 columnInfo 中获取对应类型的字段信息
                let columnInfoForType = [];
                
                if (this.columnInfo[type] && Array.isArray(this.columnInfo[type])) {
                    columnInfoForType = this.columnInfo[type];
                } else if (Array.isArray(this.columnInfo)) {
                    columnInfoForType = this.columnInfo.filter(c => c.section === type);
                }

                // 智能字段名匹配函数：处理带下划线和不带下划线的字段名
                const findValueByColumnName = (item, columnName) => {
                    console.log(`🔍 查找字段 "${columnName}" 的值...`);
                    console.log('可用字段:', Object.keys(item));
                    
                    // 1. 直接匹配
                    if (item[columnName] !== undefined && item[columnName] !== null) {
                        console.log(`✅ 直接匹配成功: ${columnName} = ${item[columnName]}`);
                        return item[columnName];
                    }
                    
                    // 2. 智能添加下划线 (objectname1 -> object_name1, operationname2 -> operation_name2)
                    // 匹配 xxxname + 数字 的模式
                    const withUnderscorePattern1 = columnName.replace(/([a-z]+)(name)([0-9]+)/gi, '$1_$2_$3');
                    if (item[withUnderscorePattern1] !== undefined && item[withUnderscorePattern1] !== null) {
                        console.log(`✅ 模式1匹配成功: ${columnName} -> ${withUnderscorePattern1} = ${item[withUnderscorePattern1]}`);
                        return item[withUnderscorePattern1];
                    }
                    
                    // 3. 通用下划线规则 (objectname1 -> object_name1)
                    const withUnderscore = columnName.replace(/([a-z])([0-9])/g, '$1_$2');
                    if (item[withUnderscore] !== undefined && item[withUnderscore] !== null) {
                        console.log(`✅ 通用下划线匹配成功: ${columnName} -> ${withUnderscore} = ${item[withUnderscore]}`);
                        return item[withUnderscore];
                    }
                    
                    // 4. 尝试移除下划线的版本 (object_name1 -> objectname1)
                    const withoutUnderscore = columnName.replace(/_/g, '');
                    if (item[withoutUnderscore] !== undefined && item[withoutUnderscore] !== null) {
                        console.log(`✅ 移除下划线匹配成功: ${columnName} -> ${withoutUnderscore} = ${item[withoutUnderscore]}`);
                        return item[withoutUnderscore];
                    }
                    
                    // 5. 不区分大小写匹配
                    const lowerColumnName = columnName.toLowerCase();
                    for (const key in item) {
                        if (key.toLowerCase() === lowerColumnName) {
                            console.log(`✅ 不区分大小写匹配成功: ${columnName} -> ${key} = ${item[key]}`);
                            return item[key];
                        }
                    }
                    
                    // 6. 模糊匹配：尝试在所有字段中找相似的
                    const normalizedColumnName = columnName.replace(/_/g, '').toLowerCase();
                    for (const key in item) {
                        const normalizedKey = key.replace(/_/g, '').toLowerCase();
                        if (normalizedKey === normalizedColumnName) {
                            console.log(`✅ 模糊匹配成功: ${columnName} -> ${key} = ${item[key]}`);
                            return item[key];
                        }
                    }
                    
                    console.warn(`❌ 未找到匹配字段: ${columnName}`);
                    return null;
                };

                if (columnInfoForType.length > 0) {
                    return columnInfoForType.map(c => {
                        const columnName = c.column_name || c.columnName || c.fieldName;
                        const contribution = c.column_contribution || c.columnContribution || '';
                        const displayName = c.displayName || columnName;
                        
                        // 使用智能匹配函数获取值
                        const value = findValueByColumnName(item, columnName);
                        
                        // 字段名后加上类型（如果有的话）
                        const labelWithType = contribution 
                            ? `${displayName} (${contribution})` 
                            : displayName;
                        
                        return {
                            label: labelWithType,
                            value: value !== null && value !== undefined && value !== '' ? value : '-'
                        };
                    });
                }
                
                // 如果没有字段信息，直接从 item 中提取
                return Object.keys(item)
                    .filter(key => !['id', 'create_time', 'sample_serial', 'operation_id'].includes(key))
                    .map(key => ({ label: key, value: item[key] }));
            };
            
            // 构建树形结构的根节点数组
            this.directoryTree = [];

            // 1. 对象区域
            if (objectList.length > 0) {
                const objectItem = objectList[0];
                const objectAreaNode = {
                    id: 'object_area',
                    label: '对象区域',
                    data: [],
                    children: [{
                        id: `object_${objectItem.id}`,
                        label: '对象字段',
                        data: formatDataForDisplay(objectItem, 'object'),
                        children: []
                    }]
                };
                this.directoryTree.push(objectAreaNode);
            }

            // 2. 操作区域
            if (operationList.length > 0) {
                const operationAreaNode = {
                    id: 'operation_area',
                    label: '操作区域',
                    data: [],
                    children: operationList.map((operation, index) => {
                        // 查找该操作对应的所有结果
                        const matchedResults = resultList.filter(result => 
                            result.operation_id === operation.id
                        );
                        
                        // 构建子节点数组：先添加操作字段，再添加结果
                        const operationChildren = [];
                        
                        // 添加操作字段节点
                        operationChildren.push({
                            id: `operation_field_${operation.id}`,
                            label: '操作字段',
                            data: formatDataForDisplay(operation, 'operation'),
                            children: []
                        });
                        
                        // 添加结果节点
                        matchedResults.forEach((result, resultIndex) => {
                            operationChildren.push({
                                id: `result_${result.id}`,
                                label: `结果${resultIndex + 1}`,
                                data: formatDataForDisplay(result, 'result'),
                                children: []
                            });
                        });

                        return {
                            id: `operation_${operation.id}`,
                            label: `操作${index + 1}`,
                            data: [],
                            children: operationChildren
                        };
                    })
                };
                this.directoryTree.push(operationAreaNode);
            }

            // 3. 结果区域（显示所有没有匹配到操作的独立结果）
            if (resultList.length > 0) {
                // 收集所有已匹配的operation_id
                const matchedOperationIds = new Set(operationList.map(op => op.id));
                
                // 筛选出没有匹配到操作的结果
                const unmatchedResults = resultList.filter(result => 
                    !result.operation_id || !matchedOperationIds.has(result.operation_id)
                );

                // 只有存在未匹配的结果时才显示结果区域
                if (unmatchedResults.length > 0) {
                    const resultAreaNode = {
                        id: 'result_area',
                        label: '结果区域',
                        data: [],
                        children: unmatchedResults.map((result, index) => ({
                            id: `result_${result.id}`,
                            label: `结果${index + 1}`,
                            data: formatDataForDisplay(result, 'result'),
                            children: []
                        }))
                    };
                    this.directoryTree.push(resultAreaNode);
                }
            }

            // 默认选中第一个有数据的节点
            if (this.directoryTree.length > 0) {
                let firstNode = this.directoryTree[0];
                if (firstNode.children && firstNode.children.length > 0) {
                    firstNode = firstNode.children[0];
                }
                this.handleNodeClick(firstNode);
            }
        },
        getSectionLabel(type) {
            switch(type) {
                case 'object': return '对象';
                case 'operation': return '操作';
                case 'result': return '结果';
                default: return '项目';
            }
        },
        handleNodeClick(node) {
            if (node.data && node.data.length > 0) {
                this.selectedNode = node;
                this.selectedNodeData = node.data;
            } else {
                this.selectedNode = {};
                this.selectedNodeData = [];
            }
        }
    }
};
</script>

<style scoped>
.dialog-content {
    display: flex;
    height: 65vh;
    gap: 20px;
    /* GPU硬件加速 */
    -webkit-transform: translate3d(0, 0, 0);
    transform: translate3d(0, 0, 0);
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
}

.sidebar {
    width: 280px;
    background: rgba(255, 255, 255, 0.98);
    /* 🚀 性能优化：移除backdrop-filter（性能杀手） */
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border-radius: 16px;
    /* 简化阴影提升性能 */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08),
                0 0 0 1px rgba(102, 126, 234, 0.1) inset;
    border: 2px solid rgba(102, 126, 234, 0.15);
    padding: 20px;
    overflow-y: auto;
    /* 🚀 优化动画时长到0.2s（60fps黄金时长） */
    transition: box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1),
                border-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    /* GPU硬件加速 */
    -webkit-transform: translate3d(0, 0, 0);
    transform: translate3d(0, 0, 0);
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
    will-change: box-shadow, border-color;
}

.sidebar:hover {
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15),
                0 0 0 1px rgba(102, 126, 234, 0.2) inset;
    border-color: rgba(102, 126, 234, 0.3);
}

.sidebar-title {
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

.content-area {
    flex: 1;
    background: rgba(255, 255, 255, 0.98);
    /* 🚀 性能优化：移除backdrop-filter（性能杀手） */
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border-radius: 16px;
    /* 简化阴影提升性能 */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08),
                0 0 0 1px rgba(102, 126, 234, 0.1) inset;
    border: 2px solid rgba(102, 126, 234, 0.15);
    padding: 25px;
    overflow-y: auto;
    /* 🚀 优化动画时长到0.2s（60fps黄金时长） */
    transition: box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1),
                border-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    /* GPU硬件加速 */
    -webkit-transform: translate3d(0, 0, 0);
    transform: translate3d(0, 0, 0);
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
    will-change: box-shadow, border-color;
}

.content-area:hover {
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15),
                0 0 0 1px rgba(102, 126, 234, 0.2) inset;
    border-color: rgba(102, 126, 234, 0.3);
}

.data-display {
    /* 🚀 优化动画时长到0.25s（60fps黄金时长） */
    animation: fadeIn 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    /* GPU硬件加速 */
    -webkit-transform: translate3d(0, 0, 0);
    transform: translate3d(0, 0, 0);
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
    will-change: opacity, transform;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translate3d(0, 8px, 0);
    }
    to {
        opacity: 1;
        transform: translate3d(0, 0, 0);
    }
}

.data-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid rgba(102, 126, 234, 0.2);
}

.data-header i {
    font-size: 24px;
    color: #667eea;
}

.data-header h3 {
    margin: 0;
    font-size: 20px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.5px;
}

.placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 15px;
    color: #909399;
}

.placeholder i {
    font-size: 48px;
    color: #dcdfe6;
}

.placeholder p {
    font-size: 15px;
    color: #909399;
}

/* 滚动条样式 */
.sidebar::-webkit-scrollbar,
.content-area::-webkit-scrollbar {
    width: 8px;
}

.sidebar::-webkit-scrollbar-thumb,
.content-area::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    border-radius: 4px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    /* GPU加速滚动条 */
    transform: translate3d(0, 0, 0);
}

.sidebar::-webkit-scrollbar-thumb:hover,
.content-area::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
    /* 简化阴影提升性能 */
    box-shadow: 0 0 8px rgba(102, 126, 234, 0.4);
}

.sidebar::-webkit-scrollbar-track,
.content-area::-webkit-scrollbar-track {
    background: rgba(245, 247, 250, 0.5);
    border-radius: 4px;
}

/* 🚀 优化滚动性能 - 使用GPU加速 */
.sidebar,
.content-area {
    -webkit-overflow-scrolling: touch;
    scroll-behavior: smooth;
    /* 优化渲染性能 */
    contain: layout style paint;
}

/* 树节点样式 */
.sidebar >>> .el-tree {
    background: transparent;
    font-size: 15px;
}

.sidebar >>> .el-tree-node__content {
    height: 40px;
    border-radius: 10px;
    margin-bottom: 5px;
    /* 🚀 优化动画时长到0.2s */
    transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1),
                color 0.2s cubic-bezier(0.4, 0, 0.2, 1),
                transform 0.2s cubic-bezier(0.4, 0, 0.2, 1),
                box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 0 12px;
    /* GPU硬件加速 */
    -webkit-transform: translate3d(0, 0, 0);
    transform: translate3d(0, 0, 0);
    will-change: transform, background-color;
}

.sidebar >>> .el-tree-node__content:hover {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
    transform: translate3d(3px, 0, 0);
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.12);
}

.sidebar >>> .el-tree-node.is-current > .el-tree-node__content {
    background: rgba(102, 126, 234, 0.15);
    color: #667eea;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
}

/* 表格样式 */
.content-area >>> .el-table {
    border-radius: 10px;
    overflow: hidden;
    /* GPU硬件加速 */
    -webkit-transform: translate3d(0, 0, 0);
    transform: translate3d(0, 0, 0);
    will-change: transform;
}

.content-area >>> .el-table th {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
    font-weight: 600;
}

.content-area >>> .el-table tbody tr {
    /* 🚀 优化表格行悬停动画 */
    transition: background-color 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

.content-area >>> .el-table tbody tr:hover {
    background: rgba(102, 126, 234, 0.05);
}

.content-area >>> .el-table td,
.content-area >>> .el-table th {
    border-color: rgba(102, 126, 234, 0.1);
}
</style>

<style>
/* 弹窗基础样式 */
.template-detail-dialog {
    margin-top: 5vh !important;
    margin-bottom: 5vh !important;
}

/* 🚀 优化对话框打开/关闭动画性能 */
.template-detail-dialog.el-dialog__wrapper {
    transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.template-detail-dialog.el-dialog__wrapper .el-dialog {
    /* 优化对话框进入动画 */
    animation: dialogFadeIn 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    /* GPU硬件加速 */
    -webkit-transform: translate3d(0, 0, 0);
    transform: translate3d(0, 0, 0);
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
    will-change: transform, opacity;
}

@keyframes dialogFadeIn {
    from {
        opacity: 0;
        transform: translate3d(0, -20px, 0) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translate3d(0, 0, 0) scale(1);
    }
}

.template-detail-dialog .el-dialog {
    background: rgba(255, 255, 255, 0.99);
    /* 🚀 性能优化：移除backdrop-filter（性能杀手） */
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border-radius: 20px;
    /* 简化阴影提升性能 */
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2),
                0 0 0 1px rgba(102, 126, 234, 0.1) inset;
    border: 2px solid rgba(102, 126, 234, 0.2);
    /* GPU硬件加速 */
    -webkit-transform: translate3d(0, 0, 0);
    transform: translate3d(0, 0, 0);
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
    will-change: transform;
}

.template-detail-dialog .el-dialog__header {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.05) 0%, 
        rgba(118, 75, 162, 0.05) 100%);
    border-radius: 20px 20px 0 0;
    border-bottom: 2px solid rgba(102, 126, 234, 0.1);
    padding: 25px 30px;
}

.template-detail-dialog .el-dialog__title {
    font-size: 22px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.5px;
}

.template-detail-dialog .el-dialog__body {
    padding: 25px 30px;
    overflow-y: auto;
    max-height: calc(90vh - 180px);
}

.template-detail-dialog .el-dialog__footer {
    border-top: 2px solid rgba(102, 126, 234, 0.1);
    padding: 20px 30px;
}

/* 按钮样式 */
.close-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: white;
    padding: 10px 24px;
    font-weight: 600;
    /* 🚀 优化动画时长到0.2s */
    transition: background 0.2s cubic-bezier(0.4, 0, 0.2, 1),
                transform 0.2s cubic-bezier(0.4, 0, 0.2, 1),
                box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    /* GPU硬件加速 */
    -webkit-transform: translate3d(0, 0, 0);
    transform: translate3d(0, 0, 0);
    will-change: transform, background;
}

.close-btn:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: translate3d(0, -2px, 0);
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.35);
}
</style>
