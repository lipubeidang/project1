/**
 * 枚举配置管理器
 * 使用后端API存储模板枚举配置，支持多用户跨电脑实时共享
 * 
 * 工作原理：
 * 1. 所有配置存储在服务器的 JSON 文件中
 * 2. 通过 HTTP API 进行读写操作
 * 3. 支持多用户并发访问
 * 4. 自动同步，无需手动导入导出
 * 
 * API 接口：
 * - GET  /api/enum-config        - 获取所有配置
 * - POST /api/enum-config        - 保存配置
 * - DELETE /api/enum-config/:key - 删除配置
 */

// API 服务器地址
// 使用相对路径，通过vue.config.js的proxy代理到配置服务器
// 开发环境：通过代理访问（''会使用当前域名+端口）
// 生产环境：需要配置实际的API服务器地址
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'http://localhost:3001'  // 生产环境直接访问
  : '';  // 开发环境通过代理访问

// 本地缓存（提高性能，减少网络请求）
let cachedConfig = null;
let cacheTimestamp = 0;
const CACHE_DURATION = 5000; // 缓存5秒

// 并发控制：请求队列
let requestQueue = [];
let isProcessing = false;

/**
 * 并发控制：处理请求队列
 */
async function processQueue() {
  if (isProcessing || requestQueue.length === 0) {
    return;
  }

  isProcessing = true;
  const request = requestQueue.shift();

  try {
    const result = await request.execute();
    request.resolve(result);
  } catch (error) {
    request.reject(error);
  } finally {
    isProcessing = false;
    // 继续处理下一个请求
    if (requestQueue.length > 0) {
      setTimeout(processQueue, 0);
    }
  }
}

/**
 * 添加请求到队列（支持并发控制）
 * @param {Function} execute - 要执行的函数
 * @returns {Promise} 执行结果
 */
function enqueue(execute) {
  return new Promise((resolve, reject) => {
    requestQueue.push({ execute, resolve, reject });
    processQueue();
  });
}

/**
 * 从服务器获取所有配置
 * @returns {Promise<Object>}
 */
async function fetchAllConfigsFromServer() {
  // 检查缓存
  const now = Date.now();
  if (cachedConfig && (now - cacheTimestamp) < CACHE_DURATION) {
    console.log('📦 使用缓存的配置数据');
    return { ...cachedConfig };
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/enum-config`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.success) {
      // 更新缓存
      cachedConfig = result.data;
      cacheTimestamp = now;
      
      console.log('✅ 从服务器获取配置，模板数量:', Object.keys(result.data).length);
      return result.data;
    } else {
      throw new Error(result.error || '获取配置失败');
    }
  } catch (error) {
    console.error('❌ 获取配置失败:', error.message);
    
    // 如果服务器不可用，尝试使用缓存
    if (cachedConfig) {
      console.warn('⚠️ 服务器不可用，使用缓存数据');
      return { ...cachedConfig };
    }
    
    // 如果没有缓存，返回空对象
    return {};
  }
}

/**
 * 保存配置到服务器
 * @param {String} templateKey - 模板键
 * @param {Object} config - 配置对象
 * @returns {Promise<Boolean>}
 */
async function saveConfigToServer(templateKey, config) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/enum-config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        templateKey,
        config
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.success) {
      // 清空缓存，下次读取时会重新获取
      cachedConfig = null;
      console.log('✅ 配置已保存到服务器:', templateKey);
      return true;
    } else {
      throw new Error(result.error || '保存配置失败');
    }
  } catch (error) {
    console.error('❌ 保存配置失败:', error.message);
    throw error;
  }
}

/**
 * 从服务器删除配置
 * @param {String} templateKey - 模板键
 * @returns {Promise<Boolean>}
 */
async function deleteConfigFromServer(templateKey) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/enum-config/${encodeURIComponent(templateKey)}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.success) {
      // 清空缓存
      cachedConfig = null;
      console.log('✅ 配置已从服务器删除:', templateKey);
      return true;
    } else {
      throw new Error(result.error || '删除配置失败');
    }
  } catch (error) {
    console.error('❌ 删除配置失败:', error.message);
    throw error;
  }
}

/**
 * 获取所有模板的枚举配置
 * @returns {Promise<Object>} 所有模板配置
 */
export async function getAllEnumConfigs() {
  return enqueue(async () => {
    return await fetchAllConfigsFromServer();
  });
}

/**
 * 获取指定模板的枚举配置
 * @param {String|Number} templateKey - 模板ID或模板名称
 * @returns {Promise<Object>} 该模板的枚举配置
 */
export async function getEnumConfig(templateKey) {
  return enqueue(async () => {
    const allConfigs = await fetchAllConfigsFromServer();
    return allConfigs[templateKey] || {};
  });
}

/**
 * 保存指定模板的枚举配置
 * @param {String|Number} templateKey - 模板ID或模板名称
 * @param {Object} enumConfig - 枚举配置对象
 * @returns {Promise<Boolean>} 是否保存成功
 */
export async function saveEnumConfig(templateKey, enumConfig) {
  return enqueue(async () => {
    return await saveConfigToServer(templateKey, enumConfig);
  });
}

/**
 * 删除指定模板的枚举配置
 * @param {String|Number} templateKey - 模板ID或模板名称
 * @returns {Promise<Boolean>} 是否删除成功
 */
export async function deleteEnumConfig(templateKey) {
  return enqueue(async () => {
    return await deleteConfigFromServer(templateKey);
  });
}

/**
 * 从字段列表中提取枚举配置
 * @param {Array} fields - 字段数组
 * @returns {Object} 枚举配置对象
 */
export function extractEnumConfig(fields) {
  const config = {};
  const nameIndex = {}; // 用于追踪字段名的使用次数
  
  fields.forEach((field, index) => {
    if (field.type === 'enum' && field.enumOptions) {
      // 标准化字段名（用于匹配）
      const normalizedName = field.name.toLowerCase().replace(/[_\s-]/g, '');
      
      // 使用多个键来存储，提高匹配成功率
      const enumData = {
        fieldName: field.name,
        originalFieldName: field.name, // 原始字段名
        normalizedName: normalizedName,  // 标准化字段名用于匹配
        index: index,  // 字段索引
        options: field.enumOptions.map(opt => ({
          label: opt.label,
          value: opt.value
        }))
      };
      
      // 主键：使用索引和字段名
      config[`field_${index}_${field.name}`] = enumData;
      
      // 备用键1：只使用字段名（处理索引不匹配的情况）
      const nameKey = `name_${field.name}`;
      if (!nameIndex[nameKey]) {
        nameIndex[nameKey] = 0;
      }
      config[nameKey] = enumData;
      nameIndex[nameKey]++;
      
      // 备用键2：使用标准化字段名（处理字段名格式不同的情况）
      config[`normalized_${normalizedName}`] = enumData;
    }
  });
  return config;
}

/**
 * 将枚举配置应用到字段列表
 * @param {Array} fields - 字段数组
 * @param {Object} config - 枚举配置对象
 */
export function applyEnumConfig(fields, config) {
  if (!config || Object.keys(config).length === 0) {
    return;
  }
  
  fields.forEach((field, index) => {
    if (field.type === 'enum') {
      const configKey = `field_${index}_${field.name}`;
      const enumConfig = config[configKey];
      if (enumConfig) {
        field.enumOptions = enumConfig.options || [{ label: 'A', value: '' }];
      }
    }
  });
}

/**
 * 保存模板的完整枚举配置（包含三个区域）
 * @param {String|Number} templateKey - 模板ID或模板名称
 * @param {Array} objectFields - 对象区域字段
 * @param {Array} operationFields - 操作区域字段
 * @param {Array} resultFields - 结果区域字段
 * @returns {Promise<Boolean>} 是否保存成功
 */
export async function saveTemplateEnumConfig(templateKey, objectFields, operationFields, resultFields) {
  const config = {
    object: extractEnumConfig(objectFields),
    operation: extractEnumConfig(operationFields),
    result: extractEnumConfig(resultFields),
    timestamp: new Date().toISOString()
  };
  return await saveEnumConfig(templateKey, config);
}

/**
 * 加载模板的完整枚举配置（包含三个区域）
 * @param {String|Number} templateKey - 模板ID或模板名称
 * @param {Array} objectFields - 对象区域字段
 * @param {Array} operationFields - 操作区域字段
 * @param {Array} resultFields - 结果区域字段
 * @returns {Promise<Boolean>} 是否加载成功
 */
export async function loadTemplateEnumConfig(templateKey, objectFields, operationFields, resultFields) {
  const config = await getEnumConfig(templateKey);
  if (config && Object.keys(config).length > 0) {
    if (config.object) applyEnumConfig(objectFields, config.object);
    if (config.operation) applyEnumConfig(operationFields, config.operation);
    if (config.result) applyEnumConfig(resultFields, config.result);
    console.log('✅ 枚举配置已加载:', templateKey);
    return true;
  }
  return false;
}

/**
 * 导出配置文件（下载为JSON文件，备份用）
 */
export async function exportConfigFile() {
  try {
    const allConfigs = await fetchAllConfigsFromServer();
    
    // 构建符合文件格式的配置对象
    const exportData = {
      _metadata: {
        version: "1.0.0",
        description: "模板枚举配置存储文件 - 所有模板的枚举选项都保存在这里",
        lastUpdated: new Date().toISOString(),
        note: "此文件由系统自动管理，支持多用户并发访问",
        exportedFrom: window.location.hostname,
        templateCount: Object.keys(allConfigs).length
      },
      templates: allConfigs
    };
    
    const configJson = JSON.stringify(exportData, null, 2);
    const blob = new Blob([configJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    link.download = `template-enum-config-backup-${timestamp}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    console.log('📥 配置文件已导出（备份），包含', Object.keys(allConfigs).length, '个模板');
    return true;
  } catch (error) {
    console.error('❌ 导出配置文件失败:', error);
    return false;
  }
}

/**
 * 导入配置文件（批量导入到服务器）
 * @param {File} file - JSON配置文件
 * @returns {Promise<Boolean>}
 */
export async function importConfigFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = async (e) => {
      try {
        const importedData = JSON.parse(e.target.result);
        
        // 验证文件格式
        if (!importedData.templates) {
          console.error('❌ 无效的配置文件格式');
          resolve(false);
          return;
        }
        
        // 批量保存到服务器
        const templates = importedData.templates;
        let successCount = 0;
        
        for (const [key, config] of Object.entries(templates)) {
          try {
            await saveConfigToServer(key, config);
            successCount++;
          } catch (error) {
            console.error(`❌ 导入模板 ${key} 失败:`, error);
          }
        }
        
        console.log(`✅ 配置导入完成，成功导入 ${successCount}/${Object.keys(templates).length} 个模板`);
        resolve(successCount > 0);
      } catch (error) {
        console.error('❌ 导入配置失败:', error);
        reject(error);
      }
    };
    
    reader.onerror = () => {
      console.error('❌ 读取文件失败');
      reject(new Error('读取文件失败'));
    };
    
    reader.readAsText(file);
  });
}

/**
 * 列出所有已保存的模板ID
 * @returns {Promise<Array>} 模板ID数组
 */
export async function listAllTemplateIds() {
  const templates = await getAllEnumConfigs();
  return Object.keys(templates);
}

/**
 * 打印所有枚举配置概览（调试用）
 */
export async function debugAllEnumConfigs() {
  console.group('📊 所有枚举配置概览');
  const allConfigs = await getAllEnumConfigs();
  const templateIds = Object.keys(allConfigs);
  
  if (templateIds.length === 0) {
    console.warn('⚠️ 没有任何枚举配置');
    console.groupEnd();
    return;
  }
  
  console.log(`共有 ${templateIds.length} 个模板的枚举配置`);
  
  templateIds.forEach(templateId => {
    const config = allConfigs[templateId];
    console.group(`📝 模板ID: ${templateId}`);
    console.log('保存时间:', config.timestamp || '未知');
    console.log('最后修改:', config.lastModified || '未知');
    
    ['object', 'operation', 'result'].forEach(section => {
      if (config[section] && Object.keys(config[section]).length > 0) {
        const sectionConfig = config[section];
        const fieldCount = Object.keys(sectionConfig).length;
        console.log(`${section} 区域: ${fieldCount} 个配置项`);
        
        // 提取唯一的字段名
        const uniqueFields = new Set();
        Object.values(sectionConfig).forEach(item => {
          if (item.fieldName) uniqueFields.add(item.fieldName);
        });
        console.log(`  字段: ${Array.from(uniqueFields).join(', ')}`);
      }
    });
    
    console.groupEnd();
  });
  
  console.groupEnd();
}

/**
 * 打印指定模板的枚举配置详情（调试用）
 * @param {String|Number} key 模板ID或模板名称
 * @returns {Promise<void>}
 */
export async function debugEnumConfig(key) {
  console.group(`🔍 模板 ${key} 的枚举配置详情`);
  
  const config = await getEnumConfig(key);
  
  if (!config) {
    console.warn(`⚠️ 未找到模板 ${key} 的枚举配置`);
    console.groupEnd();
    return;
  }
  
  console.log('保存时间:', config.timestamp || '未知');
  console.log('最后修改:', config.lastModified || '未知');
  
  ['object', 'operation', 'result'].forEach(section => {
    if (config[section] && Object.keys(config[section]).length > 0) {
      const sectionConfig = config[section];
      console.group(`📋 ${section} 区域 (${Object.keys(sectionConfig).length} 个配置项)`);
      
      // 按字段名分组显示
      const fieldGroups = {};
      Object.entries(sectionConfig).forEach(([enumValue, item]) => {
        const fieldName = item.fieldName || '未知字段';
        if (!fieldGroups[fieldName]) {
          fieldGroups[fieldName] = [];
        }
        fieldGroups[fieldName].push({ enumValue, ...item });
      });
      
      Object.entries(fieldGroups).forEach(([fieldName, items]) => {
        console.group(`字段: ${fieldName}`);
        items.forEach(item => {
          console.log(`  ${item.enumValue}: ${item.displayName || '无显示名'}`);
        });
        console.groupEnd();
      });
      
      console.groupEnd();
    }
  });
  
  console.groupEnd();
}

/**
 * 清空缓存
 */
export function clearCache() {
  cachedConfig = null;
  cacheTimestamp = 0;
  console.log('🧹 缓存已清空');
}

/**
 * 批量保存多个模板配置（优化性能）
 * @param {Object} configs - { templateKey: enumConfig, ... }
 * @returns {Promise<Boolean>} 是否保存成功
 */
export async function batchSaveEnumConfigs(configs) {
  let successCount = 0;
  const keys = Object.keys(configs);
  
  for (const templateKey of keys) {
    try {
      await saveConfigToServer(templateKey, configs[templateKey]);
      successCount++;
    } catch (error) {
      console.error(`❌ 保存模板 ${templateKey} 失败:`, error);
    }
  }
  
  console.log(`✅ 批量保存完成，成功 ${successCount}/${keys.length} 个模板配置`);
  return successCount > 0;
}

// 导出工具函数供外部使用
export default {
  getAllEnumConfigs,
  getEnumConfig,
  saveEnumConfig,
  deleteEnumConfig,
  extractEnumConfig,
  applyEnumConfig,
  saveTemplateEnumConfig,
  loadTemplateEnumConfig,
  exportConfigFile,
  importConfigFile,
  listAllTemplateIds,
  debugAllEnumConfigs,
  debugEnumConfig,
  clearCache,
  batchSaveEnumConfigs
};

