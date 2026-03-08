<template>
    <div class="model-training-page">
        <Navbar @dropdown-action="handleDropdownAction" />
        <TemplateNavbar @nav-action="handleNavAction" @audit-action="handleAuditAction" />

        <!-- 主要内容区域 -->
        <div class="main-content">
            <div class="content-container">
                <div class="page-header">
                    <div class="header-top">
                        <el-button 
                            type="info" 
                            icon="el-icon-arrow-left"
                            @click="handleBack"
                            class="back-button"
                        >
                            返回
                        </el-button>
                        <h2>模型训练</h2>
                    </div>
                </div>

                <div class="training-layout">
                    <!-- 左侧：当前训练进度 -->
                    <div class="current-training-section">
                        <div class="section-header">
                            <h3>
                                <i class="el-icon-loading"></i>
                                当前训练进度
                            </h3>
                        </div>
                        <div class="training-progress-box" v-if="isTraining">
                            <el-progress 
                                :percentage="trainingProgress" 
                                :status="trainingProgress === 100 ? 'success' : ''"
                                :stroke-width="24"
                                class="progress-bar"
                            ></el-progress>
                            <p class="progress-text">{{ trainingProgressText }}</p>
                            <div class="training-info">
                                <p><strong>训练数据量：</strong>{{ trainingDataCount }} 条</p>
                                <p><strong>开始时间：</strong>{{ trainingStartTime }}</p>
                            </div>
                        </div>
                        <div class="no-training" v-else>
                            <i class="el-icon-info"></i>
                            <p>当前没有正在训练的模型</p>
                            <el-button 
                                type="primary" 
                                @click="handleBack"
                                size="small"
                            >
                                返回选择数据
                            </el-button>
                        </div>
                    </div>

                    <!-- 右侧：历史已训练模型 -->
                    <div class="history-models-section">
                        <div class="section-header">
                            <h3>
                                <i class="el-icon-collection"></i>
                                历史已训练模型
                            </h3>
                        </div>
                        <div class="models-grid">
                            <div 
                                v-for="model in historyModels" 
                                :key="model.id"
                                class="model-card"
                                @click="viewModelDetail(model)"
                            >
                                <div class="model-icon">
                                    <i :class="model.icon"></i>
                                </div>
                                <div class="model-info">
                                    <h4>{{ model.name }}</h4>
                                    <p class="model-date">{{ model.trainDate }}</p>
                                    <p class="model-status">
                                        <el-tag type="success" size="small">训练完成</el-tag>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 模型详情对话框 -->
        <el-dialog
            title="模型训练结果"
            :visible.sync="showModelDetail"
            width="85%"
            center
            :before-close="handleDialogClose"
        >
            <div class="model-detail-container" v-if="selectedModel">
                <div class="detail-header">
                    <h3>{{ selectedModel.name }} 训练结果</h3>
                    <p class="detail-date">训练时间：{{ selectedModel.trainDate }}</p>
                </div>
                
                <div class="detail-content">
                    <!-- 左侧：训练图片 -->
                    <div class="detail-image-section">
                        <h4>训练结果图片</h4>
                        <div class="image-container">
                            <img 
                                v-if="selectedModel.imageUrl" 
                                :src="selectedModel.imageUrl" 
                                alt="训练结果图片" 
                                class="result-image"
                                @error="handleImageError"
                            />
                            <div v-else class="image-loading">
                                <i class="el-icon-loading" style="font-size: 32px;"></i>
                                <p>正在加载图片...</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 右侧：训练指标 -->
                    <div class="detail-metrics-section">
                        <h4>训练指标</h4>
                        <div class="metrics-container">
                            <div class="metrics-header">
                                <i class="el-icon-data-analysis"></i>
                                <span>模型性能指标</span>
                            </div>
                            <div class="metrics-content">
                                <div class="metrics-row">
                                    <div class="metric-item">
                                        <span class="metric-label">最佳轮次 (Best Epoch):</span>
                                        <span class="metric-value">{{ selectedModel.metrics.best_epoch }}</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">最佳损失 (Best Loss):</span>
                                        <span class="metric-value">{{ selectedModel.metrics.best_loss.toFixed(9) }}</span>
                                    </div>
                                </div>
                                <div class="metrics-divider"></div>
                                <div class="metrics-section">
                                    <h4 class="section-title">训练集指标</h4>
                                    <div class="metrics-row">
                                        <div class="metric-item">
                                            <span class="metric-label">R² 分数:</span>
                                            <span class="metric-value">{{ selectedModel.metrics.train_r2.toFixed(6) }}</span>
                                        </div>
                                        <div class="metric-item">
                                            <span class="metric-label">平均绝对误差 (MAE):</span>
                                            <span class="metric-value">{{ selectedModel.metrics.train_mae.toFixed(6) }}</span>
                                        </div>
                                        <div class="metric-item">
                                            <span class="metric-label">均方根误差 (RMSE):</span>
                                            <span class="metric-value">{{ selectedModel.metrics.train_rmse.toFixed(6) }}</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="metrics-divider"></div>
                                <div class="metrics-section">
                                    <h4 class="section-title">测试集指标</h4>
                                    <div class="metrics-row">
                                        <div class="metric-item">
                                            <span class="metric-label">R² 分数:</span>
                                            <span class="metric-value">{{ selectedModel.metrics.test_r2.toFixed(6) }}</span>
                                        </div>
                                        <div class="metric-item">
                                            <span class="metric-label">平均绝对误差 (MAE):</span>
                                            <span class="metric-value">{{ selectedModel.metrics.test_mae.toFixed(6) }}</span>
                                        </div>
                                        <div class="metric-item">
                                            <span class="metric-label">均方根误差 (RMSE):</span>
                                            <span class="metric-value">{{ selectedModel.metrics.test_rmse.toFixed(6) }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button @click="showModelDetail = false">关闭</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
import Navbar from '../components/Navbar.vue'
import TemplateNavbar from '../components/TemplateNavbar.vue'

export default {
    name: 'ModelTraining',
    components: {
        Navbar,
        TemplateNavbar
    },
    data() {
        return {
            // 当前训练进度
            isTraining: false,
            trainingProgress: 0,
            trainingProgressText: '正在初始化...',
            trainingTimer: null,
            trainingDataCount: 0,
            trainingStartTime: '',
            // 历史已训练模型
            historyModels: [
                {
                    id: 1,
                    name: 'Transformer',
                    icon: 'el-icon-cpu',
                    trainDate: '2025-11-18 14:32:15',
                    imageUrl: '/模型训练图片.png',
                    metrics: {
                        best_epoch: 256,
                        best_loss: 0.000121340970890411,
                        train_r2: 0.8337273178478967,
                        train_mae: 0.06201135360633358,
                        train_rmse: 0.09560802050034772,
                        test_r2: 0.8900385499000549,
                        test_mae: 0.18664707243442535,
                        test_rmse: 0.2735595703125
                    }
                },
                {
                    id: 2,
                    name: 'MLP',
                    icon: 'el-icon-connection',
                    trainDate: '2025-11-17 16:45:28',
                    imageUrl: '/模型训练图片.png',
                    metrics: {
                        best_epoch: 200,
                        best_loss: 0.000152340970890411,
                        train_r2: 0.8237273178478967,
                        train_mae: 0.07201135360633358,
                        train_rmse: 0.10560802050034772,
                        test_r2: 0.8800385499000549,
                        test_mae: 0.19664707243442535,
                        test_rmse: 0.2835595703125
                    }
                }
            ],
            // 模型详情对话框
            showModelDetail: false,
            selectedModel: null
        }
    },
    mounted() {
        // 检查是否有正在训练的任务（可以从路由参数或localStorage获取）
        const trainingData = this.$route.query.trainingData
        if (trainingData) {
            this.startTraining(JSON.parse(trainingData))
        }
    },
    beforeDestroy() {
        // 清除定时器
        if (this.trainingTimer) {
            clearInterval(this.trainingTimer)
            this.trainingTimer = null
        }
    },
    methods: {
        // 开始训练
        startTraining(trainingData) {
            this.isTraining = true
            this.trainingProgress = 0
            this.trainingProgressText = '正在初始化...'
            this.trainingDataCount = trainingData ? trainingData.length : 0
            this.trainingStartTime = new Date().toLocaleString('zh-CN')
            
            // 总时长40秒
            const totalDuration = 40000
            const updateInterval = 500
            const progressStep = (updateInterval / totalDuration) * 100
            
            let currentProgress = 0
            
            // 清除之前的定时器
            if (this.trainingTimer) {
                clearInterval(this.trainingTimer)
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
            ]
            
            this.trainingTimer = setInterval(() => {
                currentProgress += progressStep
                
                if (currentProgress >= 100) {
                    currentProgress = 100
                    this.trainingProgress = 100
                    this.trainingProgressText = '训练完成！'
                    
                    // 清除定时器
                    clearInterval(this.trainingTimer)
                    this.trainingTimer = null
                    
                    // 延迟1秒后添加到历史模型列表
                    setTimeout(() => {
                        this.addToHistoryModels()
                        this.isTraining = false
                        this.$message.success('模型训练完成！')
                    }, 1000)
                } else {
                    this.trainingProgress = Math.min(Math.floor(currentProgress), 99)
                    
                    // 根据进度更新文本
                    for (let i = progressStages.length - 1; i >= 0; i--) {
                        if (this.trainingProgress >= progressStages[i].progress) {
                            this.trainingProgressText = progressStages[i].text
                            break
                        }
                    }
                }
            }, updateInterval)
        },
        
        // 添加到历史模型列表
        addToHistoryModels() {
            const newModel = {
                id: Date.now(),
                name: 'Mymodel',
                icon: 'el-icon-star-on',
                trainDate: new Date().toLocaleString('zh-CN'),
                imageUrl: '/模型训练图片.png',
                metrics: {
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
            this.historyModels.unshift(newModel) // 添加到列表开头
        },
        
        // 查看模型详情
        viewModelDetail(model) {
            this.selectedModel = model
            this.showModelDetail = true
        },
        
        // 处理图片加载错误
        handleImageError() {
            this.$message.error('图片加载失败，请检查文件路径')
        },
        
        // 处理对话框关闭
        handleDialogClose() {
            this.showModelDetail = false
            this.selectedModel = null
        },
        
        // 返回机器学习页面
        handleBack() {
            this.$router.push('/machine-learning').catch(() => {})
        },
        
        handleDropdownAction(action) {
            console.log('Dropdown action:', action)
        },
        handleNavAction(action) {
            console.log('Nav action:', action)
        },
        handleAuditAction(action) {
            console.log('Audit action:', action)
        }
    }
}
</script>

<style lang="scss" scoped>
.model-training-page {
    min-height: 100vh;
    background-color: #f5f5f5;
}

.main-content {
    padding: 20px;
    margin-top: 60px;
}

.content-container {
    max-width: 1600px;
    margin: 0 auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    padding: 30px;
}

.page-header {
    margin-bottom: 30px;
    
    .header-top {
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        
        .back-button {
            position: absolute;
            left: 0;
            padding: 10px 20px;
            font-size: 14px;
            border-radius: 6px;
            transition: all 0.3s ease;
            
            &:hover {
                transform: translateX(-3px);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            }
        }
        
        h2 {
            font-size: 28px;
            color: #303133;
            margin: 0;
        }
    }
}

.training-layout {
    display: flex;
    gap: 30px;
    min-height: 600px;
}

.current-training-section,
.history-models-section {
    flex: 1;
}

.section-header {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid #e8eaed;
    
    h3 {
        font-size: 20px;
        color: #303133;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
        
        i {
            color: #409eff;
        }
    }
}

.training-progress-box {
    background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
    border: 1px solid #e8eaed;
    border-radius: 8px;
    padding: 30px;
    text-align: center;
    
    .progress-bar {
        margin-bottom: 20px;
    }
    
    .progress-text {
        font-size: 16px;
        color: #606266;
        margin-bottom: 20px;
        font-weight: 500;
    }
    
    .training-info {
        text-align: left;
        background: #f0f9ff;
        padding: 15px;
        border-radius: 6px;
        border-left: 4px solid #409eff;
        
        p {
            margin: 8px 0;
            font-size: 14px;
            color: #606266;
            
            strong {
                color: #303133;
            }
        }
    }
}

.no-training {
    background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
    border: 1px solid #e8eaed;
    border-radius: 8px;
    padding: 60px 30px;
    text-align: center;
    
    i {
        font-size: 64px;
        color: #c0c4cc;
        margin-bottom: 20px;
        display: block;
    }
    
    p {
        font-size: 16px;
        color: #909399;
        margin-bottom: 20px;
    }
}

.models-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
}

.model-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border: 1px solid #e8eaed;
    border-radius: 8px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    
    &:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        border-color: #409eff;
    }
    
    .model-icon {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
        
        i {
            font-size: 28px;
            color: white;
        }
    }
    
    .model-info {
        width: 100%;
        
        h4 {
            font-size: 18px;
            color: #303133;
            margin: 0 0 10px 0;
        }
        
        .model-date {
            font-size: 12px;
            color: #909399;
            margin: 5px 0;
        }
        
        .model-status {
            margin: 10px 0 0 0;
        }
    }
}

.model-detail-container {
    .detail-header {
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid #e8eaed;
        
        h3 {
            font-size: 22px;
            color: #303133;
            margin: 0 0 10px 0;
        }
        
        .detail-date {
            font-size: 14px;
            color: #909399;
            margin: 0;
        }
    }
    
    .detail-content {
        display: flex;
        gap: 30px;
        min-height: 500px;
    }
    
    .detail-image-section,
    .detail-metrics-section {
        flex: 1;
    }
    
    .detail-image-section {
        h4 {
            font-size: 16px;
            color: #303133;
            margin-bottom: 15px;
        }
        
        .image-container {
            border: 1px solid #e8eaed;
            border-radius: 8px;
            padding: 15px;
            background: #fafafa;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 400px;
            
            .result-image {
                max-width: 100%;
                max-height: 500px;
                object-fit: contain;
                border-radius: 6px;
            }
            
            .image-loading {
                text-align: center;
                color: #909399;
                
                p {
                    margin-top: 10px;
                }
            }
        }
    }
    
    .detail-metrics-section {
        h4 {
            font-size: 16px;
            color: #303133;
            margin-bottom: 15px;
        }
        
        .metrics-container {
            background: #fafafa;
            border: 1px solid #e8eaed;
            border-radius: 8px;
            padding: 20px;
            
            .metrics-header {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 20px;
                font-size: 16px;
                font-weight: 600;
                color: #303133;
                
                i {
                    color: #409eff;
                }
            }
            
            .metrics-content {
                .metrics-row {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 20px;
                    margin-bottom: 15px;
                }
                
                .metric-item {
                    flex: 1;
                    min-width: 200px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px;
                    background: white;
                    border-radius: 6px;
                    border: 1px solid #e8eaed;
                    
                    .metric-label {
                        font-size: 14px;
                        color: #606266;
                    }
                    
                    .metric-value {
                        font-size: 14px;
                        font-weight: 600;
                        color: #409eff;
                    }
                }
                
                .metrics-divider {
                    height: 1px;
                    background: #e8eaed;
                    margin: 20px 0;
                }
                
                .metrics-section {
                    .section-title {
                        font-size: 15px;
                        color: #303133;
                        margin: 0 0 15px 0;
                        font-weight: 600;
                    }
                }
            }
        }
    }
}

// 响应式设计
@media (max-width: 1200px) {
    .training-layout {
        flex-direction: column;
    }
    
    .detail-content {
        flex-direction: column;
    }
}

@media (max-width: 768px) {
    .models-grid {
        grid-template-columns: 1fr;
    }
}
</style>
