<template>
    <div class="home-page">
        <Navbar @dropdown-action="handleDropdownAction" />
        <!-- 页面其他内容 -->
        <div class="statistics-container">
            <h1 class="platform-title">生物医用材料数据管理服务平台</h1>

            <div class="stats-grid">
                <!-- 第一行 -->
                <div class="stat-item" @click="goToPaper">
                    <div class="stat-label">文献</div>
                    <div class="stat-value">{{ paper }}项</div>
                    <!-- <div class="stat-value">{{ 3057 }}篇</div> -->
                </div>
                <div class="stat-item">
                    <div class="stat-label">生产</div>
                    <!-- <div class="stat-value">{{ product }}项</div> -->
                    <div class="stat-value">{{ 0 }}项</div>
                </div>

                <!-- 第二行 -->
                <div class="stat-item">
                    <div class="stat-label">计算</div>
                    <!-- <div class="stat-value">{{ compute }}项</div> -->
                    <div class="stat-value">{{ 0 }}项</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">实验</div>
                    <!-- <div class="stat-value">{{ experment }}项</div> -->
                    <div class="stat-value">{{ 1381 }}项</div>
                </div>

                <!-- 第三行 -->
                <div class="stat-item">
                    <div class="stat-label">材料制备</div>
                    <!-- <div class="stat-value">{{ cnt1 }}</div> -->
                    <div class="stat-value">{{ 1962}}项</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">理化性质</div>
                    <!-- <div class="stat-value">{{ cnt2 }}</div> -->
                    <div class="stat-value">{{ 3446 }}项</div>
                </div>
                 
            </div>
        </div>

        <div class="mulit-options">
            <div class="option-item" @click="goToDataStatistics">
                <div class="option-img"><i class="el-icon-collection"></i></div>
                <div class="option-label">数据统计</div>
            </div>
            <div class="option-item" @click="goToDataSearch">
                <div class="option-img"><i class="el-icon-search"></i></div>
                <div class="option-label">数据检索</div>
            </div>
            <div class="option-item" @click="goToChat">
                <div class="option-img"><i class="el-icon-chat-round"></i></div>
                <div class="option-label">智能对话</div>
            </div>
            <div class="option-item" @click="goToDisplayexp">
                <div class="option-img"><i class="el-icon-magic-stick"></i></div>
                <div class="option-label">机器学习</div>
            </div>
            <div class="option-item" @click="goToTemplate">
                <div class="option-img"><i class="el-icon-files"></i></div>
                <div class="option-label">模版库</div>
            </div>
        </div>


    </div>
</template>


<script>
import Navbar from '../components/Navbar.vue';
// import axios from 'axios'; // 暂时注释掉，因为外部API不可用

export default {
    name: "HomeS",
    components: {
        Navbar
    },
    data() {
        return {
            // cnt1: 1962,
            // cnt2: 3446,
            // cnt3: 0,
            // cnt4: 0,
            // paper: 135,
            // product: 0,
            // compute: 0,
            // experment: 1381,
            cnt1: 0,
            cnt2: 0,
            cnt3: 0,
            cnt4: 0,
            paper: 0,
            product: 0,
            compute: 0,
            experment: 0,
        }
    },
    mounted() {
        this.fetchData();
    },
    methods: {
        fetchData() {
            //当页面加载完成后，发送异步请求，获取数据
            // 暂时注释掉无法访问的外部API调用
            // var _this = this;
            // axios({
            //    method: "get",
            //    url: "http://192.168.26.251:8085/files_information/"
            //     //url: "http://100.67.42.59:8085/files_information/"
            // }).then(function (resp) {
            //    _this.paper = resp.data[0];
            // }).catch((error) => {
            //    console.error('请求失败:', error)
            // })
            console.log('Home.vue 数据加载已跳过外部API调用')
            // axios({
            //    method: "get",
            //    url: "http://192.168.27.13:18080/basemodule/count/2"
            // }).then(function (resp) {
            //    _this.compute = resp.data.data;
            // }).catch((error) => {
            //    console.error('请求失败:', error)
            // })
            // axios({
            //     method:"get",
            //     url:"http://192.168.27.13:18080/basemodule/count/3"
            // }).then(function (resp) {
            //     _this.product = resp.data.data;
            // }).catch((error) => {
            //     console.error('请求失败:', error)
            // })
            // axios({
            //     method:"get",
            //     url:"http://192.168.27.13:18080/basemodule/count/4"
            // }).then(function (resp) {
            //     _this.experment = resp.data.data;
            // }).catch((error) => {
            //     console.error('请求失败:', error)
            // })
            // axios({
            //     method:"get",
            //     url:"http://192.168.27.13:18080/basemodule/count/5"
            // }).then(function (resp) {
            //     _this.cnt1 = resp.data.data;
            // }).catch((error) => {
            //     console.error('请求失败:', error)
            // })
            // axios({
            //     method:"get",
            //     url:"http://192.168.27.13:18080/basemodule/count/6"
            // }).then(function (resp) {
            //     _this.cnt2 = resp.data.data;
            // }).catch((error) => {
            //     console.error('请求失败:', error)
            // })
            // axios({
            //     method:"get",
            //     url:"http://192.168.27.13:18080/basemodule/count/7"
            // }).then(function (resp) {
            //     _this.cnt3 = resp.data.data;
            // }).catch((error) => {
            //     console.error('请求失败:', error)
            // })
            // axios({
            //     method:"get",
            //     url:"http://192.168.27.13:18080/basemodule/count/8"
            // }).then(function (resp) {
            //     _this.cnt4 = resp.data.data;
            // }).catch((error) => {
            //     console.error('请求失败:', error)
            // })
        },
        handleDropdownAction(action) {
            console.log('下拉菜单点击:', action);
            // 根据action执行不同操作
            switch (action) {
                case 'profile':
                    // 跳转个人中心
                    this.$router.push('/person').catch(() => {});
                    break;
                case 'logout':
                    // 执行退出登录
                    this.$router.push('/login').catch(() => {});
                    break;
            }
        },
        goToDataStatistics() {
            this.$router.push('/displayEchart').catch(() => {});
        },
        goToDataSearch() {
            this.$router.push('/search').catch(() => {});
        },
        goToChat() {
            this.$router.push('/chat').catch(() => {});
        },
        goToDisplayexp() {
            this.$router.push('/displayexp').catch(() => {});
        },
        goToPaper() {
            this.$router.push('/paper').catch(() => {});
        },
        goToTemplate() {
            this.$router.push('/template').catch(() => {});
        }
    },
}    
</script>

<style scoped>
/* 首页容器 */
.home-page {
    padding-top: 80px;
}

/* 导航栏下方面板 */
.statistics-container {
    width: 100%;
    height: 500px;
    background-image: url('../assets/home.jpg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: "Microsoft YaHei", sans-serif;
}

.platform-title {
    text-align: center;
    color: #aac9f4;
    font-size: 60px;
    font-weight: bold;
    margin-bottom: 40px;
    margin-right: 15%;
    border-bottom: 2px solid #e0e0e0;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px 50px;
}

/* #93c5fd */
.stat-item {
    background: #dbe7f3;
    /* 渐变背景颜色 */
    color: black;
    /* 文本颜色 */
    padding: 15px 20px;
    /* 内边距 */
    width: 80%;
    /* 固定按钮宽度 */
    height: 60%;
    /* 固定按钮高度，增加高度以适应两行文本 */
    border: none;
    /* 无边框 */
    border-radius: 8px;
    /* 圆角 */
    cursor: pointer;
    /* 鼠标悬停时显示为手型 */
    font-size: 18px;
    /* 文本大小 */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    /* 添加阴影效果 */
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    /* 动画效果 */
    display: flex;
    /* 使用Flexbox居中文本 */
    justify-content: center;
    /* 水平居中文本 */
    align-items: center;
    /* 垂直居中文本 */
    flex-direction: column;
    /* 文本垂直排列 */
    text-align: center;
    /* 文本居中对齐 */
}

.stat-label {
    margin: 10px;
    font-size: 20px;
    color: #555;
    font-weight: bold;
    /* 加粗 */
    margin-bottom: 10px;
    /* 添加间距 */
}

.stat-value {
    font-size: 20px;
    color: #1a3e72;
    font-weight: bold;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }

    .platform-title {
        font-size: 22px;
    }

    .stat-label {
        font-size: 16px;
    }

    .stat-value {
        font-size: 20px;
    }
}

/* 最后一部分 */
.mulit-options {
    height: 300px;
    background-color: #f0f0f0;
    /* 浅灰色背景 */
    display: flex;
    align-items: center;
    /* 垂直居中 */
    justify-content: space-evenly;
    padding: 5% 5%;
}

.option-item {
    background: #e8e6e6;
    /* 渐变背景颜色 */
    color: black;
    /* 文本颜色 */
    padding: 10px 20px;
    /* 内边距 */
    width: 180px;
    /* 固定按钮宽度 */
    height: 90px;
    /* 固定按钮高度，增加高度以适应两行文本 */
    border: none;
    /* 无边框 */
    border-radius: 8px;
    /* 圆角 */
    cursor: pointer;
    /* 鼠标悬停时显示为手型 */
    font-size: 25px;
    font-weight: bold;
    /* 文本大小 */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    /* 添加阴影效果 */
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    /* 动画效果 */
    display: flex;
    flex-direction: row;
}

.option-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.option-label {
    margin: 27px 4px;
    color: #555;
}

.option-img {
    padding-left: 10px;
    margin: 28px 10px;
}
</style>