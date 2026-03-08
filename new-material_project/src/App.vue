<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
  created() {
    // 页面加载时，从 localStorage 恢复登录状态到 Vuex
    this.restoreLoginState();
  },
  methods: {
    restoreLoginState() {
      try {
        const userData = JSON.parse(localStorage.getItem('xm-user') || '{}');
        if (userData.username) {
          // 恢复用户名和权限到 Vuex
          const userRole = userData.role || userData.logininfo?.role || userData.logininfo?.type || userData.logininfo?.userType || 1;
          this.$store.commit('setUserInfo', { 
            username: userData.username, 
            role: userRole 
          });
          console.log('✅ 恢复登录状态:', userData.username, '角色:', userRole);
        }
      } catch (error) {
        console.error('恢复登录状态失败:', error);
      }
    }
  }
}
</script>

<style lang="scss">
/* 引入性能优化样式 - 确保60fps流畅动画 */
@import './assets/performance-optimize.css';

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  
  /* 开启GPU硬件加速 */
  transform: translate3d(0, 0, 0);
  -webkit-transform: translate3d(0, 0, 0);
}

</style>
