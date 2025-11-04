import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 导入专门的Element Plus样式覆盖文件，确保在官方样式之后导入以实现覆盖
import './assets/element-overrides.css'
import './assets/tailwind.css'
import 'font-awesome/css/font-awesome.min.css'

// 导入Element Plus图标（确保图标可用）
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 处理ResizeObserver循环错误
if (typeof window !== 'undefined') {
  window.ResizeObserver = new Proxy(window.ResizeObserver || {}, {
    construct: (target, args) => {
      const callback = args[0]
      return new target((entries, observer) => {
        window.requestAnimationFrame(() => {
          callback(entries, observer)
        })
      }, args[1])
    }
  })
}

console.log('开始创建 Vue 应用')

const app = createApp(App)

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 为筛选框添加最高优先级的内联样式
const addFilterStyles = () => {
  // 使用setTimeout确保DOM加载完成后再添加样式
  setTimeout(() => {
    // 查找并应用样式到所有筛选框
    const selectWrappers = document.querySelectorAll('.search-filters .el-select .el-input__wrapper')
    selectWrappers.forEach(wrapper => {
      wrapper.style.backgroundColor = '#1f2937'
      wrapper.style.borderColor = '#374151'
      wrapper.style.boxShadow = 'none'
    })

    const inputInners = document.querySelectorAll('.search-filters .el-select .el-input__inner')
    inputInners.forEach(input => {
      input.style.backgroundColor = '#1f2937'
      input.style.color = '#d1d5db'
    })

    const icons = document.querySelectorAll('.search-filters .el-select .el-input__suffix-inner .el-input__icon')
    icons.forEach(icon => {
      icon.style.color = '#9ca3af'
    })

    // 特别处理已在DOM中的筛选框
    const statusSelect = document.getElementById('alarm-status-select')
    if (statusSelect) {
      const statusWrapper = statusSelect.querySelector('.el-input__wrapper')
      const statusInput = statusSelect.querySelector('.el-input__inner')
      const statusIcon = statusSelect.querySelector('.el-input__suffix-inner .el-input__icon')
      
      if (statusWrapper) statusWrapper.style.backgroundColor = '#1f2937'
      if (statusInput) statusInput.style.backgroundColor = '#1f2937'
      if (statusIcon) statusIcon.style.color = '#9ca3af'
    }

    const waylineSelect = document.getElementById('alarm-wayline-select')
    if (waylineSelect) {
      const waylineWrapper = waylineSelect.querySelector('.el-input__wrapper')
      const waylineInput = waylineSelect.querySelector('.el-input__inner')
      const waylineIcon = waylineSelect.querySelector('.el-input__suffix-inner .el-input__icon')
      
      if (waylineWrapper) waylineWrapper.style.backgroundColor = '#1f2937'
      if (waylineInput) waylineInput.style.backgroundColor = '#1f2937'
      if (waylineIcon) waylineIcon.style.color = '#9ca3af'
    }
  }, 0)
}

console.log('Vue 应用创建完成')

// 使用插件 - 通过Element Plus配置选项修改主题
app.use(ElementPlus, {
  size: 'default',
  zIndex: 3000,
  // 通过配置修改全局样式
  cssVars: {
    // 全局颜色变量
    'el-color-primary': '#3b82f6',
    'el-color-success': '#10b981',
    'el-color-warning': '#f59e0b',
    'el-color-danger': '#ef4444',
    'el-color-info': '#64748b',
    // 输入框样式
    'el-input-bg-color': '#1f2937',
    'el-input-text-color': '#d1d5db',
    'el-input-border-color': '#374151',
    // 下拉选择框样式
    'el-select-dropdown-bg-color': '#1f2937',
    'el-select-dropdown-border-color': '#374151',
    'el-select-dropdown-item-color': '#d1d5db',
    'el-select-dropdown-item-hover-bg-color': '#374151',
    'el-select-dropdown-item-selected-bg-color': '#1e3a8a'
  }
})

app.use(router)
app.use(store)

console.log('插件安装完成')

// 挂载应用
app.mount('#app')

// 应用样式
addFilterStyles()

// 监听DOM变化，确保动态添加的元素也能应用样式
const observer = new MutationObserver(() => {
  addFilterStyles()
})

observer.observe(document.body, {
  childList: true,
  subtree: true
})

console.log('Vue 应用挂载完成')