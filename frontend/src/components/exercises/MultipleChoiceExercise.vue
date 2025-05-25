<template>
  <div class="exercise-content">
    <div class="exercise-type">
      <el-tag size="small" type="success">{{ t('选择题') }}</el-tag>
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
    <div class="options">
      <div 
        v-for="(option, key) in exercise.options" 
        :key="key"
        class="option"
        :class="{ 'correct-answer': key === exercise.answer }"
      >
        {{ option }}
      </div>
    </div>
    <div class="answer-section">
      <p class="answer"><strong>{{ t('答案') }}:</strong> {{ exercise.answer }}</p>
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
  border: 1px solid var(--border-color);
}

.option:hover {
  background-color: var(--bg-color-hover);
}

.option.correct-answer {
  border-color: var(--el-color-success);
  background-color: var(--el-color-success-light);
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
</style>