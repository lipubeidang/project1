<template>
<div>
    <Navbar @dropdown-action="handleDropdownAction" />
    <div class = "head-container">
        <h1>案例展示</h1>
    </div>
    <div class="corner-carousel-container">

    <!-- 左上角轮播图 -->
    <el-carousel class="corner-carousel top-left">
        <el-carousel-item v-for="(item, index) in imageList1" :key="index">
            <h3 class="carousel-title">骨诱导相关</h3>
            <img :src="item.url" alt="轮播图" class="carousel-img">
            <div class="carousel-caption">
            {{ item.title }}
            </div>
        </el-carousel-item>
    </el-carousel>

    <!-- 右上角轮播图 -->
    <el-carousel class="corner-carousel top-right">
        <el-carousel-item v-for="(item, index) in imageList2" :key="index">
            <h3 class="carousel-title">类骨磷灰石</h3>
            <img :src="item.url" alt="轮播图" class="carousel-img">
            <div class="carousel-caption">
            {{ item.title }}
            </div>
        </el-carousel-item>
    </el-carousel>

    <!-- 左下角轮播图 -->
    <el-carousel class="corner-carousel bottom-left">
        <el-carousel-item v-for="(item, index) in imageList3" :key="index">
            <h3 class="carousel-title">工艺优化</h3>
            <img :src="item.url" alt="轮播图" class="carousel-img">
            <div class="carousel-caption">
            {{ item.title }}
            </div>
        </el-carousel-item>
    </el-carousel>

    <!-- 右下角轮播图 -->
    <el-carousel class="corner-carousel bottom-right">
        <el-carousel-item v-for="(item, index) in imageList4" :key="index">
            <h3 class="carousel-title">高通量实验</h3>
            <img :src="item.url" alt="轮播图" class="carousel-img">
            <div class="carousel-caption">
            {{ item.title }}
            </div>
        </el-carousel-item>
    </el-carousel>

    <!-- 中央按钮 -->
    <div class="center-button-container">
      <el-button type="primary" size="large" class="center-button" @click="goToFlow">开始机器学习</el-button>
    </div>

    </div>
    </div>
</template>


<script>
import Navbar from '../components/Navbar.vue';
export default {
    name: "DisplayExp",
    components: {
        Navbar
    },
    data() {
        return {
            userName: '用户名',
            circleUrl: "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png",
            imageList1:[
                { 
                url: require("../assets/bone1.png"), // 使用 require 导入
                title: 'list1_1' 
                }
            ],
            imageList2:[
            { 
                url: require("../assets/list2_1.png"), // 使用 require 导入
                title: 'list2_1' 
                },
                { 
                url: require("../assets/list2_2.png"), // 使用 require 导入
                title: 'list2_2' 
                },
                { 
                url: require("../assets/list2_3.png"), // 使用 require 导入
                title: 'list2_3' 
                },
                { 
                url: require("../assets/list2_4.png"), // 使用 require 导入
                title: 'list2_4' 
                },
            ],
            imageList3:[
                { 
                url: require("../assets/100Epoch.png"), // 使用 require 导入
                title: 'list3_1' 
                },
                { 
                url: require("../assets/150Epoch.png"), // 使用 require 导入
                title: 'list3_2' 
                },
                { 
                url: require("../assets/200Epoch.png"), // 使用 require 导入
                title: 'list3_3' 
                },
            ],
            imageList4:[
                { 
                url: require("../assets/list4_1.png"), // 使用 require 导入
                title: 'list4_1' 
                }
            ],
           
        }
    },
    mounted() {
        
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
        goToFlow() {
            this.$router.push('/flow');
        },
        
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

.corner-carousel-container {
  position: relative;
  width: 100%;
  min-height: 600px; /* 容器最小高度 */
  padding: 20px;
  display: grid;
  grid-template-columns: 1fr minmax(50px, 170px) 1fr; /* 3列布局中间列更窄 */
  grid-template-rows: 1fr minmax(50px, 120px) 1fr;    /* 3行布局中间行更窄 */
  gap: 10px; /* 网格间距 */
}

.corner-carousel {
  width: 100%;
  height: 320px;
  border-radius: 0px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 定位四个角落 */
.top-left {
  grid-row: 1;
  grid-column: 1;
}

.top-right {
  grid-row: 1;
  grid-column: 3;
}

.bottom-left {
  grid-row: 3;
  grid-column: 1;
}

.bottom-right {
  grid-row: 3;
  grid-column: 3;
}

/* 中央按钮样式 */
.center-button-container {
  grid-row: 2;
  grid-column: 2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.center-button {
  width: 200px; /* 自定义宽度 */
  height: 70px; /* 自定义高度 */
  line-height: 40px; /* 垂直居中文字 */
  padding: 0; /* 重置内边距 */
  font-size: 20px;
}

.carousel-img {
    max-width: 98%; /* 预留一些边距，避免图片紧贴容器边缘 */
    max-height: 98%;
    object-fit: cotain;      /* 关键属性：保持比例覆盖容器，可能裁剪边缘 */
}

.head-container {
    width: 100%;
    height: 12%;
    margin-top: 3%;
}
</style>