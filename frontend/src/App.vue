<template>
  <div class="app" :class="themeClass">
    <nav class="nav">
      <router-link 
        v-for="route in routes" 
        :key="route.path"
        :to="route.path"
        class="nav-link"
      >
        <i :class="route.meta.icon"></i>
        <span>{{ t(route.meta.title) }}</span>
      </router-link>
    </nav>
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useSettings, t } from './store/settings'

const router = useRouter()
const routes = router.options.routes.filter(route => [
  '/', '/map', '/tools', '/tutorials', '/settings'
].includes(route.path))
const settings = useSettings()

// 计算主题类名
const themeClass = computed(() => {
  return `theme-${settings.value.theme}`
})

// 监听语言变化更新标题
watch(() => settings.value.language, () => {
  const currentRoute = router.currentRoute.value
  if (currentRoute.meta?.title) {
    document.title = `${t(currentRoute.meta.title)} | AI教育助手`
  }
})
</script>

<style>
:root[data-theme="light"] {
  --bg-color: #ffffff;
  --text-color: #353740;
  --nav-bg: #f7f7f8;
  --border-color: rgba(0, 0, 0, 0.1);
  --hover-color: rgba(16, 163, 127, 0.05);
  --primary-color: #10a37f;
}

:root[data-theme="dark"] {
  --bg-color: #1a1b1e;
  --text-color: #e0e1e6;
  --nav-bg: #2c2d30;
  --border-color: rgba(255, 255, 255, 0.1);
  --hover-color: rgba(16, 163, 127, 0.15);
  --primary-color: #10a37f;
}

.app {
  display: flex;
  min-height: 100vh;
  background: var(--bg-color);
  color: var(--text-color);
}

.nav {
  width: 260px;
  background: var(--nav-bg);
  border-right: 1px solid var(--border-color);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  color: var(--text-color);
  text-decoration: none;
  transition: all 0.2s;
}

.nav-link:hover {
  background: var(--hover-color);
}

.nav-link.router-link-active {
  background: var(--primary-color);
  color: white;
}

.nav-link i {
  font-size: 1.25rem;
  width: 1.5rem;
  text-align: center;
}

.main-content {
  flex: 1;
  overflow: hidden;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .app {
    flex-direction: column;
  }

  .nav {
    width: 100%;
    flex-direction: row;
    padding: 0.5rem;
    overflow-x: auto;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }

  .nav-link {
    padding: 0.5rem 0.75rem;
  }

  .nav-link span {
    display: none;
  }
}
</style>