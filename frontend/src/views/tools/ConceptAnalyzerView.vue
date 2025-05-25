<template>
  <div class="concept-analyzer-container">
    <div class="analyzer-header">
      <h2>{{ t('概念分析器') }}</h2>
      <p class="description">{{ t('深入分析概念的定义、特征和关联关系') }}</p>
    </div>

    <div class="analyzer-content">
      <div class="input-section">
        <el-form :model="formData" label-position="top" @submit.prevent="analyzeConcept">
          <el-form-item :label="t('概念名称')">
            <el-input
              v-model="formData.concept"
              :placeholder="t('请输入要分析的概念名称')"
              :clearable="true"
              @keyup.enter="analyzeConcept"
            />
          </el-form-item>





          <div class="action-buttons">
            <el-button
              type="primary"
              @click="analyzeConcept"
              :loading="isLoading"
              :disabled="!formData.concept"
            >
              {{ t('开始分析') }}
            </el-button>
            <el-button @click="resetForm" :disabled="isLoading">{{ t('重置') }}</el-button>
          </div>
        </el-form>
      </div>

      <div class="result-section" v-if="analysis">

        <el-row :gutter="20" v-if="analysis.concept || analysis.definition">
          <el-col :span="24">
            <el-card class="definition-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <h4>{{ analysis.concept || t('概念') }}</h4>
                </div>
              </template>
              <div class="definition-content" v-if="analysis.definition">
                <p class="definition-text">{{ analysis.definition }}</p>
              </div>
              <div class="definition-content" v-else>
                <p class="definition-text text-muted">{{ t('暂无定义') }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" class="mt-4">
          <el-col :span="12">
            <el-card class="characteristics-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <h4>{{ t('核心特征') }}</h4>
                </div>
              </template>
              <div v-if="analysis.characteristics && analysis.characteristics.length > 0">
                <ul class="characteristics-list">
                  <li v-for="(char, index) in analysis.characteristics" :key="index">
                    {{ char }}
                  </li>
                </ul>
              </div>
              <div v-else class="empty-content">
                <p class="text-muted">{{ t('暂无核心特征数据') }}</p>
              </div>
            </el-card>
          </el-col>

          <el-col :span="12">
            <el-card class="examples-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <h4>{{ t('典型示例') }}</h4>
                </div>
              </template>
              <div v-if="analysis.examples && analysis.examples.length > 0">
                <ul class="examples-list">
                  <li v-for="(example, index) in analysis.examples" :key="index">
                    {{ example }}
                  </li>
                </ul>
              </div>
              <div v-else class="empty-content">
                <p class="text-muted">{{ t('暂无典型示例数据') }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>

          <el-row :gutter="20" class="mt-4">
            <el-col :span="24">
              <el-card class="network-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <h4>{{ t('概念关系网络') }}</h4>
                  </div>
                </template>
                <div class="network-graph">
                  <div v-if="analysis.relations && analysis.relations.length > 0" class="graph-container" ref="graphContainer"></div>
                  <div v-else class="empty-content">
                    <p class="text-muted">{{ t('暂无概念关系网络数据') }}</p>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="20" class="mt-4">
            <el-col :span="24">
              <el-card class="applications-card">
                <template #header>
                  <div class="card-header">
                    <h4>{{ t('应用场景') }}</h4>
                  </div>
                </template>
                <div v-if="analysis.applications && analysis.applications.length > 0" class="scenarios-list">
                  <el-timeline>
                    <el-timeline-item
                      v-for="(application, index) in analysis.applications"
                      :key="index"
                    >
                      {{ application }}
                    </el-timeline-item>
                  </el-timeline>
                </div>
                <div v-else class="empty-content">
                  <p class="text-muted">{{ t('暂无应用场景数据') }}</p>
                </div>
              </el-card>
            </el-col>
          </el-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted } from 'vue'
import { useSettings, t } from '../../store/settings'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'

const settings = useSettings()

// 表单数据
const formData = reactive({
  concept: ''
})




// 状态管理
const isLoading = ref(false)
const analysis = ref(null)
const graphContainer = ref(null)
let graphInstance = null

// 分析概念
const analyzeConcept = async () => {
  if (!formData.concept) {
    ElMessage.warning(t('请输入概念名称'))
    return
  }

  isLoading.value = true
  try {
    const response = await axios.post('/api/concept/analyze', {
      concept_name: formData.concept
    })

    // 验证响应数据结构
    if (!response.data || !response.data.data) {
      throw new Error('服务器返回的数据格式不正确：响应数据为空')
    }

    const responseData = response.data.data

    // 验证必需字段
    const requiredFields = {
      concept: { type: 'string', required: true },
      definition: { type: 'string', required: true },
      characteristics: { type: 'array', required: false },
      examples: { type: 'array', required: false },
      relations: { type: 'array', required: false },
      applications: { type: 'array', required: false }
    }
    const missingFields = Object.entries(requiredFields).filter(([field, config]) => {
      const value = responseData[field]
      if (config.required && !value) return true
      if (config.type === 'array' && Array.isArray(value) && value.length === 0) return false
      return false
    }).map(([field]) => field)
    
    // 记录缺失字段但不抛出错误
    if (missingFields.length > 0) {
      console.warn(`响应数据中缺少以下必需字段: [${missingFields.join(', ')}]`)
    }

    // 如果缺少必需字段，抛出错误
    if (missingFields.some(field => requiredFields[field].required)) {
      throw new Error('服务器返回的数据缺少必需字段')
    }

    analysis.value = responseData
    
    // 在下一个 tick 初始化关系图
    if (analysis.value && analysis.value.relations && analysis.value.relations.length > 0) {
      nextTick(() => {
        initGraph()
      })
    }
  } catch (error) {
    let errorMessage = t('分析失败，请稍后重试')
    if (error.response && error.response.data && error.response.data.detail) {
      errorMessage = t(error.response.data.detail)
    }
    
    // Enhanced error logging
    const errorDetails = {
      type: error.name,
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      context: {
        concept: formData.concept,
        responseStatus: error.response?.status,
        responseData: error.response?.data
      }
    }
    
    console.error('Concept analysis failed:', errorDetails)
    ElMessage.error(errorMessage)
  } finally {
    isLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.concept = ''
  analysis.value = null
  if (graphInstance) {
    graphInstance.dispose()
    graphInstance = null
  }
}

// 初始化关系图
const initGraph = () => {
  if (!graphContainer.value) return

  // 销毁已有实例
  if (graphInstance) {
    graphInstance.dispose()
  }

  // 创建新实例
  graphInstance = echarts.init(graphContainer.value)

  // 构建节点和边数据
  const nodes = [{
    id: 'center',
    name: analysis.value.concept,
    symbolSize: 70,
    itemStyle: { 
      color: '#1890ff',
      borderWidth: 2,
      borderColor: '#fff',
      shadowColor: 'rgba(0, 0, 0, 0.2)',
      shadowBlur: 10
    },
    category: 0
  }]

  const edges = []
  const relationColors = {
    '子类': '#2ecc71',
    '组成关系': '#e74c3c',
    '相关': '#f39c12',
    '应用': '#9b59b6'
  }

  analysis.value.relations.forEach((relation, index) => {
    nodes.push({
      id: `node${index}`,
      name: relation.concept,
      symbolSize: 50,
      itemStyle: { 
        color: relationColors[relation.relationship] || '#95a5a6',
        borderWidth: 1,
        borderColor: '#fff',
        shadowColor: 'rgba(0, 0, 0, 0.1)',
        shadowBlur: 5
      },
      category: 1
    })

    edges.push({
      source: 'center',
      target: `node${index}`,
      value: relation.relationship,
      lineStyle: {
        color: relationColors[relation.relationship] || '#95a5a6',
        width: 2,
        type: 'solid',
        curveness: 0.2,
        shadowColor: 'rgba(0, 0, 0, 0.1)',
        shadowBlur: 2
      },
      label: {
        show: true,
        formatter: t(relation.relationship),
        fontSize: 12,
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        padding: [4, 8],
        borderRadius: 4
      }
    })
  })

  // 配置项
  const option = {
    title: {
      text: t('概念关系网络'),
      top: 'bottom',
      left: 'right',
      textStyle: {
        fontSize: 14,
        color: '#666'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.dataType === 'node') {
          return params.name
        } else if (params.dataType === 'edge') {
          return t(params.value)
        }
      }
    },
    legend: [{
      data: [t('中心概念'), t('相关概念')],
      bottom: 30,
      icon: 'circle'
    }],
    animationDurationUpdate: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [{
      type: 'graph',
      layout: 'force',
      data: nodes,
      links: edges,
      categories: [
        { name: t('中心概念') },
        { name: t('相关概念') }
      ],
      roam: true,
      label: {
        show: true,
        position: 'right',
        fontSize: 12,
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        padding: [4, 8],
        borderRadius: 4
      },
      force: {
        repulsion: 200,
        edgeLength: 120,
        gravity: 0.1
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 4
        }
      }
    }]
  }

  graphInstance.setOption(option)
}


// 处理关系点击
const handleRelationClick = (relation) => {
  formData.concept = relation.concept
  analyzeConcept()
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
  padding: 2.5rem;
  max-width: 1200px;
  margin: 0 auto;
  background-color: var(--bg-color);
  min-height: 100vh;
}

.analyzer-header {
  margin-bottom: 3rem;
  text-align: center;
}

.analyzer-header h2 {
  color: var(--primary-color);
  margin-bottom: 1rem;
  font-size: 2.5rem;
  font-weight: 600;
  text-shadow: 0 2px 4px var(--shadow-color);
}

.description {
  color: var(--text-color);
  font-size: 1.2rem;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.analyzer-content {
  display: grid;
  gap: 2.5rem;
}

.input-section {
  background-color: var(--message-bg);
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px var(--shadow-color);
  transition: all 0.3s ease;
}

.input-section:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px var(--primary-shadow);
}

.action-buttons {
  margin-top: 2.5rem;
  display: flex;
  gap: 1.5rem;
  justify-content: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: var(--message-bg);
  border-bottom: 1px solid var(--border-color);
}

.card-header h4 {
  margin: 0;
  color: var(--primary-color);
  font-size: 1.2rem;
  font-weight: 600;
}

.definition-section,
.characteristics-section,
.examples-section {
  margin-bottom: 2.5rem;
}

.definition-section h5,
.characteristics-section h5,
.examples-section h5 {
  color: var(--text-color);
  margin-bottom: 1.2rem;
  font-weight: 600;
}

.characteristics-section ul,
.examples-list ul {
  list-style-type: none;
  padding: 0;
}

.characteristics-list li,
.examples-list li {
  padding: 0.8rem 1rem;
  margin-bottom: 0.8rem;
  background-color: var(--message-bg);
  border-radius: 6px;
  transition: all 0.3s ease;
  border-left: 4px solid var(--primary-color);
}

.characteristics-list li:hover,
.examples-list li:hover {
  transform: translateX(5px);
  background-color: var(--hover-color);
}

.network-controls {
  margin-bottom: 1.2rem;
  text-align: right;
}

.network-graph {
  height: 600px;
  background-color: var(--message-bg);
  border-radius: 8px;
  padding: 1rem;
  box-shadow: inset 0 2px 8px var(--shadow-color);
}

.graph-container {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
}

.scenarios-list {
  padding: 1.2rem;
}

.el-timeline-item {
  padding-bottom: 1.5rem;
}

.el-timeline-item__content {
  background-color: var(--message-bg);
  padding: 1rem 1.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.el-timeline-item__content:hover {
  background-color: var(--hover-color);
  transform: translateX(5px);
}

.empty-content {
  padding: 3rem;
  text-align: center;
  background-color: var(--message-bg);
  border-radius: 8px;
  border: 1px dashed var(--border-color);
}

.text-muted {
  color: var(--placeholder-color);
  font-size: 0.95rem;
}

.definition-content,
.characteristics-list,
.examples-list,
.network-graph,
.scenarios-list {
  min-height: 120px;
  padding: 1rem;
}

.el-card {
  height: 100%;
  margin-bottom: 1.5rem;
  border-radius: 12px;
  transition: all 0.3s ease;
  border: none;
  box-shadow: 0 4px 16px var(--shadow-color);
}

.el-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px var(--primary-shadow);
}

.definition-text {
  font-size: 1.1rem;
  line-height: 1.8;
  color: var(--text-color);
  padding: 1rem;
  background-color: var(--message-bg);
  border-radius: 8px;
  margin: 0;
}
</style>