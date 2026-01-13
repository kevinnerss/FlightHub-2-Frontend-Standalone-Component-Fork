
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
    // 添加认证 token（若存在）
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

// API方法
export default {
  // 获取航线列表
  async getRoutes() {
    return await api.get('/routes')
  },

  // 获取任务数据
  async getTaskData() {
    return await api.get('/tasks/current')
  },

  // 获取报警列表
  async getAlarms() {
    try {
      // 使用真实API获取告警数据
      const response = await api.get('/alarms/')

      // 转换数据格式以匹配前端组件的期望格式
      const alarms = response.map(alarm => ({
        id: alarm.id,
        title: alarm.category_details.name,
        description: alarm.content,
        timestamp: alarm.created_at,
        location: `坐标(${alarm.latitude}, ${alarm.longitude})`,
        type: alarm.category_details.name,
        severity: alarm.status === 'PENDING' ? '高' :
          alarm.status === 'PROCESSING' ? '中' : '低',
        imageUrl: alarm.image_url || ''
      }))

      return alarms
    } catch (error) {
      console.error('获取报警列表失败:', error)
      throw error
    }
  },

  // 获取无人机状态
  async getDroneStatus() {
    return await api.get('/drone/status')
  },

  // 处理报警
  async processAlarm(alarmId) {
    try {
      // 使用真实API处理报警
      const response = await api.patch(`/alarms/${alarmId}/`, {
        status: 'PROCESSING',
        handler: 'Frontend User'
      })
      return { success: true, data: response }
    } catch (error) {
      console.error('处理报警失败:', error)
      throw error
    }
  },

  // 控制无人机
  async controlDrone(action) {
    try {
      // 使用真实API控制无人机
      const response = await api.post('/drone/control/', { action })
      return { success: true, data: response }
    } catch (error) {
      console.error('控制无人机失败:', error)
      throw error
    }
  },

  // 更新高度
  async updateAltitude(altitude) {
    try {
      // 使用真实API更新高度
      const response = await api.put('/drone/altitude/', { altitude })
      return { success: true, data: response }
    } catch (error) {
      console.error('更新高度失败:', error)
      throw error
    }
  },

  // 更新速度
  async updateSpeed(speed) {
    try {
      // 使用真实API更新速度
      const response = await api.put('/drone/speed/', { speed })
      return { success: true, data: response }
    } catch (error) {
      console.error('更新速度失败:', error)
      throw error
    }
  },

  // 紧急停止
  async emergencyStop() {
    try {
      // 使用真实API执行紧急停止
      const response = await api.post('/drone/emergency-stop/')
      return { success: true, data: response }
    } catch (error) {
      console.error('紧急停止失败:', error)
      throw error
    }
  },

  // 获取设备列表（后端代理司空 /openapi/v0.1/device）
  async getDevices(params = {}) {
    try {
      const response = await api.get('/flight-task-proxy/devices', { params })
      return response
    } catch (error) {
      console.error('获取设备列表失败:', error)
      throw error
    }
  }
}
