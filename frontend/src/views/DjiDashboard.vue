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
      <!-- 左侧面板 - 机场列表 -->
      <div class="side-panel left-panel">
        <div class="panel-section dock-panel">
          <div class="panel-header">
            <h3 class="panel-title">机场列表</h3>
            <button class="panel-action" @click="loadDockList" :disabled="dockLoading">
              {{ dockLoading ? '加载中...' : '刷新' }}
            </button>
          </div>
          <div class="panel-body dock-panel-body">
            <div v-if="dockLoading && docks.length === 0" class="panel-placeholder">正在加载机场...</div>
            <div v-else-if="dockLoadError" class="panel-placeholder error">{{ dockLoadError }}</div>
            <div v-else-if="docks.length === 0" class="panel-placeholder">暂无机场数据</div>
            <ul v-else class="dock-list">
              <li
                  v-for="dock in docks"
                  :key="dock.id || dock.dock_sn"
                  class="dock-item"
                  :class="{ active: isDockSelected(dock) }"
                  @click="handleDockSelected(dock)"
              >
                <div class="dock-item-header">
                  <div class="dock-item-name">
                    <span class="status-dot" :class="{ online: dock.is_online }"></span>
                    <span class="dock-name">{{ getDockDisplayName(dock) }}</span>
                  </div>
                  <span class="dock-status" :class="{ online: dock.is_online }">
                    {{ dock.is_online ? '在线' : '离线' }}
                  </span>
                </div>
                <div class="dock-item-meta">
                  <span class="dock-sn">SN {{ dock.dock_sn || '--' }}</span>
                  <span v-if="dock.drone_sn" class="drone-sn">无人机 {{ dock.drone_sn }}</span>
                  <span class="drone-state" :class="{ working: isDroneWorking(dock) }">
                    {{ getDroneStateLabel(dock) }}
                  </span>
                </div>
              </li>
            </ul>

            <div class="dock-latest">
              <div class="dock-latest-header">
                <span class="dock-latest-title">最新位置</span>
                <div class="dock-latest-tags" v-if="selectedDock">
                  <span v-if="selectedDock?.drone_sn" class="dock-latest-sn">{{ selectedDock.drone_sn }}</span>
                  <span class="dock-latest-state" :class="{ working: isDroneWorking(selectedDock) }">
                    {{ getDroneStateLabel(selectedDock) }}
                  </span>
                </div>
              </div>
              <div v-if="!selectedDock" class="panel-placeholder small">请选择机场</div>
              <div v-else-if="!selectedDock.drone_sn" class="panel-placeholder small">该机场未绑定无人机</div>
              <div v-else-if="positionLoading && latestPositions.length === 0" class="panel-placeholder small">读取中...</div>
              <div v-else-if="latestPositions.length === 0" class="panel-placeholder small">暂无位置数据</div>
              <div v-else class="position-list">
                <div
                    v-for="(pos, index) in latestPositions"
                    :key="pos.id || pos.timestamp || index"
                    class="position-item"
                >
                  <div class="position-row">
                    <span class="position-label">时间</span>
                    <span class="position-value">{{ formatPositionTime(pos.timestamp || pos.created_at) }}</span>
                  </div>
                  <div class="position-row">
                    <span class="position-label">坐标</span>
                    <span class="position-value">{{ formatPositionCoords(pos) }}</span>
                  </div>
                  <div class="position-row">
                    <span class="position-label">高度</span>
                    <span class="position-value">{{ formatPositionAltitude(pos) }}</span>
                  </div>
                  <div v-if="pos.battery_percent !== null && pos.battery_percent !== undefined" class="position-row">
                    <span class="position-label">电量</span>
                    <span class="position-value">{{ pos.battery_percent }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="panel-section alarm-panel">
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

      </div>

      <!-- 中间区域 - 3D视图和直播 -->
      <div class="main-view">
        <div class="viewer-grid">
        <!-- Cesium 3D视图 -->
        <div class="cesium-section">
          <div class="cesium-controls">
            <button class="control-btn" @click="focusOnModel">定位模型</button>
            <button class="control-btn" @click="focusOnWayline">定位航线</button>
            <button
              class="control-btn"
              :class="{ 'is-active': cameraMode === 'bird' }"
              @click="setCameraMode('bird')"
            >
              鸟瞰视角
            </button>
            <button
              class="control-btn"
              :class="{ 'is-active': cameraMode === 'third' }"
              @click="setCameraMode('third')"
            >
              第三人称
            </button>
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
            <div v-if="showCreateTaskButton" class="create-task-overlay">
              <button class="create-task-button" @click="openCreateTaskDialog">创建任务</button>
            </div>
          </div>
        </div>
        <!-- 实时监控面板（直播流播放器） -->
        <div class="panel-section live-monitor-section">
          <div class="monitor-header">
            <span class="monitor-title">实时直播</span>
            <div class="monitor-actions">
              <div class="stream-toggle">
                <button
                  class="stream-btn"
                  :class="{ active: liveStreamType === 'airport' }"
                  :disabled="!airportPushUrl"
                  @click="setLiveStreamType('airport')"
                >
                  机场直播
                </button>
                <button
                  class="stream-btn"
                  :class="{ active: liveStreamType === 'drone' }"
                  :disabled="!dronePushUrl"
                  @click="setLiveStreamType('drone')"
                >
                  无人机直播
                </button>
              </div>
              <div class="monitor-commands">
                <button
                  class="command-btn warning"
                  :disabled="!selectedDockSn || commandLoading.returnHome"
                  @click="handleReturnHome"
                >
                  {{ commandLoading.returnHome ? '返航中...' : '返航' }}
                </button>
                <button
                  class="command-btn default"
                  :disabled="!selectedDockSn || commandLoading.cancelReturn"
                  @click="handleCancelReturn"
                >
                  {{ commandLoading.cancelReturn ? '取消中...' : '取消返航' }}
                </button>
                <button
                  class="command-btn info"
                  :disabled="!selectedDockSn || commandLoading.pause"
                  @click="handlePause"
                >
                  {{ commandLoading.pause ? '暂停中...' : '暂停' }}
                </button>
                <button
                  class="command-btn success"
                  :disabled="!selectedDockSn || commandLoading.resume"
                  @click="handleResume"
                >
                  {{ commandLoading.resume ? '恢复中...' : '恢复' }}
                </button>
              </div>
            </div>
          </div>
          <div class="live-player-wrapper">
            <LiveStreamPlayer
                :key="`${liveStreamType}-${currentLiveStreamId}-${currentLiveStreamUrl}`"
                :stream-id="currentLiveStreamId"
                :stream-name="currentLiveStreamName"
                :stream-url-override="currentLiveStreamUrl"
                :zlm-server="zlmServerUrl"
                :auto-play="true"
            />
          </div>
        </div>
        </div>
      </div>

    </div>

    <CreateFlightTaskDialog
      v-model="showCreateTaskDialog"
      :sn="selectedDockSn"
      :dock-name="selectedDockName"
    />

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
            <div v-if="currentAlarm.image_signed_url || currentAlarm.image_url" class="detail-item full-width">
              <span class="detail-label">告警图片</span>
              <div class="alarm-image">
                <img
                  :src="currentAlarm.image_signed_url || currentAlarm.image_url"
                  alt="告警图片"
                  @error="handleImageError"
                />
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
import AlarmPanel from '../components/AlarmPanel.vue'
import LiveStreamPlayer from '../components/LiveStreamPlayer.vue'
import CreateFlightTaskDialog from '../components/CreateFlightTaskDialog.vue'
import alarmApi from '../api/alarmApi.js'
import waylineApi from '../api/waylineApi.js'
import componentConfigApi from '../api/componentConfigApi.js'
import dockStatusApi from '../api/dockStatusApi.js'
import dronePositionApi from '../api/dronePositionApi.js'
import flightTaskInfoApi from '../api/flightTaskInfoApi.js'
import flightTaskApi from '../api/flightTaskApi.js'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'DjiDashboard',
  components: {
    AlarmPanel,
    LiveStreamPlayer,
    CreateFlightTaskDialog
  },
  data() {
    return {
      detectTypes: [
        { name: '铁路', code: 'rail', icon: '🛤️', keywords: 'rail, 铁路, 轨道' },
        { name: '接触网', code: 'contactline', icon: '⚡', keywords: 'contactline, 接触网, catenary, overhead' },
        { name: '桥梁', code: 'bridge', icon: '🌉', keywords: 'bridge, 桥梁' },
        { name: '保护区', code: 'protected_area', icon: '🛡️', keywords: 'protected_area, 保护区' }
      ],
      loading: false,
      error: '',
      globeVisible: true,
      cameraMode: 'third',
      imageryProviderType: 'aerial',
      fh2Loaded: false,
      selectedWayline: null,
      alarms: [],
      loadingAlarms: false,
      showAlarmDetail: false,
      currentAlarm: null,
      fh2CheckTimer: null,
      componentConfig: null,
      zlmServerUrl: 'http://192.168.10.10',
      liveStreamType: 'airport',
      showCreateTaskDialog: false,
      commandLoading: {
        returnHome: false,
        cancelReturn: false,
        pause: false,
        resume: false
      },
      actionDetails: [],
      waylinePointSource: '',
      docks: [],
      dockLoading: false,
      dockLoadError: '',
      dockPollTimer: null,
      selectedDock: null,
      latestPositions: [],
      positionLoading: false,
      positionPollTimer: null,
      positionPollingDeviceSn: '',
      lastDroneTimestamp: null,
      lastDroneHeading: null,
      lastDronePosition: null,
      currentWaylineUuid: '',
      lastTaskInfoAttempt: 0,
      lastTaskInfoSn: '',
      taskInfoFetchInFlight: false,
      waylineFetchInFlight: false,
      chaseCameraListener: null
    }
  },
  computed: {
    selectedDockSn() {
      return this.selectedDock?.dock_sn || ''
    },
    selectedDockName() {
      return this.selectedDock?.display_name || this.selectedDock?.dock_name || this.selectedDock?.dock_sn || ''
    },
    showCreateTaskButton() {
      if (this.loading || this.error) return false
      if (!this.selectedDock || !this.selectedDockSn) return false
      return this.selectedDock.drone_in_dock === 1 || this.selectedDock.drone_in_dock === '1'
    },
    airportPushUrl() {
      return this.selectedDock?.airport_push || ''
    },
    dronePushUrl() {
      return this.selectedDock?.drone_push || ''
    },
    currentLiveStreamUrl() {
      return this.liveStreamType === 'drone' ? this.dronePushUrl : this.airportPushUrl
    },
    currentLiveStreamName() {
      return this.liveStreamType === 'drone' ? '无人机直播' : '机场直播'
    },
    currentLiveStreamId() {
      if (this.liveStreamType === 'drone') {
        return this.selectedDock?.drone_sn || this.selectedDock?.dock_sn || ''
      }
      return this.selectedDock?.dock_sn || ''
    }
  },
  created() {
    this.cesiumLib = null
    this.viewer = null
    this.tileset = null
    this.waylineEntity = null
    this.waylinePointEntities = []
    this.droneEntity = null
    this.lastDroneCartesian = null
    this.invertedTriangleImage = null
    this.alarmEntities = []
    this.actionDetailEntities = []
    this.pickHandler = null
  },
  mounted() {
    this.checkFh2Availability()
    this.initSelectedWaylineFromRoute()
    this.loadDockList()
    this.startDockPolling()
    this.$nextTick(() => {
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
    if (this.viewer && this.chaseCameraListener) {
      this.viewer.scene.postUpdate.removeEventListener(this.chaseCameraListener)
    }
    if (this.viewer) {
      this.viewer.destroy()
      this.viewer = null
    }
    if (this.pickHandler) {
      this.pickHandler.destroy()
      this.pickHandler = null
    }
    if (this.dockPollTimer) {
      clearInterval(this.dockPollTimer)
      this.dockPollTimer = null
    }
    if (this.positionPollTimer) {
      clearInterval(this.positionPollTimer)
      this.positionPollTimer = null
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
        if (!container) throw new Error('找不到 Cesium 容器')

        this.viewer = new Cesium.Viewer(container, {
          sceneMode: Cesium.SceneMode.SCENE3D,
          scene3DOnly: true,
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
          creditContainer: document.createElement('div')
        })

        this.viewer.scene.globe.depthTestAgainstTerrain = false;
        this.viewer.scene.screenSpaceCameraController.enableCollisionDetection = false;

        this.viewer.scene.globe.show = this.globeVisible
        await this.setupImageryLayers(Cesium)
        this.tuneCameraControls(this.viewer.scene.screenSpaceCameraController)
        this.setupPickHandler(Cesium)

        this.viewer.resize()
        const centerLon = 116.39;
        const centerLat = 39.90;

        this.viewer.camera.setView({
          destination: Cesium.Cartesian3.fromDegrees(centerLon, centerLat, 4000),
          orientation: {
            heading: 0,
            pitch: Cesium.Math.toRadians(-90),
            roll: 0
          }
        });

        try {
          this.tileset = await Cesium.Cesium3DTileset.fromUrl('/models/site_model/3dtiles/tileset.json')
          this.viewer.scene.primitives.add(this.tileset)
          await this.tileset.readyPromise
          await this.viewer.zoomTo(this.tileset, new Cesium.HeadingPitchRange(
              0,
              Cesium.Math.toRadians(-30),
              this.tileset.boundingSphere.radius * 2.5
          ))
          this.viewer.resize()
        } catch (tilesetError) {
          console.error('加载3D Tiles模型失败:', tilesetError)
        }
      } catch (err) {
        this.error = '初始化Cesium失败: ' + err.message
        console.error('Cesium initialization error:', err)
      } finally {
        this.loading = false
      }
    },

    async applyWaylineSelection(wayline) {
      if (!wayline?.id) return
      if (this.selectedWayline?.id === wayline.id) return
      console.log('[Dashboard] 航线更新:', wayline?.name, wayline?.id)
      this.selectedWayline = wayline

      // 1. 先加载告警
      this.fetchAlarmsByWayline(wayline.id)

      // 2. 获取动作详情 (用于蓝点/航线兜底)
      let validPoints = []
      try {
        const res = await waylineApi.getWaylineActionDetails(wayline.id)
        this.actionDetails = Array.isArray(res?.action_details) ? res.action_details : []
        validPoints = this.actionDetails

        this.plotActionDetailMarkers(this.actionDetails)
        console.log('[Debug] 成功获取动作详情点，数量:', validPoints.length)
      } catch (e) {
        console.warn('[Debug] 获取动作详情失败', e)
      }

      // 3. 使用当前航线绘制
      await this.ensureWaylineWithPoints(wayline, validPoints)
    },

// 核心数据解析：增加去重逻辑，防止 NaN
// 修改函数签名，增加 fallbackData 参数
    async ensureWaylineWithPoints(wayline, fallbackData = []) {
      console.log('----------------------------------------------------');
      console.log('[Debug] 开始构建航线，WaylineID:', wayline?.id);

      let finalWayline = { ...wayline };
      let sourceList = [];
      let pointSource = '';

      // 1. 真实航点：仅使用 WaylineFingerprint.action_details
      if (fallbackData.length > 0) {
        console.log('[Debug] 来源: WaylineFingerprint.action_details (数量: ' + fallbackData.length + ')');
        sourceList = fallbackData;
        pointSource = 'actionDetails';
      }

      // 2. 如果还是空的，那就彻底没戏了
      if (sourceList.length === 0) {
        console.error('[Error] 未拿到 WaylineFingerprint.action_details 数据。');
        alert(`航线 ID ${wayline.id} 没有真实航点数据，无法绘制。`);
        return;
      }

      // 4. 解析数据 (打印第一条数据，帮你确认字段名)
      console.log('[Debug] 准备解析的第一条数据样本:', JSON.stringify(sourceList[0]));

      const mappedPoints = [];
      sourceList.forEach((p, i) => {
        // 暴力匹配所有可能的字段名
        const lon = this.toNumber(p.lon ?? p.longitude ?? p.long ?? p.x);
        const lat = this.toNumber(p.lat ?? p.latitude ?? p.y);
        const alt = this.getActionDetailAltitude(p);
        const safeAlt = Number.isFinite(alt) ? alt : 0;

        if (Number.isFinite(lon) && Number.isFinite(lat)) {
          mappedPoints.push({
            longitude: lon,
            latitude: lat,
            altitude: safeAlt,
            heading: Number(p.aircraft_heading || p.heading || 0),
            gimbalPitch: Number(p.gimbal_pitch || 0)
          });
        } else {
          if (i === 0) console.warn('[Debug] 第一条数据解析失败，字段不匹配:', p);
        }
      });

      console.log(`[Debug] 解析完成，有效坐标点: ${mappedPoints.length} 个`);

      const mergeThresholdMeters = 0.5;
      const uniquePoints = this.mergeCloseWaypoints(mappedPoints, mergeThresholdMeters);
      if (uniquePoints.length !== mappedPoints.length) {
        console.log(`[Debug] 航点去重: ${mappedPoints.length} -> ${uniquePoints.length}`);
      }

      if (uniquePoints.length > 1) {
        finalWayline.waypoints = uniquePoints;
        this.waylinePointSource = pointSource || 'actionDetails';
        // 确保 Vue 响应式更新
        this.selectedWayline = finalWayline;

        // 延迟执行绘制，确保 DOM/Viewer 稳定
        setTimeout(() => {
          this.drawWaylineOnMap(finalWayline);
        }, 200);
      } else {
        alert('解析后有效点数不足 2 个，无法连线');
      }
    },
    drawWaylineOnMap(wayline) {
      if (!this.viewer || !wayline?.waypoints?.length) return;
      const Cesium = this.cesiumLib || window.Cesium;

      // 清理旧实体
      if (this.waylineEntity) {
        this.viewer.entities.remove(this.waylineEntity);
        this.waylineEntity = null;
      }
      if (this.waylinePointEntities.length) {
        this.waylinePointEntities.forEach(entity => this.viewer.entities.remove(entity));
        this.waylinePointEntities = [];
      }

      // 1. 提取坐标
      const positions = wayline.waypoints.map(p =>
          Cesium.Cartesian3.fromDegrees(p.longitude, p.latitude, p.altitude)
      );

      // 2. 绘制航线（轻微辉光 + 清晰主线）
      this.waylineEntity = this.viewer.entities.add({
        name: wayline.name || '航线',
        polyline: {
          positions: positions,
          width: 10,
          material: new Cesium.PolylineGlowMaterialProperty({
            glowPower: 0.15,
            color: Cesium.Color.CYAN.withAlpha(0.85)
          }),
          clampToGround: false,
          arcType: Cesium.ArcType.NONE,
          // 被地形遮挡时也保留可见性
          depthFailMaterial: new Cesium.PolylineGlowMaterialProperty({
            glowPower: 0.1,
            color: Cesium.Color.CYAN.withAlpha(0.45)
          })
        }
      });

      // 3. 绘制航点（保持原样，这部分你已经能看到了）
      if (this.waylinePointSource !== 'actionDetails') {
        positions.forEach((pos) => {
          const pointEntity = this.viewer.entities.add({
            position: pos,
            point: {
              pixelSize: 8,
              color: Cesium.Color.RED,
              outlineColor: Cesium.Color.WHITE,
              outlineWidth: 2,
              disableDepthTestDistance: Number.POSITIVE_INFINITY // 确保点永远在最上层
            }
          });
          this.waylinePointEntities.push(pointEntity);
        });
      }

      // 4. 视角飞向整个航线范围
      const sphere = Cesium.BoundingSphere.fromPoints(positions);
      this.viewer.camera.flyToBoundingSphere(sphere, {
        duration: 1.0,
        offset: new Cesium.HeadingPitchRange(0, Cesium.Math.toRadians(-30), sphere.radius * 2.5)
      });
    },

    // 安全的计算朝向函数，处理重合点
    calculateHeading(p1, p2) {
      const Cesium = this.cesiumLib || window.Cesium;
      // 如果点太近，直接返回 0，防止数学错误
      if (Cesium.Cartesian3.distance(p1, p2) < 1.0) {
        return 0;
      }

      // 建立局部坐标系 ENU (East-North-Up)
      const transform = Cesium.Transforms.eastNorthUpToFixedFrame(p1);
      const invTransform = Cesium.Matrix4.inverse(transform, new Cesium.Matrix4());

      // 将 p2 转到 p1 的局部坐标系
      const p2Local = Cesium.Matrix4.multiplyByPoint(invTransform, p2, new Cesium.Cartesian3());

      // 计算角度: atan2(y, x) 是相对东方向的逆时针角度
      // Cesium Heading 是相对北方向的顺时针角度
      // 数学转换:
      // East(X) -> 0 rad (Math) -> 90 deg (Cesium)
      // North(Y) -> 90 deg (Math) -> 0 deg (Cesium)
      // 简易公式: angle = atan2(x, y) (注意 x,y 顺序与标准 atan2 相反) 即可得到顺时针相对Y轴的角度吗？
      // Cesium 标准做法：
      let angle = Math.atan2(p2Local.y, p2Local.x);
      // angle 是与X轴(东)的夹角。
      // 我们需要 Heading (与北的夹角)。
      // Heading = 90度 - angle (弧度制: PI/2 - angle)
      let heading = Cesium.Math.PI_OVER_TWO - angle;

      return heading;
    },
    enableChaseCamera(entity, distance = 80, height = 30) {
      const Cesium = this.cesiumLib || window.Cesium;

      // 1. 清理旧的监听器，防止重复绑定导致相机乱晃
      if (this.chaseCameraListener) {
        this.viewer.scene.postUpdate.removeEventListener(this.chaseCameraListener);
        this.chaseCameraListener = null;
      }

      // 2. 定义每帧刷新逻辑
      this.chaseCameraListener = () => {
        // 只有无人机存在且在显示时才跟随
        if (!entity || !entity.show) return;

        const time = Cesium.JulianDate.now();

        // 获取当前时刻的位置和朝向
        const position = entity.position?.getValue(time);
        const orientation = entity.orientation?.getValue(time);

        if (position) {
          // A. 计算模型变换矩阵 (Model Matrix)
          // 这个矩阵代表了无人机当前的坐标系：原点在无人机中心，轴向跟随无人机旋转
          const transform = orientation
            ? Cesium.Matrix4.fromRotationTranslation(
              Cesium.Matrix3.fromQuaternion(orientation),
              position
            )
            : Cesium.Transforms.eastNorthUpToFixedFrame(position);

          // B. 定义相机在【局部坐标系】中的位置
          // 假设：X轴是正前方，Y轴是右侧，Z轴是上方
          // 我们要放在：后方 (-X) 且 上方 (+Z)
          // 注意：不同模型的坐标系可能不同。如果发现相机在侧面，请调整这里的 x/y 值
          const offset = new Cesium.Cartesian3(-distance, 0, height);

          // C. 将局部偏移量转换为世界坐标
          const cameraPosition = Cesium.Matrix4.multiplyByPoint(
              transform,
              offset,
              new Cesium.Cartesian3()
          );

          // D. 设置相机
          // destination: 相机位置 (世界坐标)
          // orientation: 让相机看向无人机中心 (direction)

          // 计算相机看向目标的方向向量
          const direction = Cesium.Cartesian3.subtract(
              position,
              cameraPosition,
              new Cesium.Cartesian3()
          );
          Cesium.Cartesian3.normalize(direction, direction);

          // 设置相机，保持 Up 轴大致向上 (避免翻滚)
          this.viewer.camera.setView({
            destination: cameraPosition,
            orientation: {
              direction: direction,
              up: Cesium.Cartesian3.normalize(position, new Cesium.Cartesian3()) // 使用地心向量作为Up，保持地球水平
            }
          });
        }
      };

      // 3. 绑定到场景更新事件 (每一帧渲染前执行)
      this.viewer.scene.postUpdate.addEventListener(this.chaseCameraListener);
    },
    // --- 辅助方法 ---
    enableDynamicChaseCamera(entity, offsetProperty) {
      const Cesium = this.cesiumLib || window.Cesium;

      if (this.chaseCameraListener) {
        this.viewer.scene.postUpdate.removeEventListener(this.chaseCameraListener);
      }

      this.chaseCameraListener = () => {
        if (!entity || !entity.show) return;

        const time = this.viewer.clock.currentTime;

        // 1. 获取当前时刻的各项属性
        const position = entity.position.getValue(time);
        const orientation = entity.orientation.getValue(time);
        // 【关键】获取当前时刻应该有的相机偏移量 (是远是近，由时间轴决定)
        const currentOffset = offsetProperty.getValue(time);

        if (position && orientation && currentOffset) {
          const transform = Cesium.Matrix4.fromRotationTranslation(
              Cesium.Matrix3.fromQuaternion(orientation),
              position
          );

          // 2. 应用动态偏移量
          const cameraPosition = Cesium.Matrix4.multiplyByPoint(
              transform,
              currentOffset,
              new Cesium.Cartesian3()
          );

          // 3. 计算朝向 (相机始终盯着无人机中心)
          // 如果是特写模式(Zoomed)，相机其实是在无人机前方，回头看无人机可能会穿模
          // 所以这里做一个微调：
          // 如果 currentOffset.x > 0 (在机头前方)，我们就让相机看向前方无限远，模拟第一人称
          // 如果 currentOffset.x < 0 (在机尾后方)，我们就看向无人机

          let direction;

          if (currentOffset.x > 0) {
            // 模拟第一人称：方向就是无人机的正前方
            // 简单做法：取 transform 的 X 轴方向
            const forwardTarget = Cesium.Matrix4.multiplyByPoint(transform, new Cesium.Cartesian3(100, 0, 0), new Cesium.Cartesian3());
            direction = Cesium.Cartesian3.subtract(forwardTarget, cameraPosition, new Cesium.Cartesian3());
          } else {
            // 模拟第三人称：看向无人机
            direction = Cesium.Cartesian3.subtract(position, cameraPosition, new Cesium.Cartesian3());
          }

          Cesium.Cartesian3.normalize(direction, direction);

          this.viewer.camera.setView({
            destination: cameraPosition,
            orientation: {
              direction: direction,
              up: Cesium.Cartesian3.normalize(position, new Cesium.Cartesian3())
            }
          });
        }
      };

      this.viewer.scene.postUpdate.addEventListener(this.chaseCameraListener);
    },
    setCameraMode(mode) {
      if (!mode) return;
      this.cameraMode = mode;
      this.applyCameraMode(true);
    },
    applyCameraMode(force = false) {
      if (!this.viewer) return;
      const Cesium = this.cesiumLib || window.Cesium;
      if (!Cesium) return;

      if (this.cameraMode === 'third') {
        if ((force || !this.chaseCameraListener) && this.droneEntity) {
          this.enableChaseCamera(this.droneEntity, 80, 30);
        }
        return;
      }

      if (this.chaseCameraListener) {
        this.viewer.scene.postUpdate.removeEventListener(this.chaseCameraListener);
        this.chaseCameraListener = null;
      }
      this.viewer.trackedEntity = undefined;

      if (this.droneEntity?.position) {
        const position = this.droneEntity.position.getValue(Cesium.JulianDate.now());
        if (position) {
          this.updateBirdCameraFromCartesian(position);
        }
      }
    },
    updateBirdCameraFromCartesian(cartesian, heightOffset = 200) {
      if (!this.viewer || !cartesian) return;
      const Cesium = this.cesiumLib || window.Cesium;
      if (!Cesium) return;
      const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
      if (!cartographic) return;
      const lon = Cesium.Math.toDegrees(cartographic.longitude);
      const lat = Cesium.Math.toDegrees(cartographic.latitude);
      const alt = cartographic.height;
      const safeHeight = Number.isFinite(alt) ? Math.max(alt + heightOffset, 200) : 300;
      this.viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(lon, lat, safeHeight),
        orientation: {
          heading: 0,
          pitch: Cesium.Math.toRadians(-90),
          roll: 0
        }
      });
    },
    updateBirdCameraFromCoords(longitude, latitude, altitude, heightOffset = 200) {
      if (!this.viewer) return;
      const Cesium = this.cesiumLib || window.Cesium;
      if (!Cesium) return;
      if (!Number.isFinite(longitude) || !Number.isFinite(latitude)) return;
      const safeHeight = Number.isFinite(altitude) ? Math.max(altitude + heightOffset, 200) : 300;
      this.viewer.camera.setView({
        destination: Cesium.Cartesian3.fromDegrees(longitude, latitude, safeHeight),
        orientation: {
          heading: 0,
          pitch: Cesium.Math.toRadians(-90),
          roll: 0
        }
      });
    },
    focusOnModel() {
      if (this.viewer && this.tileset) {
        const Cesium = this.cesiumLib || window.Cesium;
        if (!Cesium) return;
        const range = (this.tileset.boundingSphere?.radius || 1000) * 2.5;
        this.viewer.flyTo(this.tileset, {
          offset: new Cesium.HeadingPitchRange(0, Cesium.Math.toRadians(-30), range)
        }).catch(err => console.warn('飞到模型失败', err));
      }
    },

    focusOnWayline() {
      if (!this.viewer || !this.waylineEntity?.polyline?.positions) return;
      const Cesium = this.cesiumLib || window.Cesium;
      if (!Cesium) return;
      const time = this.viewer.clock?.currentTime || Cesium.JulianDate.now();
      const positions = this.waylineEntity.polyline.positions.getValue(time);
      if (!positions || positions.length === 0) return;
      const sphere = Cesium.BoundingSphere.fromPoints(positions);
      this.viewer.camera.flyToBoundingSphere(sphere, {
        duration: 1.2,
        offset: new Cesium.HeadingPitchRange(0, Cesium.Math.toRadians(-30), sphere.radius * 2.5)
      });
    },

    resetCameraView() {
      if (this.viewer) {
        const Cesium = this.cesiumLib || window.Cesium;
        if (!Cesium) return;

        if (this.chaseCameraListener) {
          this.viewer.scene.postUpdate.removeEventListener(this.chaseCameraListener);
          this.chaseCameraListener = null;
        }
        this.viewer.trackedEntity = undefined;

        if (this.waylineEntity?.polyline?.positions) {
          const positions = this.waylineEntity.polyline.positions.getValue(new Cesium.JulianDate());
          if (positions?.[0]) {
            this.viewer.camera.flyTo({
              destination: positions[0],
              orientation: {
                heading: Cesium.Math.toRadians(0),
                pitch: Cesium.Math.toRadians(-45),
                roll: 0.0
              },
              duration: 1.2
            });
            return;
          }
        }
      }
    },

    toggleGlobe() {
      this.globeVisible = !this.globeVisible;
      if (this.viewer) {
        this.viewer.scene.globe.show = this.globeVisible;
      }
    },

    handleViewAlarmDetail(alarm) {
      this.currentAlarm = alarm;
      this.showAlarmDetail = true;
    },

    handleImageError(event) {
      // 图片加载失败时显示占位图
      event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23ddd" width="400" height="300"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E图片加载失败%3C/text%3E%3C/svg%3E';
    },

    async handleProcessAlarm(alarmId) {
      try {
        await alarmApi.patchAlarm(alarmId, { status: 'COMPLETED' });
        this.alarms = this.alarms.filter(alarm => alarm.id !== alarmId);
      } catch (error) {
        console.error('更新告警状态失败:', error);
      }
    },

    formatAlarmTime(timestamp) {
      if (!timestamp) return '--';
      const date = new Date(timestamp);
      return date.toLocaleString('zh-CN');
    },

    startDockPolling() {
      this.stopDockPolling()
      this.dockPollTimer = setInterval(() => {
        this.loadDockList(true)
      }, 1000)
    },

    stopDockPolling() {
      if (this.dockPollTimer) {
        clearInterval(this.dockPollTimer)
        this.dockPollTimer = null
      }
    },

    async loadDockList(silent = false) {
      if (silent && this.dockLoading) return
      if (!silent) {
        this.dockLoading = true
        this.dockLoadError = ''
      }
      try {
        const response = await dockStatusApi.getAllDocks()
        const list = Array.isArray(response) ? response : (response.results || [])
        this.docks = list
        this.dockLoadError = ''
        if (this.selectedDock) {
          const match = list.find(dock => {
            if (this.selectedDock.id && dock.id) {
              return this.selectedDock.id === dock.id
            }
            return this.selectedDock.dock_sn && dock.dock_sn && this.selectedDock.dock_sn === dock.dock_sn
          })
          if (match) {
            this.selectedDock = match
            this.syncLiveStreamType()
            if (!(match.drone_in_dock === 1 || match.drone_in_dock === '1')) {
              this.showCreateTaskDialog = false
            }
          }
        }
        if (this.selectedDock) {
          this.startPositionPolling()
        }
      } catch (error) {
        console.error('获取机场列表失败:', error)
        if (!silent) {
          this.dockLoadError = '机场列表加载失败'
        }
      } finally {
        if (!silent) {
          this.dockLoading = false
        }
      }
    },

    handleDockSelected(dock) {
      if (!dock) return
      const previousSn = this.selectedDock?.drone_sn
      this.selectedDock = dock
      this.latestPositions = []
      this.positionLoading = false
      if (!(dock.drone_in_dock === 1 || dock.drone_in_dock === '1')) {
        this.showCreateTaskDialog = false
      }
      if (previousSn && dock?.drone_sn && previousSn !== dock.drone_sn) {
        this.resetDroneTrackingState()
      }
      this.syncLiveStreamType()
      this.startPositionPolling()
    },
    syncLiveStreamType() {
      const hasAirport = Boolean(this.airportPushUrl)
      const hasDrone = Boolean(this.dronePushUrl)
      if (this.liveStreamType === 'airport' && hasAirport) return
      if (this.liveStreamType === 'drone' && hasDrone) return
      if (hasAirport) {
        this.liveStreamType = 'airport'
        return
      }
      if (hasDrone) {
        this.liveStreamType = 'drone'
        return
      }
      this.liveStreamType = 'airport'
    },
    setLiveStreamType(type) {
      if (type === 'airport' && this.airportPushUrl) {
        this.liveStreamType = 'airport'
        return
      }
      if (type === 'drone' && this.dronePushUrl) {
        this.liveStreamType = 'drone'
      }
    },
    openCreateTaskDialog() {
      if (!this.selectedDockSn) return
      this.showCreateTaskDialog = true
    },
    async handleReturnHome() {
      const deviceSn = this.selectedDockSn
      if (!deviceSn) {
        ElMessage.warning('请先选择机场')
        return
      }
      try {
        await ElMessageBox.confirm('确认执行返航操作？', '提示', {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        })
      } catch (error) {
        return
      }
      this.commandLoading.returnHome = true
      try {
        const res = await flightTaskApi.returnHome(deviceSn)
        if (res.code === 0) {
          ElMessage.success('返航指令已发送')
        } else {
          ElMessage.error(res.msg || '返航指令发送失败')
        }
      } catch (error) {
        ElMessage.error('返航指令发送失败：' + (error.message || '未知错误'))
      } finally {
        this.commandLoading.returnHome = false
      }
    },
    async handleCancelReturn() {
      const deviceSn = this.selectedDockSn
      if (!deviceSn) {
        ElMessage.warning('请先选择机场')
        return
      }
      try {
        await ElMessageBox.confirm('确认取消返航？', '提示', {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        })
      } catch (error) {
        return
      }
      this.commandLoading.cancelReturn = true
      try {
        const res = await flightTaskApi.cancelReturn(deviceSn)
        if (res.code === 0) {
          ElMessage.success('已取消返航')
        } else {
          ElMessage.error(res.msg || '取消返航失败')
        }
      } catch (error) {
        ElMessage.error('取消返航失败：' + (error.message || '未知错误'))
      } finally {
        this.commandLoading.cancelReturn = false
      }
    },
    async handlePause() {
      const deviceSn = this.selectedDockSn
      if (!deviceSn) {
        ElMessage.warning('请先选择机场')
        return
      }
      try {
        await ElMessageBox.confirm('确认暂停当前任务？', '提示', {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'info'
        })
      } catch (error) {
        return
      }
      this.commandLoading.pause = true
      try {
        const res = await flightTaskApi.pauseTask(deviceSn)
        if (res.code === 0) {
          ElMessage.success('任务已暂停')
        } else {
          ElMessage.error(res.msg || '暂停任务失败')
        }
      } catch (error) {
        ElMessage.error('暂停任务失败：' + (error.message || '未知错误'))
      } finally {
        this.commandLoading.pause = false
      }
    },
    async handleResume() {
      const deviceSn = this.selectedDockSn
      if (!deviceSn) {
        ElMessage.warning('请先选择机场')
        return
      }
      try {
        await ElMessageBox.confirm('确认恢复任务？', '提示', {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'success'
        })
      } catch (error) {
        return
      }
      this.commandLoading.resume = true
      try {
        const res = await flightTaskApi.resumeTask(deviceSn)
        if (res.code === 0) {
          ElMessage.success('任务已恢复')
        } else {
          ElMessage.error(res.msg || '恢复任务失败')
        }
      } catch (error) {
        ElMessage.error('恢复任务失败：' + (error.message || '未知错误'))
      } finally {
        this.commandLoading.resume = false
      }
    },

    startPositionPolling() {
      const deviceSn = this.selectedDock?.drone_sn
      const shouldPoll = deviceSn && this.isDroneWorking(this.selectedDock)
      if (!shouldPoll) {
        this.stopPositionPolling()
        this.clearDigitalTwinAndAlarms()
        return
      }
      if (this.positionPollingDeviceSn && this.positionPollingDeviceSn !== deviceSn) {
        this.resetDroneTrackingState()
      }
      if (this.positionPollTimer && this.positionPollingDeviceSn === deviceSn) {
        return
      }
      this.stopPositionPolling()
      this.positionPollingDeviceSn = deviceSn
      this.fetchLatestPositions()
      this.positionPollTimer = setInterval(() => {
        this.fetchLatestPositions()
      }, 500)
    },

    stopPositionPolling() {
      if (this.positionPollTimer) {
        clearInterval(this.positionPollTimer)
        this.positionPollTimer = null
      }
      this.positionPollingDeviceSn = ''
    },

    async fetchLatestPositions() {
      const deviceSn = this.selectedDock?.drone_sn
      if (!deviceSn || this.positionLoading || !this.isDroneWorking(this.selectedDock)) return
      this.positionLoading = true
      try {
        const response = await dronePositionApi.getPositions({
          device_sn: deviceSn,
          ordering: '-timestamp'
        })
        if (this.selectedDock?.drone_sn !== deviceSn) return
        const list = Array.isArray(response) ? response : (response.results || [])
        this.latestPositions = list.slice(0, 2)
        this.updateDigitalTwinFromPositions(list)
      } catch (error) {
        console.error('获取无人机位置失败:', error)
      } finally {
        this.positionLoading = false
      }
    },

    getDockDisplayName(dock) {
      return dock?.display_name || dock?.dock_name || dock?.dock_sn || '未知机场'
    },

    updateDigitalTwinFromPositions(positions) {
      const latestPosition = Array.isArray(positions) ? positions[0] : null
      if (latestPosition) {
        this.updateDroneEntityFromPosition(latestPosition)
      }
      const dockSn = this.selectedDock?.dock_sn
      if (!dockSn) return
      const now = Date.now()
      if (dockSn === this.lastTaskInfoSn && now - this.lastTaskInfoAttempt < 3000) {
        return
      }
      if (this.taskInfoFetchInFlight) return
      this.lastTaskInfoSn = dockSn
      this.lastTaskInfoAttempt = now
      void this.syncWaylineFromTaskInfo(dockSn)
    },
    updateDroneEntityFromPosition(position) {
      if (!position || !this.viewer) return
      const Cesium = this.cesiumLib || window.Cesium
      if (!Cesium) return

      const timestamp = this.getPositionTimestamp(position)
      if (Number.isFinite(timestamp) && this.lastDroneTimestamp && timestamp <= this.lastDroneTimestamp) {
        return
      }

      const payload = this.extractPositionData(position)
      const longitude = payload.longitude
      const latitude = payload.latitude
      if (!Number.isFinite(longitude) || !Number.isFinite(latitude)) return
      const altitude = Number.isFinite(payload.altitude) ? payload.altitude : 0
      const cartesian = Cesium.Cartesian3.fromDegrees(longitude, latitude, altitude)

      if (!this.droneEntity) {
        this.droneEntity = this.viewer.entities.add({
          name: '无人机',
          position: cartesian,
          model: {
            uri: '/models/fly.glb',
            minimumPixelSize: 128,
            maximumScale: 2000,
            scale: 1.0,
            runAnimations: true
          }
        })
      } else {
        this.droneEntity.position = cartesian
      }

      const heading = this.resolveDroneHeading(payload.heading, cartesian)
      if (Number.isFinite(heading)) {
        const modelHeadingOffset = Cesium.Math.toRadians(-90)
        this.droneEntity.orientation = Cesium.Transforms.headingPitchRollQuaternion(
          cartesian,
          new Cesium.HeadingPitchRoll(heading + modelHeadingOffset, 0, 0)
        )
      }

      if (Number.isFinite(timestamp)) {
        this.lastDroneTimestamp = timestamp
      }
      this.lastDronePosition = { longitude, latitude, altitude }
      this.lastDroneCartesian = cartesian

      if (this.cameraMode === 'bird') {
        this.updateBirdCameraFromCoords(longitude, latitude, altitude)
      } else if (this.cameraMode === 'third' && !this.chaseCameraListener) {
        this.enableChaseCamera(this.droneEntity, 80, 30)
      }
    },
    extractPositionData(position) {
      const rawData = this.parseRawData(position?.raw_data)
      const raw = rawData?.position || rawData?.location || rawData || {}
      const longitude = this.toNumber(
        position?.longitude ?? position?.lon ?? position?.lng ?? raw.longitude ?? raw.lon ?? raw.lng
      )
      const latitude = this.toNumber(
        position?.latitude ?? position?.lat ?? raw.latitude ?? raw.lat
      )
      const altitude = this.toNumber(
        position?.altitude ??
        position?.height ??
        position?.relative_height ??
        position?.ellipsoid_height ??
        raw.altitude ??
        raw.height ??
        raw.relative_height ??
        raw.ellipsoid_height
      )
      const heading = this.toNumber(
        position?.heading ??
        position?.yaw ??
        position?.aircraft_heading ??
        raw.heading ??
        raw.yaw ??
        raw.aircraft_heading
      )
      return { longitude, latitude, altitude, heading }
    },
    parseRawData(raw) {
      if (!raw) return null
      if (typeof raw === 'object') return raw
      if (typeof raw !== 'string') return null
      try {
        return JSON.parse(raw)
      } catch (e) {
        return null
      }
    },
    getPositionTimestamp(position) {
      const rawData = this.parseRawData(position?.raw_data)
      const candidates = [
        position?.timestamp,
        position?.created_at,
        position?.updated_at,
        position?.time,
        position?.ts,
        rawData?.timestamp,
        rawData?.time,
        rawData?.ts
      ]
      for (const candidate of candidates) {
        const normalized = this.normalizeTimestamp(candidate)
        if (Number.isFinite(normalized)) {
          return normalized
        }
      }
      return NaN
    },
    normalizeTimestamp(value) {
      if (value === null || value === undefined) return NaN
      if (value instanceof Date) {
        const time = value.getTime()
        return Number.isFinite(time) ? time : NaN
      }
      if (typeof value === 'number') {
        if (value > 1e12) return value
        if (value > 1e9) return value * 1000
        return value
      }
      if (typeof value === 'string') {
        const trimmed = value.trim()
        if (!trimmed) return NaN
        const parsed = Date.parse(trimmed)
        if (!Number.isNaN(parsed)) return parsed
        const asNumber = Number(trimmed)
        if (Number.isFinite(asNumber)) return this.normalizeTimestamp(asNumber)
      }
      return NaN
    },
    resolveDroneHeading(rawHeading, cartesian) {
      const Cesium = this.cesiumLib || window.Cesium
      if (!Cesium || !cartesian) return NaN
      let heading = this.toNumber(rawHeading)
      if (Number.isFinite(heading)) {
        if (Math.abs(heading) > Math.PI * 2) {
          heading = Cesium.Math.toRadians(heading)
        }
        this.lastDroneHeading = heading
        return heading
      }
      if (this.lastDroneCartesian) {
        const computed = this.calculateHeading(this.lastDroneCartesian, cartesian)
        if (Number.isFinite(computed)) {
          this.lastDroneHeading = computed
          return computed
        }
      }
      return this.lastDroneHeading ?? NaN
    },

    async syncWaylineFromTaskInfo(dockSn) {
      const normalizedSn = String(dockSn || '').trim()
      if (!normalizedSn) return
      if (this.taskInfoFetchInFlight) return
      this.taskInfoFetchInFlight = true
      try {
        const response = await flightTaskInfoApi.getLatestBySn(normalizedSn)
        let taskInfo = response
        if (Array.isArray(response)) {
          taskInfo = response[0]
        } else if (response?.results) {
          taskInfo = response.results[0]
        } else if (response?.data && typeof response.data === 'object' && !Array.isArray(response.data)) {
          taskInfo = response.data
        }
        if (!taskInfo || Object.keys(taskInfo).length === 0) return
        const params = this.parseTaskParams(taskInfo.params)
        const waylineUuid = params?.wayline_uuid || params?.wayline_id || taskInfo.wayline_id
        const normalizedUuid = String(waylineUuid || '').trim()
        if (!normalizedUuid) return
        if (normalizedUuid === this.currentWaylineUuid) return
        this.currentWaylineUuid = normalizedUuid
        await this.syncWaylineFromUuid(normalizedUuid)
      } catch (error) {
        console.error('获取任务信息失败:', error)
      } finally {
        this.taskInfoFetchInFlight = false
      }
    },

    async syncWaylineFromUuid(waylineUuid) {
      const normalizedUuid = String(waylineUuid || '').trim()
      if (!normalizedUuid) return
      if (this.waylineFetchInFlight) return
      this.waylineFetchInFlight = true
      try {
        let response = await waylineApi.getWaylines({ wayline_id: normalizedUuid })
        let list = Array.isArray(response) ? response : (response.results || response.data || [])
        if (!list.length) {
          response = await waylineApi.getWaylines({ wayline_id__icontains: normalizedUuid })
          list = Array.isArray(response) ? response : (response.results || response.data || [])
        }
        let match = list.find(item => String(item?.wayline_id) === normalizedUuid) || list[0]
        if (!match && /^\d+$/.test(normalizedUuid)) {
          const detail = await waylineApi.getWaylineDetail(normalizedUuid)
          if (detail?.id) {
            match = detail
          }
        }
        if (!match) {
          console.warn('[Dashboard] 未找到匹配航线:', normalizedUuid)
          return
        }
        await this.applyWaylineSelection(match)
      } catch (error) {
        console.error('获取航线信息失败:', error)
      } finally {
        this.waylineFetchInFlight = false
      }
    },

    parseTaskParams(params) {
      if (!params) return null
      if (typeof params === 'object') return params
      if (typeof params !== 'string') return null
      try {
        return JSON.parse(params)
      } catch (e) {
        return null
      }
    },

    isDroneWorking(dock) {
      return dock?.drone_in_dock === 0 || dock?.drone_in_dock === '0'
    },

    getDroneStateLabel(dock) {
      if (dock?.drone_in_dock === 1 || dock?.drone_in_dock === '1') return '机舱内'
      if (dock?.drone_in_dock === 0 || dock?.drone_in_dock === '0') return '任务中'
      return '状态未知'
    },

    isDockSelected(dock) {
      if (!dock || !this.selectedDock) return false
      if (this.selectedDock.id && dock.id) {
        return this.selectedDock.id === dock.id
      }
      return this.selectedDock.dock_sn && dock.dock_sn && this.selectedDock.dock_sn === dock.dock_sn
    },

    formatPositionTime(timestamp) {
      return this.formatAlarmTime(timestamp)
    },

    formatPositionCoords(position) {
      const lat = this.toNumber(position?.latitude)
      const lon = this.toNumber(position?.longitude)
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) return '--'
      return `${lat.toFixed(6)}, ${lon.toFixed(6)}`
    },

    formatPositionAltitude(position) {
      const altitude = this.toNumber(position?.altitude)
      if (Number.isFinite(altitude)) {
        return `${altitude.toFixed(1)} m`
      }
      const relative = this.toNumber(position?.relative_height)
      return Number.isFinite(relative) ? `${relative.toFixed(1)} m` : '--'
    },

    async loadComponentConfig() {
      try {
        this.componentConfig = await componentConfigApi.getConfig();
      } catch (err) {
        console.warn('获取组件配置失败，将使用默认配置', err);
      }
    },
    // async setupImageryLayers(Cesium) {
    //   if (!this.viewer) return;
    //   const layers = this.viewer.imageryLayers;
    //   layers.removeAll();
    //   const localTilesUrl = 'http://192.168.10.10:5000/tiles/{z}/{x}/{y}';
    //   const extent = Cesium.Rectangle.fromDegrees(122.0, 41.0, 124.0, 43.0);
    // 
    //   try {
    //     const layer = new Cesium.UrlTemplateImageryProvider({
    //       url: localTilesUrl,
    //       tilingScheme: new Cesium.WebMercatorTilingScheme(),
    //       rectangle: extent,
    //       minimumLevel: 0,
    //       maximumLevel: 19
    //     });
    //     layers.addImageryProvider(layer);
    //     setTimeout(() => {
    //       this.viewer.camera.flyTo({ destination: extent });
    //     }, 1000);
    //   } catch (e) {
    //     console.warn('地图加载失败', e);
    //   }
    // },
    async setupImageryLayers(Cesium) {
      if (!this.viewer) return;
      const layers = this.viewer.imageryLayers;
      layers.removeAll();
    
      try {
        // 方案 B：使用 ArcGIS 全球卫星底图 (无需申请 Key，稳定且快)
        const arcgisProvider = await Cesium.ArcGisMapServerImageryProvider.fromUrl(
            'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer'
        );
        layers.addImageryProvider(arcgisProvider);
    
        // 叠加一层透明的混合路网（可选，为了看地名）
        // const roads = await Cesium.ArcGisMapServerImageryProvider.fromUrl(
        //   'https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Hybrid_Reference/MapServer'
        // );
        // layers.addImageryProvider(roads);
    
      } catch (e) {
        console.warn('地图加载失败', e);
      }
    },
    tuneCameraControls(controller) {
      if (!controller) return;
      const applyNumber = (key, value) => {
        if (typeof controller[key] === 'number') {
          controller[key] = value;
        }
      };
      applyNumber('inertiaSpin', 0.1);
      applyNumber('inertiaTranslate', 0.12);
      applyNumber('inertiaZoom', 0.1);
      applyNumber('minimumZoomRate', 0.05);
      applyNumber('maximumZoomRate', 80000);
      applyNumber('zoomFactor', 0.4);
      applyNumber('rotateFactor', 0.15);
      applyNumber('tiltFactor', 0.15);
      applyNumber('lookFactor', 0.2);
      applyNumber('translateFactor', 0.2);
      applyNumber('_zoomFactor', 0.4);
      applyNumber('_rotateFactor', 0.15);
      applyNumber('_tiltFactor', 0.15);
      applyNumber('_lookFactor', 0.2);
      applyNumber('_translateFactor', 0.2);
      applyNumber('minimumRotateRate', 0.005);
      applyNumber('maximumRotateRate', 0.2);
      applyNumber('minimumTiltRate', 0.005);
      applyNumber('maximumTiltRate', 0.2);
      applyNumber('rotateRateRangeAdjustment', 0.2);
      applyNumber('_rotateRateRangeAdjustment', 0.2);
      applyNumber('tiltRateRangeAdjustment', 0.2);
      applyNumber('_tiltRateRangeAdjustment', 0.2);
    },

    async fetchAlarmsByWayline(waylineId) {
      if (!waylineId) {
        this.alarms = [];
        this.clearAlarmMarkers();
        return;
      }
      this.loadingAlarms = true;
      try {
        const response = await alarmApi.getAlarms({ wayline: waylineId });
        this.alarms = Array.isArray(response) ? response : (response.results || []);
        this.plotAlarmMarkers(this.alarms);
      } catch (error) {
        console.error('获取告警信息失败:', error);
        this.alarms = [];
        this.clearAlarmMarkers();
      } finally {
        this.loadingAlarms = false;
      }
    },

    getFilteredAlarms() {
      return this.alarms;
    },

    handleAlarmRefresh() {
      if (this.selectedWayline) {
        this.fetchAlarmsByWayline(this.selectedWayline.id);
      }
      if (this.alarms.length) {
        this.plotAlarmMarkers(this.alarms);
      }
    },

    async initSelectedWaylineFromRoute() {
      try {
        const id = this.$route?.query?.wayline_id;
        if (!id) return;
        const detail = await alarmApi.getWaylineDetail(id);
        if (detail && detail.id) {
          this.selectedWayline = detail;
          this.fetchAlarmsByWayline(detail.id);
          this.ensureWaylineWithPoints(detail);
          this.fetchActionDetails(detail.id);
        }
      } catch (e) {
        console.warn('根据路由初始化航线失败', e);
      }
    },
    async fetchActionDetails(waylineId) {
      try {
        const res = await waylineApi.getWaylineActionDetails(waylineId);
        this.actionDetails = Array.isArray(res?.action_details) ? res.action_details : [];
        this.plotActionDetailMarkers(this.actionDetails);
      } catch (e) {
        console.warn('获取航线动作详情失败', e);
        this.actionDetails = [];
        this.clearActionDetailMarkers();
      }
    },
    plotActionDetailMarkers(details) {
      if (!this.viewer) return;
      const Cesium = this.cesiumLib || window.Cesium;
      if (!Cesium) return;
      this.clearActionDetailMarkers();
      const rawPoints = [];
      details.forEach(d => {
        const lat = this.toNumber(d.lat);
        const lon = this.toNumber(d.lon);
        const h = this.getActionDetailAltitude(d);
        const safeHeight = Number.isFinite(h) ? h : 0;
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
        rawPoints.push({
          longitude: lon,
          latitude: lat,
          altitude: safeHeight
        });
      });

      const mergeThresholdMeters = 0.5;
      const points = this.mergeCloseWaypoints(rawPoints, mergeThresholdMeters);
      const triangleImage = this.getInvertedTriangleImage();
      const entities = [];
      points.forEach(point => {
        const top = Cesium.Cartesian3.fromDegrees(point.longitude, point.latitude, point.altitude);
        const bottom = Cesium.Cartesian3.fromDegrees(point.longitude, point.latitude, 0);
        const line = this.viewer.entities.add({
          polyline: {
            positions: [top, bottom],
            width: 1.5,
            material: Cesium.Color.WHITE.withAlpha(0.85),
            depthFailMaterial: Cesium.Color.WHITE.withAlpha(0.35),
            clampToGround: false
          }
        });
        entities.push(line);

        const labelHeight = Math.max(point.altitude * 0.5, 1);
        const label = this.viewer.entities.add({
          position: Cesium.Cartesian3.fromDegrees(point.longitude, point.latitude, labelHeight),
          label: {
            text: Number.isFinite(point.altitude) ? `${point.altitude.toFixed(1)} m` : '--',
            font: '12px sans-serif',
            fillColor: Cesium.Color.WHITE,
            outlineColor: Cesium.Color.BLACK,
            outlineWidth: 2,
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            horizontalOrigin: Cesium.HorizontalOrigin.LEFT,
            pixelOffset: new Cesium.Cartesian2(6, -6),
            disableDepthTestDistance: Number.POSITIVE_INFINITY
          }
        });
        entities.push(label);

        const marker = this.viewer.entities.add({
          position: top,
          billboard: triangleImage ? {
            image: triangleImage,
            width: 18,
            height: 14,
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            disableDepthTestDistance: Number.POSITIVE_INFINITY
          } : undefined,
          point: triangleImage ? undefined : {
            pixelSize: 7,
            color: Cesium.Color.CYAN.withAlpha(0.95),
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 1,
            disableDepthTestDistance: Number.POSITIVE_INFINITY
          }
        });
        entities.push(marker);
      });
      this.actionDetailEntities = entities;
    },
    clearActionDetailMarkers() {
      if (this.viewer && this.actionDetailEntities.length) {
        this.actionDetailEntities.forEach(e => this.viewer.entities.remove(e));
      }
      this.actionDetailEntities = [];
    },
    getInvertedTriangleImage() {
      if (this.invertedTriangleImage) return this.invertedTriangleImage;
      if (typeof document === 'undefined') return null;
      const canvas = document.createElement('canvas');
      canvas.width = 24;
      canvas.height = 18;
      const ctx = canvas.getContext('2d');
      if (!ctx) return null;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.beginPath();
      ctx.moveTo(canvas.width / 2, canvas.height - 2);
      ctx.lineTo(2, 2);
      ctx.lineTo(canvas.width - 2, 2);
      ctx.closePath();
      ctx.fillStyle = 'rgba(34, 211, 238, 0.95)';
      ctx.fill();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.95)';
      ctx.lineWidth = 2;
      ctx.stroke();
      this.invertedTriangleImage = canvas;
      return canvas;
    },
    getActionDetailAltitude(detail) {
      const candidates = [
        detail?.height,
        detail?.altitude,
        detail?.ellipsoid_height,
        detail?.z
      ];
      for (const candidate of candidates) {
        const value = this.toNumber(candidate);
        if (Number.isFinite(value)) {
          return value;
        }
      }
      return NaN;
    },
    mergeCloseWaypoints(points, thresholdMeters = 0.5) {
      if (!Array.isArray(points) || points.length === 0) return [];
      const merged = [];
      points.forEach(point => {
        if (!merged.length) {
          merged.push(point);
          return;
        }
        const last = merged[merged.length - 1];
        const distance = this.getWaypointDistanceMeters(last, point);
        if (Number.isFinite(distance) && distance <= thresholdMeters) {
          return;
        }
        merged.push(point);
      });
      return merged;
    },
    getWaypointDistanceMeters(pointA, pointB) {
      const lon1 = this.toNumber(pointA?.longitude);
      const lat1 = this.toNumber(pointA?.latitude);
      const lon2 = this.toNumber(pointB?.longitude);
      const lat2 = this.toNumber(pointB?.latitude);
      if (!Number.isFinite(lon1) || !Number.isFinite(lat1) || !Number.isFinite(lon2) || !Number.isFinite(lat2)) {
        return NaN;
      }
      const alt1 = this.toNumber(pointA?.altitude);
      const alt2 = this.toNumber(pointB?.altitude);
      const Cesium = this.cesiumLib || window.Cesium;
      if (Cesium?.Cartesian3) {
        const a = Cesium.Cartesian3.fromDegrees(lon1, lat1, Number.isFinite(alt1) ? alt1 : 0);
        const b = Cesium.Cartesian3.fromDegrees(lon2, lat2, Number.isFinite(alt2) ? alt2 : 0);
        return Cesium.Cartesian3.distance(a, b);
      }
      const rad = Math.PI / 180;
      const phi1 = lat1 * rad;
      const phi2 = lat2 * rad;
      const dPhi = (lat2 - lat1) * rad;
      const dLambda = (lon2 - lon1) * rad;
      const sinDphi = Math.sin(dPhi / 2);
      const sinDlambda = Math.sin(dLambda / 2);
      const aVal = sinDphi * sinDphi + Math.cos(phi1) * Math.cos(phi2) * sinDlambda * sinDlambda;
      const c = 2 * Math.atan2(Math.sqrt(aVal), Math.sqrt(1 - aVal));
      const horizontal = 6371000 * c;
      if (Number.isFinite(alt1) && Number.isFinite(alt2)) {
        const dz = alt2 - alt1;
        return Math.sqrt(horizontal * horizontal + dz * dz);
      }
      return horizontal;
    },

    handleLocateAlarm(alarm) {
      const lat = this.toNumber(alarm?.latitude);
      const lon = this.toNumber(alarm?.longitude);
      if (!Number.isFinite(lat) || !Number.isFinite(lon) || !this.viewer) return;
      const Cesium = this.cesiumLib || window.Cesium;
      if (!Cesium) return;
      const height = this.getAlarmAltitude(alarm);
      const safeHeight = Number.isFinite(height) ? height : 200;
      const destination = Cesium.Cartesian3.fromDegrees(lon, lat, safeHeight);
      this.viewer.camera.flyTo({
        destination,
        orientation: {
          heading: Cesium.Math.toRadians(0),
          pitch: Cesium.Math.toRadians(-45),
          roll: 0.0
        },
        duration: 1.2
      });
    },
    plotAlarmMarkers(alarms) {
      if (!this.viewer) return;
      const Cesium = this.cesiumLib || window.Cesium;
      if (!Cesium) return;
      this.clearAlarmMarkers();
      const entities = [];
      const pinBuilder = (Cesium.PinBuilder) ? new Cesium.PinBuilder() : null;
      const pinCanvas = pinBuilder ? pinBuilder.fromColor(Cesium.Color.ORANGE, 32) : null;
      alarms.forEach(alarm => {
        const lat = this.toNumber(alarm.latitude);
        const lon = this.toNumber(alarm.longitude);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
        const altitude = this.getAlarmAltitude(alarm);
        const position = Cesium.Cartesian3.fromDegrees(lon, lat, Number.isFinite(altitude) ? altitude : 0);
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
        });
        entities.push(entity);
      });
      this.alarmEntities = entities;
    },

    clearAlarmMarkers() {
      if (this.viewer && this.alarmEntities.length) {
        this.alarmEntities.forEach(e => this.viewer.entities.remove(e));
      }
      this.alarmEntities = [];
    },
    resetDroneTrackingState() {
      this.lastDroneTimestamp = null;
      this.lastDroneHeading = null;
      this.lastDronePosition = null;
      this.lastDroneCartesian = null;
    },

    clearDigitalTwin() {
      if (this.viewer && this.waylineEntity) {
        this.viewer.entities.remove(this.waylineEntity);
        this.waylineEntity = null;
      }
      if (this.viewer && this.waylinePointEntities.length) {
        this.waylinePointEntities.forEach(entity => this.viewer.entities.remove(entity));
        this.waylinePointEntities = [];
      }
      if (this.viewer && this.droneEntity) {
        this.viewer.entities.remove(this.droneEntity);
        this.droneEntity = null;
      }
      if (this.viewer && this.chaseCameraListener) {
        this.viewer.scene.postUpdate.removeEventListener(this.chaseCameraListener);
        this.chaseCameraListener = null;
      }
      this.clearActionDetailMarkers();
      this.actionDetails = [];
      this.selectedWayline = null;
      this.currentWaylineUuid = '';
      this.waylinePointSource = '';
      this.resetDroneTrackingState();
    },

    clearAlarmData() {
      this.alarms = [];
      this.clearAlarmMarkers();
      this.showAlarmDetail = false;
      this.currentAlarm = null;
      this.loadingAlarms = false;
    },

    clearDigitalTwinAndAlarms() {
      this.clearDigitalTwin();
      this.clearAlarmData();
    },

    setupPickHandler(Cesium) {
      if (!this.viewer || this.pickHandler) return;
      this.pickHandler = new Cesium.ScreenSpaceEventHandler(this.viewer.scene.canvas);
      this.pickHandler.setInputAction(click => {
        const picked = this.viewer.scene.pick(click.position);
        if (Cesium.defined(picked) && picked.id && picked.id.alarmData) {
          this.currentAlarm = picked.id.alarmData;
          this.showAlarmDetail = true;
        }
      }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    },

    toNumber(val) {
      const num = Number(val);
      return Number.isFinite(num) ? num : NaN;
    },

    getAlarmAltitude(alarm) {
      const candidates = [alarm?.high, alarm?.altitude, alarm?.alt];
      for (const candidate of candidates) {
        const value = this.toNumber(candidate);
        if (Number.isFinite(value)) {
          return value;
        }
      }
      return NaN;
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

.detect-type-summary {
  padding: 16px 20px;
  background: rgba(26, 31, 58, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(0, 212, 255, 0.16);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
}

.detect-type-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.detect-type-title {
  font-size: 14px;
  font-weight: 700;
  color: #e2e8f0;
}

.detect-type-subtitle {
  font-size: 12px;
  color: #94a3b8;
}

.detect-type-table-wrap {
  overflow: auto;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.detect-type-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 520px;
  background: rgba(11, 16, 36, 0.35);
}

.detect-type-table th,
.detect-type-table td {
  padding: 10px 12px;
  font-size: 12px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  color: #cbd5e1;
}

.detect-type-table th {
  text-align: left;
  font-weight: 700;
  color: #e2e8f0;
  background: rgba(26, 31, 58, 0.45);
}

.type-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #e2e8f0;
  white-space: nowrap;
}

.type-icon {
  width: 18px;
  display: inline-flex;
  justify-content: center;
}

.code-cell {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  color: #93c5fd;
  white-space: nowrap;
}

.keywords-cell {
  color: #94a3b8;
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
  grid-template-columns: 320px 1fr;
  grid-template-rows: minmax(0, 1fr);
  gap: 24px;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

/* 侧边面板 */
.side-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
  height: 100%;
  overflow: hidden;
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
.left-panel {
  min-height: 0;
}

.dock-panel {
  flex: 0 0 auto;
}

.dock-panel-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
  flex: 0 0 auto;
}

.panel-action {
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: rgba(0, 212, 255, 0.12);
  color: #00d4ff;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.panel-action:hover:not(:disabled) {
  background: rgba(0, 212, 255, 0.2);
  border-color: rgba(0, 212, 255, 0.5);
}

.panel-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.panel-placeholder {
  padding: 12px;
  border-radius: 10px;
  text-align: center;
  font-size: 12px;
  color: #94a3b8;
  background: rgba(10, 14, 39, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.15);
}

.panel-placeholder.small {
  padding: 8px;
  font-size: 11px;
}

.panel-placeholder.error {
  color: #fca5a5;
  border-color: rgba(248, 113, 113, 0.35);
}

.dock-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 320px;
  overflow: auto;
  flex: 0 0 auto;
}

.dock-item {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(11, 16, 36, 0.6);
  cursor: pointer;
  transition: all 0.2s ease;
}

.dock-item:hover {
  border-color: rgba(0, 212, 255, 0.45);
  background: rgba(15, 23, 42, 0.7);
}

.dock-item.active {
  border-color: rgba(0, 212, 255, 0.7);
  box-shadow: 0 0 0 1px rgba(0, 212, 255, 0.2);
}

.dock-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.dock-item-name {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #64748b;
}

.status-dot.online {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
}

.dock-name {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dock-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid rgba(249, 115, 22, 0.4);
  color: #f97316;
  background: rgba(249, 115, 22, 0.1);
  flex-shrink: 0;
}

.dock-status.online {
  border-color: rgba(34, 197, 94, 0.4);
  color: #22c55e;
  background: rgba(34, 197, 94, 0.12);
}

.dock-item-meta {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 11px;
  color: #94a3b8;
}

.dock-sn,
.drone-sn {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.drone-state {
  font-size: 11px;
  color: #cbd5e1;
}

.drone-state.working {
  color: #22c55e;
}

.dock-latest {
  padding-top: 10px;
  border-top: 1px solid rgba(148, 163, 184, 0.15);
}

.dock-latest-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  gap: 8px;
}

.dock-latest-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dock-latest-title {
  font-size: 12px;
  color: #94a3b8;
}

.dock-latest-sn {
  font-size: 11px;
  color: #38bdf8;
  font-family: monospace;
}

.dock-latest-state {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 10px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  color: #94a3b8;
}

.dock-latest-state.working {
  border-color: rgba(34, 197, 94, 0.5);
  color: #22c55e;
  background: rgba(34, 197, 94, 0.08);
}

.position-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.position-item {
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid rgba(0, 212, 255, 0.2);
  background: rgba(15, 23, 42, 0.65);
}

.position-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 11px;
  color: #cbd5e1;
}

.position-label {
  color: #94a3b8;
}

.alarm-panel {
  flex: 0 0 360px;
  height: 360px;
}

.alarm-panel-body {
  flex: 1 1 auto;
  height: 100%;
  overflow: hidden;
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
  color: #94a3b8;
  background: rgba(10, 14, 39, 0.6);
  border-radius: 12px;
}

/* 中间主视图 */
.main-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.viewer-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  height: 100%;
  min-height: 0;
  flex: 1;
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

.create-task-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 4;
  pointer-events: none;
  background: rgba(6, 10, 24, 0.25);
}

.create-task-button {
  pointer-events: auto;
  padding: 18px 40px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 16px;
  border: 1px solid rgba(56, 189, 248, 0.6);
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.9), rgba(37, 99, 235, 0.9));
  color: #ffffff;
  cursor: pointer;
  box-shadow: 0 12px 30px rgba(0, 212, 255, 0.25);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.create-task-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 32px rgba(0, 212, 255, 0.3);
}

.cesium-controls {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  flex-wrap: wrap;
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
.control-btn.is-active {
  background: rgba(0, 212, 255, 0.3);
  border-color: rgba(0, 212, 255, 0.7);
  color: #ffffff;
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.25);
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

/* 直播监控区域样式 */
.live-monitor-section {
  flex: 1;
  min-height: 500px;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

.live-monitor-section .panel-body {
  padding: 0;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(0, 212, 255, 0.05);
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
}

.monitor-title {
  font-size: 14px;
  font-weight: 600;
  color: #00d4ff;
}

.monitor-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.monitor-commands {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.command-btn {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  color: #e2e8f0;
  background: rgba(15, 23, 42, 0.7);
}

.command-btn.warning {
  border-color: rgba(245, 158, 11, 0.6);
  color: #fbbf24;
}

.command-btn.default {
  border-color: rgba(148, 163, 184, 0.5);
  color: #e2e8f0;
}

.command-btn.info {
  border-color: rgba(56, 189, 248, 0.6);
  color: #7dd3fc;
}

.command-btn.success {
  border-color: rgba(34, 197, 94, 0.6);
  color: #86efac;
}

.command-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stream-toggle {
  display: flex;
  gap: 8px;
}

.stream-btn {
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: rgba(11, 16, 36, 0.8);
  color: #e2e8f0;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.stream-btn.active {
  background: rgba(0, 212, 255, 0.2);
  border-color: rgba(0, 212, 255, 0.6);
  color: #00d4ff;
}

.stream-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.live-player-wrapper {
  flex: 1;
  overflow: hidden;
  padding: 12px;
  display: flex;
  flex-direction: column;
}


@media (max-width: 1180px) {
  .dashboard-content {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    height: auto;
  }

  .side-panel {
    order: 2;
    height: auto;
    overflow: visible;
  }

  .main-view {
    order: 1;
    height: auto;
  }

  .viewer-grid {
    grid-template-columns: 1fr;
    height: auto;
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
