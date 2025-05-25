<template>
  <div class="knowledge-parser-container">
    <div class="parser-header">
      <h2>{{ t('文章知识点解析器') }}</h2>
      <p class="description">{{ t('从文章中提取并解析知识点结构、关联和应用') }}</p>
    </div>

    <div class="parser-content">
      <div class="input-section">
        <el-form :model="formData" label-position="top" @submit.prevent="parseKnowledge">
          <el-form-item :label="t('文章内容')">
            <el-input
              v-model="formData.knowledge"
              type="textarea"
              :rows="8"
              :placeholder="t('请输入或粘贴要解析的文章内容')"
              :clearable="true"
              @keyup.enter="parseKnowledge"
            />
          </el-form-item>

          <div class="action-buttons">
            <el-button
              type="primary"
              @click="parseKnowledge"
              :loading="isLoading"
              :disabled="!formData.knowledge"
            >
              {{ t('开始解析') }}
            </el-button>
            <el-button @click="resetForm" :disabled="isLoading">{{ t('重置') }}</el-button>
          </div>
        </el-form>
      </div>

      <div class="result-section" v-if="analysisResult && analysisResult.knowledge_points">
        <el-row :gutter="24">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="(point, index) in analysisResult.knowledge_points" :key="index" class="mb-4">
            <el-card class="knowledge-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <h4>{{ t('知识点') }} {{ index + 1 }}</h4>
                  <div class="tag-group">
                    <el-tag :type="getDifficultyType(point.difficulty)" size="small" class="mr-2">
                      {{ t('难度') }}: {{ t(point.difficulty) }}
                    </el-tag>
                    <el-tag :type="getImportanceType(point.importance)" size="small">
                      {{ t('重要性') }}: {{ t(point.importance) }}
                    </el-tag>
                  </div>
                </div>
              </template>
              
              <div class="card-content">
                <div class="content-section">
                  <p class="content-text">{{ point.content }}</p>
                </div>

                <div class="summary-section">
                  <h5>{{ t('概述') }}</h5>
                  <p class="summary-text">{{ point.summary }}</p>
                </div>

                <div class="section-group">
                  <div class="section">
                    <h5>{{ t('相关概念') }}</h5>
                    <div class="tag-container">
                      <el-tag
                        v-for="(concept, idx) in point.related_concepts"
                        :key="idx"
                        class="mr-2 mb-2"
                        type="info"
                        effect="plain"
                      >
                        {{ concept }}
                      </el-tag>
                    </div>
                  </div>

                  <div class="section">
                    <h5>{{ t('前置知识') }}</h5>
                    <div class="tag-container">
                      <el-tag
                        v-for="(prereq, idx) in point.prerequisites"
                        :key="idx"
                        class="mr-2 mb-2"
                        type="warning"
                        effect="plain"
                      >
                        {{ prereq }}
                      </el-tag>
                    </div>
                  </div>

                  <div class="section">
                    <h5>{{ t('示例') }}</h5>
                    <div class="tag-container">
                      <el-tag
                        v-for="(example, idx) in point.examples"
                        :key="idx"
                        class="mr-2 mb-2"
                        type="success"
                        effect="plain"
                      >
                        {{ example }}
                      </el-tag>
                    </div>
                  </div>

                  <div class="section">
                    <h5>{{ t('关键要点') }}</h5>
                    <ul class="key-points-list">
                      <li v-for="(point, idx) in point.key_points" :key="idx">
                        {{ point }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const { t } = useI18n()

const formData = ref({
  knowledge: ''
})

const isLoading = ref(false)
const analysisResult = ref(null)

const parseKnowledge = async () => {
  if (!formData.value.knowledge) return
  
  isLoading.value = true
  try {
    // API调用
    const response = await axios.post('/api/knowledge_point/parse', {
      content: formData.value.knowledge
    })
    
    console.warn('解析结果:', response)
    analysisResult.value = response.data.data
  } catch (error) {
    ElMessage.error(error.message || '解析失败，请稍后重试')
    console.error('解析失败:', error)
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  formData.value.knowledge = ''
  analysisResult.value = null
}

const getDifficultyType = (difficulty) => {
  const types = {
    'low': 'success',
    'intermediate': 'warning',
    'high': 'danger'
  }
  return types[difficulty] || 'info'
}

const getImportanceType = (importance) => {
  const types = {
    'low': 'info',
    'medium': 'warning',
    'high': 'danger'
  }
  return types[importance] || 'info'
}
</script>

<style scoped>
.knowledge-parser-container {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
}

.parser-header {
  margin-bottom: 2rem;
  text-align: center;
}

.parser-header h2 {
  color: var(--el-color-primary);
  margin-bottom: 1rem;
  font-size: 2rem;
  font-weight: 600;
}

.description {
  color: var(--el-text-color-regular);
  font-size: 1.1rem;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.input-section {
  background-color: var(--el-bg-color);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: var(--el-box-shadow-light);
  margin-bottom: 2rem;
  transition: all 0.3s ease;
}

.input-section:hover {
  box-shadow: var(--el-box-shadow);
}

.action-buttons {
  margin-top: 1.5rem;
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.knowledge-card {
  height: 100%;
  transition: all 0.3s ease;
}

.knowledge-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--el-box-shadow);
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-header h4 {
  margin: 0;
  color: var(--el-color-primary);
  font-size: 1.1rem;
  font-weight: 600;
}

.tag-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.content-section {
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding-bottom: 1rem;
}

.content-text {
  margin: 0;
  line-height: 1.6;
  color: var(--el-text-color-primary);
}

.summary-section h5,
.section h5 {
  margin: 0 0 0.5rem;
  color: var(--el-text-color-regular);
  font-size: 1rem;
  font-weight: 500;
}

.summary-text {
  margin: 0;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

.section-group {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.key-points-list {
  margin: 0;
  padding-left: 1.2rem;
}

.key-points-list li {
  margin-bottom: 0.5rem;
  color: var(--el-text-color-regular);
  line-height: 1.4;
}

.key-points-list li:last-child {
  margin-bottom: 0;
}

.mb-4 {
  margin-bottom: 1.5rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}
</style>