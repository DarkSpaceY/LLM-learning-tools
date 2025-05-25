<template>
  <div class="settings-container">
    <div class="settings-content">
      <div class="settings-header">
        <h1>{{ t('设置') }}</h1>
        <div class="header-actions">
          <button class="refresh-button" @click="refreshSettings" :disabled="isRefreshing">
            <i class="fas fa-sync" :class="{ 'fa-spin': isRefreshing }"></i>
            {{ isRefreshing ? t('刷新中...') : t('刷新') }}
          </button>
          <button class="save-button" @click="saveAllSettings" :disabled="isSaving">
            <i class="fas fa-save"></i>
            {{ isSaving ? t('保存中...') : t('保存设置') }}
          </button>
        </div>
      </div>

      <div class="settings-section">
        <h2>{{ t('AI模型') }}</h2>
        <div class="setting-item">
          <label>
            {{ t('LLM提供商') }}
            <select v-model="pendingSettings.default_provider" @change="handleProviderChange">
              <option value="ollama">Ollama (本地)</option>
              <option value="deepseek">DeepSeek</option>
              <option value="openai">OpenAI</option>
              <option value="openrouter">OpenRouter</option>
            </select>
          </label>
        </div>
        
        <div class="setting-item" v-if="pendingSettings.default_provider !== 'ollama'">
          <label>
            {{ t('API密钥') }}
            <div class="api-key-input-container">
              <input 
                type="password" 
                v-model="providerConfig.api_key"
                :placeholder="t('请输入API密钥')"
                @input="handleApiKeyChange"
              >
              <div class="api-key-error" v-if="pendingSettings.default_provider === 'openai' && !providerConfig.api_key">
                {{ t('请输入OpenAI API密钥以加载可用模型') }}
              </div>
            </div>
          </label>
        </div>

        <div class="setting-item">
          <label>
            {{ t('API地址') }}
            <input 
              type="text" 
              v-model="providerConfig.base_url"
              :placeholder="t('请输入API地址')"
            >
          </label>
        </div>

        <div class="model-search">
          <input
            type="text"
            v-model="searchQuery"
            :placeholder="t('搜索模型')"
            class="search-input"
          >
        </div>

        <div class="model-list">
          <div v-for="model in filteredModels" :key="model.id" class="model-item">
            <label class="model-label">
              <input
                type="radio"
                :value="model.id"
                v-model="providerConfig.model_name"
                name="model"
              >
              <div class="model-info">
                <span class="model-name">{{ model.name }}</span>
                <span class="model-type">{{ model.type }}</span>
                <span class="model-description">{{ model.description }}</span>
              </div>
            </label>
          </div>
        </div>

        <div class="pagination" v-if="totalPages > 1">
          <button 
            @click="currentPage--" 
            :disabled="currentPage === 1"
            class="page-button"
          >
            <i class="fas fa-chevron-left"></i>
          </button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button 
            @click="currentPage++" 
            :disabled="currentPage === totalPages"
            class="page-button"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>

        <div class="setting-item">
          <label>
            {{ t('温度') }}
            <input 
              type="range" 
              v-model.number="providerConfig.temperature"
              min="0" 
              max="1" 
              step="0.1"
            >
            <span class="value-display">{{ providerConfig.temperature }}</span>
          </label>
        </div>

        <div class="setting-item">
          <label>
            {{ t('最大Token数') }}
            <input 
              type="number" 
              v-model.number="providerConfig.max_tokens"
              min="1" 
              max="8192"
            >
          </label>
        </div>
      </div>

      <div class="settings-section">
        <h2>{{ t('界面设置') }}</h2>
        <div class="setting-item">
          <label>
            {{ t('主题') }}
            <select 
              v-model="pendingSettings.theme"
              @change="handleThemeChange"
            >
              <option value="light">{{ t('浅色') }}</option>
              <option value="dark">{{ t('深色') }}</option>
              <option value="system">{{ t('跟随系统') }}</option>
            </select>
          </label>
        </div>
        <div class="setting-item">
          <label>
            {{ t('语言') }}
            <select 
              v-model="pendingSettings.language"
              @change="handleLanguageChange"
            >
              <option value="zh-CN">简体中文</option>
              <option value="en-US">English</option>
            </select>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { eventBus, Events } from '../utils/eventBus'

// i18n翻译
const translations = {
  'zh-CN': {
    '设置': '设置',
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
    '请输入OpenAI API密钥以加载可用模型': '请输入OpenAI API密钥以加载可用模型',
    '请输入API密钥': '请输入API密钥',
    '获取模型列表失败': '获取模型列表失败',
    '无效的API响应格式': '无效的API响应格式',
    '加载模型列表时出错：': '加载模型列表时出错：'
  },
  'en-US': {
    '设置': 'Settings',
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
    '请输入OpenAI API密钥以加载可用模型': 'Please enter OpenAI API key to load available models',
    '请输入API密钥': 'Please enter API key',
    '获取模型列表失败': 'Failed to fetch model list',
    '无效的API响应格式': 'Invalid API response format',
    '加载模型列表时出错：': 'Error loading model list: '
  }
}

const currentLanguage = ref('zh-CN')
const t = (key) => translations[currentLanguage.value]?.[key] || key

const availableModels = ref([])
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(5)

const pendingSettings = ref({
  default_provider: 'ollama',
  theme: 'light',
  language: 'zh-CN'
})

// 根据搜索和分页过滤模型列表
const filteredModels = computed(() => {
  const query = searchQuery.value.toLowerCase()
  const filtered = availableModels.value.filter(model => 
    model.name.toLowerCase().includes(query) ||
    model.description.toLowerCase().includes(query)
  )
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

// 计算总页数
const totalPages = computed(() => {
  const query = searchQuery.value.toLowerCase()
  const filtered = availableModels.value.filter(model => 
    model.name.toLowerCase().includes(query) ||
    model.description.toLowerCase().includes(query)
  )
  return Math.ceil(filtered.length / pageSize.value)
})

const providerConfig = ref({
  api_key: '',
  base_url: 'http://localhost:11434',
  model_name: 'deepseek-r1:8b',
  temperature: 0.7,
  max_tokens: 1024
})

const isRefreshing = ref(false)
const isSaving = ref(false)

const loadModels = async () => {
  try {
    const provider = pendingSettings.value.default_provider
    let models = []
    
    if (provider === 'ollama') {
      const ollamaResponse = await fetch('http://localhost:11434/api/tags')
      const ollamaData = await ollamaResponse.json()
      models = ollamaData.models.map(model => ({
        id: model.name,
        name: model.name.charAt(0).toUpperCase() + model.name.slice(1),
        type: 'Chat',
        description: `${model.name} ${model.size} 本地模型`
      }))
    } else if (provider === 'openrouter') {
      // 从OpenRouter API获取模型列表
      const response = await fetch('https://openrouter.ai/api/v1/models', {
        headers: {
          'HTTP-Referer': 'https://github.com/OpenRouterTeam/openrouter-python',
          'X-Title': 'AI Education Frontend',
          'Authorization': `Bearer ${providerConfig.value.api_key}`,
          'Content-Type': 'application/json'
        }
      })
      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.message || '获取模型列表失败')
      }
      if (!data.data || !Array.isArray(data.data)) {
        throw new Error('无效的API响应格式')
      }
      models = data.data.map(model => ({
        id: model.id,
        name: model.name,
        type: 'Chat',
        description: model.description || `OpenRouter - ${model.name}`
      }))
    } else if (provider === 'openai') {
      // 从OpenAI API获取模型列表
      const response = await fetch(`${providerConfig.value.base_url}/models`, {
        headers: {
          'Authorization': `Bearer ${providerConfig.value.api_key}`,
          'Content-Type': 'application/json'
        }
      })
      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.error?.message || '获取模型列表失败')
      }
      models = data.data
        .filter(model => model.id.includes('gpt'))
        .map(model => ({
          id: model.id,
          name: model.id,
          type: 'Chat',
          description: `OpenAI - ${model.id}`
        }))
    } else {
      // 其他提供商使用默认配置中的模型列表
      models = defaultConfigs[provider]?.models || []
    }
    
    availableModels.value = models
  } catch (error) {
    console.error('Error loading models:', error)
    // 加载失败时使用默认配置
    availableModels.value = defaultConfigs[pendingSettings.value.default_provider]?.models || []
  }
}

const loadSettings = async () => {
  try {
    const response = await fetch('/api/settings')
    const result = await response.json()
    if (result.success) {
      // 保持当前提供商不变
      const currentProvider = pendingSettings.value.default_provider
      pendingSettings.value = {
        default_provider: currentProvider || result.data.default_provider || 'ollama',
        theme: result.data.theme,
        language: result.data.language
      }
      
      const config = result.data[pendingSettings.value.default_provider] || {}
      providerConfig.value = {
        api_key: config.api_key || '',
        base_url: config.base_url || 'http://localhost:11434',
        model_name: config.model_name || 'deepseek-r1:8b',
        temperature: config.temperature || 0.7,
        max_tokens: config.max_tokens || -1
      }
      
      currentLanguage.value = result.data.language
      handleThemeChange()
    } else {
      console.error('Failed to load settings:', result.message)
    }
  } catch (error) {
    console.error('Error loading settings:', error)
  }
}

const handleThemeChange = () => {
  document.documentElement.setAttribute('data-theme', pendingSettings.value.theme)
  eventBus.emit(Events.THEME_CHANGE, pendingSettings.value.theme)
}

const handleLanguageChange = () => {
  currentLanguage.value = pendingSettings.value.language
  eventBus.emit(Events.LANGUAGE_CHANGE, pendingSettings.value.language)
}

const defaultConfigs = {
  ollama: {
    api_key: '',
    base_url: 'http://localhost:11434',
    model_name: 'deepseek-r1:8b',
    temperature: 0.7,
    max_tokens: -1,
    models: [] // 将通过API动态获取
  },
  openai: {
    api_key: '',
    base_url: 'https://api.openai.com/v1',
    model_name: 'gpt-3.5-turbo',
    temperature: 0.7,
    max_tokens: -1,
    models: []
  },
  deepseek: {
    api_key: '',
    base_url: 'https://api.deepseek.com/v1',
    model_name: 'deepseek-chat',
    temperature: 0.7,
    max_tokens: -1,
    models: [
      { id: 'deepseek-chat', name: 'DeepSeek Chat', type: 'Chat', description: 'DeepSeek通用聊天模型' },
      { id: 'deepseek-coder', name: 'DeepSeek Coder', type: 'Code', description: 'DeepSeek专业代码模型' }
    ]
  },
  openai: {
    api_key: '',
    base_url: 'https://api.openai-proxy.com/v1', // 使用代理地址
    model_name: 'gpt-3.5-turbo',
    temperature: 0.7,
    max_tokens: -1,
    models: [] // 将通过API动态获取
  },
  openrouter: {
    api_key: '',
    base_url: 'https://openrouter.ai/api/v1',
    model_name: 'openai/gpt-3.5-turbo',
    temperature: 0.7,
    max_tokens: -1,
    models: [] // 将通过API动态获取
  }
}

const handleProviderChange = async () => {
  // 重置当前提供商的配置
  const config = defaultConfigs[pendingSettings.value.default_provider]
  providerConfig.value = { ...config }
  
  // 如果是OpenAI且没有API密钥，则不加载模型
  if (pendingSettings.value.default_provider === 'openai' && !providerConfig.value.api_key) {
    availableModels.value = []
    return
  }
  
  // 加载新提供商的模型列表
  await loadModels()
}

const handleApiKeyChange = async () => {
  if (pendingSettings.value.default_provider === 'openai' && providerConfig.value.api_key) {
    await loadModels()
  }
}


const saveAllSettings = async () => {
  isSaving.value = true
  try {
    // 保存所有提供商的配置
    const settings = {
      ...pendingSettings.value,
      ollama: defaultConfigs.ollama,
      deepseek: defaultConfigs.deepseek,
      openai: defaultConfigs.openai,
      openrouter: defaultConfigs.openrouter,
      [pendingSettings.value.default_provider]: providerConfig.value // 当前提供商的配置覆盖默认配置
    }
    
    const response = await fetch('/api/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: 'global',
        preferences: settings
      })
    })
    const result = await response.json()
    if (result.success) {
      alert(t('设置保存成功！'))
      eventBus.emit(Events.SETTINGS_UPDATED, settings)
    } else {
      throw new Error(result.message)
    }
  } catch (error) {
    console.error('Error saving settings:', error)
    alert(t('保存设置失败：') + error.message)
  } finally {
    isSaving.value = false
  }
}

const refreshSettings = async () => {
  isRefreshing.value = true
  try {
    // 先加载设置，保持当前提供商不变
    await loadSettings()
    // 然后加载当前提供商的模型列表
    await loadModels()
  } catch (error) {
    console.error('Error refreshing settings:', error)
  } finally {
    isRefreshing.value = false
  }
}

onMounted(refreshSettings)
onActivated(refreshSettings)
</script>

<style scoped>
/* 保持原有样式不变 */
.settings-container {
  height: 100vh;
  background: var(--bg-color);
  overflow-y: auto;
}

.settings-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.settings-header h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-color);
  letter-spacing: -0.5px;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.refresh-button,
.save-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.refresh-button {
  background-color: var(--primary-color);
  color: white;
}

.save-button {
  background-color: #1976d2;
  color: white;
}

.refresh-button:hover:not(:disabled),
.save-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.refresh-button:hover:not(:disabled) {
  background-color: #0d8c6d;
}

.save-button:hover:not(:disabled) {
  background-color: #1565c0;
}

.refresh-button:disabled,
.save-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.settings-section {
  background: var(--bg-color);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
}

.settings-section h2 {
  margin: 0 0 1.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  letter-spacing: -0.5px;
}

.model-search {
  margin: 1rem 0;
}

.search-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.model-list {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(1000px, 1000px));
  margin-bottom: 1rem;
  justify-content: center;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 1rem 0;
  gap: 1rem;
}

.page-button {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.page-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 1rem;
}

.model-item {
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  transition: all 0.2s;
  background: var(--bg-color);
  height: 120px;
  display: flex;
  align-items: center;
}

.model-item:hover {
  border-color: var(--primary-color);
  background-color: var(--hover-color);
  transform: translateY(-1px);
}

.model-label {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  cursor: pointer;
  width: 100%;
}

.model-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.model-name {
  font-weight: 500;
  color: var(--text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 1rem;
  line-height: 1.5;
}

.model-type {
  font-size: 0.875rem;
  color: var(--primary-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.model-description {
  font-size: 0.875rem;
  color: var(--text-color);
  opacity: 0.7;
  margin-top: 0.25rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.setting-item {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border-radius: 8px;
  background-color: var(--nav-bg);
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-item label {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  font-weight: 500;
  color: var(--text-color);
}

.api-key-input-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 200px;
}

.api-key-error {
  color: var(--error-color);
  font-size: 0.75rem;
  line-height: 1.2;
  margin-top: 0.25rem;
}

.setting-item select,
.setting-item input[type="text"],
.setting-item input[type="password"],
.setting-item input[type="number"] {
  width: 200px;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--bg-color);
  color: var(--text-color);
  font-size: 14px;
}

.setting-item select,
.setting-item input[type="text"],
.setting-item input[type="password"],
.setting-item input[type="number"] {
  cursor: pointer;
}

.setting-item select:hover,
.setting-item input[type="text"]:hover,
.setting-item input[type="password"]:hover,
.setting-item input[type="number"]:hover {
  border-color: var(--primary-color);
}

.setting-item select:focus,
.setting-item input[type="text"]:focus,
.setting-item input[type="password"]:focus,
.setting-item input[type="number"]:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-color-light);
}

.setting-item input[type="range"] {
  width: 160px;
  margin-right: 8px;
  vertical-align: middle;
}

.setting-item .value-display {
  display: inline-block;
  min-width: 32px;
  text-align: right;
  color: var(--text-color-light);
}

/* 响应式布局 */
@media (max-width: 768px) {
  .settings-content {
    padding: 1rem;
  }

  .settings-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .refresh-button,
  .save-button {
    flex: 1;
    justify-content: center;
  }

  .settings-header h1 {
    font-size: 1.5rem;
  }

  .model-list {
    grid-template-columns: 1fr;
  }

  .setting-item label {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .setting-item select {
    width: 100%;
  }
}
</style>