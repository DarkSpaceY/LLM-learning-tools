<template>
  <div class="exercise-content">
    <div class="exercise-type">
      <el-tag size="small" type="primary">{{ t('填空题') }}</el-tag>
      <el-rate
        v-model="exercise.difficulty"
        :max="5"
        disabled
        show-score
        text-color="#ff9900"
      />
    </div>
    <div class="question-text">
      <template v-for="(part, index) in questionParts" :key="index">
        <span v-if="!part.isBlank">{{ part.text }}</span>
        <span v-else class="blank-space">?</span>
      </template>
    </div>
    <div class="answer-section">
      <p class="answer">
        <strong>{{ t('答案') }}:</strong>
        <template v-for="(answer, index) in answerList" :key="index">
          <span class="blank-answer">
            {{ index + 1 }}. {{ answer }}
          </span>
        </template>
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

const questionParts = computed(() => {
  const parts = []
  const text = props.exercise.question
  const blankRegex = /_{3,}/g
  let lastIndex = 0
  let match

  while ((match = blankRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({
        text: text.substring(lastIndex, match.index),
        isBlank: false
      })
    }
    parts.push({ text: match[0], isBlank: true })
    lastIndex = match.index + match[0].length
  }

  if (lastIndex < text.length) {
    parts.push({
      text: text.substring(lastIndex),
      isBlank: false
    })
  }

  return parts
})

const answerList = computed(() => {
  return Array.isArray(props.exercise.answer)
    ? props.exercise.answer
    : [props.exercise.answer]
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

.blank-space {
  display: inline-block;
  min-width: 80px;
  margin: 0 0.5rem;
  padding: 0 0.5rem;
  border-bottom: 2px solid var(--primary-color);
  text-align: center;
  color: var(--primary-color);
}

.blank-answer {
  display: inline-block;
  margin-right: 1rem;
  padding: 0.25rem 0.75rem;
  background-color: var(--el-color-primary-light-9);
  border-radius: 4px;
  color: var(--primary-color);
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