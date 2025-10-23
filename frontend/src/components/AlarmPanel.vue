<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden h-full flex flex-col">
    <!-- 标题栏 -->
    <div class="p-4 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 flex justify-between items-center">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
        <i class="fa fa-bell text-red-500 mr-2"></i>
        报警信息
        <span v-if="alarms.length > 0" class="ml-2 text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300">
          {{ alarms.length }}
        </span>
      </h3>
      <button class="text-xs text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400">
        <i class="fa fa-refresh mr-1"></i>刷新
      </button>
    </div>
    
    <!-- 报警列表 -->
    <div class="flex-grow overflow-y-auto p-2">
      <div v-if="alarms.length === 0" class="text-center py-10 text-gray-500 dark:text-gray-400">
        <i class="fa fa-check-circle text-green-500 text-4xl mb-2"></i>
        <p>暂无报警信息</p>
      </div>
      
      <div 
        v-for="alarm in alarms" 
        :key="alarm.id"
        class="mb-3 p-3 rounded-md border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 hover:shadow-md transition-all duration-200"
      >
        <!-- 报警头部 -->
        <div class="flex justify-between items-start">
          <div>
            <div class="flex items-center">
              <h4 class="font-medium text-gray-900 dark:text-white">{{ alarm.title }}</h4>
              <span 
                class="ml-2 text-xs px-2 py-0.5 rounded-full"
                :class="{
                  'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300': alarm.severity === '高',
                  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300': alarm.severity === '中',
                  'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300': alarm.severity === '低'
                }"
              >
                {{ alarm.severity }}级
              </span>
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {{ formatDateTime(alarm.timestamp) }} · {{ alarm.location }}
            </p>
          </div>
          <button 
            class="text-gray-400 hover:text-red-500 dark:text-gray-500 dark:hover:text-red-400 transition-colors"
            @click="$emit('alarm-processed', alarm.id)"
            title="标记为已处理"
          >
            <i class="fa fa-times"></i>
          </button>
        </div>
        
        <!-- 报警描述 -->
        <p class="text-sm text-gray-600 dark:text-gray-300 mt-2 line-clamp-2">{{ alarm.description }}</p>
        
        <!-- 报警图片 -->
        <div v-if="alarm.imageUrl" class="mt-3 rounded-md overflow-hidden">
          <img 
            :src="alarm.imageUrl" 
            alt="报警图片" 
            class="w-full h-32 object-cover hover:opacity-90 transition-opacity"
            @click="showImageDetail(alarm.imageUrl)"
          >
        </div>
        
        <!-- 操作按钮 -->
        <div class="mt-3 flex justify-between">
          <span class="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
            {{ alarm.type }}
          </span>
          <button class="text-sm text-blue-600 dark:text-blue-400 hover:underline flex items-center">
            查看详情
            <i class="fa fa-angle-right ml-1"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AlarmPanel',
  props: {
    alarms: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    // 格式化日期时间
    formatDateTime(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    
    // 显示图片详情
    showImageDetail(imageUrl) {
      // 这里可以实现图片放大查看功能
      console.log('查看图片详情:', imageUrl)
      // 可以使用模态框或其他方式显示大图
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

/* 报警项动画 */
.mb-3 {
  animation: slideIn 0.3s ease-in-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 高优先级报警闪烁效果 */
.border-red-100 {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(220, 38, 38, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(220, 38, 38, 0);
  }
}
</style>