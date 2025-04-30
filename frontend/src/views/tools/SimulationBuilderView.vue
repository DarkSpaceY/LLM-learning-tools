<template>
  <div class="simulation-builder-container">
    <div class="builder-header">
      <h2>{{ t('仿真构建器') }}</h2>
      <p class="description">{{ t('创建交互式学习仿真，可视化复杂概念和过程') }}</p>
    </div>

    <div class="builder-content">
      <div class="input-section">
        <h3>{{ t('仿真配置') }}</h3>
        <el-form :model="formData" label-position="top">
          <el-form-item :label="t('仿真名称')">
            <el-input
              v-model="formData.name"
              :placeholder="t('请输入仿真名称')"
            />
          </el-form-item>

          <el-form-item :label="t('仿真类型')">
            <el-select
              v-model="formData.type"
              :placeholder="t('请选择仿真类型')"
            >
              <el-option
                v-for="type in simulationTypes"
                :key="type.value"
                :label="t(type.label)"
                :value="type.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item :label="t('参数设置')">
            <div class="parameters-list">
              <div v-for="(param, index) in formData.parameters" :key="index" class="parameter-item">
                <el-input
                  v-model="param.name"
                  :placeholder="t('参数名称')"
                  class="param-name"
                />
                <el-input-number
                  v-model="param.value"
                  :placeholder="t('参数值')"
                  :controls-position="'right'"
                  class="param-value"
                />
                <el-button
                  type="danger"
                  icon="Delete"
                  circle
                  @click="removeParameter(index)"
                />
              </div>
              <el-button
                type="primary"
                plain
                icon="Plus"
                @click="addParameter"
              >
                {{ t('添加参数') }}
              </el-button>
            </div>
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

      <div class="preview-section" v-if="simulation">
        <h3>{{ t('仿真预览') }}</h3>
        <el-card class="simulation-card">
          <div class="simulation-controls">
            <div class="control-panel">
              <el-button-group>
                <el-button
                  type="primary"
                  icon="VideoPlay"
                  @click="startSimulation"
                  :disabled="isRunning"
                >
                  {{ t('开始') }}
                </el-button>
                <el-button
                  type="warning"
                  icon="VideoPause"
                  @click="pauseSimulation"
                  :disabled="!isRunning"
                >
                  {{ t('暂停') }}
                </el-button>
                <el-button
                  type="info"
                  icon="RefreshRight"
                  @click="resetSimulation"
                >
                  {{ t('重置') }}
                </el-button>
              </el-button-group>
            </div>

            <div class="simulation-canvas">
              <!-- Canvas for simulation rendering -->
              <canvas ref="simulationCanvas"></canvas>
            </div>

            <div class="simulation-stats">
              <el-descriptions :column="2" border>
                <el-descriptions-item :label="t('运行时间')">
                  {{ simulationTime }}s
                </el-descriptions-item>
                <el-descriptions-item :label="t('当前状态')">
                  <el-tag :type="getStatusType(simulationStatus)">
                    {{ t(simulationStatus) }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useSettings, t } from '../../store/settings'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const settings = useSettings()

// 仿真类型选项
const simulationTypes = [
  { value: 'physics', label: '物理仿真' },
  { value: 'chemistry', label: '化学反应' },
  { value: 'biology', label: '生物过程' },
  { value: 'math', label: '数学模型' }
]

// 表单数据
const formData = reactive({
  name: '',
  type: '',
  parameters: []
})

// 状态管理
const isLoading = ref(false)
const simulation = ref(null)
const isRunning = ref(false)
const simulationTime = ref(0)
const simulationStatus = ref('ready')
const simulationCanvas = ref(null)
let animationFrameId = null

// 添加参数
const addParameter = () => {
  formData.parameters.push({
    name: '',
    value: 0
  })
}

// 移除参数
const removeParameter = (index) => {
  formData.parameters.splice(index, 1)
}

// 构建仿真
const buildSimulation = async () => {
  if (!formData.name || !formData.type) {
    ElMessage.warning(t('请完整填写仿真信息'))
    return
  }

  isLoading.value = true
  try {
    const response = await axios.post('/api/tools/simulation-builder/build', {
      name: formData.name,
      type: formData.type,
      parameters: formData.parameters
    })
    simulation.value = response.data.simulation
    simulationStatus.value = 'ready'
    initializeSimulation()
  } catch (error) {
    ElMessage.error(t('构建失败，请稍后重试'))
    console.error('构建失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.name = ''
  formData.type = ''
  formData.parameters = []
  simulation.value = null
  resetSimulation()
}

// 初始化仿真
const initializeSimulation = () => {
  if (!simulationCanvas.value) return

  const ctx = simulationCanvas.value.getContext('2d')
  // Initialize canvas and simulation environment
  // This will be implemented based on specific simulation requirements
}

// 开始仿真
const startSimulation = () => {
  if (!simulation.value) return

  isRunning.value = true
  simulationStatus.value = 'running'
  animate()
}

// 暂停仿真
const pauseSimulation = () => {
  isRunning.value = false
  simulationStatus.value = 'paused'
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
}

// 重置仿真
const resetSimulation = () => {
  isRunning.value = false
  simulationTime.value = 0
  simulationStatus.value = 'ready'
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  initializeSimulation()
}

// 动画循环
const animate = () => {
  if (!isRunning.value) return

  simulationTime.value += 0.016 // Approximately 60 FPS
  updateSimulation()
  renderSimulation()

  animationFrameId = requestAnimationFrame(animate)
}

// 更新仿真状态
const updateSimulation = () => {
  if (!simulation.value) return

  // Update simulation state based on parameters and time
  // This will be implemented based on specific simulation requirements
}

// 渲染仿真
const renderSimulation = () => {
  if (!simulationCanvas.value) return

  const ctx = simulationCanvas.value.getContext('2d')
  // Render current simulation state
  // This will be implemented based on specific simulation requirements
}

// 获取状态样式
const getStatusType = (status) => {
  const types = {
    'ready': 'info',
    'running': 'success',
    'paused': 'warning',
    'error': 'danger'
  }
  return types[status] || 'info'
}

// 生命周期钩子
onMounted(() => {
  window.addEventListener('resize', initializeSimulation)
})

onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  window.removeEventListener('resize', initializeSimulation)
})
</script>

<style scoped>
.simulation-builder-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.builder-header {
  margin-bottom: 2rem;
  text-align: center;
}

.builder-header h2 {
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.description {
  color: var(--text-color-secondary);
  font-size: 1.1rem;
}

.builder-content {
  display: grid;
  gap: 2rem;
}

.input-section {
  background-color: var(--bg-color);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.parameters-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.parameter-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.param-name {
  flex: 2;
}

.param-value {
  flex: 1;
}

.action-buttons {
  margin-top: 2rem;
  display: flex;
  gap: 1rem;
}

.simulation-card {
  padding: 1rem;
}

.simulation-controls {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.control-panel {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.simulation-canvas {
  width: 100%;
  height: 400px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  overflow: hidden;
}

.simulation-canvas canvas {
  width: 100%;
  height: 100%;
}

.simulation-stats {
  margin-top: 1rem;
}
</style>