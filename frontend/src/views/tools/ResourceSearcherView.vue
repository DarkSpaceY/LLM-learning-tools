<template>
  <div class="resource-searcher-container">
    <div class="searcher-header">
      <h2>{{ t('学习资源搜索器') }}</h2>
      <p class="description">{{ t('智能搜索优质学习资源，提供评分和标签分类') }}</p>
    </div>

    <div class="searcher-content">
      <div class="input-section">
        <el-form :model="searchForm" label-position="top" @submit.prevent="searchResources">
          <el-form-item :label="t('搜索关键词')">
            <el-input
              v-model="searchForm.keyword"
              :placeholder="t('请输入要搜索的关键词')"
              :clearable="true"
              @keyup.enter="searchResources"
            >
              <template #append>
                <el-button 
                  type="primary" 
                  @click="searchResources" 
                  :loading="isLoading"
                  :icon="Search"
                >
                  {{ t('搜索') }}
                </el-button>
              </template>
            </el-input>
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item :label="t('资源类型')">
                <el-checkbox-group
                  v-model="searchForm.types"
                  @change="handleTypeChange"
                  class="resource-type-checkboxes"
                >
                  <el-checkbox
                    v-for="type in resourceTypes"
                    :key="type.value"
                    :value="type.value"
                  >
                    <el-icon><component :is="type.icon" /></el-icon>
                    {{ t(type.label) }}
                  </el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="t('难度等级')">
                <el-rate
                  v-model="searchForm.difficulty"
                  :max="5"
                  :texts="difficultyTexts"
                  show-text
                  text-color="#ff9900"
                />
              </el-form-item>
            </el-col>
          </el-row>


        </el-form>
      </div>

      <div class="result-section" v-if="resources.length > 0">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card class="results-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <h4>{{ t('搜索结果') }}</h4>
                  <el-tag type="success">{{ t('共找到 {0} 个资源', [total]) }}</el-tag>
                </div>
              </template>
              <div class="resources-list">
                <el-card
                  v-for="resource in resources"
                  :key="resource.id"
                  class="resource-card"
                  shadow="hover"
                >
                  <div class="resource-header">
                    <div class="title-section">
                      <el-link :href="resource.url" target="_blank" type="primary" :underline="false">
                        <h4>
                          <el-icon><Link /></el-icon>
                          {{ resource.title }}
                        </h4>
                      </el-link>
                      <div class="resource-meta">
                        <el-tag size="small" :type="getTypeTag(resource.type)">
                          <el-icon><component :is="getTypeIcon(resource.type)" /></el-icon>
                          {{ t(resource.type) }}
                        </el-tag>
                        <el-rate
                          v-model="resource.difficulty"
                          disabled
                          show-score
                          text-color="#ff9900"
                        />
                      </div>
                    </div>
                  </div>

                  <p class="resource-description">{{ resource.description }}</p>
                </el-card>

                <div class="pagination-container">
                  <el-pagination
                    v-model:current-page="currentPage"
                    v-model:page-size="pageSize"
                    :total="total"
                    :page-sizes="[10, 20, 30, 50]"
                    :background="true"
                    layout="total, sizes, prev, pager, next"
                    @size-change="handleSizeChange"
                    @current-change="handleCurrentChange"
                  />
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <div class="no-result" v-else-if="hasSearched">
        <el-empty
          :image="emptyImage"
          :description="t('暂无搜索结果')"
        >
          <template #description>
            <p>{{ t('没有找到相关的学习资源') }}</p>
            <p class="suggestion">{{ t('建议尝试：') }}</p>
            <ul>
              <li>{{ t('检查关键词是否正确') }}</li>
              <li>{{ t('尝试使用不同的搜索词') }}</li>
              <li>{{ t('减少筛选条件') }}</li>
            </ul>
          </template>
          <el-button type="primary" @click="resetSearch">
            {{ t('重置搜索') }}
          </el-button>
        </el-empty>
      </div>
      
      <div class="loading-state" v-if="isLoading">
        <el-skeleton :rows="3" animated />
        <el-skeleton :rows="3" animated />
        <el-skeleton :rows="3" animated />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useSettings, t } from '../../store/settings'
import { ElMessage } from 'element-plus'
import { searchResources as searchResourcesApi, saveResource as saveResourceApi, shareResource as shareResourceApi } from '../../api'
import { Search, Link } from '@element-plus/icons-vue'
import { resourceTypes, typeTagMap, typeIconMap } from '../../config/resourceTypes'
import axios from 'axios'
const settings = useSettings()

// 难度等级文本
const difficultyTexts = [
  t('入门'),
  t('基础'),
  t('进阶'),
  t('高级'),
  t('专家')
]

// 搜索表单数据
const searchForm = reactive({
  keyword: '',
  types: [], // 资源类型数组
  difficulty: 0
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 状态管理
const isLoading = ref(false)
const resources = ref([])
const hasSearched = ref(false)

// 搜索资源
const handleTypeChange = (val) => {
  // 确保val是数组
  if (Array.isArray(val)) {
    // 直接赋值选中的类型数组
    searchForm.types = val
    console.log('已选择的资源类型:', searchForm.types)
  } else {
    console.warn('资源类型选择值无效:', val)
    searchForm.types = [] // 重置为空数组
  }
}

const searchResources = async () => {
  if (!searchForm.keyword.trim()) {
    ElMessage.warning(t('请输入搜索关键词'))
    return
  }

  isLoading.value = true
  try {
    const response = await axios.post('/api/resources/search', {
      query: searchForm.keyword,
      types: searchForm.types,
      difficulty: searchForm.difficulty
    })

    if (response.data.success) {
      // 处理返回的数据
      const items = response.data.data.items.map(item => ({
        ...item,
        url: item.url.replace(/`/g, '').trim() // 移除URL中的反引号
      }))

      resources.value = items
      total.value = response.data.data.total
      hasSearched.value = true
    } else {
      ElMessage.warning(response.data.message || t('搜索失败'))
    }
  } catch (error) {
    ElMessage.error(t('搜索失败，请稍后重试'))
    console.error('搜索失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 处理分页大小变化
const handleSizeChange = (val) => {
  pageSize.value = val
  searchResources()
}

// 处理页码变化
const handleCurrentChange = (val) => {
  currentPage.value = val
  searchResources()
}

// 获取资源类型标签样式
const getTypeTag = (type) => typeTagMap[type] || 'info'

// 获取资源类型图标
const getTypeIcon = (type) => typeIconMap[type] || typeIconMap.document

// 格式化日期
const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

// 重置搜索
const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.types = []
  searchForm.difficulty = 0
  searchForm.sort = 'relevance'
  currentPage.value = 1
  hasSearched.value = false
  resources.value = []
}

// 收藏资源
const saveResource = async (resource) => {
  try {
    await saveResourceApi(resource.id)
    ElMessage.success(t('收藏成功'))
  } catch (error) {
    ElMessage.error(t('收藏失败，请稍后重试'))
    console.error('收藏失败:', error)
  }
}

// 分享资源
const shareResource = async (resource) => {
  try {
    const shareUrl = await shareResourceApi(resource.id)
    await navigator.clipboard.writeText(shareUrl)
    ElMessage.success(t('分享链接已复制到剪贴板'))
  } catch (error) {
    ElMessage.error(t('分享失败，请稍后重试'))
    console.error('分享失败:', error)
  }
}
</script>

<style scoped>
.resource-searcher-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 4rem);
}

.searcher-header {
  margin-bottom: 2rem;
  text-align: center;
}

.searcher-header h2 {
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.description {
  color: var(--text-color-secondary);
  font-size: 1.1rem;
}

.searcher-content {
  display: grid;
  gap: 2rem;
}

.search-section {
  background-color: var(--bg-color);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.resource-card {
  margin-bottom: 1.5rem;
  transition: transform 0.2s ease;
}

.resource-card:hover {
  transform: translateY(-2px);
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.resource-header h4 {
  margin: 0;
  font-size: 1.2rem;
}

.resource-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
}

.title-section {
  flex: 1;
}

.action-section {
  margin-left: 1rem;
}

.review-count {
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

.resource-description {
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
  line-height: 1.5;
}



.pagination-container {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
}

.no-result {
  margin-top: 2rem;
  text-align: center;
}

.suggestion {
  margin-top: 1rem;
  color: var(--text-color-secondary);
}

.loading-state {
  margin-top: 2rem;
}

.loading-state .el-skeleton {
  margin-bottom: 2rem;
}

.loading-state .el-skeleton:last-child {
  margin-bottom: 0;
}

.resource-type-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.resource-type-checkboxes .el-checkbox {
  margin-right: 0;
  margin-bottom: 0;
}

.resource-type-checkboxes .el-checkbox .el-icon {
  margin-right: 0.5rem;
  vertical-align: middle;
}
</style>