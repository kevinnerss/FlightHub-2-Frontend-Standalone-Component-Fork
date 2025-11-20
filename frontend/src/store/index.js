import { createStore } from 'vuex'
import droneApi from '../api/droneApi'
import authApi from '../api/authApi'

export default createStore({
  state: {
    // 无人机航线数据
    droneRoutes: [],
    selectedRoute: null,

    // 任务数据
    taskProgress: 0,
    currentTask: null,
    remainingTime: '',
    completedTasks: 0,
    totalTasks: 0,

    // 报警数据
    alarms: [],

    // 无人机状态
    droneStatus: '待命',
    batteryLevel: 100,
    currentAltitude: 0,
    currentSpeed: 0,
    targetAltitude: 0,
    targetSpeed: 0,

    // 视频流
    videoStreamUrl: '',
    isStreaming: false,

    // 系统状态
    isLoading: false,
    error: null,
    darkMode: true,

    // 用户认证状态
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!localStorage.getItem('token'),
    users: [],

    // 用户管理分页
    currentPage: 1,
    pageSize: 10,
    totalUsers: 0
  },

  mutations: {
    // 设置航线数据
    SET_ROUTES(state, routes) {
      state.droneRoutes = routes
    },
    SET_SELECTED_ROUTE(state, route) {
      state.selectedRoute = route
    },

    // 设置任务数据
    SET_TASK_PROGRESS(state, progress) {
      state.taskProgress = progress
    },
    SET_CURRENT_TASK(state, task) {
      state.currentTask = task
    },
    SET_REMAINING_TIME(state, time) {
      state.remainingTime = time
    },
    SET_TASK_STATS(state, { completed, total }) {
      state.completedTasks = completed
      state.totalTasks = total
    },

    // 设置报警数据
    SET_ALARMS(state, alarms) {
      state.alarms = alarms
    },
    REMOVE_ALARM(state, alarmId) {
      state.alarms = state.alarms.filter(alarm => alarm.id !== alarmId)
    },

    // 设置无人机状态
    SET_DRONE_STATUS(state, status) {
      state.droneStatus = status
    },
    SET_BATTERY_LEVEL(state, level) {
      state.batteryLevel = level
    },
    SET_CURRENT_ALTITUDE(state, altitude) {
      state.currentAltitude = altitude
    },
    SET_CURRENT_SPEED(state, speed) {
      state.currentSpeed = speed
    },
    SET_TARGET_ALTITUDE(state, altitude) {
      state.targetAltitude = altitude
    },
    SET_TARGET_SPEED(state, speed) {
      state.targetSpeed = speed
    },

    // 设置视频流
    SET_VIDEO_STREAM(state, url) {
      state.videoStreamUrl = url
    },
    SET_IS_STREAMING(state, isStreaming) {
      state.isStreaming = isStreaming
    },

    // 系统状态
    SET_LOADING(state, isLoading) {
      state.isLoading = isLoading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    SET_DARK_MODE(state, isDark) {
      state.darkMode = isDark
      document.documentElement.classList.toggle('dark', isDark)
      localStorage.setItem('darkMode', isDark ? 'true' : 'false')
    },

    // 用户认证相关mutation
    SET_USER(state, user) {
      state.user = user
      state.isAuthenticated = true
    },
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    LOGOUT(state) {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      localStorage.removeItem('token')
    },

    // 用户管理相关mutation
    ADD_USER(state, user) {
      state.users.push(user)
    },
    UPDATE_USER(state, updatedUser) {
      const index = state.users.findIndex(user => user.id === updatedUser.id)
      if (index !== -1) {
        state.users[index] = { ...state.users[index], ...updatedUser }
      }
    },
    DELETE_USER(state, userId) {
      state.users = state.users.filter(user => user.id !== userId)
    },

    // 设置用户列表
    SET_USERS(state, users) {
      state.users = users
    },

    // 设置分页信息
    SET_PAGINATION_INFO(state, { currentPage, pageSize, totalUsers }) {
      if (currentPage !== undefined) state.currentPage = currentPage
      if (pageSize !== undefined) state.pageSize = pageSize
      if (totalUsers !== undefined) state.totalUsers = totalUsers
    }
  },

  actions: {
    // 初始化系统数据
    async initializeSystem({ commit }) {
      commit('SET_LOADING', true)
      try {
        // 获取航线数据
        const routes = await droneApi.getRoutes()
        commit('SET_ROUTES', routes)

        // 获取任务数据
        const taskData = await droneApi.getTaskData()
        commit('SET_TASK_PROGRESS', taskData.progress)
        commit('SET_CURRENT_TASK', taskData.currentTask)
        commit('SET_REMAINING_TIME', taskData.remainingTime)
        commit('SET_TASK_STATS', {
          completed: taskData.completedTasks,
          total: taskData.totalTasks
        })

        // 获取报警数据
        const alarms = await droneApi.getAlarms()
        commit('SET_ALARMS', alarms)

        // 获取无人机状态
        const droneStatus = await droneApi.getDroneStatus()
        commit('SET_DRONE_STATUS', droneStatus.status)
        commit('SET_BATTERY_LEVEL', droneStatus.batteryLevel)
        commit('SET_CURRENT_ALTITUDE', droneStatus.altitude)
        commit('SET_CURRENT_SPEED', droneStatus.speed)

        // 设置视频流
        commit('SET_VIDEO_STREAM', droneStatus.videoStreamUrl)
        commit('SET_IS_STREAMING', droneStatus.isStreaming)

      } catch (error) {
        commit('SET_ERROR', error.message)
        console.error('初始化系统失败:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    },

    // 选择航线
    selectRoute({ commit }, route) {
      commit('SET_SELECTED_ROUTE', route)
    },

    // 处理报警
    processAlarm({ commit }, alarmId) {
      commit('REMOVE_ALARM', alarmId)
      // 这里可以调用API将报警标记为已处理
      droneApi.processAlarm(alarmId)
    },

    // 无人机控制
    controlDrone({ commit }, action) {
      commit('SET_DRONE_STATUS', {
        'start': '飞行中',
        'stop': '待命',
        'pause': '暂停',
        'return': '返回中'
      }[action])

      // 调用API执行控制动作
      droneApi.controlDrone(action)
    },

    // 更新目标高度
    updateTargetAltitude({ commit }, altitude) {
      commit('SET_TARGET_ALTITUDE', altitude)
      // 调用API更新高度
      droneApi.updateAltitude(altitude)
    },

    // 更新目标速度
    updateTargetSpeed({ commit }, speed) {
      commit('SET_TARGET_SPEED', speed)
      // 调用API更新速度
      droneApi.updateSpeed(speed)
    },

    // 紧急停止
    emergencyStop({ commit }) {
      commit('SET_DRONE_STATUS', '已停止')
      commit('SET_CURRENT_SPEED', 0)
      // 调用API执行紧急停止
      droneApi.emergencyStop()
    },

    // 切换暗黑模式
    toggleDarkMode({ commit, state }) {
      commit('SET_DARK_MODE', !state.darkMode)
    },

    // 刷新视频流
    refreshStream({ commit }) {
      const timestamp = Date.now()
      commit('SET_VIDEO_STREAM', `https://picsum.photos/1280/720?random=${timestamp}`)
    },

    // 用户认证相关action
    async login({ commit }, credentials) {
      try {
        // 调用后端API进行登录
        const response = await authApi.login(credentials)

        // 保存用户信息和token
        commit('SET_USER', {
          id: response.user.id,
          username: response.user.username,
          name: response.user.name,
          role: response.user.role
        })
        commit('SET_TOKEN', response.token)

        return { user: response.user, token: response.token }
      } catch (error) {
        console.error('登录失败:', error)
        throw new Error(error.message || '用户名或密码错误')
      }
    },

    logout({ commit }) {
      // 调用后端API进行注销
      authApi.logout().catch(error => {
        console.error('注销失败:', error)
      })
      commit('LOGOUT')
    },

    // 用户管理相关action
    async addUser({ commit }, userData) {
      try {
        // 调用后端API添加用户
        const newUser = await authApi.register(userData)
        commit('ADD_USER', newUser)
        return newUser
      } catch (error) {
        console.error('添加用户失败:', error)
        throw new Error(error.message || '添加用户失败')
      }
    },

    async updateUser({ commit }, { id, ...updates }) {
      try {
        // 调用后端API更新用户
        const updatedUser = await authApi.updateUser(id, updates)
        commit('UPDATE_USER', updatedUser)
        return updatedUser
      } catch (error) {
        console.error('更新用户失败:', error)
        throw new Error(error.message || '更新用户失败')
      }
    },

    async deleteUser({ commit }, userId) {
      try {
        // 调用后端API删除用户
        await authApi.deleteUser(userId)
        commit('DELETE_USER', userId)
      } catch (error) {
        console.error('删除用户失败:', error)
        throw new Error(error.message || '删除用户失败')
      }
    },

    // 获取所有用户
    async fetchUsers({ commit, state }, params = {}) {
      try {
        const { page = state.currentPage, page_size = state.pageSize, search = '' } = params
        const response = await authApi.getUsers({ page, page_size, search })

        // 处理Django REST Framework的分页响应格式
        if (response.results) {
          commit('SET_USERS', response.results)
          commit('SET_PAGINATION_INFO', {
            currentPage: page,
            pageSize: page_size,
            totalUsers: response.count
          })
        } else {
          // 兼容非分页响应
          commit('SET_USERS', response)
        }

        return response
      } catch (error) {
        console.error('获取用户列表失败:', error)
        throw new Error(error.message || '获取用户列表失败')
      }
    }
  },

  getters: {
    // 获取进行中的任务
    activeTasks: (state) => {
      return state.droneRoutes.filter(route => route.status === 'in_progress')
    },

    // 获取高优先级报警
    highPriorityAlarms: (state) => {
      return state.alarms.filter(alarm => alarm.severity === '高')
    },

    // 获取电池状态类名
    batteryStatusClass: (state) => {
      if (state.batteryLevel > 70) return 'bg-green-500'
      if (state.batteryLevel > 30) return 'bg-yellow-500'
      return 'bg-red-500'
    },

    // 用户相关getter
    currentUser: (state) => {
      return state.user
    },

    isAdmin: (state) => {
      return state.user && state.user.role === 'admin'
    },

    allUsers: (state) => {
      return state.users
    }
  }
})