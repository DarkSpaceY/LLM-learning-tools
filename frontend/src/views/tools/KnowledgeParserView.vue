<template>
  <div class="knowledge-parser-container">
    <div class="parser-header">
      <h2>{{ t('知识点解析器') }}</h2>
      <p class="description">{{ t('解析文本中的关键知识点，标注重要程度和难度') }}</p>
    </div>

    <div class="parser-content">
      <div class="input-section">
        <h3>{{ t('输入文本') }}</h3>
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="8"
          :placeholder="t('请输入需要解析的文本内容...')"
        />
        <div class="action-buttons">
          <el-button 
            type="primary" 
            @click="parseText"
            :loading="isLoading"
          >
            {{ t('开始解析') }}
          </el-button>
          <el-button @click="clearInput">{{ t('清空') }}</el-button>
        </div>
      </div>

      <div class="result-section" v-if="parseResults.length > 0">
        <h3>{{ t('解析结果') }}</h3>
        <el-card v-for="(point, index) in parseResults" 
          :key="index"
          class="knowledge-point-card"
        >
          <div class="point-header">
            <h4>{{ point.content }}</h4>
            <div class="point-tags">
              <el-tag :type="getDifficultyType(point.difficulty)">
                {{ t('难度') }}: {{ point.difficulty }}
              </el-tag>
              <el-tag :type="getImportanceType(point.importance)">
                {{ t('重要度') }}: {{ point.importance }}
              </el-tag>
            </div>
          </div>
          <p class="point-explanation">{{ point.explanation }}</p>
          <div class="point-relations" v-if="point.relations && point.relations.length">
            <h5>{{ t('相关知识点') }}:</h5>
            <el-tag 
              v-for="relation in point.relations" 
              :key="relation"
              size="small"
              class="relation-tag"
            >
              {{ relation }}
            </el-tag>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useSettings, t } from '../../store/settings'
import { ElMessage } from 'element-plus'
import { parseKnowledge } from '../../api'

const settings = useSettings()

// 状态管理
const inputText = ref('')
const isLoading = ref(false)
const parseResults = ref([])

// 解析文本
const parseText = async () => {
  if (!inputText.value.trim()) {
    ElMessage.warning(t('请输入需要解析的文本'))
    return
  }

  isLoading.value = true
  try {
    const response = await parseKnowledge({
      content: inputText.value
    })
    parseResults.value = response.data.data
  } catch (error) {
    ElMessage.error(t('解析失败，请稍后重试'))
    console.error('解析失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 清空输入
const clearInput = () => {
  inputText.value = ''
  parseResults.value = []
}

// 获取难度标签类型
const getDifficultyType = (difficulty) => {
  const types = {
    '简单': 'success',
    '中等': 'warning',
    '困难': 'danger'
  }
  return types[difficulty] || 'info'
}

// 获取重要度标签类型
const getImportanceType = (importance) => {
  const types = {
    '一般': 'info',
    '重要': 'warning',
    '核心': 'danger'
  }
  return types[importance] || 'info'
}
</script>

<style scoped>
.knowledge-parser-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.parser-header {
  margin-bottom: 2rem;
  text-align: center;
}

.parser-header h2 {
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.description {
  color: var(--text-color-secondary);
  font-size: 1.1rem;
}

.parser-content {
  display: grid;
  gap: 2rem;
}

.input-section h3,
.result-section h3 {
  margin-bottom: 1rem;
  color: var(--text-color);
}

.action-buttons {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
}

.knowledge-point-card {
  margin-bottom: 1rem;
}

.point-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.point-header h4 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.1rem;
}

.point-tags {
  display: flex;
  gap: 0.5rem;
}

.point-explanation {
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
}

.point-relations {
  margin-top: 1rem;
}

.point-relations h5 {
  margin: 0 0 0.5rem;
  color: var(--text-color);
}

.relation-tag {
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
}
</style>