<template>
  <div class="concept-analyzer-container">
    <div class="analyzer-header">
      <h2>{{ t('概念分析器') }}</h2>
      <p class="description">{{ t('深入分析概念的定义、特征和关联关系') }}</p>
    </div>

    <div class="analyzer-content">
      <div class="input-section">
        <h3>{{ t('概念输入') }}</h3>
        <el-form :model="formData" label-position="top">
          <el-form-item :label="t('概念名称')">
            <el-input
              v-model="formData.concept"
              :placeholder="t('请输入要分析的概念名称')"
            />
          </el-form-item>

          <el-form-item :label="t('学科领域')">
            <el-select
              v-model="formData.domain"
              :placeholder="t('请选择学科领域')"
            >
              <el-option
                v-for="domain in domainOptions"
                :key="domain.value"
                :label="t(domain.label)"
                :value="domain.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item :label="t('分析维度')">
            <el-checkbox-group v-model="formData.dimensions">
              <el-checkbox
                v-for="dim in dimensionOptions"
                :key="dim.value"
                :label="dim.value"
              >
                {{ t(dim.label) }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>

        <div class="action-buttons">
          <el-button
            type="primary"
            @click="analyzeConcept"
            :loading="isLoading"
          >
            {{ t('开始分析') }}
          </el-button>
          <el-button @click="resetForm">{{ t('重置') }}</el-button>
        </div>
      </div>

      <div class="result-section" v-if="analysis">
        <h3>{{ t('分析结果') }}</h3>

        <el-tabs v-model="activeTab" class="analysis-tabs">
          <el-tab-pane :label="t('基本信息')" name="basic">
            <el-card class="info-card">
              <template #header>
                <div class="card-header">
                  <h4>{{ analysis.concept }}</h4>
                  <el-tag>{{ t(analysis.domain) }}</el-tag>
                </div>
              </template>
              
              <div class="definition-section">
                <h5>{{ t('定义') }}</h5>
                <p>{{ analysis.definition }}</p>
              </div>

              <div class="characteristics-section">
                <h5>{{ t('核心特征') }}</h5>
                <ul>
                  <li v-for="(char, index) in analysis.characteristics" :key="index">
                    {{ char }}
                  </li>
                </ul>
              </div>

              <div class="examples-section">
                <h5>{{ t('典型示例') }}</h5>
                <el-collapse>
                  <el-collapse-item
                    v-for="(example, index) in analysis.examples"
                    :key="index"
                    :title="example.title"
                  >
                    <p>{{ example.description }}</p>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </el-card>
          </el-tab-pane>

          <el-tab-pane :label="t('关系网络')" name="relations">
            <el-card class="network-card">
              <div class="network-controls">
                <el-radio-group v-model="networkView" size="small">
                  <el-radio-button value="graph">{{ t('图形视图') }}</el-radio-button>
                  <el-radio-button value="list">{{ t('列表视图') }}</el-radio-button>
                </el-radio-group>
              </div>

              <div v-if="networkView === 'graph'" class="network-graph">
                <!-- 这里将使用可视化库（如 ECharts）渲染关系图 -->
                <div class="graph-container" ref="graphContainer"></div>
              </div>

              <div v-else class="network-list">
                <div
                  v-for="(group, type) in analysis.relations"
                  :key="type"
                  class="relation-group"
                >
                  <h5>{{ t(type) }}</h5>
                  <el-tag
                    v-for="relation in group"
                    :key="relation.concept"
                    :type="getRelationType(type)"
                    class="relation-tag"
                    @click="handleRelationClick(relation)"
                  >
                    {{ relation.concept }}
                    <span class="relation-strength" v-if="relation.strength">
                      ({{ relation.strength }})
                    </span>
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-tab-pane>

          <el-tab-pane :label="t('应用场景')" name="applications">
            <el-card class="applications-card">
              <div class="scenarios-list">
                <el-timeline>
                  <el-timeline-item
                    v-for="(scenario, index) in analysis.applications"
                    :key="index"
                    :timestamp="scenario.field"
                    :type="getScenarioType(scenario.relevance)"
                  >
                    <h5>{{ scenario.title }}</h5>
                    <p>{{ scenario.description }}</p>
                    <div class="scenario-tags">
                      <el-tag
                        v-for="tag in scenario.tags"
                        :key="tag"
                        size="small"
                        effect="plain"
                      >
                        {{ tag }}
                      </el-tag>
                    </div>
                  </el-timeline-item>
                </el-timeline>
              </div>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useSettings, t } from '../../store/settings'
import { ElMessage } from 'element-plus'
import axios from 'axios'
// 假设我们使用 ECharts 进行关系图可视化
import * as echarts from 'echarts'

const settings = useSettings()

// 学科领域选项
const domainOptions = [
  { value: 'math', label: '数学' },
  { value: 'physics', label: '物理' },
  { value: 'chemistry', label: '化学' },
  { value: 'biology', label: '生物' },
  { value: 'computer', label: '计算机' },
  { value: 'other', label: '其他' }
]

// 分析维度选项
const dimensionOptions = [
  { value: 'definition', label: '概念定义' },
  { value: 'characteristics', label: '核心特征' },
  { value: 'relations', label: '关联关系' },
  { value: 'examples', label: '典型示例' },
  { value: 'applications', label: '应用场景' }
]

// 表单数据
const formData = reactive({
  concept: '',
  domain: '',
  dimensions: ['definition', 'characteristics', 'relations']
})

// 状态管理
const isLoading = ref(false)
const analysis = ref(null)
const activeTab = ref('basic')
const networkView = ref('graph')
const graphContainer = ref(null)
let graphInstance = null

// 分析概念
const analyzeConcept = async () => {
  if (!formData.concept || !formData.domain || formData.dimensions.length === 0) {
    ElMessage.warning(t('请完整填写分析信息'))
    return
  }

  isLoading.value = true
  try {
    const response = await axios.post('/api/tools/concept-analyzer/analyze', {
      concept: formData.concept,
      domain: formData.domain,
      dimensions: formData.dimensions
    })
    analysis.value = response.data.analysis
    
    // 如果有关系数据，在下一个 tick 初始化图形
    if (analysis.value.relations && networkView.value === 'graph') {
      nextTick(() => {
        initGraph()
      })
    }
  } catch (error) {
    ElMessage.error(t('分析失败，请稍后重试'))
    console.error('分析失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.concept = ''
  formData.domain = ''
  formData.dimensions = ['definition', 'characteristics', 'relations']
  analysis.value = null
  if (graphInstance) {
    graphInstance.dispose()
    graphInstance = null
  }
}

// 获取关系类型样式
const getRelationType = (type) => {
  const types = {
    'prerequisite': 'info',
    'related': 'success',
    'derived': 'warning',
    'application': 'danger'
  }
  return types[type] || ''
}

// 获取场景类型
const getScenarioType = (relevance) => {
  const types = {
    'high': 'success',
    'medium': 'warning',
    'low': 'info'
  }
  return types[relevance] || 'info'
}

// 处理关系点击
const handleRelationClick = (relation) => {
  formData.concept = relation.concept
  analyzeConcept()
}

// 初始化关系图
const initGraph = () => {
  if (!graphContainer.value) return

  if (graphInstance) {
    graphInstance.dispose()
  }

  graphInstance = echarts.init(graphContainer.value)
  
  // 这里需要根据实际数据结构转换为 ECharts 图形数据
  const graphData = convertToGraphData(analysis.value.relations)
  
  const option = {
    title: {
      text: t('概念关系网络'),
      top: 'bottom',
      left: 'right'
    },
    tooltip: {
      trigger: 'item'
    },
    legend: {
      data: Object.keys(analysis.value.relations).map(type => t(type))
    },
    animationDurationUpdate: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [{
      type: 'graph',
      layout: 'force',
      data: graphData.nodes,
      links: graphData.links,
      categories: graphData.categories,
      roam: true,
      label: {
        show: true,
        position: 'right'
      },
      force: {
        repulsion: 100
      }
    }]
  }

  graphInstance.setOption(option)
}

// 转换关系数据为图形数据
const convertToGraphData = (relations) => {
  const nodes = [{
    id: formData.concept,
    name: formData.concept,
    symbolSize: 50,
    category: 'center'
  }]
  
  const links = []
  const categories = [{ name: 'center' }]

  Object.entries(relations).forEach(([type, items]) => {
    categories.push({ name: type })
    
    items.forEach(item => {
      nodes.push({
        id: item.concept,
        name: item.concept,
        symbolSize: 30,
        category: type
      })
      
      links.push({
        source: formData.concept,
        target: item.concept,
        value: item.strength || 1
      })
    })
  })

  return { nodes, links, categories }
}

// 监听窗口大小变化
onMounted(() => {
  window.addEventListener('resize', () => {
    if (graphInstance) {
      graphInstance.resize()
    }
  })
})
</script>

<style scoped>
.concept-analyzer-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.analyzer-header {
  margin-bottom: 2rem;
  text-align: center;
}

.analyzer-header h2 {
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.description {
  color: var(--text-color-secondary);
  font-size: 1.1rem;
}

.analyzer-content {
  display: grid;
  gap: 2rem;
}

.input-section {
  background-color: var(--bg-color);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.action-buttons {
  margin-top: 2rem;
  display: flex;
  gap: 1rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h4 {
  margin: 0;
  color: var(--primary-color);
}

.definition-section,
.characteristics-section,
.examples-section {
  margin-bottom: 2rem;
}

.definition-section h5,
.characteristics-section h5,
.examples-section h5 {
  color: var(--text-color);
  margin-bottom: 1rem;
}

.characteristics-section ul {
  list-style-type: disc;
  padding-left: 1.5rem;
}

.network-controls {
  margin-bottom: 1rem;
  text-align: right;
}

.network-graph {
  height: 600px;
}

.graph-container {
  width: 100%;
  height: 100%;
}

.relation-group {
  margin-bottom: 1.5rem;
}

.relation-group h5 {
  margin-bottom: 1rem;
  color: var(--text-color);
}

.relation-tag {
  margin: 0.25rem;
  cursor: pointer;
}

.relation-strength {
  font-size: 0.9em;
  opacity: 0.8;
}

.scenarios-list {
  padding: 1rem;
}

.scenario-tags {
  margin-top: 0.5rem;
}

.scenario-tags .el-tag {
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
}
</style>