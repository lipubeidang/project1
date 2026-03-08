<template>
    <div class="template-library-page" :key="componentKey">
        <Navbar @dropdown-action="handleDropdownAction" />
        <TemplateNavbar @nav-action="handleNavAction" @audit-action="handleAuditAction" />

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
                <!-- 标题和描述区域 -->
                <div class="header-section">
                    <div class="template-info">
                        <div class="info-header">
                            <span class="section-label">模板描述</span>
                            <h2 class="content-title">{{ currentNode?.name || '请选择模板' }}</h2>
                        </div>
                        <div class="template-description" v-if="currentNode?.isTemplate">
                            <div class="description-header">
                                <i class="el-icon-document"></i>
                                <span>描述信息</span>
                            </div>
                            <div class="description-content">
                                {{ currentNode?.template?.description || '该模板暂无描述信息' }}
                            </div>
                            <div class="template-meta" v-if="currentNode?.template">
                                <div class="meta-item">
                                    <i class="el-icon-user"></i>
                                    <span>创建者：{{ currentNode.template.creator || '未知' }}</span>
                                </div>
                                <div class="meta-item">
                                    <i class="el-icon-time"></i>
                                    <span>创建时间：{{ currentNode.template.createTime || '未知' }}</span>
                                </div>
                            </div>
                        </div>
                        <div class="template-placeholder" v-else>
                            <i class="el-icon-document"></i>
                            <p>请从左侧选择一个模板查看详细信息</p>
                        </div>
                    </div>
                </div>

                <!-- 搜索和筛选区域 -->
                <div class="filter-section">
                    <div class="filter-row">
                        <div class="filter-item">
                            <label>sample_serial</label>
                            <el-input 
                                placeholder="请输入sample_serial" 
                                v-model="filterForm.templateName"
                                size="small"
                                style="width: 200px;"
                            />
                        </div>
                        <el-button type="primary" size="small" icon="el-icon-search" @click="handleSearch">查询</el-button>
                        <el-button size="small" @click="handleReset">重置</el-button>
                    </div>
                </div>

                <!-- 表格 -->
                <div class="table-container">
                    <el-empty v-if="tableData.length === 0 && !currentNode" description="请从左侧选择模板查看数据" :image-size="120">
                        <template slot="image">
                            <i class="el-icon-folder-opened" style="font-size: 80px; color: #dcdfe6;"></i>
                        </template>
                    </el-empty>
                    <el-empty v-else-if="tableData.length === 0 && currentNode && currentNode.isTemplate" description="该模板暂无数据" :image-size="100"></el-empty>
                    <template v-else>
                        <div class="table-scroll-box">
                            <el-table
                                :data="tableData"
                                v-loading="loading"
                                element-loading-text="正在加载数据..."
                                element-loading-spinner="el-icon-loading"
                                stripe
                                style="width: 100%"
                                :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
                                border
                            >
                                <el-table-column
                                    label="序号"
                                    width="80"
                                    align="center"
                                    :index="getIndex"
                                    type="index"
                                />
                                <el-table-column
                                    prop="sample_serial"
                                    label="Sample Serial"
                                    min-width="300"
                                    show-overflow-tooltip
                                >
                                    <template slot-scope="scope">
                                        <div class="sample-serial-cell">
                                            <i class="el-icon-document" style="color: #409EFF; margin-right: 8px;"></i>
                                            <span class="sample-serial-text">{{ scope.row.sample_serial || '-' }}</span>
                                        </div>
                                    </template>
                                </el-table-column>
                                <el-table-column
                                    label="操作"
                                    width="200"
                                    align="center"
                                    fixed="right"
                                >
                                    <template slot-scope="scope">
                                        <div class="operation-buttons">
                                            <el-button 
                                                type="primary" 
                                                size="small" 
                                                icon="el-icon-view"
                                                @click="handleView(scope.row)"
                                            >查看</el-button>
                                        </div>
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
                            :total="total"
                            :disabled="total === 0"
                        />
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 模板描述对话框 -->
        <TemplateDescription
            :visible.sync="showTemplateDescription"
            :template="currentTemplate"
        />
        <TemplateDetailDialog
            :visible.sync="isDetailDialogVisible"
            :module-id="detailModuleId"
            :sample-serial="detailSampleSerial"
        />
    </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import TemplateNavbar from '../components/TemplateNavbar.vue';
import TemplateDescription from '../components/TemplateDescription.vue';
import TemplateDetailDialog from '../components/TemplateDetailDialog.vue';

export default {
    name: "TemplateLibrary",
    components: {
        Navbar,
        TemplateNavbar,
        TemplateDescription,
        TemplateDetailDialog
    },
    data() {
        return {
            componentKey: 0,
            uploadUrl: '',  // 移除细胞活力数据模版的上传URL
            uploadLoading: false,
            directoryTree: [],
            defaultProps: {
                children: 'children',
                label: 'name'
            },
            filterForm: {
                templateName: ''
            },
            currentNode: null,
            selectedCategory: '',
            tableData: [],
            allTableData: [],
            currentPage: 1,
            pageSize: 20,
            total: 0,
            moduleDataList: [], // 存储模版数据
            dynamicColumns: [], // 动态列
            showTemplateDescription: false,
            currentTemplate: null,
            loading: false,
            isDetailDialogVisible: false,
            detailModuleId: null,
            detailSampleSerial: null
        }
    },
    mounted() {
        console.log('TemplateLibrary 组件已挂载');
        this.loadDirectoryTree();
    },
    activated() {
        console.log('TemplateLibrary 组件已激活');
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
    updated() {
        console.log('TemplateLibrary 组件已更新');
    },
    watch: {
        $route: {
            handler(to) {
                console.log('路由变化');
                if (to && to.path === '/templatelibrary') {
                    console.log('返回到模板库页面，重新初始化');
                    this.loadTemplateData();
                    this.forceRerender();
                }
            },
            immediate: true
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
        async loadTemplateData() {
            try {
                if (!this.currentNode) {
                    console.log('没有选中的节点，不加载数据');
                    this.tableData = [];
                    this.total = 0;
                    return;
                }

                console.log('开始加载模板数据');
                // 使用getmodules接口获取数据
                const response = await this.$request.get(`/basemodule/module/getmodules/${this.currentNode.id}`);
                console.log('API响应:', response.data);
                
                if (response.data && response.data.code === 0) {
                    const templates = response.data.module_list || [];
                    // 只显示state为1的模板
                    const activeTemplates = templates.filter(item => item.state === 1);
                    
                    // 转换数据格式
                    const formattedData = activeTemplates.map(item => ({
                        id: item.id,
                        templateName: item.sample_serial || item.name,
                        tags: item.name,
                        createTime: item.createTime,
                        creator: item.creator,
                        rawData: item
                    }));
                    
                    console.log('格式化后的数据:', formattedData);
                    
                    // 更新表格数据
                    this.tableData = formattedData;
                    this.total = formattedData.length;
                    
                    console.log('更新后的表格数据长度:', this.tableData.length);
                } else {
                    throw new Error(response.data.msg || '获取数据失败');
                }
            } catch (error) {
                console.error('加载模板数据失败:', error);
                this.$message.error('加载模板数据失败，请重试');
                this.tableData = [];
                this.total = 0;
            }
        },
        initData() {
            // 初始化数据，默认显示全部
            this.tableData = this.allTableData;
            console.log('数据已初始化，tableData长度:', this.tableData.length);
            console.log('当前tableData数据:', this.tableData);
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
                    // TODO: 跳转到模版创建页面
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
                    // TODO: 跳转到模版停用页面
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
                                                parentId: subCat.id,
                                                isTemplate: true,
                                                template: template
                                            }))
                                    };
                                }
                            } catch (error) {
                                console.error(`获取目录 ${subCat.name} 的模板失败:`, error);
                                return {
                                    id: subCat.id,
                                    name: subCat.name,
                                    isSubCategory: true,
                                    children: []
                                };
                            }
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
                console.log('加载完成的三级目录树:', this.directoryTree);
            } catch (error) {
                console.error('加载目录失败:', error);
                this.$message.error('加载目录失败');
            }
        },

        async handleNodeClick(data) {
            console.log('点击节点:', data);
            this.currentNode = data;
            
            // 更新页面标题显示当前选中的模板名称
            if (data.isTemplate) {
                document.title = `模板库 - ${data.name}`;
                this.selectedCategory = data.parentId;
            } else if (data.isSubCategory) {
                document.title = `模板库 - ${data.name}`;
                this.selectedCategory = data.id;
            } else if (data.isBigCategory) {
                document.title = `模板库 - ${data.name}`;
            } else {
                document.title = '模板库';
            }
            
            // 清空表格数据
            this.tableData = [];
            this.total = 0;
            this.moduleDataList = [];
            
            // 只有点击具体模板时才加载数据，点击大目录或小目录不加载数据
            if (data.isTemplate) {
                // 如果点击的是模板，只获取该模板的数据
                await this.loadModuleData(data.id);
            } else if (data.isBigCategory) {
                // 点击大目录时，显示提示信息但不加载数据
                console.log('点击大目录，不加载数据');
            } else if (data.isSubCategory) {
                // 点击小目录时，显示提示信息但不加载数据
                console.log('点击小目录，不加载数据');
            }
        },
        
        // 加载父目录下所有模板的数据
        async loadModuleDataForParent(parentNode) {
            this.loading = true;
            try {
                console.log('开始加载父目录数据:', parentNode.name);
                const allData = [];
                let successCount = 0;
                let emptyCount = 0;
                
                // 获取所有子模板的数据
                for (const child of parentNode.children) {
                    if (child.isTemplate && child.id) {
                        try {
                            const response = await this.$request.get(`/basemodule/moduledata/list/${child.id}`);
                            console.log(`获取模板 ${child.name} 的数据:`, response.data);
                            
                            if (response.data && response.data.code === 0) {
                                const dataList = response.data.moduleData || [];
                                if (dataList.length > 0) {
                                    // 为每条数据添加模板名称标识
                                    const normalizedList = dataList.map(item => this.normalizeModuleData(item, child.id, child.name));
                                    allData.push(...normalizedList);
                                    successCount++;
                                } else {
                                    emptyCount++;
                                }
                            }
                        } catch (error) {
                            console.warn(`模板 ${child.name} 暂无数据或未配置:`, error.message);
                            emptyCount++;
                            // 静默处理错误，继续加载其他模板
                        }
                    }
                }
                
                console.log('所有数据:', allData);
                this.moduleDataList = allData;
                this.updateTableData();
                
                if (allData.length > 0) {
                    this.$message.success(`成功加载 ${allData.length} 条数据（${successCount} 个模板有数据）`);
                } else if (emptyCount > 0) {
                    this.$message.info('该目录下的模板暂无数据');
                } else {
                    this.$message.warning('该目录下没有可用的模板');
                }
                
            } catch (error) {
                console.error('加载父目录数据失败:', error);
                this.$message.error('加载数据失败，请重试');
            } finally {
                this.loading = false;
            }
        },
        
        // 加载单个模板的数据
        async loadModuleData(moduleId) {
            this.loading = true;
            try {
                console.log('开始加载模板数据:', moduleId);
                const response = await this.$request.get(`/basemodule/moduledata/list/${moduleId}`);
                console.log('获取模板数据响应:', response.data);
                
                if (response.data && response.data.code === 0) {
                    const rawList = response.data.moduleData || [];
                    this.moduleDataList = rawList.map(item => this.normalizeModuleData(item, moduleId, this.currentNode?.name));
                    this.updateTableData();
                    
                    if (this.moduleDataList.length > 0) {
                        this.$message.success(`成功加载 ${this.moduleDataList.length} 条数据`);
                    } else {
                        this.$message.info('该模板暂无数据');
                    }
                } else {
                    throw new Error(response.data.msg || '获取数据失败');
                }
            } catch (error) {
                console.error('加载模板数据失败:', error);
                
                // 清空数据列表
                this.moduleDataList = [];
                this.updateTableData();
                
                // 判断是否为服务器错误（可能是模板没有配置表或没有数据）
                if (error.response && error.response.status === 500) {
                    this.$message.warning('该模板暂无数据或未配置数据表');
                } else {
                    this.$message.error('加载数据失败，请重试');
                }
            } finally {
                this.loading = false;
            }
        },
        
        // 更新表格数据（支持分页）
        updateTableData() {
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            this.tableData = this.moduleDataList.slice(start, end);
            this.total = this.moduleDataList.length;
            
            // 更新动态列
            this.updateDynamicColumns();
            
            console.log(`分页: 第${this.currentPage}页, 每页${this.pageSize}条, 总共${this.total}条`);
        },
        
        // 更新动态列
        updateDynamicColumns() {
            if (this.moduleDataList.length === 0) {
                this.dynamicColumns = [];
                return;
            }
            
            // 获取所有字段
            const allKeys = new Set();
            this.moduleDataList.forEach(item => {
                Object.keys(item).forEach(key => {
                    // 排除一些内部字段
                    if (
                        key !== 'templateName' &&
                        key !== 'moduleId' &&
                        key !== 'id' &&
                        key !== 'sampleSerial' &&
                        key !== 'sample_serial'
                    ) {
                        allKeys.add(key);
                    }
                });
            });
            
            this.dynamicColumns = Array.from(allKeys);
            console.log('动态列:', this.dynamicColumns);
        },
        normalizeModuleData(item, moduleId, templateName = '') {
            const sampleSerial = item.sampleSerial || item.sample_serial || '';
            return {
                ...item,
                templateName: templateName || item.templateName,
                moduleId,
                sampleSerial,
                sample_serial: sampleSerial
            };
        },
        
        // 格式化列标签
        formatColumnLabel(key) {
            // 将驼峰命名转换为更友好的显示
            return key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
        },
        
        // 格式化单元格值
        formatCellValue(value) {
            if (value === null || value === undefined) {
                return '-';
            }
            if (typeof value === 'object') {
                return JSON.stringify(value);
            }
            return value;
        },
        async handleSearch() {
            try {
                if (!this.filterForm.templateName.trim()) {
                    this.$message.warning('请输入sample_serial');
                    return;
                }

                if (!this.currentNode) {
                    this.$message.warning('请先选择一个目录或模板');
                    return;
                }

                this.loading = true;
                const searchTerm = this.filterForm.templateName.toLowerCase();
                const allData = [];

                // 判断当前节点是模板还是父目录
                if (this.currentNode.isTemplate) {
                    // 如果是模板，只搜索当前模板的数据
                    const response = await this.$request.get(`/basemodule/moduledata/list/${this.currentNode.id}`);
                    console.log('搜索模板数据响应:', response.data);
                    
                    if (response.data && response.data.code === 0) {
                        const dataList = response.data.moduleData || [];
                        // 过滤匹配的数据
                        const filteredData = dataList.filter(item => {
                            const sampleSerial = (item.sample_serial || item.sampleSerial || '').toLowerCase();
                            return sampleSerial.includes(searchTerm);
                        });
                        
                        // 添加moduleId到每条数据
                        filteredData.forEach(item => {
                            allData.push(this.normalizeModuleData(item, this.currentNode.id, this.currentNode.name));
                        });
                    }
                } else {
                    // 如果是父目录，搜索该目录下所有模板的数据
                    const children = this.currentNode.children || [];
                    for (const child of children) {
                        if (child.isTemplate && child.id) {
                            try {
                                const response = await this.$request.get(`/basemodule/moduledata/list/${child.id}`);
                                console.log(`搜索模板 ${child.name} 的数据:`, response.data);
                                
                                if (response.data && response.data.code === 0) {
                                    const dataList = response.data.moduleData || [];
                                    // 过滤匹配的数据
                                    const filteredData = dataList.filter(item => {
                                        const sampleSerial = (item.sample_serial || item.sampleSerial || '').toLowerCase();
                                        return sampleSerial.includes(searchTerm);
                                    });
                                    
                                    // 添加moduleId到每条数据
                                    filteredData.forEach(item => {
                                        allData.push(this.normalizeModuleData(item, child.id, child.name));
                                    });
                                }
                            } catch (error) {
                                console.error(`搜索模板 ${child.name} 数据失败:`, error);
                            }
                        }
                    }
                }

                console.log('搜索结果:', allData);
                this.moduleDataList = allData;
                this.currentPage = 1; // 重置到第一页
                this.updateTableData();

                if (allData.length > 0) {
                    this.$message.success(`找到 ${allData.length} 条匹配的数据`);
                } else {
                    this.$message.warning('未找到匹配的数据');
                }
            } catch (error) {
                console.error('查询失败:', error);
                this.$message.error('查询失败，请重试');
                this.moduleDataList = [];
                this.updateTableData();
            } finally {
                this.loading = false;
            }
        },
        async handleReset() {
            this.filterForm = {
                templateName: ''
            };
            
            if (this.currentNode) {
                // 重新获取当前节点的数据
                await this.handleNodeClick(this.currentNode);
                this.$message.success('已重置并刷新数据');
            } else {
                this.tableData = [];
                this.total = 0;
                this.$message.info('请先选择一个模板');
            }
        },
        handleView(row) {
            console.log('========== handleView 点击查看 ==========');
            console.log('行数据 row:', row);
            console.log('当前节点 currentNode:', this.currentNode);
            
            const moduleId = row.moduleId || this.currentNode?.id;
            const sampleSerial = row.sampleSerial || row.sample_serial;

            console.log('提取的 moduleId:', moduleId);
            console.log('提取的 sampleSerial:', sampleSerial);
            console.log('row.moduleId:', row.moduleId);
            console.log('row.sampleSerial:', row.sampleSerial);
            console.log('row.sample_serial:', row.sample_serial);

            if (!moduleId || !sampleSerial) {
                console.error('❌ 缺少必要参数');
                this.$message.warning('缺少模块ID或 sampleSerial，无法查看详情');
                return;
            }

            console.log('✅ 准备打开详情弹窗，参数:', { moduleId, sampleSerial });
            this.detailModuleId = moduleId;
            this.detailSampleSerial = sampleSerial;
            this.isDetailDialogVisible = true;
        },

        // HTML转义函数，防止XSS攻击
        escapeHtml(text) {
            if (typeof text !== 'string') {
                text = String(text || '');
            }
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, function(m) { return map[m]; });
        },

        // 格式化字段标签
        formatFieldLabel(key) {
            const labelMap = {
                'operation1': '操作一',
                'operation2': '操作二', 
                'operation3': '操作三',
                'result1': '结果一',
                'result2': '结果二',
                'result3': '结果三',
                'name': '名称',
                'height': '高度',
                'width': '宽度',
                'length': '长度',
                'diameter': '直径',
                'thickness': '厚度'
            };
            return labelMap[key] || key;
        },
        handleSizeChange(val) {
            this.pageSize = val;
            this.currentPage = 1; // 重置到第一页
            this.updateTableData();
        },
        handleCurrentChange(val) {
            this.currentPage = val;
            this.updateTableData();
        },

        // 上传前的验证
        beforeUpload(file) {
            // 检查文件类型
            const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                           file.type === 'application/vnd.ms-excel';
            if (!isExcel) {
                this.$message.error('只能上传Excel文件！');
                return false;
            }

            // 检查文件大小（限制为10MB）
            const isLt10M = file.size / 1024 / 1024 < 10;
            if (!isLt10M) {
                this.$message.error('文件大小不能超过10MB！');
                return false;
            }

            // 检查是否选择了模板
            if (!this.selectedCategory) {
                this.$message.error('请先选择模板类型！');
                return false;
            }

            this.uploadLoading = true;
            return true;
        },

        // 上传成功的回调
        handleUploadSuccess(response) {
            this.uploadLoading = false;
            if (response.code === 0) {
                // 使用 Message Box 显示详细的导入信息
                this.$alert(response.msg, '上传结果', {
                    confirmButtonText: '确定',
                    type: 'success',
                    callback: () => {
                        // 重新加载数据
                        this.loadTemplateData();
                    }
                });
            } else {
                this.$message.error(response.msg || '上传失败，请重试！');
            }
        },

        // 上传失败的回调
        handleUploadError(err) {
            this.uploadLoading = false;
            console.error('上传失败:', err);
            this.$message.error('上传失败，请重试！');
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

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes glow-pulse {
  0%, 100% {
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
  }
  50% {
    box-shadow: 0 0 35px rgba(102, 126, 234, 0.6);
  }
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.4);
  }
  50% {
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.8);
  }
}

.template-library-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7474bf 100%);
    background-size: 200% 200%;
    animation: gradientShift 15s ease infinite;
    padding-top: 100px;
    position: relative;
    overflow-x: hidden;
    overflow-y: auto;
    scroll-behavior: smooth;
}

.template-library-page::before {
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
.template-library-page::-webkit-scrollbar {
    width: 12px;
}

.template-library-page::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    border-radius: 6px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.template-library-page::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.template-library-page::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 6px;
}

.template-library-page::-webkit-scrollbar-corner {
    background: rgba(255, 255, 255, 0.1);
}

/* 主要内容区域 */
.main-content {
    margin-top: 100px; /* 留出顶部主导航+子导航高度，避免内容被遮挡 */
    display: flex;
    min-height: calc(100vh - 100px);
    overflow: visible;
    position: relative;
    z-index: 1;
}

/* 左侧边栏 */
.sidebar {
    width: 280px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(102, 126, 234, 0.2);
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15),
                0 0 0 1px rgba(255, 255, 255, 0.3) inset;
    border-radius: 0 20px 20px 0;
    margin: 20px 0 20px 20px;
    position: relative;
    z-index: 1;
    animation: slideDown 0.6s ease;
    transition: all 0.3s ease;
}

.sidebar:hover {
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2),
                0 0 0 1px rgba(102, 126, 234, 0.3) inset;
}

.sidebar-header {
    padding: 15px;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    gap: 10px;
}

.menu-btn {
    flex-shrink: 0;
}

.category-list {
    flex: 1;
    overflow-y: auto;
    padding: 20px 15px;
}

/* 美化 el-tree 组件 */
.category-list >>> .el-tree {
    background: transparent;
    font-size: 16px;
    font-weight: 500;
}

/* 确保所有子节点容器可见 */
.category-list >>> .el-tree-node__children {
    overflow: visible !important;
}

/* 强制所有标签文字可见 - 移除任何可能导致透明的样式 */
.category-list >>> .el-tree-node__label {
    -webkit-text-fill-color: currentColor !important;
    background-clip: border-box !important;
    -webkit-background-clip: border-box !important;
}

/* 树节点样式 */
.category-list >>> .el-tree-node {
    margin-bottom: 8px;
}

.category-list >>> .el-tree-node__content {
    height: 48px;
    line-height: 48px;
    padding: 0 15px;
    border-radius: 12px;
    margin-bottom: 6px;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
    font-size: 16px;
    font-weight: 500;
    color: #606266;
}

.category-list >>> .el-tree-node__content::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    transform: scaleY(0);
    transition: transform 0.3s ease;
    border-radius: 0 4px 4px 0;
}

.category-list >>> .el-tree-node__content:hover {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.1) 0%, 
        rgba(118, 75, 162, 0.1) 100%);
    color: #667eea;
    transform: translateX(5px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    font-weight: 600;
}

.category-list >>> .el-tree-node__content:hover::before {
    transform: scaleY(1);
}

/* 选中状态 */
.category-list >>> .el-tree-node.is-current > .el-tree-node__content {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.15) 0%, 
        rgba(118, 75, 162, 0.15) 100%);
    color: #667eea;
    font-weight: 700;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2),
                0 0 0 1px rgba(102, 126, 234, 0.2) inset;
}

.category-list >>> .el-tree-node.is-current > .el-tree-node__content::before {
    transform: scaleY(1);
    width: 5px;
}

/* 展开/收起图标 */
.category-list >>> .el-tree-node__expand-icon {
    font-size: 18px;
    color: #667eea;
    transition: all 0.3s ease;
    margin-right: 8px;
}

.category-list >>> .el-tree-node__expand-icon:hover {
    transform: scale(1.2);
    color: #764ba2;
}

.category-list >>> .el-tree-node__expand-icon.is-leaf {
    color: transparent;
}

/* 节点标签文字 */
.category-list >>> .el-tree-node__label {
    font-size: 16px;
    font-weight: 500;
    letter-spacing: 0.3px;
    transition: all 0.3s ease;
    color: #606266;
}

.category-list >>> .el-tree-node__content:hover .el-tree-node__label {
    font-weight: 600;
    color: #667eea;
}

.category-list >>> .el-tree-node.is-current > .el-tree-node__content .el-tree-node__label {
    font-weight: 700;
    color: #667eea;
}

/* 大目录节点特殊样式 - 第1级（直接子节点） */
.category-list >>> .el-tree > .el-tree-node > .el-tree-node__content {
    font-size: 18px;
    font-weight: 700;
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.08) 0%, 
        rgba(118, 75, 162, 0.08) 100%);
    border: 2px solid rgba(102, 126, 234, 0.2);
    margin-bottom: 12px;
}

.category-list >>> .el-tree > .el-tree-node > .el-tree-node__content .el-tree-node__label {
    font-size: 18px;
    font-weight: 700;
    color: #667eea !important;
}

.category-list >>> .el-tree > .el-tree-node > .el-tree-node__content:hover {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.15) 0%, 
        rgba(118, 75, 162, 0.15) 100%);
    border-color: rgba(102, 126, 234, 0.4);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.25);
}

.category-list >>> .el-tree > .el-tree-node > .el-tree-node__content:hover .el-tree-node__label {
    color: #764ba2 !important;
}

/* 第2级节点样式 - 大目录下的子目录 */
.category-list >>> .el-tree > .el-tree-node .el-tree-node__children > .el-tree-node > .el-tree-node__content {
    padding-left: 35px;
    font-size: 15px;
}

.category-list >>> .el-tree > .el-tree-node .el-tree-node__children > .el-tree-node > .el-tree-node__content .el-tree-node__label {
    color: #606266 !important;
    font-weight: 500;
}

/* 第2级节点悬停时保持颜色可见 */
.category-list >>> .el-tree > .el-tree-node .el-tree-node__children > .el-tree-node > .el-tree-node__content:hover .el-tree-node__label {
    color: #667eea !important;
}

/* 第2级节点选中状态 */
.category-list >>> .el-tree > .el-tree-node .el-tree-node__children > .el-tree-node.is-current > .el-tree-node__content .el-tree-node__label {
    color: #667eea !important;
    font-weight: 600;
}

/* 第3级节点样式 - 子目录下的模版 */
.category-list >>> .el-tree > .el-tree-node .el-tree-node__children .el-tree-node__children > .el-tree-node > .el-tree-node__content {
    padding-left: 55px;
    font-size: 14px;
}

.category-list >>> .el-tree > .el-tree-node .el-tree-node__children .el-tree-node__children > .el-tree-node > .el-tree-node__content .el-tree-node__label {
    color: #606266 !important;
    font-weight: 500;
}

/* 第3级节点悬停时保持颜色可见 */
.category-list >>> .el-tree > .el-tree-node .el-tree-node__children .el-tree-node__children > .el-tree-node > .el-tree-node__content:hover .el-tree-node__label {
    color: #667eea !important;
}

/* 第3级节点选中状态 */
.category-list >>> .el-tree > .el-tree-node .el-tree-node__children .el-tree-node__children > .el-tree-node.is-current > .el-tree-node__content .el-tree-node__label {
    color: #667eea !important;
    font-weight: 600;
}

.category-item {
    padding: 12px 20px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #333;
    font-size: 14px;
}

.category-item:hover {
    background-color: #f5f7fa;
    color: #667eea;
}

.category-item.active {
    background-color: #667eea;
    color: white;
    font-weight: bold;
}

/* 右侧内容区域 */
.content-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    margin: 20px 20px 120px 20px;
    border-radius: 20px;
    padding: 30px 30px 40px 30px;
    min-height: calc(100vh - 100px);
    overflow: visible;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15),
                0 0 0 1px rgba(255, 255, 255, 0.3) inset;
    position: relative;
    z-index: 1;
    animation: fadeInScale 0.6s ease;
}

.content-area::before {
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

.content-area::after {
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

@keyframes gradientSlide {
    0% { background-position: 0% 0%; }
    100% { background-position: 200% 0%; }
}

.header-section {
    margin-bottom: 15px;
}

.template-info {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.95) 0%, 
        rgba(248, 249, 250, 0.95) 100%);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1),
                0 0 0 1px rgba(102, 126, 234, 0.1) inset;
    border: 2px solid rgba(102, 126, 234, 0.15);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.template-info:hover {
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2),
                0 0 0 1px rgba(102, 126, 234, 0.25) inset;
    transform: translateY(-2px);
    border-color: rgba(102, 126, 234, 0.3);
}

.info-header {
    position: relative;
    margin-bottom: 10px;
}

.section-label {
    position: absolute;
    top: -15px;
    left: -15px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 6px 14px;
    border-radius: 8px 0 8px 0;
    font-size: 12px;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    letter-spacing: 0.5px;
}

.content-title {
    font-size: 22px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 5px 0 0 0;
    padding-bottom: 12px;
    border-bottom: 2px solid rgba(102, 126, 234, 0.2);
    letter-spacing: 0.5px;
    position: relative;
}

.content-title::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 80px;
    height: 4px;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-radius: 2px;
    animation: pulse-glow 2s infinite;
}

.template-description {
    color: #606266;
    line-height: 1.4;
    background-color: #f9f9f9;
    border-radius: 8px;
    margin-top: 10px;
}

.description-header {
    padding: 10px 15px;
    border-bottom: 2px solid rgba(102, 126, 234, 0.15);
    display: flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.05) 0%, 
        rgba(118, 75, 162, 0.05) 100%);
    border-radius: 8px 8px 0 0;
    color: #667eea;
    font-weight: 700;
    font-size: 14px;
    letter-spacing: 0.3px;
}

.description-content {
    padding: 10px 12px;
    min-height: 50px;
    max-height: 80px;
    line-height: 1.5;
    color: #606266;
    white-space: pre-wrap;
    overflow-y: auto;
}

.template-meta {
    padding: 8px 12px;
    background: #f5f7fa;
    border-radius: 0 0 8px 8px;
    display: flex;
    gap: 20px;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #909399;
    font-size: 12px;
}

.meta-item i {
    font-size: 14px;
    color: #667eea;
}

.template-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100px;
    color: #909399;
    background: #f9f9f9;
    border-radius: 8px;
    margin-top: 10px;
}

.template-placeholder i {
    font-size: 36px;
    margin-bottom: 10px;
    color: #dcdfe6;
}

.template-placeholder p {
    font-size: 13px;
}

/* 筛选区域 */
.filter-section {
    margin-bottom: 25px;
    padding: 20px 25px;
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.95) 0%, 
        rgba(248, 249, 250, 0.95) 100%);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1),
                0 0 0 1px rgba(102, 126, 234, 0.1) inset;
    border: 2px solid rgba(102, 126, 234, 0.15);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}

.filter-section::before {
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

.filter-section:hover::before {
    left: 100%;
}

.filter-section:hover {
    border-color: rgba(102, 126, 234, 0.3);
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2),
                0 0 0 1px rgba(102, 126, 234, 0.2) inset;
    transform: translateY(-2px);
}

.upload-button {
    display: inline-block;
    margin-left: 10px;
}

.upload-button .el-upload {
    display: inline-block;
}

.filter-row {
    display: flex;
    align-items: center;
    gap: 15px;
    flex-wrap: wrap;
}

.filter-item {
    display: flex;
    align-items: center;
    gap: 8px;
}

.filter-item label {
    font-size: 14px;
    color: #606266;
    white-space: nowrap;
}

/* 表格容器 */
.table-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    position: relative;
    min-height: 600px;
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.95) 0%, 
        rgba(248, 249, 250, 0.95) 100%);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 30px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1),
                0 0 0 1px rgba(102, 126, 234, 0.1) inset;
    border: 2px solid rgba(102, 126, 234, 0.15);
    overflow: visible;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.table-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
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
    border-radius: 16px;
}

.table-container:hover::before {
    opacity: 1;
}

.table-container:hover {
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2),
                0 0 0 1px rgba(102, 126, 234, 0.25) inset;
    transform: translateY(-2px);
    border-color: rgba(102, 126, 234, 0.3);
}

.table-scroll-box {
    flex: 1;
    overflow: visible;
    border-radius: 8px;
    position: relative;
}

/* 移除内部滚动条样式，使用外层滚动条控制 */

.el-table {
    flex: 1;
    overflow: visible;
    border-radius: 8px;
}

.el-table__body-wrapper {
    overflow: visible !important;
    max-height: none !important;
    height: auto !important;
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

/* 移除表格内部滚动条样式 */

/* 分页 */
.pagination {
    margin-top: 20px;
    margin-bottom: 100px; /* 增加底部间距，提供更深的滚动距离 */
    padding: 15px 0;
    display: flex;
    justify-content: flex-end;
    background: white;
    border-radius: 8px;
}

.pagination .el-pagination {
    font-weight: 500;
}

.pagination .el-pagination.is-background .el-pager li:not(.disabled).active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
    transition: all 0.3s ease;
}

.pagination .el-pagination.is-background .el-pager li:not(.disabled):hover {
    color: #667eea;
    transform: translateY(-2px);
}

.pagination .el-pagination .btn-prev,
.pagination .el-pagination .btn-next {
    transition: all 0.3s ease;
}

.pagination .el-pagination .btn-prev:hover,
.pagination .el-pagination .btn-next:hover {
    color: #667eea;
    transform: translateY(-2px);
}

/* 滚动条样式 */
.category-list::-webkit-scrollbar {
    width: 8px;
}

.category-list::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    border-radius: 4px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.category-list::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.category-list::-webkit-scrollbar-track {
    background: rgba(245, 247, 250, 0.5);
    border-radius: 4px;
}

/* Sample Serial 单元格样式 */
.sample-serial-cell {
    display: flex;
    align-items: center;
    padding: 8px 0;
}

.sample-serial-text {
    font-size: 14px;
    color: #303133;
    font-weight: 500;
    letter-spacing: 0.3px;
}

/* 操作按钮样式 */
.operation-buttons {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
    white-space: nowrap;
}

.operation-buttons .el-button {
    transition: all 0.3s ease;
}

.operation-buttons .el-button:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 6px 15px rgba(102, 126, 234, 0.4);
}

.operation-buttons .el-button--primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.operation-buttons .el-button--primary:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

/* 响应式设计 */
@media (max-width: 1200px) {
    .main-content {
        flex-direction: column;
    }

    .sidebar {
        width: 100%;
        height: auto;
        max-height: 300px;
    }

    .content-area {
        margin: 10px;
    }
}

@media (max-width: 768px) {
    .filter-row {
        flex-direction: column;
        align-items: stretch;
    }

    .filter-item {
        width: 100%;
    }

    .filter-item label {
        width: 80px;
    }
}

/* 空状态样式优化 */
.el-empty {
    padding: 80px 0;
}

.el-empty__description {
    font-size: 15px;
    color: #909399;
    margin-top: 20px;
}

/* 加载状态优化 */
.el-loading-mask {
    background-color: rgba(255, 255, 255, 0.95) !important;
}

.el-loading-spinner .el-icon-loading {
    font-size: 32px;
    color: #409EFF;
}

.el-loading-text {
    font-size: 14px;
    color: #606266;
}

/* 表格行号样式 */
.el-table .el-table__body td:first-child {
    font-weight: 600;
    color: #909399;
}

/* 优化按钮组间距 */
.filter-row .el-button + .el-button {
    margin-left: 10px;
}

/* Tag标签优化 */
.el-tag {
    transition: all 0.3s ease;
}

.el-tag:hover {
    transform: scale(1.05);
}

/* 详情对话框样式 - 固定85%屏幕大小 */
.detail-dialog-fixed {
    width: 85vw !important;
    height: 85vh !important;
    max-width: none !important;
    min-width: 800px;
    max-height: none !important;
    margin: 0 !important;
    position: fixed !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
}

/* 隐藏弹窗右上角的X按钮 */
.detail-dialog-fixed .el-message-box__headerbtn {
    display: none !important;
}

.detail-dialog-fixed .el-message-box__header .el-message-box__close {
    display: none !important;
}

.detail-dialog-fixed .el-message-box__content {
    max-height: calc(85vh - 120px);
    overflow-y: auto;
    padding: 0;
}

/* 详情对话框滚动条样式 */
.detail-dialog-fixed .el-message-box__content::-webkit-scrollbar {
    width: 12px;
}

.detail-dialog-fixed .el-message-box__content::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #409EFF 0%, #337ecc 100%);
    border-radius: 6px;
    border: 2px solid #f5f7fa;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.detail-dialog-fixed .el-message-box__content::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #337ecc 0%, #2c5aa0 100%);
}

.detail-dialog-fixed .el-message-box__content::-webkit-scrollbar-track {
    background: #f5f7fa;
    border-radius: 6px;
}

.detail-dialog-fixed .el-message-box__content::-webkit-scrollbar-corner {
    background: #f5f7fa;
}

/* 弹窗内容区域滚动条样式 */
.detail-dialog-fixed .el-message-box__content > div::-webkit-scrollbar {
    width: 10px;
}

.detail-dialog-fixed .el-message-box__content > div::-webkit-scrollbar-thumb {
    background: #409EFF;
    border-radius: 5px;
}

.detail-dialog-fixed .el-message-box__content > div::-webkit-scrollbar-thumb:hover {
    background: #337ecc;
}

.detail-dialog-fixed .el-message-box__content > div::-webkit-scrollbar-track {
    background: #f5f7fa;
    border-radius: 5px;
}
</style>