<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden h-full flex flex-col">
    <!-- 标题栏 -->
    <div class="p-4 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 flex justify-between items-center">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
        <i class="fa fa-cubes text-blue-500 mr-2"></i>
        3D可视化
        <span v-if="selectedRoute" class="ml-2 text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
          {{ selectedRoute.name }}
        </span>
      </h3>
      
      <!-- 视图控制 -->
      <div class="flex items-center space-x-3">
        <!-- 视图模式切换 -->
        <div class="flex rounded-md shadow-sm">
          <button 
            class="inline-flex items-center px-3 py-1 text-sm font-medium border border-gray-300 dark:border-gray-600 rounded-l-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            @click="changeViewMode('top')"
            :class="{ 'bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300 border-blue-300 dark:border-blue-500': viewMode === 'top' }"
          >
            <i class="fa fa-arrow-down mr-1"></i>顶视图
          </button>
          <button 
            class="inline-flex items-center px-3 py-1 text-sm font-medium border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            @click="changeViewMode('side')"
            :class="{ 'bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300 border-blue-300 dark:border-blue-500': viewMode === 'side' }"
          >
            <i class="fa fa-arrow-right mr-1"></i>侧视图
          </button>
          <button 
            class="inline-flex items-center px-3 py-1 text-sm font-medium border border-gray-300 dark:border-gray-600 rounded-r-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            @click="changeViewMode('3d')"
            :class="{ 'bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300 border-blue-300 dark:border-blue-500': viewMode === '3d' }"
          >
            <i class="fa fa-cube mr-1"></i>3D视图
          </button>
        </div>
        
        <!-- 图层控制 -->
        <button class="p-1 text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400" @click="toggleLayersPanel">
          <i class="fa fa-layers"></i>
        </button>
        
        <!-- 缩放控制 -->
        <div class="flex flex-col bg-gray-200 dark:bg-gray-700 rounded">
          <button class="p-1 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-t">
            <i class="fa fa-search-plus"></i>
          </button>
          <button class="p-1 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-b">
            <i class="fa fa-search-minus"></i>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 3D 可视化区域 -->
    <div class="flex-grow relative bg-gray-900">
      <!-- 模拟3D场景 -->
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="text-center">
          <i class="fa fa-cube text-gray-700 text-6xl mb-4"></i>
          <p class="text-gray-500">3D场景加载中...</p>
          <p class="text-xs text-gray-600 mt-1">选择航线以显示3D模型</p>
        </div>
      </div>
      
      <!-- 报警标记点 -->
      <div v-for="alarm in alarmPoints" :key="alarm.id" class="absolute" style="left: 30%; top: 40%;">
        <div class="relative">
          <div 
            class="w-4 h-4 rounded-full cursor-pointer animate-pulse"
            :class="{
              'bg-red-500': alarm.severity === '高',
              'bg-yellow-500': alarm.severity === '中',
              'bg-blue-500': alarm.severity === '低'
            }"
            @click="showAlarmDetail(alarm)"
            title="{{ alarm.title }}"
          ></div>
          <div 
            class="absolute -inset-4 rounded-full"
            :class="{
              'bg-red-500/20': alarm.severity === '高',
              'bg-yellow-500/20': alarm.severity === '中',
              'bg-blue-500/20': alarm.severity === '低'
            }"
            animate-ping
          ></div>
        </div>
      </div>
    </div>
    
    <!-- 底部信息栏 -->
    <div class="p-3 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600 flex justify-between items-center">
      <div class="text-sm text-gray-600 dark:text-gray-400">
        <span>比例: 1:1000</span>
        <span class="mx-2">|</span>
        <span>高程: 50m</span>
      </div>
      <div class="text-sm text-gray-600 dark:text-gray-400">
        <span>坐标: (23.124, 113.235)</span>
      </div>
    </div>
    
    <!-- 图层控制面板 (隐藏状态) -->
    <div v-if="showLayers" class="absolute top-20 right-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-600 p-3 w-64">
      <h4 class="text-sm font-semibold mb-2 text-gray-900 dark:text-white">图层控制</h4>
      <div class="space-y-2 text-sm">
        <label class="flex items-center">
          <input type="checkbox" class="rounded text-blue-600" checked>
          <span class="ml-2 text-gray-700 dark:text-gray-300">地形</span>
        </label>
        <label class="flex items-center">
          <input type="checkbox" class="rounded text-blue-600" checked>
          <span class="ml-2 text-gray-700 dark:text-gray-300">建筑</span>
        </label>
        <label class="flex items-center">
          <input type="checkbox" class="rounded text-blue-600" checked>
          <span class="ml-2 text-gray-700 dark:text-gray-300">电力设施</span>
        </label>
        <label class="flex items-center">
          <input type="checkbox" class="rounded text-blue-600" checked>
          <span class="ml-2 text-gray-700 dark:text-gray-300">航线</span>
        </label>
        <label class="flex items-center">
          <input type="checkbox" class="rounded text-blue-600" checked>
          <span class="ml-2 text-gray-700 dark:text-gray-300">报警点</span>
        </label>
        <label class="flex items-center">
          <input type="checkbox" class="rounded text-blue-600">
          <span class="ml-2 text-gray-700 dark:text-gray-300">标注</span>
        </label>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VisualizationPanel',
  props: {
    selectedRoute: {
      type: Object,
      default: null
    },
    alarmPoints: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      viewMode: '3d',
      showLayers: false
    }
  },
  methods: {
    // 更改视图模式
    changeViewMode(mode) {
      this.viewMode = mode
      this.$emit('view-mode-changed', mode)
    },
    
    // 切换图层面板
    toggleLayersPanel() {
      this.showLayers = !this.showLayers
    },
    
    // 显示报警详情
    showAlarmDetail(alarm) {
      console.log('显示报警详情:', alarm)
      // 这里可以实现点击报警点显示详细信息的功能
    }
  }
}
</script>

<style scoped>
/* 动画效果 */
@keyframes ping {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

.animate-ping {
  animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 图层面板淡入淡出 */
.absolute {
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>