<template>
  <div class="exercise-content">
    <div class="exercise-type">
      <el-tag size="small" type="warning">{{ t('判断题') }}</el-tag>
      <el-rate
        v-model="exercise.difficulty"
        :max="5"
        disabled
        show-score
        text-color="#ff9900"
      />
    </div>
    <div class="question-text">
      {{ exercise.question }}
    </div>
    <div class="true-false-options">
      <el-radio-group v-model="selectedAnswer" disabled>
        <el-radio label="true" border>{{ t('正确') }}</el-radio>
        <el-radio label="false" border>{{ t('错误') }}</el-radio>
      </el-radio-group>
    </div>
    <div class="answer-section">
      <p class="answer">
        <strong>{{ t('答案') }}:</strong>
        {{ exercise.answer === 'true' ? t('正确') : t('错误') }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue'
import { useSettings, t } from '../../store/settings'

const props = defineProps({
  exercise: {
    type: Object,
    required: true
  }
})

const selectedAnswer = computed(() => props.exercise.answer)
</script>

<style scoped>
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

.question-text {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.true-false-options {
  margin: 1.5rem 0;
  display: flex;
  justify-content: center;
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

:deep(.el-radio) {
  margin-right: 1.5rem;
  padding: 0.5rem 1rem;
}

:deep(.el-radio__label) {
  font-size: 1rem;
}
</style>