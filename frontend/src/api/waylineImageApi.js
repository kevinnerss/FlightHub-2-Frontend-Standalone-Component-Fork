import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截：直接返回 data
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('WaylineImage API 请求错误:', error)
    return Promise.reject(error)
  }
)

export default {
  async getImages(params = {}) {
    return api.get('/wayline-images/', { params })
  },

  async createImage(payload) {
    return api.post('/wayline-images/', payload)
  },

  async deleteImage(id) {
    return api.delete(`/wayline-images/${id}/`)
  }
}
