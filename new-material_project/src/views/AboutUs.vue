<template>
    <div>
        <Navbar @dropdown-action="handleDropdownAction" />

        <!-- 导航栏下方的两张图片（上下排列） -->
        <div class="image-container">
            <img 
                :src="require('../assets/data1.png')" 
                alt="图片1" 
                class="about-image"
            >
            
            <img 
                :src="require('../assets/plat1.png')" 
                alt="图片2" 
                class="about-image"
            >
        </div>
    </div>
</template>


<script>
import Navbar from '../components/Navbar.vue';
// import axios from 'axios';

export default {
    name: "AboutUs",
    components: {
        Navbar
    },
    data() {
        return {
            
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
        
    },
}    
</script>

<style scoped>
/* 图片容器样式（改为垂直排列） */
.image-container {
  display: flex;
  flex-direction: column; /* 垂直排列 */
  align-items: center; /* 水平居中 */
  padding: 20px;
  gap: 20px; /* 图片间距 */
}

.about-image {
  width: 60%; /* 图片宽度 */
  border-radius: 8px; /* 圆角 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); /* 阴影 */
}

.about-image {
  transition: transform 0.3s ease;
}

.about-image:hover {
  transform: scale(1.02); /* 悬停时微放大 */
}
</style>