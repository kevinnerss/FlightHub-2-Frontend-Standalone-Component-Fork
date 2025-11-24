import axios from 'axios'

// axios 实例
const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 自动附带认证 token
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
  error => Promise.reject(error)
)

let cachedConfig = null

export default {
  /**
   * 获取组件公共参数配置
   * @param {boolean} force 是否强制刷新缓存
   */
  async getConfig(force = false) {
    if (cachedConfig && !force) return cachedConfig
    const data = await api.get('/component-config/1/')
    cachedConfig = data
    return data
  },

  /**
   * 更新组件公共参数配置
   * @param {object} payload 配置对象
   */
  async updateConfig(payload) {
    const data = await api.patch('/component-config/1/', payload)
    cachedConfig = data
    return data
  },

  /**
   * 清除本地缓存
   */
  clearCache() {
    cachedConfig = null
  }
}
