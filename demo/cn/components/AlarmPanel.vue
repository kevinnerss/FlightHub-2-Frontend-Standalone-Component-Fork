<template>
  <div class="alarm-panel p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md h-full flex flex-col">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">报警信息</h3>
      <span class="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100">
        {{ alarms.length }}个报警
      </span>
    </div>
    
    <div class="overflow-y-auto flex-grow">
      <div 
        v-for="alarm in alarms" 
        :key="alarm.id"
        class="alarm-item mb-4 p-3 rounded-md border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700"
      >
        <div class="flex items-start justify-between">
          <h4 class="font-medium text-gray-900 dark:text-white">{{ alarm.title }}</h4>
          <span class="alarm-dot"></span>
        </div>
        <p class="text-sm text-gray-600 dark:text-gray-300 mt-1">{{ alarm.description }}</p>
        <div class="mt-2 flex justify-between items-center text-xs text-gray-500 dark:text-gray-400">
          <span>{{ formatTime(alarm.timestamp) }}</span>
          <span>{{ alarm.location }}</span>
        </div>
        <div class="mt-3 relative">
          <img 
            :src="alarm.imageUrl" 
            :alt="alarm.title"
            class="w-full h-32 object-cover rounded cursor-pointer hover:opacity-90 transition-opacity"
            @click="viewAlarmDetails(alarm)"
          >
        </div>
        <button 
          class="mt-2 w-full py-1 text-xs text-blue-600 dark:text-blue-400 hover:underline"
          @click="markAsProcessed(alarm.id)"
        >
          标记为已处理
        </button>
      </div>
    </div>
    
    <!-- 报警详情模态框 -->
    <div v-if="showDetails" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-lg w-full max-h-[90vh] overflow-auto">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">{{ selectedAlarm?.title }}</h3>
          <button @click="showDetails = false" class="absolute top-4 right-4 text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="p-4">
          <img 
            :src="selectedAlarm?.imageUrl" 
            :alt="selectedAlarm?.title"
            class="w-full h-auto rounded mb-4"
          >
          <p class="text-gray-700 dark:text-gray-300 mb-4">{{ selectedAlarm?.description }}</p>
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p class="text-gray-500 dark:text-gray-400">时间</p>
              <p class="font-medium text-gray-900 dark:text-white">{{ formatTime(selectedAlarm?.timestamp) }}</p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">位置</p>
              <p class="font-medium text-gray-900 dark:text-white">{{ selectedAlarm?.location }}</p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">类型</p>
              <p class="font-medium text-gray-900 dark:text-white">{{ selectedAlarm?.type }}</p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">严重程度</p>
              <p class="font-medium" :class="severityClass(selectedAlarm?.severity)">{{ selectedAlarm?.severity }}</p>
            </div>
          </div>
        </div>
        <div class="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
          <button 
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mr-2"
            @click="markAsProcessed(selectedAlarm?.id)"
          >
            标记为已处理
          </button>
          <button 
            class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white rounded hover:bg-gray-300 dark:hover:bg-gray-600"
            @click="showDetails = false"
          >
            关闭
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
  emits: ['alarm-processed'],
  data() {
    return {
      showDetails: false,
      selectedAlarm: null
    }
  },
  methods: {
    formatTime(timestamp) {
      if (!timestamp) return '';
      const date = new Date(timestamp);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    },
    viewAlarmDetails(alarm) {
      this.selectedAlarm = alarm;
      this.showDetails = true;
    },
    markAsProcessed(alarmId) {
      this.$emit('alarm-processed', alarmId);
      if (this.showDetails) {
        this.showDetails = false;
      }
    },
    severityClass(severity) {
      switch(severity) {
        case '高':
          return 'text-red-600 dark:text-red-400';
        case '中':
          return 'text-yellow-600 dark:text-yellow-400';
        case '低':
          return 'text-blue-600 dark:text-blue-400';
        default:
          return 'text-gray-600 dark:text-gray-400';
      }
    }
  }
}
</script>

<style scoped>
.alarm-panel {
  max-height: 100%;
}

.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f7fafc;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

.alarm-dot {
  width: 8px;
  height: 8px;
  background-color: #ef4444;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
</style>