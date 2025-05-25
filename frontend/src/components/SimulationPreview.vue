<template>
  <div class="simulation-preview-component">
    <el-button type="primary" @click="openSimulationWindow">
      {{ t('在新窗口中打开') }}
    </el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useSettings, t } from '../store/settings'

const emit = defineEmits(['update:html', 'error'])

const props = defineProps({
  html: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  simulationId: {
    type: String,
    default: ''
  }
})

let simulationWindow = null

// 在新窗口中打开仿真
const openSimulationWindow = () => {
  // 如果已经有窗口打开，就关闭它
  if (simulationWindow && !simulationWindow.closed) {
    simulationWindow.close()
  }

  // 创建新窗口
  simulationWindow = window.open('', '_blank', 'width=800,height=600')
  
  // 构建完整的HTML内容
  const fullHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>${props.title || '仿真预览'}</title>
      <style>
        body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
        .simulation-info { margin-bottom: 20px; }
        .simulation-content { width: 100%; min-height: 400px; }
      </style>
    </head>
    <body>
      ${props.title || props.description ? `
        <div class="simulation-info">
          ${props.title ? `<h2>${props.title}</h2>` : ''}
          ${props.description ? `<p>${props.description}</p>` : ''}
          ${props.simulationId ? `<p>ID: ${props.simulationId}</p>` : ''}
        </div>
      ` : ''}
      <div class="simulation-content">
        ${props.html}
      </div>
    </body>
    </html>
  `

  // 写入内容到新窗口
  simulationWindow.document.write(fullHtml)
  simulationWindow.document.close()

  // 添加窗口关闭事件监听
  simulationWindow.onbeforeunload = () => {
    simulationWindow = null
  }
}

</script>

<style scoped>
.simulation-preview-component {
  display: flex;
  justify-content: center;
  padding: 1rem;
}
</style>