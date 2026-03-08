/**
 * 枚举配置存储工具类
 * 使用静态JSON文件存储模板枚举配置，支持跨电脑共享
 * 
 * 重要说明：
 * - 此文件已升级为使用JSON文件替代localStorage
 * - 支持并发读写操作
 * - 配置文件位置：/public/template-enum-config.json
 */

import {
  getAllEnumConfigs as getAll,
  getEnumConfig as get,
  saveEnumConfig as save,
  deleteEnumConfig as remove,
  extractEnumConfig as extract,
  applyEnumConfig as apply,
  saveTemplateEnumConfig as saveTemplate,
  loadTemplateEnumConfig as loadTemplate
} from './enumConfigManager';

/**
 * 获取所有枚举配置
 * @returns {Promise<Object>} 所有模板的枚举配置
 */
export async function getAllEnumConfigs() {
  return await getAll();
}

/**
 * 获取指定模板的枚举配置
 * @param {String|Number} key 模板ID或模板名称
 * @returns {Promise<Object>} 该模板的枚举配置
 */
export async function getEnumConfig(key) {
  return await get(key);
}

/**
 * 保存指定模板的枚举配置
 * @param {String|Number} key 模板ID或模板名称（推荐使用模板名称）
 * @param {Object} config 枚举配置对象
 * @returns {Promise<Boolean>} 是否保存成功
 */
export async function saveEnumConfig(key, config) {
  return await save(key, config);
}

/**
 * 删除指定模板的枚举配置
 * @param {String|Number} key 模板ID或模板名称
 * @returns {Promise<Boolean>} 是否删除成功
 */
export async function deleteEnumConfig(key) {
  return await remove(key);
}

/**
 * 从字段列表中提取枚举配置
 * @param {Array} fields 字段数组
 * @returns {Object} 枚举配置对象
 */
export function extractEnumConfig(fields) {
  return extract(fields);
}

/**
 * 将枚举配置应用到字段列表
 * @param {Array} fields 字段数组
 * @param {Object} config 枚举配置对象
 */
export function applyEnumConfig(fields, config) {
  return apply(fields, config);
}

/**
 * 保存模板的完整枚举配置（包含三个区域）
 * @param {String|Number} key 模板ID或模板名称（推荐使用模板名称）
 * @param {Array} objectFields 对象区域字段
 * @param {Array} operationFields 操作区域字段
 * @param {Array} resultFields 结果区域字段
 * @returns {Promise<Boolean>} 是否保存成功
 */
export async function saveTemplateEnumConfig(key, objectFields, operationFields, resultFields) {
  return await saveTemplate(key, objectFields, operationFields, resultFields);
}

/**
 * 加载模板的完整枚举配置（包含三个区域）
 * @param {String|Number} key 模板ID或模板名称
 * @param {Array} objectFields 对象区域字段
 * @param {Array} operationFields 操作区域字段
 * @param {Array} resultFields 结果区域字段
 * @returns {Promise<Boolean>} 是否加载成功
 */
export async function loadTemplateEnumConfig(key, objectFields, operationFields, resultFields) {
  return await loadTemplate(key, objectFields, operationFields, resultFields);
}

/**
 * 导出配置文件（下载为JSON文件）
 * 用于在不同电脑间同步配置
 * @returns {Promise<Boolean>} 是否导出成功
 */
export async function exportConfigFile() {
  const { exportConfigFile: exportFile } = await import('./enumConfigManager');
  return await exportFile();
}

/**
 * 导入配置文件
 * 用于从其他电脑同步配置
 * @param {File} file - JSON配置文件
 * @returns {Promise<Boolean>} 是否导入成功
 */
export async function importConfigFile(file) {
  const { importConfigFile: importFile } = await import('./enumConfigManager');
  return await importFile(file);
}

/**
 * 列出所有已保存的模板ID
 * @returns {Promise<Array>} 模板ID数组
 */
export async function listAllTemplateIds() {
  const { listAllTemplateIds: listIds } = await import('./enumConfigManager');
  return await listIds();
}

/**
 * 在控制台打印所有枚举配置概览（调试用）
 * @returns {Promise<void>}
 */
export async function debugAllEnumConfigs() {
  const { debugAllEnumConfigs: debug } = await import('./enumConfigManager');
  return await debug();
}

/**
 * 在控制台打印指定模板的枚举配置详情（调试用）
 * @param {String|Number} key 模板ID或模板名称
 * @returns {Promise<void>}
 */
export async function debugEnumConfig(key) {
  const { debugEnumConfig: debug } = await import('./enumConfigManager');
  return await debug(key);
}

/**
 * 清空缓存
 */
export function clearCache() {
  import('./enumConfigManager').then(module => {
    module.clearCache();
  });
}

