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
            <AnalysisResults :data="analysisData" />
          </div>
        </div>

        <!-- 右侧：图像对比 -->
        <div class="lg:col-span-2">
          <div class="card p-6">
            <ImageComparison
              ref="comparisonRef"
              :original-image="originalImage"
              :analysis-data="analysisData"
              :is-loading="isAnalyzing"
            />
          </div>

          <!-- 操作说明 -->
          <div class="card p-6 mt-6">
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
                  <p class="text-gray-500 text-xs mt-1">系统自动检测花瓣形态特征</p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span class="text-green-600 font-bold">3</span>
                </div>
                <div>
                  <p class="font-medium text-gray-700">查看结果</p>
                  <p class="text-gray-500 text-xs mt-1">查看分析数据和可视化标记</p>
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
import { ref } from 'vue'
import axios from 'axios'
import ImageUploader from './components/ImageUploader.vue'
import ImageComparison from './components/ImageComparison.vue'
import AnalysisResults from './components/AnalysisResults.vue'

const uploaderRef = ref(null)
const comparisonRef = ref(null)

const originalImage = ref('')
const analysisData = ref(null)
const isAnalyzing = ref(false)

function handleFileSelected(file, dataUrl) {
  originalImage.value = dataUrl
  analysisData.value = null
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
      originalImage.value = 'data:image/png;base64,' + response.data.original_image
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
</script>
