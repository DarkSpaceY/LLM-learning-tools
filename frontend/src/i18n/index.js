import { createI18n } from 'vue-i18n'

const messages = {
  zh: {
    '文章知识点解析器': '文章知识点解析器',
    '从文章中提取并解析知识点结构、关联和应用': '从文章中提取并解析知识点结构、关联和应用',
    '文章内容': '文章内容',
    '请输入或粘贴要解析的文章内容': '请输入或粘贴要解析的文章内容',
    '开始解析': '开始解析',
    '重置': '重置',
    '知识点': '知识点',
    '难度': '难度',
    '重要性': '重要性',
    '概述': '概述',
    '相关概念': '相关概念',
    '前置知识': '前置知识',
    '示例': '示例',
    '关键要点': '关键要点',
    'low': '低',
    'intermediate': '中等',
    'high': '高',
    'medium': '中等'
  },
  en: {
    '文章知识点解析器': 'Article Knowledge Parser',
    '从文章中提取并解析知识点结构、关联和应用': 'Extract and analyze knowledge structure, relationships and applications from articles',
    '文章内容': 'Article Content',
    '请输入或粘贴要解析的文章内容': 'Please enter or paste the article content to analyze',
    '开始解析': 'Start Analysis',
    '重置': 'Reset',
    '知识点': 'Knowledge Point',
    '难度': 'Difficulty',
    '重要性': 'Importance',
    '概述': 'Overview',
    '相关概念': 'Related Concepts',
    '前置知识': 'Prerequisites',
    '示例': 'Examples',
    '关键要点': 'Key Points',
    'low': 'Low',
    'intermediate': 'Intermediate',
    'high': 'High',
    'medium': 'Medium'
  }
}

const i18n = createI18n({
  legacy: false,
  locale: 'zh',
  fallbackLocale: 'en',
  messages
})

export default i18n