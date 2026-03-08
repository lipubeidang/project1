<template>
    <div class="template-audit-page" :key="componentKey">
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
                <!-- 页面标题 -->
                <div class="page-header">
                    <h2>模版审核</h2>
                    <p v-if="currentNode && currentNode.name">当前目录：{{ currentNode.name }}</p>
                    <p v-else>请选择左侧目录查看该目录下的模版</p>
                </div>

                <!-- 审核状态切换 -->
                <div class="audit-tabs">
                    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
                        <el-tab-pane label="未审核" name="pending">
                            <div class="tab-content">
                                <div class="templates-grid" v-if="pendingTemplates.length > 0">
                                    <div 
                                        v-for="template in pendingTemplates" 
                                        :key="template.id"
                                        class="template-card"
                                    >
                                        <div class="template-header">
                                            <h4>{{ template.name }}</h4>
                                            <el-tag type="warning">未审核</el-tag>
                                        </div>
                                        <div class="template-info">
                                            <p><strong>创建者：</strong>{{ template.creator || '未知' }}</p>
                                            <p><strong>创建时间：</strong>{{ formatDate(template.createTime) }}</p>
                                            <p><strong>描述：</strong>{{ template.description || '暂无描述' }}</p>
                                        </div>
                                        <div class="template-actions">
                                            <el-button 
                                                type="primary" 
                                                size="small"
                                                @click="viewTemplateDetail(template)"
                                            >
                                                审核模版
                                            </el-button>
                                            <el-button 
                                                type="danger" 
                                                size="small"
                                                @click="rejectTemplate(template)"
                                            >
                                                拒绝
                                            </el-button>
                                        </div>
                                    </div>
                                </div>
                                <div v-else class="no-data">
                                    <el-empty description="暂无待审核的模版"></el-empty>
                                </div>
                            </div>
                        </el-tab-pane>
                        
                        <el-tab-pane label="已通过" name="approved">
                            <div class="tab-content">
                                <div class="templates-grid" v-if="approvedTemplates.length > 0">
                                    <div 
                                        v-for="template in approvedTemplates" 
                                        :key="template.id"
                                        class="template-card approved"
                                    >
                                        <div class="template-header">
                                            <h4>{{ template.name }}</h4>
                                            <el-tag type="success">已通过</el-tag>
                                        </div>
                        <div class="template-info">
                            <p><strong>创建者：</strong>{{ template.creator || '未知' }}</p>
                            <p><strong>创建时间：</strong>{{ formatDate(template.createTime) }}</p>
                            <p><strong>描述：</strong>{{ template.description || '暂无描述' }}</p>
                        </div>
                                        <div class="template-actions">
                                            <el-button 
                                                type="primary" 
                                                size="small"
                                                @click="viewTemplateDetail(template)"
                                            >
                                                查看详情
                                            </el-button>
                                        </div>
                                    </div>
                                </div>
                                <div v-else class="no-data">
                                    <el-empty description="暂无已通过的模版"></el-empty>
                                </div>
                            </div>
                        </el-tab-pane>
                    </el-tabs>
                </div>
            </div>
        </div>

        <!-- 模板详情对话框 -->
        <TemplateDescription 
            :visible.sync="showTemplateDescription"
            :template="currentTemplate"
        />
    </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import TemplateNavbar from '../components/TemplateNavbar.vue';
import TemplateDescription from '../components/TemplateDescription.vue';

export default {
    name: "TemplateAudit",
    components: {
        Navbar,
        TemplateNavbar,
        TemplateDescription
    },
    data() {
        return {
            componentKey: 0,
            activeTab: 'pending',
            directoryTree: [],
            defaultProps: {
                children: 'children',
                label: 'name'
            },
            currentNode: null,
            selectedCategory: '',
            pendingTemplates: [], // state = 0 的模版
            approvedTemplates: [], // state = 1 的模版
            showTemplateDescription: false,
            currentTemplate: null
        }
    },
    mounted() {
        // 权限检查：只有管理员可以访问审核管理页面
        this.checkAdminPermission();
        console.log('TemplateAudit 组件已挂载');
        this.loadDirectoryTree();
        // 初始时不加载模版数据，等用户选择目录后再加载
    },
    methods: {
        // 检查管理员权限
        checkAdminPermission() {
            // 优先从Vuex获取
            let userRole = this.$store.getters.getUserRole;
            
            // 如果Vuex中没有，从localStorage获取
            if (!userRole) {
                try {
                    const userData = JSON.parse(localStorage.getItem('xm-user') || '{}');
                    userRole = userData.role || userData.logininfo?.type || userData.logininfo?.userType || userData.logininfo?.role || 1;
                } catch (error) {
                    console.error('获取用户权限失败:', error);
                    userRole = 1; // 默认普通用户
                }
            }
            
            // 只有管理员（role=2）可以访问
            if (userRole !== 2) {
                this.$message.error('权限不足：只有管理员可以访问审核管理页面');
                this.$router.push('/').catch(err => {
                    // 忽略导航重复错误
                    if (err.name !== 'NavigationDuplicated') {
                        console.error('路由跳转失败:', err);
                    }
                });
                return false;
            }
            return true;
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
                    this.$router.push('/template-create').catch(() => {});
                    break;
            }
        },
        handleAuditAction(action) {
            switch (action) {
                case 'templateAudit':
                    // 当前页面，不需要跳转
                    break;
                case 'templateStop':
                    this.$message.info('进入模版停用页面');
                    // TODO: 跳转到模版停用页面
                    break;
            }
        },
        handleTabClick(tab) {
            console.log('切换到标签页:', tab.name);
        },
        async loadDirectoryTree() {
            try {
                // 定义完整的三级目录结构（写死，模仿模板库页面）
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

                // 构建目录树，小目录固定，不需要获取模板
                this.directoryTree = directoryStructure.map(bigCat => ({
                    id: bigCat.id,
                    name: bigCat.name,
                    isBigCategory: true,
                    isParent: true,
                    children: bigCat.subCategories.map(subCat => ({
                        id: subCat.id,
                        name: subCat.name,
                        isSubCategory: true,
                        isParent: true,
                        parentId: bigCat.id,
                        parentName: bigCat.name
                    }))
                }));
                
                console.log('加载完成的目录树:', this.directoryTree);
            } catch (error) {
                console.error('加载目录失败:', error);
                this.$message.error('加载目录失败');
            }
        },
        async loadTemplateData(parentId = null) {
            try {
                // 分别加载未审核和已通过的模版
                await Promise.all([
                    this.loadPendingTemplates(parentId),
                    this.loadApprovedTemplates(parentId)
                ]);
                
                console.log('待审核模板:', this.pendingTemplates);
                console.log('已通过模板:', this.approvedTemplates);
            } catch (error) {
                console.error('加载模板数据失败:', error);
                this.$message.error('加载模板数据失败: ' + error.message);
            }
        },
        
        async loadPendingTemplates(parentId = null) {
            try {
                // 获取未审核模版列表
                const response = await this.$request.get('http://localhost:8083/basemodule/process/list');
                
                if (response.data && response.data.code === 0) {
                    const allPendingTemplates = response.data.data || [];
                    
                    // 如果选择了特定的父目录，则过滤该目录下的模版
                    if (parentId) {
                        this.pendingTemplates = allPendingTemplates.filter(template => 
                            template.parent === parentId || template.parentId === parentId
                        );
                    } else {
                        this.pendingTemplates = allPendingTemplates;
                    }
                } else {
                    throw new Error(response.data.msg || '获取未审核模版列表失败');
                }
            } catch (error) {
                console.error('加载未审核模板失败:', error);
                this.pendingTemplates = [];
                throw error;
            }
        },
        
        async loadApprovedTemplates(parentId = null) {
            try {
                if (parentId) {
                    // 获取指定父目录下的已通过模版
                    const response = await this.$request.get(`http://localhost:8083/basemodule/module/getmodules/${parentId}`);
                    
                    if (response.data && response.data.code === 0) {
                        const templates = response.data.module_list || [];
                        // 只显示已通过的模版 (state = 1)
                        this.approvedTemplates = templates.filter(template => template.state === 1);
                    } else {
                        throw new Error(response.data.msg || '获取已通过模版列表失败');
                    }
                } else {
                    // 如果没有选择父目录，获取所有父目录下的已通过模版
                    const parentResponse = await this.$request.get('/basemodule/moduleparent/list');
                    if (parentResponse.data.code === 0) {
                        const allModules = parentResponse.data.module_list || [];
                        let allApprovedTemplates = [];
                        
                        // 获取前7个父目录下的所有已通过模版
                        const first7Modules = allModules.slice(0, 7);
                        for (const module of first7Modules) {
                            try {
                                const templatesResponse = await this.$request.get(`http://localhost:8083/basemodule/module/getmodules/${module.id}`);
                                if (templatesResponse.data && templatesResponse.data.code === 0) {
                                    const templates = templatesResponse.data.module_list || [];
                                    // 只添加已通过的模版，并添加父目录信息
                                    const approvedInModule = templates
                                        .filter(template => template.state === 1)
                                        .map(template => ({
                                            ...template,
                                            parentName: module.name,
                                            parentId: module.id
                                        }));
                                    allApprovedTemplates = allApprovedTemplates.concat(approvedInModule);
                                }
                            } catch (error) {
                                console.error(`获取目录 ${module.name} 的已通过模板失败:`, error);
                            }
                        }
                        
                        this.approvedTemplates = allApprovedTemplates;
                    }
                }
            } catch (error) {
                console.error('加载已通过模板失败:', error);
                this.approvedTemplates = [];
                throw error;
            }
        },
        handleNodeClick(data) {
            this.currentNode = data;
            console.log('选中节点:', data);
            
            // 如果点击的是大目录，不加载数据
            if (data.isBigCategory) {
                console.log('点击大目录，不加载数据');
                return;
            }
            
            // 如果点击的是小目录（子目录），加载该目录下的模版
            if (data.isSubCategory || data.isParent) {
                this.loadTemplateData(data.id);
            }
        },
        rejectTemplate(template) {
            this.$confirm('确定要拒绝这个模版吗？', '确认操作', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                // 从待审核列表中移除
                const index = this.pendingTemplates.findIndex(t => t.id === template.id);
                if (index !== -1) {
                    this.pendingTemplates.splice(index, 1);
                }
                this.$message.success('已拒绝该模版');
            }).catch(() => {
                // 用户取消操作
            });
        },
        async revokeApproval(template) {
            try {
                await this.$confirm('确定要撤销这个模版的审核吗？', '确认操作', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                });
                
                // 更新模板状态为未审核
                template.state = 0;
                
                // 从已通过列表移除
                const index = this.approvedTemplates.findIndex(t => t.id === template.id);
                if (index !== -1) {
                    this.approvedTemplates.splice(index, 1);
                }
                
                // 重新加载未审核的模版列表
                if (this.currentNode && this.currentNode.id) {
                    await this.loadPendingTemplates(this.currentNode.id);
                } else {
                    await this.loadPendingTemplates();
                }
                
                this.$message.success('已撤销该模版的审核');
            } catch (error) {
                if (error !== 'cancel') {
                    console.error('撤销审核失败:', error);
                    this.$message.error('撤销审核失败');
                }
            }
        },
        viewTemplateDetail(template) {
            try {
                // 判断是未审核模版还是已通过模版
                const isPendingTemplate = this.pendingTemplates.some(t => t.id === template.id);
                
                console.log('查看模版详情，ID:', template.id, '是否待审核:', isPendingTemplate);
                
                // 跳转到模版详情页面
                this.$router.push({
                    name: 'TemplateAuditDetail',
                    params: {
                        templateId: template.id
                    },
                    query: {
                        isEditable: isPendingTemplate ? 'true' : 'false',
                        isPending: isPendingTemplate ? 'true' : 'false'
                    }
                });
            } catch (error) {
                console.error('跳转模版详情失败:', error);
                this.$message.error('跳转模版详情失败');
            }
        },

        handleTemplateApproved(template) {
            // 处理模版审核通过事件
            const index = this.pendingTemplates.findIndex(t => t.id === template.id);
            if (index !== -1) {
                const approvedTemplate = this.pendingTemplates[index];
                approvedTemplate.state = 1;
                
                // 从待审核列表移除
                this.pendingTemplates.splice(index, 1);
                
                // 添加到已通过列表（如果当前显示的是同一个目录）
                if (this.currentNode && this.currentNode.id === approvedTemplate.parentId) {
                    this.approvedTemplates.push(approvedTemplate);
                }
            }
            
            // 重新加载已通过的模版列表以确保数据同步
            if (this.currentNode && this.currentNode.id) {
                this.loadApprovedTemplates(this.currentNode.id);
            } else {
                this.loadApprovedTemplates();
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

@keyframes shimmer {
  0% { transform: translateX(-50%) translateY(-50%) rotate(0deg); }
  100% { transform: translateX(-50%) translateY(-50%) rotate(360deg); }
}

.template-audit-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7474bf 100%);
    background-size: 200% 200%;
    animation: gradientShift 15s ease infinite;
    padding-top: 100px;
    position: relative;
    overflow-x: hidden;
}

.template-audit-page::before {
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

.main-content {
    display: flex;
    margin-top: 100px;
    min-height: calc(100vh - 100px);
    position: relative;
    z-index: 1;
}

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
    padding: 20px;
    overflow-y: auto;
    position: relative;
    z-index: 1;
    animation: slideDown 0.6s ease;
    transition: all 0.3s ease;
}

.sidebar:hover {
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2),
                0 0 0 1px rgba(102, 126, 234, 0.3) inset;
}

.category-list {
    height: 100%;
    padding: 20px 15px;
    overflow-y: auto;
}

/* 美化 el-tree 组件 */
.category-list >>> .el-tree {
    background: transparent;
    font-size: 16px;
    font-weight: 500;
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
}

.category-list >>> .el-tree-node__content:hover .el-tree-node__label {
    font-weight: 600;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.category-list >>> .el-tree-node.is-current > .el-tree-node__content .el-tree-node__label {
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* 大目录节点特殊样式 */
.category-list >>> .el-tree-node[data-level="1"] > .el-tree-node__content {
    font-size: 18px;
    font-weight: 700;
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.08) 0%, 
        rgba(118, 75, 162, 0.08) 100%);
    border: 2px solid rgba(102, 126, 234, 0.2);
    margin-bottom: 12px;
}

.category-list >>> .el-tree-node[data-level="1"] > .el-tree-node__content .el-tree-node__label {
    font-size: 18px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.category-list >>> .el-tree-node[data-level="1"] > .el-tree-node__content:hover {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.15) 0%, 
        rgba(118, 75, 162, 0.15) 100%);
    border-color: rgba(102, 126, 234, 0.4);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.25);
}

/* 子目录节点样式 */
.category-list >>> .el-tree-node[data-level="2"] > .el-tree-node__content {
    padding-left: 35px;
    font-size: 15px;
}

.category-list >>> .el-tree-node[data-level="2"] > .el-tree-node__content .el-tree-node__label {
    color: #606266;
    font-weight: 500;
}

.category-list >>> .el-tree-node[data-level="3"] > .el-tree-node__content {
    padding-left: 55px;
    font-size: 14px;
}

.category-list >>> .el-tree-node[data-level="3"] > .el-tree-node__content .el-tree-node__label {
    color: #606266;
    font-weight: 500;
}

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

.page-header {
    margin-bottom: 35px;
    position: relative;
    padding-bottom: 15px;
}

.page-header::after {
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

.page-header h2 {
    font-size: 28px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 10px 0;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.page-header p {
    color: #606266;
    margin: 0;
    font-size: 14px;
}

.audit-tabs {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.95) 0%, 
        rgba(248, 249, 250, 0.95) 100%);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1),
                0 0 0 1px rgba(102, 126, 234, 0.1) inset;
    border: 2px solid rgba(102, 126, 234, 0.15);
    transition: all 0.3s ease;
}

.audit-tabs:hover {
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15),
                0 0 0 1px rgba(102, 126, 234, 0.2) inset;
}

.tab-content {
    margin-top: 20px;
}

.templates-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 20px;
}

.template-card {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.95) 0%, 
        rgba(248, 249, 250, 0.95) 100%);
    backdrop-filter: blur(10px);
    border: 2px solid rgba(102, 126, 234, 0.15);
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1),
                0 0 0 1px rgba(255, 255, 255, 0.3) inset;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
    animation: fadeInScale 0.4s ease;
}

.template-card::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, 
        transparent 30%, 
        rgba(102, 126, 234, 0.1) 50%, 
        transparent 70%);
    transform: rotate(45deg);
    transition: all 0.6s ease;
    opacity: 0;
}

.template-card:hover::before {
    opacity: 1;
    animation: shimmer 1.5s infinite;
}

.template-card:hover {
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2),
                0 0 0 1px rgba(102, 126, 234, 0.25) inset;
    transform: translateY(-5px) scale(1.02);
    border-color: rgba(102, 126, 234, 0.3);
}

.template-card.approved {
    border-left: 4px solid #67c23a;
}

.template-card.approved::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, #67c23a 0%, #85ce61 100%);
    border-radius: 16px 0 0 16px;
}

.template-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 2px solid rgba(102, 126, 234, 0.1);
    position: relative;
    z-index: 1;
}

.template-header h4 {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.3px;
}

.template-info {
    margin-bottom: 20px;
    position: relative;
    z-index: 1;
}

.template-info p {
    margin: 10px 0;
    color: #606266;
    font-size: 14px;
    line-height: 1.6;
}

.template-info p strong {
    color: #667eea;
    font-weight: 600;
}

.template-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    position: relative;
    z-index: 1;
}

.template-actions .el-button {
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.template-actions .el-button--primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
}

.template-actions .el-button--primary:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.template-actions .el-button--danger:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 6px 20px rgba(245, 108, 108, 0.5);
}

.no-data {
    text-align: center;
    padding: 60px 40px;
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.5) 0%, 
        rgba(248, 249, 250, 0.5) 100%);
    border-radius: 16px;
    border: 2px dashed rgba(102, 126, 234, 0.2);
}

/* 标签页样式优化 */
.audit-tabs >>> .el-tabs__header {
    margin-bottom: 20px;
}

.audit-tabs >>> .el-tabs__item {
    font-size: 16px;
    font-weight: 600;
    color: #606266;
    transition: all 0.3s ease;
}

.audit-tabs >>> .el-tabs__item.is-active {
    color: #667eea;
}

.audit-tabs >>> .el-tabs__active-bar {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    height: 3px;
}

.audit-tabs >>> .el-tabs__item:hover {
    color: #667eea;
}

/* 滚动条样式 */
.sidebar::-webkit-scrollbar,
.category-list::-webkit-scrollbar {
    width: 8px;
}

.sidebar::-webkit-scrollbar-thumb,
.category-list::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    border-radius: 4px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.sidebar::-webkit-scrollbar-thumb:hover,
.category-list::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.sidebar::-webkit-scrollbar-track,
.category-list::-webkit-scrollbar-track {
    background: rgba(245, 247, 250, 0.5);
    border-radius: 4px;
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
        margin: 20px;
        border-radius: 20px;
    }
    
    .content-area {
        margin: 10px 20px 120px 20px;
    }
}

@media (max-width: 768px) {
    .templates-grid {
        grid-template-columns: 1fr;
    }
    
    .template-card {
        padding: 20px;
    }
    
    .page-header h2 {
        font-size: 24px;
    }
}
</style>
