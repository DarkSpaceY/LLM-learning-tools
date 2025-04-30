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
        <div class="model-list">
          <div v-for="model in availableModels" :key="model.id" class="model-item">
            <label class="model-label">
              <input
                type="radio"
                :value="model.id"
                v-model="pendingSettings.default_model"
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
import { ref, onMounted, onActivated } from 'vue'
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
    '保存设置失败：': '保存设置失败：'
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
    '保存设置失败：': 'Failed to save settings: '
  }
}

const currentLanguage = ref('zh-CN')
const t = (key) => translations[currentLanguage.value]?.[key] || key

const availableModels = ref([])
const pendingSettings = ref({
  default_model: '',
  theme: 'light',
  language: 'zh-CN'
})
const isRefreshing = ref(false)
const isSaving = ref(false)

const loadModels = async () => {
  try {
    const response = await fetch('/api/models')
    const result = await response.json()
    if (result.success) {
      availableModels.value = result.data
    } else {
      console.error('Failed to load models:', result.message)
    }
  } catch (error) {
    console.error('Error loading models:', error)
  }
}

const loadSettings = async () => {
  try {
    const response = await fetch('/api/settings')
    const result = await response.json()
    if (result.success) {
      pendingSettings.value = {
        default_model: result.data.default_model,
        theme: result.data.theme,
        language: result.data.language
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

const saveAllSettings = async () => {
  isSaving.value = true
  try {
    const response = await fetch('/api/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: 'global',
        preferences: pendingSettings.value
      })
    })
    const result = await response.json()
    if (result.success) {
      alert(t('设置保存成功！'))
      eventBus.emit(Events.SETTINGS_UPDATED, pendingSettings.value)
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
    await Promise.all([
      loadModels(),
      loadSettings()
    ])
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

.model-list {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

.model-item {
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  transition: all 0.2s;
  background: var(--bg-color);
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
  align-items: center;
  font-weight: 500;
  color: var(--text-color);
}

.setting-item select {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  background-color: var(--bg-color);
  font-size: 0.875rem;
  color: var(--text-color);
  min-width: 140px;
  cursor: pointer;
  transition: all 0.2s;
}

.setting-item select:hover {
  border-color: var(--primary-color);
}

.setting-item select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.1);
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