import { createRouter, createWebHistory } from 'vue-router'

// 懒加载路由组件
const DjiDashboard = () => import('../views/DjiDashboard.vue')
const DigitalTwin = () => import('../views/DigitalTwin.vue')
const AlarmManagement = () => import('../views/AlarmManagement.vue')

const routes = [
  {
    path: '/',
    name: 'DjiDashboard',
    component: DjiDashboard,
    meta: {
      title: '主控台'
    }
  },
  {
    path: '/digital-twin',
    name: 'DigitalTwin',
    component: DigitalTwin,
    meta: {
      title: '数字孪生'
    }
  },
  {
    path: '/alarm-management',
    name: 'AlarmManagement',
    component: AlarmManagement,
    meta: {
      title: '告警管理'
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