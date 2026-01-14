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
  async getPositions(params = {}) {
    try {
      return await api.get('/drone-positions/', { params })
    } catch (error) {
      console.error('Failed to fetch drone positions:', error)
      throw error
    }
  }
}
