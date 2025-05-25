<template>
  <div class="exercise-generator-container">
    <div class="generator-header">
      <h2>{{ t('练习题生成器') }}</h2>
      <p class="description">{{ t('根据知识点智能生成练习题，提供详细解析和答案') }}</p>
    </div>

    <div class="generator-content">
      <div class="input-section">
        <el-form :model="formData" label-position="top" @submit.prevent="generateExercises">
          <el-form-item :label="t('知识点')">
            <el-input
              v-model="formData.topic"
              :placeholder="t('请输入知识点名称')"
              :clearable="true"
              @keyup.enter="generateExercises"
            />
          </el-form-item>

          <el-form-item :label="t('题目类型')">
            <el-select
              v-model="formData.types"
              multiple
              collapse-tags
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

          <el-form-item :label="t('难度等级')">
            <el-rate
              v-model="formData.difficulty"
              :max="5"
              :texts="difficultyLevels"
              show-text
            />
          </el-form-item>

          <el-form-item :label="t('生成数量')">
            <el-input-number
              v-model="formData.count"
              :min="1"
              :max="10"
              :step="1"
            />
          </el-form-item>

          <div class="action-buttons">
            <el-button
              type="primary"
              @click="generateExercises"
              :loading="isLoading"
              :disabled="!formData.topic || !formData.types.length"
            >
              {{ t('生成练习题') }}
            </el-button>
            <el-button @click="resetForm" :disabled="isLoading">{{ t('重置') }}</el-button>
          </div>
        </el-form>
      </div>

      <div class="result-section" v-if="exercises.length > 0">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card class="exercises-card">
              <template #header>
                <div class="card-header">
                  <h4>{{ t('生成的练习题') }}</h4>
                  <el-button
                    type="primary"
                    size="small"
                    @click="exportExercises"
                    :disabled="!exercises.length"
                  >
                    {{ t('导出练习题') }}
                  </el-button>
                </div>
              </template>
              <div class="exercises-list">
                <el-collapse accordion>
                  <el-collapse-item
                    v-for="(exercise, index) in exercises"
                    :key="index"
                    :title="`${t('题目')} ${index + 1}: ${exercise.question}`"
                  >
                    <component
                      :is="getExerciseComponent(exercise.type)"
                      :exercise="exercise"
                    />
                  </el-collapse-item>
                </el-collapse>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useSettings, t } from '../../store/settings'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { generateExercises as generateExercisesApi } from '../../api'
import { saveAs } from 'file-saver'
import { Download, QuestionFilled } from '@element-plus/icons-vue'

// 导入题型组件
import MultipleChoiceExercise from '../../components/exercises/MultipleChoiceExercise.vue'
import TrueFalseExercise from '../../components/exercises/TrueFalseExercise.vue'
import ShortAnswerExercise from '../../components/exercises/ShortAnswerExercise.vue'
import FillBlankExercise from '../../components/exercises/FillBlankExercise.vue'
import CalculationExercise from '../../components/exercises/CalculationExercise.vue'

const settings = useSettings()

// 题目类型选项
const questionTypes = [
  { value: 'multiple_choice', label: '选择题' },
  { value: 'true_false', label: '判断题' },
  { value: 'short_answer', label: '简答题' },
  { value: 'fill_blank', label: '填空题' },
  { value: 'calculation', label: '计算题' }
]

// 难度等级
const difficultyLevels = [t('入门'), t('基础'), t('进阶'), t('挑战'), t('专家')]

// 表单数据
const formData = reactive({
  topic: '',
  types: [],
  difficulty: 3,
  count: 5
})

// 状态管理
const isLoading = ref(false)
const exercises = ref([])

// 生成练习题
const generateExercises = async () => {
  // 表单验证
  if (!formData.topic.trim()) {
    ElMessage.warning(t('请输入知识点'))
    return
  }

  if (!formData.types.length) {
    ElMessage.warning(t('请选择至少一种题目类型'))
    return
  }

  isLoading.value = true
  try {
    const response = await axios.post('/api/exercises/generate', {
      topic: formData.topic.trim(),
      types: formData.types,
      difficulty: formData.difficulty,
      count: formData.count
    })
    const rawData = response.data.data
    if (!rawData || !Array.isArray(rawData)) {
      throw new Error(t('服务器返回的数据格式不正确'))
    }

    // 处理后端返回的数据，转换为前端需要的格式
    exercises.value = rawData.map(exercise => ({
      question: exercise.question,
      options: exercise.options || {},
      answer: exercise.answer,
      type: exercise.type_ === '选择' ? 'multiple_choice' :
            exercise.type_ === '判断' ? 'true_false' :
            exercise.type_ === '计算' ? 'calculation' :
            exercise.type_ === '简答' ? 'short_answer' :
            exercise.type_ === '填空' ? 'fill_blank' : 'other',
      difficulty: formData.difficulty // 使用用户选择的难度
    }))
    ElMessage.success(t('练习题生成成功'))
  } catch (error) {
    let errorMessage = t('生成失败，请稍后重试')
    if (error.response?.data?.message) {
      errorMessage = t(error.response.data.message)
    } else if (error.message) {
      errorMessage = t(error.message)
    }
    ElMessage.error(errorMessage)
    console.error('Exercise generation failed:', error)
  } finally {
    isLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.topic = ''
  formData.types = []
  formData.difficulty = 3
  formData.count = 5
  exercises.value = []
}

// 根据题目类型获取对应的组件
const getExerciseComponent = (type) => {
  const components = {
    'multiple_choice': MultipleChoiceExercise,
    'true_false': TrueFalseExercise,
    'short_answer': ShortAnswerExercise,
    'fill_blank': FillBlankExercise,
    'calculation': CalculationExercise
  }
  return components[type] || MultipleChoiceExercise
}

// 导出练习题
const exportExercises = () => {
  if (!exercises.value.length) return
  
  const content = exercises.value.map((exercise, index) => {
    let text = `${index + 1}. ${exercise.question}\n`
    if (exercise.options) {
      text += Object.entries(exercise.options)
        .map(([key, value]) => `   ${value}`)
        .join('\n')
      text += '\n'
    }
    text += `答案：${exercise.answer}\n`
    if (exercise.explanation) {
      text += `解析：${exercise.explanation}\n`
    }
    text += '-------------------\n'
    return text
  }).join('\n')

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  saveAs(blob, `练习题-${formData.topic}-${new Date().toLocaleDateString()}.txt`)
  ElMessage.success(t('练习题导出成功'))
}
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
  animation: fadeIn 0.5s ease-in-out;
}

.generator-header h2 {
  color: var(--primary-color);
  margin-bottom: 0.5rem;
  font-size: 2rem;
  font-weight: 600;
}

.description {
  color: var(--text-color-secondary);
  font-size: 1.1rem;
  line-height: 1.5;
}

.generator-content {
  display: grid;
  gap: 2rem;
}

.input-section {
  background-color: var(--bg-color);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.input-section:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.action-buttons {
  margin-top: 2rem;
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.exercises-card {
  margin-bottom: 1.5rem;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: var(--bg-color);
  border-bottom: 1px solid var(--border-color);
}

.exercise-content {
  padding: 1.5rem;
  background-color: var(--bg-color);
}

.exercise-type {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.options {
  margin: 1.5rem 0;
}

.option {
  margin: 0.75rem 0;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background-color: var(--bg-color-light);
  transition: background-color 0.2s ease;
}

.option:hover {
  background-color: var(--bg-color-hover);
}

.answer-section {
  margin: 1.5rem 0;
  padding: 1rem;
  border-radius: 8px;
  background-color: var(--bg-color-light);
  border-left: 4px solid var(--primary-color);
}

.answer strong,
.explanation strong {
  color: var(--primary-color);
  display: block;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
}

.knowledge-points {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.knowledge-tag {
  margin: 0.25rem;
  transition: transform 0.2s ease;
}

.knowledge-tag:hover {
  transform: scale(1.05);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>