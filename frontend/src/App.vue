<template>
  <div class="h-screen bg-gray-900 text-gray-300 transition-colors duration-300 flex flex-col">
    <!-- 导航栏 - 科技感风格 -->
    <el-menu 
      mode="horizontal" 
      router 
      class="bg-[#111827] border-b border-[#374151] text-[#93c5fd] flex-shrink-0"
      :style="{
        boxShadow: '0 0 15px rgba(59, 130, 246, 0.1)',
        background: 'linear-gradient(90deg, #111827, #1e293b)'
      }"
    >
      <el-menu-item 
        index="/" 
        class="tech-nav-item"
        :style="{
          fontSize: '16px',
          fontWeight: '500',
          transition: 'all 0.3s ease',
          position: 'relative',
          overflow: 'hidden',
          color: '#93c5fd'
        }"
      >
        主控台
      </el-menu-item>
      
      <el-menu-item 
        index="/alarm-management" 
        class="tech-nav-item"
        :style="{
          fontSize: '16px',
          fontWeight: '500',
          transition: 'all 0.3s ease',
          position: 'relative',
          overflow: 'hidden',
          color: '#93c5fd'
        }"
      >
        告警管理
      </el-menu-item>
    </el-menu>
    
    <!-- 路由视图容器 -->
    <div class="flex-grow overflow-hidden">
      <router-view class="h-full" />
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  created() {
    console.log('App 组件已创建')
    // 检查系统主题偏好
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    const isDarkMode = localStorage.getItem('darkMode') === 'true' || (!localStorage.getItem('darkMode') && prefersDark)
    
    // 设置暗黑模式
    if (isDarkMode) {
      document.documentElement.classList.add('dark')
    }
  },
  mounted() {
    console.log('App 组件已挂载')
  }
}
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #0b0f19;
  color: #e5e7eb;
  line-height: 1.6;
}

/* 科技感导航样式 */
:deep(.tech-nav-item) {
  position: relative;
  overflow: hidden;
}

:deep(.tech-nav-item:hover) {
    background-color: rgba(59, 130, 246, 0.15) !important;
    color: #bfdbfe !important;
  }
  
  :deep(.tech-nav-item.is-active) {
    background-color: rgba(59, 130, 246, 0.2) !important;
    color: #bfdbfe !important;
  }

:deep(.tech-nav-item.is-active::after) {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.5);
}

/* Element Plus 导航栏样式覆盖 */
:deep(.el-menu) {
  background-color: transparent !important;
}

:deep(.el-menu-item) {
    color: #93c5fd !important;
    padding: 0 20px !important;
    height: 60px !important;
    line-height: 60px !important;
  }

/* 添加科技感网格背景 */
.h-screen {
  background-image: 
    linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  background-position: center center;
}

#app {
  width: 100%;
  min-height: 100vh;
  background-color: #0b0f19;
  background-image: 
    radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
    linear-gradient(to bottom, rgba(17, 24, 39, 0.9), rgba(11, 15, 25, 0.9)),
    url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiMxNTE5MjkiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRjMC0yLjIxLTEuNzktNC00LTRzLTQgMS43OS00IDQgMS43OSA0IDQgNCA0LTEuNzkgNC00em0wLTE2YzAtMi4yMS0xLjc5LTQtNC00cy00IDEuNzktNCA0IDEuNzkgNCA0IDQgNC0xLjc5IDQtNHoiLz48cGF0aCBkPSJNMjAgMjBjMC0yLjIxLTEuNzktNC00LTRzLTQgMS43OS00IDQgMS43OSA0IDQgNCA0LTEuNzkgNC00em0xNiAxNmMwLTIuMjEtMS43OS00LTQtNHMtNCAxLjc5LTQgNCAxLjc5IDQgNCA0IDQtMS43OSA0LTR6Ii8+PC9nPjwvZz48L3N2Zz4=');
  background-attachment: fixed;
  background-position: center;
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1f2937;
}

::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #4b5563;
}

/* 全局过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 防止内容溢出 */
.overflow-hidden {
  overflow: hidden;
}

/* 内容居中 */
.content-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 响应式边距 */
@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }
}

/* 全局Element Plus样式覆盖 */
/* 下拉选择框样式 */
.el-select {
  --el-input-bg-color: #1f2937 !important;
  --el-input-border-color: #374151 !important;
  --el-input-text-color: #d1d5db !important;
  --el-input-hover-border-color: #3b82f6 !important;
  --el-input-focus-border-color: #3b82f6 !important;
}

.el-input__wrapper {
  background-color: #1f2937 !important;
  border: 1px solid #374151 !important;
  box-shadow: none !important;
}

.el-input__inner {
  background-color: #1f2937 !important;
  border: none !important;
  color: #d1d5db !important;
}

.el-input__suffix-inner .el-input__icon {
  color: #9ca3af !important;
}

/* 下拉菜单样式 */
.el-select-dropdown {
  background-color: #1f2937 !important;
  border: 1px solid #374151 !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
}

.el-select-dropdown__item {
  color: #d1d5db !important;
}

.el-select-dropdown__item:hover {
  background-color: #374151 !important;
  color: #93c5fd !important;
}

.el-select-dropdown__item.selected {
  background-color: #1e3a8a !important;
  color: #93c5fd !important;
}

/* 确保搜索筛选区域的样式优先级 */
.search-filters .el-select {
  background-color: #1f2937 !important;
}

.search-filters .el-input__wrapper {
  background-color: #1f2937 !important;
  border: 1px solid #374151 !important;
}

.search-filters .el-input__inner {
  background-color: #1f2937 !important;
  color: #d1d5db !important;
}
</style>