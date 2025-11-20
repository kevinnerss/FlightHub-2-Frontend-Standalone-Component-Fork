import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加token等认证信息
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

// 航线信息API服务
export default {
  // 获取航线列表
  async getWaylines(params = {}) {
    try {
      const response = await api.get('/waylines/', { params })
      return response
    } catch (error) {
      console.error('获取航线列表失败:', error)
      throw error
    }
  },

  // 获取单个航线详情
  async getWaylineDetail(waylineId) {
    try {
      const response = await api.get(`/waylines/${waylineId}/`)
      return response
    } catch (error) {
      console.error('获取航线详情失败:', error)
      throw error
    }
  },

  // 创建新航线
  async createWayline(waylineData) {
    try {
      const response = await api.post('/waylines/', waylineData)
      return response
    } catch (error) {
      console.error('创建航线失败:', error)
      throw error
    }
  },

  // 更新航线
  async updateWayline(waylineId, waylineData) {
    try {
      const response = await api.put(`/waylines/${waylineId}/`, waylineData)
      return response
    } catch (error) {
      console.error('更新航线失败:', error)
      throw error
    }
  },

  // 部分更新航线
  async patchWayline(waylineId, waylineData) {
    try {
      const response = await api.patch(`/waylines/${waylineId}/`, waylineData)
      return response
    } catch (error) {
      console.error('部分更新航线失败:', error)
      throw error
    }
  },

  // 删除航线
  async deleteWayline(waylineId) {
    try {
      const response = await api.delete(`/waylines/${waylineId}/`)
      return response
    } catch (error) {
      console.error('删除航线失败:', error)
      throw error
    }
  }
}