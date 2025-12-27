import axios from 'axios'

const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加 token
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

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  /**
   * 启动直播监听
   * @param {string} streamId - 流ID (例如: drone01)
   * @param {number} interval - 截图间隔(秒)
   */
  async startMonitor(streamId, interval = 3.0) {
    return api.post('/live-monitor/start/', {
      stream_id: streamId,
      interval
    })
  },

  /**
   * 停止直播监听
   * @param {string} streamId - 流ID
   */
  async stopMonitor(streamId) {
    return api.post('/live-monitor/stop/', {
      stream_id: streamId
    })
  },

  /**
   * 获取监听状态
   * @param {string} streamId - 流ID (可选，不传则返回所有)
   */
  async getStatus(streamId = null) {
    const params = streamId ? { stream_id: streamId } : {}
    return api.get('/live-monitor/status/', { params })
  }
}
