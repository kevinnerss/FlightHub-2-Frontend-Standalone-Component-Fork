import { createRouter, createWebHistory } from 'vue-router'

// 懒加载路由组件
const DjiDashboard = () => import('../views/DjiDashboard.vue')
const ApiTest = () => import('../views/ApiTest.vue')

const routes = [
  {
    path: '/',
    name: 'DjiDashboard',
    component: DjiDashboard,
    meta: {
      title: '无人机巡检数字孪生系统'
    }
  },
  {
    path: '/api-test',
    name: 'ApiTest',
    component: ApiTest,
    meta: {
      title: 'API连通性测试'
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