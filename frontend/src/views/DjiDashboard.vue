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
        <div class="panel-header">
          <h3 class="panel-title">航线管理</h3>
        </div>
        <div class="panel-body">
          <WaylineFallback 
            v-if="!fh2Loaded" 
            :current-selected-id="selectedWayline?.id"
            @wayline-selected="handleWaylineSelected"
          />
          <div v-else class="dji-placeholder">
            <p>航线列表将在这里显示（由大疆组件提供）</p>
          </div>
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
          <div ref="cesiumWrapper" class="cesium-container">
            <!-- 加载指示器 -->
            <div v-if="loading" class="loading-overlay">
              <div class="loading-content">
                <div class="loading-spinner"></div>
                <span>正在加载模型...</span>
              </div>
            </div>

            <!-- 错误信息 -->
            <div v-if="error" class="error-overlay">
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
          <div class="panel-header">
            <h3 class="panel-title">报警信息</h3>
            <span v-if="selectedWayline" class="wayline-badge">
              {{ selectedWayline.name }}
            </span>
          </div>
          <div class="panel-body alarm-panel-body">
            <div v-if="loadingAlarms" class="loading-state">
              <div class="loading-spinner small"></div>
              <p>加载中...</p>
            </div>
            <AlarmPanel 
              v-else
              :alarms="getFilteredAlarms()"
              @refresh="handleAlarmRefresh"
              @view-detail="handleViewAlarmDetail"
              @process-alarm="handleProcessAlarm"
            />
          </div>
        </div>

        <!-- 实时监控 -->
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
      viewer: null,
      tileset: null,
      loading: false,
      error: '',
      fh2Loaded: false,
      selectedWayline: null,
      alarms: [],
      loadingAlarms: false,
      showAlarmDetail: false,
      currentAlarm: null
    }
  },
  async mounted() {
    this.checkFh2Availability()
    this.$nextTick(async () => {
      setTimeout(async () => {
        await this.initCesium()
      }, 200)
    })
  },
  methods: {
    checkFh2Availability() {
      if (typeof window.FH2 !== 'undefined') {
        this.fh2Loaded = true
      } else {
        this.fh2Loaded = false
        setTimeout(() => {
          this.checkFh2Availability()
        }, 1000)
      }
    },
    
    async initCesium() {
      try {
        const Cesium = await import('cesium')
        Cesium.Ion.defaultAccessToken = ''
        
        const wrapper = this.$refs.cesiumWrapper
        if (!wrapper) {
          throw new Error('找不到 cesiumWrapper 元素')
        }
        
        const container = document.createElement('div')
        container.id = 'cesiumContainer'
        container.style.width = '100%'
        container.style.height = '100%'
        container.style.position = 'absolute'
        wrapper.appendChild(container)
        
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
    
    handleWaylineSelected(wayline) {
      this.selectedWayline = wayline
      this.fetchAlarmsByWayline(wayline.id)
    },
    
    async fetchAlarmsByWayline(waylineId) {
      if (!waylineId) {
        this.alarms = []
        return
      }
      
      this.loadingAlarms = true
      try {
        const response = await alarmApi.getAlarms({ wayline_id: waylineId })
        this.alarms = Array.isArray(response) ? response : (response.results || [])
      } catch (error) {
        console.error('获取告警信息失败:', error)
        this.alarms = []
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
  },
  beforeUnmount() {
    if (this.viewer) {
      this.viewer.destroy()
    }
  }
}
</script>

<style scoped>
.dashboard-premium {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 24px;
  gap: 24px;
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
}

/* 侧边面板 */
.side-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
}

.progress-section {
  flex-shrink: 0;
}

.cesium-section {
  flex: 1;
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
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(0, 212, 255, 0.2);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-spinner.small {
  width: 32px;
  height: 32px;
  border-width: 3px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-icon {
  font-size: 48px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #94a3b8;
  gap: 12px;
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
  background: rgba(100, 116, 139, 0.2);
  color: #94a3b8;
  border: 1px solid rgba(100, 116, 139, 0.3);
}

.secondary-btn:hover {
  background: rgba(100, 116, 139, 0.3);
}

/* Cesium容器 */
#cesiumContainer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

/* 响应式 */
@media (max-width: 1400px) {
  .dashboard-content {
    grid-template-columns: 250px 1fr 280px;
  }
}

@media (max-width: 1200px) {
  .dashboard-content {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
  }
  
  .side-panel {
    flex-direction: row;
  }
  
  .panel-section {
    flex: 1;
  }
}
</style>