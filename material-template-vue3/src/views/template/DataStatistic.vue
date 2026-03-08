<template>
  <div class="data-statistic-page">
    <Navbar />
    
    <div class="page-container">
      <div class="page-header">
        <h1>数据统计</h1>
        <p>查看各类数据的统计信息</p>
      </div>

      <div class="statistic-cards">
        <el-card 
          v-for="(stat, index) in statistics" 
          :key="index"
          class="stat-card"
          shadow="hover"
        >
          <div class="stat-content">
            <div class="stat-icon" :style="{ background: stat.color }">
              <el-icon :size="32"><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">{{ stat.label }}</div>
              <div class="stat-value">{{ stat.value }}</div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 图表容器 -->
      <div class="EchartContainer">
        <div ref="chartContainer1" class="chart-item"></div>
        <div ref="chartContainer2" class="chart-item"></div>
        <div ref="chartContainer3" class="chart-item"></div>
      </div>

      <!-- 数据表格 -->
      <div class="table-container">
        <el-table 
          v-if="tableData.length > 0 && tableColumns.length > 0"
          :data="tableData" 
          style="margin-top: 20px" 
          max-height="300"
          border
        >
          <el-table-column 
            v-for="column in tableColumns" 
            :key="column.prop" 
            :prop="column.prop"
            :label="column.label" 
            :width="column.width"
          />
        </el-table>
        <div v-else-if="loading" class="loading-text">数据加载中...</div>
        <div v-else class="empty-text">暂无数据</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'
import { DataAnalysis, Document, Collection, Files } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const statistics = ref([])

const chartContainer1 = ref(null)
const chartContainer2 = ref(null)
const chartContainer3 = ref(null)
let chartInstance1 = null
let chartInstance2 = null
let chartInstance3 = null

const tableData = ref([])
const tableColumns = ref([])
const loading = ref(false)

const loadStatistics = async () => {
  try {
    const response = await request.get('/data/statistic/all')
    if (response.data?.code === 0 && response.data?.data) {
      const data = response.data.data
      // 更新已审核数据和待审核数据
      if (statistics.value[0]) {
        statistics.value[0].value = data.approvedData || 0
      }
      if (statistics.value[1]) {
        statistics.value[1].value = data.pendingData || 0
      }
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const fetchTableData = async () => {
  loading.value = true
  tableData.value = []
  tableColumns.value = [
    { prop: 'materialName', label: '材料名称', width: 200 },
    { prop: 'value', label: '材料值', width: 150 }
  ]

  try {
    // 使用假数据，因为原API可能不可用
    // 如果需要真实数据，可以取消注释下面的代码
    // const response = await request.get('http://192.168.25.10:31344/webhook/e1730fbf-9939-47ff-968e-4e91e0cc7e7f')
    // if (response.data) {
    //   tableData.value = Object.entries(response.data).map(([key, value]) => ({
    //     materialName: key,
    //     value: value
    //   }))
    // }
    
    // 使用假数据
    tableData.value = [
      { materialName: 'β-TCP占比', value: 234 },
      { materialName: '明胶', value: 6 },
      { materialName: 'hMSCs', value: 31 },
      { materialName: 'HA占比', value: 327 },
      { materialName: '胶原', value: 51 },
      { materialName: 'BMP-2', value: 43 },
      { materialName: '壳聚糖', value: 6 },
      { materialName: '聚左乳酸PLLA', value: 42 },
      { materialName: '磷酸钙', value: 24 },
      { materialName: 'DBM', value: 25 }
    ]
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('网络错误，请检查后端连接')
  } finally {
    loading.value = false
  }
}

const initChart1 = () => {
  if (!chartContainer1.value) return
  
  chartInstance1 = echarts.init(chartContainer1.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {},
    grid: {
      left: '3%',
      right: '4%',
      top: '1%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01],
      axisTick: { show: true },
      axisLine: { show: true },
      axisLabel: { show: true },
      splitLine: { show: true }
    },
    yAxis: {
      type: 'category',
      data: ['β-TCP占比', '明胶', 'hMSCs', 'HA占比', '胶原', 'BMP-2', '壳聚糖', '聚左乳酸PLLA', '磷酸钙', 'DBM'],
      axisTick: { show: false },
      axisLine: { show: true },
      axisLabel: { show: false },
      splitLine: { show: false }
    },
    series: [
      {
        type: 'bar',
        data: [234, 6, 31, 327, 51, 43, 6, 42, 24, 25],
        showBackground: true,
        label: {
          show: true,
          formatter: '{b}',
          position: 'left',
          align: 'left',
          textStyle: {
            color: '#000000',
            fontSize: 13,
            fontStyle: 'italic'
          },
          offset: [10, 0]
        },
        itemStyle: {
          color: function (params) {
            const colorList = [
              new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#008B8B' },
                { offset: 1, color: '#ADD8E6' }
              ]),
              new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#63B8FF' },
                { offset: 1, color: '#ADD8E6' }
              ]),
              new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#87CEEB' },
                { offset: 1, color: '#ADD8E6' }
              ]),
              new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#2E8B57' },
                { offset: 1, color: '#ADD8E6' }
              ]),
              new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#1874CD' },
                { offset: 1, color: '#ADD8E6' }
              ])
            ]
            return colorList[params.dataIndex % colorList.length]
          },
          borderRadius: [0, 999, 999, 0]
        }
      }
    ]
  }
  
  chartInstance1.setOption(option)
  
  window.addEventListener('resize', () => {
    if (chartInstance1) {
      chartInstance1.resize()
    }
  })
}

const initChart2 = () => {
  if (!chartContainer2.value) return
  
  chartInstance2 = echarts.init(chartContainer2.value)
  
  const option = {
    legend: {
      top: 'bottom'
    },
    toolbox: {
      show: true,
      feature: {
        dataView: { show: true, readOnly: false },
        restore: { show: true },
        saveAsImage: { show: true }
      }
    },
    series: [
      {
        name: 'Nightingale',
        type: 'pie',
        radius: [50, 250],
        center: ['50%', '50%'],
        roseType: 'area',
        itemStyle: {
          borderRadius: 8
        },
        data: [
          { value: 51, name: '胶原' },
          { value: 43, name: 'BMP-2' },
          { value: 43, name: 'α-TCP' },
          { value: 42, name: '聚左乳酸PLLA' },
          { value: 31, name: 'hMSCs' },
          { value: 25, name: 'DBM' },
          { value: 24, name: '磷酸钙' }
        ]
      }
    ]
  }
  
  chartInstance2.setOption(option)
  
  window.addEventListener('resize', () => {
    if (chartInstance2) {
      chartInstance2.resize()
    }
  })
}

const initChart3 = () => {
  if (!chartContainer3.value) return
  
  chartInstance3 = echarts.init(chartContainer3.value)
  
  const option = {
    xAxis: {
      type: 'category',
      boundaryGap: false,
      axisTick: { show: true },
      axisLine: { show: true },
      axisLabel: { show: true, interval: 0 },
      splitLine: { show: true },
      data: ['β-TCP占比', '明胶', 'hMSCs', 'HA占比', '胶原', 'BMP-2', '壳聚糖', '聚左乳酸PLLA', '磷酸钙', 'DBM']
    },
    yAxis: {
      type: 'value',
      axisTick: { show: true },
      axisLine: { show: true },
      axisLabel: { show: true },
      splitLine: { show: true }
    },
    series: [
      {
        data: [234, 6, 31, 327, 51, 43, 6, 42, 24, 25],
        type: 'line',
        areaStyle: {}
      }
    ]
  }
  
  chartInstance3.setOption(option)
  
  window.addEventListener('resize', () => {
    if (chartInstance3) {
      chartInstance3.resize()
    }
  })
}

onMounted(() => {
  loadStatistics()
  fetchTableData()
  setTimeout(() => {
    initChart1()
    initChart2()
    initChart3()
  }, 100)
})

onBeforeUnmount(() => {
  if (chartInstance1) {
    chartInstance1.dispose()
    chartInstance1 = null
  }
  if (chartInstance2) {
    chartInstance2.dispose()
    chartInstance2 = null
  }
  if (chartInstance3) {
    chartInstance3.dispose()
    chartInstance3 = null
  }
})
</script>

<style lang="scss" scoped>
.data-statistic-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-top: 60px;
}

.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  
  h1 {
    font-size: 32px;
    color: #303133;
    margin-bottom: 10px;
  }
  
  p {
    font-size: 16px;
    color: #909399;
  }
}

.statistic-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
  
  .stat-card {
    .stat-content {
      display: flex;
      align-items: center;
      gap: 20px;
      
      .stat-icon {
        width: 64px;
        height: 64px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
      }
      
      .stat-info {
        flex: 1;
        
        .stat-label {
          font-size: 14px;
          color: #909399;
          margin-bottom: 8px;
        }
        
        .stat-value {
          font-size: 28px;
          font-weight: bold;
          color: #303133;
        }
      }
    }
  }
}

.EchartContainer {
  display: flex;
  gap: 20px;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 30px;
  
  .chart-item {
    width: 600px;
    height: 400px;
    min-width: 300px;
    
    &:nth-child(3) {
      width: 550px;
      height: 500px;
    }
  }
}

.table-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  .loading-text,
  .empty-text {
    text-align: center;
    padding: 40px;
    color: #909399;
    font-size: 14px;
  }
}
</style>


