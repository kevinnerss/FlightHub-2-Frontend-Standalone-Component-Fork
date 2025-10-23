import { createRouter, createWebHistory } from 'vue-router'

// 懒加载路由组件
const Dashboard = () => import('../views/Dashboard.vue')
const RoutePlanning = () => import('../views/RoutePlanning.vue')
const DataAnalysis = () => import('../views/DataAnalysis.vue')
const Settings = () => import('../views/Settings.vue')

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: '无人机巡检数字孪生系统'
    }
  },
  {
    path: '/route-planning',
    name: 'RoutePlanning',
    component: RoutePlanning,
    meta: {
      title: '航线规划'
    }
  },
  {
    path: '/data-analysis',
    name: 'DataAnalysis',
    component: DataAnalysis,
    meta: {
      title: '数据分析'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: {
      title: '系统设置'
    }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 全局前置守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '无人机巡检数字孪生系统'
  next()
})

export default router