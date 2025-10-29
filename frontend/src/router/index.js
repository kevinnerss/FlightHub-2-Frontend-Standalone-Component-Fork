import { createRouter, createWebHistory } from 'vue-router'

// 懒加载路由组件
const DjiDashboard = () => import('../views/DjiDashboard.vue')
const ApiTest = () => import('../views/ApiTest.vue')
const DigitalTwin = () => import('../views/DigitalTwin.vue')
const TestLayout = () => import('../views/TestLayout.vue')
const CesiumTest = () => import('../views/CesiumTest.vue')
const PureCesiumTest = () => import('../views/PureCesiumTest.vue')

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
  },
  {
    path: '/digital-twin',
    name: 'DigitalTwin',
    component: DigitalTwin,
    meta: {
      title: '数字孪生系统'
    }
  },
  {
    path: '/test-layout',
    name: 'TestLayout',
    component: TestLayout,
    meta: {
      title: '布局测试'
    }
  },
  {
    path: '/cesium-test',
    name: 'CesiumTest',
    component: CesiumTest,
    meta: {
      title: 'Cesium测试'
    }
  },
  {
    path: '/pure-cesium-test',
    name: 'PureCesiumTest',
    component: PureCesiumTest,
    meta: {
      title: '纯Cesium测试'
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