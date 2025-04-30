<template>
  <div class="content-generator">
    <!-- 生成阶段进度显示 -->
    <div class="progress-container">
      <div class="stage-info">
        <el-tag
          v-if="currentStage"
          :type="getStageType(currentStage)"
          class="stage-tag"
        >
          {{ stageDisplayText[currentStage] || currentStage }}
        </el-tag>
        <span class="status-message">{{ statusMessage }}</span>
      </div>
      <el-progress
        v-if="currentStage"
        :percentage="calculateProgress(currentStage)"
        :status="getProgressStatus(currentStage)"
        :stroke-width="20"
        :show-text="true"
        :format="formatProgress"
        class="stage-progress"
      />
      <div v-if="errors.length" class="error-message">
        <p v-for="(error, index) in errors" :key="index">{{ error }}</p>
      </div>
    </div>

    <!-- 生成的内容树形结构 -->
    <div class="content-tree" v-if="chapters.length" :class="{'generating': currentStage !== 'complete'}">
      <el-tree
        :data="treeData"
        :props="defaultProps"
        node-key="id"
        default-expand-all
        @node-click="handleNodeClick"
      >
        <template #default="{ node, data }">
          <span class="custom-tree-node">
            <span class="node-content" :class="{'generating': isGenerating(data)}">
              <div class="title-row">
                <strong>{{ data.data.title }}</strong>
                <el-tag
                  size="small"
                  :type="getNodeType(data)"
                  class="node-type"
                >
                  {{ data.type === 'chapter' ? '章节' : '小节' }}
                </el-tag>
              </div>
              <p class="description">{{ data.data.description }}</p>
            </span>
            <span v-if="data.type === 'section'" class="node-actions">
              <el-button
                type="primary"
                size="small"
                :disabled="!data.data.content"
                @click.stop="showContent(data)"
              >
                查看内容
                <i class="el-icon-view"></i>
              </el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </div>

    <!-- 内容详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="selectedNode?.title || '内容详情'"
      width="70%"
      :before-close="handleDialogClose"
    >
      <template #default>
        <div v-if="selectedNode" class="content-detail">
          <div class="content-header">
            <h3 class="section-title">{{ selectedNode.title }}</h3>
            <p class="section-description">{{ selectedNode.description }}</p>
          </div>
          <div class="content-section">
            <div v-for="(paragraph, index) in selectedNode.content"
                 :key="index"
                 class="content-paragraph"
            >
              {{ paragraph }}
            </div>
          </div>
        </div>
      </template>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElDialog, ElProgress, ElTree, ElButton, ElTag } from 'element-plus'

// 辅助函数
const getStageType = (stage) => {
  switch (stage) {
    case 'chapters':
      return 'primary'
    case 'sections':
      return 'success'
    case 'content':
      return 'warning'
    case 'error':
      return 'danger'
    default:
      return 'info'
  }
}

const getNodeType = (node) => {
  if (node.type === 'chapter') {
    return currentStage.value === 'chapters' ? 'primary' : 'success'
  } else {
    return currentStage.value === 'sections' ? 'warning' : 'success'
  }
}

const isGenerating = (node) => {
  if (node.type === 'chapter') {
    return currentStage.value === 'chapters'
  } else {
    return currentStage.value === 'sections'
  }
}

const calculateProgress = (stage) => {
  const currentValue = progress.value[stage] || 0
  const maxValue = stage === 'chapters' ? 5 : 20
  return Math.round((currentValue / maxValue) * 100)
}

const getProgressStatus = (stage) => {
  if (stage === 'error') return 'exception'
  return calculateProgress(stage) === 100 ? 'success' : ''
}

const formatProgress = (percentage) => {
  if (percentage === 100) return '完成'
  return `${percentage}%`
}

// 状态和数据
const currentStage = ref('')
const statusMessage = ref('')
const chapters = ref([])
const sections = ref({})  // 章节ID到小节列表的映射
const errors = ref([])
const progress = ref({
  chapters: 0,
  sections: 0,
  content: 0
})

// 状态对应的显示文本
const stageDisplayText = {
  chapters: '正在生成章节大纲...',
  sections: '正在生成小节内容...',
  content: '正在生成详细内容...'
}

// 树形结构配置
const defaultProps = {
  children: 'children',
  label: 'label'
}

// 计算树形数据
const treeData = computed(() => {
  return chapters.value.map(chapter => ({
    id: `chapter-${chapter.number}`,
    label: `${chapter.title}\n${chapter.description}`,
    type: 'chapter',
    data: chapter,
    children: (sections.value[chapter.number] || []).map(section => ({
      id: `section-${section.number}`,
      label: `${section.title}\n${section.description}`,
      type: 'section',
      data: section
    }))
  }))
})

// 节点点击和内容显示
const selectedNode = ref(null)
const dialogVisible = ref(false)

const handleNodeClick = (data) => {
  if (data.type === 'section') {
    showContent(data)
  }
}

const showContent = (node) => {
  selectedNode.value = node.data
  dialogVisible.value = true
}

// 处理JSON消息
const processMessage = (data) => {
  try {
    if (!data || !data.type) {
      console.error('无效的消息格式:', data)
      return
    }

    switch(data.type) {
      case 'progress':
        handleProgress(data)
        break
      case 'chapter':
        addChapter(data.data)
        break
      case 'section':
        addSection(data.data)
        break
      case 'content':
        updateSectionContent(data.data)
        break
      case 'error':
        handleError(data.message)
        break
    }
  } catch (e) {
    console.error('处理消息失败:', e)
  }
}

// 处理进度更新
const handleProgress = (data) => {
  // 更新当前阶段
  currentStage.value = data.stage
  
  // 清理旧的进度
  if (data.status === 'start') {
    progress.value[data.stage] = 0
    statusMessage.value = stageDisplayText[data.stage]
    // 清理旧的内容
    if (data.stage === 'chapters') {
      chapters.value = []
      sections.value = {}
    } else if (data.stage === 'sections') {
      Object.keys(sections.value).forEach(key => {
        sections.value[key] = []
      })
    }
  }
  // 更新进度
  else if (data.status === 'complete') {
    progress.value[data.stage] = data.count || 0
    const count = progress.value[data.stage]
    switch (data.stage) {
      case 'chapters':
        statusMessage.value = `已完成章节大纲，共 ${count} 章`
        break
      case 'sections':
        statusMessage.value = `已完成小节结构，共 ${count} 个小节`
        break
      case 'content':
        statusMessage.value = `已完成详细内容，共 ${count} 个段落`
        currentStage.value = 'complete'
        break
    }
  }
}

// 添加章节
const addChapter = (chapter) => {
  const index = chapters.value.findIndex(c => c.number === chapter.number)
  if (index === -1) {
    chapters.value.push(chapter)
  } else {
    chapters.value[index] = chapter
  }
}

// 添加小节
const addSection = (section) => {
  const chapterNumber = parseInt(section.number.split('.')[0])
  if (!sections.value[chapterNumber]) {
    sections.value[chapterNumber] = []
  }
  const index = sections.value[chapterNumber].findIndex(
    s => s.number === section.number
  )
  if (index === -1) {
    sections.value[chapterNumber].push(section)
  } else {
    sections.value[chapterNumber][index] = section
  }
}

// 更新小节内容
const updateSectionContent = (data) => {
  const { chapter, section: sectionNumber, content } = data
  const sectionList = sections.value[chapter] || []
  const section = sectionList.find(s => s.number === sectionNumber)
  if (section) {
    if (!section.content) section.content = []
    section.content.push(content)
  }
}

// 处理错误
const handleError = (message) => {
  errors.value.push(message)
  statusMessage.value = message
  currentStage.value = 'error'
}

defineExpose({
  processMessage
})
</script>

<style scoped>
.content-generator {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.progress-container {
  padding: 20px;
  border-radius: 12px;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stage-tag {
  font-size: 1rem;
  padding: 8px 16px;
  border-radius: 6px;
}

.stage-progress {
  margin-top: 16px;
}

.stage-progress :deep(.el-progress-bar__outer) {
  border-radius: 8px;
  background-color: var(--border-color);
}

.stage-progress :deep(.el-progress-bar__inner) {
  border-radius: 8px;
  transition: width 0.3s ease-in-out;
}

.content-tree {
  padding: 20px;
  border-radius: 12px;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.content-tree.generating {
  opacity: 0.9;
  border: 1px solid var(--primary-color);
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 12px;
  white-space: pre-line;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.node-content {
  flex: 1;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.node-content.generating {
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
}

.title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.description {
  margin: 0;
  color: var(--text-color-secondary);
  font-size: 14px;
  line-height: 1.4;
}

.node-type {
  opacity: 0.8;
}

.custom-tree-node :deep(.el-tree-node__content) {
  height: auto;
  min-height: 40px;
}

.node-actions {
  margin-left: 20px;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.custom-tree-node:hover .node-actions {
  opacity: 1;
}

.node-actions .el-button {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.content-detail {
  padding: 24px;
  background: var(--bg-color);
  border-radius: 12px;
}

.content-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.section-title {
  font-size: 1.5rem;
  color: var(--text-color);
  margin-bottom: 8px;
  font-weight: 600;
}

.section-description {
  color: var(--text-color-secondary);
  font-size: 14px;
  line-height: 1.6;
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.content-paragraph {
  padding: 16px;
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  line-height: 1.8;
  color: var(--text-color);
  font-size: 15px;
  transition: all 0.3s ease;
}

.content-paragraph:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.resource-type {
  color: #909399;
  margin-left: 8px;
  font-size: 13px;
}

.resource-desc {
  color: #606266;
  margin: 5px 0 10px 20px;
  font-size: 14px;
  line-height: 1.6;
}

.error-message {
  color: #f56c6c;
  padding: 10px;
  border-radius: 4px;
  background-color: #fef0f0;
  margin: 10px 0;
}

.stage-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.status-message {
  color: var(--text-color);
  font-size: 14px;
}

:deep(.el-progress-bar__inner) {
  transition: all 0.3s ease;
}

:deep(.el-tag) {
  font-weight: 600;
}
</style>