const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
   devServer: {
    host: '0.0.0.0', // 绑定所有网卡，使局域网可访问
    port: 8080,      // 默认端口，可自定义
    open: false,     // 启动时不自动打开浏览器
    hot: true ,       // 热更新
    allowedHosts: 'all',  // 允许所有主机访问
    // 配置代理，将前端请求转发到后端
    proxy: {
      // 枚举配置API走3001端口（配置服务器）
      '/api/enum-config': {
        target: 'http://localhost:3001',
        changeOrigin: true
      },
      // 其他API走8083端口（主后端）
      '/api': {
        target: 'http://localhost:8083',  // 本地后端地址
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''  // 去掉/api前缀
        }
      }
    }
  }
})
