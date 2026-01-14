import axios from 'axios'

const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API request error:', error)
    return Promise.reject(error)
  }
)

export default {
  async getLatestBySn(sn) {
    if (!sn) return {}
    try {
      return await api.get('/flight-task-info/latest-by-sn/', { params: { sn } })
    } catch (error) {
      console.error('Failed to fetch flight task info:', error)
      throw error
    }
  }
}
