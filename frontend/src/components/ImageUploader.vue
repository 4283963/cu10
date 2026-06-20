<template>
  <div class="image-uploader">
    <div
      class="upload-area border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 cursor-pointer"
      :class="{
        'border-green-400 bg-green-50': isDragging,
        'border-gray-300 hover:border-green-500 hover:bg-gray-50': !isDragging && !hasImage,
        'border-green-500 bg-green-50': hasImage,
      }"
      @click="triggerFileInput"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        class="hidden"
        @change="handleFileChange"
      />
      
      <div v-if="!hasImage" class="upload-placeholder">
        <div class="mx-auto w-16 h-16 mb-4 text-green-500">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-700 mb-2">拖拽标本图片到这里</h3>
        <p class="text-gray-500 text-sm mb-4">或点击选择文件</p>
        <p class="text-xs text-gray-400">支持 JPG、PNG、WEBP 等格式</p>
      </div>

      <div v-else class="preview-container">
        <img
          :src="previewUrl"
          alt="预览图片"
          class="max-h-64 mx-auto rounded-lg shadow-md"
        />
        <p class="mt-3 text-sm text-gray-600">{{ fileName }}</p>
        <button
          class="mt-3 text-sm text-green-600 hover:text-green-700 underline"
          @click.stop="clearImage"
        >
          重新选择
        </button>
      </div>
    </div>

    <div class="mt-4 flex justify-center">
      <button
        class="btn-primary px-8"
        :disabled="!hasImage || isAnalyzing"
        :class="{ 'opacity-50 cursor-not-allowed': !hasImage || isAnalyzing }"
        @click="analyzeImage"
      >
        <span v-if="isAnalyzing" class="flex items-center gap-2">
          <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 10.709V12H4v2.291z"></path>
          </svg>
          分析中...
        </span>
        <span v-else>开始分析</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['analyze', 'file-selected'])

const fileInput = ref(null)
const isDragging = ref(false)
const selectedFile = ref(null)
const previewUrl = ref('')
const isAnalyzing = ref(false)

const hasImage = computed(() => !!selectedFile.value)
const fileName = computed(() => selectedFile.value?.name || '')

function triggerFileInput() {
  fileInput.value.click()
}

function handleFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    loadFile(file)
  }
}

function handleDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    loadFile(file)
  }
}

function loadFile(file) {
  selectedFile.value = file
  
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target.result
    emit('file-selected', file, e.target.result)
  }
  reader.readAsDataURL(file)
}

function clearImage() {
  selectedFile.value = null
  previewUrl.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function analyzeImage() {
  if (!selectedFile.value) return
  
  isAnalyzing.value = true
  emit('analyze', selectedFile.value)
}

function setAnalyzing(value) {
  isAnalyzing.value = value
}

defineExpose({
  setAnalyzing,
  clearImage
})
</script>
