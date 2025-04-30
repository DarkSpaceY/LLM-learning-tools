import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import MapView from '../views/MapView.vue'
import SettingsView from '../views/SettingsView.vue'
import ToolboxView from '../views/ToolboxView.vue'
import TutorialView from '../views/TutorialView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: '对话',
        icon: 'fas fa-comments'
      }
    },
    {
      path: '/map',
      name: 'map',
      component: MapView,
      meta: {
        title: '知识图谱',
        icon: 'fas fa-project-diagram'
      }
    },
    {
      path: '/tools',
      name: 'tools',
      component: ToolboxView,
      meta: {
        title: '工具箱',
        icon: 'fas fa-tools'
      }
    },
    {
      path: '/tools/knowledge-parser',
      name: 'knowledge-parser',
      component: () => import('../views/tools/KnowledgeParserView.vue'),
      meta: {
        title: '知识点解析器',
        icon: 'fas fa-brain'
      }
    },
    {
      path: '/tools/exercise',
      name: 'exercise',
      component: () => import('../views/tools/ExerciseGeneratorView.vue'),
      meta: {
        title: '练习题生成器',
        icon: 'fas fa-pencil-alt'
      }
    },
    {
      path: '/tools/resource',
      name: 'resource',
      component: () => import('../views/tools/ResourceSearcherView.vue'),
      meta: {
        title: '学习资源搜索器',
        icon: 'fas fa-search-plus'
      }
    },
    {
      path: '/tools/plan',
      name: 'plan',
      component: () => import('../views/tools/LearningPlannerView.vue'),
      meta: {
        title: '学习计划生成器',
        icon: 'fas fa-calendar-alt'
      }
    },
    {
      path: '/tools/concept',
      name: 'concept',
      component: () => import('../views/tools/ConceptAnalyzerView.vue'),
      meta: {
        title: '概念分析器',
        icon: 'fas fa-microscope'
      }
    },
    {
      path: '/tools/simulation',
      name: 'simulation',
      component: () => import('../views/tools/SimulationBuilderView.vue'),
      meta: {
        title: '仿真构建器',
        icon: 'fas fa-cube'
      }
    },
    {
      path: '/tutorials',
      name: 'tutorials',
      component: TutorialView,
      meta: {
        title: '教程',
        icon: 'fas fa-book'
      }
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
      meta: {
        title: '设置',
        icon: 'fas fa-cog'
      }
    }
  ]
})

// 更新页面标题
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title} | AI教育助手`
  next()
})

export default router