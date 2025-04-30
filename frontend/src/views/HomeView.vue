<!-- 保持template和script部分不变 -->
<template>
  <div class="app-container">
    <!-- 左侧：大纲树 -->
    <div class="outline-panel">
      <h3>{{ t('学习大纲') }}</h3>
      <el-tree
        :data="outlineTree"
        node-key="id"
        :props="defaultProps"
        :expand-on-click-node="false"
        @node-click="handleNodeClick"
        class="custom-tree"
        highlight-current
      >
        <template #default="{ node, data }">
          <span class="custom-tree-node">
            <span class="node-title">
              <span class="title">{{ data.label }}</span>
              <!-- <div v-if="data.description" class="description">{{ data.description }}</div> -->
            </span>
            <span v-if="data.type === 'section'" class="action-buttons">
              <el-button link type="primary" @click.stop="viewContent(data)">
                {{ t('查看内容') }}
              </el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </div>

    <!-- 右侧：聊天和内容区域 -->
    <div class="content-panel">
      <!-- 流式输出区域 -->
      <div class="stream-output" ref="messageContainer">
        <!-- 显示用户问题 -->
        <div v-if="userQuestion" class="user-question">
          {{ userQuestion }}
        </div>
        
        <!-- 显示当前状态和进度 -->
        <div v-if="currentStage || currentProgress" class="stage-info">
          <div class="stage-text">{{ currentStage }}</div>
          <div v-if="currentProgress" class="progress-info">
            <el-progress
              :percentage="currentProgress"
              :status="progressStatus"
              :stroke-width="10"
              :show-text="true"
            />
          </div>
        </div>

        <!-- 显示流式输出内容 -->
        <div v-if="currentMessage" class="message-content" :class="{ 'streaming': isLoading }">
          <div class="content-wrapper">
            <template v-if="showThinking">
              <div v-for="(block, index) in splitThinkingBlocks(currentMessage)" :key="index">
                <div v-if="block.type === 'think'" class="think-block">
                  <div class="think-header">
                    <i class="fas fa-brain"></i>
                    <span>思考过程</span>
                  </div>
                  <div class="think-content">
                    <MarkdownDisplay :content="block.content" />
                  </div>
                </div>
                <MarkdownDisplay v-else :content="block.content" />
              </div>
            </template>
            <MarkdownDisplay v-else :content="currentMessage" />
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-container">
        <textarea
          v-model="userInput"
          @keydown.enter.exact.prevent="sendMessage"
          @keydown.enter.shift.exact=""
          :placeholder="t('请输入您想学习的主题...')"
          rows="1"
          ref="inputField"
          :disabled="isLoading"
        ></textarea>
        <button @click="sendMessage" :disabled="isLoading" class="send-button">
          <i class="fas fa-paper-plane"></i>
          {{ isLoading ? t('生成中...') : t('发送') }}
        </button>
      </div>
    </div>

    <!-- 内容查看对话框 -->
    <el-dialog
      v-model="contentDialogVisible"
      :title="selectedSection?.title || ''"
      width="80%"
      :destroy-on-close="true"
      class="section-dialog"
    >
      <div class="section-content">
        <div class="content-header">
          <h3>{{ selectedSection?.title }}</h3>
          <p class="description">{{ selectedSection?.description }}</p>
        </div>
        <div class="content-body">
          <MarkdownDisplay :content="selectedSection?.content || ''" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import MarkdownDisplay from '../components/MarkdownDisplay.vue'
import { v4 as uuidv4 } from 'uuid'
import { useSettings, t } from '../store/settings'
import { ElMessage, ElMessageBox } from 'element-plus'

const settings = useSettings()
const userInput = ref('')
const messageContainer = ref(null)
const inputField = ref(null)
const isLoading = ref(false)
const sessionId = ref(uuidv4())
let eventSource = null

// 状态管理
const userQuestion = ref('')        // 用户问题
const currentMessage = ref('')      // 当前流式输出内容
const currentStage = ref('')        // 当前阶段
const currentProgress = ref(0)      // 当前进度
const progressStatus = ref('')      // 进度状态

// 树形结构相关
const outlineTree = ref([])
const defaultProps = {
  children: 'children',
  label: 'label'
}

// 内容查看相关
const contentDialogVisible = ref(false)
const selectedSection = ref(null)

// 根据数据类型添加到树形结构
const addToTree = (data) => {
  if (data.type === 'chapter') {
    // 处理章节数据
    const chapter = {
      id: `chapter-${data.data.number}`,
      label: data.data.title,
      type: 'chapter',
      description: data.data.description,
      children: []
    }
    
    // 查找是否已存在该章节
    const existingIndex = outlineTree.value.findIndex(
      c => c.id === `chapter-${data.data.number}`
    )
    
    if (existingIndex >= 0) {
      // 保留原有的子节点
      chapter.children = outlineTree.value[existingIndex].children
      // 更新章节
      outlineTree.value[existingIndex] = chapter
    } else {
      outlineTree.value.push(chapter)
      // 按章节号排序
      outlineTree.value.sort((a, b) => {
        const aNum = parseInt(a.id.split('-')[1])
        const bNum = parseInt(b.id.split('-')[1])
        return aNum - bNum
      })
    }
  } else if (data.type === 'section') {
    // 处理小节数据
    const [chapterNum] = data.data.number.split('.')
    const chapterIndex = outlineTree.value.findIndex(
      c => c.id === `chapter-${chapterNum}`
    )
    
    if (chapterIndex >= 0) {
      const section = {
        id: `section-${data.data.number}`,
        label: `${data.data.number} ${data.data.title}`,
        type: 'section',
        title: `${data.data.number} ${data.data.title}`,
        description: data.data.description,
        content: ''
      }
      
      // 查找是否已存在该小节
      const existingIndex = outlineTree.value[chapterIndex].children.findIndex(
        s => s.id === `section-${data.data.number}`
      )
      
      if (existingIndex >= 0) {
        // 保留原有内容
        section.content = outlineTree.value[chapterIndex].children[existingIndex].content
        // 更新小节
        outlineTree.value[chapterIndex].children[existingIndex] = section
      } else {
        outlineTree.value[chapterIndex].children.push(section)
        // 按小节号排序
        outlineTree.value[chapterIndex].children.sort((a, b) => {
          const [, aSection] = a.id.split('-')[1].split('.')
          const [, bSection] = b.id.split('-')[1].split('.')
          return parseInt(aSection) - parseInt(bSection)
        })
      }
    }
  } else if (data.type === 'content') {
    // 处理内容数据
    const chapterNum = data.data.chapter
    const sectionNum = data.data.section
    const chapterIndex = outlineTree.value.findIndex(
      c => c.id === `chapter-${chapterNum}`
    )
    
    if (chapterIndex >= 0) {
      const chapter = outlineTree.value[chapterIndex]
      const section = chapter.children.find(s => s.id === `section-${sectionNum}`)
      
      if (section) {
        if (typeof data.data.content === 'string') {
          section.content = data.data.content
        }
      }
    }
  }
}

// 处理节点点击
const handleNodeClick = (data) => {
  if (data.type === 'section') {
    viewContent(data)
  }
}

// 查看内容
const viewContent = (data) => {
  selectedSection.value = data
  contentDialogVisible.value = true
}

// 用于分割思考块和普通内容的辅助函数
const splitThinkingBlocks = (content) => {
  if (!content) return []
  
  // 清理多余的换行符
  content = content.replace(/\n{3,}/g, '\n\n')
  
  const blocks = []
  let lastIndex = 0
  
  // 使用正则表达式匹配<think>标签
  const regex = /<think>([\s\S]*?)<\/think>/g
  let match
  
  while ((match = regex.exec(content)) !== null) {
    // 添加思考标签之前的内容
    if (match.index > lastIndex) {
      blocks.push({
        type: 'normal',
        content: content.slice(lastIndex, match.index).trim()
      })
    }
    
    // 添加思考块内容
    blocks.push({
      type: 'think',
      content: match[1].trim()
    })
    
    lastIndex = match.index + match[0].length
  }
  
  // 添加最后一段普通内容
  if (lastIndex < content.length) {
    blocks.push({
      type: 'normal',
      content: content.slice(lastIndex).trim()
    })
  }
  
  return blocks
}

// 控制是否显示思考过程
const showThinking = ref(true)

// 滚动到底部
const scrollToBottom = () => {
  setTimeout(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  }, 100)
}

// 清理EventSource
const cleanupEventSource = () => {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
}

const ClearChunk = () => {
  currentMessage.value = ''
}

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const userMessage = userInput.value.trim()
  userInput.value = ''
  isLoading.value = true
  
  // 重置状态
  userQuestion.value = userMessage
  currentMessage.value = ''
  currentStage.value = ''
  currentProgress.value = 0
  progressStatus.value = ''
  outlineTree.value = []

  try {
    // 清理现有的事件源
    cleanupEventSource()

    // 创建新的事件源
    const encodedMessage = encodeURIComponent(userMessage)
    const url = `/api/dialogue/stream?session_id=${sessionId.value}&message=${encodedMessage}&model=${settings.value.default_model}`
    eventSource = new EventSource(url)

    // 处理消息
    eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        isLoading.value = false
        cleanupEventSource()
        return
      }

      try {
        const data = JSON.parse(event.data)

        // 根据消息类型处理
        switch (data.type) {
          case 'progress':
            handleProgress(data)
            ClearChunk()
            break
            
          case 'chunk':
            if (data.content) {
              currentMessage.value += data.content
              // scrollToBottom()
            }
            break
            
          case 'chapter':
          case 'section':
          case 'content':
            addToTree(data)
            ClearChunk()
            break
            
          case 'complete':
            handleComplete(data)
            break
            
          case 'error':
            handleError(data)
            break
        }
      } catch (error) {
        console.error('处理消息失败:', error)
        ElMessage.error(t('消息处理失败'))
        isLoading.value = false
        cleanupEventSource()
      }
    }

    // 处理错误
    eventSource.onerror = (error) => {
      console.error('SSE Error:', error)
      ElMessage.error(t('连接中断，请重试'))
      isLoading.value = false
      cleanupEventSource()
    }

  } catch (error) {
    console.error(error)
    ElMessage.error(t('发送消息失败'))
    isLoading.value = false
  }
}

// 处理进度信息
const handleProgress = (data) => {
  const stage = data.stage
  const status = data.status
  const count = data.count || 0

  // 更新阶段显示
  if (status === 'start') {
    currentStage.value = stageToText(stage)
    currentProgress.value = 0
    progressStatus.value = ''
  } else if (status === 'complete') {
    currentProgress.value = 100
    progressStatus.value = 'success'
    
    switch (stage) {
      case 'chapters':
        currentStage.value = t(`已完成章节大纲，共 ${count} 章`)
        break
      case 'sections':
        currentStage.value = t(`已完成小节结构，共 ${count} 个小节`)
        break
      case 'content':
        currentStage.value = t(`已完成详细内容，共 ${count} 个段落`)
        break
    }
  }
}

// 处理完成消息
const handleComplete = (data) => {
  isLoading.value = false
  currentMessage.value = ''
  currentStage.value = t('生成完成')
  currentProgress.value = 100
  progressStatus.value = 'success'
  cleanupEventSource()
  
  // 显示保存确认对话框
  ElMessageBox.confirm(
    t('是否保存本次生成的教程？'),
    t('保存确认'),
    {
      confirmButtonText: t('保存'),
      cancelButtonText: t('取消'),
      type: 'info'
    }
  ).then(() => {
    saveTutorial()
  }).catch(() => {})
}

// 保存教程
const saveTutorial = async () => {
  try {
    // 准备保存的数据
    const tutorialData = {
      title: userQuestion.value,
      chapters: outlineTree.value.map(chapter => ({
        number: parseInt(chapter.id.split('-')[1]),
        title: chapter.label,
        description: chapter.description,
        sections: chapter.children.map(section => ({
          number: section.id.split('-')[1],
          title: section.label.slice(section.label.indexOf(' ') + 1), // 去掉编号部分
          description: section.description,
          content: section.content
        }))
      }))
    }

    // 发送保存请求
    const response = await fetch('/api/tutorials/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(tutorialData)
    })

    const result = await response.json()
    if (result.success) {
      ElMessage.success(t('教程保存成功'))
    } else {
      throw new Error(result.message)
    }
  } catch (error) {
    console.error('Failed to save tutorial:', error)
    ElMessage.error(t('保存教程失败'))
  }
}

// 处理错误消息
const handleError = (data) => {
  ElMessage.error(data.message || t('发生错误，请稍后重试'))
  isLoading.value = false
  currentStage.value = t('生成失败')
  progressStatus.value = 'exception'
  cleanupEventSource()
}

// 阶段文本转换
const stageToText = (stage) => {
  switch(stage) {
    case 'chapters':
      return t('正在生成章节大纲...')
    case 'sections':
      return t('正在生成小节内容...')
    case 'content':
      return t('正在生成详细内容...')
    default:
      return t('正在生成...')
  }
}

onMounted(() => {
  currentMessage.value = t('👋 你好！我是你的AI学习助手。请告诉我你想学习的主题，我会为你规划详细的学习路径。')
})

onUnmounted(() => {
  cleanupEventSource()
})
</script>

<style scoped>
/* 思考块样式 */
.think-block {
  margin: 1rem 0;
  padding: 1rem;
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.think-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  color: var(--primary-color);
  font-weight: 500;
  font-size: 0.9rem;
}

.think-header i {
  font-size: 1rem;
}

.think-content {
  color: var(--text-color-secondary);
  font-size: 0.95rem;
  line-height: 1.6;
  white-space: pre-wrap;
  padding: 0.5rem;
  background: rgba(var(--primary-color-rgb), 0.05);
  border-radius: 4px;
}

/* 动画效果 */
.message-content.streaming .think-block {
  border-color: var(--primary-color);
  animation: think-pulse 2s infinite;
}

@keyframes think-pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(var(--primary-color-rgb), 0.2);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(var(--primary-color-rgb), 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(var(--primary-color-rgb), 0);
  }
}
.app-container {
  height: 100vh;
  display: flex;
  background: var(--bg-color);
  color: var(--text-color);
}

/* 大纲面板 */
.outline-panel {
  width: 300px;
  border-right: 1px solid var(--border-color);
  padding: 1rem;
  overflow-y: auto;
  background: var(--bg-color);
}

.outline-panel h3 {
  margin-bottom: 1rem;
  color: var(--primary-color);
  font-size: 1.2rem;
}

/* 树形控件自定义样式 */
.custom-tree {
  background: transparent;
  --el-tree-node-hover-bg-color: rgba(var(--primary-color-rgb), 0.1);
  --el-tree-node-content-height: auto;
}

:deep(.el-tree) {
  background-color: transparent;
  color: var(--text-color);
}

:deep(.el-tree-node__content) {
  background-color: transparent;
  height: auto;
  min-height: 40px;
  padding: 4px 0;
  transition: all 0.3s ease;
}

:deep(.el-tree-node__content:hover) {
  background-color: var(--el-tree-node-hover-bg-color);
}

:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background-color: rgba(var(--primary-color-rgb), 0.15);
  color: var(--primary-color);
}

:deep(.el-tree-node.is-expanded > .el-tree-node__content) {
  font-weight: 500;
}

:deep(.el-tree-node__expand-icon) {
  color: var(--text-color-secondary);
  transition: all 0.3s ease;
}

:deep(.el-tree-node__expand-icon.expanded) {
  transform: rotate(90deg);
  color: var(--primary-color);
}

:deep(.el-tree-node__expand-icon.is-leaf) {
  color: transparent;
}

/* 树节点样式 */
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 8px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.node-title {
  flex: 1;
  margin-right: 1rem;
}

.node-title .title {
  font-weight: 500;
  color: var(--text-color);
  transition: color 0.3s ease;
}

:deep(.el-tree-node.is-current) .node-title .title {
  color: var(--primary-color);
}

.node-title .description {
  font-size: 0.9em;
  color: var(--text-color-secondary);
  margin-top: 4px;
  line-height: 1.4;
  transition: color 0.3s ease;
}

:deep(.el-tree-node.is-current) .node-title .description {
  color: var(--text-color);
}

.action-buttons {
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.custom-tree-node:hover .action-buttons {
  opacity: 1;
}

:deep(.el-button--primary) {
  --el-button-hover-bg-color: rgba(var(--primary-color-rgb), 0.1);
  --el-button-hover-text-color: var(--primary-color);
}

/* 内容面板 */
.content-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.stream-output {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  margin-bottom: 1rem;
}

/* 用户问题 */
.user-question {
  font-size: 1.2rem;
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

/* 进度信息 */
.stage-info {
  margin-bottom: 1rem;
  background: var(--bg-color);
}

.stage-text {
  color: var(--primary-color);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.progress-info {
  padding-top: 0.5rem;
}

/* 消息内容 */
.message-content {
  padding: 1rem;
  background: var(--bg-color);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  margin-bottom: 1rem;
}

.message-content.streaming {
  border-color: var(--primary-color);
  background: linear-gradient(
    90deg,
    var(--bg-color) 0%,
    rgba(var(--primary-color-rgb), 0.05) 50%,
    var(--bg-color) 100%
  );
  background-size: 200% 100%;
  animation: flow 2s linear infinite;
}

.content-wrapper {
  position: relative;
}

.message-content.streaming .content-wrapper::after {
  content: '▋';
  display: inline-block;
  color: var(--primary-color);
  animation: cursor-blink 0.8s step-end infinite;
  margin-left: 2px;
  font-size: 1.1em;
  line-height: 1;
  vertical-align: baseline;
}

/* 思考块样式 */
.think-block {
  margin: 1rem 0;
  padding: 1rem;
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.think-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  color: var(--primary-color);
  font-weight: 500;
  font-size: 0.9rem;
}

.think-header i {
  font-size: 1rem;
}

.think-content {
  color: var(--text-color-secondary);
  font-size: 0.95rem;
  line-height: 1.6;
  white-space: pre-wrap;
  padding: 0.5rem;
  background: rgba(var(--primary-color-rgb), 0.05);
  border-radius: 4px;
}

/* 输入区域 */
.input-container {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--bg-color);
  border-top: 1px solid var(--border-color);
  align-items: center;
}

textarea {
  flex: 1;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  resize: none;
  outline: none;
  font-size: 0.9375rem;
  line-height: 1.5;
  padding: 0.5rem;
  transition: border-color 0.3s;
  background: var(--bg-color);
  color: var(--text-color);
}

textarea:focus {
  border-color: var(--primary-color);
}

.send-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  background: var(--primary-color);
  color: white;
  font-size: 0.9375rem;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.send-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-button:not(:disabled):hover {
  opacity: 0.9;
}
/* 弹窗样式 */
:deep(.el-dialog.el-dialog--center.section-dialog .el-dialog) {
  background: var(--bg-color) !important;
  border: 2px solid var(--primary-color) !important;
  box-shadow: 0 0 15px rgba(var(--primary-color-rgb), 0.15) !important;
}

:deep(.section-dialog .el-dialog__header) {
  background: var(--bg-color) !important;
  color: var(--text-color);
  border-bottom: 1px solid var(--border-color);
  margin-right: 0;
  padding: 20px;
}

:deep(.section-dialog .el-dialog__title) {
  color: var(--text-color) !important;
  font-weight: 500;
}

:deep(.section-dialog .el-dialog__headerbtn) {
  top: 20px;
  right: 20px;
}

:deep(.section-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: var(--text-color-secondary);
}

:deep(.section-dialog .el-dialog__headerbtn:hover .el-dialog__close) {
  color: var(--primary-color);
}

.section-content {
  padding: 1.5rem;
  color: var(--text-color);
  background: var(--bg-color);
}

.content-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.content-header h3 {
  font-size: 1.5rem;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.content-header .description {
  color: var(--text-color-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
}

.content-body {
  line-height: 1.8;
  color: var(--text-color);
  font-size: 1rem;
}

/* 确保对话框中的代码块和其他元素样式一致 */
/* 代码块样式统一 */
:deep(.code-block),
:deep(.content-body .code-block) {
  position: relative;
  margin: 1rem 0;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: border-color 0.3s ease;
}

:deep(.code-block pre),
:deep(.content-body .code-block pre) {
  margin: 0;
  padding: 0;
  background: transparent;
}

:deep(.code-block code),
:deep(.content-body .code-block code) {
  display: block;
  padding: 2.5rem 1rem 1rem;
  font-family: 'Fira Code', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  tab-size: 2;
  background-color: var(--bg-color);
  color: var(--text-color);
  white-space: pre;
}

:deep(.code-lang),
:deep(.content-body .code-lang) {
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

:deep(.code-block:hover),
:deep(.content-body .code-block:hover) {
  border-color: var(--primary-color);
}

/* 确保代码内容在语言标签下方显示正确 */
:deep(.code-block code),
:deep(.content-body .code-block code) {
  padding-top: 2.5rem;
}

.content-body :deep(.markdown-preview) {
  padding: 0;
  background: transparent;
}

/* 思考块样式 */
.think-block {
  margin: 1.5rem 0;
  padding: 1.5rem;
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.think-header {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--primary-color);
  font-weight: 500;
  font-size: 1rem;
}

.think-header i {
  font-size: 1.2rem;
}

.think-content {
  color: var(--text-color);
  font-size: 0.95rem;
  line-height: 1.6;
}

.think-content :deep(.markdown-preview) {
  background: transparent;
  padding: 0;
}

/* 动画效果 */
.message-content.streaming .think-block {
  animation: think-pulse 2s infinite;
}


:deep(.copy-button),
:deep(.content-body .copy-button) {
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
}

:deep(.code-block:hover .copy-button),
:deep(.content-body .code-block:hover .copy-button) {
  opacity: 0.9;
}

:deep(.copy-button:hover),
:deep(.content-body .copy-button:hover) {
  opacity: 1;
  transform: scale(1.05);
  background: var(--primary-color);
}

:deep(.copy-button i),
:deep(.content-body .copy-button i) {
  color: var(--bg-color);
  font-size: 0.9rem;
}

:deep(.copy-button:active),
:deep(.content-body .copy-button:active) {
  transform: scale(0.95);
}

:deep(.copy-button i),
:deep(.content-body .copy-button i) {
  font-size: 0.9rem;
  color: var(--bg-color);
}

:deep(.code-block .copy-button:hover) {
  background: rgba(var(--primary-color-rgb), 0.2);
}

:deep(.code-block .copy-button i) {
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

/* 代码块的语言标签和复制按钮 */
:deep(.code-lang),
:deep(.content-body .code-lang) {
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


/* 黑暗模式下的代码块样式调整 */
:deep(.code-block),
:deep(.content-body .code-block) {
  background: var(--bg-color);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.code-block code),
:deep(.content-body .code-block code) {
  display: block;
  padding: 2.5rem 1rem 1rem;  /* 增加顶部内边距，为语言标签和复制按钮留出空间 */
  font-family: 'Fira Code', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  tab-size: 2;
  background-color: var(--bg-color);
  color: var(--text-color);
  white-space: pre;
}

/* 优化复制按钮样式 */
:deep(.code-block .copy-button),
:deep(.content-body .code-block .copy-button) {
  top: 4px;
  right: 4px;
  padding: 4px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--primary-color-rgb), 0.1);
  transition: all 0.3s ease;
}

:deep(.code-block .copy-button:active) {
  transform: scale(0.95);
}

:deep(.code-block .copy-button:hover) {
  background: rgba(var(--primary-color-rgb), 0.2);
}

:deep(.code-block .copy-button i) {
  transition: transform 0.3s ease;
}

:deep(.code-block .copy-button:active i) {
  transform: scale(0.9);
}

/* 代码高亮的颜色方案 */
:deep(.hljs-keyword),
:deep(.content-body .hljs-keyword) {
  color: #c678dd;
}

:deep(.hljs-string),
:deep(.content-body .hljs-string) {
  color: #98c379;
}

:deep(.hljs-number),
:deep(.content-body .hljs-number) {
  color: #d19a66;
}

:deep(.hljs-function),
:deep(.content-body .hljs-function) {
  color: #61afef;
}

:deep(.hljs-params),
:deep(.content-body .hljs-params) {
  color: #e06c75;
}

:deep(.hljs-comment),
:deep(.content-body .hljs-comment) {
  color: #7f848e;
  font-style: italic;
}

:deep(.hljs-class),
:deep(.content-body .hljs-class) {
  color: #e5c07b;
}

:deep(.hljs-variable),
:deep(.content-body .hljs-variable) {
  color: #e06c75;
}

:deep(.hljs-operator),
:deep(.content-body .hljs-operator) {
  color: #56b6c2;
}

/* 表格样式 */
:deep(.table-wrapper) {
  margin: 1rem 0;
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

:deep(.table-wrapper table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0;
  border: none;
}

:deep(.table-wrapper::-webkit-scrollbar) {
  height: 6px;
}

:deep(.table-wrapper::-webkit-scrollbar-thumb) {
  background-color: var(--border-color);
  border-radius: 3px;
}

:deep(.table-wrapper::-webkit-scrollbar-track) {
  background-color: transparent;
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

/* 图片样式 */
:deep(.image-wrapper) {
  margin: 1rem 0;
  text-align: center;
}

:deep(.image-wrapper img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

:deep(.image-caption) {
  margin-top: 0.5rem;
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

/* 链接样式 */
:deep(a) {
  color: var(--primary-color);
  text-decoration: none;
  transition: all 0.3s ease;
  border-bottom: 1px dashed var(--primary-color);
  padding-bottom: 1px;
}

:deep(a:hover) {
  opacity: 0.8;
}

:deep(a[target="_blank"])::after {
  content: "↗";
  display: inline-block;
  margin-left: 4px;
  font-size: 0.8em;
}

/* 其他 markdown 元素样式 */
:deep(blockquote) {
  margin: 1rem 0;
  padding: 1rem;
  border-left: 4px solid var(--primary-color);
  background: rgba(var(--primary-color-rgb), 0.05);
  border-radius: 4px;
}

:deep(hr) {
  margin: 2rem 0;
  border: none;
  border-top: 1px solid var(--border-color);
}

:deep(ul), :deep(ol) {
  padding-left: 1.5rem;
  margin: 1rem 0;
}

:deep(li) {
  margin: 0.5rem 0;
}

/* 动画 */
@keyframes flow {
  0% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes cursor-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

@keyframes think-pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(var(--primary-color-rgb), 0.2);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(var(--primary-color-rgb), 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(var(--primary-color-rgb), 0);
  }
}

/* Element Plus 深色模式覆盖 */
:deep(.el-tree--highlight-current .el-tree-node.is-current>.el-tree-node__content) {
  background-color: rgba(var(--primary-color-rgb), 0.1);
}

:deep(.el-dialog__body) {
  padding: 0;
  color: var(--text-color);
}
</style>