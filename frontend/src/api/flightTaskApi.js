import axios from 'axios'

// Create axios instance for Backend Proxy
// The proxy endpoint is /api/v1/flight-task-proxy/
const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    // Add token for OUR backend (Django), not for the external DJI API
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('Backend API request error:', error)
    return Promise.reject(error)
  }
)

export default {
  // Get device list (via proxy)
  async getDevices() {
    try {
      // Calls GET /api/v1/flight-task-proxy/devices/
      const response = await api.get('/flight-task-proxy/devices/')
      // Response structure from proxy matches DJI: { code: 0, data: { list: [...] } }
      if (response.code === 0 && response.data && response.data.list) {
        return response.data.list
      }
      return []
    } catch (error) {
      console.error('Failed to get devices:', error)
      throw error
    }
  },

  // Create flight task (via proxy)
  async createFlightTask(taskData) {
    try {
      // Calls POST /api/v1/flight-task-proxy/create/
      const response = await api.post('/flight-task-proxy/create/', taskData)
      return response
    } catch (error) {
      console.error('Failed to create flight task:', error)
      throw error
    }
  }
}
