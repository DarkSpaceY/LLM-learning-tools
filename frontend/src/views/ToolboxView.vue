<template>
  <div class="toolbox-container">
    <div class="toolbox-header">
      <h2>{{ t('学习工具箱') }}</h2>
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          :placeholder="t('搜索工具')"
          prefix-icon="el-icon-search"
        >
          <template #prefix>
            <i class="fas fa-search"></i>
          </template>
        </el-input>
      </div>
    </div>

    <div class="category-filter">
      <el-radio-group v-model="selectedCategory">
        <el-radio-button value="all">{{ t('全部') }}</el-radio-button>
        <el-radio-button v-for="category in categories" 
          :key="category.value" 
          :value="category.value"
        >
          {{ t(category.label) }}
        </el-radio-button>
      </el-radio-group>
    </div>

    <div class="tools-grid">
      <el-card
        v-for="tool in filteredTools"
        :key="tool.id"
        class="tool-card"
        :body-style="{ padding: '0px' }"
      >
        <div class="tool-icon">
          <i :class="tool.icon"></i>
        </div>
        <div class="tool-content">
          <h3>{{ t(tool.name) }}</h3>
          <p>{{ t(tool.description) }}</p>
          <el-button type="primary" @click="useTool(tool)">
            {{ t('使用') }}
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSettings, t } from '../store/settings'

const router = useRouter()
const settings = useSettings()

// 工具分类
const categories = [
  { value: 'analysis', label: '分析工具' },
  { value: 'learning', label: '学习工具' },
  { value: 'practice', label: '练习工具' }
]

// 工具列表数据
const tools = [
  {
    id: 'knowledge-point-parser',
    name: '知识点解析器',
    description: '解析文本中的关键知识点，标注重要程度和难度',
    category: 'analysis',
    icon: 'fas fa-brain',
    route: '/tools/knowledge-parser'
  },
  {
    id: 'exercise-generator',
    name: '练习题生成器',
    description: '根据主题智能生成各类型练习题，包含详细解析',
    category: 'practice',
    icon: 'fas fa-pencil-alt',
    route: '/tools/exercise'
  },
  {
    id: 'knowledge-searcher',
    name: '学习资源搜索器',
    description: '搜索并推荐优质学习资源，包含评分和标签',
    category: 'learning',
    icon: 'fas fa-search-plus',
    route: '/tools/resource'
  },
  {
    id: 'learning-planner',
    name: '学习计划生成器',
    description: '制定个性化学习计划，合理安排学习进度',
    category: 'learning',
    icon: 'fas fa-calendar-alt',
    route: '/tools/plan'
  },
  {
    id: 'concept-analyzer',
    name: '概念分析器',
    description: '深入分析和解释复杂概念，提供详细的理解框架',
    category: 'analysis',
    icon: 'fas fa-microscope',
    route: '/tools/concept'
  },
  {
    id: 'simulation-builder',
    name: '仿真构建器',
    description: '构建和运行仿真实验，提供交互式学习体验',
    category: 'learning',
    icon: 'fas fa-cube',
    route: '/tools/simulation'
  }
]

// 状态管理
const searchQuery = ref('')
const selectedCategory = ref('all')

// 过滤工具列表
const filteredTools = computed(() => {
  return tools.filter(tool => {
    const matchesSearch = tool.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         tool.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = selectedCategory.value === 'all' || tool.category === selectedCategory.value
    return matchesSearch && matchesCategory
  })
})

// 使用工具
const useTool = (tool) => {
  router.push(tool.route)
}
</script>

<style scoped>
.toolbox-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.toolbox-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.toolbox-header h2 {
  color: var(--primary-color);
  margin: 0;
}

.search-bar {
  width: 300px;
}

.category-filter {
  margin-bottom: 2rem;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
}

.tool-card {
  border-radius: 8px;
  transition: transform 0.3s ease;
  cursor: pointer;
}

.tool-card:hover {
  transform: translateY(-5px);
}

.tool-icon {
  background: var(--primary-color);
  color: white;
  height: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 8px 8px 0 0;
}

.tool-icon i {
  font-size: 2.5rem;
}

.tool-content {
  padding: 1.5rem;
}

.tool-content h3 {
  margin: 0 0 1rem;
  color: var(--text-color);
}

.tool-content p {
  color: var(--text-color-secondary);
  margin-bottom: 1.5rem;
  min-height: 3em;
}
</style>