import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  config => {
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

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// 机场状态API方法
export default {
  /**
   * 获取所有机场状态
   */
  async getAllDocks() {
    try {
      const response = await api.get('/dock-status/all_docks/')
      return response
    } catch (error) {
      console.error('获取机场列表失败:', error)
      throw error
    }
  },

  /**
   * 获取在线机场
   */
  async getOnlineDocks() {
    try {
      const response = await api.get('/dock-status/online_docks/')
      return response
    } catch (error) {
      console.error('获取在线机场失败:', error)
      throw error
    }
  },

  /**
   * 获取单个机场详情
   * @param {number} dockId - 机场ID
   */
  async getDockDetail(dockId) {
    try {
      const response = await api.get(`/dock-status/${dockId}/`)
      return response
    } catch (error) {
      console.error('获取机场详情失败:', error)
      throw error
    }
  },

  /**
   * 获取机场历史记录
   * @param {number} dockId - 机场ID
   * @param {Object} params - 查询参数 { start_time, end_time }
   */
  async getDockHistory(dockId, params = {}) {
    try {
      const response = await api.get(`/dock-status/${dockId}/history/`, { params })
      return response
    } catch (error) {
      console.error('获取机场历史记录失败:', error)
      throw error
    }
  },

  /**
   * 获取机场统计信息
   */
  async getDockStatistics() {
    try {
      const response = await api.get('/dock-status/statistics/')
      return response
    } catch (error) {
      console.error('获取机场统计信息失败:', error)
      throw error
    }
  },

  /**
   * 搜索机场
   * @param {Object} params - 查询参数
   */
  async searchDocks(params = {}) {
    try {
      const response = await api.get('/dock-status/', { params })
      return response
    } catch (error) {
      console.error('搜索机场失败:', error)
      throw error
    }
  },

  /**
   * 更新机场名称
   * @param {number} dockId - 机场ID
   * @param {string} dockName - 新名称
   */
  async updateDockName(dockId, dockName) {
    try {
      const response = await api.patch(`/dock-status/${dockId}/`, { dock_name: dockName })
      return response
    } catch (error) {
      console.error('更新机场名称失败:', error)
      throw error
    }
  }
}
