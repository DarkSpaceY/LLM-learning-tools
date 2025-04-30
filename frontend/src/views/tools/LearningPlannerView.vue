<template>
  <div class="learning-planner-container">
    <div class="planner-header">
      <h2>{{ t('学习计划生成器') }}</h2>
      <p class="description">{{ t('制定个性化学习计划，合理安排学习进度') }}</p>
    </div>

    <div class="planner-content">
      <div class="input-section">
        <el-form :model="formData" label-position="top">
          <el-form-item :label="t('学习目标')">
            <el-input
              v-model="formData.goal"
              type="textarea"
              :rows="3"
              :placeholder="t('请描述你的学习目标...')"
            />
          </el-form-item>

          <el-form-item :label="t('当前水平')">
            <el-rate
              v-model="formData.currentLevel"
              :texts="levelTexts"
              show-text
            />
          </el-form-item>

          <el-form-item :label="t('目标水平')">
            <el-rate
              v-model="formData.targetLevel"
              :texts="levelTexts"
              show-text
            />
          </el-form-item>

          <el-form-item :label="t('每周可投入时间（小时）')">
            <el-input-number
              v-model="formData.weeklyHours"
              :min="1"
              :max="40"
            />
          </el-form-item>

          <el-form-item :label="t('学习偏好')">
            <el-checkbox-group v-model="formData.preferences">
              <el-checkbox
                v-for="pref in preferenceOptions"
                :key="pref.value"
                :value="pref.value"
              >
                {{ t(pref.label) }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>

        <div class="action-buttons">
          <el-button
            type="primary"
            @click="generatePlan"
            :loading="isLoading"
          >
            {{ t('生成学习计划') }}
          </el-button>
          <el-button @click="resetForm">{{ t('重置') }}</el-button>
        </div>
      </div>

      <div class="result-section" v-if="plan">
        <h3>{{ t('学习计划') }}</h3>
        
        <el-card class="overview-card">
          <template #header>
            <div class="card-header">
              <h4>{{ t('计划概览') }}</h4>
              <el-button type="primary" size="small" @click="exportPlan">
                {{ t('导出计划') }}
              </el-button>
            </div>
          </template>
          <div class="overview-content">
            <div class="overview-item">
              <span class="label">{{ t('预计完成时间') }}:</span>
              <span class="value">{{ plan.estimatedDuration }}</span>
            </div>
            <div class="overview-item">
              <span class="label">{{ t('总学时') }}:</span>
              <span class="value">{{ plan.totalHours }} {{ t('小时') }}</span>
            </div>
            <div class="milestone-list">
              <h5>{{ t('关键里程碑') }}:</h5>
              <el-timeline>
                <el-timeline-item
                  v-for="(milestone, index) in plan.milestones"
                  :key="index"
                  :timestamp="milestone.time"
                >
                  {{ milestone.description }}
                </el-timeline-item>
              </el-timeline>
            </div>
          </div>
        </el-card>

        <div class="weekly-plans">
          <el-collapse v-model="activeWeeks">
            <el-collapse-item
              v-for="(week, index) in plan.weeklyPlans"
              :key="index"
              :title="t('第 {0} 周', [index + 1])"
              :name="index"
            >
              <div class="week-content">
                <div class="learning-tasks">
                  <div
                    v-for="(task, taskIndex) in week.tasks"
                    :key="taskIndex"
                    class="task-item"
                  >
                    <div class="task-header">
                      <el-checkbox v-model="task.completed">
                        {{ task.name }}
                      </el-checkbox>
                      <span class="task-duration">{{ task.duration }}</span>
                    </div>
                    <p class="task-description">{{ task.description }}</p>
                    <div class="task-resources" v-if="task.resources.length">
                      <h6>{{ t('推荐资源') }}:</h6>
                      <ul>
                        <li v-for="resource in task.resources" :key="resource.url">
                          <el-link :href="resource.url" target="_blank">
                            {{ resource.title }}
                          </el-link>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
                <div class="week-summary">
                  <strong>{{ t('本周重点') }}:</strong>
                  <p>{{ week.focus }}</p>
                  <div class="progress-info">
                    <span>{{ t('进度') }}: {{ week.progress }}%</span>
                    <el-progress :percentage="week.progress" />
                  </div>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useSettings, t } from '../../store/settings'
import { ElMessage } from 'element-plus'
import { generateLearningPlan as generateLearningPlanApi } from '../../api'

const settings = useSettings()

// 水平等级文本
const levelTexts = [
  t('入门'),
  t('基础'),
  t('进阶'),
  t('高级'),
  t('专家')
]

// 学习偏好选项
const preferenceOptions = [
  { value: 'video', label: '视频学习' },
  { value: 'reading', label: '阅读学习' },
  { value: 'practice', label: '实践练习' },
  { value: 'interactive', label: '互动学习' },
  { value: 'project', label: '项目驱动' }
]

// 表单数据
const formData = reactive({
  goal: '',
  currentLevel: 0,
  targetLevel: 0,
  weeklyHours: 10,
  preferences: []
})

// 状态管理
const isLoading = ref(false)
const plan = ref(null)
const activeWeeks = ref([0])

// 生成学习计划
const generatePlan = async () => {
  if (!formData.goal || formData.currentLevel === 0 || formData.targetLevel === 0) {
    ElMessage.warning(t('请完整填写学习计划信息'))
    return
  }

  isLoading.value = true
  try {
    const response = await generateLearningPlanApi({
      user_id: 'current_user',
      knowledge_points: [formData.goal],
      duration_days: Math.ceil(formData.weeklyHours * 4),
      user_level: formData.currentLevel
    })
    plan.value = response.data.data
  } catch (error) {
    ElMessage.error(t('生成失败，请稍后重试'))
    console.error('生成失败:', error)
  } finally {
    isLoading.value = false
  }

  if (formData.targetLevel <= formData.currentLevel) {
    ElMessage.warning(t('目标水平必须高于当前水平'))
    return
  }

  isLoading.value = true
  try {
    const response = await axios.post('/api/tools/learning-planner/generate', {
      goal: formData.goal,
      currentLevel: formData.currentLevel,
      targetLevel: formData.targetLevel,
      weeklyHours: formData.weeklyHours,
      preferences: formData.preferences
    })
    plan.value = response.data.plan
    activeWeeks.value = [0]
  } catch (error) {
    ElMessage.error(t('生成失败，请稍后重试'))
    console.error('生成失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.goal = ''
  formData.currentLevel = 0
  formData.targetLevel = 0
  formData.weeklyHours = 10
  formData.preferences = []
  plan.value = null
}

// 导出计划
const exportPlan = () => {
  // TODO: 实现导出功能
  ElMessage.success(t('计划已导出'))
}
</script>

<style scoped>
.learning-planner-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.planner-header {
  margin-bottom: 2rem;
  text-align: center;
}

.planner-header h2 {
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.description {
  color: var(--text-color-secondary);
  font-size: 1.1rem;
}

.planner-content {
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

.overview-card {
  margin-bottom: 2rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h4 {
  margin: 0;
}

.overview-content {
  padding: 1rem 0;
}

.overview-item {
  margin-bottom: 1rem;
}

.overview-item .label {
  font-weight: bold;
  margin-right: 0.5rem;
}

.milestone-list {
  margin-top: 1.5rem;
}

.milestone-list h5 {
  margin-bottom: 1rem;
}

.week-content {
  padding: 1rem 0;
}

.task-item {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border-radius: 4px;
  background-color: var(--bg-color);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.task-duration {
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

.task-description {
  color: var(--text-color-secondary);
  margin: 0.5rem 0;
}

.task-resources {
  margin-top: 1rem;
}

.task-resources h6 {
  margin: 0 0 0.5rem;
  color: var(--text-color);
}

.task-resources ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.task-resources li {
  margin: 0.25rem 0;
}

.week-summary {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.progress-info {
  margin-top: 1rem;
}
</style>