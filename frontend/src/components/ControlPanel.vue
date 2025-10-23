<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
    <!-- 标题栏 -->
    <div class="p-3 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
      <h3 class="text-base font-semibold text-gray-900 dark:text-white flex items-center">
        <i class="fa fa-gamepad text-green-500 mr-2"></i>
        无人机控制
      </h3>
    </div>
    
    <!-- 控制面板 -->
    <div class="p-4 space-y-4">
      <!-- 主控制按钮 -->
      <div class="grid grid-cols-2 gap-3">
        <button 
          class="flex flex-col items-center justify-center py-3 rounded-md bg-blue-600 hover:bg-blue-700 text-white transition-colors"
          @click="handleControl('start')"
          :disabled="currentStatus === '飞行中'"
        >
          <i class="fa fa-play-circle text-xl mb-1"></i>
          <span class="text-sm font-medium">启动</span>
        </button>
        <button 
          class="flex flex-col items-center justify-center py-3 rounded-md bg-yellow-600 hover:bg-yellow-700 text-white transition-colors"
          @click="handleControl('pause')"
          :disabled="currentStatus !== '飞行中'"
        >
          <i class="fa fa-pause-circle text-xl mb-1"></i>
          <span class="text-sm font-medium">暂停</span>
        </button>
        <button 
          class="flex flex-col items-center justify-center py-3 rounded-md bg-red-600 hover:bg-red-700 text-white transition-colors"
          @click="handleControl('stop')"
          :disabled="currentStatus === '待命' || currentStatus === '已停止'"
        >
          <i class="fa fa-stop-circle text-xl mb-1"></i>
          <span class="text-sm font-medium">停止</span>
        </button>
        <button 
          class="flex flex-col items-center justify-center py-3 rounded-md bg-purple-600 hover:bg-purple-700 text-white transition-colors"
          @click="handleControl('return')"
          :disabled="currentStatus === '待命' || currentStatus === '已停止' || currentStatus === '返回中'"
        >
          <i class="fa fa-undo text-xl mb-1"></i>
          <span class="text-sm font-medium">返航</span>
        </button>
      </div>
      
      <!-- 高度控制 -->
      <div>
        <div class="flex justify-between items-center mb-2">
          <label class="text-sm text-gray-700 dark:text-gray-300">目标高度</label>
          <span class="text-sm font-medium text-blue-600 dark:text-blue-400">{{ targetAltitude }} m</span>
        </div>
        <input 
          type="range" 
          min="0" 
          max="100" 
          step="1" 
          v-model.number="localTargetAltitude" 
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          @change="handleAltitudeChange"
          :disabled="currentStatus !== '飞行中'"
        >
        <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>0m</span>
          <span>50m</span>
          <span>100m</span>
        </div>
      </div>
      
      <!-- 速度控制 -->
      <div>
        <div class="flex justify-between items-center mb-2">
          <label class="text-sm text-gray-700 dark:text-gray-300">目标速度</label>
          <span class="text-sm font-medium text-blue-600 dark:text-blue-400">{{ targetSpeed }} m/s</span>
        </div>
        <input 
          type="range" 
          min="0" 
          max="15" 
          step="0.5" 
          v-model.number="localTargetSpeed" 
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          @change="handleSpeedChange"
          :disabled="currentStatus !== '飞行中'"
        >
        <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>0m/s</span>
          <span>7.5m/s</span>
          <span>15m/s</span>
        </div>
      </div>
      
      <!-- 紧急停止按钮 -->
      <button 
        class="w-full py-3 flex items-center justify-center bg-red-700 hover:bg-red-800 text-white rounded-md transition-colors animate-pulse"
        @click="$emit('emergency-stop')"
      >
        <i class="fa fa-exclamation-triangle mr-2"></i>
        <span class="font-medium">紧急停止</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ControlPanel',
  props: {
    currentStatus: {
      type: String,
      default: '待命'
    },
    targetAltitude: {
      type: Number,
      default: 0
    },
    targetSpeed: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      localTargetAltitude: this.targetAltitude,
      localTargetSpeed: this.targetSpeed
    }
  },
  watch: {
    targetAltitude(newVal) {
      this.localTargetAltitude = newVal
    },
    targetSpeed(newVal) {
      this.localTargetSpeed = newVal
    }
  },
  methods: {
    // 处理控制动作
    handleControl(action) {
      this.$emit('control-action', action)
    },
    
    // 处理高度变更
    handleAltitudeChange() {
      this.$emit('update-altitude', this.localTargetAltitude)
    },
    
    // 处理速度变更
    handleSpeedChange() {
      this.$emit('update-speed', this.localTargetSpeed)
    }
  }
}
</script>

<style scoped>
/* 滑块样式 */
input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

input[type="range"]::-webkit-slider-thumb:hover {
  transform: scale(1.2);
  background: #2563eb;
}

input[type="range"]:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

input[type="range"]:disabled::-webkit-slider-thumb {
  cursor: not-allowed;
  background: #94a3b8;
}

/* 按钮禁用状态 */
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 紧急停止按钮动画 */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(220, 38, 38, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(220, 38, 38, 0);
  }
}
</style>