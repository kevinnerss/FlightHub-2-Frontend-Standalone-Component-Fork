<template>
  <div class="control-panel p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">控制面板</h3>
      <span class="px-2 py-1 text-xs rounded-full" :class="statusClass">
        {{ currentStatus }}
      </span>
    </div>
    
    <div class="grid grid-cols-2 gap-3 mb-4">
      <button 
        class="flex flex-col items-center justify-center p-3 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-md transition-colors dark:bg-blue-900 dark:text-blue-100 dark:hover:bg-blue-800"
        @click="handleControlAction('start')"
        :disabled="currentStatus === '飞行中'"
      >
        <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
        </svg>
        <span class="text-xs">启动飞行</span>
      </button>
      
      <button 
        class="flex flex-col items-center justify-center p-3 bg-red-50 hover:bg-red-100 text-red-600 rounded-md transition-colors dark:bg-red-900 dark:text-red-100 dark:hover:bg-red-800"
        @click="handleControlAction('stop')"
        :disabled="currentStatus !== '飞行中'"
      >
        <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
        <span class="text-xs">停止飞行</span>
      </button>
      
      <button 
        class="flex flex-col items-center justify-center p-3 bg-green-50 hover:bg-green-100 text-green-600 rounded-md transition-colors dark:bg-green-900 dark:text-green-100 dark:hover:bg-green-800"
        @click="handleControlAction('pause')"
        :disabled="currentStatus !== '飞行中'"
      >
        <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span class="text-xs">暂停</span>
      </button>
      
      <button 
        class="flex flex-col items-center justify-center p-3 bg-yellow-50 hover:bg-yellow-100 text-yellow-600 rounded-md transition-colors dark:bg-yellow-900 dark:text-yellow-100 dark:hover:bg-yellow-800"
        @click="handleControlAction('return')"
      >
        <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
        </svg>
        <span class="text-xs">返回</span>
      </button>
    </div>
    
    <div class="space-y-3">
      <div>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">飞行高度调整</p>
        <input 
          type="range" 
          min="0" 
          max="100" 
          :value="targetAltitude" 
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          @input="updateAltitude($event.target.value)"
        >
        <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>0m</span>
          <span>{{ targetAltitude }}m</span>
          <span>100m</span>
        </div>
      </div>
      
      <div>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">飞行速度调整</p>
        <input 
          type="range" 
          min="0" 
          max="20" 
          :value="targetSpeed" 
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          @input="updateSpeed($event.target.value)"
        >
        <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>0m/s</span>
          <span>{{ targetSpeed }}m/s</span>
          <span>20m/s</span>
        </div>
      </div>
    </div>
    
    <button 
      class="w-full mt-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors dark:bg-purple-700 dark:hover:bg-purple-600"
      @click="handleEmergencyStop"
    >
      紧急停止
    </button>
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
  emits: ['control-action', 'update-altitude', 'update-speed', 'emergency-stop'],
  computed: {
    statusClass() {
      switch (this.currentStatus) {
        case '飞行中':
          return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100';
        case '暂停':
          return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100';
        case '待命':
          return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100';
        case '错误':
          return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100';
        default:
          return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100';
      }
    }
  },
  methods: {
    handleControlAction(action) {
      this.$emit('control-action', action);
    },
    updateAltitude(value) {
      this.$emit('update-altitude', parseInt(value));
    },
    updateSpeed(value) {
      this.$emit('update-speed', parseInt(value));
    },
    handleEmergencyStop() {
      if (confirm('确定执行紧急停止？这将立即中断所有飞行操作。')) {
        this.$emit('emergency-stop');
      }
    }
  }
}
</script>

<style scoped>
.control-panel {
  animation: fadeIn 0.5s ease-in;
}

input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #4299e1;
  cursor: pointer;
}

input[type="range"]::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #4299e1;
  cursor: pointer;
  border: none;
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