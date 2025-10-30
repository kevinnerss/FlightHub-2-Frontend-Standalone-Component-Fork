<template>
  <div class="digital-twin h-screen flex flex-col">
    <!-- 顶部导航 - 简化结构 -->
    <div class="header bg-white border-b flex items-center justify-between px-4 h-16 flex-shrink-0">
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
    </div>
    
    <!-- 主内容区 -->
    <div class="main-content flex flex-1 overflow-hidden">
      <!-- 3D模型视图区域 - 简化嵌套结构 -->
      <div class="model-view flex-1 flex flex-col">
        <!-- 视图控制栏 -->
        <div class="view-controls p-2 bg-gray-100 border-b flex items-center justify-between">
          <span class="text-lg font-medium">3D模型视图</span>
          <div class="flex items-center gap-2">
            <el-input 
              v-model="modelPath" 
              placeholder="输入模型路径，如: /models/Model_0/tileset.json" 
              size="small" 
              style="width: 350px"
            />
            <el-button @click="loadModel" size="small">加载模型</el-button>
            <el-button @click="forceResize" size="small">强制调整大小</el-button>
            <!-- 新增点位选择按钮 -->
            <el-button @click="togglePointSelection" size="small" :type="pointSelectionEnabled ? 'primary' : ''">
              {{ pointSelectionEnabled ? '退出点选模式' : '点选模式' }}
            </el-button>
          </div>
        </div>
        
        <!-- Cesium容器 - 直接使用div而非多层嵌套 -->
        <div ref="cesiumWrapper" class="cesium-wrapper flex-1 relative">
          <!-- Cesium容器会动态创建 -->
          
          <!-- 加载指示器 -->
          <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 z-10">
            <el-spinner size="large" />
            <span class="ml-2 text-white">正在加载模型...</span>
          </div>
          
          <!-- 错误信息 -->
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
      
      <!-- 右侧面板 -->
      <div class="side-panel w-60 bg-white border-l p-4 overflow-y-auto">
        <!-- 模型控制面板 -->
        <div class="panel-section mb-6">
          <h3 class="text-base font-medium mb-3">模型控制</h3>
          <div class="space-y-4">
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
        </div>
        
        <!-- 点位信息面板 -->
        <div class="panel-section mb-6" v-if="selectedPoint">
          <h3 class="text-base font-medium mb-3">点位信息</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-500">X:</span>
              <span>{{ selectedPoint.x.toFixed(3) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Y:</span>
              <span>{{ selectedPoint.y.toFixed(3) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Z:</span>
              <span>{{ selectedPoint.z.toFixed(3) }}</span>
            </div>
            <div class="mt-2">
              <el-button @click="clearSelectedPoint" size="small">清除点位</el-button>
            </div>
          </div>
        </div>
        
        <!-- 模型信息面板 -->
        <div class="panel-section mb-6">
          <h3 class="text-base font-medium mb-3">模型信息</h3>
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
        </div>
        
        <!-- 使用说明 -->
        <div class="panel-section">
          <h3 class="text-base font-medium mb-3">使用说明</h3>
          <div class="text-xs text-gray-500 space-y-2">
            <p>1. 将3D Tiles数据集放入 <code>public/models/</code> 目录</p>
            <p>2. 在上方输入框中输入模型路径</p>
            <p>3. 点击"加载模型"按钮加载3D模型</p>
            <p>4. 点击"点选模式"按钮可在模型上选择点位</p>
            <p>5. 当前默认模型路径: <code>/models/Model_0/tileset.json</code></p>
          </div>
        </div>
      </div>
    </div>
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
      debugInfo: '',
      // 添加当前尺寸跟踪，避免不必要的调整
      currentWidth: 0,
      currentHeight: 0,
      debouncedForceResize: null,
      // 新增点选相关属性
      pointSelectionEnabled: false,
      selectedPoint: null,
      clickHandler: null
    }
  },
  async mounted() {
    // 等待DOM更新完成后再初始化Cesium
    this.$nextTick(async () => {
      // 等待一小段时间确保DOM完全渲染
      setTimeout(async () => {
        // 等待Cesium资源加载完成后再初始化
        await this.initCesium()
        
        // 初始化 ResizeObserver
        this.initResizeObserver()
        
        // 自动加载默认模型
        await this.loadModel()
      }, 200)
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
    // 移除窗口大小调整事件监听
    window.removeEventListener('resize', this.handleWindowResize)
    // 清理防抖函数的定时器
    if (this.debouncedForceResize && this.debouncedForceResize.timeout) {
      clearTimeout(this.debouncedForceResize.timeout)
    }
    // 清理点选相关的资源
    if (this.clickHandler) {
      this.clickHandler.destroy();
    }
  },
  methods: {
    async initCesium() {
      try {
        // 动态导入Cesium
        const Cesium = await import('cesium')
        
        // 设置Cesium的access token为空（因为我们使用的是本地资源）
        Cesium.Ion.defaultAccessToken = ''
        
        // 使用引用获取包装器元素
        const wrapper = this.$refs.cesiumWrapper
        if (!wrapper) {
          throw new Error('找不到 cesiumWrapper 元素')
        }
        
        // 移除已存在的Cesium容器（如果有）
        const existingContainer = document.getElementById('cesiumContainer')
        if (existingContainer) {
          existingContainer.remove()
        }
        
        // 使用原生DOM操作创建容器，避免Vue响应式影响
        const container = document.createElement('div')
        container.id = 'cesiumContainer'
        
        // 重要：在添加到DOM前先设置好样式
        container.style.width = '100%'
        container.style.height = '100%'
        container.style.position = 'relative'
        container.style.margin = '0'
        container.style.padding = '0'
        container.style.overflow = 'hidden'
        container.style.zIndex = '1'
        
        // 先将容器添加到DOM中
        wrapper.appendChild(container)
        
        // 确保容器有正确的尺寸
        const width = wrapper.offsetWidth
        const height = wrapper.offsetHeight
        
        if (width <= 0 || height <= 0) {
          throw new Error(`无效的容器尺寸: ${width}x${height}`)
        }
        
        console.log('初始化Cesium容器尺寸:', width, 'x', height)
        
        // 初始化Cesium Viewer - 添加一些关键配置以确保正确的大小调整
        this.viewer = new Cesium.Viewer(container, {
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
          creditContainer: document.createElement('div'),
          // 关键配置：避免Cesium自动添加resize监听器，由我们自己控制
          automaticallyTrackDataSourceClocks: false,
          // 提高渲染性能
          orderIndependentTranslucency: true,
          // 确保canvas元素可以正确调整大小
          contextOptions: {
            alpha: true,
            stencil: true
          }
        })
        
        // 确保canvas元素的尺寸正确设置
        if (this.viewer && this.viewer.canvas) {
          this.viewer.canvas.style.width = '100%'
          this.viewer.canvas.style.height = '100%'
        }

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
    
    // 防抖函数
    debounce(func, wait) {
      let timeout;
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout);
          func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      };
    },
    
    initResizeObserver() {
      const wrapper = this.$refs.cesiumWrapper
      if (!wrapper) return
      
      // 移除任何现有的ResizeObserver，防止多个实例
      if (this.resizeObserver) {
        this.resizeObserver.disconnect()
      }
      
      // 创建更宽松的防抖函数
      this.debouncedForceResize = this.debounce(() => {
        if (this.viewer) {
          console.log('防抖后调用forceResize')
          this.forceResize()
        }
      }, 100) // 增加到100ms，给DOM更多时间稳定
      
      // 创建 ResizeObserver 实例，但避免在回调中立即修改DOM
      this.resizeObserver = new ResizeObserver(entries => {
        // 记录尺寸变化，但不直接在回调中修改
        if (entries.length > 0) {
          const entry = entries[0]
          const width = entry.contentRect.width
          const height = entry.contentRect.height
          console.log(`ResizeObserver检测到尺寸变化: ${width}x${height}`)
        }
        // 使用防抖函数延迟处理
        this.debouncedForceResize()
      })
      
      // 只观察包装器元素
      this.resizeObserver.observe(wrapper, {
        box: 'content-box' // 观察内容盒大小
      })
      
      // 添加窗口调整大小事件监听
      window.addEventListener('resize', this.handleWindowResize)
      
      // 初始时立即调用一次调整大小
      setTimeout(() => {
        this.forceResize()
      }, 100)
    },
    
    handleWindowResize() {
      if (this.viewer) {
        // 利用已定义的防抖函数
        this.debouncedForceResize()
      }
    },
    
    // 强制调整Cesium容器大小
    forceResize() {
      try {
        console.log('开始强制调整大小...')
        const wrapper = this.$refs.cesiumWrapper
        const container = document.getElementById('cesiumContainer')
        
        if (!wrapper || !container || !this.viewer) {
          console.warn('无法调整大小：缺少必要元素')
          return
        }
        
        // 强制重新计算布局
        void wrapper.offsetHeight
        
        // 获取包装器的实际尺寸
        const width = wrapper.offsetWidth
        const height = wrapper.offsetHeight
        
        // 避免无效尺寸
        if (width <= 0 || height <= 0) {
          console.warn('无效的容器尺寸，跳过调整:', width, 'x', height)
          return
        }
        
        console.log('获取到的包装器尺寸:', width, 'x', height)
        
        // 更新调试信息
        this.debugInfo = `Wrapper: ${width}x${height}`
        
        // 关键修改：使用百分比而非像素值，让CSS自动处理
        container.style.width = '100%'
        container.style.height = '100%'
        
        // 确保canvas元素也使用百分比
        if (this.viewer && this.viewer.canvas) {
          this.viewer.canvas.style.width = '100%'
          this.viewer.canvas.style.height = '100%'
          console.log('设置canvas样式为100%宽高')
        }
        
        // 直接强制重新创建视图，而不是简单调用resize
        if (this.viewer) {
          console.log('调用scene.resize()和viewer.resize()')
          // 先调用scene.resize()
          this.viewer.scene.resize()
          // 再调用viewer.resize()
          this.viewer.resize()
          
          // 强制重排和重绘
          void container.offsetHeight
          
          // 延迟一帧再resize一次，确保生效
          requestAnimationFrame(() => {
            console.log('requestAnimationFrame中再次调用resize')
            if (this.viewer) {
              this.viewer.scene.resize()
              this.viewer.resize()
            }
          })
        }
        
        // 更新调试信息
        setTimeout(() => {
          if (container && this.viewer && this.viewer.canvas) {
            this.debugInfo = `Wrapper: ${width}x${height}, Canvas: ${this.viewer.canvas.clientWidth}x${this.viewer.canvas.clientHeight}`
          }
        }, 100)
        
        console.log('强制调整大小完成')
      } catch (error) {
        console.error('调整大小失败:', error)
      }
    },
    
    // 检查容器尺寸（更新为适应新结构）
    checkContainerSizes() {
      const wrapper = this.$refs.cesiumWrapper;
      const container = document.getElementById('cesiumContainer');
      const mainContent = wrapper ? wrapper.closest('.main-content') : null;
      
      if (wrapper && container) {
        this.debugInfo = `Wrapper: ${wrapper.offsetWidth}x${wrapper.offsetHeight}, Container: ${container.offsetWidth}x${container.offsetHeight}`;
        console.log('容器尺寸:', {
          wrapper: { width: wrapper.offsetWidth, height: wrapper.offsetHeight },
          container: { width: container.offsetWidth, height: container.offsetHeight },
          mainContent: mainContent ? { width: mainContent.offsetWidth, height: mainContent.offsetHeight } : null
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
    },
    
    // 新增点选相关方法
    togglePointSelection() {
      this.pointSelectionEnabled = !this.pointSelectionEnabled;
      
      if (this.pointSelectionEnabled) {
        this.enablePointSelection();
      } else {
        this.disablePointSelection();
      }
    },
    
    async enablePointSelection() {
      const Cesium = await import('cesium');
      
      // 移除已有的点击事件处理器（如果存在）
      if (this.clickHandler) {
        this.clickHandler.destroy();
      }
      
      // 创建新的点击事件处理器
      this.clickHandler = new Cesium.ScreenSpaceEventHandler(this.viewer.canvas);
      this.clickHandler.setInputAction(async (click) => {
        try {
          const pickedObject = this.viewer.scene.pick(click.position);
          
          if (pickedObject && pickedObject.primitive) {
            // 获取点击位置的笛卡尔坐标
            const cartesian = this.viewer.camera.pickEllipsoid(click.position, this.viewer.scene.globe.ellipsoid);
            
            if (cartesian) {
              // 转换为经纬度坐标
              const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
              const longitude = Cesium.Math.toDegrees(cartographic.longitude);
              const latitude = Cesium.Math.toDegrees(cartographic.latitude);
              const height = cartographic.height;
              
              // 保存选中的点
              this.selectedPoint = {
                x: longitude,
                y: latitude,
                z: height,
                cartesian: cartesian
              };
              
              console.log('选中的点:', this.selectedPoint);
            } else {
              // 如果无法从椭球体获取坐标，则尝试从模型获取
              const ray = this.viewer.camera.getPickRay(click.position);
              const position = this.viewer.scene.globe.pick(ray, this.viewer.scene);
              
              if (position) {
                const cartographic = Cesium.Cartographic.fromCartesian(position);
                const longitude = Cesium.Math.toDegrees(cartographic.longitude);
                const latitude = Cesium.Math.toDegrees(cartographic.latitude);
                const height = cartographic.height;
                
                this.selectedPoint = {
                  x: longitude,
                  y: latitude,
                  z: height,
                  cartesian: position
                };
                
                console.log('选中的点(从模型):', this.selectedPoint);
              }
            }
          }
        } catch (error) {
          console.error('点选过程中出错:', error);
        }
      }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    },
    
    disablePointSelection() {
      if (this.clickHandler) {
        this.clickHandler.destroy();
        this.clickHandler = null;
      }
    },
    
    clearSelectedPoint() {
      this.selectedPoint = null;
    }
  }
}
</script>

<style scoped>
/* 基础布局样式 */
.digital-twin {
  width: 100%;
  height: 100vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  z-index: 10;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.model-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; /* 防止flex子元素溢出 */
}

.view-controls {
  flex-shrink: 0;
}

.cesium-wrapper {
  flex: 1;
  position: relative;
  min-height: 0; /* 防止flex子元素溢出 */
}

.side-panel {
  flex-shrink: 0;
  min-height: 0; /* 防止flex子元素溢出 */
}

/* 面板部分样式 */
.panel-section {
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.panel-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

/* Cesium容器样式 - 通过JS动态设置，这里只设置基础样式 */
#cesiumContainer {
  position: absolute;
  top: 0;
  left: 0;
  margin: 0;
  padding: 0;
  overflow: hidden;
  z-index: 1;
}

code {
  background-color: #f1f1f1;
  padding: 2px 4px;
  border-radius: 3px;
}

/* 强制所有元素正确计算大小 */
* {
  box-sizing: border-box;
}

/* 确保弹性布局中的文本不会导致溢出 */
span, p {
  word-break: break-word;
  overflow-wrap: break-word;
}
</style>