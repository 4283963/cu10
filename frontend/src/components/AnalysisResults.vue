<template>
  <div class="analysis-results">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-700">分析结果</h3>
      <div class="flex items-center gap-2" v-if="props.historyCount > 0">
        <button
          class="btn-secondary text-sm px-3 py-1.5"
          @click="$emit('export-excel')"
          title="导出 Excel"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </button>
        <button
          class="text-sm text-gray-500 hover:text-red-500 px-2 py-1"
          @click="$emit('clear-history')"
          title="清空历史"
        >
          清空
        </button>
      </div>
    </div>
    
    <div v-if="!data" class="text-center py-8 text-gray-400">
      <svg class="w-16 h-16 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <p>暂无分析数据</p>
      <p class="text-sm mt-1">上传图片后点击开始分析</p>
    </div>

    <div v-else class="space-y-4">
      <!-- 花瓣形态分类 -->
      <div class="p-4 rounded-xl border-2" :class="shapeCardClass">
        <h4 class="text-sm font-medium text-gray-600 mb-3 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
          </svg>
          形态分类结果
        </h4>
        <div class="flex items-center gap-4">
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <span
                class="w-3 h-3 rounded-full"
                :class="shapeDotClass"
              ></span>
              <span class="text-2xl font-bold" :class="shapeTextClass">{{ data.shape_type || '未知' }}</span>
            </div>
            <div class="text-xs text-gray-500 mt-1">
              基于面积、周长、锯齿综合判定</div>
          </div>
        </div>
        <div class="mt-3 space-y-1.5">
          <div v-for="(score, shape) in data.shape_score" :key="shape" class="flex items-center gap-2">
            <span class="text-xs text-gray-600 w-14">{{ shape }}</span>
            <div class="flex-1 bg-gray-200 rounded-full h-1.5">
              <div
                class="h-1.5 rounded-full transition-all duration-500"
                :class="shapeBarClass(shape)"
                :style="{ width: score + '%' }"
              ></div>
            </div>
            <span class="text-xs text-gray-500 w-12 text-right">{{ score.toFixed(1) }}%</span>
          </div>
        </div>
      </div>

      <!-- 核心指标 -->
      <div class="grid grid-cols-2 gap-4">
        <div class="stat-card bg-blue-50 rounded-xl p-4 border border-blue-100">
          <div class="text-blue-600 text-sm font-medium mb-1">脉络数量</div>
          <div class="text-2xl font-bold text-blue-700">{{ data.vein_count }}</div>
          <div class="text-xs text-blue-500 mt-1">条</div>
        </div>
        
        <div class="stat-card bg-red-50 rounded-xl p-4 border border-red-100">
          <div class="text-red-600 text-sm font-medium mb-1">锯齿数量</div>
          <div class="text-2xl font-bold text-red-700">{{ data.serration_count }}</div>
          <div class="text-xs text-red-500 mt-1">个</div>
        </div>
      </div>

      <!-- 面积相关 -->
      <div class="card p-4">
        <h4 class="text-sm font-medium text-gray-600 mb-3 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
          </svg>
          面积参数
        </h4>
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-gray-600 text-sm">花瓣面积</span>
            <span class="font-semibold text-gray-800">{{ formatNumber(data.petal_area) }} px²</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-gray-600 text-sm">锯齿总面积</span>
            <span class="font-semibold text-gray-800">{{ formatNumber(data.serration_area) }} px²</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div 
              class="bg-green-500 h-2 rounded-full transition-all duration-500"
              :style="{ width: serrationRatio + '%' }"
            ></div>
          </div>
          <div class="text-xs text-gray-500 text-right">锯齿占比: {{ serrationRatio.toFixed(2) }}%</div>
        </div>
      </div>

      <!-- 形状参数 -->
      <div class="card p-4">
        <h4 class="text-sm font-medium text-gray-600 mb-3 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
          </svg>
          形状参数
        </h4>
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-gray-600 text-sm">花瓣周长</span>
            <span class="font-semibold text-gray-800">{{ formatNumber(data.petal_perimeter) }} px</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-gray-600 text-sm">圆形度</span>
            <span class="font-semibold text-gray-800">{{ formatNumber(data.circularity) }}</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div 
              class="bg-purple-500 h-2 rounded-full transition-all duration-500"
              :style="{ width: Math.min(data.circularity * 100, 100) + '%' }"
            ></div>
          </div>
          <div class="text-xs text-gray-500 text-right">值越接近 1 越接近圆形</div>
        </div>
      </div>

      <!-- 图像信息 -->
      <div class="card p-4">
        <h4 class="text-sm font-medium text-gray-600 mb-3 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          图像信息
        </h4>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div class="text-gray-600">宽度</div>
          <div class="text-gray-800 font-medium text-right">{{ data.original_width }} px</div>
          <div class="text-gray-600">高度</div>
          <div class="text-gray-800 font-medium text-right">{{ data.original_height }} px</div>
        </div>
      </div>

      <!-- 标记点统计 -->
      <div class="card p-4">
        <h4 class="text-sm font-medium text-gray-600 mb-3 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          标记点统计
        </h4>
        <div class="flex gap-4">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-blue-500"></span>
            <span class="text-sm text-gray-600">脉络点: {{ data.vein_points?.length || 0 }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-red-500"></span>
            <span class="text-sm text-gray-600">锯齿点: {{ data.serration_points?.length || 0 }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: null
  },
  historyCount: {
    type: Number,
    default: 0
  }
})

defineEmits(['export-excel', 'clear-history'])

const serrationRatio = computed(() => {
  if (!props.data || props.data.petal_area === 0) return 0
  return (props.data.serration_area / props.data.petal_area) * 100
})

function formatNumber(num) {
  if (num === undefined || num === null) return '0'
  return Number(num).toLocaleString('zh-CN', { maximumFractionDigits: 2 })
}

const shapeType = computed(() => props.data?.shape_type || '未知')

const shapeCardClass = computed(() => {
  const map = {
    '圆形': 'bg-blue-50 border-blue-200',
    '尖形': 'bg-yellow-50 border-yellow-200',
    '波浪形': 'bg-red-50 border-red-200',
    '未知': 'bg-gray-50 border-gray-200'
  }
  return map[shapeType.value] || map['未知']
})

const shapeTextClass = computed(() => {
  const map = {
    '圆形': 'text-blue-700',
    '尖形': 'text-yellow-700',
    '波浪形': 'text-red-700',
    '未知': 'text-gray-700'
  }
  return map[shapeType.value] || map['未知']
})

const shapeDotClass = computed(() => {
  const map = {
    '圆形': 'bg-blue-500',
    '尖形': 'bg-yellow-500',
    '波浪形': 'bg-red-500',
    '未知': 'bg-gray-500'
  }
  return map[shapeType.value] || map['未知']
})

function shapeBarClass(shape) {
  const map = {
    '圆形': 'bg-blue-500',
    '尖形': 'bg-yellow-500',
    '波浪形': 'bg-red-500',
    '未知': 'bg-gray-500'
  }
  return map[shape] || map['未知']
}
</script>
