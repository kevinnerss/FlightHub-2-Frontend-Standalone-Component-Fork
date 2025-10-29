<template>
  <div class="digital-twin h-screen flex flex-col">
    <el-container class="flex-1 overflow-hidden">
      <!-- 顶部导航 -->
      <el-header height="60px" class="bg-white border-b flex items-center justify-between px-4 flex-shrink-0">
        <div class="flex items-center">
          <h1 class="text-xl font-bold">数字孪生系统</h1>
        </div>
        <div class="flex items-center gap-2">
          <el-button @click="resetView">重置视角</el-button>
          <el-button @click="toggleWireframe">{{ wireframe ? '实体模式' : '线框模式' }}</el-button>
          <!-- 调试信息 -->
          <div v-if="debugInfo" class="text-xs bg-gray-200 p-1 rounded">
            {{ debugInfo }}
          </div>
        </div>
      </el-header>
      
      <el-container class="p-4 gap-4 flex-1 overflow-hidden">
        <!-- 主内容区 - 3D模型视图 -->
        <el-main class="p-0 flex-1 overflow-hidden">
          <el-card 
            shadow="hover" 
            class="h-full border-0 flex flex-col"
            :body-style="{ 
              flex: '1',
              display: 'flex',
              flexDirection: 'column',
              padding: '0'
            }"
          >
            <template #header>
              <div class="flex items-center justify-between">
                <span class="text-lg font-medium">3D模型视图</span>
                <div class="flex items-center gap-2">
                  <el-input 
                    v-model="modelPath" 
                    placeholder="输入模型路径，如: /models/Model_0/tileset.json" 
                    size="small" 
                    style="width: 350px"
                  />
                  <el-button @click="loadModel" size="small">加载模型</el-button>
                  <el-button @click="checkContainerSizes" size="small">检查尺寸</el-button>
                </div>
              </div>
            </template>
            
            <div class="flex-1 relative">
              <div id="cesiumContainer" ref="cesiumContainer" class="absolute inset-0">
                <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 z-10">
                  <el-spinner size="large" />
                  <span class="ml-2 text-white">正在加载模型...</span>
                </div>
                <div v-if="error" class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 z-10">
                  <el-alert
                    :title="error"
                    type="error"
                    show-icon
                    class="w-96"
                  />
                </div>
              </div>
            </div>
          </el-card>
        </el-main>
        
        <!-- 右侧面板 -->
        <el-aside width="240px" class="space-y-4 overflow-hidden">
          <!-- 模型控制面板 -->
          <el-card shadow="hover" class="border-0 h-full flex flex-col">
            <template #header>
              <div class="flex items-center justify-between">
                <span class="text-base font-medium">模型控制</span>
              </div>
            </template>
            <div class="space-y-4 flex-grow overflow-y-auto">
              <div>
                <label class="block text-sm font-medium mb-1">模型缩放</label>
                <el-slider 
                  v-model="scale" 
                  :min="0.1" 
                  :max="5" 
                  :step="0.1" 
                  @change="updateScale"
                  show-input
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium mb-1">旋转角度</label>
                <el-slider 
                  v-model="rotation" 
                  :min="0" 
                  :max="360" 
                  @change="updateRotation"
                  show-input
                />
              </div>
              
              <div class="grid grid-cols-2 gap-2">
                <el-button @click="removeModel">移除模型</el-button>
                <el-button @click="flyToModel">飞向模型</el-button>
              </div>
            </div>
          </el-card>
          
          <!-- 模型信息面板 -->
          <el-card shadow="hover" class="border-0">
            <template #header>
              <div class="flex items-center justify-between">
                <span class="text-base font-medium">模型信息</span>
              </div>
            </template>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-500">模型格式:</span>
                <span>3D Tiles</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">模型状态:</span>
                <span>{{ modelState }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">加载路径:</span>
                <span class="text-xs">{{ modelPath || '未指定' }}</span>
              </div>
            </div>
          </el-card>
          
          <!-- 使用说明 -->
          <el-card shadow="hover" class="border-0">
            <template #header>
              <div class="flex items-center justify-between">
                <span class="text-base font-medium">使用说明</span>
              </div>
            </template>
            <div class="text-xs text-gray-500 space-y-2">
              <p>1. 将3D Tiles数据集放入 <code>public/models/</code> 目录</p>
              <p>2. 在上方输入框中输入模型路径</p>
              <p>3. 点击"加载模型"按钮加载3D模型</p>
              <p>4. 当前默认模型路径: <code>/models/Model_0/tileset.json</code></p>
            </div>
          </el-card>
        </el-aside>
      </el-container>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'DigitalTwin',
  data() {
    return {
      viewer: null,
      tileset: null,
      loading: false,
      error: '',
      wireframe: false,
      scale: 1.0,
      rotation: 0,
      modelState: '未加载',
      modelPath: '/models/Model_0/tileset.json', // 默认模型路径
      resizeObserver: null,
      debugInfo: ''
    }
  },
  async mounted() {
    // 等待DOM更新完成后再初始化Cesium
    this.$nextTick(async () => {
      // 等待Cesium资源加载完成后再初始化
      await this.initCesium()
      
      // 初始化 ResizeObserver
      this.initResizeObserver()
      
      // 自动加载默认模型
      await this.loadModel()
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
        
        // 确保容器元素存在且已正确渲染
        const container = document.getElementById('cesiumContainer')
        if (!container) {
          throw new Error('找不到 cesiumContainer 元素')
        }
        
        // 明确设置容器尺寸
        container.style.width = '100%'
        container.style.height = '100%'
        
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
          creditContainer: document.createElement('div')
        })

        // 设置初始视角
        this.viewer.camera.setView({
          destination: Cesium.Cartesian3.fromDegrees(116.3913, 39.9075, 1000),
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
            console.log('Cesium容器大小变化:', width, 'x', height)
            
            // 调整 Cesium Viewer 大小
            this.viewer.resize()
          }
        }
      })
      
      // 开始观察容器元素
      this.resizeObserver.observe(container)
    },
    
    checkContainerSizes() {
      const container = document.getElementById('cesiumContainer');
      const cardBody = container ? container.parentElement : null;
      const card = cardBody ? cardBody.parentElement : null;
      const main = card ? card.parentElement : null;
      
      if (container) {
        this.debugInfo = `Container: ${container.offsetWidth}x${container.offsetHeight}`;
        console.log('容器尺寸:', {
          container: { width: container.offsetWidth, height: container.offsetHeight },
          cardBody: cardBody ? { width: cardBody.offsetWidth, height: cardBody.offsetHeight } : null,
          card: card ? { width: card.offsetWidth, height: card.offsetHeight } : null,
          main: main ? { width: main.offsetWidth, height: main.offsetHeight } : null
        });
      }
    },
    
    async loadModel() {
      if (!this.viewer || !this.modelPath) return
      
      this.loading = true
      this.error = ''
      
      try {
        // 动态导入Cesium
        const Cesium = await import('cesium')
        
        // 如果已有模型，先移除
        if (this.tileset) {
          this.viewer.scene.primitives.remove(this.tileset)
          this.tileset = null
        }
        
        // 加载3D Tiles数据集
        this.tileset = await Cesium.Cesium3DTileset.fromUrl(this.modelPath)
        
        this.viewer.scene.primitives.add(this.tileset)
        
        // 缩放到模型
        if (this.tileset.readyPromise) {
          this.tileset.readyPromise.then(() => {
            this.modelState = '已加载'
            this.flyToModel()
          }).catch(error => {
            this.error = '模型加载失败: ' + error.message
            this.modelState = '加载失败'
            console.error('Tileset loading error:', error)
          }).finally(() => {
            this.loading = false
          })
        } else {
          // 如果没有readyPromise，直接设置状态
          this.modelState = '已加载'
          this.flyToModel()
          this.loading = false
        }
      } catch (err) {
        this.error = '模型加载失败: ' + err.message
        this.modelState = '加载失败'
        this.loading = false
        console.error('Model loading error:', err)
      }
    },
    removeModel() {
      if (this.tileset) {
        this.viewer.scene.primitives.remove(this.tileset)
        this.tileset = null
        this.modelState = '已移除'
      }
    },
    flyToModel() {
      if (this.viewer && this.tileset) {
        this.viewer.flyTo(this.tileset)
      }
    },
    async resetView() {
      if (this.viewer) {
        // 重置到初始视角
        const Cesium = await import('cesium')
        this.viewer.camera.setView({
          destination: Cesium.Cartesian3.fromDegrees(116.3913, 39.9075, 1000),
          orientation: {
            heading: Cesium.Math.toRadians(0),
            pitch: Cesium.Math.toRadians(-30),
            roll: 0.0
          }
        })
      }
    },
    toggleWireframe() {
      if (!this.tileset) return
      
      this.wireframe = !this.wireframe
      this.tileset.debugWireframe = this.wireframe
    },
    updateScale(value) {
      if (!this.tileset) return
      
      // 应用缩放
      console.log('更新模型缩放:', value)
    },
    updateRotation(value) {
      if (!this.tileset) return
      
      // 应用旋转
      console.log('更新模型旋转:', value)
    }
  }
}
</script>

<style scoped>
.digital-twin {
  width: 100%;
  height: 100%;
}

#cesiumContainer {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

code {
  background-color: #f1f1f1;
  padding: 2px 4px;
  border-radius: 3px;
}
</style>