import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/tailwind.css'
import 'font-awesome/css/font-awesome.min.css'

console.log('开始创建 Vue 应用')

const app = createApp(App)

console.log('Vue 应用创建完成')

// 使用插件
app.use(router)
app.use(store)
app.use(ElementPlus)

console.log('插件安装完成')

// 挂载应用
app.mount('#app')

console.log('Vue 应用挂载完成')