<template>
    <div class="sinter-curve-recommend-page">
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
                        <h2>烧结曲线推荐</h2>
                    </div>
                    <p>请选择结构类型，查看对应的结构图片</p>
                </div>

                <div class="selection-area">
                    <!-- 左侧：下拉框选择 -->
                    <div class="left-panel">
                        <div class="select-wrapper">
                            <label class="select-label">选择结构类型：</label>
                            <el-select
                                v-model="selectedStructure"
                                placeholder="请选择结构类型"
                                class="structure-select"
                                @change="handleStructureChange"
                                @visible-change="handleSelectVisibleChange"
                                popper-class="structure-select-dropdown"
                            >
                                <el-option
                                    v-for="structure in structureOptions"
                                    :key="structure.value"
                                    :label="structure.label"
                                    :value="structure.value"
                                >
                                    <span 
                                        class="option-item"
                                        @mouseenter="handleOptionHover(structure)"
                                        @mouseleave="handleOptionLeave"
                                    >
                                        {{ structure.label }}
                                    </span>
                                </el-option>
                            </el-select>
                        </div>

                        <div class="select-wrapper" v-if="selectedStructure">
                            <label class="select-label">模型选择：</label>
                            <el-select
                                v-model="selectedModel"
                                placeholder="请选择模型"
                                class="model-select"
                                @change="handleModelChange"
                            >
                                <el-option
                                    v-for="model in modelOptions"
                                    :key="model.value"
                                    :label="model.label"
                                    :value="model.value"
                                >
                                </el-option>
                            </el-select>
                        </div>

                        <div class="selected-info" v-if="selectedStructure">
                            <p>当前选择：<strong>{{ getCurrentStructureLabel() }}</strong></p>
                        </div>
                        
                        <div class="selected-info" v-if="selectedModel" style="margin-top: 10px;">
                            <p>当前模型：<strong>{{ getCurrentModelLabel() }}</strong></p>
                        </div>

                        <div class="confirm-button-wrapper" style="margin-top: 20px;">
                            <el-button 
                                type="primary" 
                                size="medium"
                                @click="handleConfirm"
                                :disabled="!selectedStructure || !selectedModel"
                                class="confirm-button"
                            >
                                <i class="el-icon-check"></i>
                                确定
                            </el-button>
                        </div>
                    </div>

                    <!-- 右侧：图片/图表展示区域 -->
                    <div class="right-panel">
                        <div class="image-preview">
                            <!-- 显示烧结曲线图表 -->
                            <div v-if="showResult" class="chart-container">
                                <div ref="sinterCurveChart" class="chart-wrapper"></div>
                                <div class="image-label">
                                    烧结曲线推荐结果
                                </div>
                            </div>
                            <!-- 显示结构图片（悬停或选择时） -->
                            <div v-else-if="hoveredImage || selectedImage" class="image-container">
                                <img 
                                    :src="hoveredImage || selectedImage" 
                                    :alt="getCurrentStructureLabel()"
                                    class="structure-image"
                                />
                                <div class="image-label">
                                    {{ hoveredStructureLabel || getCurrentStructureLabel() }}
                                </div>
                            </div>
                            <div v-else class="placeholder">
                                <i class="el-icon-picture-outline"></i>
                                <p>请将鼠标悬停在下拉选项上或选择结构类型查看图片</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import Navbar from '../components/Navbar.vue'
import TemplateNavbar from '../components/TemplateNavbar.vue'
import * as echarts from 'echarts'

export default {
    name: 'SinterCurveRecommend',
    components: {
        Navbar,
        TemplateNavbar
    },
    data() {
        return {
            selectedStructure: '',
            selectedModel: 'Mymodel', // 默认选择Mymodel
            hoveredImage: '',
            hoveredStructureLabel: '',
            selectedImage: '',
            structureOptions: [
                { label: 'A方孔', value: 'A', image: '/方孔.png' },
                { label: 'B金刚石', value: 'B', image: '/金刚石.png' },
                { label: 'C镜像金刚石', value: 'C', image: '/镜像金刚石.png' },
                { label: 'D面心八面体', value: 'D', image: '/面心八面体.png' },
                { label: 'E面心顶角', value: 'E', image: '/面心顶角.png' },
                { label: 'F四维立方', value: 'F', image: '/四维立方.png' },
                { label: 'G体心顶角', value: 'G', image: '/体心顶角.png' }
            ],
            modelOptions: [
                { label: 'Mymodel', value: 'Mymodel' },
                { label: 'MLP', value: 'MLP' },
                { label: 'Transformer', value: 'Transformer' }
            ],
            showResult: false, // 是否显示结果
            chartInstance: null // ECharts实例
        }
    },
    beforeDestroy() {
        // 销毁图表实例
        if (this.chartInstance) {
            this.chartInstance.dispose()
            this.chartInstance = null
        }
    },
    methods: {
        handleStructureChange(value) {
            const structure = this.structureOptions.find(s => s.value === value)
            if (structure) {
                this.selectedImage = structure.image
                this.hoveredImage = '' // 清除悬停图片
                this.hoveredStructureLabel = ''
                this.showResult = false // 选择结构后隐藏结果图片
                // 选择结构后，重置模型选择为默认值
                this.selectedModel = 'Mymodel'
            }
        },
        handleOptionHover(structure) {
            this.hoveredImage = structure.image
            this.hoveredStructureLabel = structure.label
        },
        handleOptionLeave() {
            // 如果已经选择了结构，保留选中图片；否则清空
            if (!this.selectedStructure) {
                this.hoveredImage = ''
                this.hoveredStructureLabel = ''
            } else {
                // 如果已选择，悬停离开时恢复为选中图片
                const structure = this.structureOptions.find(s => s.value === this.selectedStructure)
                if (structure) {
                    this.hoveredImage = ''
                    this.hoveredStructureLabel = ''
                }
            }
        },
        handleSelectVisibleChange(visible) {
            // 当下拉框关闭时，如果已选择结构，恢复显示选中图片
            if (!visible && this.selectedStructure) {
                const structure = this.structureOptions.find(s => s.value === this.selectedStructure)
                if (structure) {
                    this.hoveredImage = ''
                    this.hoveredStructureLabel = ''
                }
            }
        },
        getCurrentStructureLabel() {
            const structure = this.structureOptions.find(s => s.value === this.selectedStructure)
            return structure ? structure.label : ''
        },
        handleModelChange(value) {
            console.log('选择的模型:', value)
            this.showResult = false // 选择模型后隐藏结果图片
        },
        getCurrentModelLabel() {
            const model = this.modelOptions.find(m => m.value === this.selectedModel)
            return model ? model.label : ''
        },
        handleConfirm() {
            // 点击确定后绘制烧结曲线图表
            if (this.selectedStructure && this.selectedModel) {
                this.showResult = true
                this.$nextTick(() => {
                    this.initSinterCurveChart()
                })
                this.$message.success('已生成烧结曲线推荐结果')
            } else {
                this.$message.warning('请先选择结构类型和模型')
            }
        },
        
        // 初始化烧结曲线图表
        initSinterCurveChart() {
            // 销毁之前的图表实例
            if (this.chartInstance) {
                this.chartInstance.dispose()
            }
            
            const chartDom = this.$refs.sinterCurveChart
            if (!chartDom) {
                return
            }
            
            this.chartInstance = echarts.init(chartDom)
            
            // 生成烧结曲线数据（温度-时间曲线）
            // 根据图片描述：X轴0-1800，Y轴0-1200
            // 关键点：(0,0), (300,250), (750,398), (1050,550), (1350,1100), (1500,1100), (1800,20)
            const timeData = []
            const temperatureData = []
            
            // 生成数据点，每10个单位一个点
            for (let t = 0; t <= 1800; t += 10) {
                timeData.push(t)
                let temp = 0
                
                if (t <= 300) {
                    // 第一阶段：0到300，从0到250°C
                    temp = (250 / 300) * t
                } else if (t <= 750) {
                    // 第二阶段：300到750，从250到398°C
                    const progress = (t - 300) / (750 - 300)
                    temp = 250 + (398 - 250) * progress
                } else if (t <= 1050) {
                    // 第三阶段：750到1050，从398到550°C
                    const progress = (t - 750) / (1050 - 750)
                    temp = 398 + (550 - 398) * progress
                } else if (t <= 1350) {
                    // 第四阶段：1050到1350，从550到1100°C（陡峭上升）
                    const progress = (t - 1050) / (1350 - 1050)
                    temp = 550 + (1100 - 550) * progress
                } else if (t <= 1500) {
                    // 保温阶段：1350到1500，保持在1100°C
                    temp = 1100
                } else {
                    // 冷却阶段：1500到1800，从1100°C快速下降到20°C
                    const progress = (t - 1500) / (1800 - 1500)
                    temp = 1100 - (1100 - 20) * progress
                }
                
                temperatureData.push(temp)
            }
            
            const option = {
                title: {
                    text: '烧结曲线推荐',
                    left: 'center',
                    textStyle: {
                        fontSize: 18,
                        fontWeight: 'bold'
                    }
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross'
                    },
                    formatter: function(params) {
                        let result = `时间: ${params[0].axisValue} 分钟<br/>`
                        params.forEach(param => {
                            // 处理 value 可能是数组的情况 [x, y]
                            let value = param.value
                            if (Array.isArray(value)) {
                                // 如果是数组，取第二个元素（y值）
                                value = value[1]
                            }
                            // 确保 value 是数字
                            const numValue = typeof value === 'number' ? value : parseFloat(value) || 0
                            result += `${param.seriesName}: ${numValue.toFixed(2)}${param.seriesName === '温度' ? '℃' : ''}<br/>`
                        })
                        return result
                    }
                },
                legend: {
                    data: ['温度'],
                    top: 35
                },
                grid: {
                    left: '10%',
                    right: '10%',
                    bottom: '15%',
                    top: '20%',
                    containLabel: true
                },
                xAxis: {
                    type: 'value',
                    name: '时间',
                    nameLocation: 'middle',
                    nameGap: 30,
                    min: 0,
                    max: 1800,
                    axisLabel: {
                        formatter: '{value}'
                    },
                    splitLine: {
                        show: true,
                        lineStyle: {
                            type: 'dashed'
                        }
                    }
                },
                yAxis: {
                    type: 'value',
                    name: '温度 (℃)',
                    min: 0,
                    max: 1200,
                    axisLabel: {
                        formatter: '{value}'
                    },
                    splitLine: {
                        show: true,
                        lineStyle: {
                            type: 'dashed'
                        }
                    }
                },
                series: [
                    {
                        name: '温度',
                        type: 'line',
                        smooth: true,
                        data: timeData.map((time, index) => [time, temperatureData[index]]),
                        lineStyle: {
                            color: '#409eff',
                            width: 3
                        },
                        itemStyle: {
                            color: '#409eff'
                        },
                        areaStyle: {
                            color: {
                                type: 'linear',
                                x: 0,
                                y: 0,
                                x2: 0,
                                y2: 1,
                                colorStops: [
                                    { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
                                    { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
                                ]
                            }
                        },
                        markPoint: {
                            data: [
                                { coord: [300, 250], name: '250℃' },
                                { coord: [750, 398], name: '398℃' },
                                { coord: [1050, 550], name: '550℃' },
                                { coord: [1350, 1100], name: '1100℃' },
                                { coord: [1500, 1100], name: '1100℃' }
                            ],
                            label: {
                                formatter: '{b}',
                                position: 'top'
                            }
                        }
                    }
                ]
            }
            
            this.chartInstance.setOption(option)
            
            // 响应式调整
            window.addEventListener('resize', () => {
                if (this.chartInstance) {
                    this.chartInstance.resize()
                }
            })
        },
        handleDropdownAction(action) {
            // 处理导航栏下拉操作
            console.log('Dropdown action:', action)
        },
        handleNavAction(action) {
            // 处理导航操作
            console.log('Nav action:', action)
        },
        handleAuditAction(action) {
            // 处理审核操作
            console.log('Audit action:', action)
        },
        handleBack() {
            // 返回机器学习页面
            this.$router.push('/machine-learning').catch(() => {})
        }
    }
}
</script>

<style lang="scss" scoped>
.sinter-curve-recommend-page {
    min-height: 100vh;
    background-color: #f5f5f5;
}

.main-content {
    padding: 20px;
    margin-top: 60px; // 为导航栏留出空间
}

.content-container {
    max-width: 1400px;
    margin: 0 auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    padding: 30px;
}

.page-header {
    margin-bottom: 30px;
    text-align: center;
    
    .header-top {
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        margin-bottom: 10px;
        
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
    }
    
    h2 {
        font-size: 28px;
        color: #303133;
        margin: 0;
    }
    
    p {
        font-size: 14px;
        color: #909399;
        margin-top: 10px;
    }
}

.selection-area {
    display: flex;
    gap: 40px;
    align-items: flex-start;
    min-height: 500px;
}

.left-panel {
    flex: 0 0 350px;
    
    .select-wrapper {
        margin-bottom: 20px;
        
        .select-label {
            display: block;
            font-size: 16px;
            color: #606266;
            margin-bottom: 12px;
            font-weight: 500;
        }
        
        .structure-select,
        .model-select {
            width: 100%;
            
            ::v-deep .el-input__inner {
                height: 45px;
                font-size: 15px;
            }
        }
    }
    
    .selected-info {
        padding: 15px;
        background-color: #f0f9ff;
        border-radius: 6px;
        border-left: 4px solid #409eff;
        
        p {
            margin: 0;
            font-size: 14px;
            color: #606266;
            
            strong {
                color: #409eff;
                font-size: 16px;
            }
        }
    }
    
    .confirm-button-wrapper {
        text-align: center;
        
        .confirm-button {
            width: 100%;
            height: 45px;
            font-size: 16px;
            font-weight: 500;
            border-radius: 6px;
            transition: all 0.3s ease;
            
            &:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
            }
            
            &:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
        }
    }
}

.right-panel {
    flex: 1;
    min-height: 500px;
    
    .image-preview {
        width: 100%;
        height: 100%;
        min-height: 500px;
        border: 2px dashed #dcdfe6;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #fafafa;
        transition: all 0.3s ease;
        
        .image-container {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
            
            .structure-image {
                max-width: 100%;
                max-height: 450px;
                object-fit: contain;
                border-radius: 6px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                transition: transform 0.3s ease;
                
                &:hover {
                    transform: scale(1.02);
                }
            }
            
            .image-label {
                margin-top: 15px;
                font-size: 18px;
                font-weight: 600;
                color: #303133;
            }
        }
        
        .chart-container {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
            
            .chart-wrapper {
                width: 100%;
                height: 450px;
                min-height: 450px;
            }
            
            .image-label {
                margin-top: 15px;
                font-size: 18px;
                font-weight: 600;
                color: #303133;
            }
        }
        
        .placeholder {
            text-align: center;
            color: #909399;
            
            i {
                font-size: 64px;
                margin-bottom: 15px;
                display: block;
                color: #c0c4cc;
            }
            
            p {
                font-size: 14px;
                margin: 0;
            }
        }
    }
}

// 下拉选项样式
::v-deep .structure-select-dropdown {
    .el-select-dropdown__item {
        padding: 0;
        
        .option-item {
            display: block;
            padding: 0 20px;
            line-height: 34px;
            cursor: pointer;
            transition: background-color 0.3s;
            
            &:hover {
                background-color: #f5f7fa;
            }
        }
    }
}

// 响应式设计
@media (max-width: 1024px) {
    .selection-area {
        flex-direction: column;
    }
    
    .left-panel {
        flex: 1;
        width: 100%;
    }
    
    .right-panel {
        width: 100%;
    }
}
</style>
