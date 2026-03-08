<template>
  <div class="display-echart-page">
    <Navbar @dropdown-action="handleDropdownAction" />
    <!-- 页面其他内容 -->
    <!-- 用于渲染 ECharts 图表的容器 -->
    <div class="EchartContainer">
      <div ref="chartContainer1" style="width: 600px; height: 400px;"></div>
      <div ref="chartContainer2" style="width: 550px; height: 400px;"></div>
      <div ref="chartContainer3" style="width: 550px; height: 500px;"></div>
    </div>
    <div class="table-container">
      <!-- 表格 -->
      <el-table v-if="tableData.length > 0 && tableColumns.length > 0"
          :data="tableData" style="margin-top: 20px" max-height="300">
          <!-- 动态生成列 -->
          <el-table-column v-for="column in tableColumns" :key="column.prop" :prop="column.prop"
              :label="column.label" :width="column.width">
          </el-table-column>
      </el-table>

      <div v-else-if="loading" class="loading-text">数据加载中...</div>
      <div v-else class="empty-text">暂无数据</div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import Navbar from '../components/Navbar.vue';

export default {
  name: 'DisplayEchart',
  components: {
    Navbar
  },
  data(){
    return{
      tableData: [],
      tableColumns:[]
    }
  },
  mounted() {
    // 在组件挂载后初始化 ECharts 图表
    this.initChart1();
    this.initChart2();
    this.initChart3();
    this.fetchTableData();
  },
  methods: {
    handleDropdownAction(action) {
      console.log('下拉菜单点击:', action);
      // 根据action执行不同操作
      switch (action) {
        case 'profile':
          // 跳转个人中心
          this.$router.push('/person');
          break;
        case 'logout':
          // 执行退出登录
          this.$router.push('/login');
          break;
      }
    },
    fetchTableData() {
      this.loading = true;
      this.tableData = [
      ];
      this.tableColumns = [
        {
          prop:"materialName",
          label:"材料名称"
        },
        {
          prop:"value",
          label:"材料值"
        }
      ];

      try {
          this.$request.get(
              'http://192.168.25.10:31344/webhook/e1730fbf-9939-47ff-968e-4e91e0cc7e7f'
          ).then(res => {
            console.log(res.data);
            this.tableData = Object.entries(res.data).map(([key, value]) => ({
              materialName: key,
              value: value
            }));
          })}catch (error) {
              console.error('获取数据失败:', error);
              this.$message.error('网络错误，请检查后端连接');
          } finally {
              this.loading = false;
          }
      },
    initChart1() {
      // 获取图表容器的引用
      const chartDom = this.$refs.chartContainer1;
      // 初始化 ECharts 实例
      const myChart = echarts.init(chartDom);
      // 配置图表选项
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
          axisTick: {
            show: true // 不显示坐标轴刻度线
          },
          axisLine: {
            show: true, // 不显示坐标轴线
          },
          axisLabel: {
            show: true, // 不显示坐标轴上的文字
          },
          splitLine: {
            show: true // 不显示网格线
          },
        },
        yAxis: {
          type: 'category',
          data: ['β-TCP占比', '明胶', 'hMSCs', 'HA占比', '胶原', 'BMP-2', '壳聚糖','聚左乳酸PLLA','磷酸钙','DBM'],
          axisTick: {
            show: false // 不显示坐标轴刻度线
          },
          axisLine: {
            show: true, // 不显示坐标轴线
          },
          axisLabel: {
            show: false, // 不显示坐标轴上的文字
          },
          splitLine: {
            show: false // 不显示网格线
          },
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
                color: "#000000",
                fontSize: 13,
                fontStyle: 'italic', // 标签字体斜体
              },
              offset: [10, 0]
            },
            itemStyle: {
              normal: {
                color: function (params) {
                  // 定义一个颜色数组
                  let colorList = [
                    //前四个参数用于配置渐变色的起止位置，这四个参数依次对应 右下左上 四个方位。也就是从右边开始顺时针方向。
                    //通过修改前4个参数，可以实现不同的渐变方向
                    /*第五个参数则是一个数组，用于配置颜色的渐变过程。
                      每项为一个对象，包含offset和color两个参数
                    */
                    new echarts.graphic.LinearGradient(
                      0, 0, 1, 0,
                      [
                        { offset: 0, color: '#008B8B' },                   //柱图渐变色//offset范围是0~1，用于表示位置，0是指0%处的颜色
                        { offset: 1, color: '#ADD8E6' },                   //柱图渐变色
                      ]
                    ),
                    new echarts.graphic.LinearGradient(
                      0, 0, 1, 0,
                      [
                        { offset: 0, color: '#63B8FF' },                   //柱图渐变色
                        { offset: 1, color: '#ADD8E6' },                   //柱图渐变色
                      ]
                    ),
                    new echarts.graphic.LinearGradient(
                      0, 0, 1, 0,
                      [
                        { offset: 0, color: '#87CEEB' },                   //柱图渐变色
                        { offset: 1, color: '#ADD8E6' },                   //柱图渐变色
                      ]
                    ),
                    new echarts.graphic.LinearGradient(
                      0, 0, 1, 0,
                      [
                        { offset: 0, color: '#2E8B57' },                   //柱图渐变色
                        { offset: 1, color: '#ADD8E6' },                   //柱图渐变色
                      ]
                    ),
                    new echarts.graphic.LinearGradient(
                      0, 0, 1, 0,
                      [
                        { offset: 0, color: '#1874CD' },                   //柱图渐变色
                        { offset: 1, color: '#ADD8E6' },                   //柱图渐变色
                      ]
                    ),
                  ];
                  // 根据数据项索引返回颜色
                  return colorList[params.dataIndex % colorList.length];
                },
                borderRadius: [0, 999, 999, 0],//（顺时针左上，右上，右下，左下）
              }
            }
          }

        ]
      };
      // 使用刚指定的配置项和数据显示图表
      if (option && typeof option === 'object') {
        myChart.setOption(option);
      }
      // 监听窗口大小变化，重新调整图表大小
      window.addEventListener('resize', () => {
        myChart.resize();
      });
    },
    initChart2() {
      // 获取图表容器的引用
      const chartDom = this.$refs.chartContainer2;
      // 初始化 ECharts 实例
      const myChart = echarts.init(chartDom);
      // 配置图表选项
      const option = {
        legend: {
          top: 'bottom'
        },
        toolbox: {
          show: true,
          feature: {
            // mark: { show: true },
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
              { value: 24, name: '磷酸钙' }, 
            ]
          }
        ]
      };
      // 使用刚指定的配置项和数据显示图表
      if (option && typeof option === 'object') {
        myChart.setOption(option);
      }
      // 监听窗口大小变化，重新调整图表大小
      window.addEventListener('resize', () => {
        myChart.resize();
      });
    },
    initChart3() {
      // 获取图表容器的引用
      const chartDom = this.$refs.chartContainer3;
      // 初始化 ECharts 实例
      const myChart = echarts.init(chartDom);
      // 配置图表选项
      const option = {
        xAxis: {
        type: 'category',
        boundaryGap: false,
        axisTick: {
            show: true // 不显示坐标轴刻度线
          },
        axisLine: {
            show: true, // 不显示坐标轴线
          },
        axisLabel: {
            show: true, // 不显示坐标轴上的文字
            interval:0 // 0 表示显示所有标签，不间隔隐藏
          },
        splitLine: {
            show: true // 不显示网格线
          },
        data: ['β-TCP占比', '明胶', 'hMSCs', 'HA占比', '胶原', 'BMP-2', '壳聚糖','聚左乳酸PLLA','磷酸钙','DBM']
      },
      yAxis: {
        type: 'value',
        axisTick: {
            show: true // 不显示坐标轴刻度线
          },
          axisLine: {
            show: true, // 不显示坐标轴线
          },
          axisLabel: {
            show: true, // 不显示坐标轴上的文字
          },
          splitLine: {
            show: true // 不显示网格线
          },
      },
      series: [
        {
          data: [234, 6, 31, 327, 51, 43, 6, 42, 24, 25],
          type: 'line',
          areaStyle: {}
        }
      ]
      };
      // 使用刚指定的配置项和数据显示图表
      if (option && typeof option === 'object') {
        myChart.setOption(option);
      }
      // 监听窗口大小变化，重新调整图表大小
      window.addEventListener('resize', () => {
        myChart.resize();
      });
    }
  }
};
</script>

<style scoped>
/* 数据统计页面容器 */
.display-echart-page {
    padding-top: 80px;
}

/* 可以添加自定义样式 */
.EchartContainer {
  display: flex;
  gap: 20px; /* 设置元素之间的间距 */
  justify-content: center; /* 水平居中对齐 */
  align-items: center; /* 垂直居中对齐 */
  flex-wrap: wrap; /* 当空间不足时自动换行 */
}

.EchartContainer > div {
  min-width: 300px; /* 设置最小宽度，防止元素被压缩得太小 */
}
</style>