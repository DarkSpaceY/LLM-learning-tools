<template>
  <div class="simulation-builder-container">
    <div class="builder-header">
      <h2>{{ t('仿真构建器') }}</h2>
      <p class="description">{{ t('创建交互式学习仿真，可视化复杂概念和过程') }}</p>
    </div>

    <div class="builder-content">
      <div class="input-section">
        <h3>{{ t('模型交互') }}</h3>
        <el-form :model="formData" label-position="top">
          <el-form-item :label="t('仿真名称')">
            <el-input
              v-model="formData.name"
              :placeholder="t('请输入仿真名称')"
            />
          </el-form-item>

          <el-form-item :label="t('代码生成提示')">
            <el-input
              type="textarea"
              v-model="formData.prompt"
              :rows="4"
              :placeholder="t('请描述您想要生成的仿真代码，例如：创建一个弹簧振子模型，或者绘制二次函数及其导数')"
            />
          </el-form-item>

          <el-form-item :label="t('从文件导入')">
            <el-upload
              class="upload-demo"
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              accept=".txt,.js,.html"
              :on-change="handleFileChange"
            >
              <el-button type="primary">
                {{ t('选择文件') }}
              </el-button>
              <template #tip>
                <div class="el-upload__tip">
                  {{ t('支持 .txt, .js, .html 文件') }}
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>

        <div class="action-buttons">
          <el-button
            type="primary"
            @click="buildSimulation"
            :loading="isLoading"
          >
            {{ t('构建仿真') }}
          </el-button>
          <el-button @click="resetForm">{{ t('重置') }}</el-button>
        </div>
      </div>

      <div class="preview-section">
        <div class="code-section" v-if="formData.generatedCode">
          <div class="code-header">
            <h4>{{ t('生成的代码') }}</h4>
            <el-button-group>
              <el-button
                type="primary"
                icon="VideoPlay"
                @click="executeCode"
                :loading="isLoading"
              >
                {{ t('执行代码') }}
              </el-button>
              <el-button
                type="info"
                icon="Edit"
                @click="editCode"
              >
                {{ t('编辑代码') }}
              </el-button>
            </el-button-group>
          </div>
          <div class="code-editor" ref="codeEditor"></div>
        </div>

        <SimulationPreview
          v-if="simulation"
          :html="formData.generatedCode"
          :title="simulationData.title"
          :description="simulationData.description"
          :simulation-id="simulationData.id"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { useSettings, t } from '../../store/settings'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import SimulationPreview from '../../components/SimulationPreview.vue'
import * as monaco from 'monaco-editor'

const settings = useSettings()

// 表单数据
const formData = reactive({
  name: '',
  prompt: '',
  generatedCode: ''
})

// 处理文件上传
const handleFileChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    formData.generatedCode = e.target.result
    initializeCodeEditor()
  }
  reader.onerror = (e) => {
    ElMessage.error(t('文件读取失败'))
    console.error('文件读取错误:', e)
  }
  reader.readAsText(file.raw)
}

// 仿真环境数据结构
const simulationData = reactive({
  id: '',
  title: '',
  description: '',
  code: '',
  parameters: {}
})

// 状态管理
const isLoading = ref(false)
const simulation = ref(null)
const simulationCanvas = ref(null)
const codeEditor = ref(null)

// 生成代码
const generateCode = async () => {
  if (!formData.name || !formData.prompt) {
    ElMessage.warning(t('请完整填写仿真名称和代码生成提示'))
    return
  }

  isLoading.value = true
  try {
    const response = await axios.post('/api/simulation/generate', {
      topic: formData.prompt
    })
    console.log(response.data.data)
    const { id, title, description, code, parameters } = response.data.data
    simulationData.id = id
    simulationData.title = title
    simulationData.description = description
    simulationData.code = code
    simulationData.parameters = parameters
    formData.generatedCode = code
    initializeCodeEditor()
  } catch (error) {
    ElMessage.error(t('代码生成失败，请稍后重试'))
    console.error('代码生成失败:', error)
  } finally {
    isLoading.value = false
  }
}

let editor = null

// 初始化代码编辑器
const initializeCodeEditor = () => {
  if (!codeEditor.value) return
  
  if (editor) {
    editor.setValue(formData.generatedCode)
    return
  }

  editor = monaco.editor.create(codeEditor.value, {
    value: formData.generatedCode,
    language: 'javascript',
    theme: 'vs-dark',
    minimap: { enabled: true },
    automaticLayout: true,
    fontSize: 14,
    lineNumbers: 'on',
    scrollBeyondLastLine: false,
    roundedSelection: false,
    readOnly: false,
    cursorStyle: 'line',
    selectOnLineNumbers: true,
    contextmenu: true,
    scrollbar: {
      useShadows: false,
      verticalHasArrows: true,
      horizontalHasArrows: true,
      vertical: 'visible',
      horizontal: 'visible',
      verticalScrollbarSize: 10,
      horizontalScrollbarSize: 10,
      arrowSize: 30
    }
  })
}

// 编辑代码
const editCode = () => {
  if (!editor) return
  formData.generatedCode = editor.getValue()
}

// 执行代码
const executeCode = async () => {
  if (!formData.generatedCode) {
    ElMessage.warning(t('请先生成或编辑代码'))
    return
  }

  isLoading.value = true
  try {
    simulation.value = true
  } catch (error) {
    ElMessage.error(t('代码执行失败，请检查代码是否正确'))
    console.error('执行失败:', error)
    simulation.value = null
  } finally {
    isLoading.value = false
  }
}

// 构建仿真
const buildSimulation = async () => {
  await generateCode()
  if (formData.generatedCode) {
    await executeCode()
  }
}

// 重置表单
const resetForm = () => {
  formData.name = ''
  formData.prompt = ''
  formData.generatedCode = ''
  simulation.value = null
  if (editor) {
    editor.setValue('')
  }
}

// 组件卸载前清理编辑器实例
onBeforeUnmount(() => {
  if (editor) {
    editor.dispose()
    editor = null
  }
})
</script>

<style scoped>
.simulation-builder-container {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.builder-header {
  margin-bottom: 3rem;
  text-align: center;
  padding: 1rem;
  background: var(--bg-color-overlay);
  border-radius: 8px;
}

.builder-header h2 {
  color: var(--el-color-primary);
  margin-bottom: 1rem;
  font-size: 2rem;
  font-weight: 600;
}

.description {
  color: var(--el-text-color-secondary);
  font-size: 1.2rem;
  line-height: 1.6;
}

.builder-content {
  display: grid;
  grid-template-columns: minmax(300px, 1fr) minmax(500px, 2fr);
  gap: 2rem;
}

.input-section {
  background-color: var(--el-bg-color);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: var(--el-box-shadow-light);
  height: fit-content;
}

.action-buttons {
  margin-top: 2.5rem;
  display: flex;
  gap: 1.2rem;
  justify-content: flex-end;
}

.preview-section {
  background: var(--el-bg-color);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: var(--el-box-shadow-light);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.code-section {
  background: var(--el-fill-color-light);
  border-radius: 8px;
  padding: 1rem;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.code-header h4 {
  color: var(--el-text-color-primary);
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0;
}

.code-editor {
  background: var(--el-bg-color);
  border-radius: 4px;
  border: 1px solid var(--el-border-color);
  transition: border-color 0.3s;
}

.code-editor:hover {
  border-color: var(--el-color-primary);
}

.code-editor textarea {
  border: none;
  outline: none;
  resize: vertical;
  padding: 1rem;
  background: transparent;
  color: var(--el-text-color-regular);
}

.simulation-info {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--el-bg-color-overlay);
  border-radius: 8px;
}

.simulation-info h4 {
  color: var(--el-color-primary);
  font-size: 1.2rem;
  margin: 0 0 0.8rem 0;
}

.simulation-info p {
  color: var(--el-text-color-regular);
  margin: 0.5rem 0;
  line-height: 1.4;
}

.simulation-info .simulation-id {
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
  margin-top: 1rem;
}

.simulation-preview {
  width: 100%;
  height: calc(100vh - 300px);
  min-height: 400px;
  border: none;
  overflow: hidden;
  background: var(--el-bg-color);
  transition: all 0.3s ease;
  box-shadow: var(--el-box-shadow-light);
  border-radius: 12px;
}

@media (max-width: 1200px) {
  .builder-content {
    grid-template-columns: 1fr;
  }
  
  .simulation-canvas {
    height: 400px;
  }
}
</style>