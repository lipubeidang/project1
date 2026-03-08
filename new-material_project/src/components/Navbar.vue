<template>
    <!-- 固定在顶部的导航栏 -->
    <header class="main-header">
        <div class="header-container">
            <div class="logo-container">
                <img src="../assets/logo.png" alt="材料Logo" class="logo-img">
                <h1 class="logo-text">生物医用材料数据资源节点</h1>
            </div>
            <div class="dropdown-item1">
                <!-- 首页导航，to 属性对应路由的 path -->
                <router-link to="/" class="nav-link">首页</router-link>
                <!-- 关于我们导航，to 属性对应 /paper 路径 -->
                <router-link to="/aboutus" class="nav-link">关于我们</router-link>
            </div>
            <div class="user-section" @click="toggleDropdown" ref="userDropdown">
                <!-- 头像 -->
                <el-col :span="12">
                    <div class="avatar">
                        <el-avatar :size="50" :src="circleUrl"></el-avatar>
                    </div>
                </el-col>
                <div class="username">
                    <span>{{ userName }}</span>
                </div>
                <div class="dropdown" :class="{ active: isDropdownOpen }">
                    <a href="#" class="dropdown-item" v-for="(item, index) in dropdownItems" :key="index"
                        @click.prevent="handleDropdownClick(item)">
                        {{ item.text }}
                    </a>
                </div>
            </div>
        </div>
    </header>
</template>

<script>
export default {
    name: 'NavbarS',
    data() {
        return {
            isDropdownOpen: false,
            dropdownItems: [
                { text: '个人中心', action: 'profile' },
                { text: '退出登录', action: 'logout' }
            ],
            userName: '用户名',
            circleUrl: "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png",
        }
    },
    computed: {
        userInitials() {
            return this.userName.substring(0, 1).toUpperCase();
        }
    },
    methods: {
        toggleDropdown() {
            this.isDropdownOpen = !this.isDropdownOpen;
        },
        handleDropdownClick(item) {
            this.isDropdownOpen = false;
            this.$emit('dropdown-action', item.action);
        },
        // closeDropdown(event) {
        //     // if (!this.$refs.userDropdown.contains(event.target)) {
        //     //     this.isDropdownOpen = false;
        //     // }
        // }
    },
    mounted() {
        document.addEventListener('click', this.closeDropdown);
    },
    beforeUnmount() {
        document.removeEventListener('click', this.closeDropdown);
    }
}
</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Roboto', sans-serif;
}


/* 顶部导航栏样式 */
.main-header {
    background-color: rgb(255, 255, 255);
    color: rgb(255, 255, 255);
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-container {
    width: 100%;
    margin: 0 1%;
    /* padding: 0 0px; */
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 80px;
}

.logo-container {
    display: flex;
    align-items: center;
    white-space: nowrap;
    gap: 15px;
}

.logo-text {
    font-size: 2rem;
    font-weight: bold;
    color: rgb(15, 76, 243);
}

.logo-img {
    height: 60px;
    width: auto;
}

.form-img {
    height: 44px;
    width: auto;
    margin-right: 5px;
}

/* 头像 */
.avatar {
    margin-top: 5px;
}

.user-section {
    position: relative;
    display: flex;
    align-items: center;
    gap: 12px;
    padding-left: 10px;
    margin-right: 150px;
}

.username {
    display: flex;
    align-items: center;
    padding: 5px 10px;
    border-radius: 4px;
    transition: all 0.3s ease;
    color: rgb(13, 134, 233);
    cursor: pointer;
    font-weight: bold;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-left: 8px;
}

.username:hover {
    background-color: rgba(255, 255, 255, 0.1);
    transform: scale(1.05);
}

.dropdown {
    position: absolute;
    top: 100%;
    /* right: 0; */
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    width: 140px;
    opacity: 0;
    visibility: hidden;
    transform: translateY(10px);
    transition: all 0.3s ease;
    z-index: 100;
}

.dropdown.active {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.dropdown-item {
    padding: 10px 15px;
    color: rgb(13, 134, 233);
    text-decoration: none;
    display: block;
    transition: all 0.2s ease;
}

.dropdown-item1 {
    /* color: #333; */
    /* text-decoration: none; */
    transition: all 0.2s ease;
    padding-left: 60%;
    display: flex;
    gap: 10px;
    white-space: nowrap;
}

.nav-link {
    text-decoration: none;
    color: #333;
}

.dropdown-item:hover {
    background-color: #f0f0f0;
    color: #1a3e72;
}

.dropdown-item:not(:last-child) {
    border-bottom: 1px solid #e0e0e0;
}
</style>