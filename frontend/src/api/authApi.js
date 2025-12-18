// 直接把默认值也改成相对路径，这样就算环境变量失效，它也会乖乖走 Nginx
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8001/api/v1'
//const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || '/api/v1'

// 创建axios实例
const createRequest = async (url, options = {}) => {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  }

  // 如果有token，添加到请求头
  const token = localStorage.getItem('token')
  if (token) {
    headers['Authorization'] = `Token ${token}`
  }

  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || '请求失败')
    }

    return data
  } catch (error) {
    console.error('API请求错误:', error)
    throw error
  }
}

const authApi = {
  // 用户登录
  login: async (credentials) => {
    const response = await createRequest('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(credentials)
    })
    // 转换响应格式，使后端返回的key字段变为token
    return {
      token: response.key,
      user: response.user
    }
  },

  // 用户注册
  register: async (userData) => {
    return createRequest('/users/', {
      method: 'POST',
      body: JSON.stringify(userData)
    })
  },

  // 获取当前用户信息
  getCurrentUser: async () => {
    return createRequest('/users/me/')
  },

  // 用户注销
  logout: async () => {
    return createRequest('/auth/logout/', {
      method: 'POST'
    })
  },

  // 获取所有用户（管理员权限）
  getUsers: async (params = {}) => {
    const { page = 1, page_size = 10, search = '' } = params
    const queryParams = new URLSearchParams()
    queryParams.append('page', page)
    queryParams.append('page_size', page_size)
    if (search) {
      queryParams.append('search', search)
    }
    return createRequest(`/users/?${queryParams.toString()}`)
  },

  // 更新用户信息
  updateUser: async (userId, userData) => {
    return createRequest(`/users/${userId}/`, {
      method: 'PATCH',
      body: JSON.stringify(userData)
    })
  },

  // 删除用户
  deleteUser: async (userId) => {
    return createRequest(`/users/${userId}/`, {
      method: 'DELETE'
    })
  }
}

export default authApi