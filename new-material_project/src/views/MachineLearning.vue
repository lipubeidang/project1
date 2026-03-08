<template>
    <div class="machine-learning-page" :key="componentKey">
        <Navbar @dropdown-action="handleDropdownAction" />
        <TemplateNavbar @nav-action="handleNavAction" @audit-action="handleAuditAction" />
        
        <!-- 隐藏的文件输入，用于选择 xlsx 文件 -->
        <input 
            ref="fileInput" 
            type="file" 
            accept=".xlsx,.xls" 
            style="display: none;" 
            @change="handleFileSelect"
        />

        <!-- 主要内容区域 -->
        <div class="main-content">
            <!-- 左侧分类菜单 -->
            <div class="sidebar">
                 <div class="category-list">
                    <el-tree
                        :data="directoryTree"
                        :props="defaultProps"
                        @node-click="handleNodeClick"
                        :default-expanded-keys="['big_cat_1']"
                        node-key="id"
                        highlight-current
                    ></el-tree>
                 </div>
            </div>

            <!-- 右侧内容区域 -->
            <div class="content-area">
                <!-- 机器学习按钮栏区域 -->
                <div class="header-section">
                    <div class="ml-button-bar">
                        <div class="button-bar-header">
                            <span class="section-label">机器学习</span>
                            <h2 class="content-title">{{ currentNode?.name || '请选择模板' }}</h2>
                        </div>
                        <div class="button-group">
                            <el-button 
                                type="primary" 
                                icon="el-icon-data-analysis"
                                @click="handleMLAction('transform')"
                                :disabled="!currentNode"
                            >
                                数据转换
                            </el-button>
                            <el-button 
                                type="success" 
                                icon="el-icon-s-data"
                                @click="handleMLAction('augment')"
                                :disabled="!currentNode || selectedDataRows.length === 0"
                            >
                                数据增强
                            </el-button>
                            <el-button 
                                type="warning" 
                                icon="el-icon-view"
                                @click="handleMLAction('train')"
                                :disabled="!currentNode || selectedDataRows.length === 0"
                            >
                                模型训练
                            </el-button>
                            <el-button 
                                type="danger" 
                                icon="el-icon-star-on"
                                @click="handleSinteringCurve"
                                :disabled="!currentNode"
                            >
                                烧结曲线推荐
                            </el-button>
                        </div>
                    </div>
                </div>

                <!-- 表名选择区域（数据转换后显示） -->
                <div class="table-select-box" v-if="showTransformTables && transformTables.length > 0">
                    <div class="filter-header">
                        <span class="filter-title">
                            <i class="el-icon-s-grid"></i>
                            数据表选择
                        </span>
                        <span class="selected-count">共 {{ transformTables.length }} 张表</span>
                    </div>
                    <div class="table-tabs-container">
                        <el-tabs 
                            v-model="currentTableIndex" 
                            @tab-click="handleTableTabClick"
                            type="card"
                        >
                            <el-tab-pane 
                                v-for="(table, index) in transformTables" 
                                :key="index"
                                :label="table.name"
                                :name="String(index)"
                            >
                            </el-tab-pane>
                        </el-tabs>
                    </div>
                </div>
                
                <!-- 列字段选择区域（非数据转换模式显示） -->
                <div class="column-filter-box" v-if="!showTransformTables && expandedTableData.length > 0">
                    <div class="filter-header">
                        <span class="filter-title">
                            <i class="el-icon-s-grid"></i>
                            列字段选择
                        </span>
                        <span class="selected-count">已选择 {{ checkedColumns.length }} / {{ allAvailableColumns.length }} 列</span>
                    </div>
                    <div class="filter-content">
                        <el-checkbox 
                            :indeterminate="isIndeterminate" 
                            v-model="checkAll"
                            @change="handleCheckAllChange"
                            class="check-all-box"
                        >
                            全选
                        </el-checkbox>
                        <div class="checkbox-group-container">
                            <el-checkbox-group 
                                v-model="checkedColumns" 
                                @change="handleCheckedColumnsChange"
                                class="column-checkbox-group"
                            >
                                <el-checkbox 
                                    v-for="col in allAvailableColumns" 
                                    :label="col.prop" 
                                    :key="col.prop"
                                    class="column-checkbox"
                                >
                                    {{ col.label }}
                                </el-checkbox>
                            </el-checkbox-group>
                        </div>
                        <div class="filter-actions">
                            <el-button type="primary" size="small" @click="applyColumnFilter">
                                <i class="el-icon-check"></i>
                                应用选择
                            </el-button>
                            <el-button size="small" @click="resetColumnFilter">
                                <i class="el-icon-refresh"></i>
                                重置
                            </el-button>
                        </div>
                    </div>
                </div>

                <!-- 表格 -->
                <div class="table-container">
                    <el-empty v-if="!showTransformTables && expandedTableData.length === 0 && !currentNode" description="请从左侧选择模板查看数据" :image-size="120">
                        <template slot="image">
                            <i class="el-icon-folder-opened" style="font-size: 80px; color: #dcdfe6;"></i>
                        </template>
                    </el-empty>
                    <el-empty v-else-if="!showTransformTables && expandedTableData.length === 0 && currentNode && currentNode.isTemplate" description="该模板暂无数据" :image-size="100"></el-empty>
                    <el-empty v-else-if="showTransformTables && totalDataCount === 0" description="当前表暂无数据" :image-size="100"></el-empty>
                    <template v-else>
                        <div class="table-scroll-box">
                            <el-table
                                ref="dataTable"
                                :data="displayTableData"
                                v-loading="loading"
                                element-loading-text="正在加载数据..."
                                element-loading-spinner="el-icon-loading"
                                stripe
                                style="width: 100%; min-width: 100%"
                                :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
                                border
                                @selection-change="handleSelectionChange"
                                @select-all="handleSelectAll"
                            >
                                <!-- 选择列 -->
                                <el-table-column
                                    type="selection"
                                    width="55"
                                    align="center"
                                />
                                
                                <el-table-column
                                    label="序号"
                                    width="80"
                                    align="center"
                                    :index="getIndex"
                                    type="index"
                                />
                                
                                <!-- 动态列 -->
                                <el-table-column
                                    v-for="col in displayColumns"
                                    :key="col.prop"
                                    :prop="col.prop"
                                    :label="col.label"
                                    :width="col.width || 200"
                                    show-overflow-tooltip
                                >
                                    <template slot-scope="scope">
                                        {{
                                            scope.row[col.prop] === null || 
                                            scope.row[col.prop] === undefined || 
                                            scope.row[col.prop] === ''
                                                ? '-'
                                                : scope.row[col.prop]
                                        }}
                                    </template>
                                </el-table-column>
                            </el-table>
                        </div>
                    </template>

                    <!-- 分页 -->
                    <div class="pagination">
                        <el-pagination
                            @size-change="handleSizeChange"
                            @current-change="handleCurrentChange"
                            :current-page.sync="currentPage"
                            :page-sizes="[20, 50, 100, 200]"
                            :page-size.sync="pageSize"
                            :pager-count="7"
                            layout="total, sizes, prev, pager, next, jumper"
                            :total="totalDataCount"
                            :disabled="totalDataCount === 0"
                        />
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 模型训练进度条对话框 -->
        <el-dialog
            title="模型训练中"
            :visible.sync="showTrainingProgress"
            :close-on-click-modal="false"
            :close-on-press-escape="false"
            :show-close="false"
            width="500px"
            center
        >
            <div class="training-progress-container">
                <el-progress 
                    :percentage="trainingProgress" 
                    :status="trainingProgress === 100 ? 'success' : ''"
                    :stroke-width="20"
                ></el-progress>
                <p class="progress-text">{{ trainingProgressText }}</p>
            </div>
        </el-dialog>
        
        <!-- 训练完成提示对话框 -->
        <el-dialog
            title="训练完成"
            :visible.sync="showTrainingComplete"
            width="400px"
            center
        >
            <div class="training-complete-container">
                <i class="el-icon-success" style="font-size: 48px; color: #67C23A; margin-bottom: 20px;"></i>
                <p style="font-size: 16px; margin-bottom: 20px;">模型训练已完成！</p>
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button type="primary" @click="handleMymodelClick">Mymodel</el-button>
                <el-button @click="handleTrainingComplete">完成</el-button>
            </span>
        </el-dialog>
        
        <!-- 图片显示弹窗 -->
        <el-dialog
            title="训练结果"
            :visible.sync="showImageDialog"
            width="80%"
            center
            :before-close="handleImageDialogClose"
        >
            <div class="image-dialog-container">
                <img 
                    v-if="imageUrl" 
                    :src="imageUrl" 
                    alt="训练结果图片" 
                    class="result-image"
                    @error="handleImageError"
                />
                <div v-else class="image-loading">
                    <i class="el-icon-loading" style="font-size: 32px;"></i>
                    <p>正在加载图片...</p>
                </div>
                
                <!-- 训练数据展示区域 -->
                <div class="training-metrics-container" v-if="imageUrl">
                    <div class="metrics-header">
                        <i class="el-icon-data-analysis"></i>
                        <span>训练指标</span>
                    </div>
                    <div class="metrics-content">
                        <div class="metrics-row">
                            <div class="metric-item">
                                <span class="metric-label">最佳轮次 (Best Epoch):</span>
                                <span class="metric-value">{{ trainingMetrics.best_epoch }}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">最佳损失 (Best Loss):</span>
                                <span class="metric-value">{{ trainingMetrics.best_loss.toFixed(9) }}</span>
                            </div>
                        </div>
                        <div class="metrics-divider"></div>
                        <div class="metrics-section">
                            <h4 class="section-title">训练集指标</h4>
                            <div class="metrics-row">
                                <div class="metric-item">
                                    <span class="metric-label">R² 分数:</span>
                                    <span class="metric-value">{{ trainingMetrics.train_r2.toFixed(6) }}</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">平均绝对误差 (MAE):</span>
                                    <span class="metric-value">{{ trainingMetrics.train_mae.toFixed(6) }}</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">均方根误差 (RMSE):</span>
                                    <span class="metric-value">{{ trainingMetrics.train_rmse.toFixed(6) }}</span>
                                </div>
                            </div>
                        </div>
                        <div class="metrics-divider"></div>
                        <div class="metrics-section">
                            <h4 class="section-title">测试集指标</h4>
                            <div class="metrics-row">
                                <div class="metric-item">
                                    <span class="metric-label">R² 分数:</span>
                                    <span class="metric-value">{{ trainingMetrics.test_r2.toFixed(6) }}</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">平均绝对误差 (MAE):</span>
                                    <span class="metric-value">{{ trainingMetrics.test_mae.toFixed(6) }}</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">均方根误差 (RMSE):</span>
                                    <span class="metric-value">{{ trainingMetrics.test_rmse.toFixed(6) }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import TemplateNavbar from '../components/TemplateNavbar.vue';
import * as XLSX from 'xlsx';

export default {
    name: "MachineLearning",
    components: {
        Navbar,
        TemplateNavbar
    },
    data() {
        return {
            componentKey: 0,
            directoryTree: [],
            defaultProps: {
                children: 'children',
                label: 'name'
            },
            currentNode: null,
            tableData: [],
            expandedTableData: [], // 展开后的数据（一个对象一个操作一个结果为一行）
            currentPage: 1,
            pageSize: 20,
            total: 0,
            dynamicColumns: [], // 动态列
            loading: false,
            isDetailDialogVisible: false,
            detailModuleId: null,
            detailSampleSerial: null,
            selectedDataRows: [], // 选中的数据行
            allSelectedRows: new Set(), // 所有选中的数据行（使用Set存储，用于跨页选择）
            tableRef: null, // 表格引用
            columnInfo: {}, // 存储字段信息
            // 列字段选择相关
            allAvailableColumns: [], // 所有可用的列
            checkedColumns: [], // 选中的列
            checkAll: true, // 全选状态
            isIndeterminate: false, // 半选状态
            // xlsx 文件数据相关
            xlsxFileData: [], // 从 xlsx 文件读取的原始数据
            currentFilterMode: null, // 当前过滤模式：'transform' 或 'augment'
            // 数据转换后的5张表
            transformTables: [], // 存储5张表的数据 [{name: '表1', data: [], originalData: [], isAugmented: false}, ...]
            currentTableIndex: '0', // 当前选中的表索引（字符串类型，用于tabs）
            showTransformTables: false, // 是否显示转换后的表
            // 模型训练相关
            showTrainingProgress: false, // 显示训练进度条
            trainingProgress: 0, // 训练进度百分比
            trainingProgressText: '正在初始化...', // 进度条文本
            trainingTimer: null, // 训练定时器
            showTrainingComplete: false, // 显示训练完成对话框
            // 图片显示相关
            showImageDialog: false, // 显示图片弹窗
            imageUrl: '', // 图片URL
            // 训练数据
            trainingMetrics: {
                best_epoch: 256,
                best_loss: 0.000121340970890411,
                train_r2: 0.8337273178478967,
                train_mae: 0.06201135360633358,
                train_rmse: 0.09560802050034772,
                test_r2: 0.8900385499000549,
                test_mae: 0.18664707243442535,
                test_rmse: 0.2735595703125
            }
        }
    },
    computed: {
        // 显示的表格数据（分页后的展开数据）
        displayTableData() {
            // 如果显示转换后的表，使用当前表的数据
            if (this.showTransformTables && this.transformTables.length > 0) {
                const currentTable = this.transformTables[parseInt(this.currentTableIndex)];
                if (currentTable && currentTable.data) {
                    const start = (this.currentPage - 1) * this.pageSize;
                    const end = start + this.pageSize;
                    return currentTable.data.slice(start, end);
                }
                return [];
            }
            // 否则使用原来的数据
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            return this.expandedTableData.slice(start, end);
        },
        // 获取所有数据（不分页）
        allTableData() {
            if (this.showTransformTables && this.transformTables.length > 0) {
                const currentTable = this.transformTables[parseInt(this.currentTableIndex)];
                if (currentTable && currentTable.data) {
                    return currentTable.data;
                }
                return [];
            }
            return this.expandedTableData;
        },
        // 要显示的列（根据用户选择过滤）
        displayColumns() {
            // 如果显示转换后的表，使用当前表的列
            if (this.showTransformTables && this.transformTables.length > 0) {
                const currentTable = this.transformTables[parseInt(this.currentTableIndex)];
                if (currentTable && currentTable.columns) {
                    return currentTable.columns;
                }
            }
            // 否则使用原来的列选择逻辑
            if (this.checkedColumns.length === 0) {
                return this.dynamicColumns;
            }
            return this.dynamicColumns.filter(col => this.checkedColumns.includes(col.prop));
        },
        // 总数据条数
        totalDataCount() {
            if (this.showTransformTables && this.transformTables.length > 0) {
                const currentTable = this.transformTables[parseInt(this.currentTableIndex)];
                if (currentTable && currentTable.data) {
                    return currentTable.data.length;
                }
                return 0;
            }
            return this.total;
        }
    },
    mounted() {
        console.log('MachineLearning 组件已挂载');
        this.loadDirectoryTree();
        // 自动加载预设的 Excel 文件
        this.autoLoadExcelFile();
    },
    activated() {
        console.log('MachineLearning 组件已激活');
        this.loadTemplateData();
    },
    beforeRouteEnter(to, from, next) {
        console.log('beforeRouteEnter', from.path, '->', to.path);
        next(vm => {
            vm.loadTemplateData();
            vm.forceRerender();
        });
    },
    beforeRouteUpdate(to, from, next) {
        console.log('beforeRouteUpdate', from.path, '->', to.path);
        this.loadTemplateData();
        this.forceRerender();
        next();
    },
    watch: {
        $route: {
            handler(to) {
                console.log('路由变化');
                if (to && to.path === '/machine-learning') {
                    console.log('返回到机器学习页面，重新初始化');
                    this.loadTemplateData();
                    this.forceRerender();
                }
            },
            immediate: true
        },
        // 监听表格数据变化，更新选中状态
        displayTableData: {
            handler() {
                this.$nextTick(() => {
                    this.updateTableSelection(this.displayTableData);
                });
            },
            deep: true
        },
        // 监听当前页变化
        currentPage() {
            this.$nextTick(() => {
                this.updateTableSelection(this.displayTableData);
            });
        },
        // 监听页面大小变化
        pageSize() {
            this.$nextTick(() => {
                this.updateTableSelection(this.displayTableData);
            });
        }
    },
    methods: {
        forceRerender() {
            // 强制重新渲染组件
            this.componentKey += 1;
        },
        
        // 计算序号
        getIndex(index) {
            return (this.currentPage - 1) * this.pageSize + index + 1;
        },
        
        // 处理机器学习操作
        handleMLAction(action) {
            const actionMap = {
                'transform': '数据转换',
                'augment': '数据增强',
                'train': '模型训练'
            };
            
            // 数据转换只依赖模板选择；其余操作仍需要勾选数据行
            if (action !== 'transform' && this.selectedDataRows.length === 0) {
                this.$message.warning('请先选择要处理的数据行');
                return;
            }
            
            console.log(`执行${actionMap[action]}操作:`, {
                action: action,
                template: this.currentNode,
                selectedData: this.selectedDataRows,
                dataCount: this.selectedDataRows.length
            });
            
            // 根据不同操作执行不同逻辑
            switch (action) {
                case 'transform':
                    this.handleDataTransform();
                    break;
                case 'augment':
                    this.handleDataAugment();
                    break;
                case 'train':
                    this.handleModelTraining();
                    break;
                default:
                    this.$message.info(`${actionMap[action] || '该'}功能开发中...`);
            }
        },
        
        // 处理数据转换
        async handleDataTransform() {
            // 加载5张Excel表
            await this.loadTransformTables();
        },
        
        // 加载5张Excel表
        async loadTransformTables() {
            this.loading = true;
            this.transformTables = [];
            
            // 5张Excel文件名和对应的表名（放在public目录下）
            const tableConfigs = [
                { fileName: 'geometry_edges.xlsx', tableName: 'Geometry Edges' },
                { fileName: 'geometry_nodes.xlsx', tableName: 'Geometry Nodes' },
                { fileName: 'gs_feature.xlsx', tableName: 'GS Feature' },
                { fileName: 'sinter_curve_edges.xlsx', tableName: 'Sinter Curve Edges' },
                { fileName: 'sinter_curve_nodes.xlsx', tableName: 'Sinter Curve Nodes' }
            ];
            
            try {
                // 并行加载所有表
                const loadPromises = tableConfigs.map(async (config) => {
                    let tableData = null;
                    
                    try {
                        const response = await fetch(`/${config.fileName}`);
                        if (response.ok) {
                            const arrayBuffer = await response.arrayBuffer();
                            tableData = await this.parseExcelToTableData(arrayBuffer, config.tableName);
                        } else {
                            console.warn(`文件 ${config.fileName} 不存在`);
                        }
                    } catch (error) {
                        console.warn(`加载 ${config.fileName} 失败:`, error);
                    }
                    
                    return tableData;
                });
                
                const tables = await Promise.all(loadPromises);
                
                // 过滤掉加载失败的表
                this.transformTables = tables.filter(table => table !== null);
                
                if (this.transformTables.length === 0) {
                    this.$message.warning('未找到数据转换表文件，请确保public目录下有对应的Excel文件');
                    this.loading = false;
                    return;
                }
                
                // 显示转换后的表
                this.showTransformTables = true;
                this.currentTableIndex = '0';
                this.currentPage = 1;
                
                // 清空选中状态
                this.allSelectedRows.clear();
                this.selectedDataRows = [];
                
                this.$message.success(`成功加载 ${this.transformTables.length} 张数据表`);
            } catch (error) {
                console.error('加载数据转换表失败:', error);
                this.$message.error('加载数据转换表失败，请检查文件');
            } finally {
                this.loading = false;
            }
        },
        
        // 解析Excel文件为表数据
        async parseExcelToTableData(arrayBuffer, tableName) {
            try {
                const data = new Uint8Array(arrayBuffer);
                const workbook = XLSX.read(data, { type: 'array' });
                
                // 读取第一个工作表
                const firstSheetName = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[firstSheetName];
                
                // 将工作表转换为 JSON 数组
                // 使用 defval: null 确保空单元格被识别为 null，而不是 undefined
                let jsonData = XLSX.utils.sheet_to_json(worksheet, { defval: null });
                
                if (jsonData.length === 0) {
                    return null;
                }
                
                // 调试：检查 Excel 解析出来的实际值
                console.log('=== Excel 解析调试信息 ===');
                jsonData.forEach((row, i) => {
                    if (i < 3) { // 只打印前3行
                        console.log(`row ${i}:`, row);
                        Object.keys(row).forEach(key => {
                            if (key === 'is_aug' || key.includes('is_aug')) {
                                console.log(`  ${key}:`, row[key], 'type:', typeof row[key]);
                            }
                        });
                    }
                });
                console.log('=== 调试信息结束 ===');
                
                // 处理空值：将null、undefined、空字符串转换为"-"，但保留0值
                jsonData = jsonData.map(row => {
                    const processedRow = {}
                    Object.keys(row).forEach(key => {
                        const value = row[key]
                        // 只有真正的空值才转换为"-"，0值保持不变
                        // 特别注意：0 === 0 是 true，所以 0 值不会被转换
                        if (value === null || value === undefined || value === '') {
                            processedRow[key] = '-'
                        } else {
                            processedRow[key] = value
                        }
                    })
                    return processedRow
                })
                
                // 如果是GS Feature表，初始只显示is_aug=0的数据，隐藏is_aug=1的数据
                let displayData = jsonData;
                if (tableName === 'GS Feature' || tableName.includes('GS Feature')) {
                    // 分离is_aug=0和is_aug=1的数据
                    const dataIsAug0 = jsonData.filter(row => this.getIsAugValue(row.is_aug) === 0);
                    const dataIsAug1 = jsonData.filter(row => this.getIsAugValue(row.is_aug) === 1);
                    
                    // 初始只显示is_aug=0的数据
                    displayData = dataIsAug0;
                    
                    // 根据数据自动生成列（使用所有数据生成列，以便后续显示is_aug=1的数据时列结构一致）
                    const columns = this.generateColumnsFromData(jsonData);
                    
                    return {
                        name: tableName,
                        data: displayData, // 当前显示的数据（只有is_aug=0）
                        originalData: jsonData, // 保存所有原始数据
                        dataIsAug0: dataIsAug0, // is_aug=0的数据
                        dataIsAug1: dataIsAug1, // is_aug=1的数据
                        isAugmented: false, // 是否已进行数据增强
                        columns: columns
                    };
                }
                
                // 根据数据自动生成列
                const columns = this.generateColumnsFromData(jsonData);
                
                return {
                    name: tableName,
                    data: displayData,
                    originalData: jsonData, // 保存原始数据
                    columns: columns
                };
            } catch (error) {
                console.error(`解析表 ${tableName} 失败:`, error);
                return null;
            }
        },
        
        // 获取is_aug的数值（统一转换为0或1）
        getIsAugValue(isAug) {
            if (isAug === 0 || isAug === '0' || isAug === false || isAug === 'false') {
                return 0;
            }
            if (isAug === 1 || isAug === '1' || isAug === true || isAug === 'true') {
                return 1;
            }
            // 如果不存在或无法识别，默认返回0
            return 0;
        },
        
        // 根据数据生成列
        generateColumnsFromData(data) {
            if (!data || data.length === 0) {
                return [];
            }
            
            // 收集所有字段名
            const allKeys = new Set();
            data.forEach(row => {
                Object.keys(row).forEach(key => {
                    allKeys.add(key);
                });
            });
            
            const columnArray = Array.from(allKeys);
            
            // 排序：优先显示常见字段
            const sortedColumns = columnArray.sort((a, b) => {
                const priority = ['sample_serial', 'id', 'name', 'type'];
                const aIndex = priority.indexOf(a);
                const bIndex = priority.indexOf(b);
                if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
                if (aIndex !== -1) return -1;
                if (bIndex !== -1) return 1;
                return a.localeCompare(b);
            });
            
            return sortedColumns.map(col => ({
                prop: col,
                label: this.formatColumnLabel(col),
                width: col === 'sample_serial' ? 250 : 200
            }));
        },
        
        // 处理表切换
        handleTableTabClick(tab) {
            this.currentTableIndex = tab.name;
            this.currentPage = 1; // 切换表时重置到第一页
            // 切换表时清空选中状态
            this.allSelectedRows.clear();
            this.selectedDataRows = [];
            // 更新选中状态
            this.$nextTick(() => {
                this.updateTableSelection(this.displayTableData);
            });
        },
        
        // 处理数据增强
        handleDataAugment() {
            // 如果当前显示的是转换表，且是GS Feature表，则追加is_aug=1的数据
            if (this.showTransformTables && this.transformTables.length > 0) {
                const currentTable = this.transformTables[parseInt(this.currentTableIndex)];
                if (currentTable && (currentTable.name === 'GS Feature' || currentTable.name.includes('GS Feature'))) {
                    // 如果还没有进行数据增强，则追加is_aug=1的数据
                    if (!currentTable.isAugmented && currentTable.dataIsAug1) {
                        // 将is_aug=1的数据追加到is_aug=0的数据后面
                        currentTable.data = [...currentTable.dataIsAug0, ...currentTable.dataIsAug1];
                        currentTable.isAugmented = true;
                        this.currentPage = 1; // 重置到第一页
                        this.$message.success(`数据增强完成，已显示 ${currentTable.dataIsAug1.length} 条增强数据`);
                        return;
                    } else if (currentTable.isAugmented) {
                        this.$message.info('GS Feature表已经进行过数据增强');
                        return;
                    }
                }
            }
            
            // 隐藏转换表，显示原来的列字段选择
            this.showTransformTables = false;
            
            // 如果已经读取了文件，直接过滤显示 is_aug=1 的数据
            if (this.xlsxFileData.length > 0) {
                this.filterAndDisplayData('augment');
            } else {
                // 如果还没有读取文件，先触发文件选择
                this.currentFilterMode = 'augment';
                this.$refs.fileInput.click();
            }
        },
        
        // 处理文件选择
        handleFileSelect(event) {
            const file = event.target.files[0];
            if (!file) {
                return;
            }
            
            // 检查文件类型
            const fileName = file.name.toLowerCase();
            if (!fileName.endsWith('.xlsx') && !fileName.endsWith('.xls')) {
                this.$message.error('请选择 Excel 文件（.xlsx 或 .xls）');
                return;
            }
            
            this.loading = true;
            const reader = new FileReader();
            
            reader.onload = async (e) => {
                try {
                    const arrayBuffer = e.target.result;
                    await this.parseExcelFile(arrayBuffer);
                    
                    // 根据当前模式过滤并显示数据
                    if (this.currentFilterMode) {
                        this.filterAndDisplayData(this.currentFilterMode);
                    }
                } catch (error) {
                    console.error('读取 Excel 文件失败:', error);
                    this.$message.error('读取 Excel 文件失败，请检查文件格式');
                } finally {
                    this.loading = false;
                    // 清空文件输入，以便下次可以重新选择同一个文件
                    event.target.value = '';
                }
            };
            
            reader.onerror = () => {
                this.loading = false;
                this.$message.error('读取文件失败');
                event.target.value = '';
            };
            
            reader.readAsArrayBuffer(file);
        },
        
        // 过滤并显示数据
        filterAndDisplayData(mode) {
            if (this.xlsxFileData.length === 0) {
                this.$message.warning('请先选择数据转换 xlsx 文件');
                return;
            }
            
            let filteredData = [];
            
            if (mode === 'transform') {
                // 数据转换：显示 is_aug=0 的数据
                filteredData = this.xlsxFileData.filter(row => {
                    const isAug = row.is_aug;
                    return isAug === 0 || isAug === '0' || isAug === false || isAug === 'false';
                });
                this.$message.success(`显示数据转换结果：${filteredData.length} 条数据（is_aug=0）`);
            } else if (mode === 'augment') {
                // 数据增强：显示 is_aug=1 的数据，并放在前面
                const augmentData = this.xlsxFileData.filter(row => {
                    const isAug = row.is_aug;
                    return isAug === 1 || isAug === '1' || isAug === true || isAug === 'true';
                });
                
                // 获取 is_aug=0 的数据
                const transformData = this.xlsxFileData.filter(row => {
                    const isAug = row.is_aug;
                    return isAug === 0 || isAug === '0' || isAug === false || isAug === 'false';
                });
                
                // 将 is_aug=1 的数据放在前面
                filteredData = [...augmentData, ...transformData];
                this.$message.success(`显示数据增强结果：${augmentData.length} 条增强数据在前，${transformData.length} 条原始数据在后`);
            }
            
            // 更新表格数据
            this.expandedTableData = filteredData;
            this.total = filteredData.length;
            this.currentPage = 1; // 重置到第一页
            
            // 清空选中状态
            this.allSelectedRows.clear();
            this.selectedDataRows = [];
            
            // 根据数据自动生成列
            this.setupDynamicColumnsFromData(filteredData);
        },
        
        // 处理模型训练
        handleModelTraining() {
            const trainingData = this.selectedDataRows.map(row => ({
                sample_serial: row.sample_serial,
                data_type: row.data_type,
                row_id: row.row_id,
                features: this.extractFeatures(row),
                labels: this.extractLabels(row)
            }));
            
            console.log('准备训练数据:', trainingData);
            
            this.$confirm(`确定要使用选中的 ${this.selectedDataRows.length} 条数据进行模型训练吗？`, '确认训练', {
                confirmButtonText: '开始训练',
                cancelButtonText: '取消',
                type: 'info'
            }).then(() => {
                // 跳转到模型训练页面，并传递训练数据
                this.$router.push({
                    path: '/model-training',
                    query: {
                        trainingData: JSON.stringify(trainingData)
                    }
                }).catch(() => {});
            }).catch(() => {
                this.$message.info('已取消训练');
            });
        },
        
        // 开始模型训练（带进度条）
        startTraining() {
            // 重置进度
            this.trainingProgress = 0;
            this.trainingProgressText = '正在初始化...';
            this.showTrainingProgress = true;
            
            // 总时长10秒
            const totalDuration = 10000; // 10秒 = 10000毫秒
            const updateInterval = 500; // 每500毫秒更新一次
            const progressStep = (updateInterval / totalDuration) * 100; // 每次更新的进度百分比
            
            let currentProgress = 0;
            
            // 清除之前的定时器
            if (this.trainingTimer) {
                clearInterval(this.trainingTimer);
            }
            
            // 更新进度文本的阶段
            const progressStages = [
                { progress: 0, text: '正在初始化...' },
                { progress: 15, text: '正在加载数据...' },
                { progress: 30, text: '正在预处理数据...' },
                { progress: 45, text: '正在训练模型...' },
                { progress: 60, text: '正在优化参数...' },
                { progress: 75, text: '正在保存模型...' },
                { progress: 90, text: '正在生成结果...' },
                { progress: 100, text: '训练完成！' }
            ];
            
            this.trainingTimer = setInterval(() => {
                currentProgress += progressStep;
                
                if (currentProgress >= 100) {
                    currentProgress = 100;
                    this.trainingProgress = 100;
                    this.trainingProgressText = '训练完成！';
                    
                    // 清除定时器
                    clearInterval(this.trainingTimer);
                    this.trainingTimer = null;
                    
                    // 延迟500毫秒后关闭进度条，显示完成对话框
                    setTimeout(() => {
                        this.showTrainingProgress = false;
                        this.showTrainingComplete = true;
                    }, 500);
                } else {
                    this.trainingProgress = Math.min(Math.floor(currentProgress), 99);
                    
                    // 根据进度更新文本
                    for (let i = progressStages.length - 1; i >= 0; i--) {
                        if (this.trainingProgress >= progressStages[i].progress) {
                            this.trainingProgressText = progressStages[i].text;
                            break;
                        }
                    }
                }
            }, updateInterval);
        },
        
        // 处理训练完成
        handleTrainingComplete() {
            this.showTrainingComplete = false;
        },
        
        // 处理Mymodel点击
        handleMymodelClick() {
            this.showTrainingComplete = false;
            // 直接加载并显示模型训练图片
            this.loadAndShowImage();
        },
        
        // 加载并显示图片（直接从public目录加载）
        loadAndShowImage() {
            this.showImageDialog = true;
            this.imageUrl = '';
            
            // 直接从public目录加载模型训练图片
            const imageFileName = '模型训练图片.png';
            
            // 尝试加载图片
            const img = new Image();
            img.onload = () => {
                this.imageUrl = `/${imageFileName}`;
            };
            img.onerror = () => {
                // 如果.png格式不存在，尝试其他格式
                const alternativeNames = [
                    '模型训练图片.jpg',
                    '模型训练图片.jpeg',
                    '模型训练图片.gif',
                    '模型训练图片.bmp'
                ];
                
                let found = false;
                let checkIndex = 0;
                
                const checkNext = () => {
                    if (checkIndex >= alternativeNames.length) {
                        if (!found) {
                            this.$message.error('未找到模型训练图片，请确保public目录下有"模型训练图片.png"文件');
                            this.showImageDialog = false;
                        }
                        return;
                    }
                    
                    const testImg = new Image();
                    testImg.onload = () => {
                        this.imageUrl = `/${alternativeNames[checkIndex]}`;
                        found = true;
                    };
                    testImg.onerror = () => {
                        checkIndex++;
                        checkNext();
                    };
                    testImg.src = `/${alternativeNames[checkIndex]}`;
                };
                
                checkNext();
            };
            img.src = `/${imageFileName}`;
        },
        
        // 处理图片加载错误
        handleImageError() {
            this.$message.error('图片加载失败，请检查文件路径');
            this.showImageDialog = false;
        },
        
        // 处理图片对话框关闭
        handleImageDialogClose() {
            this.showImageDialog = false;
            this.imageUrl = '';
        },
        
        // 处理烧结曲线推荐
        handleSinteringCurve() {
            // 跳转到烧结曲线推荐页面
            this.$router.push('/sinter-curve-recommend').catch(() => {});
        },
        
        // 提取特征数据
        extractFeatures(row) {
            const features = {};
            
            // 提取对象和操作相关的字段作为特征
            Object.keys(row).forEach(key => {
                if (key.startsWith('object_') || key.startsWith('operation_')) {
                    if (row[key] !== '-' && row[key] !== null && row[key] !== undefined) {
                        features[key] = row[key];
                    }
                }
            });
            
            return features;
        },
        
        // 提取标签数据
        extractLabels(row) {
            const labels = {};
            
            // 提取结果相关的字段作为标签
            Object.keys(row).forEach(key => {
                if (key.startsWith('result_')) {
                    if (row[key] !== '-' && row[key] !== null && row[key] !== undefined) {
                        labels[key] = row[key];
                    }
                }
            });
            
            return labels;
        },
        
        async loadTemplateData() {
            try {
                if (!this.currentNode || !this.currentNode.isTemplate) {
                    console.log('没有选中的模板节点，不加载数据');
                    this.expandedTableData = [];
                    this.total = 0;
                    this.dynamicColumns = [];
                    return;
                }

                this.loading = true;
                console.log('开始加载模板数据，模板ID:', this.currentNode.id);
                
                // 直接获取所有数据
                const response = await this.$request.get(`/basemodule/moduledata/list/${this.currentNode.id}`);
                console.log('API响应:', response.data);
                
                if (response.data && (response.data.msg === 'success' || response.data.code === 0)) {
                    const moduleData = response.data.moduleData || [];
                    console.log('获取到的模板数据:', moduleData);
                    
                    if (moduleData.length === 0) {
                        this.expandedTableData = [];
                        this.total = 0;
                        this.dynamicColumns = [];
                        return;
                    }
                    
                    // 直接使用接口返回的数据
                    this.expandedTableData = moduleData;
                    this.total = moduleData.length;
                    
                    // 清空选中状态
                    this.allSelectedRows.clear();
                    this.selectedDataRows = [];
                    
                    // 根据数据自动生成列
                    this.setupDynamicColumnsFromData(moduleData);
                    
                    console.log('加载数据成功，总数:', this.total);
                    console.log('数据示例:', moduleData.slice(0, 3));
                } else {
                    throw new Error(response.data.msg || '获取数据失败');
                }
            } catch (error) {
                console.error('加载模板数据失败:', error);
                this.$message.error('加载模板数据失败，请重试');
                this.expandedTableData = [];
                this.total = 0;
                this.dynamicColumns = [];
            } finally {
                this.loading = false;
            }
        },
        
        // 加载字段信息
        async loadColumnInfo() {
            try {
                const columnResponse = await this.$request.get(`/basemodule/moduledata/getColumnInfo/${this.currentNode.id}`);
                if (columnResponse.data && columnResponse.data.code === 0) {
                    this.columnInfo = columnResponse.data.columnInfo || columnResponse.data.data || {};
                    console.log('字段信息:', this.columnInfo);
                }
            } catch (error) {
                console.warn('获取字段信息失败:', error);
                this.columnInfo = {};
            }
        },
        
        // 加载并展开详细数据
        async loadAndExpandDetailData(moduleData) {
            const expandedData = [];
            const allColumns = new Set();
            
            // 为每个sample_serial获取详细数据
            for (const item of moduleData) {
                const sampleSerial = item.sample_serial;
                if (!sampleSerial) continue;
                
                try {
                    console.log('获取详细数据:', sampleSerial);
                    const detailResponse = await this.$request.post('/basemodule/moduledata/getdetail', {
                        sampleSerial: sampleSerial,
                        moduleId: String(this.currentNode.id)
                    });
                    
                    if (detailResponse.data && detailResponse.data.code === 0) {
                        const detailData = detailResponse.data.moduleData;
                        const { objectList = [], operationList = [], resultList = [] } = detailData;
                        
                        // 展开数据：一个对象+一个操作+一个结果=一行数据
                        const expandedRows = this.expandDetailData(objectList, operationList, resultList, sampleSerial);
                        expandedData.push(...expandedRows);
                        
                        // 收集所有字段名
                        expandedRows.forEach(row => {
                            Object.keys(row).forEach(key => allColumns.add(key));
                        });
                    }
                } catch (error) {
                    console.error(`获取${sampleSerial}详细数据失败:`, error);
                }
            }
            
            // 设置动态列
            this.setupDynamicColumns(allColumns);
            
            // 更新展开后的数据
            this.expandedTableData = expandedData;
            this.total = expandedData.length;
            
            console.log('展开后的数据总数:', this.total);
            console.log('展开后的数据示例:', expandedData.slice(0, 3));
        },
        
        // 展开详细数据
        expandDetailData(objectList, operationList, resultList, sampleSerial) {
            const expandedRows = [];
            
            if (objectList.length === 0) {
                return expandedRows;
            }
            
            const objectData = objectList[0]; // 通常只有一个对象
            
            if (operationList.length === 0) {
                // 如果没有操作，只创建一行对象数据
                const row = {
                    sample_serial: sampleSerial,
                    data_type: '对象',
                    row_id: `${sampleSerial}_object_${objectData.id}`,
                    ...this.extractFieldData(objectData, 'object')
                };
                expandedRows.push(row);
            } else {
                // 为每个操作创建行
                operationList.forEach((operation, opIndex) => {
                    // 找到该操作对应的结果
                    const matchedResults = resultList.filter(result => 
                        result.operation_id === operation.id
                    );
                    
                    if (matchedResults.length === 0) {
                        // 如果没有结果，只创建操作行
                        const row = {
                            sample_serial: sampleSerial,
                            data_type: `操作${opIndex + 1}`,
                            row_id: `${sampleSerial}_operation_${operation.id}`,
                            ...this.extractFieldData(objectData, 'object'),
                            ...this.extractFieldData(operation, 'operation')
                        };
                        expandedRows.push(row);
                    } else {
                        // 为每个结果创建一行
                        matchedResults.forEach((result, resultIndex) => {
                            const row = {
                                sample_serial: sampleSerial,
                                data_type: `操作${opIndex + 1}-结果${resultIndex + 1}`,
                                row_id: `${sampleSerial}_operation_${operation.id}_result_${result.id}`,
                                ...this.extractFieldData(objectData, 'object'),
                                ...this.extractFieldData(operation, 'operation'),
                                ...this.extractFieldData(result, 'result')
                            };
                            expandedRows.push(row);
                        });
                    }
                });
            }
            
            return expandedRows;
        },
        
        // 提取字段数据
        extractFieldData(item, type) {
            const extractedData = {};
            
            // 从columnInfo中获取该类型的字段信息
            let columnInfoForType = [];
            if (this.columnInfo[type] && Array.isArray(this.columnInfo[type])) {
                columnInfoForType = this.columnInfo[type];
            } else if (Array.isArray(this.columnInfo)) {
                columnInfoForType = this.columnInfo.filter(c => c.section === type);
            }
            
            if (columnInfoForType.length > 0) {
                // 根据字段信息提取数据
                columnInfoForType.forEach(colInfo => {
                    const columnName = colInfo.column_name || colInfo.columnName || colInfo.fieldName;
                    const displayName = colInfo.displayName || columnName;
                    const fieldKey = `${type}_${displayName}`;
                    
                    // 智能字段匹配
                    const value = this.findValueByColumnName(item, columnName);
                    extractedData[fieldKey] = value !== null && value !== undefined && value !== '' ? value : '-';
                });
            } else {
                // 如果没有字段信息，提取所有字段
                Object.keys(item).forEach(key => {
                    if (!['id', 'create_time', 'operation_id'].includes(key)) {
                        const fieldKey = `${type}_${key}`;
                        extractedData[fieldKey] = item[key];
                    }
                });
            }
            
            return extractedData;
        },
        
        // 智能字段匹配（从TemplateDetailDialog复制）
        findValueByColumnName(item, columnName) {
            // 1. 直接匹配
            if (item[columnName] !== undefined && item[columnName] !== null) {
                return item[columnName];
            }
            
            // 2. 智能添加下划线
            const withUnderscorePattern1 = columnName.replace(/([a-z]+)(name)([0-9]+)/gi, '$1_$2_$3');
            if (item[withUnderscorePattern1] !== undefined && item[withUnderscorePattern1] !== null) {
                return item[withUnderscorePattern1];
            }
            
            // 3. 通用下划线规则
            const withUnderscore = columnName.replace(/([a-z])([0-9])/g, '$1_$2');
            if (item[withUnderscore] !== undefined && item[withUnderscore] !== null) {
                return item[withUnderscore];
            }
            
            // 4. 尝试移除下划线的版本
            const withoutUnderscore = columnName.replace(/_/g, '');
            if (item[withoutUnderscore] !== undefined && item[withoutUnderscore] !== null) {
                return item[withoutUnderscore];
            }
            
            // 5. 不区分大小写匹配
            const lowerColumnName = columnName.toLowerCase();
            for (const key in item) {
                if (key.toLowerCase() === lowerColumnName) {
                    return item[key];
                }
            }
            
            // 6. 模糊匹配
            const normalizedColumnName = columnName.replace(/_/g, '').toLowerCase();
            for (const key in item) {
                const normalizedKey = key.replace(/_/g, '').toLowerCase();
                if (normalizedKey === normalizedColumnName) {
                    return item[key];
                }
            }
            
            return null;
        },
        
        // 根据数据自动生成列
        setupDynamicColumnsFromData(data) {
            if (!data || data.length === 0) {
                this.dynamicColumns = [];
                return;
            }
            
            // 收集所有字段名
            const allColumns = new Set();
            data.forEach(row => {
                Object.keys(row).forEach(key => {
                    if (key !== 'row_id') { // 排除row_id
                        allColumns.add(key);
                    }
                });
            });
            
            const columnArray = Array.from(allColumns);
            
            // 排序：sample_serial, data_type 优先，然后按字母顺序
            const sortedColumns = columnArray.sort((a, b) => {
                if (a === 'sample_serial') return -1;
                if (b === 'sample_serial') return 1;
                if (a === 'data_type') return -1;
                if (b === 'data_type') return 1;
                
                // 按类型前缀排序：object_ < operation_ < result_
                const getTypeOrder = (col) => {
                    if (col.startsWith('object_')) return 1;
                    if (col.startsWith('operation_')) return 2;
                    if (col.startsWith('result_')) return 3;
                    return 4;
                };
                
                const orderA = getTypeOrder(a);
                const orderB = getTypeOrder(b);
                if (orderA !== orderB) return orderA - orderB;
                
                return a.localeCompare(b);
            });
            
            this.dynamicColumns = sortedColumns.map(col => ({
                prop: col,
                label: this.formatColumnLabel(col),
                width: col === 'sample_serial' ? 250 : col === 'data_type' ? 150 : 200
            }));
            
            console.log('设置的动态列:', this.dynamicColumns);
            
            // 初始化列字段选择
            this.initializeColumnSelection();
        },
        
        // 设置动态列（保留旧方法以兼容）
        setupDynamicColumns(allColumns) {
            const columnArray = Array.from(allColumns);
            
            // 排序：sample_serial, data_type, 然后按类型分组
            const sortedColumns = columnArray.sort((a, b) => {
                if (a === 'sample_serial') return -1;
                if (b === 'sample_serial') return 1;
                if (a === 'data_type') return -1;
                if (b === 'data_type') return 1;
                if (a === 'row_id') return 1;
                if (b === 'row_id') return -1;
                
                // 按类型前缀排序：object_ < operation_ < result_
                const getTypeOrder = (col) => {
                    if (col.startsWith('object_')) return 1;
                    if (col.startsWith('operation_')) return 2;
                    if (col.startsWith('result_')) return 3;
                    return 4;
                };
                
                const orderA = getTypeOrder(a);
                const orderB = getTypeOrder(b);
                if (orderA !== orderB) return orderA - orderB;
                
                return a.localeCompare(b);
            });
            
            this.dynamicColumns = sortedColumns
                .filter(col => col !== 'row_id') // 隐藏row_id列
                .map(col => ({
                    prop: col,
                    label: this.formatColumnLabel(col),
                    width: col === 'sample_serial' ? 250 : col === 'data_type' ? 150 : 200
                }));
            
            console.log('设置的动态列:', this.dynamicColumns);
            
            // 初始化列字段选择
            this.initializeColumnSelection();
        },
        
        // 格式化列标签
        formatColumnLabel(columnName) {
            if (columnName === 'sample_serial') return 'Sample Serial';
            if (columnName === 'data_type') return '数据类型';
            
            // 移除类型前缀并格式化
            const withoutPrefix = columnName.replace(/^(object|operation|result)_/, '');
            return withoutPrefix.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        },
        
        // 处理选择变化
        handleSelectionChange(selection) {
            // 获取当前页的所有数据
            const allData = this.allTableData;
            const currentPageData = this.displayTableData;
            
            // 更新所有选中行的集合
            // 先移除当前页的所有数据
            currentPageData.forEach(row => {
                const rowKey = this.getRowKey(row);
                this.allSelectedRows.delete(rowKey);
            });
            
            // 添加当前选中的数据
            selection.forEach(row => {
                const rowKey = this.getRowKey(row);
                this.allSelectedRows.add(rowKey);
            });
            
            // 更新selectedDataRows为所有选中的数据
            this.selectedDataRows = allData.filter(row => {
                const rowKey = this.getRowKey(row);
                return this.allSelectedRows.has(rowKey);
            });
            
            console.log('选中的数据行（所有页）:', this.selectedDataRows.length, '当前页:', selection.length);
        },
        
        // 处理全选
        handleSelectAll(selection) {
            const allData = this.allTableData;
            
            if (selection.length > 0) {
                // 全选：将所有数据添加到选中集合
                allData.forEach(row => {
                    const rowKey = this.getRowKey(row);
                    this.allSelectedRows.add(rowKey);
                });
                this.$message.success(`已全选所有 ${allData.length} 条数据`);
            } else {
                // 取消全选：清空所有选中
                this.allSelectedRows.clear();
                this.$message.info('已取消全选');
            }
            
            // 更新selectedDataRows为所有选中的数据
            this.selectedDataRows = allData.filter(row => {
                const rowKey = this.getRowKey(row);
                return this.allSelectedRows.has(rowKey);
            });
            
            console.log('全选/取消全选 - 所有页选中:', this.selectedDataRows.length);
        },
        
        // 获取行的唯一标识
        getRowKey(row) {
            // 使用sample_serial和row_id作为唯一标识，如果没有则使用对象引用
            if (row.sample_serial && row.row_id) {
                return `${row.sample_serial}_${row.row_id}`;
            }
            if (row.sample_serial) {
                return row.sample_serial;
            }
            if (row.id) {
                return String(row.id);
            }
            // 如果都没有，使用JSON字符串作为key（可能性能较差，但能保证唯一性）
            return JSON.stringify(row);
        },
        
        // 更新表格选中状态
        updateTableSelection(pageData) {
            if (!this.$refs.dataTable) {
                return;
            }
            
            // 清除当前选中
            this.$refs.dataTable.clearSelection();
            
            // 根据allSelectedRows设置当前页的选中状态
            pageData.forEach(row => {
                const rowKey = this.getRowKey(row);
                if (this.allSelectedRows.has(rowKey)) {
                    this.$refs.dataTable.toggleRowSelection(row, true);
                }
            });
        },
        
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
                    this.$message.info('进入模版创建');
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
        
        async loadDirectoryTree() {
            try {
                // 定义完整的三级目录结构（写死）
                const directoryStructure = [
                    {
                        id: 'big_cat_1',
                        name: '材料属性',
                        isBigCategory: true,
                        subCategories: [
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
                        ]
                    },
                    {
                        id: 'big_cat_2',
                        name: '数据来源',
                        isBigCategory: true,
                        subCategories: [
                            { id: 11, name: '文献' },
                            { id: 12, name: '计算' },
                            { id: 13, name: '实验' },
                            { id: 14, name: '研发生产' },
                            { id: 15, name: '临床应用' },
                            { id: 16, name: '其他数据来源' }
                        ]
                    },
                    {
                        id: 'big_cat_3',
                        name: '材料功能',
                        isBigCategory: true,
                        subCategories: [
                            { id: 17, name: '骨科材料' },
                            { id: 18, name: '心血管材料' },
                            { id: 19, name: '牙科材料' },
                            { id: 20, name: '其他材料功能' }
                        ]
                    }
                ];

                // 为每个小目录获取其下的模板
                const buildTreePromises = directoryStructure.map(async bigCat => {
                    const subCategoriesWithTemplates = await Promise.all(
                        bigCat.subCategories.map(async subCat => {
                            try {
                                const templatesResponse = await this.$request.get(`/basemodule/module/getmodules/${subCat.id}`);
                                if (templatesResponse.data && templatesResponse.data.code === 0) {
                                    const templates = templatesResponse.data.module_list || [];
                                    
                                    return {
                                        id: subCat.id,
                                        name: subCat.name,
                                        isSubCategory: true,
                                        children: templates
                                            .filter(template => template.state === 1)
                                            .map(template => ({
                                                id: template.id,
                                                name: template.name,
                                                isTemplate: true,
                                                template: template
                                            }))
                                    };
                                }
                            } catch (error) {
                                console.error(`获取小目录 ${subCat.name} 的模板失败:`, error);
                            }
                            
                            return {
                                id: subCat.id,
                                name: subCat.name,
                                isSubCategory: true,
                                children: []
                            };
                        })
                    );
                    
                    return {
                        id: bigCat.id,
                        name: bigCat.name,
                        isBigCategory: true,
                        children: subCategoriesWithTemplates
                    };
                });

                this.directoryTree = await Promise.all(buildTreePromises);
                console.log('目录树加载完成:', this.directoryTree);
            } catch (error) {
                console.error('加载目录树失败:', error);
                this.$message.error('加载目录树失败，请刷新页面重试');
            }
        },
        
        handleNodeClick(node) {
            console.log('点击节点:', node);
            
            if (node.isTemplate) {
                this.currentNode = node;
                this.currentPage = 1;
                this.loadTemplateData();
            }
        },
        
        handleSizeChange(val) {
            console.log(`每页 ${val} 条`);
            this.pageSize = val;
            this.currentPage = 1; // 重置到第一页
            // 页面大小改变后，更新选中状态
            this.$nextTick(() => {
                this.updateTableSelection(this.displayTableData);
            });
        },
        
        handleCurrentChange(val) {
            console.log(`当前页: ${val}`);
            this.currentPage = val;
            // 页面切换后，更新选中状态
            this.$nextTick(() => {
                this.updateTableSelection(this.displayTableData);
            });
        },
        
        handleView(row) {
            console.log('查看详情:', row);
            this.detailModuleId = this.currentNode.id;
            this.detailSampleSerial = row.sample_serial;
            this.isDetailDialogVisible = true;
        },
        
        // 列字段选择相关方法
        handleCheckAllChange(val) {
            this.checkedColumns = val ? this.allAvailableColumns.map(col => col.prop) : [];
            this.isIndeterminate = false;
        },
        
        handleCheckedColumnsChange(value) {
            let checkedCount = value.length;
            this.checkAll = checkedCount === this.allAvailableColumns.length;
            this.isIndeterminate = checkedCount > 0 && checkedCount < this.allAvailableColumns.length;
        },
        
        applyColumnFilter() {
            // 应用列选择，这里不需要额外操作，因为 displayColumns 计算属性会自动更新
            this.$message.success(`已应用列选择，当前显示 ${this.checkedColumns.length} 列`);
        },
        
        resetColumnFilter() {
            // 重置为全选状态
            this.checkedColumns = this.allAvailableColumns.map(col => col.prop);
            this.checkAll = true;
            this.isIndeterminate = false;
            this.$message.success('已重置列选择为全选状态');
        },
        
        // 初始化列字段选择
        initializeColumnSelection() {
            // 将所有动态列设为可选择的列
            this.allAvailableColumns = [...this.dynamicColumns];
            // 默认全选
            this.checkedColumns = this.dynamicColumns.map(col => col.prop);
            this.checkAll = true;
            this.isIndeterminate = false;
        },
        
        // 自动加载预设的 Excel 文件
        async autoLoadExcelFile() {
            // 预设的 Excel 文件名（放在 public 目录下）
            const excelFileName = '数据转换.xlsx'; // 或者 '数据转换.xls'
            
            // 尝试加载文件
            try {
                this.loading = true;
                
                // 使用 fetch 从 public 目录加载文件
                const response = await fetch(`/${excelFileName}`);
                
                if (!response.ok) {
                    // 如果文件不存在，尝试其他可能的文件名
                    const alternativeNames = [
                        '数据转换.xls',
                        'data_transform.xlsx',
                        'data_transform.xls'
                    ];
                    
                    let fileLoaded = false;
                    for (const fileName of alternativeNames) {
                        try {
                            const altResponse = await fetch(`/${fileName}`);
                            if (altResponse.ok) {
                                const arrayBuffer = await altResponse.arrayBuffer();
                                await this.parseExcelFile(arrayBuffer);
                                fileLoaded = true;
                                console.log(`成功自动加载文件: ${fileName}`);
                                break;
                            }
                        } catch (e) {
                            // 继续尝试下一个文件名
                        }
                    }
                    
                    if (!fileLoaded) {
                        console.log('未找到预设的 Excel 文件，将在首次使用时提示选择文件');
                        this.loading = false;
                        return;
                    }
                } else {
                    const arrayBuffer = await response.arrayBuffer();
                    await this.parseExcelFile(arrayBuffer);
                    console.log(`成功自动加载文件: ${excelFileName}`);
                }
            } catch (error) {
                console.warn('自动加载 Excel 文件失败:', error);
                console.log('将在首次使用时提示选择文件');
            } finally {
                this.loading = false;
            }
        },
        
        // 解析 Excel 文件（提取公共逻辑）
        async parseExcelFile(arrayBuffer) {
            try {
                const data = new Uint8Array(arrayBuffer);
                const workbook = XLSX.read(data, { type: 'array' });
                
                // 读取第一个工作表
                const firstSheetName = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[firstSheetName];
                
                // 将工作表转换为 JSON 数组
                // 使用 defval: null 确保空单元格被识别为 null，而不是 undefined
                let jsonData = XLSX.utils.sheet_to_json(worksheet, { defval: null });
                
                // 调试：检查 Excel 解析出来的实际值
                console.log('=== Excel 解析调试信息 (parseExcelFile) ===');
                jsonData.forEach((row, i) => {
                    if (i < 3) { // 只打印前3行
                        console.log(`row ${i}:`, row);
                        Object.keys(row).forEach(key => {
                            if (key === 'is_aug' || key.includes('is_aug')) {
                                console.log(`  ${key}:`, row[key], 'type:', typeof row[key]);
                            }
                        });
                    }
                });
                console.log('=== 调试信息结束 ===');
                
                // 处理空值：将null、undefined、空字符串转换为"-"，但保留0值
                jsonData = jsonData.map(row => {
                    const processedRow = {}
                    Object.keys(row).forEach(key => {
                        const value = row[key]
                        // 只有真正的空值才转换为"-"，0值保持不变
                        // 特别注意：0 === 0 是 true，所以 0 值不会被转换
                        if (value === null || value === undefined || value === '') {
                            processedRow[key] = '-'
                        } else {
                            processedRow[key] = value
                        }
                    })
                    return processedRow
                })
                
                console.log('自动加载的 Excel 数据:', jsonData);
                
                // 存储原始数据
                this.xlsxFileData = jsonData;
                
                this.$message.success(`已自动加载 ${jsonData.length} 条数据`);
            } catch (error) {
                console.error('解析 Excel 文件失败:', error);
                throw error;
            }
        }
    }
}
</script>

<style scoped>
/* 页面容器 */
.machine-learning-page {
    min-height: 100vh;
    background: linear-gradient(to bottom, #f5f7fa 0%, #ffffff 100%);
    position: relative;
    overflow-x: hidden;
}

/* 主要内容区域 */
.main-content {
    display: flex;
    margin-top: 100px;
    padding: 0;
    min-height: calc(100vh - 100px);
    position: relative;
}

/* 左侧边栏 */
.sidebar {
    width: 280px;
    min-width: 280px;
    max-width: 280px;
    background: linear-gradient(to bottom, #ffffff, #fafbfc);
    border-right: 1px solid #e8eaed;
    display: flex;
    flex-direction: column;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
    flex-shrink: 0;
    position: sticky;
    top: 100px;
    height: calc(100vh - 100px);
    overflow: hidden;
    z-index: 10;
}

.category-list {
    flex: 1;
    overflow-y: auto;
    padding: 10px 0;
}

/* 右侧内容区域 */
.content-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    background-color: #ffffff;
    margin: 20px 20px 120px 20px;
    border-radius: 8px;
    padding: 20px 20px 40px 20px;
    min-height: calc(100vh - 100px);
    overflow: hidden;
    min-width: 0;
    position: relative;
}

.header-section {
    margin-bottom: 15px;
    flex-shrink: 0;
}

/* 机器学习按钮栏样式 */
.ml-button-bar {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
    border: 1px solid #e8eaed;
    transition: all 0.3s ease;
    width: 100%;
    box-sizing: border-box;
    position: relative;
    z-index: 5;
}

.ml-button-bar:hover {
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.12);
}

.button-bar-header {
    position: relative;
    margin-bottom: 20px;
}

.section-label {
    position: absolute;
    top: -35px;
    left: -20px;
    background: #409EFF;
    color: white;
    padding: 4px 12px;
    border-radius: 8px 0 8px 0;
    font-size: 12px;
    font-weight: bold;
}

.content-title {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    margin: 5px 0 0 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #e0e0e0;
}

.button-group {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
    width: 100%;
}

.button-group .el-button {
    flex: 1 1 auto;
    min-width: 120px;
    max-width: 200px;
    height: 45px;
    font-size: 15px;
    font-weight: 500;
    border-radius: 8px;
    transition: all 0.3s ease;
    box-sizing: border-box;
}

.button-group .el-button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 表选择区域样式 */
.table-select-box {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border: 1px solid #e8eaed;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
}

.table-select-box:hover {
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.12);
}

.table-tabs-container {
    padding: 15px 20px;
}

.table-tabs-container .el-tabs {
    margin-top: 10px;
}

.table-tabs-container .el-tabs__item {
    font-size: 14px;
    font-weight: 500;
    padding: 0 20px;
}

.table-tabs-container .el-tabs__item.is-active {
    color: #409EFF;
    font-weight: 600;
}

/* 列字段选择区域样式 */
.column-filter-box {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border: 1px solid #e8eaed;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
}

.column-filter-box:hover {
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.12);
}

.filter-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid #e8eaed;
    background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
    border-radius: 10px 10px 0 0;
}

.filter-title {
    font-size: 16px;
    font-weight: bold;
    color: #333;
    display: flex;
    align-items: center;
    gap: 8px;
}

.filter-title i {
    color: #409EFF;
}

.selected-count {
    font-size: 14px;
    color: #666;
    background: #e8f4ff;
    padding: 4px 12px;
    border-radius: 15px;
    border: 1px solid #b3d8ff;
}

.filter-content {
    padding: 20px;
}

.check-all-box {
    margin-bottom: 15px;
    font-weight: bold;
    color: #333;
}

.checkbox-group-container {
    margin-bottom: 20px;
    max-height: 200px;
    overflow-y: auto;
    border: 1px solid #e8eaed;
    border-radius: 6px;
    padding: 15px;
    background: #fafbfc;
}

.column-checkbox-group {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 20px;
}

.column-checkbox {
    margin-right: 0 !important;
    margin-bottom: 8px;
    padding: 6px 12px;
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    transition: all 0.2s ease;
    min-width: 150px;
}

.column-checkbox:hover {
    background: #f0f9ff;
    border-color: #409EFF;
}

.column-checkbox.is-checked {
    background: #e8f4ff;
    border-color: #409EFF;
    color: #409EFF;
}

.filter-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
}

.filter-actions .el-button {
    padding: 8px 20px;
    border-radius: 6px;
    font-weight: 500;
}

/* 滚动条样式 */
.checkbox-group-container::-webkit-scrollbar {
    width: 6px;
}

.checkbox-group-container::-webkit-scrollbar-thumb {
    background-color: #c0c4cc;
    border-radius: 3px;
}

.checkbox-group-container::-webkit-scrollbar-thumb:hover {
    background-color: #909399;
}

.checkbox-group-container::-webkit-scrollbar-track {
    background-color: #f5f7fa;
    border-radius: 3px;
}

/* 表格容器 */
.table-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    position: relative;
    min-height: 600px;
    background: linear-gradient(to bottom, #ffffff, #f9fafb);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.08);
    overflow: hidden;
    width: 100%;
    box-sizing: border-box;
    min-width: 0;
}

.table-scroll-box {
    flex: 1;
    overflow-x: auto;
    overflow-y: auto;
    border-radius: 8px;
    position: relative;
    min-height: 0;
    width: 100%;
    box-sizing: border-box;
}

.el-table {
    width: 100%;
    min-width: fit-content;
    border-radius: 8px;
}

.el-table__body-wrapper {
    overflow-x: auto !important;
    overflow-y: auto !important;
    max-height: none !important;
}

.el-table__header-wrapper {
    overflow: visible !important;
}

.el-table__fixed,
.el-table__fixed-right {
    position: absolute !important;
}

/* 确保表格滚动不影响外部布局 */
.table-scroll-box .el-table {
    position: relative;
}

.table-scroll-box .el-table__body {
    width: 100% !important;
}

/* 表格行悬停效果 */
.el-table tbody tr:hover {
    background-color: #f0f9ff !important;
    cursor: pointer;
}

/* 表格边框优化 */
.el-table td, .el-table th {
    border-color: #e8eaed !important;
}

/* 分页 */
.pagination {
    margin-top: 20px;
    margin-bottom: 100px;
    padding: 15px 0;
    display: flex;
    justify-content: flex-end;
    background: white;
    border-radius: 8px;
    flex-shrink: 0;
    width: 100%;
}

.pagination .el-pagination {
    font-weight: 500;
}

.pagination .el-pagination.is-background .el-pager li:not(.disabled).active {
    background-color: #409EFF;
    color: white;
}

/* 滚动条样式 */
.category-list::-webkit-scrollbar {
    width: 6px;
}

.category-list::-webkit-scrollbar-thumb {
    background-color: #dcdfe6;
    border-radius: 3px;
}

.category-list::-webkit-scrollbar-thumb:hover {
    background-color: #c0c4cc;
}

/* 表格滚动条样式 */
.table-scroll-box::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

.table-scroll-box::-webkit-scrollbar-thumb {
    background-color: #c0c4cc;
    border-radius: 4px;
}

.table-scroll-box::-webkit-scrollbar-thumb:hover {
    background-color: #909399;
}

.table-scroll-box::-webkit-scrollbar-track {
    background-color: #f5f7fa;
    border-radius: 4px;
}

/* 操作按钮样式 */
.operation-buttons {
    display: flex;
    gap: 8px;
    justify-content: center;
}

/* 训练进度条容器 */
.training-progress-container {
    padding: 20px;
    text-align: center;
}

.progress-text {
    margin-top: 20px;
    font-size: 14px;
    color: #606266;
    font-weight: 500;
}

/* 训练完成容器 */
.training-complete-container {
    text-align: center;
    padding: 20px;
}

/* 图片对话框容器 */
.image-dialog-container {
    text-align: center;
    padding: 20px;
    min-height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.result-image {
    max-width: 100%;
    max-height: 70vh;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    object-fit: contain;
}

.image-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #909399;
    font-size: 16px;
}

.image-loading p {
    margin-top: 15px;
}

/* 训练指标展示区域 */
.training-metrics-container {
    margin-top: 30px;
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    border: 1px solid #e8eaed;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
}

.metrics-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: bold;
    color: #333;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid #409EFF;
}

.metrics-header i {
    color: #409EFF;
    font-size: 20px;
}

.metrics-content {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.metrics-row {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: space-between;
}

.metric-item {
    flex: 1;
    min-width: 200px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 15px;
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    transition: all 0.3s ease;
}

.metric-item:hover {
    background: #f0f9ff;
    border-color: #409EFF;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.metric-label {
    font-size: 14px;
    color: #606266;
    font-weight: 500;
}

.metric-value {
    font-size: 15px;
    color: #409EFF;
    font-weight: 600;
    font-family: 'Courier New', monospace;
}

.metrics-divider {
    height: 1px;
    background: linear-gradient(to right, transparent, #e0e0e0, transparent);
    margin: 10px 0;
}

.metrics-section {
    margin-top: 10px;
}

.section-title {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin-bottom: 15px;
    padding-left: 10px;
    border-left: 4px solid #409EFF;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .main-content {
        flex-direction: column;
    }

    .sidebar {
        width: 100%;
        border-right: none;
        border-bottom: 1px solid #e8eaed;
    }

    .content-area {
        margin: 10px;
    }
    
    .button-group {
        flex-direction: column;
    }
    
    .button-group .el-button {
        width: 100%;
    }
    
    .image-dialog-container {
        min-height: 300px;
    }
    
    .result-image {
        max-height: 50vh;
    }
}
</style>

