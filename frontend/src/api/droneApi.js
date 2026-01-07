
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

// 模拟数据 - 在实际项目中会被真实API替代
const mockData = {
  routes: [
    {
      id: 1,
      name: '高压线路巡检',
      status: 'completed',
      length: 15.2,
      duration: 45,
      lastFlight: '2024-01-15 10:30:00',
      checkpoints: 25
    },
    {
      id: 2,
      name: '变电站设备检查',
      status: 'in_progress',
      length: 3.8,
      duration: 20,
      lastFlight: '2024-01-15 14:15:00',
      checkpoints: 12
    },
    {
      id: 3,
      name: '风电场巡检',
      status: 'pending',
      length: 22.5,
      duration: 60,
      lastFlight: '2024-01-14 16:45:00',
      checkpoints: 36
    },
    {
      id: 4,
      name: '光伏电站检查',
      status: 'pending',
      length: 8.3,
      duration: 30,
      lastFlight: '2024-01-14 09:20:00',
      checkpoints: 18
    },
    {
      id: 5,
      name: '输电线路走廊巡查',
      status: 'completed',
      length: 35.6,
      duration: 90,
      lastFlight: '2024-01-13 13:50:00',
      checkpoints: 52
    }
  ],
  taskData: {
    progress: 65,
    currentTask: {
      name: '变电站设备检查',
      id: 'T-20240115-001'
    },
    remainingTime: '12:45',
    completedTasks: 8,
    totalTasks: 12
  },
  alarms: [
    {
      id: 1,
      title: '电力线异常发热',
      description: '在坐标(23.124, 113.235)处检测到电力线温度异常升高，可能存在线路老化或过载情况。',
      timestamp: '2024-01-15T14:22:35',
      location: '变电站A区域-东线路',
      type: '温度异常',
      severity: '高',
      imageUrl: 'https://picsum.photos/800/600?random=1'
    },
    {
      id: 2,
      title: '绝缘子损伤',
      description: '在铁塔#128处发现绝缘子表面有明显裂纹，需要进一步检查。',
      timestamp: '2024-01-15T13:45:12',
      location: '铁塔#128',
      type: '设备损伤',
      severity: '中',
      imageUrl: 'https://picsum.photos/800/600?random=2'
    },
    {
      id: 3,
      title: '植被靠近',
      description: '在110kV线路#45-#46段发现树木生长过盛，距离线路仅2.5米，存在安全隐患。',
      timestamp: '2024-01-15T12:30:48',
      location: '线路#45-#46',
      type: '通道隐患',
      severity: '低',
      imageUrl: 'https://picsum.photos/800/600?random=3'
    }
  ],
  droneStatus: {
    status: '飞行中',
    batteryLevel: 78,
    altitude: 35,
    speed: 8,
    videoStreamUrl: 'https://picsum.photos/1280/720?random=10',
    isStreaming: true
  }
}

// API方法
export default {
  // 获取航线列表
  async getRoutes() {
    try {
      // 使用真实API
      return await api.get('/routes')
    } catch (error) {
      console.error('获取航线列表失败，使用模拟数据:', error)
      // 出错时返回模拟数据
      return mockData.routes
    }
  },

  // 获取任务数据
  async getTaskData() {
    try {
      // 使用真实API
      return await api.get('/tasks/current')
    } catch (error) {
      console.error('获取任务数据失败，使用模拟数据:', error)
      return mockData.taskData
    }
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
      console.error('获取报警列表失败，使用模拟数据:', error)
      return mockData.alarms
    }
  },

  // 获取无人机状态
  async getDroneStatus() {
    try {
      // 使用真实API
      return await api.get('/drone/status')
    } catch (error) {
      console.error('获取无人机状态失败，使用模拟数据:', error)
      return mockData.droneStatus
    }
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
