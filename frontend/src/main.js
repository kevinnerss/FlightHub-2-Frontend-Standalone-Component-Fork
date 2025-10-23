import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import './assets/tailwind.css'
import 'font-awesome/css/font-awesome.min.css'

const app = createApp(App)

// 使用插件
app.use(router)
app.use(store)

// 挂载应用
app.mount('#app')