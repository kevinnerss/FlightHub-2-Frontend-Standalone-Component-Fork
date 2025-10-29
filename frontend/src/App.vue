<template>
  <div class="h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-300 flex flex-col">
    <!-- 导航栏 -->
    <el-menu mode="horizontal" router class="flex-shrink-0">
      <el-menu-item index="/">主控台</el-menu-item>
      <el-menu-item index="/api-test">API测试</el-menu-item>
      <el-menu-item index="/digital-twin">数字孪生</el-menu-item>
      <el-menu-item index="/test-layout">布局测试</el-menu-item>
      <el-menu-item index="/cesium-test">Cesium测试</el-menu-item>
      <el-menu-item index="/pure-cesium-test">纯Cesium测试</el-menu-item>
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

html, body {
  font-family: 'Inter', 'system-ui', 'sans-serif';
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100%;
  overflow: hidden;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.dark ::-webkit-scrollbar-track {
  background: #1f2937;
}

.dark ::-webkit-scrollbar-thumb {
  background: #4b5563;
}

.dark ::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}
</style>