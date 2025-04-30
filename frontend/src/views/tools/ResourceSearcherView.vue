<template>
  <div class="resource-searcher-container">
    <div class="searcher-header">
      <h2>{{ t('学习资源搜索器') }}</h2>
      <p class="description">{{ t('搜索并推荐优质学习资源，包含评分和标签') }}</p>
    </div>

    <div class="searcher-content">
      <div class="search-section">
        <el-form :model="searchForm" label-position="top">
          <el-form-item :label="t('关键词')">
            <el-input
              v-model="searchForm.keyword"
              :placeholder="t('请输入搜索关键词')"
              @keyup.enter="searchResources"
            >
              <template #append>
                <el-button @click="searchResources" :loading="isLoading">
                  <i class="fas fa-search"></i>
                </el-button>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item :label="t('资源类型')">
            <el-select
              v-model="searchForm.types"
              multiple
              collapse-tags
              :placeholder="t('请选择资源类型')"
            >
              <el-option
                v-for="type in resourceTypes"
                :key="type.value"
                :label="t(type.label)"
                :value="type.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item :label="t('难度等级')">
            <el-rate
              v-model="searchForm.difficulty"
              :texts="difficultyTexts"
              show-text
            />
          </el-form-item>

          <el-form-item :label="t('排序方式')">
            <el-radio-group v-model="searchForm.sort">
              <el-radio-button value="relevance">{{ t('相关度') }}</el-radio-button>
              <el-radio-button value="rating">{{ t('评分') }}</el-radio-button>
              <el-radio-button value="date">{{ t('最新') }}</el-radio-button>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>

      <div class="result-section" v-if="resources.length > 0">
        <h3>{{ t('搜索结果') }}</h3>
        <el-card
          v-for="resource in resources"
          :key="resource.id"
          class="resource-card"
        >
          <div class="resource-header">
            <h4>
              <el-link :href="resource.url" target="_blank" type="primary">
                {{ resource.title }}
              </el-link>
            </h4>
            <div class="resource-meta">
              <el-tag size="small" :type="getTypeTag(resource.type)">
                {{ t(resource.type) }}
              </el-tag>
              <el-rate
                v-model="resource.rating"
                disabled
                text-color="#ff9900"
              />
              <span class="review-count">({{ resource.reviewCount }})</span>
            </div>
          </div>

          <p class="resource-description">{{ resource.description }}</p>

          <div class="resource-tags">
            <el-tag
              v-for="tag in resource.tags"
              :key="tag"
              size="small"
              class="tag"
              effect="plain"
            >
              {{ tag }}
            </el-tag>
          </div>

          <div class="resource-footer">
            <span class="author">{{ t('作者') }}: {{ resource.author }}</span>
            <span class="date">{{ formatDate(resource.date) }}</span>
          </div>
        </el-card>

        <div class="pagination-container" v-if="total > 0">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 30, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>

      <div class="no-result" v-else-if="hasSearched">
        <el-empty :description="t('暂无搜索结果')" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useSettings, t } from '../../store/settings'
import { ElMessage } from 'element-plus'
import { searchResources as searchResourcesApi } from '../../api'

const settings = useSettings()

// 资源类型选项
const resourceTypes = [
  { value: 'video', label: '视频教程' },
  { value: 'article', label: '文章' },
  { value: 'document', label: '文档' },
  { value: 'course', label: '在线课程' },
  { value: 'book', label: '电子书' },
  { value: 'tool', label: '工具' }
]

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
  types: [],
  difficulty: 0,
  sort: 'relevance'
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
const searchResources = async () => {
  if (!searchForm.keyword.trim()) {
    ElMessage.warning(t('请输入搜索关键词'))
    return
  }

  isLoading.value = true
  try {
    const response = await searchResourcesApi({
      query: searchForm.keyword,
      resource_type: searchForm.types.join(','),
      difficulty: searchForm.difficulty
    })
    resources.value = response.data.data
    total.value = resources.value.length
    hasSearched.value = true
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
const getTypeTag = (type) => {
  const types = {
    'video': 'success',
    'article': 'info',
    'document': 'warning',
    'course': 'danger',
    'book': '',
    'tool': 'primary'
  }
  return types[type] || 'info'
}

// 格式化日期
const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}
</script>

<style scoped>
.resource-searcher-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
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

.resource-tags {
  margin-bottom: 1rem;
}

.tag {
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
}

.resource-footer {
  display: flex;
  justify-content: space-between;
  color: var(--text-color-secondary);
  font-size: 0.9rem;
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
</style>