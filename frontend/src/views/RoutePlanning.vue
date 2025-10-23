<template>
  <div class="p-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">航线规划</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- 航线列表 -->
        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <h3 class="text-lg font-semibold mb-3 text-gray-800 dark:text-gray-200">现有航线</h3>
          <div class="space-y-2 max-h-[60vh] overflow-y-auto">
            <div 
              v-for="route in droneRoutes" 
              :key="route.id"
              class="p-3 rounded-md border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
              :class="{ 'border-blue-500 bg-blue-50 dark:bg-blue-900/30': selectedRoute?.id === route.id }"
              @click="handleRouteSelect(route)"
            >
              <p class="font-medium text-gray-900 dark:text-white">{{ route.name }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ route.length }}km · {{ route.checkpoints }}个检查点</p>
            </div>
          </div>
          <button class="mt-4 w-full py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
            <i class="fa fa-plus mr-2"></i>创建新航线
          </button>
        </div>
        
        <!-- 地图和航线编辑 -->
        <div class="md:col-span-2 bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <h3 class="text-lg font-semibold mb-3 text-gray-800 dark:text-gray-200">航线编辑</h3>
          <div class="bg-gray-200 dark:bg-gray-800 rounded-md h-[60vh] flex items-center justify-center">
            <div class="text-center">
              <i class="fa fa-map-o text-4xl text-gray-400 mb-2"></i>
              <p class="text-gray-500 dark:text-gray-400">地图加载中...</p>
              <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">选择或创建航线以进行编辑</p>
            </div>
          </div>
          <div class="flex justify-end mt-4 space-x-2">
            <button class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600">
              撤销
            </button>
            <button class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600">
              保存
            </button>
            <button class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
              应用航线
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
  name: 'RoutePlanning',
  computed: {
    ...mapState([
      'droneRoutes',
      'selectedRoute'
    ])
  },
  methods: {
    ...mapActions([
      'selectRoute'
    ]),
    
    handleRouteSelect(route) {
      this.selectRoute(route)
    }
  }
}
</script>