import { VideoCamera, Document, Reading, School, Tools } from '@element-plus/icons-vue'

export const resourceTypes = [
  { value: 'video', label: '视频教程', icon: VideoCamera },
  { value: 'article', label: '文章', icon: Document },
  { value: 'document', label: '文档', icon: Document },
  { value: 'course', label: '在线课程', icon: School },
  { value: 'book', label: '电子书', icon: Reading },
  { value: 'tool', label: '工具', icon: Tools }
]

export const typeTagMap = {
  video: 'success',
  article: 'info',
  document: 'warning',
  course: 'danger',
  book: '',
  tool: 'primary'
}

export const typeIconMap = {
  video: VideoCamera,
  article: Document,
  document: Document,
  course: School,
  book: Reading,
  tool: Tools
}