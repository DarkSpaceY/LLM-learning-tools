<template>
  <div class="tutorial-container">
    <!-- 左侧：文件选择和教程树 -->
    <div class="outline-panel">
      <div class="file-selector">
        <h3>{{ t('选择教程文件') }}</h3>
        <div class="file-select-container">
          <el-select
            v-model="selectedFile"
            filterable
            clearable
            :placeholder="t('请选择教程文件')"
            @change="handleFileChange"
            class="file-select"
          >
            <el-option
              v-for="file in tutorialFiles"
              :key="file.id"
              :label="file.title"
              :value="file.id"
            >
              <div class="file-option">
                <span class="file-title">{{ file.title }}</span>
                <span class="file-date">{{ formatDate(file.metadata.created_at) }}</span>
              </div>
            </el-option>
          </el-select>
          <el-button
            v-if="selectedFile"
            type="danger"
            link
            @click="handleDelete"
            class="delete-button"
          >
            <i class="fas fa-trash"></i>
            {{ t('删除') }}
          </el-button>
        </div>
      </div>
  
      <div v-if="selectedFile" class="tree-container">
        <h3>{{ t('教程目录') }}</h3>
        <el-tree
          :data="tutorialTree"
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
    </div>

    <!-- 右侧：内容区域 -->
    <div class="content-panel">
      <template v-if="selectedSection">
        <div class="content-header">
          <h2>{{ selectedSection.title }}</h2>
          <p class="description">{{ selectedSection.description }}</p>
        </div>
        <div class="content-body">
          <MarkdownDisplay :content="selectedSection.content" />
        </div>
      </template>
      <div v-else class="empty-state">
        {{ t('请从左侧选择要查看的内容') }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSettings, t } from '../store/settings'
import MarkdownDisplay from '../components/MarkdownDisplay.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const settings = useSettings()
const tutorialFiles = ref([])
const selectedFile = ref('')
const tutorialTree = ref([])
const selectedSection = ref(null)

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// 处理文件选择
const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      t('确定要删除这个教程吗？此操作不可恢复。'),
      t('删除确认'),
      {
        confirmButtonText: t('删除'),
        cancelButtonText: t('取消'),
        type: 'warning'
      }
    )

    const response = await fetch(`/api/tutorials/${selectedFile.value}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    
    if (data.success) {
      ElMessage.success(t('教程删除成功'))
      selectedFile.value = ''
      tutorialTree.value = []
      selectedSection.value = null
      await loadTutorialFiles()
    } else {
      throw new Error(data.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete tutorial:', error)
      ElMessage.error(t('删除教程失败'))
    }
  }
}

const handleFileChange = async (fileId) => {
  selectedSection.value = null
  if (!fileId) {
    tutorialTree.value = []
    selectedSection.value = null
    return
  }

  try {
    const response = await fetch(`/api/tutorials/${fileId}`)
    const data = await response.json()
    if (data.success) {
      tutorialTree.value = data.data.children
      selectedSection.value = null
    }
  } catch (error) {
    console.error('Failed to load tutorial:', error)
    ElMessage.error(t('加载教程失败'))
  }
}

// 加载教程文件列表
const loadTutorialFiles = async () => {
  try {
    const response = await fetch('/api/tutorials/list')
    const data = await response.json()
    if (data.success) {
      tutorialFiles.value = data.data
    }
  } catch (error) {
    console.error('Failed to load tutorial files:', error)
    ElMessage.error(t('加载教程列表失败'))
  }
}

const defaultProps = {
  children: 'children',
  label: 'label'
}

// 处理节点点击
const handleNodeClick = (data) => {
  if (data.type === 'section') {
    selectedSection.value = data
  }
}

// 查看内容
const viewContent = (data) => {
  selectedSection.value = data
}

// 加载教程列表
const loadTutorials = async () => {
  try {
    const response = await fetch('/api/tutorials/list')
    const data = await response.json()
    if (data.success) {
      tutorialTree.value = data.tutorials
    }
  } catch (error) {
    console.error('Failed to load tutorials:', error)
    ElMessage.error(t('加载教程失败'))
  }
}

onMounted(() => {
  loadTutorialFiles()
})
</script>

<style scoped>
.tutorial-container {
  height: 100vh;
  display: flex;
  background: var(--bg-color);
  color: var(--text-color);
}

/* 左侧面板 */
.outline-panel {
  width: 300px;
  border-right: 1px solid var(--border-color);
  padding: 1rem;
  overflow-y: auto;
  background: var(--bg-color);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.file-selector {
  margin-bottom: 1rem;
}

.file-select-container {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-top: 0.5rem;
}

.file-select {
  flex: 1;
}

.delete-button {
  padding: 8px;
  font-size: 0.9rem;
}

.delete-button i {
  margin-right: 4px;
}

.file-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-title {
  color: var(--text-color);
  font-weight: 500;
}

.file-date {
  color: var(--text-color-secondary);
  font-size: 0.8rem;
}

.tree-container {
  flex: 1;
  overflow-y: auto;
}

.outline-panel h3 {
  margin-bottom: 1rem;
  color: var(--primary-color);
  font-size: 1.2rem;
}

/* 内容面板 */
.content-panel {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.content-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.content-header h2 {
  margin-bottom: 0.5rem;
  color: var(--text-color);
  font-size: 1.8rem;
}

.description {
  color: var(--text-color-secondary);
  font-size: 1rem;
  line-height: 1.6;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-color-secondary);
  font-size: 1.1rem;
}

/* 继承 HomeView 的树样式 */
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
</style>