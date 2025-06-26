<template>
  <div class="markdown-preview">
    <MdPreview
      :modelValue="processedContent"
      :previewTheme="isDark ? 'dark' : 'default'"
      codeTheme="atom"
      :showCodeRowNumber="true"
      :tableShape="0"
      :mdKatex="true"
      class="markdown-body"
    >
      <template #code-block="{ code, lang }">
        <div class="code-block">
          <div v-if="lang" class="code-lang">{{ lang }}</div>
          <pre><code>{{ code }}</code></pre>
          <pre class="scrollable-code"><code>{{ code }}</code></pre>
          <button class="copy-button" @click="copyCode(code)">
            <i class="fas fa-copy"></i>
          </button>
        </div>
      </template>
    </MdPreview>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'
import 'katex/dist/katex.min.css'
import { useSettings, t } from '../store/settings'
import { ElMessage } from 'element-plus'

const settings = useSettings()
const isDark = computed(() => settings.value.theme === 'dark')

const props = defineProps({
  content: {
    type: String,
    required: true
  }
})

// 处理内容中的 markdown 代码块
const processedContent = computed(() => {
  if (!props.content) return ''
  
  // 处理 ```markdown 代码块
  return props.content.replace(/```markdown\n([\s\S]*?)```/g, (match, code) => {
    // 移除前后的空白字符
    return code.trim()
  }).replace(/```\s*\n/g, '```\n')  // 清理其他代码块的语言标记
})

// 复制代码的方法
const copyCode = async (code) => {
  try {
    await navigator.clipboard.writeText(code)
    ElMessage({
      message: t('复制成功'),
      type: 'success',
      duration: 2000
    })
  } catch (err) {
    ElMessage.error(t('复制失败'))
    console.error('Failed to copy:', err)
  }
}
</script>

<style scoped>
.markdown-preview {
  width: 100%;
}

/* KaTeX 样式覆盖 */
:deep(.katex-display) {
  margin: 1em 0;
  overflow-x: auto;
  overflow-y: hidden;
}

:deep(.katex) {
  font-size: 1.1em;
}

:deep(.katex-html) {
  overflow-x: auto;
  overflow-y: hidden;
}

.markdown-body {
  color: var(--text-color);
  font-size: 1rem;
  line-height: 1.8;
}

.code-block {
  position: relative;
  margin: 1rem 0;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  transition: border-color 0.3s ease;
}

.code-block:hover {
  border-color: var(--primary-color);
}

.code-lang {
  position: absolute;
  top: 0;
  left: 0;
  padding: 6px 10px;
  font-size: 0.8rem;
  color: var(--text-color);
  background: var(--primary-color);
  opacity: 0.9;
  border-bottom-right-radius: 6px;
  z-index: 1;
}

.code-block pre {
  margin: 0;
  padding: 2.5rem 1rem 1rem;
  background: transparent;
}

.code-block code {
  font-family: 'Fira Code', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  tab-size: 2;
}

.copy-button {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0;
  transition: all 0.3s ease;
  color: var(--text-color);
}

.code-block:hover .copy-button {
  opacity: 0.9;
}

.copy-button:hover {
  opacity: 1;
  transform: scale(1.05);
}

.copy-button:active {
  transform: scale(0.95);
}

.copy-button i {
  font-size: 0.9rem;
  color: var(--bg-color);
}

/* 关键样式：为代码块添加滚动条 */
.scrollable-code {
  overflow: auto; /* 自动显示滚动条 */
  max-height: 300px; /* 限制最大高度（根据需求调整） */
  max-width: 100%; /* 防止水平溢出 */
  padding: 1em; /* 内边距 */
  margin: 0.5em 0; /* 外边距 */
  background-color: #f5f5f5; /* 背景色 */
  border-radius: 4px; /* 圆角 */
}

/* 暗黑模式适配 */
.dark .scrollable-code {
  background-color: #2d2d2d; /* 暗黑背景 */
}

/* 确保代码不换行 */
.scrollable-code code {
  white-space: pre; /* 保留空白和换行 */
  display: block; /* 确保滚动条生效 */
}

/* 自定义其他 markdown 样式 */
:deep(blockquote) {
  margin: 1rem 0;
  padding: 1rem;
  border-left: 4px solid var(--primary-color);
  background: rgba(var(--primary-color-rgb), 0.05);
  border-radius: 4px;
}

:deep(table) {
  width: 100%;
  margin: 1rem 0;
  border-collapse: collapse;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

:deep(th) {
  background: rgba(var(--primary-color-rgb), 0.1);
  padding: 12px;
  text-align: left;
  font-weight: 500;
  border-bottom: 1px solid var(--border-color);
}

:deep(td) {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
}

:deep(tr:last-child td) {
  border-bottom: none;
}

:deep(tr:nth-child(even)) {
  background: rgba(var(--primary-color-rgb), 0.02);
}
</style>