<template>
  <div class="visualization-panel bg-gray-900 rounded-lg shadow-md h-full relative overflow-hidden">
    <div class="absolute top-4 left-4 z-10">
      <div class="bg-black bg-opacity-50 text-white p-2 rounded-md">
        <h3 class="text-lg font-semibold">3D 可视化</h3>
      </div>
    </div>
    
    <div class="absolute top-4 right-4 z-10 flex space-x-2">
      <button 
        class="bg-black bg-opacity-50 text-white p-2 rounded-md hover:bg-opacity-70 transition-all"
        @click="toggleViewMode"
        title="切换视图模式"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
      </button>
      
      <button 
        class="bg-black bg-opacity-50 text-white p-2 rounded-md hover:bg-opacity-70 transition-all"
        @click="resetView"
        title="重置视图"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
      </button>
      
      <button 
        class="bg-black bg-opacity-50 text-white p-2 rounded-md hover:bg-opacity-70 transition-all"
        @click="toggleLayers"
        title="图层控制"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
        </svg>
      </button>
    </div>
    
    <div id="visualization-container" class="w-full h-full">
      <!-- 模拟的3D场景 -->
      <div class="w-full h-full flex items-center justify-center">
        <div class="text-center">
          <div class="drone-model mb-4">
            <svg class="w-24 h-24 text-blue-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
              <circle cx="12" cy="7" r="4"></circle>
              <!-- 螺旋桨 -->
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M16 3l2 2-2 2" class="propeller"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M6 3l-2 2 2 2" class="propeller"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M16 15l2-2-2-2" class="propeller"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M6 15l-2-2 2-2" class="propeller"></path>
            </svg>
          </div>
          <p class="text-gray-400 text-lg">3D 场景加载中...</p>
          <p class="text-gray-500 text-sm mt-2">请等待模型和环境数据加载完成</p>
        </div>
      </div>
    </div>
    
    <!-- 图层控制面板 -->
    <div v-if="showLayers" class="absolute bottom-4 right-4 z-10 bg-black bg-opacity-80 text-white p-4 rounded-md w-64">
      <div class="flex justify-between items-center mb-3">
        <h4 class="font-medium">图层控制</h4>
        <button @click="showLayers = false" class="text-gray-400 hover:text-white">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
      
      <div class="space-y-2">
        <div class="flex items-center">
          <input type="checkbox" id="terrain" v-model="layers.terrain" class="mr-2">
          <label for="terrain" class="text-sm">地形</label>
        </div>
        <div class="flex items-center">
          <input type="checkbox" id="buildings" v-model="layers.buildings" class="mr-2">
          <label for="buildings" class="text-sm">建筑物</label>
        </div>
        <div class="flex items-center">
          <input type="checkbox" id="powerlines" v-model="layers.powerlines" class="mr-2">
          <label for="powerlines" class="text-sm">电力线</label>
        </div>
        <div class="flex items-center">
          <input type="checkbox" id="flightpath" v-model="layers.flightpath" class="mr-2">
          <label for="flightpath" class="text-sm">飞行路径</label>
        </div>
        <div class="flex items-center">
          <input type="checkbox" id="alarmpoints" v-model="layers.alarmpoints" class="mr-2">
          <label for="alarmpoints" class="text-sm">报警点</label>
        </div>
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
  emits: ['view-mode-changed', 'layers-changed'],
  data() {
    return {
      showLayers: false,
      currentViewMode: 'top',
      layers: {
        terrain: true,
        buildings: true,
        powerlines: true,
        flightpath: true,
        alarmpoints: true
      }
    }
  },
  mounted() {
    // 模拟3D场景初始化
    this.initializeVisualization();
  },
  watch: {
    layers: {
      deep: true,
      handler(newLayers) {
        this.$emit('layers-changed', newLayers);
      }
    }
  },
  methods: {
    initializeVisualization() {
      // 这里将来可以集成Three.js等3D库来实际渲染3D场景
      console.log('初始化3D可视化场景');
    },
    toggleViewMode() {
      const viewModes = ['top', 'side', 'perspective', 'drone'];
      const currentIndex = viewModes.indexOf(this.currentViewMode);
      this.currentViewMode = viewModes[(currentIndex + 1) % viewModes.length];
      this.$emit('view-mode-changed', this.currentViewMode);
      
      // 模拟视图模式切换
      console.log(`切换到${this.currentViewMode}视图`);
    },
    resetView() {
      console.log('重置视图');
    },
    toggleLayers() {
      this.showLayers = !this.showLayers;
    }
  }
}
</script>

<style scoped>
.visualization-panel {
  position: relative;
}

#visualization-container {
  position: relative;
}

.propeller {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 悬停效果 */
button:hover svg {
  transform: scale(1.1);
}

/* 过渡动画 */
.showLayers-enter-active,
.showLayers-leave-active {
  transition: all 0.3s ease;
}

.showLayers-enter-from,
.showLayers-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>