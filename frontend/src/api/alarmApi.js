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

// 告警信息API服务
export default {
  // 获取告警列表
  async getAlarms(params = {}) {
    try {
      const response = await api.get('/alarms/', { params })
      return response
    } catch (error) {
      console.error('获取告警列表失败:', error)
      throw error
    }
  },

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

  // 获取单个告警详情
  async getAlarmDetail(alarmId) {
    try {
      const response = await api.get(`/alarms/${alarmId}/`)
      return response
    } catch (error) {
      console.error('获取告警详情失败:', error)
      throw error
    }
  },

  // 创建新告警
  async createAlarm(alarmData) {
    try {
      const response = await api.post('/alarms/', alarmData)
      return response
    } catch (error) {
      console.error('创建告警失败:', error)
      throw error
    }
  },

  // 更新告警
  async updateAlarm(alarmId, alarmData) {
    try {
      const response = await api.put(`/alarms/${alarmId}/`, alarmData)
      return response
    } catch (error) {
      console.error('更新告警失败:', error)
      throw error
    }
  },

  // 部分更新告警（如状态）
  async patchAlarm(alarmId, alarmData) {
    try {
      const response = await api.patch(`/alarms/${alarmId}/`, alarmData)
      return response
    } catch (error) {
      console.error('部分更新告警失败:', error)
      throw error
    }
  },

  // 删除告警
  async deleteAlarm(alarmId) {
    try {
      const response = await api.delete(`/alarms/${alarmId}/`)
      return response
    } catch (error) {
      console.error('删除告警失败:', error)
      throw error
    }
  },

  // 获取告警类型列表
  async getAlarmCategories() {
    try {
      const response = await api.get('/alarm-categories/')
      return response
    } catch (error) {
      console.error('获取告警类型列表失败:', error)
      throw error
    }
  }
}