<template>
    <div>
        <Navbar @dropdown-action="handleDropdownAction" />

        <div class="paper-data-box">
            <!-- 展示搜索的数据 -->
            <el-table :data="usedTableData" @row-click="showPaper" border style="width: 100%;" height="750" size="large">

                <el-table-column v-for="col in cols" :prop="col" label="文献名称" :key="col" >
                </el-table-column>

            </el-table>
            <!--分页工具条-->
            <el-pagination @current-change="handleCurrentChange" :current-page="currentPage" :page-size="15"
                layout="total, prev, pager, next, jumper" :total="cnt">
            </el-pagination>
        </div>


    </div>
</template>


<script>
import Navbar from '../components/Navbar.vue';
import axios from 'axios';
export default {
    name: "PaperP",
    components: {
        Navbar
    },
    data() {
        return {
            userName: '用户名',
            circleUrl: "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png",

            isIndeterminate: true,
            cols: ["file_name"],
            // 当前页的表格数据
            usedTableData: [{
                SampleSerial: 'SampleSerial',
                SampleName: 'SampleName',
                SurfaceTreatmentMethods: 'SurfaceTreatmentMethods',
                SurfaceTension: 'SurfaceTension',
                SurfaceMorphologyPhoto: 'SurfaceMorphologyPhoto',
                SurfaceMorphology: 'SurfaceMorphology',
            }, {
                SampleSerial: 'SampleSerial',
                SampleName: 'SampleName',
                SurfaceTreatmentMethods: 'SurfaceTreatmentMethods',
                SurfaceTension: 'SurfaceTension',
                SurfaceMorphologyPhoto: 'SurfaceMorphologyPhoto',
                SurfaceMorphology: 'SurfaceMorphology',
            }],
            // 当前页码
            currentPage: 1,
            // 所有满足检索条件的数据 和 个数
            allData: [],
            cnt: 800,
        }
    },
    mounted() {
        var _this = this;
        axios({
            method: "get",
            url: "http://192.168.26.251:8085/files_information/",
            //url: "http://100.67.42.59:8085/files_information/"
        }).then(function (resp) {
            _this.allData = resp.data[1];
            console.log(_this.allData.slice(0, 10));
            // 根据 allData 计算得到 cnt(总数据条数) 和 cols(列名)
            // _this.cols = Object.keys(_this.allData[0]);
            console.log(_this.cols);
            _this.cnt = _this.allData.length;
            // 将tabelData设置为allData的前10个数据(不足10个全部显示)
            _this.usedTableData = _this.allData.slice(0, 15);
        }).catch((error) => {
            console.error('请求失败:', error)
        })
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
        handleNavClick(link) {
            this.$emit('nav-action', link.action);
        },

        //分页
        handleCurrentChange(val) {
            console.log(`当前页: ${val}`);
            this.currentPage = val;
            // 根据当前页重新确定新的 tabelData
            this.usedTableData = this.allData.slice(15 * (val - 1), 15 * val);
        },
        
        //点击查看某一篇文献
        showPaper(row) {
            console.log("row");
            console.log(row.file_path);
            var safePath = encodeURI(row.file_path);
            const url = `http://192.168.26.251:8085${safePath}`;
            console.log(url);
            // 使用 window.location 跳转（当前窗口打开）
            window.location.href = url;
        }
    },
}    
</script>

<style scoped>
::v-deep .el-input__inner.custom-height {
    height: 50px;
    /* 设置高度为 50px */
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Roboto', sans-serif;
}


/* 检索数据展示 */
.paper-data-box {
    padding: 50px;
    background-color: white;
    width: 70%;
    height: auto;
    margin-left: 15%;
}

</style>