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

// 巡检任务API服务
export default {
  // 获取巡检任务列表
  async getInspectTasks(params = {}) {
    try {
      const response = await api.get('/inspect-tasks/', { params })
      return response
    } catch (error) {
      console.error('获取巡检任务列表失败:', error)
      throw error
    }
  },

  // 获取单个巡检任务详情
  async getInspectTaskDetail(taskId) {
    try {
      const response = await api.get(`/inspect-tasks/${taskId}/`)
      return response
    } catch (error) {
      console.error('获取巡检任务详情失败:', error)
      throw error
    }
  },

  // 创建新巡检任务
  async createInspectTask(taskData) {
    try {
      const response = await api.post('/inspect-tasks/', taskData)
      return response
    } catch (error) {
      console.error('创建巡检任务失败:', error)
      throw error
    }
  },

  // 更新巡检任务
  async updateInspectTask(taskId, taskData) {
    try {
      const response = await api.put(`/inspect-tasks/${taskId}/`, taskData)
      return response
    } catch (error) {
      console.error('更新巡检任务失败:', error)
      throw error
    }
  },

  // 部分更新巡检任务
  async patchInspectTask(taskId, taskData) {
    try {
      const response = await api.patch(`/inspect-tasks/${taskId}/`, taskData)
      return response
    } catch (error) {
      console.error('部分更新巡检任务失败:', error)
      throw error
    }
  },

  // 删除巡检任务
  async deleteInspectTask(taskId) {
    try {
      const response = await api.delete(`/inspect-tasks/${taskId}/`)
      return response
    } catch (error) {
      console.error('删除巡检任务失败:', error)
      throw error
    }
  },

  // 同步图片
  async syncImages(taskId) {
    try {
      const response = await api.post(`/inspect-tasks/${taskId}/sync_images/`)
      return response
    } catch (error) {
      console.error('同步图片失败:', error)
      throw error
    }
  },

  // 触发检测
  async triggerDetect(taskId) {
    try {
      const response = await api.post(`/inspect-tasks/${taskId}/trigger_detect/`)
      return response
    } catch (error) {
      console.error('触发检测失败:', error)
      throw error
    }
  },

  // 预扫描 MinIO 目录
  async scanCandidateFolders() {
    try {
      const response = await api.get('/scan_candidate_folders')
      return response
    } catch (error) {
      console.error('预扫描任务文件夹失败:', error)
      throw error
    }
  },

  // 批量启动检测任务
  async startSelectedTasks(folders = []) {
    try {
      const response = await api.post('/start_selected_tasks', { folders })
      return response
    } catch (error) {
      console.error('启动检测任务失败:', error)
      throw error
    }
  },

  // 强制结束检测任务
  async stopDetect(payload = {}) {
    try {
      const response = await api.post('/stop_detect', payload)
      return response
    } catch (error) {
      console.error('结束检测任务失败:', error)
      throw error
    }
  },

  // 获取父任务的子任务列表
  async getSubTasks(parentId) {
    try {
      const response = await api.get(`/inspect-tasks/${parentId}/sub_tasks/`)
      return response
    } catch (error) {
      console.error('获取子任务列表失败:', error)
      throw error
    }
  },

  // 获取某个巡检任务下的图片列表
  async getTaskImages(taskId) {
    try {
      const response = await api.get(`/inspect-tasks/${taskId}/images/`)
      return response
    } catch (error) {
      console.error('获取巡检任务图片失败:', error)
      throw error
    }
  },

  // 启动巡检任务（将pending改为scanning）
  async startTask(taskId) {
    try {
      const response = await api.post(`/inspect-tasks/${taskId}/start/`)
      return response
    } catch (error) {
      console.error('启动巡检任务失败:', error)
      throw error
    }
  },

  // 强制结束任务并删除所有相关记录（InspectTask, InspectImage, Alarm）
  async forceDeleteTask(taskId) {
    try {
      const response = await api.delete(`/inspect-tasks/${taskId}/force_delete/`)
      return response
    } catch (error) {
      console.error('强制删除任务失败:', error)
      throw error
    }
  }
}