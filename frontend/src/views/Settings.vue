<template>
  <div class="p-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">系统设置</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- 左侧导航 -->
        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <h3 class="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">设置项</h3>
          <nav class="space-y-1">
            <a 
              href="#" 
              class="block px-3 py-2 rounded-md text-base font-medium bg-blue-600 text-white"
            >
              系统偏好
            </a>
            <a 
              href="#" 
              class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
            >
              无人机配置
            </a>
            <a 
              href="#" 
              class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
            >
              报警规则
            </a>
            <a 
              href="#" 
              class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
            >
              用户管理
            </a>
          </nav>
        </div>
        
        <!-- 右侧设置内容 -->
        <div class="md:col-span-2 bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
          <h3 class="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">系统偏好</h3>
          
          <div class="space-y-6">
            <!-- 主题设置 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">主题设置</label>
              <div class="flex items-center space-x-4">
                <label class="inline-flex items-center">
                  <input type="radio" name="theme" value="light" class="text-blue-600">
                  <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">浅色模式</span>
                </label>
                <label class="inline-flex items-center">
                  <input type="radio" name="theme" value="dark" class="text-blue-600" :checked="darkMode">
                  <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">深色模式</span>
                </label>
                <label class="inline-flex items-center">
                  <input type="radio" name="theme" value="system" class="text-blue-600">
                  <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">跟随系统</span>
                </label>
              </div>
            </div>
            
            <!-- 语言设置 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">语言设置</label>
              <select class="mt-1 block w-full pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
                <option value="zh-CN">简体中文</option>
                <option value="en-US">English</option>
              </select>
            </div>
            
            <!-- 数据刷新间隔 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">数据刷新间隔</label>
              <div class="flex items-center space-x-2">
                <input 
                  type="range" 
                  min="1" 
                  max="60" 
                  value="5" 
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                >
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">5秒</span>
              </div>
            </div>
            
            <!-- 通知设置 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">通知设置</label>
              <div class="space-y-2">
                <label class="inline-flex items-center">
                  <input type="checkbox" class="rounded text-blue-600" checked>
                  <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">接收报警通知</span>
                </label>
                <label class="inline-flex items-center">
                  <input type="checkbox" class="rounded text-blue-600" checked>
                  <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">接收任务完成通知</span>
                </label>
                <label class="inline-flex items-center">
                  <input type="checkbox" class="rounded text-blue-600">
                  <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">接收系统更新通知</span>
                </label>
              </div>
            </div>
          </div>
          
          <div class="mt-8 flex justify-end space-x-3">
            <button class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
              取消
            </button>
            <button class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
              保存设置
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'Settings',
  computed: {
    ...mapState([
      'darkMode'
    ])
  },
  methods: {
    ...mapActions([
      'toggleDarkMode',
      'setDarkMode'
    ])
  }
}
</script>