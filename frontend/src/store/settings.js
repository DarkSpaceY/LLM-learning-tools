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
    '教程':'教程',

    // 仿真构建器
    '仿真构建器': '仿真构建器',
    '创建交互式学习仿真，可视化复杂概念和过程': '创建交互式学习仿真，可视化复杂概念和过程',
    '模型交互': '模型交互',
    '仿真名称': '仿真名称',
    '请输入仿真名称': '请输入仿真名称',
    '代码生成提示': '代码生成提示',
    '请描述您想要生成的仿真代码，例如：创建一个弹簧振子模型，或者绘制二次函数及其导数': '请描述您想要生成的仿真代码，例如：创建一个弹簧振子模型，或者绘制二次函数及其导数',
    '从文件导入': '从文件导入',
    '选择文件': '选择文件',
    '支持 .txt, .js, .html 文件': '支持 .txt, .js, .html 文件',
    '构建仿真': '构建仿真',
    '生成的代码': '生成的代码',
    '执行代码': '执行代码',
    '编辑代码': '编辑代码',

    // 资源搜索器
    '学习资源搜索器': '学习资源搜索器',
    '智能搜索优质学习资源，提供评分和标签分类': '智能搜索优质学习资源，提供评分和标签分类',
    '搜索关键词': '搜索关键词',
    '请输入要搜索的关键词': '请输入要搜索的关键词',
    '搜索': '搜索',
    '资源类型': '资源类型',
    '搜索结果': '搜索结果',
    '共找到 {0} 个资源': '共找到 {0} 个资源',

    // 知识点解析器
    '文章知识点解析器': '文章知识点解析器',
    '从文章中提取并解析知识点结构、关联和应用': '从文章中提取并解析知识点结构、关联和应用',
    '文章内容': '文章内容',
    '请输入或粘贴要解析的文章内容': '请输入或粘贴要解析的文章内容',
    '开始解析': '开始解析',

    // 练习题生成器
    '练习题生成器': '练习题生成器',
    '根据知识点智能生成练习题，提供详细解析和答案': '根据知识点智能生成练习题，提供详细解析和答案',
    '知识点': '知识点',
    '请输入知识点名称': '请输入知识点名称',
    '题目类型': '题目类型',
    '请选择题目类型': '请选择题目类型',
    '难度等级': '难度等级',
    '生成数量': '生成数量',
    '生成练习题': '生成练习题',
    '生成的练习题': '生成的练习题',
    '导出练习题': '导出练习题',
    '题目': '题目',

    // 概念分析器
    '概念分析器': '概念分析器',
    '深入分析概念的定义、特征和关联关系': '深入分析概念的定义、特征和关联关系',
    '概念名称': '概念名称',
    '请输入要分析的概念名称': '请输入要分析的概念名称',
    '开始分析': '开始分析',
    '核心特征': '核心特征',
    '典型示例': '典型示例',
    '概念关系网络': '概念关系网络',
    '应用场景': '应用场景',
    '暂无定义': '暂无定义',
    '暂无核心特征数据': '暂无核心特征数据',
    '暂无典型示例数据': '暂无典型示例数据',
    '暂无概念关系网络数据': '暂无概念关系网络数据',
    '暂无应用场景数据': '暂无应用场景数据',
    '中心概念': '中心概念',
    '相关概念': '相关概念',
    '子类': '子类',
    '组成关系': '组成关系',
    '相关': '相关',
    '应用': '应用',
    
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
    '发生错误，请稍后重试': '发生错误，请稍后重试',
    '请求失败': '请求失败',
    
    // 工具页面
    '学习工具箱': '学习工具箱',
    
    // HomeView和TutorialView
    '学习大纲': '学习大纲',
    '查看内容': '查看内容',
    '请从左侧选择要查看的内容': '请从左侧选择要查看的内容',
    '选择教程文件': '选择教程文件',
    '请选择教程文件': '请选择教程文件',
    '教程目录': '教程目录',
    '删除确认': '删除确认',
    '确定要删除这个教程吗？此操作不可恢复。': '确定要删除这个教程吗？此操作不可恢复。',
    '教程删除成功': '教程删除成功',
    '删除教程失败': '删除教程失败',
    '加载教程失败': '加载教程失败',
    '加载教程列表失败': '加载教程列表失败',
    '搜索工具': '搜索工具',
    '全部': '全部',
    '分析工具': '分析工具',
    '学习工具': '学习工具',
    '练习工具': '练习工具',
    '使用': '使用',
    '知识点解析器': '知识点解析器',
    '解析文本中的关键知识点，标注重要程度和难度': '解析文本中的关键知识点，标注重要程度和难度',
    '练习题生成器': '练习题生成器',
    '根据主题智能生成各类型练习题，包含详细解析': '根据主题智能生成各类型练习题，包含详细解析',
    '学习资源搜索器': '学习资源搜索器',
    '搜索并推荐优质学习资源，包含评分和标签': '搜索并推荐优质学习资源，包含评分和标签',
    '概念分析器': '概念分析器',
    '深入分析和解释复杂概念，提供详细的理解框架': '深入分析和解释复杂概念，提供详细的理解框架',
    '仿真构建器': '仿真构建器',
    '构建和运行仿真实验，提供交互式学习体验': '构建和运行仿真实验，提供交互式学习体验',
    
    // 知识图谱页面
    '输入初始知识点': '输入初始知识点',
    '生成': '生成',
    '知识点描述（可选）': '知识点描述（可选）',
    '导出': '导出',
    '导入': '导入',
    '重置': '重置',
    '导入知识图谱': '导入知识图谱',
    '主题': '主题',
    '创建时间': '创建时间',
    '操作': '操作',
    '加载': '加载',
    '删除': '删除',
    '节点信息': '节点信息',
    '类别': '类别',
    '拓展该节点': '拓展该节点',
    '点击可查看详情': '点击可查看详情',
    '可继续拓展该知识点': '可继续拓展该知识点',
    '从': '从',
    '到': '到',
    '入门': '入门',
    '基础': '基础',
    '进阶': '进阶',
    '挑战': '挑战',
    '专家': '专家',
    '视频教程': '视频教程',
    "文章": "文章",
    "文档": "文档",
    "在线课程": "在线课程",
    '电子书': 'E-电子书',
    '工具': '工具'
  },
  'en-US': {
    // Navigation
    '对话': 'Chat',
    '知识图谱': 'Knowledge Map',
    '工具箱': 'Tools',
    '设置': 'Settings',
    '教程':'Tutorials',
    // HomeView和TutorialView
    '学习大纲': 'Learning Outline',
    '查看内容': 'View Content',
    '请从左侧选择要查看的内容': 'Please select content from the left panel',
    '选择教程文件': 'Select Tutorial File',
    '请选择教程文件': 'Please select a tutorial file',
    '教程目录': 'Tutorial Contents',
    '删除确认': 'Delete Confirmation',
    '确定要删除这个教程吗？此操作不可恢复。': 'Are you sure you want to delete this tutorial? This action cannot be undone.',
    '教程删除成功': 'Tutorial deleted successfully',
    '删除教程失败': 'Failed to delete tutorial',
    '加载教程失败': 'Failed to load tutorial',
    '加载教程列表失败': 'Failed to load tutorial list',
    // Simulation Builder
    '仿真构建器': 'Simulation Builder',
    '创建交互式学习仿真，可视化复杂概念和过程': 'Create interactive learning simulations to visualize complex concepts and processes',
    '模型交互': 'Model Interaction',
    '仿真名称': 'Simulation Name',
    '请输入仿真名称': 'Please enter simulation name',
    '代码生成提示': 'Code Generation Prompt',
    '请描述您想要生成的仿真代码，例如：创建一个弹簧振子模型，或者绘制二次函数及其导数': 'Please describe the simulation code you want to generate, e.g.: create a spring oscillator model, or plot a quadratic function and its derivative',
    '从文件导入': 'Import from File',
    '选择文件': 'Choose File',
    '支持 .txt, .js, .html 文件': 'Supports .txt, .js, .html files',
    '构建仿真': 'Build Simulation',
    '生成的代码': 'Generated Code',
    '执行代码': 'Execute Code',
    '编辑代码': 'Edit Code',

    // Resource Searcher
    '学习资源搜索器': 'Learning Resource Searcher',
    '智能搜索优质学习资源，提供评分和标签分类': 'Intelligently search for quality learning resources with ratings and tags',
    '搜索关键词': 'Search Keywords',
    '请输入要搜索的关键词': 'Please enter keywords to search',
    '搜索': 'Search',
    '资源类型': 'Resource Type',
    '搜索结果': 'Search Results',
    '共找到 {0} 个资源': 'Found {0} resources',

    // Knowledge Parser
    '文章知识点解析器': 'Article Knowledge Parser',
    '从文章中提取并解析知识点结构、关联和应用': 'Extract and analyze knowledge points structure, relationships and applications from articles',
    '文章内容': 'Article Content',
    '请输入或粘贴要解析的文章内容': 'Please enter or paste the article content to analyze',
    '开始解析': 'Start Analysis',

    // Exercise Generator
    '练习题生成器': 'Exercise Generator',
    '根据知识点智能生成练习题，提供详细解析和答案': 'Generate exercises intelligently based on knowledge points with detailed explanations and answers',
    '知识点': 'Knowledge Point',
    '请输入知识点名称': 'Please enter the knowledge point name',
    '题目类型': 'Question Type',
    '请选择题目类型': 'Please select question types',
    '难度等级': 'Difficulty Level',
    '生成数量': 'Number of Questions',
    '生成练习题': 'Generate Exercises',
    '生成的练习题': 'Generated Exercises',
    '导出练习题': 'Export Exercises',
    '题目': 'Question',

    // Concept Analyzer
    '概念分析器': 'Concept Analyzer',
    '深入分析概念的定义、特征和关联关系': 'Analyze concept definitions, features and relationships in depth',
    '概念名称': 'Concept Name',
    '请输入要分析的概念名称': 'Please enter the concept name to analyze',
    '开始分析': 'Start Analysis',
    '核心特征': 'Core Features',
    '典型示例': 'Typical Examples',
    '概念关系网络': 'Concept Relationship Network',
    '应用场景': 'Application Scenarios',
    '暂无定义': 'No definition available',
    '暂无核心特征数据': 'No core features data available',
    '暂无典型示例数据': 'No typical examples available',
    '暂无概念关系网络数据': 'No concept relationship network data available',
    '暂无应用场景数据': 'No application scenarios available',
    '中心概念': 'Central Concept',
    '相关概念': 'Related Concepts',
    '子类': 'Subclass',
    '组成关系': 'Composition',
    '相关': 'Related',
    '应用': 'Application',
    
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
    '发生错误，请稍后重试': 'An error occurred. Please try again later.',
    '请求失败': 'Request failed',
    
    // Tools page
    '学习工具箱': 'Learning Toolbox',
    '搜索工具': 'Search Tools',
    '全部': 'All',
    '分析工具': 'Analysis Tools',
    '学习工具': 'Learning Tools',
    '练习工具': 'Practice Tools',
    '使用': 'Use',
    '知识点解析器': 'Knowledge Point Parser',
    '解析文本中的关键知识点，标注重要程度和难度': 'Parse key knowledge points from text, mark importance and difficulty',
    '练习题生成器': 'Exercise Generator',
    '根据主题智能生成各类型练习题，包含详细解析': 'Generate various types of exercises based on topics, with detailed analysis',
    '学习资源搜索器': 'Learning Resource Searcher',
    '搜索并推荐优质学习资源，包含评分和标签': 'Search and recommend quality learning resources with ratings and tags',
    '概念分析器': 'Concept Analyzer',
    '深入分析和解释复杂概念，提供详细的理解框架': 'Deeply analyze and explain complex concepts with detailed understanding framework',
    '仿真构建器': 'Simulation Builder',
    '构建和运行仿真实验，提供交互式学习体验': 'Build and run simulation experiments to provide interactive learning experiences',
    
    // Knowledge map page
    '输入初始知识点': 'Enter initial knowledge point',
    '生成': 'Generate',
    '知识点描述（可选）': 'Knowledge point description (optional)',
    '导出': 'Export',
    '导入': 'Import',
    '重置': 'Reset',
    '导入知识图谱': 'Import Knowledge Map',
    '主题': 'Topic',
    '创建时间': 'Created At',
    '操作': 'Actions',
    '加载': 'Load',
    '删除': 'Delete',
    '节点信息': 'Node Info',
    '类别': 'Category',
    '拓展该节点': 'Expand Node',
    '点击可查看详情': 'Click to view details',
    '可继续拓展该知识点': 'Can expand this knowledge point',
    '从': 'From',
    '到': 'To',
    '入门': 'Getting Started',
    '基础': 'Basic',
    '进阶': 'Advanced',
    '挑战': 'Challenges',
    '专家': 'Experts',
    "文章": "Article",
    "文档": "Document",
    '视频教程': 'Video',
    "在线课程": "Online Course",
    '电子书': 'E-book',
    '工具': 'Tool'
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