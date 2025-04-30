<template>
  <div class="exercise-generator-container">
    <div class="generator-header">
      <h2>{{ t('练习题生成器') }}</h2>
      <p class="description">{{ t('根据主题智能生成各类型练习题，包含详细解析') }}</p>
    </div>

    <div class="generator-content">
      <div class="input-section">
        <h3>{{ t('生成设置') }}</h3>
        <el-form :model="formData" label-position="top">
          <el-form-item :label="t('知识主题')">
            <el-input 
              v-model="formData.topic" 
              :placeholder="t('请输入知识主题，例如：牛顿第二定律')"
            />
          </el-form-item>
          
          <el-form-item :label="t('题目类型')">
            <el-select 
              v-model="formData.types" 
              multiple 
              :placeholder="t('请选择题目类型')"
            >
              <el-option
                v-for="type in questionTypes"
                :key="type.value"
                :label="t(type.label)"
                :value="type.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item :label="t('难度范围')">
            <el-slider
              v-model="formData.difficultyRange"
              range
              :min="1"
              :max="5"
              :marks="difficultyMarks"
            />
          </el-form-item>

          <el-form-item :label="t('题目数量')">
            <el-input-number 
              v-model="formData.count" 
              :min="1" 
              :max="10"
            />
          </el-form-item>
        </el-form>

        <div class="action-buttons">
          <el-button 
            type="primary" 
            @click="generateExercises"
            :loading="isLoading"
          >
            {{ t('生成练习题') }}
          </el-button>
          <el-button @click="resetForm">{{ t('重置') }}</el-button>
        </div>
      </div>

      <div class="result-section" v-if="exercises.length > 0">
        <h3>{{ t('生成结果') }}</h3>
        <el-card 
          v-for="(exercise, index) in exercises" 
          :key="index"
          class="exercise-card"
        >
          <div class="exercise-header">
            <span class="exercise-index">{{ index + 1 }}.</span>
            <el-tag size="small" :type="getTypeTag(exercise.type)">
              {{ t(exercise.type) }}
            </el-tag>
            <el-tag size="small" :type="getDifficultyTag(exercise.difficulty)">
              {{ t('难度') }}: {{ exercise.difficulty }}
            </el-tag>
          </div>

          <div class="exercise-content">
            <div class="question">
              <strong>{{ t('题目') }}:</strong>
              <div v-html="exercise.question"></div>
            </div>

            <div class="options" v-if="exercise.options">
              <div 
                v-for="(option, key) in exercise.options" 
                :key="key"
                class="option"
              >
                {{ key }}. {{ option }}
              </div>
            </div>

            <el-collapse>
              <el-collapse-item :title="t('查看答案和解析')">
                <div class="answer">
                  <strong>{{ t('答案') }}:</strong>
                  <div v-html="exercise.answer"></div>
                </div>
                <div class="explanation">
                  <strong>{{ t('解析') }}:</strong>
                  <div v-html="exercise.explanation"></div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useSettings, t } from '../../store/settings'
import { ElMessage } from 'element-plus'
import { generateExercises as generateExercisesApi } from '../../api'

const settings = useSettings()

// 题目类型选项
const questionTypes = [
  { value: 'single', label: '单选题' },
  { value: 'multiple', label: '多选题' },
  { value: 'blank', label: '填空题' },
  { value: 'calculation', label: '计算题' },
  { value: 'essay', label: '简答题' }
]

// 难度标记
const difficultyMarks = {
  1: t('入门'),
  2: t('基础'),
  3: t('进阶'),
  4: t('挑战'),
  5: t('专家')
}

// 表单数据
const formData = reactive({
  topic: '',
  types: [],
  difficultyRange: [2, 4],
  count: 3
})

// 状态管理
const isLoading = ref(false)
const exercises = ref([])

// 生成练习题
const generateExercises = async () => {
  if (!formData.topic || formData.types.length === 0) {
    ElMessage.warning(t('请填写完整的生成设置'))
    return
  }

  isLoading.value = true
  try {
    const response = await generateExercisesApi({
      knowledge_points: [formData.topic],
      exercise_type: formData.types[0],
      difficulty: Math.floor((formData.difficultyRange[0] + formData.difficultyRange[1]) / 2),
      count: formData.count
    })
    exercises.value = response.data.data
  } catch (error) {
    ElMessage.error(t('生成失败，请稍后重试'))
    console.error('生成失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.topic = ''
  formData.types = []
  formData.difficultyRange = [2, 4]
  formData.count = 3
  exercises.value = []
}

// 获取题目类型标签样式
const getTypeTag = (type) => {
  const types = {
    'single': 'success',
    'multiple': 'warning',
    'blank': 'info',
    'calculation': 'danger',
    'essay': ''
  }
  return types[type] || 'info'
}

// 获取难度标签样式
const getDifficultyTag = (difficulty) => {
  const level = Math.floor(difficulty)
  const types = {
    1: 'info',
    2: 'success',
    3: 'warning',
    4: 'danger',
    5: ''
  }
  return types[level] || 'info'
}
</script>

<style scoped>
.exercise-generator-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.generator-header {
  margin-bottom: 2rem;
  text-align: center;
}

.generator-header h2 {
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.description {
  color: var(--text-color-secondary);
  font-size: 1.1rem;
}

.generator-content {
  display: grid;
  gap: 2rem;
}

.input-section {
  background-color: var(--bg-color);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.action-buttons {
  margin-top: 2rem;
  display: flex;
  gap: 1rem;
}

.exercise-card {
  margin-bottom: 1.5rem;
}

.exercise-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.exercise-index {
  font-weight: bold;
  color: var(--primary-color);
}

.exercise-content {
  margin-top: 1rem;
}

.question {
  margin-bottom: 1rem;
}

.options {
  margin: 1rem 0;
}

.option {
  margin: 0.5rem 0;
  padding: 0.5rem;
  border-radius: 4px;
  background-color: var(--bg-color);
}

.answer,
.explanation {
  margin: 1rem 0;
}

.answer strong,
.explanation strong {
  color: var(--primary-color);
  display: block;
  margin-bottom: 0.5rem;
}
</style>