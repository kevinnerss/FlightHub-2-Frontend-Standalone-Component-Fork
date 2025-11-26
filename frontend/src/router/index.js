import { createRouter, createWebHistory } from 'vue-router'

// Lazy-loaded route components
const Login = () => import('../views/Login.vue')
const UserManagement = () => import('../views/UserManagement.vue')
const DjiDashboard = () => import('../views/DjiDashboard.vue')
const AlarmManagement = () => import('../views/AlarmManagement.vue')
const AlarmStats = () => import('../views/AlarmStats.vue')
const ComponentConfig = () => import('../views/ComponentConfig.vue')
const CarouselDetection = () => import('../views/CarouselDetection.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: '\u767b\u5f55',
      requiresAuth: false
    }
  },
  
  {
    path: '/user-management',
    name: 'UserManagement',
    component: UserManagement,
    meta: {
      title: '\u4eba\u5458\u7ba1\u7406',
      requiresAuth: true,
      requiresAdmin: true
    }
  },

  {
    path: '/component-config',
    name: 'ComponentConfig',
    component: ComponentConfig,
    meta: {
      title: '\u7ec4\u4ef6\u53c2\u6570\u914d\u7f6e',
      requiresAuth: true,
      requiresAdmin: true
    }
  },

  {
    path: '/',
    name: 'DjiDashboard',
    component: DjiDashboard,
    meta: {
      title: '\u4e3b\u63a7\u53f0',
      requiresAuth: true
    }
  },

  {
    path: '/alarm-management',
    name: 'AlarmManagement',
    component: AlarmManagement,
    meta: {
      title: '\u544a\u8b66\u7ba1\u7406',
      requiresAuth: true
    }
  },

  {
    path: '/alarm-stats',
    name: 'AlarmStats',
    component: AlarmStats,
    meta: {
      title: '\u544a\u8b66\u7edf\u8ba1',
      requiresAuth: true
    }
  },

  {
    path: '/carousel-detection',
    name: 'CarouselDetection',
    component: CarouselDetection,
    meta: {
      title: '\u8f6e\u64ad\u68c0\u6d4b',
      requiresAuth: true
    }
  },
  
  // 404 page
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Global guard - authentication and authorization
router.beforeEach((to, from, next) => {
  // Set page title
  document.title = to.meta.title || '\u65e0\u4eba\u673a\u5de1\u68c0\u6570\u5b57\u5b6a\u751f\u7cfb\u7edf'
  
  // Authentication state
  const isAuthenticated = localStorage.getItem('token') !== null
  
  // Require authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }
  
  // Require admin role
  if (to.meta.requiresAdmin) {
    const userStr = localStorage.getItem('userInfo')
    let isAdmin = false
    
    if (userStr) {
      try {
        const userInfo = JSON.parse(userStr)
        isAdmin = userInfo.role === 'admin'
      } catch (e) {
        console.error('Failed to parse user info:', e)
      }
    }
    
    if (!isAdmin) {
      return next({ name: 'DjiDashboard' })
    }
  }
  
  // Redirect authenticated users away from login
  if (to.name === 'Login' && isAuthenticated) {
    return next({ name: 'DjiDashboard' })
  }
  
  next()
})

export default router
