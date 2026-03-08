/**
 * 极简配置服务器
 * 功能：提供模板枚举配置的读写API
 * 只需50行代码，支持多用户并发访问
 */

const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 3001;

// JSON配置文件路径
const CONFIG_FILE = path.join(__dirname, '../public/template-enum-config.json');

// 中间件
app.use(cors()); // 允许跨域
app.use(express.json({ limit: '10mb' })); // 解析JSON请求体

// 确保配置文件存在
async function ensureConfigFile() {
  try {
    await fs.access(CONFIG_FILE);
  } catch {
    // 文件不存在，创建默认配置
    const defaultConfig = {
      _metadata: {
        version: "1.0.0",
        description: "模板枚举配置存储文件",
        lastUpdated: new Date().toISOString()
      },
      templates: {}
    };
    await fs.writeFile(CONFIG_FILE, JSON.stringify(defaultConfig, null, 2));
    console.log('✅ 已创建默认配置文件');
  }
}

// API 1: 获取所有配置
app.get('/api/enum-config', async (req, res) => {
  try {
    const data = await fs.readFile(CONFIG_FILE, 'utf8');
    const config = JSON.parse(data);
    res.json({
      success: true,
      data: config.templates || {}
    });
    console.log(`📖 读取配置 - 模板数量: ${Object.keys(config.templates || {}).length}`);
  } catch (error) {
    console.error('❌ 读取配置失败:', error);
    res.status(500).json({
      success: false,
      error: '读取配置失败'
    });
  }
});

// API 2: 保存配置
app.post('/api/enum-config', async (req, res) => {
  try {
    const { templateKey, config } = req.body;
    
    if (!templateKey || !config) {
      return res.status(400).json({
        success: false,
        error: '参数错误：需要 templateKey 和 config'
      });
    }
    
    // 读取现有配置
    const data = await fs.readFile(CONFIG_FILE, 'utf8');
    const fullConfig = JSON.parse(data);
    
    // 更新指定模板的配置
    if (!fullConfig.templates) {
      fullConfig.templates = {};
    }
    
    fullConfig.templates[templateKey] = {
      ...config,
      lastModified: new Date().toISOString()
    };
    
    fullConfig._metadata.lastUpdated = new Date().toISOString();
    
    // 写入文件
    await fs.writeFile(CONFIG_FILE, JSON.stringify(fullConfig, null, 2));
    
    res.json({
      success: true,
      message: '配置保存成功'
    });
    
    console.log(`💾 保存配置 - 模板: ${templateKey}`);
  } catch (error) {
    console.error('❌ 保存配置失败:', error);
    res.status(500).json({
      success: false,
      error: '保存配置失败'
    });
  }
});

// API 3: 删除配置
app.delete('/api/enum-config/:templateKey', async (req, res) => {
  try {
    const { templateKey } = req.params;
    
    // 读取现有配置
    const data = await fs.readFile(CONFIG_FILE, 'utf8');
    const fullConfig = JSON.parse(data);
    
    if (fullConfig.templates && fullConfig.templates[templateKey]) {
      delete fullConfig.templates[templateKey];
      fullConfig._metadata.lastUpdated = new Date().toISOString();
      
      // 写入文件
      await fs.writeFile(CONFIG_FILE, JSON.stringify(fullConfig, null, 2));
      
      res.json({
        success: true,
        message: '配置删除成功'
      });
      
      console.log(`🗑️ 删除配置 - 模板: ${templateKey}`);
    } else {
      res.status(404).json({
        success: false,
        error: '配置不存在'
      });
    }
  } catch (error) {
    console.error('❌ 删除配置失败:', error);
    res.status(500).json({
      success: false,
      error: '删除配置失败'
    });
  }
});

// 获取本机局域网IP地址
function getLocalIP() {
  const os = require('os');
  const networkInterfaces = os.networkInterfaces();
  
  for (const interfaceName in networkInterfaces) {
    const interfaces = networkInterfaces[interfaceName];
    for (const iface of interfaces) {
      // 跳过内部回环地址和非IPv4地址
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return 'localhost';
}

// 启动服务器
async function start() {
  await ensureConfigFile();
  
  // 监听所有网络接口（0.0.0.0），使局域网可访问
  app.listen(PORT, '0.0.0.0', () => {
    const localIP = getLocalIP();
    console.log('');
    console.log('🚀 =============================================');
    console.log('   模板枚举配置服务器已启动');
    console.log('🚀 =============================================');
    console.log('');
    console.log(`   本机访问: http://localhost:${PORT}`);
    console.log(`   局域网访问: http://${localIP}:${PORT}`);
    console.log(`   配置文件: ${CONFIG_FILE}`);
    console.log('');
    console.log('   API 接口:');
    console.log(`   GET    /api/enum-config           - 获取所有配置`);
    console.log(`   POST   /api/enum-config           - 保存配置`);
    console.log(`   DELETE /api/enum-config/:key      - 删除配置`);
    console.log('');
    console.log('   💡 其他电脑可通过局域网IP访问此服务');
    console.log('   按 Ctrl+C 停止服务器');
    console.log('=============================================');
    console.log('');
  });
}

start().catch(console.error);

