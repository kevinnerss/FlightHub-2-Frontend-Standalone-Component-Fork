<template>
  <div class="pure-cesium-test h-screen flex flex-col">
    <div class="header bg-blue-600 text-white p-4">
      <h1 class="text-xl font-bold">纯Cesium测试页面</h1>
    </div>
    
    <div class="controls p-2 bg-gray-100">
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
      <button @click="forceResize" class="bg-purple-500 text-white px-4 py-2 rounded ml-2">
        强制调整大小
      </button>
    </div>
    
    <!-- Cesium容器 - 使用纯HTML/CSS -->
    <div ref="cesiumWrapper" class="cesium-wrapper flex-grow relative">
    </div>
  </div>
</template>

<script>
export default {
  name: 'PureCesiumTest',
  data() {
    return {
      viewer: null,
      tileset: null,
      loading: false,
      error: '',
      modelPath: '/models/Model_0/tileset.json'
    }
  },
  async mounted() {
    this.$nextTick(async () => {
      // 等待一段时间确保DOM完全渲染
      setTimeout(async () => {
        await this.initCesium()
        await this.loadModel()
      }, 200)
    })
  },
  beforeUnmount() {
    if (this.viewer) {
      this.viewer.destroy()
    }
  },
  methods: {
    async initCesium() {
      try {
        const Cesium = await import('cesium')
        Cesium.Ion.defaultAccessToken = ''
        
        const wrapper = this.$refs.cesiumWrapper
        if (!wrapper) {
          throw new Error('找不到 cesiumWrapper 元素')
        }
        
        // 创建Cesium容器
        const container = document.createElement('div')
        container.id = 'cesiumContainer'
        wrapper.appendChild(container)
        
        // 明确设置容器样式
        container.style.width = wrapper.offsetWidth + 'px'
        container.style.height = wrapper.offsetHeight + 'px'
        container.style.position = 'absolute'
        container.style.top = '0'
        container.style.left = '0'
        
        console.log('初始化时容器尺寸:', container.style.width, 'x', container.style.height)
        console.log('包装器尺寸:', wrapper.offsetWidth, 'x', wrapper.offsetHeight)
        
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
          creditContainer: document.createElement('div')
        })

        this.viewer.camera.setView({
          destination: Cesium.Cartesian3.fromDegrees(116.3913, 39.9075, 100000),
          orientation: {
            heading: Cesium.Math.toRadians(0),
            pitch: Cesium.Math.toRadians(-30),
            roll: 0.0
          }
        })
        
        // 添加resize监听
        window.addEventListener('resize', () => {
          if (this.viewer) {
            const newContainer = document.getElementById('cesiumContainer')
            const newWrapper = this.$refs.cesiumWrapper
            if (newContainer && newWrapper) {
              newContainer.style.width = newWrapper.offsetWidth + 'px'
              newContainer.style.height = newWrapper.offsetHeight + 'px'
              console.log('窗口大小变化，调整Cesium大小到:', newContainer.style.width, 'x', newContainer.style.height)
              this.viewer.resize()
            }
          }
        })
        
        // 添加一个短暂的延迟后强制调整大小
        setTimeout(() => {
          if (this.viewer) {
            const newContainer = document.getElementById('cesiumContainer')
            const newWrapper = this.$refs.cesiumWrapper
            if (newContainer && newWrapper) {
              newContainer.style.width = newWrapper.offsetWidth + 'px'
              newContainer.style.height = newWrapper.offsetHeight + 'px'
              console.log('初始化后强制调整大小到:', newContainer.style.width, 'x', newContainer.style.height)
              this.viewer.resize()
            }
          }
        }, 200)
      } catch (err) {
        this.error = '初始化Cesium失败: ' + err.message
        console.error('Cesium initialization error:', err)
      }
    },
    
    forceResize() {
      if (this.viewer) {
        const container = document.getElementById('cesiumContainer')
        const wrapper = this.$refs.cesiumWrapper
        if (container && wrapper) {
          container.style.width = wrapper.offsetWidth + 'px'
          container.style.height = wrapper.offsetHeight + 'px'
          console.log('强制调整大小到:', container.style.width, 'x', container.style.height)
          this.viewer.resize()
        }
        console.log('已强制调整Cesium大小')
      }
    },
    
    async loadModel() {
      if (!this.viewer || !this.modelPath) return
      
      this.loading = true
      this.error = ''
      
      try {
        const Cesium = await import('cesium')
        
        if (this.tileset) {
          this.viewer.scene.primitives.remove(this.tileset)
          this.tileset = null
        }
        
        console.log('正在加载模型:', this.modelPath)
        this.tileset = await Cesium.Cesium3DTileset.fromUrl(this.modelPath)
        this.viewer.scene.primitives.add(this.tileset)
        
        if (this.tileset.readyPromise) {
          this.tileset.readyPromise.then(() => {
            console.log('模型加载完成')
            this.viewer.zoomTo(this.tileset)
          }).catch(error => {
            this.error = '模型加载失败: ' + error.message
            console.error('Tileset loading error:', error)
          }).finally(() => {
            this.loading = false
          })
        } else {
          console.log('模型加载完成（无readyPromise）')
          this.viewer.zoomTo(this.tileset)
          this.loading = false
        }
      } catch (err) {
        this.error = '模型加载失败: ' + err.message
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

<style scoped>
.pure-cesium-test {
  width: 100%;
  height: 100%;
}

.cesium-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}
</style>