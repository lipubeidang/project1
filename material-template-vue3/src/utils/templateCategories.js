/**
 * 模版分类配置
 * 根据数据模板体系定义的8个大目录及其子目录
 */

// 分类数据结构
export const templateCategories = [
  {
    id: 'cat_basic',
    name: '材料基本信息',
    description: '材料的基本属性和信息',
    icon: 'Document',
    hasChildren: false,  // 无子目录，直接存模版
    children: []
  },
  {
    id: 'cat_design',
    name: '理性设计与预测',
    description: '计算模拟与理性设计相关模版',
    icon: 'Cpu',
    hasChildren: true,
    children: [
      { id: 'cat_design_1', name: '计算对象', parentId: 'cat_design' },
      { id: 'cat_design_2', name: '计算模型参数', parentId: 'cat_design' },
      { id: 'cat_design_3', name: '计算结果', parentId: 'cat_design' }
    ]
  },
  {
    id: 'cat_preparation',
    name: '制备与加工',
    description: '材料制备工艺与加工相关模版',
    icon: 'SetUp',
    hasChildren: true,
    children: [
      { id: 'cat_prep_1', name: '试剂原料信息', parentId: 'cat_preparation' },
      { id: 'cat_prep_2', name: '制备工艺信息', parentId: 'cat_preparation' }
    ]
  },
  {
    id: 'cat_physical',
    name: '理化及力学性能',
    description: '材料理化及力学性能表征相关模版',
    icon: 'DataLine',
    hasChildren: true,
    children: [
      { id: 'cat_phy_1', name: '表征信息', parentId: 'cat_physical' },
      { id: 'cat_phy_2', name: '表征原始数据', parentId: 'cat_physical' },
      { id: 'cat_phy_3', name: '表征衍生数据', parentId: 'cat_physical' }
    ]
  },
  {
    id: 'cat_invitro',
    name: '体外生物学评价',
    description: '体外生物学评价相关模版',
    icon: 'FirstAidKit',
    hasChildren: true,
    children: [
      { id: 'cat_invitro_1', name: '试剂原料信息', parentId: 'cat_invitro' },
      { id: 'cat_invitro_2', name: '评价信息', parentId: 'cat_invitro' },
      { id: 'cat_invitro_3', name: '评价原始数据', parentId: 'cat_invitro' },
      { id: 'cat_invitro_4', name: '评价衍生数据', parentId: 'cat_invitro' }
    ]
  },
  {
    id: 'cat_animal',
    name: '动物实验评价',
    description: '动物实验评价相关模版',
    icon: 'Aim',
    hasChildren: true,
    children: [
      { id: 'cat_animal_1', name: '试剂原料信息', parentId: 'cat_animal' },
      { id: 'cat_animal_2', name: '评价信息', parentId: 'cat_animal' },
      { id: 'cat_animal_3', name: '评价原始数据', parentId: 'cat_animal' },
      { id: 'cat_animal_4', name: '评价衍生数据', parentId: 'cat_animal' }
    ]
  },
  {
    id: 'cat_clinical',
    name: '临床试验及应用',
    description: '临床试验及应用相关模版',
    icon: 'User',
    hasChildren: true,
    children: [
      { id: 'cat_clinical_1', name: '产品患者信息', parentId: 'cat_clinical' },
      { id: 'cat_clinical_2', name: '评价信息', parentId: 'cat_clinical' },
      { id: 'cat_clinical_3', name: '评价原始数据', parentId: 'cat_clinical' },
      { id: 'cat_clinical_4', name: '评价衍生数据', parentId: 'cat_clinical' }
    ]
  },
  {
    id: 'cat_review',
    name: '审评及监管',
    description: '审评及监管相关模版',
    icon: 'Checked',
    hasChildren: true,
    children: [
      { id: 'cat_review_1', name: '产品信息', parentId: 'cat_review' },
      { id: 'cat_review_2', name: '评价信息', parentId: 'cat_review' },
      { id: 'cat_review_3', name: '评价原始数据', parentId: 'cat_review' },
      { id: 'cat_review_4', name: '评价衍生数据', parentId: 'cat_review' }
    ]
  }
]

// 将分类转换为树形结构（用于el-tree组件）
export const getCategoryTree = () => {
  return templateCategories.map(cat => ({
    id: cat.id,
    name: cat.name,
    description: cat.description,
    icon: cat.icon,
    hasChildren: cat.hasChildren,
    children: cat.children.length > 0 ? cat.children.map(sub => ({
      id: sub.id,
      name: sub.name,
      parentId: sub.parentId
    })) : undefined
  }))
}

// 获取大目录列表（用于下拉选择）
export const getBigCategories = () => {
  return templateCategories.map(cat => ({
    id: cat.id,
    name: cat.name,
    hasChildren: cat.hasChildren
  }))
}

// 根据大目录ID获取子目录
export const getSubCategories = (bigCategoryId) => {
  const category = templateCategories.find(cat => cat.id === bigCategoryId)
  return category ? category.children : []
}

// 根据ID查找分类信息
export const findCategoryById = (id) => {
  // 先在大目录中查找
  const bigCat = templateCategories.find(cat => cat.id === id)
  if (bigCat) {
    return { ...bigCat, isBigCategory: true }
  }
  
  // 在子目录中查找
  for (const cat of templateCategories) {
    const subCat = cat.children.find(sub => sub.id === id)
    if (subCat) {
      return { 
        ...subCat, 
        isBigCategory: false,
        parentName: cat.name 
      }
    }
  }
  
  return null
}

// 获取分类路径（用于面包屑显示）
export const getCategoryPath = (categoryId) => {
  const category = findCategoryById(categoryId)
  if (!category) return ''
  
  if (category.isBigCategory) {
    return category.name
  }
  
  return `${category.parentName} / ${category.name}`
}

// 默认展开的分类ID
export const defaultExpandedKeys = ['cat_basic', 'cat_design']

// 分类ID到数字ID的映射
// 材料基本信息=1, 从计算对象开始ID从9开始，其他依次递增
const categoryIdToNumericId = {
  // 材料基本信息
  'cat_basic': 1,
  // 理性设计与预测
  'cat_design_1': 9,   // 计算对象
  'cat_design_2': 10,  // 计算模型参数
  'cat_design_3': 11,  // 计算结果
  // 制备与加工
  'cat_prep_1': 12,    // 试剂原料信息
  'cat_prep_2': 13,    // 制备工艺信息
  // 理化及力学性能
  'cat_phy_1': 14,     // 表征信息
  'cat_phy_2': 15,     // 表征原始数据
  'cat_phy_3': 16,     // 表征衍生数据
  // 体外生物学评价
  'cat_invitro_1': 17, // 试剂原料信息
  'cat_invitro_2': 18, // 评价信息
  'cat_invitro_3': 19, // 评价原始数据
  'cat_invitro_4': 20, // 评价衍生数据
  // 动物实验评价
  'cat_animal_1': 21,  // 试剂原料信息
  'cat_animal_2': 22,  // 评价信息
  'cat_animal_3': 23,  // 评价原始数据
  'cat_animal_4': 24,  // 评价衍生数据
  // 临床试验及应用
  'cat_clinical_1': 25, // 产品患者信息
  'cat_clinical_2': 26, // 评价信息
  'cat_clinical_3': 27, // 评价原始数据
  'cat_clinical_4': 28, // 评价衍生数据
  // 审评及监管
  'cat_review_1': 29,   // 产品信息
  'cat_review_2': 30,   // 评价信息
  'cat_review_3': 31,   // 评价原始数据
  'cat_review_4': 32    // 评价衍生数据
}

/**
 * 将分类ID转换为数字ID
 * @param {string} categoryId - 分类ID（如 'cat_basic', 'cat_design_1'）
 * @returns {number} 数字ID，如果找不到则返回 0
 */
export const getNumericCategoryId = (categoryId) => {
  if (!categoryId) return 0
  return categoryIdToNumericId[categoryId] || 0
}

export default {
  templateCategories,
  getCategoryTree,
  getBigCategories,
  getSubCategories,
  findCategoryById,
  getCategoryPath,
  getNumericCategoryId,
  defaultExpandedKeys
}
