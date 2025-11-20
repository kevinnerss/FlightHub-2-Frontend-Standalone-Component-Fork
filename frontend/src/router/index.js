import { createRouter, createWebHistory } from 'vue-router'

// 懒加载路由组件
const Login = () => import('../views/Login.vue')
const UserManagement = () => import('../views/UserManagement.vue')
const DjiDashboard = () => import('../views/DjiDashboard.vue')

const AlarmManagement = () => import('../views/AlarmManagement.vue')



const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  
  {
    path: '/user-management',
    name: 'UserManagement',
    component: UserManagement,
    meta: {
      title: '人员管理',
      requiresAuth: true,
      requiresAdmin: true
    }
  },

  {
    path: '/',
    name: 'DjiDashboard',
    component: DjiDashboard,
    meta: {
      title: '主控台',
      requiresAuth: true
    }
  },

  {
    path: '/alarm-management',
    name: 'AlarmManagement',
    component: AlarmManagement,
    meta: {
      title: '告警管理',
      requiresAuth: true
    }
  },


  
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 全局前置守卫 - 实现认证和授权控制
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || '无人机巡检数字孪生系统'
  
  // 获取认证状态
  const isAuthenticated = localStorage.getItem('token') !== null
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !isAuthenticated) {
    // 未认证且需要认证，跳转到登录页
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }
  
  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin) {
    // 从localStorage获取用户角色信息
    const userStr = localStorage.getItem('userInfo')
    let isAdmin = false
    
    if (userStr) {
      try {
        const userInfo = JSON.parse(userStr)
        isAdmin = userInfo.role === 'admin'
      } catch (e) {
        console.error('解析用户信息失败:', e)
      }
    }
    
    if (!isAdmin) {
      // 没有管理员权限，跳转到首页
      return next({ name: 'DjiDashboard' })
    }
  }
  
  // 已认证用户访问登录页时，重定向到首页
  if (to.name === 'Login' && isAuthenticated) {
    return next({ name: 'DjiDashboard' })
  }
  
  next()
})

export default router