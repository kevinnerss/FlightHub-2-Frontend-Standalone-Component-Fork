import { createRouter, createWebHistory } from 'vue-router'

// Lazy-loaded route components
const Login = () => import('../views/Login.vue')
const UserManagement = () => import('../views/UserManagement.vue')
const DjiDashboard = () => import('../views/DjiDashboard.vue')
const CommandCenter = () => import('../views/CommandCenter.vue')
const AlarmManagement = () => import('../views/AlarmManagement.vue')
const AlarmStats = () => import('../views/AlarmStats.vue')
const CarouselDetection = () => import('../views/CarouselDetection.vue')
const CreateFlightTask = () => import('../views/CreateFlightTask.vue')
const InspectTaskManagement = () => import('../views/InspectTaskManagement.vue')
const MainView = () => import("../views/MainView.vue");
const DockMonitor = () => import('../views/DockMonitor.vue')
//const MediaLibrary = () => import('../views/ceshi.vue')

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
    path: '/',
    name: 'DjiDashboard',
    component: DjiDashboard,
    meta: {
      title: '\u4e3b\u63a7\u53f0',
      requiresAuth: true
    }
  },

  {
    path: "/main-view",
    name: "MainView",
    component: MainView,
    meta: {
      title: "首页",
      requiresAuth: true,
    },
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
      title: 'AI检测',
      requiresAuth: true
    }
  },

  {
    path: '/create-flight-task',
    name: 'CreateFlightTask',
    component: CreateFlightTask,
    meta: {
      title: '创建飞行任务',
      requiresAuth: true
    }
  },

  {
    path: '/inspect-task-management',
    name: 'InspectTaskManagement',
    component: InspectTaskManagement,
    meta: {
      title: '巡检任务管理',
      requiresAuth: true
    }
  },
  
  {
    path: '/command-center',
    name: 'CommandCenter',
    component: CommandCenter,
    meta: {
      title: '智能主控台',
      requiresAuth: true
    }
  },

  {
    path: '/dock-monitor',
    name: 'DockMonitor',
    component: DockMonitor,
    meta: {
      title: '机场监控',
      requiresAuth: true
    }
  },

  // {
  //   path: '/media-library',
  //   name: 'MediaLibrary',
  //   component: MediaLibrary,
  //   meta: {
  //     title: '\u5a92\u4f53\u6587\u4ef6\u5e93',
  //     requiresAuth: true
  //   }
  // },
  
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
