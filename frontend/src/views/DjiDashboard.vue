<template>
  <div class="dashboard-premium">
    <!-- 页面头部 -->
    <div class="dashboard-header">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="3" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
          <rect x="14" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
          <rect x="3" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
          <rect x="14" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
        </svg>
      </div>
      <div class="header-text">
        <h1 class="page-title">无人机巡检主控台</h1>
        <p class="page-subtitle">实时监控与任务管理</p>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="dashboard-content">
      <!-- 左侧面板 - 航线管理 -->
      <div class="side-panel left-panel">

        <div class="panel-body compact-panel">
          <WaylineFallback 
            :current-selected-id="selectedWayline?.id"
            @wayline-selected="handleWaylineSelected"
          />
        </div>
      </div>

      <!-- 中间区域 - 3D视图和进度 -->
      <div class="main-view">
        <!-- 任务进度条 -->
        <div class="progress-section">
          <TaskProgressBar 
            :progress="taskProgress"
            :current-task="currentTask"
            :remaining-time="remainingTime"
            :completed-tasks="completedTasks"
            :total-tasks="totalTasks"
          />
        </div>

        <!-- Cesium 3D视图 -->
        <div class="cesium-section">
          <div class="cesium-controls">
            <button class="control-btn" @click="focusOnModel">定位模型</button>
            <button class="control-btn" @click="resetCameraView">重置视角</button>
            <button class="control-btn" @click="toggleGlobe">{{ globeVisible ? '隐藏地球' : '显示地球' }}</button>
          </div>
          <!-- 直接使用ref作为Cesium容器 -->
          <div ref="cesiumContainer" class="cesium-container">
            <!-- 加载指示器 -->
            <div v-if="loading" class="loading-overlay">
              <div class="loading-content">
                <div class="loading-spinner"></div>
                <span>正在加载3D模型...</span>
              </div>
            </div>

            <!-- 错误信息 -->
            <div v-else-if="error" class="error-overlay">
              <div class="error-content">
                <div class="error-icon">⚠️</div>
                <p>{{ error }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧面板 - 告警信息 -->
      <div class="side-panel right-panel">
        <!-- 告警信息面板 -->
        <div class="panel-section">
          <div class="panel-body alarm-panel-body">
            <AlarmPanel 
              v-if="selectedWayline"
              :alarms="getFilteredAlarms()"
              :loading="loadingAlarms"
              @refresh="handleAlarmRefresh"
              @view-detail="handleViewAlarmDetail"
              @process-alarm="handleProcessAlarm"
              @locate-alarm="handleLocateAlarm"
            />
            <div v-else class="dji-placeholder">
              <p>请先选择航线查看告警信息</p>
            </div>
          </div>
        </div>

        <!-- 实时监控面板（大疆二开组件位） -->
        <div class="panel-section">
          <div class="panel-header">
            <h3 class="panel-title">实时监控</h3>
          </div>
          <div class="panel-body monitor-body">
            <p class="placeholder-text">实时监控将在这里显示（由大疆组件提供）</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 告警详情弹窗 -->
    <div v-if="showAlarmDetail" class="modal-overlay" @click.self="showAlarmDetail = false">
      <div class="modal-premium">
        <div class="modal-header">
          <h3 class="modal-title">告警详情</h3>
          <button @click="showAlarmDetail = false" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div v-if="currentAlarm" class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">告警ID</span>
              <span class="detail-value">{{ currentAlarm.id }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">告警类型</span>
              <span class="detail-value">{{ currentAlarm.category_details?.name || '未分类' }}</span>
            </div>
            <div class="detail-item full-width">
              <span class="detail-label">告警描述</span>
              <span class="detail-value">{{ currentAlarm.content }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">告警时间</span>
              <span class="detail-value">{{ formatAlarmTime(currentAlarm.created_at) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">告警位置</span>
              <span class="detail-value">坐标({{ currentAlarm.latitude }}, {{ currentAlarm.longitude }})</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">航线信息</span>
              <span class="detail-value">{{ currentAlarm.wayline?.name || currentAlarm.wayline_details?.name || '未知航线' }}</span>
            </div>
            <div v-if="currentAlarm.image_url" class="detail-item full-width">
              <span class="detail-label">告警图片</span>
              <div class="alarm-image">
                <img :src="currentAlarm.image_url" alt="告警图片" />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showAlarmDetail = false" class="modal-btn secondary-btn">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TaskProgressBar from '../components/TaskProgressBar.vue'
import AlarmPanel from '../components/AlarmPanel.vue'
import WaylineFallback from '../components/WaylineFallback.vue'
import alarmApi from '../api/alarmApi.js'
import componentConfigApi from '../api/componentConfigApi.js'

export default {
  name: 'DjiDashboard',
  components: {
    TaskProgressBar,
    AlarmPanel,
    WaylineFallback
  },
  data() {
    return {
      taskProgress: 65,
      currentTask: '变电站设备检查',
      remainingTime: '12:45',
      completedTasks: 8,
      totalTasks: 12,
      cesiumLib: null,
      viewer: null,
      tileset: null,
      loading: false,
      error: '',
      globeVisible: true,
      imageryProviderType: 'aerial',
      fh2Loaded: false,
      waylineEntity: null,
      alarmEntities: [],
      pickHandler: null,
      selectedWayline: null,
      alarms: [],
      loadingAlarms: false,
      showAlarmDetail: false,
      currentAlarm: null,
      fh2CheckTimer: null,
      componentConfig: null
    }
  },
  mounted() {
    this.checkFh2Availability()
    // 等待DOM完全渲染后再初始化Cesium
    this.$nextTick(() => {
      // 使用setTimeout确保布局计算完成
      setTimeout(async () => {
        await this.loadComponentConfig()
        this.initCesium()
      }, 500)
    })
  },
  beforeUnmount() {
    if (this.fh2CheckTimer) {
      clearTimeout(this.fh2CheckTimer)
      this.fh2CheckTimer = null
    }
    if (this.viewer) {
      this.viewer.destroy()
      this.viewer = null
    }
    if (this.pickHandler) {
      this.pickHandler.destroy()
      this.pickHandler = null
    }
  },
  methods: {
    checkFh2Availability() {
      if (typeof window !== 'undefined' && window.FH2) {
        this.fh2Loaded = true
        this.fh2CheckTimer = null
        return
      }

      this.fh2Loaded = false
      this.fh2CheckTimer = setTimeout(() => {
        this.checkFh2Availability()
      }, 1000)
    },
    
    async initCesium() {
      if (this.viewer) return

      this.loading = true
      this.error = ''
      try {
        const Cesium = await import('cesium')
        this.cesiumLib = Cesium
        const tokenFromConfig = this.componentConfig?.cesium_ion_token || this.componentConfig?.cesiumIonToken
        Cesium.Ion.defaultAccessToken =
          tokenFromConfig || process.env.VUE_APP_CESIUM_ION_TOKEN || Cesium.Ion.defaultAccessToken || ''
        
        const container = this.$refs.cesiumContainer
        if (!container) {
          throw new Error('找不到 Cesium 容器')
        }
        
        const rect = container.getBoundingClientRect()
        if (rect.width === 0 || rect.height === 0) {
          throw new Error(`容器尺寸异常: ${rect.width}x${rect.height}`)
        }
        
        // 直接在ref容器上创建Cesium Viewer
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
          scene3DOnly: true,
          creditContainer: document.createElement('div')
        })
        
        this.viewer.scene.globe.show = this.globeVisible
        await this.setupImageryLayers(Cesium)
        this.tuneCameraControls(this.viewer.scene.screenSpaceCameraController)
        this.setupPickHandler(Cesium)

        // 强制resize确保canvas正确渲染
        this.viewer.resize()
        
        // 加载3D Tiles模型
        try {
          this.tileset = await Cesium.Cesium3DTileset.fromUrl('/models/Model_0/tileset.json')
          this.viewer.scene.primitives.add(this.tileset)
          
          // 等待tileset加载完成
          await this.tileset.readyPromise
          
          // 自动缩放到模型并调整视角
          await this.viewer.zoomTo(this.tileset, new Cesium.HeadingPitchRange(
            0, // heading (朝向)
            Cesium.Math.toRadians(-30), // pitch (俯仰角，负数向下)
            this.tileset.boundingSphere.radius * 2.5 // range (距离)
          ))
          
          // 再次resize确保显示正确
          this.viewer.resize()
        } catch (tilesetError) {
          console.error('加载3D Tiles模型失败:', tilesetError)
          // 如果模型加载失败，设置默认相机位置
          this.viewer.camera.setView({
            destination: Cesium.Cartesian3.fromDegrees(116.3913, 39.9075, 1000),
            orientation: {
              heading: Cesium.Math.toRadians(0),
              pitch: Cesium.Math.toRadians(-30),
              roll: 0.0
            }
          })
        }
      } catch (err) {
        this.error = '初始化Cesium失败: ' + err.message
        console.error('Cesium initialization error:', err)
      } finally {
        this.loading = false
      }
    },
    
    handleWaylineSelected(wayline) {
      this.selectedWayline = wayline
      this.fetchAlarmsByWayline(wayline.id)
      this.ensureWaylineWithPoints(wayline)
    },

    async loadComponentConfig() {
      try {
        this.componentConfig = await componentConfigApi.getConfig()
      } catch (err) {
        console.warn('获取组件配置失败，将使用默认配置', err)
      }
    },

    async setupImageryLayers(Cesium) {
      if (!this.viewer) return
      const layers = this.viewer.imageryLayers
      layers.removeAll()
      try {
        const provider = await Cesium.IonImageryProvider.fromAssetId(2)
        layers.addImageryProvider(provider)
      } catch (e) {
        console.warn('Ion 底图加载失败，改用 OSM', e)
        layers.addImageryProvider(
          new Cesium.OpenStreetMapImageryProvider({
            url: 'https://a.tile.openstreetmap.org/'
          })
        )
      }
    },

    tuneCameraControls(controller) {
      if (!controller) return
      controller.inertiaSpin = 0.4
      controller.inertiaTranslate = 0.4
      controller.inertiaZoom = 0.4
      controller.minimumZoomRate = 0.2
      controller.maximumZoomRate = 500000
      controller._zoomFactor = 1.5
    },
    
    async fetchAlarmsByWayline(waylineId) {
      if (!waylineId) {
        this.alarms = []
        this.clearAlarmMarkers()
        return
      }
      
      this.loadingAlarms = true
      try {
        const response = await alarmApi.getAlarms({ wayline_id: waylineId })
        this.alarms = Array.isArray(response) ? response : (response.results || [])
        this.plotAlarmMarkers(this.alarms)
      } catch (error) {
        console.error('获取告警信息失败:', error)
        this.alarms = []
        this.clearAlarmMarkers()
      } finally {
        this.loadingAlarms = false
      }
    },
    
    getFilteredAlarms() {
      return this.alarms
    },
    
    handleAlarmRefresh() {
      if (this.selectedWayline) {
        this.fetchAlarmsByWayline(this.selectedWayline.id)
      }
      // 保持标记与最新数据同步
      if (this.alarms.length) {
        this.plotAlarmMarkers(this.alarms)
      }
    },

    handleLocateAlarm(alarm) {
      const lat = this.toNumber(alarm?.latitude)
      const lon = this.toNumber(alarm?.longitude)
      if (!Number.isFinite(lat) || !Number.isFinite(lon) || !this.viewer) return
      const Cesium = this.cesiumLib || window.Cesium
      if (!Cesium) return
      const height = this.toNumber(alarm?.altitude) || 200
      const destination = Cesium.Cartesian3.fromDegrees(lon, lat, height)
      const flyPromise = this.viewer.camera.flyTo({
        destination,
        orientation: {
          heading: Cesium.Math.toRadians(0),
          pitch: Cesium.Math.toRadians(-45),
          roll: 0.0
        },
        duration: 1.2
      })
      if (flyPromise && typeof flyPromise.catch === 'function') {
        flyPromise.catch(() => {})
      }
    },
    plotAlarmMarkers(alarms) {
      if (!this.viewer) return
      const Cesium = this.cesiumLib || window.Cesium
      if (!Cesium) return
      this.clearAlarmMarkers()
      const entities = []
      const pinBuilder = (Cesium.PinBuilder) ? new Cesium.PinBuilder() : null
      const pinCanvas = pinBuilder ? pinBuilder.fromColor(Cesium.Color.ORANGE, 32) : null
      alarms.forEach(alarm => {
        const lat = this.toNumber(alarm.latitude)
        const lon = this.toNumber(alarm.longitude)
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return
        const position = Cesium.Cartesian3.fromDegrees(lon, lat, this.toNumber(alarm.altitude) || 0)
        const entity = this.viewer.entities.add({
          position,
          alarmData: alarm,
          point: {
            pixelSize: 12,
            color: Cesium.Color.ORANGE.withAlpha(0.95),
            outlineColor: Cesium.Color.BLACK,
            outlineWidth: 2,
            disableDepthTestDistance: Number.POSITIVE_INFINITY
          },
          billboard: {
            image: pinCanvas || undefined,
            width: 32,
            height: 32,
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            disableDepthTestDistance: Number.POSITIVE_INFINITY
          },
          label: {
            text: alarm.id ? String(alarm.id) : '报警',
            font: '14px sans-serif',
            fillColor: Cesium.Color.WHITE,
            outlineColor: Cesium.Color.BLACK,
            outlineWidth: 2,
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            pixelOffset: new Cesium.Cartesian2(0, -28),
            disableDepthTestDistance: Number.POSITIVE_INFINITY
          }
        })
        entities.push(entity)
      })
      this.alarmEntities = entities
    },

    clearAlarmMarkers() {
      if (this.viewer && this.alarmEntities.length) {
        this.alarmEntities.forEach(e => this.viewer.entities.remove(e))
      }
      this.alarmEntities = []
    },

    setupPickHandler(Cesium) {
      if (!this.viewer || this.pickHandler) return
      this.pickHandler = new Cesium.ScreenSpaceEventHandler(this.viewer.scene.canvas)
      this.pickHandler.setInputAction(click => {
        const picked = this.viewer.scene.pick(click.position)
        if (Cesium.defined(picked) && picked.id && picked.id.alarmData) {
          this.currentAlarm = picked.id.alarmData
          this.showAlarmDetail = true
        }
      }, Cesium.ScreenSpaceEventType.LEFT_CLICK)
    },

    toNumber(val) {
      const num = Number(val)
      return Number.isFinite(num) ? num : NaN
    },

    async ensureWaylineWithPoints(wayline) {
      const hasPoints = Array.isArray(wayline?.waypoints) && wayline.waypoints.length > 0
      let finalWayline = wayline
      if (!hasPoints && wayline?.id) {
        try {
          const detail = await alarmApi.getWaylineDetail(wayline.id)
          finalWayline = (detail && detail.id) ? detail : wayline
        } catch (err) {
          console.warn('获取航线详情失败，使用已选航线基本信息', err)
        }
      }
      this.drawWaylineOnMap(finalWayline)
    },

    drawWaylineOnMap(wayline) {
      if (!this.viewer || !wayline?.waypoints?.length) {
        return
      }
      const Cesium = this.cesiumLib || window.Cesium
      if (!Cesium) return

      // 清理旧的路径
      if (this.waylineEntity) {
        this.viewer.entities.remove(this.waylineEntity)
        this.waylineEntity = null
      }

      const positions = wayline.waypoints
        .filter(p => p.longitude !== undefined && p.latitude !== undefined)
        .map(p => Cesium.Cartesian3.fromDegrees(p.longitude, p.latitude, p.height || 0))

      if (!positions.length) return

      this.waylineEntity = this.viewer.entities.add({
        name: wayline.name || '航线',
        polyline: {
          positions,
          width: 6,
          material: Cesium.Color.YELLOW.withAlpha(0.9),
          clampToGround: false
        }
      })

      // 定位到路径
      const sphere = Cesium.BoundingSphere.fromPoints(positions)
      this.viewer.camera.flyToBoundingSphere(sphere, {
        duration: 1.2,
        offset: new Cesium.HeadingPitchRange(0, Cesium.Math.toRadians(-20), sphere.radius * 3)
      })
    },

    focusOnModel() {
      if (this.viewer && this.tileset) {
        const Cesium = this.cesiumLib || window.Cesium
        if (!Cesium) return
        const range = (this.tileset.boundingSphere?.radius || 1000) * 2.5
        this.viewer.flyTo(this.tileset, {
          offset: new Cesium.HeadingPitchRange(0, Cesium.Math.toRadians(-30), range)
        }).catch(err => {
          console.warn('飞到模型失败', err)
        })
      } else if (this.viewer && this.waylineEntity) {
        const Cesium = this.cesiumLib || window.Cesium
        if (!Cesium) return
        const positions = this.waylineEntity.polyline.positions.getValue(new Cesium.JulianDate())
        const sphere = Cesium.BoundingSphere.fromPoints(positions)
        this.viewer.camera.flyToBoundingSphere(sphere, {
          duration: 1.2,
          offset: new Cesium.HeadingPitchRange(0, Cesium.Math.toRadians(-20), sphere.radius * 3)
        })
      }
    },

    resetCameraView() {
      if (this.viewer) {
        const Cesium = this.cesiumLib || window.Cesium
        if (!Cesium) return

        // 优先定位到当前航线起点
        if (this.waylineEntity?.polyline?.positions) {
          const positions = this.waylineEntity.polyline.positions.getValue(new Cesium.JulianDate())
          const first = Array.isArray(positions) && positions.length ? positions[0] : null
          if (first) {
            this.viewer.camera.flyTo({
              destination: first,
              orientation: {
                heading: Cesium.Math.toRadians(0),
                pitch: Cesium.Math.toRadians(-45),
                roll: 0.0
              },
              duration: 1.2
            })
            return
          }
        }

        // 退回模型中心
        if (this.tileset?.boundingSphere) {
          const range = (this.tileset.boundingSphere.radius || 1000) * 3
          this.viewer.camera.flyTo({
            destination: this.tileset.boundingSphere.center,
            orientation: {
              heading: Cesium.Math.toRadians(0),
              pitch: Cesium.Math.toRadians(-20),
              roll: 0.0
            },
            duration: 1.5,
            maximumHeight: range
          })
        }
      }
    },

    toggleGlobe() {
      this.globeVisible = !this.globeVisible
      if (this.viewer) {
        this.viewer.scene.globe.show = this.globeVisible
      }
    },
    
    handleViewAlarmDetail(alarm) {
      this.currentAlarm = alarm
      this.showAlarmDetail = true
    },
    
    async handleProcessAlarm(alarmId) {
      try {
        await alarmApi.patchAlarm(alarmId, { status: 'COMPLETED' })
        this.alarms = this.alarms.filter(alarm => alarm.id !== alarmId)
      } catch (error) {
        console.error('更新告警状态失败:', error)
      }
    },
    
    formatAlarmTime(timestamp) {
      if (!timestamp) return '--'
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.dashboard-premium {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  box-sizing: border-box;
  background: radial-gradient(circle at 20% 20%, rgba(0, 212, 255, 0.08), transparent 25%),
              radial-gradient(circle at 80% 0, rgba(0, 153, 255, 0.06), transparent 30%),
              #0b1024;
  color: #e2e8f0;
  overflow: hidden;
}

/* 页面头部 */
.dashboard-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px 32px;
  background: rgba(26, 31, 58, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(0, 212, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 16px rgba(0, 212, 255, 0.4);
}

.header-icon svg {
  width: 28px;
  height: 28px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 4px 0;
}

.page-subtitle {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
}

/* 主内容区 */
.dashboard-content {
  flex: 1;
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  gap: 24px;
  min-height: 0;
  overflow: hidden;
}

/* 侧边面板 */
.side-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
}

.panel-section {
  background: rgba(26, 31, 58, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(0, 212, 255, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 153, 255, 0.15) 100%);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.panel-title {
  font-size: 16px;
  font-weight: 700;
  color: #00d4ff;
  margin: 0;
}

.wayline-badge {
  padding: 4px 12px;
  background: rgba(0, 212, 255, 0.2);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 12px;
  color: #00d4ff;
  font-size: 12px;
  font-weight: 600;
}

.panel-body {
  flex: 1;
  overflow: hidden;
  min-height: 0;
}
.compact-panel {
  padding: 0;
}

.alarm-panel-body {
  max-height: 400px;
}

.monitor-body {
  padding: 40px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 150px;
}

.placeholder-text {
  color: #64748b;
  font-size: 14px;
  text-align: center;
  margin: 0;
}

.dji-placeholder {
  padding: 40px 20px;
  text-align: center;
  color: #64748b;
}

/* 中间主视图 */
.main-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
  overflow: hidden;
}

.progress-section {
  flex-shrink: 0;
}

.cesium-section {
  flex: 1;
  min-height: 500px;
  background: rgba(26, 31, 58, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(0, 212, 255, 0.2);
  overflow: hidden;
  position: relative;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.cesium-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.cesium-controls {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 8px;
  z-index: 5;
}

.control-btn {
  padding: 8px 12px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 10px;
  background: rgba(26, 31, 58, 0.8);
  color: #e0f2fe;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.control-btn:hover {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.5);
}

/* 加载和错误覆盖层 */
.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(10, 14, 39, 0.9);
  backdrop-filter: blur(10px);
  z-index: 10;
}

.loading-content,
.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: #e2e8f0;
  font-size: 16px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(0, 212, 255, 0.2);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-icon {
  font-size: 48px;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(10, 14, 39, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.modal-premium {
  background: rgba(26, 31, 58, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  box-shadow: 0 16px 64px rgba(0, 0, 0, 0.5);
  width: 100%;
  max-width: 700px;
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 153, 255, 0.1) 100%);
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #00d4ff;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.modal-close:hover {
  background: rgba(239, 68, 68, 0.3);
  transform: rotate(90deg);
}

.modal-body {
  padding: 24px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  color: #94a3b8;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  color: #e2e8f0;
  font-size: 14px;
}

.alarm-image {
  margin-top: 8px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(0, 212, 255, 0.2);
}

.alarm-image img {
  width: 100%;
  height: auto;
  display: block;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(0, 212, 255, 0.1);
}

.modal-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.secondary-btn {
  background: rgba(100, 116, 139, 0.3);
  color: #e2e8f0;
  border: 1px solid rgba(100, 116, 139, 0.5);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.secondary-btn:hover {
  background: rgba(100, 116, 139, 0.4);
  transform: translateY(-1px);
}

@media (max-width: 1180px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }

  .side-panel {
    order: 2;
  }

  .main-view {
    order: 1;
  }

  .alarm-panel-body {
    max-height: none;
  }
}
</style>

<style>
/* 强制覆盖Cesium默认样式，确保充满容器 */
.cesium-viewer,
.cesium-viewer-cesiumWidgetContainer,
.cesium-widget,
.cesium-widget canvas {
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}
</style>
