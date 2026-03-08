import Vue from 'vue'
// import './plugins/axios'
import App from './App.vue'
import router from './router'
import store from './store'

import ElementUI from 'element-ui';                      // 引入element-ui
import 'element-ui/lib/theme-chalk/index.css';           // element-ui的css样式要单独引入

import axios from 'axios'

import dragVerify from 'vue-drag-verify2'

// 导入枚举配置调试工具
import { debugAllEnumConfigs, getAllEnumConfigs, debugEnumConfig } from './utils/enumStorage'

// 创建 axios 实例并挂载到 Vue 原型
const request = axios.create({
  baseURL: '/api', // 开发环境走代理
  timeout: 60000 // 请求超时时间（60秒，适合文件上传）
});

// 添加请求拦截器
request.interceptors.request.use(
  config => {
    // 如果不是 FormData，才设置 JSON 类型
    // FormData 用于文件上传，需要浏览器自动设置 Content-Type（包含 boundary）
    if (!(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json;charset=UTF-8';
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 添加响应拦截器
request.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

Vue.prototype.$request = request;

Vue.prototype.$axios = axios

Vue.use(ElementUI,{size:"small"});

Vue.use(dragVerify)

Vue.config.productionTip = false

// 暴露全局调试函数到window对象，方便在控制台调用
if (process.env.NODE_ENV === 'development') {
  window.debugEnumConfigs = debugAllEnumConfigs;
  window.getEnumConfigs = getAllEnumConfigs;
  window.debugEnumConfig = debugEnumConfig;
  console.log('🔧 调试工具已加载，可在控制台使用：');
  console.log('  - debugEnumConfigs()  : 查看所有枚举配置概览');
  console.log('  - getEnumConfigs()    : 获取所有枚举配置原始数据');
  console.log('  - debugEnumConfig(id) : 查看指定模板的枚举配置详情');
}

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
