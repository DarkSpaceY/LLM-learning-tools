import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 知识点解析API
export const parseKnowledge = (content) => {
  return api.post('/tools/knowledge-parser/parse', { content })
}

// 练习题生成API
export const generateExercises = (params) => {
  return api.post('/tools/exercise-generator/generate', params)
}

// 资源搜索API
export const searchResources = (params) => {
  return api.post('/api/resources/search', params)
}

// 学习计划生成API
export const generateLearningPlan = (params) => {
  return api.post('/tools/learning-planner/generate', params)
}

// 概念分析API
export const analyzeConceptMap = (params) => {
  return api.post('/tools/concept-analyzer/analyze', params)
}

// 仿真环境创建API
export const buildSimulation = (params) => {
  return api.post('/tools/simulation-builder/build', params)
}

// 对话API
export const streamDialogue = (params) => {
  const { sessionId, message, model } = params
  return `/dialogue/stream?session_id=${sessionId}&message=${encodeURIComponent(message)}&model=${model}`
}

// 资源收藏API
export const saveResource = (resourceId) => {
  return api.post('/tools/resource-searcher/save', { resource_id: resourceId })
}

// 资源分享API
export const shareResource = (resourceId) => {
  return api.post('/tools/resource-searcher/share', { resource_id: resourceId })
}

// 教程相关API
export const tutorialApi = {
  // 获取教程列表
  getList: () => api.get('/tutorials/list'),
  // 获取教程内容
  getContent: (fileId) => api.get(`/tutorials/${fileId}`),
  // 保存教程
  save: (params) => api.post('/tutorials/save', params)
}

// 知识图谱相关API
export const knowledgeGraphApi = {
  // 获取图谱列表
  getList: () => api.get('/knowledge_graph/list'),
  // 获取图谱内容
  getContent: (filename) => api.get(`/knowledge_graph/${filename}`),
  // 保存图谱
  save: (params) => api.post('/knowledge_graph/save', params),
  // 生成图谱
  generate: (params) => api.post('/knowledge_graph/generate', params),
  // 扩展图谱
  expand: (params) => api.post('/knowledge_graph/expand', params)
}

// 设置相关API
export const settingsApi = {
  // 获取设置
  get: () => api.get('/settings'),
  // 更新设置
  update: (params) => api.post('/settings', params)
}

export default api