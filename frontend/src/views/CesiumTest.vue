<template>
  <div class="cesium-test h-screen flex flex-col">
    <div class="header bg-blue-600 text-white p-4 flex-shrink-0">
      <h1 class="text-xl font-bold">Cesium 测试页面</h1>
    </div>
    
    <div class="flex-grow flex flex-col">
      <div class="controls p-2 bg-gray-100 flex-shrink-0">
        <input 
          v-model="modelPath" 
          placeholder="输入模型路径" 
          class="border p-2 mr-2 w-80"
        />
        <button @click="loadModel" class="bg-blue-500 text-white px-4 py-2 rounded">
          加载模型
        </button>
        <button @click="resetView" class="bg-green-500 text-white px-4 py-2 rounded ml-2">
          重置视角
        </button>
        <button @click="checkContainerSize" class="bg-purple-500 text-white px-4 py-2 rounded ml-2">
          检查容器尺寸
        </button>
        <button @click="addTestPrimitive" class="bg-yellow-500 text-white px-4 py-2 rounded ml-2">
          添加测试图形
        </button>
      </div>
      
      <!-- Cesium容器 - 占据剩余所有空间 -->
      <div class="flex-grow relative">
        <div 
          id="cesiumContainer" 
          ref="cesiumContainer" 
          style="width: 100%; height: 100%;">
        </div>
        
        <!-- 加载指示器 -->
        <div 
          v-if="loading" 
          class="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10">
          <div class="text-white text-xl">正在加载模型...</div>
        </div>
        
        <!-- 错误信息 -->
        <div 
          v-if="error" 
          class="absolute inset-0 bg-black bg-opacity-70 flex items-center justify-center z-10">
          <div class="text-red-500 text-xl bg-white p-4 rounded">{{ error }}</div>
        </div>
        
        <!-- 调试信息 -->
        <div 
          v-if="containerInfo" 
          class="absolute top-0 left-0 bg-black bg-opacity-70 text-white p-2 text-sm z-20">
          容器尺寸: {{ containerInfo.width }} x {{ containerInfo.height }}
        </div>
        
        <!-- 模型信息 -->
        <div 
          v-if="modelInfo" 
          class="absolute top-8 left-0 bg-black bg-opacity-70 text-white p-2 text-sm z-20">
          模型状态: {{ modelInfo }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CesiumTest',
  data() {
    return {
      viewer: null,
      tileset: null,
      loading: false,
      error: '',
      modelPath: '/models/Model_0/tileset.json',
      containerInfo: null,
      modelInfo: null,
      resizeObserver: null
    }
  },
  async mounted() {
    // 确保DOM完全渲染后再初始化
    this.$nextTick(async () => {
      await this.initCesium()
      // 初始化 ResizeObserver
      this.initResizeObserver()
    })
  },
  beforeUnmount() {
    if (this.viewer) {
      this.viewer.destroy()
    }
    // 清理 ResizeObserver
    if (this.resizeObserver) {
      this.resizeObserver.disconnect()
    }
  },
  methods: {
    async initCesium() {
      try {
        // 动态导入Cesium
        const Cesium = await import('cesium')
        
        // 设置Cesium的access token为空（因为我们使用的是本地资源）
        Cesium.Ion.defaultAccessToken = ''
        
        // 确保容器元素存在
        const container = document.getElementById('cesiumContainer')
        if (!container) {
          throw new Error('找不到 cesiumContainer 元素')
        }
        
        // 明确设置容器尺寸
        container.style.width = '100%'
        container.style.height = '100%'
        
        // 获取容器尺寸
        this.containerInfo = {
          width: container.offsetWidth,
          height: container.offsetHeight
        }
        console.log('容器尺寸:', this.containerInfo)
        
        // 初始化Cesium Viewer
        this.viewer = new Cesium.Viewer('cesiumContainer', {
          animation: false,
          baseLayerPicker: false,
          fullscreenButton: false,
          vrButton: false,
          geocoder: false,
          homeButton: false,
          infoBox: false,
          sceneModePicker: false,
          selectionIndicator: false,
          timeline: false,
          navigationHelpButton: false,
          navigationInstructionsInitiallyVisible: false,
          scene3DOnly: true,
          shadows: true,
          shouldAnimate: true,
          // 移除Cesium商标
          creditContainer: document.createElement('div')
        })

        // 设置初始视角
        this.viewer.camera.setView({
          destination: Cesium.Cartesian3.fromDegrees(116.3913, 39.9075, 100000),
          orientation: {
            heading: Cesium.Math.toRadians(0),
            pitch: Cesium.Math.toRadians(-30),
            roll: 0.0
          }
        })
      } catch (err) {
        this.error = '初始化Cesium失败: ' + err.message
        console.error('Cesium initialization error:', err)
      }
    },
    
    initResizeObserver() {
      const container = document.getElementById('cesiumContainer')
      if (!container) return
      
      // 创建 ResizeObserver 实例
      this.resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
          if (entry.target === container && this.viewer) {
            const { width, height } = entry.contentRect
            console.log('容器大小变化:', width, 'x', height)
            
            // 更新容器信息显示
            this.containerInfo = { width, height }
            
            // 调整 Cesium Viewer 大小
            this.viewer.resize()
          }
        }
      })
      
      // 开始观察容器元素
      this.resizeObserver.observe(container)
    },
    
    checkContainerSize() {
      const container = document.getElementById('cesiumContainer')
      if (container) {
        this.containerInfo = {
          width: container.offsetWidth,
          height: container.offsetHeight
        }
        console.log('手动检查容器尺寸:', this.containerInfo)
      }
    },
    
    addTestPrimitive() {
      if (!this.viewer) return;
      
      const Cesium = window.CESIUM_BASE_URL ? window.CESIUM_BASE_URL : require('cesium');
      
      // 添加一个简单的测试图形
      const entity = this.viewer.entities.add({
        position: Cesium.Cartesian3.fromDegrees(116.3913, 39.9075, 100),
        point: {
          pixelSize: 10,
          color: Cesium.Color.RED
        }
      });
      
      this.viewer.flyTo(entity);
      console.log('已添加测试图形');
    },
    
    async loadModel() {
      if (!this.viewer || !this.modelPath) return
      
      this.loading = true
      this.error = ''
      this.modelInfo = '正在加载...'
      
      try {
        // 动态导入Cesium
        const Cesium = await import('cesium')
        
        // 如果已有模型，先移除
        if (this.tileset) {
          this.viewer.scene.primitives.remove(this.tileset)
          this.tileset = null
        }
        
        // 加载3D Tiles数据集
        console.log('正在加载模型:', this.modelPath)
        this.tileset = await Cesium.Cesium3DTileset.fromUrl(this.modelPath)
        
        this.viewer.scene.primitives.add(this.tileset)
        
        // 缩放到模型
        if (this.tileset.readyPromise) {
          this.tileset.readyPromise.then(() => {
            console.log('模型加载完成')
            this.modelInfo = '模型加载完成'
            this.viewer.zoomTo(this.tileset)
          }).catch(error => {
            this.error = '模型加载失败: ' + error.message
            this.modelInfo = '模型加载失败: ' + error.message
            console.error('Tileset loading error:', error)
          }).finally(() => {
            this.loading = false
          })
        } else {
          // 如果没有readyPromise，直接缩放
          console.log('模型加载完成（无readyPromise）')
          this.modelInfo = '模型加载完成（无readyPromise）'
          this.viewer.zoomTo(this.tileset)
          this.loading = false
        }
      } catch (err) {
        this.error = '模型加载失败: ' + err.message
        this.modelInfo = '模型加载失败: ' + err.message
        this.loading = false
        console.error('Model loading error:', err)
      }
    },
    
    resetView() {
      if (this.viewer) {
        const Cesium = window.CESIUM_BASE_URL ? window.CESIUM_BASE_URL : require('cesium')
        this.viewer.camera.setView({
          destination: Cesium.Cartesian3.fromDegrees(116.3913, 39.9075, 100000),
          orientation: {
            heading: Cesium.Math.toRadians(0),
            pitch: Cesium.Math.toRadians(-30),
            roll: 0.0
          }
        })
      }
    }
  }
}
</script>

<style>
.cesium-test {
  width: 100%;
  height: 100%;
}

#cesiumContainer {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
  position: relative;
}
</style>