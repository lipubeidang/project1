<template>
    <div class="template-detail-page">
        <Navbar @dropdown-action="handleDropdownAction" />
        <TemplateNavbar @nav-action="handleNavAction" @audit-action="handleAuditAction" />
        
        <!-- 页面标题 -->
        <div class="page-header">
            <h2 class="page-title">{{ templateName }}</h2>
            <div class="header-actions">
                <el-button type="text" icon="el-icon-full-screen" @click="toggleFullscreen">全屏</el-button>
                <el-button type="text" icon="el-icon-close" @click="goBack">关闭</el-button>
            </div>
        </div>

        <!-- 标签页 -->
        <div class="tabs-container">
            <el-tabs v-model="activeTab" type="border-card">
                <el-tab-pane label="模板信息" name="info">
                    <div class="tab-content">
                        <p>模板基本信息</p>
                    </div>
                </el-tab-pane>
                <el-tab-pane label="模板内容" name="content">
                    <!-- 主要内容区域 -->
                    <div class="main-content">
                        <!-- 左侧树形结构 -->
                        <div class="tree-section">
                            <el-tree
                                :data="treeData"
                                :props="treeProps"
                                node-key="id"
                                default-expand-all
                                highlight-current
                                @node-click="handleNodeClick"
                            >
                                <span class="custom-tree-node" slot-scope="{ node, data }">
                                    <span>
                                        <i :class="getNodeIcon(data)"></i>
                                        {{ node.label }}
                                    </span>
                                </span>
                            </el-tree>
                        </div>

                        <!-- 右侧内容区域 -->
                        <div class="content-section">
                            <div class="content-header">
                                <h3>{{ currentNodeTitle }}</h3>
                            </div>
                            <div class="content-body">
                                <!-- 对象区域内容 -->
                                <div v-if="currentNode && currentNode.type === 'object'">
                                    <el-form :model="objectForm" label-width="180px" size="small">
                                        <el-form-item v-for="(value, key) in objectForm" :key="key" :label="getFieldLabel(key)">
                                            <el-input v-model="objectForm[key]" :placeholder="'请输入' + getFieldLabel(key)" />
                                        </el-form-item>
                                    </el-form>
                                </div>

                                <!-- 操作区域内容 -->
                                <div v-if="currentNode && currentNode.type === 'operation'">
                                    <el-form :model="operationForm" label-width="180px" size="small">
                                        <el-form-item v-for="(value, key) in operationForm" :key="key" :label="getFieldLabel(key)">
                                            <el-input v-model="operationForm[key]" :placeholder="'请输入' + getFieldLabel(key)" />
                                        </el-form-item>
                                    </el-form>
                                </div>

                                <!-- 结果区域内容 -->
                                <div v-if="currentNode && currentNode.type === 'result'">
                                    <el-form :model="resultForm" label-width="180px" size="small">
                                        <el-form-item v-for="(value, key) in resultForm" :key="key" :label="getFieldLabel(key)">
                                            <el-input 
                                                v-model="resultForm[key]" 
                                                :type="key === 'viabilityQualitativeDescription' ? 'textarea' : 'text'"
                                                :rows="key === 'viabilityQualitativeDescription' ? 3 : 1"
                                                :placeholder="'请输入' + getFieldLabel(key)" 
                                            />
                                        </el-form-item>
                                    </el-form>
                                </div>

                                <!-- 默认显示 -->
                                <div v-if="!currentNode">
                                    <el-empty description="请从左侧选择一个节点查看详情"></el-empty>
                                </div>
                            </div>
                        </div>
                    </div>
                </el-tab-pane>
                <el-tab-pane label="规则配置" name="rules">
                    <div class="tab-content">
                        <p>规则配置内容</p>
                    </div>
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import TemplateNavbar from '../components/TemplateNavbar.vue';

export default {
    name: "TemplateDetail",
    components: {
        Navbar,
        TemplateNavbar
    },
    data() {
        return {
            templateId: null,
            templateName: '',
            activeTab: 'content',
            currentNode: null,
            currentNodeTitle: '',
            treeProps: {
                children: 'children',
                label: 'label'
            },
            treeData: [
                {
                    id: 'object',
                    label: '对象区域',
                    type: 'object',
                    children: [
                        {
                            id: 'sampleSerial',
                            label: 'sampleSerial(字符串)',
                            type: 'object'
                        },
                        {
                            id: 'sampleMorpholog',
                            label: 'sampleMorpholog(枚举)',
                            type: 'object'
                        },
                        {
                            id: 'sampleSizeLength',
                            label: 'sampleSizeLength(浮点数)',
                            type: 'object'
                        },
                        {
                            id: 'sampleSizeWidth',
                            label: 'sampleSizeWidth(浮点数)',
                            type: 'object'
                        },
                        {
                            id: 'sampleSizeHeight',
                            label: 'sampleSizeHeight(浮点数)',
                            type: 'object'
                        },
                        {
                            id: 'sampleSizeDiameter',
                            label: 'sampleSizeDiameter(浮点数)',
                            type: 'object'
                        },
                        {
                            id: 'sampleSizeThickness',
                            label: 'sampleSizeThickness(浮点数)',
                            type: 'object'
                        },
                        {
                            id: 'sampleSizeUnit',
                            label: 'sampleSizeUnit(枚举)',
                            type: 'object'
                        }
                    ]
                },
                {
                    id: 'operation',
                    label: '操作区域',
                    type: 'operation',
                    children: [
                        {
                            id: 'testMethod',
                            label: 'testMethod(枚举)',
                            type: 'operation'
                        },
                        {
                            id: 'cellType',
                            label: 'cellType(字符串)',
                            type: 'operation'
                        },
                        {
                            id: 'cellSpecies',
                            label: 'cellSpecies(字符串)',
                            type: 'operation'
                        },
                        {
                            id: 'cellSource',
                            label: 'cellSource(字符串)',
                            type: 'operation'
                        },
                        {
                            id: 'passageNumber',
                            label: 'passageNumber(整数)',
                            type: 'operation'
                        },
                        {
                            id: 'cellCultureMethod',
                            label: 'cellCultureMethod(枚举)',
                            type: 'operation'
                        },
                        {
                            id: 'evaluationType',
                            label: 'evaluationType(枚举)',
                            type: 'operation'
                        },
                        {
                            id: 'plateType',
                            label: 'plateType(字符串)',
                            type: 'operation'
                        },
                        {
                            id: 'seedingDensity',
                            label: 'seedingDensity(字符串)',
                            type: 'operation'
                        },
                        {
                            id: 'cultureMedium',
                            label: 'cultureMedium(字符串)',
                            type: 'operation'
                        },
                        {
                            id: 'cultureMediumSupplier',
                            label: 'cultureMediumSupplier(字符串)',
                            type: 'operation'
                        },
                        {
                            id: 'serumConcentration',
                            label: 'serumConcentration(字符串)',
                            type: 'operation'
                        },
                        {
                            id: 'serumSupplier',
                            label: 'serumSupplier(字符串)',
                            type: 'operation'
                        },
                        {
                            id: 'serum',
                            label: 'serum(字符串)',
                            type: 'operation'
                        },
                        {
                            id: 'osteogenicInductionMedium',
                            label: 'osteogenicInductionMedium(枚举)',
                            type: 'operation'
                        },
                        {
                            id: 'penStrep',
                            label: 'penStrep(枚举)',
                            type: 'operation'
                        },
                        {
                            id: 'cellCultureAtmosphere',
                            label: 'cellCultureAtmosphere(字符串)',
                            type: 'operation'
                        },
                        {
                            id: 'cellCultureTemperature',
                            label: 'cellCultureTemperature(浮点数)',
                            type: 'operation'
                        },
                        {
                            id: 'cellCulturePh',
                            label: 'cellCulturePh(字符串)',
                            type: 'operation'
                        },
                        {
                            id: 'cellCultureTime',
                            label: 'cellCultureTime(浮点数)',
                            type: 'operation'
                        },
                        {
                            id: 'cellCultureTimeUnit',
                            label: 'cellCultureTimeUnit(枚举)',
                            type: 'operation'
                        }
                    ]
                },
                {
                    id: 'result',
                    label: '结果区域',
                    type: 'result',
                    children: [
                        {
                            id: 'testSampleShape',
                            label: 'testSampleShape(字符串)',
                            type: 'result'
                        },
                        {
                            id: 'extractionMedium',
                            label: 'extractionMedium(字符串)',
                            type: 'result'
                        },
                        {
                            id: 'extractionCondition',
                            label: 'extractionCondition(字符串)',
                            type: 'result'
                        },
                        {
                            id: 'sterilizationMethod',
                            label: 'sterilizationMethod(字符串)',
                            type: 'result'
                        },
                        {
                            id: 'positiveControl',
                            label: 'positiveControl(字符串)',
                            type: 'result'
                        },
                        {
                            id: 'negativeControl',
                            label: 'negativeControl(字符串)',
                            type: 'result'
                        },
                        {
                            id: 'parallelSampleNumber',
                            label: 'parallelSampleNumber(整数)',
                            type: 'result'
                        },
                        {
                            id: 'testSampleSterility',
                            label: 'testSampleSterility(字符串)',
                            type: 'result'
                        },
                        {
                            id: 'agarDiffusionTest',
                            label: 'agarDiffusionTest(字符串)',
                            type: 'result'
                        },
                        {
                            id: 'filterDiaphragmDiffusionTest',
                            label: 'filterDiaphragmDiffusionTest(字符串)',
                            type: 'result'
                        },
                        {
                            id: 'viabilityQualitativeDescription',
                            label: 'viabilityQualitativeDescription(字符串)',
                            type: 'result'
                        },
                        {
                            id: 'viabilityPicture',
                            label: 'viabilityPicture(图片链接)',
                            type: 'result'
                        }
                    ]
                }
            ],
            objectForm: {
                sampleSerial: '',
                sampleMorpholog: '',
                sampleSizeLength: '',
                sampleSizeWidth: '',
                sampleSizeHeight: '',
                sampleSizeDiameter: '',
                sampleSizeThickness: '',
                sampleSizeUnit: ''
            },
            operationForm: {
                testMethod: '',
                cellType: '',
                cellSpecies: '',
                cellSource: '',
                passageNumber: '',
                cellCultureMethod: '',
                evaluationType: '',
                plateType: '',
                seedingDensity: '',
                cultureMedium: '',
                cultureMediumSupplier: '',
                serumConcentration: '',
                serumSupplier: '',
                serum: '',
                osteogenicInductionMedium: '',
                penStrep: '',
                cellCultureAtmosphere: '',
                cellCultureTemperature: '',
                cellCulturePh: '',
                cellCultureTime: '',
                cellCultureTimeUnit: ''
            },
            resultForm: {
                testSampleShape: '',
                extractionMedium: '',
                extractionCondition: '',
                sterilizationMethod: '',
                positiveControl: '',
                negativeControl: '',
                parallelSampleNumber: '',
                testSampleSterility: '',
                agarDiffusionTest: '',
                filterDiaphragmDiffusionTest: '',
                viabilityQualitativeDescription: '',
                viabilityPicture: ''
            }
        }
    },
    mounted() {
        this.templateId = this.$route.params.id;
        this.templateName = this.$route.query.name || '数据模板详情';
        this.loadTemplateData();
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
        async loadTemplateData() {
            try {
                // 获取路由参数
                const moduleId = this.$route.query.moduleId;
                const sampleSerial = this.$route.query.sampleSerial;
                
                if (!moduleId || !sampleSerial) {
                    this.$message.warning('缺少必要的参数');
                    return;
                }

                // 调用接口获取详细数据
                const response = await this.$request.post('/basemodule/moduledata/getdetail', {
                    sampleSerial: sampleSerial,
                    moduleId: moduleId
                });

                if (response.data && response.data.code === 0) {
                    const { operationList = [], resultList = [] } = response.data;
                    
                    // 处理操作数据
                    if (operationList.length > 0) {
                        const operation = operationList[0]; // 取第一个操作
                        this.operationForm = {
                            testMethod: operation.operation1 || '',
                            cellType: operation.operation2 || '',
                            cellSpecies: operation.operation3 || '',
                            cellSource: '',
                            passageNumber: '',
                            cellCultureMethod: '',
                            evaluationType: '',
                            plateType: '',
                            seedingDensity: '',
                            cultureMedium: '',
                            cultureMediumSupplier: '',
                            serumConcentration: '',
                            serumSupplier: '',
                            serum: '',
                            osteogenicInductionMedium: '',
                            penStrep: '',
                            cellCultureAtmosphere: '',
                            cellCultureTemperature: '',
                            cellCulturePh: '',
                            cellCultureTime: '',
                            cellCultureTimeUnit: ''
                        };
                    }

                    // 处理结果数据
                    if (resultList.length > 0) {
                        const result = resultList[0]; // 取第一个结果
                        this.resultForm = {
                            testSampleShape: result.result1 || '',
                            extractionMedium: result.result2 || '',
                            extractionCondition: result.result3 || '',
                            sterilizationMethod: '',
                            positiveControl: '',
                            negativeControl: '',
                            parallelSampleNumber: '',
                            testSampleSterility: '',
                            agarDiffusionTest: '',
                            filterDiaphragmDiffusionTest: '',
                            viabilityQualitativeDescription: '',
                            viabilityPicture: ''
                        };
                    }

                    // 设置对象数据
                    this.objectForm = {
                        sampleSerial: sampleSerial,
                        sampleMorpholog: '',
                        sampleSizeLength: '',
                        sampleSizeWidth: '',
                        sampleSizeHeight: '',
                        sampleSizeDiameter: '',
                        sampleSizeThickness: '',
                        sampleSizeUnit: ''
                    };
                    
                    console.log('加载的模板数据:', response.data);
                } else {
                    throw new Error(response.data.msg || '获取数据失败');
                }
            } catch (error) {
                console.error('加载模板数据失败:', error);
                this.$message.error('加载模板数据失败，请稍后重试');
            }
        },
        handleNodeClick(data) {
            this.currentNode = data;
            this.currentNodeTitle = data.label;
        },
        getNodeIcon(data) {
            const iconMap = {
                'object': 'el-icon-folder-opened',
                'operation': 'el-icon-setting',
                'result': 'el-icon-document',
                'aging': 'el-icon-time'
            };
            return iconMap[data.type] || 'el-icon-document';
        },
        getFieldLabel(key) {
            // 从树形数据中查找对应的标签
            const findLabel = (nodes) => {
                for (const node of nodes) {
                    if (node.id === key) {
                        return node.label;
                    }
                    if (node.children) {
                        const found = findLabel(node.children);
                        if (found) return found;
                    }
                }
                return null;
            };
            
            return findLabel(this.treeData) || key;
        },
        toggleFullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        },
        goBack() {
            console.log('返回上一页');
            // 使用浏览器历史记录返回，保持模板库的状态
            if (window.history.length > 1) {
                this.$router.go(-1);
            } else {
                // 如果没有历史记录，跳转到模板库页面
                this.$router.replace('/templatelibrary').catch(() => {});
            }
        }
    }
}
</script>

<style scoped>
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes pulse-border {
  0%, 100% {
    border-color: rgba(102, 126, 234, 0.3);
  }
  50% {
    border-color: rgba(102, 126, 234, 0.6);
  }
}

.template-detail-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7474bf 100%);
    background-size: 200% 200%;
    animation: gradientShift 15s ease infinite;
    position: relative;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.template-detail-page::before {
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

/* 页面标题 */
.page-header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    padding: 25px 35px;
    border-bottom: 2px solid rgba(102, 126, 234, 0.15);
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 60px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    position: relative;
    z-index: 1;
    animation: fadeInUp 0.6s ease;
}

.page-header::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 150px;
  height: 2px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  animation: pulse-border 2s infinite;
}

.page-title {
    margin: 0;
    font-size: 24px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.5px;
}

.header-actions {
    display: flex;
    gap: 12px;
}

.header-actions .el-button {
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.1) 0%, 
    rgba(118, 75, 162, 0.1) 100%);
  border: 2px solid rgba(102, 126, 234, 0.3);
  color: #667eea;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border-radius: 8px;
}

.header-actions .el-button:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

/* 标签页容器 */
.tabs-container {
    margin: 25px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
    overflow: hidden;
    position: relative;
    z-index: 1;
    animation: fadeInUp 0.8s ease 0.2s both;
}

.tab-content {
    padding: 20px;
}

/* 主要内容区域 */
.main-content {
    display: flex;
    height: calc(100vh - 300px);
    min-height: 500px;
}

/* 左侧树形结构 */
.tree-section {
    width: 370px;
    background: linear-gradient(135deg, 
      rgba(249, 250, 251, 0.95) 0%, 
      rgba(245, 247, 250, 0.95) 100%);
    backdrop-filter: blur(10px);
    border-right: 2px solid rgba(102, 126, 234, 0.15);
    overflow-y: auto;
    padding: 25px 15px;
    position: relative;
}

.tree-section::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 2px;
  height: 100px;
  background: linear-gradient(180deg, 
    #667eea 0%, 
    transparent 100%);
}

.custom-tree-node {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    font-weight: 500;
}

.custom-tree-node i {
    color: #667eea;
    font-size: 16px;
    transition: all 0.3s ease;
}

.el-tree-node:hover .custom-tree-node i {
  transform: scale(1.2) rotate(10deg);
}

/* 右侧内容区域 */
.content-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.95);
    overflow: hidden;
}

.content-header {
    padding: 25px 35px;
    border-bottom: 2px solid rgba(102, 126, 234, 0.1);
    background: linear-gradient(135deg, 
      rgba(102, 126, 234, 0.05) 0%, 
      rgba(118, 75, 162, 0.05) 100%);
    position: relative;
}

.content-header::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 35px;
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.content-header h3 {
    margin: 0;
    font-size: 20px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.5px;
}

.content-body {
    flex: 1;
    padding: 35px;
    overflow-y: auto;
    background: rgba(255, 255, 255, 0.5);
}

.form-tip {
    margin-top: 20px;
    padding: 10px 15px;
    background-color: #f0f9ff;
    border-left: 4px solid #667eea;
    color: #666;
    font-size: 14px;
}

/* Element UI 表单样式调整 */
::v-deep .el-form-item {
    margin-bottom: 22px;
}

::v-deep .el-form-item__label {
    color: #606266;
    font-weight: 500;
}

::v-deep .el-input__inner {
    border-radius: 4px;
}

/* 树形控件样式 */
::v-deep .el-tree {
    background-color: transparent;
}

::v-deep .el-tree-node__content {
    height: 42px;
    border-radius: 10px;
    margin: 4px 0;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    padding: 0 12px;
}

::v-deep .el-tree-node__content:hover {
    background: linear-gradient(135deg, 
      rgba(102, 126, 234, 0.1) 0%, 
      rgba(118, 75, 162, 0.1) 100%);
    transform: translateX(5px);
    box-shadow: -3px 0 0 0 rgba(102, 126, 234, 0.4) inset;
}

::v-deep .el-tree-node.is-current > .el-tree-node__content {
    background: linear-gradient(135deg, 
      rgba(102, 126, 234, 0.15) 0%, 
      rgba(118, 75, 162, 0.15) 100%);
    color: #667eea;
    font-weight: 700;
    transform: translateX(8px);
    box-shadow: -4px 0 0 0 rgba(102, 126, 234, 0.6) inset,
                0 4px 15px rgba(102, 126, 234, 0.2);
}

::v-deep .el-tree-node__expand-icon {
  color: #667eea;
  font-size: 14px;
  transition: all 0.3s ease;
}

/* 标签页样式 */
::v-deep .el-tabs--border-card {
    border: none;
    box-shadow: none;
    background: transparent;
}

::v-deep .el-tabs__header {
    background: linear-gradient(135deg, 
      rgba(102, 126, 234, 0.05) 0%, 
      rgba(118, 75, 162, 0.05) 100%);
    border-bottom: 2px solid rgba(102, 126, 234, 0.15);
    margin-bottom: 0;
}

::v-deep .el-tabs__item {
    font-weight: 600;
    color: #606266;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    border-radius: 8px 8px 0 0;
    padding: 0 25px;
}

::v-deep .el-tabs__item:hover {
  color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

::v-deep .el-tabs__item.is-active {
    background: rgba(255, 255, 255, 0.95);
    color: #667eea;
    font-weight: 700;
    border-bottom-color: transparent;
    box-shadow: 0 -4px 15px rgba(102, 126, 234, 0.15);
}

::v-deep .el-tabs__nav-wrap::after {
  display: none;
}

/* 滚动条样式 */
.tree-section::-webkit-scrollbar,
.content-body::-webkit-scrollbar {
    width: 8px;
}

.tree-section::-webkit-scrollbar-track,
.content-body::-webkit-scrollbar-track {
  background: rgba(245, 247, 250, 0.5);
  border-radius: 10px;
}

.tree-section::-webkit-scrollbar-thumb,
.content-body::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    transition: all 0.3s ease;
}

.tree-section::-webkit-scrollbar-thumb:hover,
.content-body::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

/* 响应式设计 */
@media (max-width: 1200px) {
    .main-content {
        flex-direction: column;
    }

    .tree-section {
        width: 100%;
        max-height: 300px;
        border-right: none;
        border-bottom: 1px solid #e0e0e0;
    }

    .content-section {
        min-height: 400px;
    }
}
</style>