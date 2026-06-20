<template>
  <div class="image-comparison">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-700">图像分析对比</h3>
      <div class="flex gap-2">
        <button
          v-for="mode in viewModes"
          :key="mode.value"
          class="px-3 py-1 text-sm rounded-lg transition-colors"
          :class="{
            'bg-green-600 text-white': currentMode === mode.value,
            'bg-gray-200 text-gray-700 hover:bg-gray-300': currentMode !== mode.value,
          }"
          @click="currentMode = mode.value"
        >
          {{ mode.label }}
        </button>
      </div>
    </div>

    <div 
      ref="containerRef"
      class="comparison-container relative bg-gray-100 rounded-xl overflow-hidden"
      :style="{ height: containerHeight + 'px' }"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseUp"
    >
      <!-- 原始图片层 -->
      <canvas
        ref="originalCanvas"
        class="absolute inset-0 w-full h-full"
      ></canvas>

      <!-- 分析结果层 -->
      <canvas
        ref="overlayCanvas"
        class="absolute inset-0 w-full h-full"
      ></canvas>

      <!-- 对比分割线 -->
      <div
        v-if="currentMode === 'compare'"
        class="comparison-slider"
        :style="{ left: sliderPosition + '%' }"
      >
        <div class="comparison-handle">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
          </svg>
        </div>
      </div>

      <!-- 加载状态 -->
      <div
        v-if="isLoading"
        class="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-20"
      >
        <div class="text-white text-center">
          <svg class="animate-spin h-10 w-10 mx-auto mb-2" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p>正在渲染分析结果...</p>
        </div>
      </div>

      <!-- 空状态 -->
      <div
        v-if="!hasImage && !isLoading"
        class="absolute inset-0 flex items-center justify-center text-gray-400"
      >
        <div class="text-center">
          <svg class="w-16 h-16 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p>请上传图片进行分析</p>
        </div>
      </div>
    </div>

    <!-- 图例 -->
    <div class="mt-4 flex flex-wrap gap-6 justify-center text-sm">
      <div class="flex items-center gap-2">
        <span class="w-6 h-0.5 bg-green-500"></span>
        <span class="text-gray-600">花瓣轮廓</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="w-3 h-3 rounded-full bg-blue-500"></span>
        <span class="text-gray-600">脉络标记</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="w-3 h-3 rounded-full bg-red-500"></span>
        <span class="text-gray-600">锯齿标记</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'

const props = defineProps({
  originalImage: {
    type: String,
    default: ''
  },
  analysisData: {
    type: Object,
    default: null
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const viewModes = [
  { value: 'original', label: '原图' },
  { value: 'overlay', label: '叠加' },
  { value: 'compare', label: '对比' }
]

const currentMode = ref('overlay')
const sliderPosition = ref(50)
const containerHeight = ref(400)
const containerRef = ref(null)
const originalCanvas = ref(null)
const overlayCanvas = ref(null)

const originalImg = ref(null)
const isDragging = ref(false)
const animationId = ref(null)

const scale = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)

const hasImage = computed(() => !!originalImg.value)

watch(() => props.originalImage, (newVal) => {
  if (newVal) {
    loadOriginalImage(newVal)
  }
})

watch(() => props.analysisData, (newVal) => {
  if (newVal && originalImg.value) {
    nextTick(() => {
      drawOverlay()
    })
  }
})

watch(currentMode, () => {
  if (originalImg.value) {
    nextTick(() => {
      drawOverlay()
    })
  }
})

watch(sliderPosition, () => {
  if (currentMode.value === 'compare' && originalImg.value) {
    drawOverlay()
  }
})

function loadOriginalImage(src) {
  const img = new Image()
  img.onload = () => {
    originalImg.value = img
    drawOriginal()
    if (props.analysisData) {
      drawOverlay()
    }
  }
  img.src = src
}

function drawOriginal() {
  if (!originalCanvas.value || !originalImg.value) return

  const canvas = originalCanvas.value
  const ctx = canvas.getContext('2d')
  const rect = canvas.parentElement.getBoundingClientRect()

  canvas.width = rect.width
  canvas.height = rect.height

  const imgRatio = originalImg.value.width / originalImg.value.height
  const canvasRatio = rect.width / rect.height

  let drawWidth, drawHeight
  if (imgRatio > canvasRatio) {
    drawWidth = rect.width
    drawHeight = rect.width / imgRatio
  } else {
    drawHeight = rect.height
    drawWidth = rect.height * imgRatio
  }

  scale.value = drawWidth / originalImg.value.width
  offsetX.value = (rect.width - drawWidth) / 2
  offsetY.value = (rect.height - drawHeight) / 2

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(originalImg.value, offsetX.value, offsetY.value, drawWidth, drawHeight)
}

function drawOverlay() {
  if (!overlayCanvas.value || !originalImg.value) return

  const canvas = overlayCanvas.value
  const ctx = canvas.getContext('2d')
  const rect = canvas.parentElement.getBoundingClientRect()

  canvas.width = rect.width
  canvas.height = rect.height

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  const s = scale.value
  const ox = offsetX.value
  const oy = offsetY.value

  if (currentMode.value === 'original') {
    return
  }

  if (currentMode.value === 'compare') {
    const clipX = (sliderPosition.value / 100) * rect.width
    
    ctx.save()
    ctx.beginPath()
    ctx.rect(clipX, 0, rect.width - clipX, rect.height)
    ctx.clip()
  }

  if (props.analysisData?.contours?.length > 0) {
    props.analysisData.contours.forEach(contour => {
      if (contour.length > 0) {
        ctx.beginPath()
        ctx.strokeStyle = '#22c55e'
        ctx.lineWidth = 2
        
        contour.forEach((point, index) => {
          const x = ox + point[0] * s
          const y = oy + point[1] * s
          if (index === 0) {
            ctx.moveTo(x, y)
          } else {
            ctx.lineTo(x, y)
          }
        })
        ctx.closePath()
        ctx.stroke()

        ctx.fillStyle = 'rgba(34, 197, 94, 0.15)'
        ctx.fill()
      }
    })
  }

  if (props.analysisData?.vein_points?.length > 0) {
    ctx.fillStyle = '#3b82f6'
    props.analysisData.vein_points.forEach(point => {
      const x = ox + point[0] * s
      const y = oy + point[1] * s
      ctx.beginPath()
      ctx.arc(x, y, 4, 0, Math.PI * 2)
      ctx.fill()
    })
  }

  if (props.analysisData?.serration_points?.length > 0) {
    ctx.fillStyle = '#ef4444'
    props.analysisData.serration_points.forEach(point => {
      const x = ox + point[0] * s
      const y = oy + point[1] * s
      ctx.beginPath()
      ctx.arc(x, y, 5, 0, Math.PI * 2)
      ctx.fill()
    })
  }

  if (currentMode.value === 'compare') {
    ctx.restore()
  }

  startAnimation()
}

function startAnimation() {
  if (animationId.value) {
    cancelAnimationFrame(animationId.value)
  }
  
  let pulsePhase = 0
  
  function animate() {
    pulsePhase += 0.05
    const pulse = Math.sin(pulsePhase) * 0.3 + 0.7
    
    if (!overlayCanvas.value || currentMode.value === 'original') {
      animationId.value = requestAnimationFrame(animate)
      return
    }

    const canvas = overlayCanvas.value
    const ctx = canvas.getContext('2d')
    const s = scale.value
    const ox = offsetX.value
    const oy = offsetY.value

    if (props.analysisData?.vein_points?.length > 0) {
      props.analysisData.vein_points.forEach(point => {
        const x = ox + point[0] * s
        const y = oy + point[1] * s
        const radius = 4 * pulse
        
        ctx.beginPath()
        ctx.fillStyle = `rgba(59, 130, 246, ${0.5 * pulse})`
        ctx.arc(x, y, radius + 3, 0, Math.PI * 2)
        ctx.fill()
      })
    }

    if (props.analysisData?.serration_points?.length > 0) {
      props.analysisData.serration_points.forEach(point => {
        const x = ox + point[0] * s
        const y = oy + point[1] * s
        const radius = 5 * pulse
        
        ctx.beginPath()
        ctx.fillStyle = `rgba(239, 68, 68, ${0.5 * pulse})`
        ctx.arc(x, y, radius + 4, 0, Math.PI * 2)
        ctx.fill()
      })
    }

    animationId.value = requestAnimationFrame(animate)
  }
  
  animate()
}

function handleMouseDown(e) {
  if (currentMode.value !== 'compare') return
  isDragging.value = true
}

function handleMouseMove(e) {
  if (!isDragging.value || currentMode.value !== 'compare') return
  
  const rect = containerRef.value?.getBoundingClientRect()
  if (!rect) return
  
  const x = ((e.clientX - rect.left) / rect.width) * 100
  sliderPosition.value = Math.max(0, Math.min(100, x))
}

function handleMouseUp() {
  isDragging.value = false
}

function handleResize() {
  if (originalImg.value) {
    drawOriginal()
    if (props.analysisData) {
      drawOverlay()
    }
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  
  nextTick(() => {
    if (props.originalImage) {
      loadOriginalImage(props.originalImage)
    }
  })
})

defineExpose({
  redraw: drawOverlay
})
</script>

<style scoped>
.comparison-container {
  min-height: 300px;
  user-select: none;
}

.comparison-slider {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: white;
  cursor: ew-resize;
  transform: translateX(-50%);
  z-index: 10;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.comparison-handle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  background-color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  color: #374151;
}

.comparison-handle svg {
  width: 20px;
  height: 20px;
}
</style>
