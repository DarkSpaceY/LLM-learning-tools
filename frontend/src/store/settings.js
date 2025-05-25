import { ref } from 'vue'
import { eventBus, Events } from '../utils/eventBus'

// 语言翻译
export const translations = {
  'zh-CN': {
    // 导航
    '对话': '对话',
    '知识图谱': '知识图谱',
    '工具箱': '工具箱',
    '设置': '设置',
    
    // 设置页面
    '刷新': '刷新',
    '刷新中...': '刷新中...',
    '保存设置': '保存设置',
    '保存中...': '保存中...',
    'AI模型': 'AI模型',
    '界面设置': '界面设置',
    '主题': '主题',
    '浅色': '浅色',
    '深色': '深色',
    '跟随系统': '跟随系统',
    '语言': '语言',
    '设置保存成功！': '设置保存成功！',
    '保存设置失败：': '保存设置失败：',
    
    // 对话页面
    '发送': '发送',
    '生成中...': '生成中...',
    '请输入您想学习的主题...': '请输入您想学习的主题...',
    '👋 你好！我是你的AI学习助手。请告诉我你想学习的主题，我会为你规划详细的学习路径，并推荐相关的学习资源。': '👋 你好！我是你的AI学习助手。请告诉我你想学习的主题，我会为你规划详细的学习路径，并推荐相关的学习资源。',
    '发生错误，请稍后重试': '发生错误，请稍后重试',
    '请求失败': '请求失败',
    
    // 工具页面
    '使用工具': '使用工具',
    '知识点解析': '知识点解析',
    '从文本中提取关键知识点': '从文本中提取关键知识点',
    '习题生成': '习题生成',
    '生成练习题和测试': '生成练习题和测试',
    '知识搜索': '知识搜索',
    '搜索相关学习资源': '搜索相关学习资源',
    
    // 知识图谱页面
    '输入学习主题...': '输入学习主题...',
    '加载中...': '加载中...',
    '搜索': '搜索'
  },
  'en-US': {
    // Navigation
    '对话': 'Chat',
    '知识图谱': 'Knowledge Map',
    '工具箱': 'Tools',
    '设置': 'Settings',
    
    // Settings page
    '刷新': 'Refresh',
    '刷新中...': 'Refreshing...',
    '保存设置': 'Save Settings',
    '保存中...': 'Saving...',
    'AI模型': 'AI Model',
    '界面设置': 'Interface',
    '主题': 'Theme',
    '浅色': 'Light',
    '深色': 'Dark',
    '跟随系统': 'System',
    '语言': 'Language',
    '设置保存成功！': 'Settings saved successfully!',
    '保存设置失败：': 'Failed to save settings: ',
    
    // Chat page
    '发送': 'Send',
    '生成中...': 'Generating...',
    '请输入您想学习的主题...': 'Enter a topic you want to learn...',
    '👋 你好！我是你的AI学习助手。请告诉我你想学习的主题，我会为你规划详细的学习路径，并推荐相关的学习资源。': '👋 Hi! I am your AI learning assistant. Please tell me what topic you want to learn, and I will plan a detailed learning path and recommend relevant resources.',
    '发生错误，请稍后重试': 'An error occurred. Please try again later.',
    '请求失败': 'Request failed',
    
    // Tools page
    '使用工具': 'Use Tool',
    '知识点解析': 'Knowledge Analysis',
    '从文本中提取关键知识点': 'Extract key knowledge points from text',
    '习题生成': 'Exercise Generator',
    '生成练习题和测试': 'Generate exercises and tests',
    '知识搜索': 'Knowledge Search',
    '搜索相关学习资源': 'Search related learning resources',
    
    // Knowledge map page
    '输入学习主题...': 'Enter learning topic...',
    '加载中...': 'Loading...',
    '搜索': 'Search'
  }
}

// CSS变量定义
const themes = {
  light: {
    // 基础颜色
    '--bg-color': '#ffffff',
    '--text-color': '#353740',
    '--border-color': 'rgba(0, 0, 0, 0.1)',
    '--shadow-color': 'rgba(0, 0, 0, 0.05)',
    '--primary-color': '#10a37f',
    '--primary-hover-color': '#0d8c6d',
    '--disabled-color': 'rgba(16, 163, 127, 0.5)',
    
    // 导航栏
    '--nav-bg': '#f7f7f8',
    '--hover-color': 'rgba(16, 163, 127, 0.05)',
    
    // 消息气泡
    '--message-bg': '#f7f7f8',
    '--error-bg': '#fff2f2',
    '--error-color': '#ff4081',
    '--code-bg': '#f7f7f8',
    '--code-color': '#353740',
    '--blockquote-color': '#666666',
    '--link-color': '#10a37f',
    
    // 其他
    '--placeholder-color': 'rgba(53, 55, 64, 0.5)',
    '--primary-shadow': 'rgba(16, 163, 127, 0.1)',
    '--gradient-bg': 'linear-gradient(45deg, rgba(16, 163, 127, 0.05) 0%, rgba(16, 163, 127, 0) 100%)'
  },
  dark: {
    // 基础颜色
    '--bg-color': '#1a1b1e',
    '--text-color': '#e0e1e6',
    '--border-color': 'rgba(255, 255, 255, 0.1)',
    '--shadow-color': 'rgba(0, 0, 0, 0.2)',
    '--primary-color': '#10a37f',
    '--primary-hover-color': '#0d8c6d',
    '--disabled-color': 'rgba(16, 163, 127, 0.5)',
    
    // 导航栏
    '--nav-bg': '#2c2d30',
    '--hover-color': 'rgba(16, 163, 127, 0.15)',
    
    // 消息气泡
    '--message-bg': '#2c2d30',
    '--error-bg': '#461c24',
    '--error-color': '#ff4081',
    '--code-bg': '#2c2d30',
    '--code-color': '#e0e1e6',
    '--blockquote-color': '#a0a1a7',
    '--link-color': '#10a37f',
    
    // 其他
    '--placeholder-color': 'rgba(224, 225, 230, 0.5)',
    '--primary-shadow': 'rgba(16, 163, 127, 0.2)',
    '--gradient-bg': 'linear-gradient(45deg, rgba(16, 163, 127, 0.1) 0%, rgba(16, 163, 127, 0) 100%)'
  }
}

// 创建一个响应式的设置存储
const settings = ref({
  theme: 'light',
  language: 'zh-CN',
  default_model: 'deepseek-r1:8b'
})

// 翻译函数
export const t = (key) => translations[settings.value.language]?.[key] || key

// 加载设置
export const loadSettings = async () => {
  try {
    const response = await fetch('/api/settings')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const result = await response.json()
    if (result.success) {
      settings.value = {
        theme: result.data?.theme || 'light',
        language: result.data?.language || 'zh-CN',
        default_model: result.data?.default_model || 'deepseek-r1:8b'
      }
      applyTheme(settings.value.theme)
    }
  } catch (error) {
    console.error('Error loading settings:', error)
    // 设置默认值
    settings.value = {
      theme: 'light',
      language: 'zh-CN',
      default_model: 'deepseek-r1:8b'
    }
    applyTheme('light')
    // 使用Element Plus的消息提示
    if (window.ElMessage) {
      window.ElMessage.error(t('设置加载失败，已使用默认配置'))
    }
  }
}

// 应用主题
export const applyTheme = (theme) => {
  const themeVars = themes[theme] || themes.light
  Object.entries(themeVars).forEach(([key, value]) => {
    document.documentElement.style.setProperty(key, value)
  })
  document.documentElement.setAttribute('data-theme', theme)
}

// 监听设置变更
eventBus.on(Events.THEME_CHANGE, (theme) => {
  settings.value.theme = theme
  applyTheme(theme)
})

eventBus.on(Events.LANGUAGE_CHANGE, (language) => {
  settings.value.language = language
})

eventBus.on(Events.SETTINGS_UPDATED, (newSettings) => {
  settings.value = {
    ...settings.value,
    ...newSettings
  }
  applyTheme(newSettings.theme)
})

// 导出设置存储
export const useSettings = () => settings

// 初始加载设置
loadSettings()