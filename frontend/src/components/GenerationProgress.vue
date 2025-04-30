<template>
  <div class="generation-progress">
    <!-- 阶段进度指示器 -->
    <div class="stage-indicator">
      <div
        v-for="(stage, index) in stages"
        :key="stage.name"
        :class="[
          'stage',
          { 'active': currentStage === stage.name },
          { 'completed': isStageCompleted(stage.name) }
        ]"
      >
        <div class="stage-icon">
          <el-icon v-if="isStageCompleted(stage.name)">
            <Check />
          </el-icon>
          <el-icon v-else-if="currentStage === stage.name" class="loading">
            <Loading />
          </el-icon>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <div class="stage-info">
          <h4>{{ stage.title }}</h4>
          <p>{{ stage.description }}</p>
        </div>
        <div
          v-if="index < stages.length - 1"
          :class="[
            'stage-connector',
            { 'completed': isStageCompleted(stage.name) }
          ]"
        ></div>
      </div>
    </div>

    <!-- 当前状态消息 -->
    <div class="status-message" v-if="currentStage !== 'complete'">
      <el-alert
        :title="getCurrentStageTitle()"
        :type="currentStage === 'error' ? 'error' : 'info'"
        :description="statusMessage"
        show-icon
      />
    </div>

    <!-- 完成状态 -->
    <div v-else class="completion-message">
      <el-result
        icon="success"
        title="生成完成"
        sub-title="教学内容已成功生成"
      >
        <template #extra>
          <el-button type="primary" @click="$emit('view-content')">查看内容</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Check, Loading } from '@element-plus/icons-vue'

const props = defineProps({
  currentStage: {
    type: String,
    required: true
  },
  statusMessage: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['view-content'])

// 定义生成阶段
const stages = [
  {
    name: 'outline',
    title: '生成大纲',
    description: '创建课程整体结构'
  },
  {
    name: 'detailed_outline',
    title: '展开细纲',
    description: '细化每个章节内容'
  },
  {
    name: 'content',
    title: '生成内容',
    description: '编写详细教学内容'
  },
  {
    name: 'resources',
    title: '搜索资源',
    description: '查找相关学习资源'
  }
]

// 判断阶段是否完成
const isStageCompleted = (stageName) => {
  const stageIndex = stages.findIndex(s => s.name === stageName)
  const currentIndex = stages.findIndex(s => s.name === props.currentStage)
  return stageIndex < currentIndex || props.currentStage === 'complete'
}

// 获取当前阶段标题
const getCurrentStageTitle = () => {
  if (props.currentStage === 'error') {
    return '生成出错'
  }
  const stage = stages.find(s => s.name === props.currentStage)
  return stage ? `正在${stage.title}...` : ''
}
</script>

<style scoped>
.generation-progress {
  padding: 20px;
}

.stage-indicator {
  display: flex;
  justify-content: space-between;
  margin-bottom: 40px;
  position: relative;
  padding: 0 20px;
}

.stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
  z-index: 1;
}

.stage-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f5f7fa;
  border: 2px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  transition: all 0.3s;
}

.stage.active .stage-icon {
  background-color: #e6f1fc;
  border-color: #409eff;
  color: #409eff;
}

.stage.completed .stage-icon {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
}

.stage-info {
  text-align: center;
}

.stage-info h4 {
  margin: 0 0 4px;
  font-size: 14px;
  color: #303133;
}

.stage-info p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.stage-connector {
  position: absolute;
  top: 20px;
  left: calc(50% + 20px);
  right: calc(-50% + 20px);
  height: 2px;
  background-color: #dcdfe6;
  transition: background-color 0.3s;
}

.stage-connector.completed {
  background-color: #409eff;
}

.loading {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-message {
  margin: 20px 0;
}

.completion-message {
  margin-top: 40px;
  text-align: center;
}
</style>