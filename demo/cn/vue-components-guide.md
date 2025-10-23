# 大疆司空2 前端组件 Vue 集成指南

本文档提供了在Vue项目中集成大疆司空2前端组件的详细指南和示例代码。

## 目录结构

在Vue项目中，推荐按以下结构组织司空2相关组件：

```
src/
├── components/
│   ├── fh2/
│   │   ├── FH2Base.vue       # FH2基础组件，处理初始化逻辑
│   │   ├── ProjectMap.vue    # 项目地图组件
│   │   ├── Cockpit.vue       # 驾驶舱组件
│   │   ├── Wayline.vue       # 航线编辑器组件
│   │   └── WaylineCreation.vue # 航线创建组件
├── services/
│   └── fh2Service.js         # FH2服务，封装SDK调用和事件处理
├── utils/
│   └── fh2Utils.js           # FH2工具函数
└── views/
    ├── Dashboard.vue         # 仪表盘页面，集成多个FH2组件
    └── ProjectDetail.vue     # 项目详情页，使用项目地图组件
```

## 1. FH2 服务封装 (fh2Service.js)

首先创建一个服务层，封装FH2 SDK的所有操作，便于统一管理和维护。

```javascript
// src/services/fh2Service.js

class FH2Service {
  constructor() {
    this.isInitialized = false
    this.eventHandlers = {}
    this.cesiumViewers = {}
  }

  /**
   * 初始化FH2 SDK
   * @param {Object} config - 初始化配置
   * @param {string} config.serverUrl - 服务器URL
   * @param {string} config.wssUrl - WebSocket URL
   * @param {string} config.hostUrl - 主机URL
   * @param {string} config.prjId - 项目ID
   * @param {string} config.projectToken - 项目Token
   * @returns {Promise<void>}
   */
  async init(config) {
    if (this.isInitialized) {
      console.warn('FH2 SDK 已经初始化')
      return
    }

    if (!window.FH2) {
      throw new Error('FH2 SDK 未加载，请检查paas.js引入')
    }

    try {
      window.FH2.initConfig({
        serverUrl: config.serverUrl,
        wssUrl: config.wssUrl,
        hostUrl: config.hostUrl,
        prjId: config.prjId,
        projectToken: config.projectToken
      })

      this.isInitialized = true
      console.log('FH2 SDK 初始化成功')
      
      // 订阅地图加载事件
      this.subscribe('cesium-viewer-change', (key) => {
        console.log(`地图实例加载: ${key}`)
        if (window.FH2.cesiumViewer && window.FH2.cesiumViewer[key]) {
          this.cesiumViewers[key] = window.FH2.cesiumViewer[key]
        }
      })

      return this
    } catch (error) {
      console.error('FH2 SDK 初始化失败:', error)
      throw error
    }
  }

  /**
   * 订阅FH2事件
   * @param {string} eventName - 事件名称
   * @param {Function} callback - 回调函数
   */
  subscribe(eventName, callback) {
    if (!window.FH2) {
      console.error('FH2 SDK 未加载')
      return
    }

    try {
      window.FH2.subscribe(eventName, callback)
      
      // 存储事件处理器，便于后续取消订阅
      if (!this.eventHandlers[eventName]) {
        this.eventHandlers[eventName] = []
      }
      this.eventHandlers[eventName].push(callback)
    } catch (error) {
      console.error(`订阅事件 ${eventName} 失败:`, error)
    }
  }

  /**
   * 取消订阅FH2事件
   * @param {string} eventName - 事件名称
   * @param {Function} callback - 回调函数，不传则取消该事件的所有订阅
   */
  unsubscribe(eventName, callback) {
    if (!window.FH2 || !this.eventHandlers[eventName]) {
      return
    }

    try {
      if (callback) {
        // 取消特定回调的订阅
        window.FH2.unsubscribe(eventName, callback)
        this.eventHandlers[eventName] = this.eventHandlers[eventName].filter(
          (handler) => handler !== callback
        )
      } else {
        // 取消该事件的所有订阅
        const handlers = this.eventHandlers[eventName]
        handlers.forEach((handler) => {
          window.FH2.unsubscribe(eventName, handler)
        })
        this.eventHandlers[eventName] = []
      }
    } catch (error) {
      console.error(`取消订阅事件 ${eventName} 失败:`, error)
    }
  }

  /**
   * 取消所有事件订阅
   */
  unsubscribeAll() {
    Object.keys(this.eventHandlers).forEach((eventName) => {
      this.unsubscribe(eventName)
    })
  }

  /**
   * 加载项目地图组件
   * @param {string} containerId - 容器ID
   */
  loadProject(containerId) {
    if (!this.isInitialized || !window.FH2) {
      throw new Error('FH2 SDK 未初始化')
    }

    try {
      window.FH2.loadProject(containerId)
      console.log(`项目地图组件加载到容器: ${containerId}`)
    } catch (error) {
      console.error('加载项目地图组件失败:', error)
      throw error
    }
  }

  /**
   * 销毁项目地图组件
   */
  destroyProject() {
    if (!window.FH2) return

    try {
      window.FH2.destroyProject()
      console.log('项目地图组件已销毁')
    } catch (error) {
      console.error('销毁项目地图组件失败:', error)
    }
  }

  /**
   * 加载驾驶舱组件
   * @param {string} containerId - 容器ID
   * @param {Object} config - 配置参数
   * @param {string} config.gateway_sn - 网关SN
   * @param {string} config.drone_sn - 飞行器SN
   */
  loadCockpit(containerId, config) {
    if (!this.isInitialized || !window.FH2) {
      throw new Error('FH2 SDK 未初始化')
    }

    try {
      window.FH2.loadCockpit(containerId, config)
      console.log(`驾驶舱组件加载到容器: ${containerId}`)
    } catch (error) {
      console.error('加载驾驶舱组件失败:', error)
      throw error
    }
  }

  /**
   * 销毁驾驶舱组件
   */
  destroyCockpit() {
    if (!window.FH2) return

    try {
      window.FH2.destroyCockpit()
      console.log('驾驶舱组件已销毁')
    } catch (error) {
      console.error('销毁驾驶舱组件失败:', error)
    }
  }

  /**
   * 加载航线编辑器组件
   * @param {string} containerId - 容器ID
   * @param {Object} config - 配置参数
   * @param {string} config.wayline_id - 航线ID
   */
  loadWayline(containerId, config) {
    if (!this.isInitialized || !window.FH2) {
      throw new Error('FH2 SDK 未初始化')
    }

    try {
      window.FH2.loadWayline(containerId, config)
      console.log(`航线编辑器组件加载到容器: ${containerId}`)
    } catch (error) {
      console.error('加载航线编辑器组件失败:', error)
      throw error
    }
  }

  /**
   * 销毁航线编辑器组件
   */
  destroyWayline() {
    if (!window.FH2) return

    try {
      window.FH2.destroyWayline()
      console.log('航线编辑器组件已销毁')
    } catch (error) {
      console.error('销毁航线编辑器组件失败:', error)
    }
  }

  /**
   * 加载航线创建组件
   * @param {string} containerId - 容器ID
   */
  loadWaylineCreation(containerId) {
    if (!this.isInitialized || !window.FH2) {
      throw new Error('FH2 SDK 未初始化')
    }

    try {
      window.FH2.loadWaylineCreation(containerId)
      console.log(`航线创建组件加载到容器: ${containerId}`)
    } catch (error) {
      console.error('加载航线创建组件失败:', error)
      throw error
    }
  }

  /**
   * 销毁航线创建组件
   */
  destroyWaylineCreation() {
    if (!window.FH2) return

    try {
      window.FH2.destroyWaylineCreation()
      console.log('航线创建组件已销毁')
    } catch (error) {
      console.error('销毁航线创建组件失败:', error)
    }
  }

  /**
   * 添加自定义地图元素
   * @param {Object} options - 自定义元素配置
   */
  addCustomMapElement(options = {}) {
    if (!window.Cesium) {
      console.error('Cesium 未加载')
      return
    }

    const defaultOptions = {
      position: window.Cesium.Cartesian3.fromDegrees(113.93, 22.57, 50),
      label: {
        text: "自定义标记",
        font: '14pt monospace',
        fillColor: window.Cesium.Color.YELLOW,
        outlineColor: window.Cesium.Color.BLACK,
        outlineWidth: 2,
        style: window.Cesium.LabelStyle.FILL_AND_OUTLINE,
        pixelOffset: new window.Cesium.Cartesian2(0, -20),
        eyeOffset: new window.Cesium.Cartesian3(0, 0, 0),
        horizontalOrigin: window.Cesium.HorizontalOrigin.CENTER,
        verticalOrigin: window.Cesium.VerticalOrigin.BOTTOM
      },
      point: {
        pixelSize: 10,
        color: window.Cesium.Color.RED,
        outlineWidth: 2,
        outlineColor: window.Cesium.Color.WHITE
      }
    }

    const elementOptions = { ...defaultOptions, ...options }
    const entities = []

    // 向所有加载的地图实例添加元素
    Object.keys(this.cesiumViewers).forEach((key) => {
      try {
        const entity = this.cesiumViewers[key].entities.add(elementOptions)
        entities.push({ key, entity })
      } catch (error) {
        console.error(`向地图实例 ${key} 添加自定义元素失败:`, error)
      }
    })

    return entities
  }

  /**
   * 切换主题
   * @param {boolean} isDark - 是否切换到深色主题
   */
  toggleTheme(isDark) {
    document.body.className = isDark ? 'set-change-color' : ''
    console.log(`主题已切换为: ${isDark ? '深色' : '默认'}`)
  }
}

// 创建单例实例
const fh2Service = new FH2Service()

export default fh2Service
```

## 2. 基础组件封装 (FH2Base.vue)

创建一个基础组件，用于处理FH2 SDK的初始化逻辑，其他FH2组件可以继承此组件。

```vue
<!-- src/components/fh2/FH2Base.vue -->
<template>
  <div class="fh2-base">
    <slot></slot>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import fh2Service from '@/services/fh2Service'

export default {
  name: 'FH2Base',
  props: {
    // FH2 配置
    fh2Config: {
      type: Object,
      default: () => ({
        serverUrl: 'http://127.0.0.1:30812',
        wssUrl: 'ws://127.0.0.1:30812/duplex/web',
        hostUrl: 'http://127.0.0.1',
        prjId: '',
        projectToken: ''
      })
    },
    // 是否自动初始化
    autoInit: {
      type: Boolean,
      default: true
    }
  },
  emits: ['init', 'error', 'ready'],
  setup(props, { emit }) {
    const isReady = ref(false)
    const error = ref(null)

    // 初始化 FH2
    const initFH2 = async () => {
      try {
        error.value = null
        await fh2Service.init(props.fh2Config)
        isReady.value = true
        emit('ready')
        return true
      } catch (err) {
        error.value = err.message
        emit('error', err)
        return false
      }
    }

    // 监听配置变化
    watch(
      () => props.fh2Config,
      async (newConfig) => {
        if (newConfig && props.autoInit) {
          await initFH2()
        }
      },
      { deep: true, immediate: props.autoInit }
    )

    // 组件挂载
    onMounted(() => {
      emit('init', { initFH2 })
    })

    // 组件卸载
    onUnmounted(() => {
      // 注意：在实际应用中，可能不需要在基础组件中取消所有订阅
      // 而是在具体的组件中管理自己的生命周期
    })

    return {
      isReady,
      error,
      initFH2
    }
  }
}
</script>

<style scoped>
.fh2-base {
  width: 100%;
  height: 100%;
}
</style>
```

## 3. 项目地图组件 (ProjectMap.vue)

```vue
<!-- src/components/fh2/ProjectMap.vue -->
<template>
  <div class="project-map-container" :class="{ 'loading': isLoading }">
    <div class="fh2-container">
      <div class="project-details">
        <div :id="containerId"></div>
        <div :id="`${containerId}-middle`"></div>
        <div :id="`${containerId}-right-micro-app`" class="right-micro-app">
          <div class="maps-micro-app">
            <div :id="`${containerId}-map-app-placeholder`" class="map-app-placeholder">
              <div :id="`${containerId}-map-global`" class="map-app-container"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="componentError" class="error-overlay">
      <div class="error-message">{{ componentError }}</div>
      <button @click="reload" class="reload-btn">重新加载</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import fh2Service from '@/services/fh2Service'

export default {
  name: 'ProjectMap',
  props: {
    // 组件ID前缀，用于生成唯一的容器ID
    idPrefix: {
      type: String,
      default: 'project-app'
    },
    // 自动加载
    autoLoad: {
      type: Boolean,
      default: true
    },
    // 监听地图加载事件
    onMapLoaded: {
      type: Function,
      default: () => {}
    }
  },
  emits: ['loaded', 'error'],
  setup(props, { emit }) {
    const isLoading = ref(false)
    const componentError = ref(null)
    const isLoaded = ref(false)
    
    // 计算容器ID
    const containerId = computed(() => props.idPrefix + '-container')
    
    // 地图加载回调
    const mapLoadedHandler = (key) => {
      if (key.includes(props.idPrefix)) {
        isLoading.value = false
        isLoaded.value = true
        emit('loaded', { key })
        props.onMapLoaded(key)
      }
    }
    
    // 加载组件
    const loadComponent = async () => {
      if (!fh2Service.isInitialized) {
        const errorMsg = 'FH2 SDK 未初始化，请先初始化'
        componentError.value = errorMsg
        emit('error', new Error(errorMsg))
        return false
      }
      
      try {
        isLoading.value = true
        componentError.value = null
        
        // 订阅地图加载事件
        fh2Service.subscribe('cesium-viewer-change', mapLoadedHandler)
        
        // 加载项目地图组件
        fh2Service.loadProject(containerId.value)
        
        return true
      } catch (err) {
        isLoading.value = false
        componentError.value = err.message
        emit('error', err)
        return false
      }
    }
    
    // 销毁组件
    const destroyComponent = () => {
      try {
        // 取消事件订阅
        fh2Service.unsubscribe('cesium-viewer-change', mapLoadedHandler)
        
        // 销毁组件
        fh2Service.destroyProject()
        
        isLoaded.value = false
        componentError.value = null
      } catch (err) {
        console.error('销毁项目地图组件失败:', err)
      }
    }
    
    // 重新加载
    const reload = () => {
      destroyComponent()
      setTimeout(() => loadComponent(), 500)
    }
    
    // 组件挂载
    onMounted(() => {
      if (props.autoLoad) {
        loadComponent()
      }
    })
    
    // 组件卸载
    onUnmounted(() => {
      destroyComponent()
    })
    
    // 暴露方法和状态
    return {
      isLoading,
      componentError,
      containerId,
      loadComponent,
      destroyComponent,
      reload
    }
  }
}
</script>

<style scoped>
.project-map-container {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #4cceac;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text,
.error-message {
  margin-top: 15px;
  font-size: 16px;
  color: #333;
}

.error-message {
  color: #e74c3c;
  text-align: center;
  padding: 0 20px;
}

.reload-btn {
  margin-top: 15px;
  padding: 8px 20px;
  background-color: #4cceac;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.reload-btn:hover {
  background-color: #45b798;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 确保容器正确显示 */
:deep(.fh2-container) {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

:deep(#project-app-container > div),
:deep(.map-app-container > div) {
  height: 100% !important;
  width: 100% !important;
}
</style>
```

## 4. 驾驶舱组件 (Cockpit.vue)

```vue
<!-- src/components/fh2/Cockpit.vue -->
<template>
  <div class="cockpit-container" :class="{ 'loading': isLoading }">
    <div class="fh2-container">
      <div :id="`${containerId}-header`"></div>
      <div class="project-details router-cockpit">
        <div :id="`${containerId}-project`"></div>
        <div :id="`${containerId}-middle`"></div>
        <div :id="`${containerId}-right-micro-app`" class="right-micro-app">
          <div class="maps-micro-app">
            <div class="cockpit-left-border-container"></div>
            <div :id="`${containerId}-map-placeholder`" class="map-app-placeholder">
              <div class="cockpit-dock-live-container"></div>
              <div :id="`${containerId}-map-global`" class="map-app-container"></div>
              <div class="cockpit-bottom-border-container"></div>
            </div>
          </div>
          <div class="project-right">
            <div :id="containerId"></div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="componentError" class="error-overlay">
      <div class="error-message">{{ componentError }}</div>
      <button @click="reload" class="reload-btn">重新加载</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import fh2Service from '@/services/fh2Service'

export default {
  name: 'Cockpit',
  props: {
    // 组件ID前缀
    idPrefix: {
      type: String,
      default: 'cockpit-app'
    },
    // 网关SN
    gatewaySn: {
      type: String,
      default: ''
    },
    // 飞行器SN
    droneSn: {
      type: String,
      default: ''
    },
    // 自动加载
    autoLoad: {
      type: Boolean,
      default: true
    }
  },
  emits: ['loaded', 'error', 'status-change'],
  setup(props, { emit }) {
    const isLoading = ref(false)
    const componentError = ref(null)
    const isLoaded = ref(false)
    
    // 计算容器ID
    const containerId = computed(() => props.idPrefix + '-container')
    
    // 加载组件
    const loadComponent = async () => {
      if (!fh2Service.isInitialized) {
        const errorMsg = 'FH2 SDK 未初始化，请先初始化'
        componentError.value = errorMsg
        emit('error', new Error(errorMsg))
        return false
      }
      
      try {
        isLoading.value = true
        componentError.value = null
        
        // 加载驾驶舱组件
        fh2Service.loadCockpit(containerId.value, {
          gateway_sn: props.gatewaySn,
          drone_sn: props.droneSn
        })
        
        isLoading.value = false
        isLoaded.value = true
        emit('loaded', { gatewaySn: props.gatewaySn, droneSn: props.droneSn })
        
        return true
      } catch (err) {
        isLoading.value = false
        componentError.value = err.message
        emit('error', err)
        return false
      }
    }
    
    // 销毁组件
    const destroyComponent = () => {
      try {
        fh2Service.destroyCockpit()
        isLoaded.value = false
        componentError.value = null
      } catch (err) {
        console.error('销毁驾驶舱组件失败:', err)
      }
    }
    
    // 重新加载
    const reload = () => {
      destroyComponent()
      setTimeout(() => loadComponent(), 500)
    }
    
    // 监听设备SN变化
    watch(
      [() => props.gatewaySn, () => props.droneSn],
      ([newGatewaySn, newDroneSn], [oldGatewaySn, oldDroneSn]) => {
        // 只有当组件已加载且SN发生变化时才重新加载
        if (isLoaded.value && (newGatewaySn !== oldGatewaySn || newDroneSn !== oldDroneSn)) {
          reload()
        }
      }
    )
    
    // 组件挂载
    onMounted(() => {
      if (props.autoLoad) {
        loadComponent()
      }
    })
    
    // 组件卸载
    onUnmounted(() => {
      destroyComponent()
    })
    
    // 暴露方法和状态
    return {
      isLoading,
      componentError,
      containerId,
      loadComponent,
      destroyComponent,
      reload
    }
  }
}
</script>

<style scoped>
.cockpit-container {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #4cceac;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text,
.error-message {
  margin-top: 15px;
  font-size: 16px;
  color: #333;
}

.error-message {
  color: #e74c3c;
  text-align: center;
  padding: 0 20px;
}

.reload-btn {
  margin-top: 15px;
  padding: 8px 20px;
  background-color: #4cceac;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.reload-btn:hover {
  background-color: #45b798;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 确保容器正确显示 */
:deep(.fh2-container) {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

:deep(#cockpit-app-container > div),
:deep(.map-app-container > div) {
  height: 100% !important;
  width: 100% !important;
}
</style>
```

## 5. 航线编辑器组件 (Wayline.vue)

```vue
<!-- src/components/fh2/Wayline.vue -->
<template>
  <div class="wayline-container" :class="{ 'loading': isLoading }">
    <div class="fh2-container">
      <div :id="`${containerId}-header`"></div>
      <div class="project-details">
        <div :id="`${containerId}-project`"></div>
        <div :id="`${containerId}-middle`"></div>
        <div :id="`${containerId}-right-micro-app`" class="right-micro-app">
          <div class="maps-micro-app">
            <div :id="`${containerId}-map-placeholder`" class="map-app-placeholder">
              <div :id="`${containerId}-map-global`" class="map-app-container"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="componentError" class="error-overlay">
      <div class="error-message">{{ componentError }}</div>
      <button @click="reload" class="reload-btn">重新加载</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import fh2Service from '@/services/fh2Service'

export default {
  name: 'Wayline',
  props: {
    // 组件ID前缀
    idPrefix: {
      type: String,
      default: 'wayline-app'
    },
    // 航线ID
    waylineId: {
      type: String,
      default: ''
    },
    // 自动加载
    autoLoad: {
      type: Boolean,
      default: true
    }
  },
  emits: ['loaded', 'error', 'saved', 'canceled', 'back'],
  setup(props, { emit }) {
    const isLoading = ref(false)
    const componentError = ref(null)
    const isLoaded = ref(false)
    
    // 计算容器ID
    const containerId = computed(() => props.idPrefix + '-container')
    
    // 事件处理函数
    const waylineSaveHandler = () => {
      emit('saved')
    }
    
    const waylineCancelHandler = () => {
      emit('canceled')
    }
    
    const waylineBackHandler = () => {
      emit('back')
    }
    
    // 加载组件
    const loadComponent = async () => {
      if (!fh2Service.isInitialized) {
        const errorMsg = 'FH2 SDK 未初始化，请先初始化'
        componentError.value = errorMsg
        emit('error', new Error(errorMsg))
        return false
      }
      
      try {
        isLoading.value = true
        componentError.value = null
        
        // 订阅航线相关事件
        fh2Service.subscribe('wayline-save', waylineSaveHandler)
        fh2Service.subscribe('wayline-cancel', waylineCancelHandler)
        fh2Service.subscribe('wayline-back', waylineBackHandler)
        
        // 加载航线编辑器组件
        fh2Service.loadWayline(containerId.value, {
          wayline_id: props.waylineId
        })
        
        isLoading.value = false
        isLoaded.value = true
        emit('loaded', { waylineId: props.waylineId })
        
        return true
      } catch (err) {
        isLoading.value = false
        componentError.value = err.message
        emit('error', err)
        return false
      }
    }
    
    // 销毁组件
    const destroyComponent = () => {
      try {
        // 取消事件订阅
        fh2Service.unsubscribe('wayline-save', waylineSaveHandler)
        fh2Service.unsubscribe('wayline-cancel', waylineCancelHandler)
        fh2Service.unsubscribe('wayline-back', waylineBackHandler)
        
        // 销毁组件
        fh2Service.destroyWayline()
        
        isLoaded.value = false
        componentError.value = null
      } catch (err) {
        console.error('销毁航线编辑器组件失败:', err)
      }
    }
    
    // 重新加载
    const reload = () => {
      destroyComponent()
      setTimeout(() => loadComponent(), 500)
    }
    
    // 监听航线ID变化
    watch(
      () => props.waylineId,
      (newId, oldId) => {
        // 只有当组件已加载且ID发生变化时才重新加载
        if (isLoaded.value && newId !== oldId) {
          reload()
        }
      }
    )
    
    // 组件挂载
    onMounted(() => {
      if (props.autoLoad) {
        loadComponent()
      }
    })
    
    // 组件卸载
    onUnmounted(() => {
      destroyComponent()
    })
    
    // 暴露方法和状态
    return {
      isLoading,
      componentError,
      containerId,
      loadComponent,
      destroyComponent,
      reload
    }
  }
}
</script>

<style scoped>
.wayline-container {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #4cceac;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text,
.error-message {
  margin-top: 15px;
  font-size: 16px;
  color: #333;
}

.error-message {
  color: #e74c3c;
  text-align: center;
  padding: 0 20px;
}

.reload-btn {
  margin-top: 15px;
  padding: 8px 20px;
  background-color: #4cceac;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.reload-btn:hover {
  background-color: #45b798;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 确保容器正确显示 */
:deep(.fh2-container) {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

:deep(#wayline-app-container > div),
:deep(.map-app-container > div) {
  height: 100% !important;
  width: 100% !important;
}
</style>
```

## 6. 航线创建组件 (WaylineCreation.vue)

```vue
<!-- src/components/fh2/WaylineCreation.vue -->
<template>
  <div class="wayline-creation-container" :class="{ 'loading': isLoading }">
    <div class="fh2-container">
      <div :id="`${containerId}-header`"></div>
      <div class="project-details">
        <div :id="`${containerId}-project`"></div>
        <div :id="`${containerId}-middle`"></div>
        <div :id="`${containerId}-right-micro-app`" class="right-micro-app">
          <div class="maps-micro-app">
            <div :id="`${containerId}-map-placeholder`" class="map-app-placeholder">
              <div :id="`${containerId}-map-global`" class="map-app-container"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="componentError" class="error-overlay">
      <div class="error-message">{{ componentError }}</div>
      <button @click="reload" class="reload-btn">重新加载</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import fh2Service from '@/services/fh2Service'

export default {
  name: 'WaylineCreation',
  props: {
    // 组件ID前缀
    idPrefix: {
      type: String,
      default: 'wayline-create-app'
    },
    // 自动加载
    autoLoad: {
      type: Boolean,
      default: true
    }
  },
  emits: ['loaded', 'error', 'saved', 'canceled'],
  setup(props, { emit }) {
    const isLoading = ref(false)
    const componentError = ref(null)
    const isLoaded = ref(false)
    
    // 计算容器ID
    const containerId = computed(() => props.idPrefix + '-container')
    
    // 事件处理函数
    const waylineCreationSavedHandler = (waylineId) => {
      emit('saved', { waylineId })
    }
    
    const waylineCreationCancelHandler = () => {
      emit('canceled')
    }
    
    // 加载组件
    const loadComponent = async () => {
      if (!fh2Service.isInitialized) {
        const errorMsg = 'FH2 SDK 未初始化，请先初始化'
        componentError.value = errorMsg
        emit('error', new Error(errorMsg))
        return false
      }
      
      try {
        isLoading.value = true
        componentError.value = null
        
        // 订阅航线创建相关事件
        fh2Service.subscribe('wayline-creation-saved', waylineCreationSavedHandler)
        fh2Service.subscribe('wayline-creation-cancel', waylineCreationCancelHandler)
        
        // 加载航线创建组件
        fh2Service.loadWaylineCreation(containerId.value)
        
        isLoading.value = false
        isLoaded.value = true
        emit('loaded')
        
        return true
      } catch (err) {
        isLoading.value = false
        componentError.value = err.message
        emit('error', err)
        return false
      }
    }
    
    // 销毁组件
    const destroyComponent = () => {
      try {
        // 取消事件订阅
        fh2Service.unsubscribe('wayline-creation-saved', waylineCreationSavedHandler)
        fh2Service.unsubscribe('wayline-creation-cancel', waylineCreationCancelHandler)
        
        // 销毁组件
        fh2Service.destroyWaylineCreation()
        
        isLoaded.value = false
        componentError.value = null
      } catch (err) {
        console.error('销毁航线创建组件失败:', err)
      }
    }
    
    // 重新加载
    const reload = () => {
      destroyComponent()
      setTimeout(() => loadComponent(), 500)
    }
    
    // 组件挂载
    onMounted(() => {
      if (props.autoLoad) {
        loadComponent()
      }
    })
    
    // 组件卸载
    onUnmounted(() => {
      destroyComponent()
    })
    
    // 暴露方法和状态
    return {
      isLoading,
      componentError,
      containerId,
      loadComponent,
      destroyComponent,
      reload
    }
  }
}
</script>

<style scoped>
.wayline-creation-container {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #4cceac;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text,
.error-message {
  margin-top: 15px;
  font-size: 16px;
  color: #333;
}

.error-message {
  color: #e74c3c;
  text-align: center;
  padding: 0 20px;
}

.reload-btn {
  margin-top: 15px;
  padding: 8px 20px;
  background-color: #4cceac;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.reload-btn:hover {
  background-color: #45b798;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 确保容器正确显示 */
:deep(.fh2-container) {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

:deep(#wayline-create-app-container > div),
:deep(.map-app-container > div) {
  height: 100% !important;
  width: 100% !important;
}
</style>
```

## 7. 在Vue应用中使用示例 (Dashboard.vue)

```vue
<!-- src/views/Dashboard.vue -->
<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>大疆司空2 管理控制台</h1>
      <div class="header-actions">
        <button @click="toggleTheme" class="theme-btn">
          {{ isDarkTheme ? '浅色主题' : '深色主题' }}
        </button>
      </div>
    </header>
    
    <!-- 初始化配置面板 -->
    <div class="config-panel" v-if="!isFH2Initialized">
      <h2>连接配置</h2>
      <form @submit.prevent="initFH2">
        <div class="form-group">
          <label for="serverIp">服务IP:</label>
          <input
            id="serverIp"
            v-model="fh2Config.serverUrl"
            type="text"
            placeholder="http://127.0.0.1:30812"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="projectId">项目ID:</label>
          <input
            id="projectId"
            v-model="fh2Config.prjId"
            type="text"
            placeholder="输入项目ID"
          />
        </div>
        
        <div class="form-group">
          <label for="projectToken">组织密钥:</label>
          <input
            id="projectToken"
            v-model="fh2Config.projectToken"
            type="text"
            placeholder="输入组织密钥"
          />
        </div>
        
        <button type="submit" class="init-btn">初始化连接</button>
      </form>
      
      <div v-if="initError" class="error-message">
        {{ initError }}
      </div>
    </div>
    
    <!-- 组件控制和显示区域 -->
    <div v-else class="components-section">
      <!-- 控制栏 -->
      <div class="control-bar">
        <div class="control-group">
          <button @click="showProjectMap = !showProjectMap" class="control-btn">
            {{ showProjectMap ? '隐藏' : '显示' }} 项目地图
          </button>
          
          <div class="control-inputs">
            <input
              v-model="droneConfig.gatewaySn"
              type="text"
              placeholder="网关SN"
              class="small-input"
            />
            <input
              v-model="droneConfig.droneSn"
              type="text"
              placeholder="飞行器SN"
              class="small-input"
            />
            <button @click="showCockpit = !showCockpit" class="control-btn">
              {{ showCockpit ? '隐藏' : '显示' }} 驾驶舱
            </button>
          </div>
          
          <div class="control-inputs">
            <input
              v-model="waylineId"
              type="text"
              placeholder="航线ID"
              class="small-input"
            />
            <button @click="showWayline = !showWayline" class="control-btn">
              {{ showWayline ? '隐藏' : '显示' }} 航线编辑器
            </button>
          </div>
          
          <button @click="showWaylineCreation = !showWaylineCreation" class="control-btn">
            {{ showWaylineCreation ? '隐藏' : '显示' }} 航线创建
          </button>
          
          <button @click="addCustomMapMarker" class="control-btn">
            添加地图标记
          </button>
        </div>
      </div>
      
      <!-- 组件显示区域 -->
      <div class="components-grid">
        <!-- 项目地图 -->
        <div v-if="showProjectMap" class="component-card">
          <div class="component-header">
            <h3>项目地图</h3>
            <button @click="showProjectMap = false" class="close-btn">×</button>
          </div>
          <div class="component-content">
            <ProjectMap
              :id-prefix="'dashboard-project'"
              @loaded="handleProjectLoaded"
              @error="handleComponentError"
            />
          </div>
        </div>
        
        <!-- 驾驶舱 -->
        <div v-if="showCockpit" class="component-card">
          <div class="component-header">
            <h3>驾驶舱</h3>
            <button @click="showCockpit = false" class="close-btn">×</button>
          </div>
          <div class="component-content">
            <Cockpit
              :id-prefix="'dashboard-cockpit'"
              :gateway-sn="droneConfig.gatewaySn"
              :drone-sn="droneConfig.droneSn"
              @loaded="handleCockpitLoaded"
              @error="handleComponentError"
              @status-change="handleCockpitStatusChange"
            />
          </div>
        </div>
        
        <!-- 航线编辑器 -->
        <div v-if="showWayline" class="component-card">
          <div class="component-header">
            <h3>航线编辑器</h3>
            <button @click="showWayline = false" class="close-btn">×</button>
          </div>
          <div class="component-content">
            <Wayline
              :id-prefix="'dashboard-wayline'"
              :wayline-id="waylineId"
              @loaded="handleWaylineLoaded"
              @error="handleComponentError"
              @saved="handleWaylineSaved"
              @canceled="handleWaylineCanceled"
              @back="handleWaylineBack"
            />
          </div>
        </div>
        
        <!-- 航线创建 -->
        <div v-if="showWaylineCreation" class="component-card">
          <div class="component-header">
            <h3>航线创建</h3>
            <button @click="showWaylineCreation = false" class="close-btn">×</button>
          </div>
          <div class="component-content">
            <WaylineCreation
              :id-prefix="'dashboard-wayline-creation'"
              @loaded="handleWaylineCreationLoaded"
              @error="handleComponentError"
              @saved="handleWaylineCreationSaved"
              @canceled="handleWaylineCreationCanceled"
            />
          </div>
        </div>
      </div>
      
      <!-- 消息通知 -->
      <div v-if="notification" class="notification" :class="notification.type">
        <span>{{ notification.message }}</span>
        <button @click="notification = null" class="notification-close">×</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import fh2Service from '@/services/fh2Service'
import ProjectMap from '@/components/fh2/ProjectMap.vue'
import Cockpit from '@/components/fh2/Cockpit.vue'
import Wayline from '@/components/fh2/Wayline.vue'
import WaylineCreation from '@/components/fh2/WaylineCreation.vue'

export default {
  name: 'Dashboard',
  components: {
    ProjectMap,
    Cockpit,
    Wayline,
    WaylineCreation
  },
  setup() {
    // FH2 配置
    const fh2Config = reactive({
      serverUrl: 'http://127.0.0.1:30812',
      wssUrl: 'ws://127.0.0.1:30812/duplex/web',
      hostUrl: 'http://127.0.0.1',
      prjId: '',
      projectToken: ''
    })
    
    // 无人机配置
    const droneConfig = reactive({
      gatewaySn: '',
      droneSn: ''
    })
    
    // 状态
    const isFH2Initialized = ref(false)
    const initError = ref('')
    const isDarkTheme = ref(false)
    
    // 组件显示状态
    const showProjectMap = ref(false)
    const showCockpit = ref(false)
    const showWayline = ref(false)
    const showWaylineCreation = ref(false)
    const waylineId = ref('')
    
    // 通知
    const notification = ref(null)
    
    // 显示通知
    const showNotification = (message, type = 'info') => {
      notification.value = {
        message,
        type // 'info', 'success', 'error', 'warning'
      }
      
      // 3秒后自动关闭通知
      setTimeout(() => {
        if (notification.value && notification.value.message === message) {
          notification.value = null
        }
      }, 3000)
    }
    
    // 初始化FH2
    const initFH2 = async () => {
      try {
        initError.value = ''
        await fh2Service.init(fh2Config)
        isFH2Initialized.value = true
        showNotification('FH2 SDK 初始化成功', 'success')
      } catch (error) {
        initError.value = error.message
        showNotification(`初始化失败: ${error.message}`, 'error')
      }
    }
    
    // 切换主题
    const toggleTheme = () => {
      isDarkTheme.value = !isDarkTheme.value
      fh2Service.toggleTheme(isDarkTheme.value)
      showNotification(`已切换到${isDarkTheme.value ? '深色' : '浅色'}主题`)
    }
    
    // 添加自定义地图标记
    const addCustomMapMarker = () => {
      try {
        fh2Service.addCustomMapElement({
          label: {
            text: 'Vue应用添加的标记',
            font: '14pt monospace',
            fillColor: window.Cesium.Color.GREEN,
            outlineColor: window.Cesium.Color.BLACK,
            outlineWidth: 2
          }
        })
        showNotification('已添加自定义地图标记', 'success')
      } catch (error) {
        showNotification(`添加地图标记失败: ${error.message}`, 'error')
      }
    }
    
    // 事件处理函数
    const handleProjectLoaded = () => {
      showNotification('项目地图加载成功', 'success')
    }
    
    const handleCockpitLoaded = () => {
      showNotification('驾驶舱加载成功', 'success')
    }
    
    const handleCockpitStatusChange = (status) => {
      showNotification(`驾驶舱状态: ${status}`, 'info')
    }
    
    const handleWaylineLoaded = () => {
      showNotification('航线编辑器加载成功', 'success')
    }
    
    const handleWaylineSaved = () => {
      showNotification('航线保存成功', 'success')
    }
    
    const handleWaylineCanceled = () => {
      showNotification('取消保存航线', 'info')
    }
    
    const handleWaylineBack = () => {
      showNotification('退出航线编辑器', 'info')
    }
    
    const handleWaylineCreationLoaded = () => {
      showNotification('航线创建组件加载成功', 'success')
    }
    
    const handleWaylineCreationSaved = ({ waylineId: newWaylineId }) => {
      waylineId.value = newWaylineId
      showNotification(`航线创建成功，ID: ${newWaylineId}`, 'success')
    }
    
    const handleWaylineCreationCanceled = () => {
      showNotification('取消创建航线', 'info')
    }
    
    const handleComponentError = (error) => {
      showNotification(`组件错误: ${error.message}`, 'error')
    }
    
    // 组件挂载时检查是否已经初始化
    onMounted(() => {
      if (fh2Service.isInitialized) {
        isFH2Initialized.value = true
        showNotification('FH2 SDK 已初始化', 'info')
      }
    })
    
    // 组件卸载时清理资源
    onUnmounted(() => {
      // 取消所有通知定时器
      // 注意：在实际应用中，可能需要更精细的资源管理
    })
    
    return {
      fh2Config,
      droneConfig,
      isFH2Initialized,
      initError,
      isDarkTheme,
      showProjectMap,
      showCockpit,
      showWayline,
      showWaylineCreation,
      waylineId,
      notification,
      initFH2,
      toggleTheme,
      addCustomMapMarker,
      handleProjectLoaded,
      handleCockpitLoaded,
      handleCockpitStatusChange,
      handleWaylineLoaded,
      handleWaylineSaved,
      handleWaylineCanceled,
      handleWaylineBack,
      handleWaylineCreationLoaded,
      handleWaylineCreationSaved,
      handleWaylineCreationCanceled,
      handleComponentError
    }
  }
}
</script>

<style scoped>
.dashboard {
  width: 100%;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.dashboard-header {
  background-color: #141b2d;
  color: white;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dashboard-header h1 {
  margin: 0;
  font-size: 24px;
}

.theme-btn {
  background-color: #4cceac;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.theme-btn:hover {
  background-color: #50dcd8;
}

.config-panel {
  background-color: white;
  max-width: 600px;
  margin: 40px auto;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.config-panel h2 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #4cceac;
}

.init-btn {
  width: 100%;
  padding: 12px;
  background-color: #4cceac;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.init-btn:hover {
  background-color: #50dcd8;
}

.error-message {
  margin-top: 16px;
  padding: 12px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  font-size: 14px;
}

.components-section {
  padding: 24px;
}

.control-bar {
  background-color: white;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.control-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.control-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.small-input {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  width: 180px;
}

.control-btn {
  padding: 8px 16px;
  background-color: #4cceac;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.control-btn:hover {
  background-color: #50dcd8;
}

.components-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
  gap: 24px;
}

.component-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 500px;
}

.component-header {
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.component-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.close-btn:hover {
  background-color: #e9ecef;
}

.component-content {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 10000;
  animation: slideIn 0.3s ease-out;
}

.notification.info {
  background-color: #e3f2fd;
  color: #1565c0;
}

.notification.success {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.notification.error {
  background-color: #ffebee;
  color: #c62828;
}

.notification.warning {
  background-color: #fff8e1;
  color: #f57c00;
}

.notification-close {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: inherit;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .components-grid {
    grid-template-columns: 1fr;
  }
  
  .component-card {
    height: 400px;
  }
  
  .control-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .control-inputs {
    flex-direction: column;
  }
  
  .small-input {
    width: 100%;
  }
}
```

## 8. Vue 项目集成最佳实践

### 8.1 异步加载 PAAS SDK

在 Vue 项目中，推荐使用动态导入方式加载 PAAS SDK，以优化首屏加载性能。

```javascript
// src/plugins/fh2.js

/**
 * 动态加载 FH2 PAAS SDK
 */
export const loadFH2SDK = () => {
  return new Promise((resolve, reject) => {
    // 检查是否已经加载
    if (window.FH2) {
      resolve(window.FH2)
      return
    }
    
    // 检查是否已经有正在加载的脚本
    if (window._fh2Loading) {
      // 如果有正在加载的脚本，则等待其加载完成
      const checkInterval = setInterval(() => {
        if (window.FH2) {
          clearInterval(checkInterval)
          resolve(window.FH2)
        }
      }, 100)
      
      // 设置超时
      setTimeout(() => {
        clearInterval(checkInterval)
        reject(new Error('FH2 SDK 加载超时'))
      }, 10000)
      
      return
    }
    
    // 标记正在加载
    window._fh2Loading = true
    
    // 创建 script 标签
    const script = document.createElement('script')
    script.src = '/path/to/paas.js' // 替换为实际的 paas.js 路径
    script.async = true
    script.onload = () => {
      window._fh2Loading = false
      resolve(window.FH2)
    }
    script.onerror = () => {
      window._fh2Loading = false
      reject(new Error('FH2 SDK 加载失败'))
    }
    
    // 添加到 document.head
    document.head.appendChild(script)
  })
}

/**
 * 注册全局 FH2 插件
 */
export default {
  install: (app, options = {}) => {
    // 将 loadFH2SDK 方法添加到全局属性
    app.config.globalProperties.$loadFH2SDK = loadFH2SDK
    
    // 提供给组合式 API 使用
    app.provide('loadFH2SDK', loadFH2SDK)
  }
}
```

在 main.js 中注册插件：

```javascript
// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import FH2Plugin from './plugins/fh2'
import './assets/main.css'

const app = createApp(App)

app.use(router)
app.use(store)
app.use(FH2Plugin)

app.mount('#app')
```

### 8.2 在组件中使用

```vue
<!-- src/components/FH2App.vue -->
<template>
  <div class="fh2-app">
    <div v-if="loading" class="loading">加载 FH2 SDK...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else>
      <!-- FH2 组件内容 -->
      <slot></slot>
    </template>
  </div>
</template>

<script>
import { ref, onMounted, inject } from 'vue'

export default {
  name: 'FH2App',
  setup() {
    const loading = ref(false)
    const error = ref('')
    const loadFH2SDK = inject('loadFH2SDK')
    
    onMounted(async () => {
      try {
        loading.value = true
        await loadFH2SDK()
        loading.value = false
      } catch (err) {
        loading.value = false
        error.value = `加载失败: ${err.message}`
      }
    })
    
    return {
      loading,
      error
    }
  }
}
</script>
```

### 8.3 错误处理与重试机制

在使用 FH2 组件时，应该实现错误处理和重试机制，以提高应用的稳定性。

```javascript
// src/utils/errorHandler.js

/**
 * 错误重试函数
 * @param {Function} fn - 要执行的函数
 * @param {Object} options - 配置选项
 * @param {number} options.maxRetries - 最大重试次数
 * @param {number} options.retryDelay - 重试间隔（毫秒）
 * @returns {Promise<any>}
 */
export const retry = async (fn, { maxRetries = 3, retryDelay = 1000 } = {}) => {
  let lastError
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error
      console.warn(`操作失败，${i + 1}/${maxRetries}，${retryDelay}ms 后重试:`, error)
      await new Promise(resolve => setTimeout(resolve, retryDelay))
    }
  }
  
  throw lastError
}

/**
 * 格式化 FH2 错误信息
 * @param {Error|string} error - 错误对象或字符串
 * @returns {string}
 */
export const formatFH2Error = (error) => {
  if (typeof error === 'string') {
    return error
  }
  
  // 根据错误类型返回友好提示
  if (error.message.includes('未初始化')) {
    return '请先初始化 FH2 SDK'
  }
  
  if (error.message.includes('连接')) {
    return '无法连接到 FH2 服务器，请检查网络或服务配置'
  }
  
  if (error.message.includes('Token')) {
    return 'Token 验证失败，请检查项目凭证是否正确'
  }
  
  return error.message || '发生未知错误'
}
```

### 8.4 性能优化建议

1. **懒加载组件**：使用 Vue 的动态导入功能，只在需要时加载 FH2 组件

```javascript
// src/router/index.js
const routes = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/project/:id',
    name: 'ProjectDetail',
    component: () => import('../views/ProjectDetail.vue'),
    meta: { requiresAuth: true }
  }
]
```

2. **按需加载 FH2 组件**：只在需要时加载和初始化 FH2 组件

```vue
<script>
import { ref, defineAsyncComponent } from 'vue'

// 异步加载 FH2 组件
const ProjectMap = defineAsyncComponent(() => import('../components/fh2/ProjectMap.vue'))
const Cockpit = defineAsyncComponent(() => import('../components/fh2/Cockpit.vue'))
const Wayline = defineAsyncComponent(() => import('../components/fh2/Wayline.vue'))
const WaylineCreation = defineAsyncComponent(() => import('../components/fh2/WaylineCreation.vue'))

export default {
  components: {
    ProjectMap,
    Cockpit,
    Wayline,
    WaylineCreation
  }
  // ...
}
</script>
```

3. **避免重复初始化**：确保 FH2 SDK 只初始化一次

4. **销毁不再使用的组件**：当组件不再需要时，调用 destroy 方法释放资源

5. **优化地图渲染**：减少地图上的自定义元素数量，避免过度渲染

### 8.5 响应式设计与移动端适配

FH2 组件需要在不同屏幕尺寸上正常工作，以下是一些响应式设计建议：

```css
/* src/assets/responsive.css */

/* 基础容器样式 */
.fh2-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .project-details {
    flex-direction: column !important;
  }
  
  .right-micro-app {
    width: 100% !important;
    height: 50% !important;
  }
  
  .maps-micro-app {
    flex-direction: column;
  }
  
  .map-app-container {
    height: 100% !important;
  }
}

@media (max-width: 480px) {
  .component-card {
    height: 300px !important;
  }
  
  .control-group {
    font-size: 12px;
  }
  
  .control-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
}
```

## 9. Vue 集成注意事项

1. **生命周期管理**：
   - 确保在组件挂载后加载 FH2 组件
   - 在组件卸载前销毁 FH2 组件，避免内存泄漏

2. **异步操作处理**：
   - FH2 SDK 操作多为异步，需要正确处理 Promise 和回调
   - 使用 try/catch 捕获可能的错误

3. **容器样式**：
   - 确保为 FH2 组件提供足够的容器空间
   - 使用 flexbox 或 grid 布局确保容器正确显示

4. **事件处理**：
   - 正确订阅和取消订阅 FH2 事件
   - 避免事件处理器重复注册

5. **避免重复初始化**：
   - FH2 SDK 应该只初始化一次
   - 使用服务层或单例模式管理 SDK 实例

6. **跨域问题**：
   - 确保服务器已正确配置 CORS
   - 在开发环境中可能需要配置代理

7. **性能考量**：
   - 避免频繁加载/销毁 FH2 组件
   - 合理管理地图元素，避免过多自定义标记影响性能

8. **调试技巧**：
   - 使用浏览器开发工具监控网络请求和控制台输出
   - 检查 FH2 事件是否正常触发
   - 确认容器元素是否正确渲染

## 10. 完整的 Vue 项目模板

为了帮助开发者快速开始，这里提供一个简单的 Vue 项目初始化步骤：

```bash
# 创建 Vue 项目
npm init vue@latest fh2-vue-integration

# 进入项目目录
cd fh2-vue-integration

# 安装依赖
npm install

# 创建所需目录结构
mkdir -p src/components/fh2 src/services src/utils src/plugins

# 创建必要的文件
# - src/services/fh2Service.js
# - src/components/fh2/FH2Base.vue
# - src/components/fh2/ProjectMap.vue
# - src/components/fh2/Cockpit.vue
# - src/components/fh2/Wayline.vue
# - src/components/fh2/WaylineCreation.vue
# - src/plugins/fh2.js
# - src/utils/errorHandler.js
# - src/views/Dashboard.vue
# - src/views/ProjectDetail.vue
```

## 11. 示例代码：Vue 3 + FH2 组件的完整集成

以下是一个完整的 Vue 3 应用入口文件示例：

```javascript
// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import FH2Plugin from './plugins/fh2'
import './assets/main.css'
import './assets/responsive.css'

const app = createApp(App)

// 注册插件
app.use(router)
app.use(store)
app.use(FH2Plugin)

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue 全局错误:', err, info)
  // 这里可以添加错误上报逻辑
}

// 挂载应用
app.mount('#app')
```

## 12. FAQ

### 12.1 如何在 Vue 组件中获取 FH2 的 Cesium 实例？

可以通过监听 `cesium-viewer-change` 事件来获取 Cesium 实例：

```vue
<script>
import { onMounted, onUnmounted } from 'vue'
import fh2Service from '@/services/fh2Service'

export default {
  setup() {
    const handleCesiumViewerChange = (key) => {
      const cesiumViewer = fh2Service.cesiumViewers[key]
      if (cesiumViewer) {
        console.log('获取到 Cesium 实例:', key, cesiumViewer)
        // 可以在这里进行 Cesium 相关操作
      }
    }
    
    onMounted(() => {
      fh2Service.subscribe('cesium-viewer-change', handleCesiumViewerChange)
    })
    
    onUnmounted(() => {
      fh2Service.unsubscribe('cesium-viewer-change', handleCesiumViewerChange)
    })
  }
}
</script>
```

### 12.2 如何处理 FH2 组件的错误和异常？

建议在每个 FH2 组件中实现错误处理和重试机制：

```vue
<script>
import { ref, onMounted } from 'vue'
import fh2Service from '@/services/fh2Service'
import { retry, formatFH2Error } from '@/utils/errorHandler'

export default {
  setup() {
    const error = ref('')
    const isLoading = ref(false)
    
    const loadComponent = async () => {
      try {
        isLoading.value = true
        error.value = ''
        
        await retry(() => {
          return fh2Service.loadProject('project-container')
        }, {
          maxRetries: 3,
          retryDelay: 2000
        })
      } catch (err) {
        error.value = formatFH2Error(err)
      } finally {
        isLoading.value = false
      }
    }
    
    onMounted(() => {
      loadComponent()
    })
    
    return {
      error,
      isLoading,
      loadComponent
    }
  }
}
</script>
```

### 12.3 如何在 Vue 项目中使用深色主题？

可以通过切换 body 的 CSS 类来实现主题切换：

```vue
<script>
import { ref, watch } from 'vue'
import fh2Service from '@/services/fh2Service'

export default {
  setup() {
    const isDarkTheme = ref(false)
    
    watch(isDarkTheme, (newValue) => {
      fh2Service.toggleTheme(newValue)
      // 可以在这里保存主题设置到本地存储
      localStorage.setItem('fh2-theme', newValue ? 'dark' : 'light')
    }, { immediate: true })
    
    // 从本地存储恢复主题设置
    const savedTheme = localStorage.getItem('fh2-theme')
    if (savedTheme) {
      isDarkTheme.value = savedTheme === 'dark'
    }
    
    return {
      isDarkTheme
    }
  }
}
</script>
```

通过以上指南和示例代码，开发者可以在 Vue 项目中成功集成大疆司空2的前端组件，实现项目地图、驾驶舱、航线编辑器和航线创建等功能。正确的组件封装和生命周期管理将确保应用的性能和稳定性。