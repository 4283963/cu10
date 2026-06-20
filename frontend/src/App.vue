<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 via-white to-emerald-50">
    <!-- 头部 -->
    <header class="bg-white shadow-sm border-b border-green-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-green-400 to-emerald-600 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-800">花期标本花瓣多维形态学分析系统</h1>
              <p class="text-sm text-gray-500">植物园标本馆 · 珍稀高山杜鹃标本分析</p>
            </div>
          </div>
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <span class="w-2 h-2 bg-green-500 rounded-full"></span>
            系统运行正常
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- 左侧：上传和结果 -->
        <div class="lg:col-span-1 space-y-6">
          <!-- 上传区域 -->
          <div class="card p-6">
            <ImageUploader
              ref="uploaderRef"
              @analyze="handleAnalyze"
              @file-selected="handleFileSelected"
            />
          </div>

          <!-- 分析结果 -->
          <div class="card p-6">
            <AnalysisResults
              :data="analysisData"
              :history-count="analysisHistory.length"
              @export-excel="exportToExcel"
              @clear-history="clearHistory"
            />
          </div>
        </div>

        <!-- 右侧：图像对比 + 形态统计 -->
        <div class="lg:col-span-2 space-y-6">
          <div class="card p-6">
            <ImageComparison
              ref="comparisonRef"
              :original-image="originalImage"
              :analysis-data="analysisData"
              :is-loading="isAnalyzing"
            />
          </div>

          <!-- 形态学分类统计 -->
          <div class="card p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-700 flex items-center gap-2">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
                </svg>
                形态分类统计
              </h3>
              <span class="text-sm text-gray-500">共分析 {{ analysisHistory.length }} 张标本</span>
            </div>

            <div v-if="analysisHistory.length === 0" class="text-center py-8 text-gray-400">
              <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <p>暂无统计数据</p>
              <p class="text-xs mt-1">上传标本图片开始分析</p>
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
              <!-- 饼图 -->
              <div class="flex justify-center">
                <canvas ref="pieChartCanvas" width="220" height="220"></canvas>
              </div>

              <!-- 图例 -->
              <div class="space-y-3">
                <div
                  v-for="(count, shape) in shapeStats"
                  :key="shape"
                  class="flex items-center justify-between p-3 rounded-lg border"
                  :class="shapeBorderClass(shape)"
                >
                  <div class="flex items-center gap-3">
                    <span
                      class="w-4 h-4 rounded-full"
                      :class="shapeColorClass(shape)"
                    ></span>
                    <span class="font-medium text-gray-700">{{ shape }}</span>
                  </div>
                  <div class="text-right">
                    <div class="font-bold text-gray-800">{{ count }}</div>
                    <div class="text-xs text-gray-500">{{ percentage(count) }}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 操作说明 -->
          <div class="card p-6">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">操作说明</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span class="text-green-600 font-bold">1</span>
                </div>
                <div>
                  <p class="font-medium text-gray-700">上传图片</p>
                  <p class="text-gray-500 text-xs mt-1">拖拽或点击上传标本图片</p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span class="text-green-600 font-bold">2</span>
                </div>
                <div>
                  <p class="font-medium text-gray-700">开始分析</p>
                  <p class="text-gray-500 text-xs mt-1">系统自动检测花瓣形态并分类</p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span class="text-green-600 font-bold">3</span>
                </div>
                <div>
                  <p class="font-medium text-gray-700">导出数据</p>
                  <p class="text-gray-500 text-xs mt-1">一键导出 Excel 分析报告</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="bg-white border-t border-gray-100 mt-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex flex-col md:flex-row justify-between items-center gap-4">
          <p class="text-sm text-gray-500">© 2024 植物园标本馆 · 花瓣形态学分析系统</p>
          <div class="flex items-center gap-4 text-sm text-gray-500">
            <span>技术支持：OpenCV + FastAPI + Vue 3</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import axios from 'axios'
import ImageUploader from './components/ImageUploader.vue'
import ImageComparison from './components/ImageComparison.vue'
import AnalysisResults from './components/AnalysisResults.vue'

const uploaderRef = ref(null)
const comparisonRef = ref(null)
const pieChartCanvas = ref(null)

const originalImage = ref('')
const analysisData = ref(null)
const isAnalyzing = ref(false)
const currentFilename = ref('')

const analysisHistory = ref([])

const shapeStats = computed(() => {
  const stats = { '圆形': 0, '尖形': 0, '波浪形': 0, '未知': 0 }
  for (const item of analysisHistory.value) {
    const shape = item.result.shape_type || '未知'
    if (stats.hasOwnProperty(shape)) {
      stats[shape]++
    } else {
      stats['未知']++
    }
  }
  return stats
})

function handleFileSelected(file, dataUrl) {
  originalImage.value = dataUrl
  analysisData.value = null
  currentFilename.value = file.name || ''
}

async function handleAnalyze(file) {
  isAnalyzing.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await axios.post('/api/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.success) {
      analysisData.value = response.data.data
      originalImage.value = 'data:image/png;base64,' + response.data.data.original_image
      
      analysisHistory.value.push({
        filename: file.name || `标本_${Date.now()}.png`,
        result: response.data.data,
        timestamp: Date.now()
      })
    } else {
      alert('分析失败：' + (response.data.message || '未知错误'))
    }
  } catch (error) {
    console.error('分析出错:', error)
    if (error.response) {
      alert('分析失败：' + (error.response.data.detail || error.response.statusText))
    } else {
      alert('分析失败，请检查后端服务是否启动')
    }
  } finally {
    isAnalyzing.value = false
    if (uploaderRef.value) {
      uploaderRef.value.setAnalyzing(false)
    }
  }
}

function clearHistory() {
  analysisHistory.value = []
}

async function exportToExcel() {
  if (analysisHistory.value.length === 0) {
    alert('暂无分析数据可导出')
    return
  }
  
  try {
    const payload = analysisHistory.value.map(item => ({
      filename: item.filename,
      result: item.result
    }))
    
    const response = await axios.post('/api/export/excel', payload, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    const disposition = response.headers['content-disposition']
    let filename = '花瓣形态分析结果.xlsx'
    if (disposition) {
      const match = disposition.match(/filename\*=UTF-8''(.+)/)
      if (match) {
        filename = decodeURIComponent(match[1])
      }
    }
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败：' + (error.response?.data?.detail || error.message))
  }
}

const shapeColors = {
  '圆形': '#60A5FA',
  '尖形': '#FBBF24',
  '波浪形': '#F87171',
  '未知': '#9CA3AF'
}

const shapeBgColors = {
  '圆形': 'bg-blue-100 border-blue-200',
  '尖形': 'bg-yellow-50 border-yellow-200',
  '波浪形': 'bg-red-50 border-red-200',
  '未知': 'bg-gray-50 border-gray-200'
}

const shapeDotClasses = {
  '圆形': 'bg-blue-500',
  '尖形': 'bg-yellow-500',
  '波浪形': 'bg-red-500',
  '未知': 'bg-gray-400'
}

function shapeColorClass(shape) {
  return shapeDotClasses[shape] || 'bg-gray-400'
}

function shapeBorderClass(shape) {
  return shapeBgColors[shape] || 'bg-gray-50 border-gray-200'
}

function percentage(count) {
  const total = analysisHistory.value.length
  if (total === 0) return 0
  return ((count / total) * 100).toFixed(1)
}

function drawPieChart() {
  const canvas = pieChartCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  const total = analysisHistory.value.length
  
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  if (total === 0) return
  
  const centerX = canvas.width / 2
  const centerY = canvas.height / 2
  const radius = Math.min(centerX, centerY) - 10
  const innerRadius = radius * 0.55
  
  let startAngle = -Math.PI / 2
  
  const order = ['圆形', '尖形', '波浪形', '未知']
  
  for (const shape of order) {
    const count = shapeStats.value[shape] || 0
    if (count === 0) continue
    
    const sliceAngle = (count / total) * 2 * Math.PI
    const endAngle = startAngle + sliceAngle
    
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, startAngle, endAngle)
    ctx.arc(centerX, centerY, innerRadius, endAngle, startAngle, true)
    ctx.closePath()
    ctx.fillStyle = shapeColors[shape] || '#9CA3AF'
    ctx.fill()
    
    ctx.strokeStyle = '#FFFFFF'
    ctx.lineWidth = 2
    ctx.stroke()
    
    startAngle = endAngle
  }
  
  ctx.fillStyle = '#1F2937'
  ctx.font = 'bold 24px sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(total.toString(), centerX, centerY - 8)
  
  ctx.fillStyle = '#6B7280'
  ctx.font = '12px sans-serif'
  ctx.fillText('总数', centerX, centerY + 14)
}

watch(
  () => analysisHistory.value.length,
  async () => {
    await nextTick()
    drawPieChart()
  }
)
</script>
