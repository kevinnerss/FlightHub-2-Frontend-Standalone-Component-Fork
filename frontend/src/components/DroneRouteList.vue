<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden h-full flex flex-col">
    <!-- 标题栏 -->
    <div class="p-4 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
        <i class="fa fa-road text-blue-500 mr-2"></i>
        航线列表
      </h3>
    </div>
    
    <!-- 航线列表 -->
    <div class="flex-grow overflow-y-auto p-2">
      <div 
        v-for="route in routes" 
        :key="route.id"
        class="mb-2 p-3 rounded-md border border-gray-200 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-400 cursor-pointer transition-all duration-200"
        :class="{ 
          'bg-blue-50 dark:bg-blue-900/20 border-blue-400 dark:border-blue-400': selectedRouteId === route.id,
          'opacity-70': route.status === 'completed',
          'opacity-90': route.status === 'pending'
        }"
        @click="$emit('route-selected', route.id)"
      >
        <div class="flex justify-between items-center">
          <h4 class="font-medium text-gray-900 dark:text-white">{{ route.name }}</h4>
          <span 
            class="text-xs px-2 py-1 rounded-full"
            :class="{
              'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300': route.status === 'completed',
              'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300': route.status === 'pending',
              'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300': route.status === 'in_progress'
            }"
          >
            {{ statusMap[route.status] }}
          </span>
        </div>
        
        <div class="mt-2 grid grid-cols-2 gap-2 text-xs text-gray-500 dark:text-gray-400">
          <div class="flex items-center">
            <i class="fa fa-map-marker mr-1 text-gray-400"></i>
            <span>{{ route.length }} km</span>
          </div>
          <div class="flex items-center">
            <i class="fa fa-clock-o mr-1 text-gray-400"></i>
            <span>{{ route.duration }} 分钟</span>
          </div>
          <div class="flex items-center">
            <i class="fa fa-flag mr-1 text-gray-400"></i>
            <span>{{ route.checkpoints }} 检查点</span>
          </div>
          <div class="flex items-center">
            <i class="fa fa-calendar mr-1 text-gray-400"></i>
            <span>{{ formatDate(route.lastFlight) }}</span>
          </div>
        </div>
        
        <!-- 进度指示器 -->
        <div v-if="route.status === 'in_progress'" class="mt-2">
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
            <div class="bg-blue-600 h-1.5 rounded-full" style="width: 65%"></div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部操作栏 -->
    <div class="p-3 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
      <button class="w-full flex items-center justify-center px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors">
        <i class="fa fa-plus mr-2"></i>
        新建航线
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DroneRouteList',
  props: {
    routes: {
      type: Array,
      required: true
    },
    selectedRouteId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      statusMap: {
        'completed': '已完成',
        'pending': '待执行',
        'in_progress': '进行中'
      }
    }
  },
  methods: {
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
/* 滚动条样式 */
.flex-grow::-webkit-scrollbar {
  width: 6px;
}

.flex-grow::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.flex-grow::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.flex-grow::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.dark .flex-grow::-webkit-scrollbar-track {
  background: #1f2937;
}

.dark .flex-grow::-webkit-scrollbar-thumb {
  background: #4b5563;
}

.dark .flex-grow::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}

/* 动画效果 */
.mb-2 {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>