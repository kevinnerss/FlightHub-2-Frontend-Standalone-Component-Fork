<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
    <!-- 标题栏 -->
    <div class="p-3 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 flex justify-between items-center">
      <h3 class="text-base font-semibold text-gray-900 dark:text-white flex items-center">
        <i class="fa fa-video-camera text-purple-500 mr-2"></i>
        实时监控
      </h3>
      <div class="flex items-center space-x-2">
        <span v-if="isStreaming" class="inline-block w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
        <span v-else class="inline-block w-2 h-2 rounded-full bg-red-500"></span>
        <button 
          class="text-xs text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400"
          @click="handleRefreshStream"
          title="刷新视频流"
        >
          <i class="fa fa-refresh"></i>
        </button>
      </div>
    </div>
    
    <!-- 视频流 -->
    <div class="relative">
      <div class="aspect-video bg-gray-900 relative overflow-hidden">
        <img 
          v-if="sanitizedVideoUrl" 
          :src="sanitizedVideoUrl" 
          alt="视频流" 
          class="w-full h-full object-cover"
          @error="handleImageError"
        >
        <div v-else class="w-full h-full flex flex-col items-center justify-center">
          <i class="fa fa-video-camera-slash text-gray-700 text-4xl mb-2"></i>
          <p class="text-gray-600 text-sm">{{ videoErrorMessage || '暂无视频流' }}</p>
        </div>
        
        <!-- 视频控制覆盖层 -->
        <div class="absolute bottom-2 left-0 right-0 flex justify-center opacity-0 hover:opacity-100 transition-opacity duration-300">
          <div class="bg-black/50 backdrop-blur-sm rounded-full px-3 py-1.5 flex items-center space-x-3">
            <button class="text-white hover:text-gray-300" @click.stop>
              <i class="fa fa-play"></i>
            </button>
            <button class="text-white hover:text-gray-300" @click.stop>
              <i class="fa fa-expand"></i>
            </button>
            <button class="text-white hover:text-gray-300" @click.stop>
              <i class="fa fa-arrows-alt"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 状态信息 -->
    <div class="p-3">
      <div class="grid grid-cols-2 gap-3">
        <div>
          <p class="text-xs text-gray-500 dark:text-gray-400">状态</p>
          <p class="text-sm font-medium text-gray-900 dark:text-white flex items-center">
            <span 
              class="inline-block w-2 h-2 rounded-full mr-2"
              :class="getStatusColorClass(safeDroneStatus)"
            ></span>
            {{ safeDroneStatus }}
          </p>
        </div>
        <div>
          <p class="text-xs text-gray-500 dark:text-gray-400">电池电量</p>
          <div class="flex items-center">
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mr-2">
              <div 
                class="h-1.5 rounded-full"
                :class="getBatteryColorClass(safeBatteryLevel)"
                :style="{ width: Math.min(100, Math.max(0, safeBatteryLevel)) + '%' }"
              ></div>
            </div>
            <span class="text-sm font-medium text-gray-900 dark:text-white min-w-8 text-right">{{ Math.min(100, Math.max(0, safeBatteryLevel)) }}%</span>
          </div>
        </div>
        <div>
          <p class="text-xs text-gray-500 dark:text-gray-400">高度</p>
          <p class="text-sm font-medium text-gray-900 dark:text-white">{{ formatNumber(safeAltitude) }} m</p>
        </div>
        <div>
          <p class="text-xs text-gray-500 dark:text-gray-400">速度</p>
          <p class="text-sm font-medium text-gray-900 dark:text-white">{{ formatNumber(safeSpeed) }} m/s</p>
        </div>
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
      default: 100
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
  data() {
    return {
      videoErrorMessage: '',
      // 默认的占位图像
      defaultImage: 'https://picsum.photos/1280/720?random=default'
    }
  },
  computed: {
    // 安全的无人机状态
    safeDroneStatus() {
      return typeof this.droneStatus === 'string' && this.droneStatus.trim() ? this.droneStatus : '待命'
    },
    
    // 安全的电池电量
    safeBatteryLevel() {
      const level = Number(this.batteryLevel)
      return isNaN(level) ? 100 : level
    },
    
    // 安全的高度
    safeAltitude() {
      const alt = Number(this.altitude)
      return isNaN(alt) ? 0 : alt
    },
    
    // 安全的速度
    safeSpeed() {
      const spd = Number(this.speed)
      return isNaN(spd) ? 0 : spd
    },
    
    // 净化后的视频URL
    sanitizedVideoUrl() {
      if (typeof this.videoStreamUrl === 'string' && this.videoStreamUrl.trim()) {
        return this.videoStreamUrl
      }
      return this.isStreaming ? this.defaultImage : ''
    }
  },
  methods: {
    // 处理刷新视频流
    handleRefreshStream() {
      this.videoErrorMessage = ''
      this.$emit('refresh-stream')
    },
    
    // 处理图像加载错误
    handleImageError(event) {
      console.error('视频流加载失败:', event)
      this.videoErrorMessage = '视频流加载失败'
      // 如果有错误，使用默认图像作为后备
      event.target.src = this.defaultImage
    },
    
    // 获取状态对应的颜色类
    getStatusColorClass(status) {
      const statusMap = {
        '待命': 'bg-green-500',
        '飞行中': 'bg-blue-500',
        '暂停': 'bg-yellow-500',
        '已停止': 'bg-red-500',
        '返回中': 'bg-red-500'
      }
      return statusMap[status] || 'bg-gray-500'
    },
    
    // 获取电池对应的颜色类
    getBatteryColorClass(level) {
      if (level > 70) return 'bg-green-500'
      if (level > 30) return 'bg-yellow-500'
      return 'bg-red-500'
    },
    
    // 格式化数字，保留一位小数
    formatNumber(num) {
      return Number(num).toFixed(1)
    }
  }
}
</script>

<style scoped>
/* 视频容器悬停效果 */
.aspect-video:hover {
  box-shadow: inset 0 0 0 2px rgba(59, 130, 246, 0.5);
}


/* 视频加载状态 */
img {
  transition: opacity 0.3s ease-in-out;
}

img:hover {
  opacity: 0.95;
}

/* 错误提示样式 */
.text-gray-600 {
  color: #6b7280;
}

.dark .text-gray-600 {
  color: #9ca3af;
}
</style>