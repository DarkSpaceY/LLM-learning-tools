<template>
  <div class="exercise-content">
    <div class="exercise-type">
      <el-tag size="small" type="info">{{ t('简答题') }}</el-tag>
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
    <div class="answer-section">
      <div class="answer">
        <strong>{{ t('答案') }}:</strong>
        <div class="answer-content">
          {{ exercise.answer }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import { useSettings, t } from '../../store/settings'

const props = defineProps({
  exercise: {
    type: Object,
    required: true
  }
})
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
  white-space: pre-wrap;
}

.answer-section {
  margin: 1.5rem 0;
  padding: 1.5rem;
  border-radius: 8px;
  background-color: var(--bg-color-light);
  border-left: 4px solid var(--primary-color);
}

.answer-content,
.explanation-content {
  margin-top: 0.5rem;
  padding: 1rem;
  background-color: var(--el-color-info-light-9);
  border-radius: 4px;
  white-space: pre-wrap;
  line-height: 1.8;
}

.key-points {
  margin: 1.5rem 0;
}

.points-list {
  margin-top: 0.5rem;
  padding-left: 1.5rem;
}

.points-list li {
  margin-bottom: 0.75rem;
  line-height: 1.6;
  position: relative;
}

.points-list li::before {
  content: '•';
  position: absolute;
  left: -1rem;
  color: var(--primary-color);
}

strong {
  color: var(--primary-color);
  display: block;
  margin-bottom: 0.5rem;
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
</style>