<template>
    <div class="template-audit-detail-page">
        <!-- 顶部导航 -->
        <Navbar @dropdown-action="handleDropdownAction" />
        <TemplateNavbar @nav-action="handleNavAction" @audit-action="handleAuditAction" />

        <!-- 主容器 -->
        <div class="container" v-loading="loading" element-loading-text="正在加载模板详情...">
            <div class="page-header">
                <el-button icon="el-icon-arrow-left" @click="goBack" class="back-btn">返回审核列表</el-button>
                <h2>{{ templateInfo.name || '模版字段信息' }}</h2>
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

            <!-- 底部操作按钮 -->
            <div class="footer-actions">
                <el-button @click="goBack" class="close-btn">返回</el-button>
                <el-button 
                    v-if="isEditable && isPendingTemplate" 
                    type="success"
                    @click="approveTemplate"
                    :loading="approving"
                    class="approve-btn"
                >
                    <i class="el-icon-check"></i>
                    审核通过
                </el-button>
            </div>
        </div>
    </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import TemplateNavbar from '../components/TemplateNavbar.vue';

export default {
    name: 'TemplateAuditDetail',
    components: {
        Navbar,
        TemplateNavbar
    },
    data() {
        return {
            templateInfo: {},
            fields: {
                object: [],
                operation: [],
                result: []
            },
            isEditable: false,
            isPendingTemplate: false,
            approving: false,
            loading: false,
            nextId: 1
        };
    },
    mounted() {
        // 从路由参数获取模板信息
        const templateId = this.$route.params.templateId || this.$route.query.templateId;
        const isEditable = this.$route.params.isEditable || this.$route.query.isEditable;
        const isPending = this.$route.params.isPending || this.$route.query.isPending;
        
        this.isEditable = isEditable === true || isEditable === 'true';
        this.isPendingTemplate = isPending === true || isPending === 'true';
        
        if (!templateId) {
            this.$message.error('缺少模板ID参数');
            this.goBack();
            return;
        }
        
        // 加载模板详情
        this.loadTemplateDetail(templateId);
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
            }
        },
        goBack() {
            this.$router.push('/template-audit').catch(() => {});
        },
        async loadTemplateDetail(templateId) {
            this.loading = true;
            try {
                console.log('加载模板详情，ID:', templateId);
                const response = await this.$request.get(`http://localhost:8083/basemodule/process/detail/${templateId}`);
                console.log('模板详情响应:', response);
                
                if (response.data && response.data.code === 0) {
                    const templateDetail = response.data.data || {};
                    console.log('模板详情数据:', templateDetail);
                    
                    this.templateInfo = {
                        id: templateId,
                        name: templateDetail.name,
                        createTime: templateDetail.createTime,
                        creator: templateDetail.creator || '未知',
                        description: templateDetail.description || '暂无描述'
                    };
                    
                    // 解析字段信息
                    this.fields = {
                        object: templateDetail.object || [],
                        operation: templateDetail.operation || [],
                        result: templateDetail.result || []
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
                } else {
                    throw new Error(response.data.msg || '获取模板详情失败');
                }
            } catch (error) {
                console.error('加载模板详情失败:', error);
                this.$message.error('加载模板详情失败: ' + (error.message || '请重试'));
                this.goBack();
            } finally {
                this.loading = false;
            }
        },
        async approveTemplate() {
            try {
                this.approving = true;
                
                // 验证必要字段
                if (!this.templateInfo.id) {
                    throw new Error('模版ID不能为空');
                }
                
                // 构建createtable接口的请求参数
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
                    this.$message.success('模版审核通过，数据表创建成功');
                    // 返回审核页面
                    this.goBack();
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
};
</script>

<style scoped>
@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
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

.template-audit-detail-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7474bf 100%);
    background-size: 200% 200%;
    animation: gradientShift 15s ease infinite;
    padding-top: 140px;
    position: relative;
}

.template-audit-detail-page::before {
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
    margin: 40px auto 100px;
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
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.page-header h2 {
    font-size: 28px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    font-weight: 700;
}

.fields-container {
    display: flex;
    flex-direction: column;
    gap: 25px;
}

.field-section {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 16px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
    border: 2px solid rgba(102, 126, 234, 0.15);
    overflow: hidden;
    transition: all 0.3s ease;
    animation: slideIn 0.4s ease;
}

.field-section:hover {
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.22);
    transform: translateY(-2px);
    border-color: rgba(102, 126, 234, 0.3);
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
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.field-item:hover {
    background: rgba(255, 255, 255, 1);
    border-color: rgba(102, 126, 234, 0.3);
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.22);
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
    transition: all 0.3s ease;
}

.field-item:hover .field-icon {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.2) 0%, 
        rgba(118, 75, 162, 0.2) 100%);
    border-color: rgba(102, 126, 234, 0.4);
    transform: rotate(10deg) scale(1.1);
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

.footer-actions {
    margin-top: 30px;
    text-align: center;
    padding-top: 20px;
    border-top: 2px solid rgba(102, 126, 234, 0.15);
    display: flex;
    justify-content: center;
    gap: 15px;
}

.close-btn {
    padding: 12px 30px;
    font-weight: 600;
    border: 2px solid rgba(102, 126, 234, 0.3);
    color: #667eea;
    background: rgba(255, 255, 255, 0.9);
    transition: all 0.3s ease;
}

.close-btn:hover {
    background: linear-gradient(135deg, 
        rgba(102, 126, 234, 0.1) 0%, 
        rgba(118, 75, 162, 0.1) 100%);
    border-color: #667eea;
    color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.25);
}

.approve-btn {
    background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
    border: none;
    color: white;
    padding: 12px 30px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.approve-btn:hover {
    background: linear-gradient(135deg, #85ce61 0%, #67c23a 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(103, 194, 58, 0.4);
}

.approve-btn i {
    margin-right: 5px;
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
}
</style>

