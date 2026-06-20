import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export async function analyzeImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  
  return response.data
}

export async function analyzePreview(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/analyze/preview', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  
  return response.data
}

export async function getHealth() {
  const response = await api.get('/health')
  return response.data
}

export default api
