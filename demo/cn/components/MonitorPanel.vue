<template>
  <div class="monitor-panel p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">实时监控</h3>
      <div class="flex space-x-2">
        <button 
          class="px-2 py-1 text-xs bg-blue-50 text-blue-600 rounded hover:bg-blue-100 dark:bg-blue-900 dark:text-blue-100 dark:hover:bg-blue-800"
          @click="toggleFullScreen"
        >
          全屏
        </button>
        <button 
          class="px-2 py-1 text-xs bg-green-50 text-green-600 rounded hover:bg-green-100 dark:bg-green-900 dark:text-green-100 dark:hover:bg-green-800"
          @click="refreshStream"
        >
          刷新
        </button>
      </div>
    </div>
    
    <div class="relative video-container">
      <img 
        :src="videoStreamUrl" 
        alt="实时监控画面"
        class="w-full h-64 object-cover rounded"
      >
      <div v-if="!isStreaming" class="absolute inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center">
        <div class="text-center text-white">
          <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p>视频流未连接</p>
        </div>
      </div>
    </div>
    
    <div class="mt-4 grid grid-cols-2 gap-4">
      <div>
        <p class="text-sm text-gray-500 dark:text-gray-400">无人机状态</p>
        <p class="font-medium text-gray-900 dark:text-white">{{ droneStatus }}</p>
      </div>
      <div>
        <p class="text-sm text-gray-500 dark:text-gray-400">电池电量</p>
        <div class="flex items-center">
          <p class="font-medium text-gray-900 dark:text-white mr-2">{{ batteryLevel }}%</p>
          <div class="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div 
              class="h-full transition-all duration-500" 
              :class="batteryLevelClass" 
              :style="{ width: `${batteryLevel}%` }"
            ></div>
          </div>
        </div>
      </div>
      <div>
        <p class="text-sm text-gray-500 dark:text-gray-400">飞行高度</p>
        <p class="font-medium text-gray-900 dark:text-white">{{ altitude }}m</p>
      </div>
      <div>
        <p class="text-sm text-gray-500 dark:text-gray-400">飞行速度</p>
        <p class="font-medium text-gray-900 dark:text-white">{{ speed }}m/s</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MonitorPanel',
  props: {
    videoStreamUrl: {
      type: String,
      default: ''
    },
    isStreaming: {
      type: Boolean,
      default: false
    },
    droneStatus: {
      type: String,
      default: '待命'
    },
    batteryLevel: {
      type: Number,
      default: 0
    },
    altitude: {
      type: Number,
      default: 0
    },
    speed: {
      type: Number,
      default: 0
    }
  },
  emits: ['refresh-stream'],
  computed: {
    batteryLevelClass() {
      if (this.batteryLevel > 70) {
        return 'bg-green-500';
      } else if (this.batteryLevel > 30) {
        return 'bg-yellow-500';
      } else {
        return 'bg-red-500';
      }
    }
  },
  methods: {
    toggleFullScreen() {
      const container = this.$el.querySelector('.video-container');
      if (!document.fullscreenElement) {
        container.requestFullscreen().catch(err => {
          console.log(`全屏请求错误: ${err.message}`);
        });
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        }
      }
    },
    refreshStream() {
      this.$emit('refresh-stream');
    }
  }
}
</script>

<style scoped>
.monitor-panel {
  animation: fadeIn 0.5s ease-in;
}

.video-container {
  position: relative;
  transition: all 0.3s ease;
}

.video-container:hover {
  transform: scale(1.01);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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