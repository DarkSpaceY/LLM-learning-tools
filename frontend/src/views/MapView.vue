<template>
  <div class="knowledge-map">
    <!-- 左侧控制面板 -->
    <div class="control-panel">
      <h3>{{ t('知识图谱') }}</h3>
      
      <!-- 初始知识点输入 -->
      <div class="input-section">
        <div class="input-group">
          <el-input
            v-model="initialTopic"
            :placeholder="t('输入初始知识点')"
            class="topic-input"
          >
            <template #append>
              <el-button @click="generateMap" :loading="isLoading">
                {{ t('生成') }}
              </el-button>
            </template>
          </el-input>
        </div>
        
        <div class="description-input">
          <el-input
            v-model="topicDescription"
            type="textarea"
            :rows="3"
            :placeholder="t('知识点描述（可选）')"
          />
        </div>
      </div>

      <!-- 图谱操作 -->
      <div class="actions">
       <el-button-group>
         <el-button @click="exportGraph" :disabled="!hasNodes">
           <i class="fas fa-file-export"></i>
           {{ t('导出') }}
         </el-button>
         <el-button @click="importGraph">
           <i class="fas fa-file-import"></i>
           {{ t('导入') }}
         </el-button>
         <el-button @click="resetGraph" :disabled="!hasNodes">
           <i class="fas fa-redo"></i>
           {{ t('重置') }}
         </el-button>
       </el-button-group>

       <!-- 导入选择器对话框 -->
       <el-dialog
         v-model="importDialogVisible"
         :title="t('导入知识图谱')"
         width="500px"
       >
         <el-table
           v-loading="isLoading"
           :data="savedGraphs"
           stripe
           style="width: 100%"
         >
           <el-table-column
             prop="topic"
             :label="t('主题')"
             width="180"
           />
           <el-table-column
             prop="created_at"
             :label="t('创建时间')"
             width="180"
           >
             <template #default="scope">
               {{ new Date(scope.row.created_at).toLocaleString() }}
             </template>
           </el-table-column>
           <el-table-column
             :label="t('操作')"
             width="180"
           >
             <template #default="scope">
               <el-button-group>
                 <el-button
                   type="primary"
                   link
                   @click="loadGraph(scope.row.filename)"
                 >
                   {{ t('加载') }}
                 </el-button>
                 <el-button
                   type="danger"
                   link
                   @click="deleteGraph(scope.row.filename)"
                 >
                   {{ t('删除') }}
                 </el-button>
               </el-button-group>
             </template>
           </el-table-column>
         </el-table>
       </el-dialog>
      </div>

            <!-- 选中节点信息 -->
      <div v-if="selectedNode" class="node-info">
        <h4>{{ t('节点信息') }}</h4>
        <div class="info-content">
          <p class="label">{{ selectedNode.label }}</p>
          <p class="category">{{ t('类别') }}: {{ selectedNode.category }}</p>
          <p class="description">{{ selectedNode.description }}</p>
          <el-button 
            type="primary" 
            @click="expandNode(selectedNode)"
            :loading="isExpandingNode"
          >
            {{ t('拓展该节点') }}
          </el-button>
        </div>
      </div>
      <!-- 日志窗口 -->
      <div class="log-window" ref="logContainer">
        <div class="log-content">
          <div v-for="(message, index) in logMessages"
               :key="index"
               class="log-message"
               :class="{ 'processing': isProcessing && index === logMessages.length - 1 }">
            {{ message }}
          </div>
        </div>
      </div>


    </div>

    <!-- 右侧图谱展示 -->
    <div class="graph-container" ref="graphContainer">
      <div id="knowledge-graph" class="graph"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useSettings, t } from '../store/settings'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

// 状态管理
const settings = useSettings()
const initialTopic = ref('')
const topicDescription = ref('')
const graphInstance = ref(null)
const graphContainer = ref(null)
const isLoading = ref(false)
const isExpandingNode = ref(false)
const selectedNode = ref(null)

// 导入相关的状态
const importDialogVisible = ref(false)
const savedGraphs = ref([])

// 添加日志相关的状态管理
const logMessages = ref([])
const logContainer = ref(null)
const isProcessing = ref(false)

// 图谱数据
const graphData = ref({
  nodes: [],
  edges: []
})

// 导入相关方法
const importGraph = async () => {
  isLoading.value = true
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/knowledge_graph/list`)
    const result = await response.json()
    if (result.success) {
      savedGraphs.value = result.data
      importDialogVisible.value = true
    } else {
      ElMessage.error(t('获取知识图谱列表失败'))
    }
  } catch (error) {
    console.error('获取知识图谱列表失败:', error)
    ElMessage.error(t('获取知识图谱列表失败'))
  } finally {
    isLoading.value = false
  }
}

const loadGraph = async (filename) => {
  isLoading.value = true
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/knowledge_graph/${filename}`)
    const result = await response.json()
    if (result.success) {
      graphData.value = result.data
      initialTopic.value = result.data.metadata?.topic || ''
      updateGraph()
      importDialogVisible.value = false
      ElMessage.success(t('知识图谱加载成功'))
    } else {
      ElMessage.error(t('加载知识图谱失败'))
    }
  } catch (error) {
    console.error('加载知识图谱失败:', error)
    ElMessage.error(t('加载知识图谱失败'))
  } finally {
    isLoading.value = false
  }
}

// 删除知识图谱
const deleteGraph = async (filename) => {
  try {
    await ElMessageBox.confirm(
      t('确定要删除这个知识图谱吗？此操作不可恢复。'),
      t('删除确认'),
      {
        confirmButtonText: t('删除'),
        cancelButtonText: t('取消'),
        type: 'warning'
      }
    )
    
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/knowledge_graph/${filename}`, {
      method: 'DELETE'
    })
    
    const result = await response.json()
    if (result.success) {
      ElMessage.success(t('知识图谱删除成功'))
      // 重新加载知识图谱列表
      await importGraph()
    } else {
      throw new Error(result.message || t('删除失败'))
    }
  } catch (error) {
    if (error.toString().includes('cancel')) return
    console.error('删除知识图谱失败:', error)
    ElMessage.error(t('删除知识图谱失败：') + error.message)
  }
}

// 添加日志
const addLog = async (message, type_) => {
  if (type_=="chunk") {
    // 追加到最后一条日志
    logMessages.value[logMessages.value.length - 1] += message
  } else {
    // 新的日志消息，直接添加
    logMessages.value.push(message)
  }
}

// 清空日志
const clearLogs = () => {
  logMessages.value = []
}
// 确保数据结构的完整性，兼容 edges 和 relations
const processGraphData = (data) => {
  return {
    nodes: Array.isArray(data.nodes) ? data.nodes : [],
    edges: Array.isArray(data.edges) ? data.edges :
          Array.isArray(data.relations) ? data.relations : []
  }
}

// 计算属性
const hasNodes = computed(() => graphData.value.nodes.length > 0)

// 初始化图谱
const initGraph = () => {
  if (!graphContainer.value) return
  
  graphInstance.value = echarts.init(graphContainer.value.querySelector('#knowledge-graph'))
  
  const option = {
    title: {
      show: false
    },
    legend: {
      show: false
    },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.dataType === 'node') {
          return `
            <div class="tooltip-content">
              <h4>${params.data.label}</h4>
              <p>${params.data.description}</p>
              <p class="category">${t('类别')}: ${params.data.category}</p>
              ${params.data.id === 'center' ?
                `<p class="tip">${t('这是中心知识点')}</p>` :
                `<p class="tip">${t('点击可查看详情')}<br>${t('可继续拓展该知识点')}</p>`
              }
            </div>
          `
        }
        return `
          <div class="tooltip-content">
            <p class="relation">${params.data.type}</p>
            <p class="tip">${t('从')} ${params.data.source} ${t('到')} ${params.data.target}</p>
          </div>
        `
      },
      backgroundColor: 'rgba(var(--bg-color-rgb), 0.9)',
      borderColor: 'var(--border-color)',
      textStyle: {
        color: 'var(--text-color)'
      }
    },
    animation: true,
    animationDurationUpdate: 500,
    animationEasingUpdate: 'quinticInOut',
    series: [{
      type: 'graph',
      layout: 'force',
      data: [],
      links: [],
      categories: [
        { name: '概念' },
        { name: '方法' },
        { name: '原理' },
        { name: '应用' }
      ],
      roam: true,
      label: {
        show: true,
        position: 'right'
      },
      force: {
        repulsion: 200,  // 增加斥力
        edgeLength: 150,  // 减小边长
        gravity: 0.1,    // 添加向心力
        friction: 0.6    // 添加摩擦力
      },
      emphasis: {
        focus: 'adjacency'
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 2,
          opacity: 1
        },
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      }
    }]
  }

  graphInstance.value.setOption(option)
  
  // 注册点击事件
  graphInstance.value.on('click', (params) => {
    if (params.dataType === 'node') {
      selectedNode.value = params.data
    }
  })
}

// 更新图谱数据
const updateGraph = () => {
  if (!graphInstance.value) return
  
  const option = {
    series: [{
      data: graphData.value.nodes.map(node => ({
        ...node,
        symbolSize: node.value * 30,  // 基于节点权重设置大小
        itemStyle: {
          color: node.id === 'center' ?
            'rgb(var(--primary-color-rgb))' :
            {
              '概念': '#91cc75',
              '方法': '#fac858',
              '原理': '#ee6666',
              '应用': '#73c0de'
            }[node.category] || '#999'
        }
      })),
      links: graphData.value.edges.map(edge => ({
        ...edge,
        source: edge.source,
        target: edge.target,
        lineStyle: {
          color: '#999',
          width: 1,
          curveness: 0.1  // 添加一点弧度，避免重叠
        },
        label: {
          show: true,
          formatter: edge.type,
          fontSize: 12,
          color: 'var(--text-color-secondary)'
        }
      })),
      links: graphData.value.edges.map(edge => ({
        ...edge,
        source: edge.source,
        target: edge.target,
        label: {
          show: true,
          formatter: edge.type
        }
      })),
    }]
  }
  
  graphInstance.value.setOption(option)
}

// 生成知识图谱
const generateMap = async () => {
  if (!initialTopic.value.trim()) {
    ElMessage.warning(t('请输入初始知识点'))
    return
  }

  isLoading.value = true
  isProcessing.value = true
  clearLogs()
  addLog(t('开始生成知识图谱...\n'), "")

  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/knowledge_graph/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        topic: initialTopic.value,
        description: topicDescription.value
      })
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value)
        const lines = text.split('\n')
        
        for (const line of lines) {
          if (!line.trim()) continue
          if (line === 'data: [DONE]') continue
          
          try {
            const data = JSON.parse(line.replace('data: ', ''))
            if (data.type === 'chunk') {
              addLog(data.data,'chunk')
            } else if (data.type === 'graph') {
              graphData.value = processGraphData(data.data)
              updateGraph()
            }
          } catch (e) {
            console.error('Failed to parse stream chunk:', e)
          }
        }
      }

      addLog(t('知识图谱生成完成\n'), "")
      ElMessage.success(t('知识图谱生成成功'))
    } catch (error) {
      addLog(t('生成失败：\n') + error.message, "")
      throw error
    } finally {
      isProcessing.value = false
      reader.releaseLock()
    }
  } catch (error) {
    console.error('Failed to generate graph:', error)
    ElMessage.error(t('生成知识图谱失败'))
  } finally {
    isLoading.value = false
  }
}

// 拓展节点
const expandNode = async (node) => {
  if (!node || !node.id) {
    ElMessage.error(t('无效的节点数据'))
    return
  }

  isExpandingNode.value = true
  clearLogs()
  addLog(t(`开始拓展节点: ${node.label}...\n`), "")

  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/knowledge_graph/expand`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'  // 添加此头部表明接受流式响应
      },
      body: JSON.stringify({
        nodeId: node.id,
        topic: node.label,
        description: node.description,
        category: node.category,
        currentNodes: graphData.value.nodes.map(n => ({
          id: n.id,
          label: n.label,
          category: n.category
        }))
      })
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(errorText || t('扩展节点请求失败'))
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    let buffer = ''  // 用于存储不完整的JSON字符串
    
    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value)
        buffer += text
        
        // 尝试从buffer中提取完整的JSON对象
        let newlineIndex
        while ((newlineIndex = buffer.indexOf('\n')) >= 0) {
          const line = buffer.slice(0, newlineIndex)
          buffer = buffer.slice(newlineIndex + 1)
          
          if (!line.trim() || line === 'data: [DONE]') continue
          
          try {
            const data = JSON.parse(line.replace('data: ', ''))
            if (data.type === 'chunk') {
              addLog(data.data, 'chunk')
            } else if (data.type === 'graph') {
              // 合并新节点和边
              const newData = processGraphData(data.data)
              const existingNodeIds = new Set(graphData.value.nodes.map(n => n.id))
              const newNodes = newData.nodes.filter(n => !existingNodeIds.has(n.id))
              
              graphData.value.nodes.push(...newNodes)
              graphData.value.edges.push(...newData.edges)
              updateGraph()
            }
          } catch (e) {
            console.error('解析流数据失败:', e, line)
          }
        }
      }
      
      if (buffer.trim()) {
        // 处理最后可能剩余的数据
        try {
          const data = JSON.parse(buffer.replace('data: ', ''))
          if (data.type === 'graph') {
            const newData = processGraphData(data.data)
            const existingNodeIds = new Set(graphData.value.nodes.map(n => n.id))
            const newNodes = newData.nodes.filter(n => !existingNodeIds.has(n.id))
            
            graphData.value.nodes.push(...newNodes)
            graphData.value.edges.push(...newData.edges)
            updateGraph()
          }
        } catch (e) {
          console.error('处理剩余数据失败:', e)
        }
      }

      ElMessage.success(t('节点拓展成功'))
      addLog(t('节点拓展完成\n'), "")
    } finally {
      reader.releaseLock()
    }
  } catch (error) {
    console.error('节点拓展失败:', error)
    addLog(t('拓展失败：') + error.message + '\n', "")
    ElMessage.error(t('节点拓展失败：') + error.message)
  } finally {
    isExpandingNode.value = false
  }
}

// 导出图谱
const exportGraph = async () => {
  if (!initialTopic.value) {
    ElMessage.error(t('请先设置知识图谱主题'))
    return
  }

  isLoading.value = true
  try {
    const exportData = {
      nodes: graphData.value.nodes,
      edges: graphData.value.edges,
      metadata: {
        exportedAt: new Date().toISOString(),
        topic: initialTopic.value
      },
      topic: initialTopic.value
    }

    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/knowledge_graph/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(exportData)
    })

    const result = await response.json()
    if (result.success) {
      ElMessage.success(t('知识图谱保存成功'))
    } else {
      throw new Error(result.message || t('保存失败'))
    }
  } catch (error) {
    console.error('保存知识图谱失败:', error)
    ElMessage.error(t('保存知识图谱失败：') + error.message)
  } finally {
    isLoading.value = false
  }
}

// 重置图谱
const resetGraph = async () => {
  try {
    await ElMessageBox.confirm(
      t('确定要重置知识图谱吗？所有未保存的内容将会丢失。'),
      t('重置确认'),
      {
        confirmButtonText: t('重置'),
        cancelButtonText: t('取消'),
        type: 'warning'
      }
    )
    
    graphData.value = { nodes: [], edges: [] }
    selectedNode.value = null
    initialTopic.value = ''
    topicDescription.value = ''
    updateGraph()
    
  } catch (err) {
    // 用户取消重置
  }
}

// 窗口大小调整处理
const handleResize = () => {
  if (graphInstance.value && graphContainer.value) {
    graphInstance.value.resize()
  }
}

onMounted(() => {
  nextTick(() => {
    initGraph()
    window.addEventListener('resize', handleResize)
  })
})

onUnmounted(() => {
  // 先移除事件监听
  window.removeEventListener('resize', handleResize)
  
  // 确保在实例存在时才进行销毁
  if (graphInstance.value) {
    graphInstance.value.dispose()
    graphInstance.value = null
  }
})
</script>

<style scoped>
.knowledge-map {
  height: 100vh;
  display: flex;
  background: var(--bg-color);
}

.control-panel {
  width: 300px;
  padding: 1.5rem;
  border-right: 1px solid var(--border-color);
  background: var(--bg-color);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
}

.control-panel h3 {
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.input-group {
  display: flex;
  gap: 0.5rem;
}

.topic-input {
  flex: 1;
}

.actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-start;
}

.node-info {
  padding: 1rem;
  background: rgba(var(--primary-color-rgb), 0.05);
  border-radius: 8px;
}

.node-info h4 {
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-content .label {
  font-weight: 500;
  color: var(--text-color);
}

.info-content .category {
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

.info-content .description {
  color: var(--text-color);
  font-size: 0.9rem;
  line-height: 1.5;
}

.graph-container {
  flex: 1;
  position: relative;
  height: 100%;
}

.graph {
  width: 100%;
  height: 100%;
}

/* 图谱工具提示样式 */
:deep(.tooltip-content) {
  padding: 0.5rem;
}

:deep(.tooltip-content h4) {
  margin: 0 0 0.5rem;
  color: var(--primary-color);
  font-weight: 500;
}

:deep(.tooltip-content p) {
  margin: 0.25rem 0;
  font-size: 0.9rem;
}

:deep(.tooltip-content .category) {
  color: var(--text-color-secondary);
  font-size: 0.8rem;
  margin-top: 0.5rem;
}

:deep(.tooltip-content .tip) {
  color: var(--primary-color);
  font-size: 0.8rem;
  margin-top: 0.5rem;
  font-style: italic;
}

:deep(.tooltip-content .relation) {
  color: var(--text-color);
  font-weight: 500;
}
</style>