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

    <div class="detect-type-summary">
      <div class="detect-type-header">
        <div class="detect-type-title">检测类型</div>
        <div class="detect-type-subtitle">rail / contactline / bridge / protected_area</div>
      </div>
      <div class="detect-type-table-wrap">
        <table class="detect-type-table">
          <thead>
          <tr>
            <th>类型</th>
            <th>英文</th>
            <th>关键字</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="t in detectTypes" :key="t.code">
            <td class="type-cell">
              <span class="type-icon">{{ t.icon }}</span>
              <span class="type-name">{{ t.name }}</span>
            </td>
            <td class="code-cell">{{ t.code }}</td>
            <td class="keywords-cell">{{ t.keywords }}</td>
          </tr>
          </tbody>
        </table>
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

        <!-- 实时监控面板（直播流播放器） -->
        <div class="panel-section live-monitor-section">
          <div class="monitor-header">
            <span class="monitor-title">实时直播</span>
            <div class="stream-selector-wrapper">
              <select v-model="selectedStreamId" class="stream-selector">
                <option v-for="stream in liveStreams" :key="stream.id" :value="stream.id">
                  {{ stream.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="live-player-wrapper">
            <LiveStreamPlayer
                v-if="currentStream"
                :key="currentStream.id"
                :stream-id="currentStream.id"
                :stream-name="currentStream.name"
                :zlm-server="zlmServerUrl"
                :auto-play="true"
            />
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
import LiveStreamPlayer from '../components/LiveStreamPlayer.vue'
import alarmApi from '../api/alarmApi.js'
import waylineApi from '../api/waylineApi.js'
import componentConfigApi from '../api/componentConfigApi.js'
import inspectTaskApi from '../api/inspectTaskApi.js'

export default {
  name: 'DjiDashboard',
  components: {
    TaskProgressBar,
    AlarmPanel,
    WaylineFallback,
    LiveStreamPlayer
  },
  data() {
    return {
      detectTypes: [
        { name: '铁路', code: 'rail', icon: '🛤️', keywords: 'rail, 铁路, 轨道' },
        { name: '接触网', code: 'contactline', icon: '⚡', keywords: 'contactline, 接触网, catenary, overhead' },
        { name: '桥梁', code: 'bridge', icon: '🌉', keywords: 'bridge, 桥梁' },
        { name: '保护区', code: 'protected_area', icon: '🛡️', keywords: 'protected_area, 保护区' }
      ],
      taskProgress: 65,
      currentTask: '变电站设备检查',
      remainingTime: '12:45',
      completedTasks: 8,
      totalTasks: 12,
      loading: false,
      error: '',
      globeVisible: true,
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
      liveStreams: [
        { id: 'dock01', name: '1号机场' },
        { id: 'drone01', name: '1号无人机' },
        { id: 'dock02', name: '2号机场' },
        { id: 'drone02', name: '2号无人机' }
      ],
      selectedStreamId: 'dock01',
      actionDetails: [],
      taskPollTimer: null,
      chaseCameraListener: null
    }
  },
  computed: {
    currentStream() {
      return this.liveStreams.find(s => s.id === this.selectedStreamId)
    }
  },
  created() {
    this.cesiumLib = null
    this.viewer = null
    this.tileset = null
    this.waylineEntity = null
    this.droneEntity = null
    this.alarmEntities = []
    this.actionDetailEntities = []
    this.pickHandler = null
  },
  mounted() {
    this.checkFh2Availability()
    this.initSelectedWaylineFromRoute()
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

    async handleWaylineSelected(wayline) {
      console.log('[Dashboard] 用户点击航线:', wayline?.name, wayline?.id);
      this.selectedWayline = wayline;

      // 1. 先加载告警
      this.fetchAlarmsByWayline(wayline.id);

      // 2. 【关键修改】先去获取那些“能显示的蓝点数据”
      let validPoints = [];
      try {
        const res = await waylineApi.getWaylineActionDetails(wayline.id);
        // 保存到 data 中用于画蓝点
        this.actionDetails = Array.isArray(res?.action_details) ? res.action_details : [];
        validPoints = this.actionDetails;

        // 画蓝点 (你之前能看到的部分)
        this.plotActionDetailMarkers(this.actionDetails);
        console.log('[Debug] 成功获取动作详情点，数量:', validPoints.length);
      } catch (e) {
        console.warn('[Debug] 获取动作详情失败', e);
      }

      // 3. 【关键修改】把获取到的蓝点数据，强行传给画线函数作为备用数据源
      // 第三个参数 true 表示：如果主接口没数据，就强制使用传入的 validPoints
      await this.ensureWaylineWithPoints(wayline, validPoints);
    },

// 核心数据解析：增加去重逻辑，防止 NaN
// 修改函数签名，增加 fallbackData 参数
    async ensureWaylineWithPoints(wayline, fallbackData = []) {
      console.log('----------------------------------------------------');
      console.log('[Debug] 开始构建航线，WaylineID:', wayline?.id);

      let finalWayline = { ...wayline };
      let sourceList = [];

      // 1. 尝试从 API 获取详情 (原来的逻辑)
      try {
        const res = await alarmApi.getWaylineDetail(wayline.id);
        const data = res.data || res;

        if (data && Array.isArray(data.action_details) && data.action_details.length > 0) {
          sourceList = data.action_details;
          console.log('[Debug] 来源: alarmApi 详情接口 (数量: ' + sourceList.length + ')');
        }
      } catch (e) {
        console.warn('[Debug] alarmApi 接口调用失败，尝试使用备用数据');
      }

      // 2. 【核心修复】如果主接口没拿到数据，使用传入的 fallbackData (即蓝点数据)
      if (sourceList.length === 0 && fallbackData.length > 0) {
        console.log('[Debug] 来源: 使用备用 fallbackData (蓝点数据) 修复航线, 数量:', fallbackData.length);
        sourceList = fallbackData;
      }

      // 3. 如果还是空的，那就彻底没戏了
      if (sourceList.length === 0) {
        console.error('[Error] 依然没有数据。请检查控制台网络请求，确认后端返回的 JSON。');
        // 打印一个 alert 方便你在界面上直接看到
        alert(`航线 ID ${wayline.id} 没有坐标数据，无法飞行。`);
        return;
      }

      // 4. 解析数据 (打印第一条数据，帮你确认字段名)
      console.log('[Debug] 准备解析的第一条数据样本:', JSON.stringify(sourceList[0]));

      const mappedPoints = [];
      sourceList.forEach((p, i) => {
        // 暴力匹配所有可能的字段名
        const lon = Number(p.lon || p.longitude || p.long || p.x);
        const lat = Number(p.lat || p.latitude || p.y);
        // 高度默认 100
        const alt = Number(p.height || p.altitude || p.ellipsoid_height || p.z || 100);

        if (Number.isFinite(lon) && Number.isFinite(lat)) {
          mappedPoints.push({
            longitude: lon,
            latitude: lat,
            altitude: alt + 50, // 抬高一点
            heading: Number(p.aircraft_heading || p.heading || 0),
            gimbalPitch: Number(p.gimbal_pitch || 0)
          });
        } else {
          if (i === 0) console.warn('[Debug] 第一条数据解析失败，字段不匹配:', p);
        }
      });

      console.log(`[Debug] 解析完成，有效坐标点: ${mappedPoints.length} 个`);

      if (mappedPoints.length > 1) {
        finalWayline.waypoints = mappedPoints;
        // 确保 Vue 响应式更新
        this.selectedWayline = finalWayline;

        // 延迟执行绘制，确保 DOM/Viewer 稳定
        setTimeout(() => {
          this.drawWaylineOnMap(finalWayline);
          this.startFlightSimulation(finalWayline);
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

      // 1. 提取坐标
      const positions = wayline.waypoints.map(p =>
          Cesium.Cartesian3.fromDegrees(p.longitude, p.latitude, p.altitude)
      );

      // 2. 绘制航线 (使用纯色，确保可见性)
      this.waylineEntity = this.viewer.entities.add({
        name: wayline.name || '航线',
        polyline: {
          positions: positions,
          width: 5, // 稍微调细一点，太宽有时候会穿模
          // 暂时不用 PolylineGlowMaterialProperty，改用纯色排查问题
          material: Cesium.Color.YELLOW.withAlpha(0.8),
          clampToGround: false,
          // 增加深度检测失败时的颜色（被地形挡住时显示红色）
          depthFailMaterial: Cesium.Color.RED
        }
      });

      // 3. 绘制航点（保持原样，这部分你已经能看到了）
      positions.forEach((pos) => {
        this.viewer.entities.add({
          position: pos,
          point: {
            pixelSize: 8,
            color: Cesium.Color.RED,
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 2,
            disableDepthTestDistance: Number.POSITIVE_INFINITY // 确保点永远在最上层
          }
        });
      });

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
    startFlightSimulation(wayline) {
      const Cesium = this.cesiumLib || window.Cesium;
      if (!this.viewer || !wayline?.waypoints?.length) return;

      // 1. 清理工作
      if (this.droneEntity) {
        this.viewer.entities.remove(this.droneEntity);
        this.droneEntity = null;
      }
      if (this.chaseCameraListener) {
        this.viewer.scene.postUpdate.removeEventListener(this.chaseCameraListener);
        this.chaseCameraListener = null;
      }

      // ----------------------------------------------------------------
      // 【步骤 1】数据分组 (Grouping)
      // 将连续坐标相同的点，归纳为一个 "Group" (站点)
      // ----------------------------------------------------------------
      const groups = [];
      let currentGroup = null;

      wayline.waypoints.forEach((pt) => {
        // 第一次循环，或者发现新点距离很远，就创建新组
        const isNewLocation = !currentGroup ||
            (Math.abs(pt.latitude - currentGroup.lat) > 0.0000001 ||
                Math.abs(pt.longitude - currentGroup.lon) > 0.0000001);

        if (isNewLocation) {
          // 开启一个新站点
          currentGroup = {
            lat: pt.latitude,
            lon: pt.longitude,
            alt: pt.altitude,
            // 记录该位置下所有的动作点数据
            actions: [pt]
          };
          groups.push(currentGroup);
        } else {
          // 还是在老地方，只是角度不一样，加入当前站点
          currentGroup.actions.push(pt);
        }
      });

      console.log(`[Debug] 原始动作点: ${wayline.waypoints.length} -> 合并为站点: ${groups.length} 个`);

      // 2. 初始化属性
      const positionProp = new Cesium.SampledPositionProperty();
      const orientationProp = new Cesium.SampledProperty(Cesium.Quaternion);
      const cameraOffsetProp = new Cesium.SampledProperty(Cesium.Cartesian3);

      positionProp.setInterpolationOptions({ interpolationDegree: 1, interpolationAlgorithm: Cesium.LinearApproximation });
      orientationProp.setInterpolationOptions({ interpolationDegree: 1, interpolationAlgorithm: Cesium.LinearApproximation });
      cameraOffsetProp.setInterpolationOptions({ interpolationDegree: 1, interpolationAlgorithm: Cesium.LinearApproximation });

      // 3. 配置参数
      const flySpeed = 2; // 飞行速度
      const modelHeadingOffset = Cesium.Math.toRadians(-90); // 模型修正

      // 视角配置
      const offsetFar = new Cesium.Cartesian3(-8, 0, 3); // 第三人称
      const offsetNear = new Cesium.Cartesian3(2, 0, 0);   // 特写

      // 4. 构建时间轴
      const startJulian = Cesium.JulianDate.now();
      let currentTime = startJulian.clone();

      // ==========================================
      // 【步骤 2】外层循环：遍历物理站点 (Groups)
      // ==========================================
      for (let i = 0; i < groups.length; i++) {
        const group = groups[i];
        const nextGroup = groups[i + 1]; // 下一个物理站点

        // 当前站点的固定坐标
        const pos = Cesium.Cartesian3.fromDegrees(group.lon, group.lat, group.alt);

        // A. 计算【飞行航向】 (Fly Heading) - 用于到达和离开
        let flyHeading = 0;
        if (nextGroup) {
          const nextPos = Cesium.Cartesian3.fromDegrees(nextGroup.lon, nextGroup.lat, nextGroup.alt);
          flyHeading = this.calculateHeading(pos, nextPos);
        } else {
          // 最后一个点，沿用上一次
          flyHeading = this._lastFlyHeading || 0;
        }
        this._lastFlyHeading = flyHeading; // 暂存

        const quatFly = Cesium.Transforms.headingPitchRollQuaternion(
            pos,
            new Cesium.HeadingPitchRoll(flyHeading + modelHeadingOffset, 0, 0)
        );

        // ----------------------------------------
        // 阶段 0: 到达站点 (Arrive)
        // ----------------------------------------
        // 如果是第一个点，初始化状态；如果是后续点，这里是飞过来的终点
        positionProp.addSample(currentTime, pos);
        orientationProp.addSample(currentTime, quatFly); // 保持飞行姿态到达
        cameraOffsetProp.addSample(currentTime, offsetFar);

        // ==========================================
        // 【步骤 3】内层循环：遍历该站点的所有动作
        // ==========================================
        for (let j = 0; j < group.actions.length; j++) {
          const actionPt = group.actions[j];

          // 1. 计算当前动作的拍摄角度
          let aircraftHeadingInfo = Number(actionPt.aircraft_heading || actionPt.gimbal_yaw || 0);
          // 转换角度 (根据你的模型朝向微调，这里假设是 -90 修正)
          let shootHeading = Cesium.Math.toRadians(-aircraftHeadingInfo) + modelHeadingOffset;

          const quatShoot = Cesium.Transforms.headingPitchRollQuaternion(
              pos,
              new Cesium.HeadingPitchRoll(shootHeading, 0, 0)
          );

          // 动作 A: 转头 (Rotate)
          // 无论之前是刚飞过来(quatFly)，还是刚做完上一个动作(prevQuatShoot)，都花 1.5s 转到当前角度
          currentTime = Cesium.JulianDate.addSeconds(currentTime, 1.5, new Cesium.JulianDate());
          positionProp.addSample(currentTime, pos);
          orientationProp.addSample(currentTime, quatShoot); // 【转头】
          cameraOffsetProp.addSample(currentTime, offsetFar);

          // 动作 B: 放大 (Zoom In)
          currentTime = Cesium.JulianDate.addSeconds(currentTime, 1.5, new Cesium.JulianDate());
          positionProp.addSample(currentTime, pos);
          orientationProp.addSample(currentTime, quatShoot);
          cameraOffsetProp.addSample(currentTime, offsetNear); // 【放大】

          // 动作 C: 保持 (Hold)
          currentTime = Cesium.JulianDate.addSeconds(currentTime, 2.0, new Cesium.JulianDate());
          positionProp.addSample(currentTime, pos);
          orientationProp.addSample(currentTime, quatShoot);
          cameraOffsetProp.addSample(currentTime, offsetNear);

          // 动作 D: 缩小 (Zoom Out)
          currentTime = Cesium.JulianDate.addSeconds(currentTime, 1.5, new Cesium.JulianDate());
          positionProp.addSample(currentTime, pos);
          orientationProp.addSample(currentTime, quatShoot);
          cameraOffsetProp.addSample(currentTime, offsetFar); // 【缩小】

          // 【关键逻辑】
          // 如果这还不是本站点的最后一个动作 (j < length - 1)
          // 那么 loops 回去，直接开始下一个动作的 "Rotate"，不进行回正！
        }

        // ----------------------------------------
        // 阶段 End: 离开站点前，回正 (Reset Heading)
        // 只有当所有动作做完，且还有下一个站点要飞时，才回正
        // ----------------------------------------
        if (nextGroup) {
          // 回正耗时 1秒
          currentTime = Cesium.JulianDate.addSeconds(currentTime, 1.0, new Cesium.JulianDate());
          positionProp.addSample(currentTime, pos);
          orientationProp.addSample(currentTime, quatFly); // 【回正到飞行方向】
          cameraOffsetProp.addSample(currentTime, offsetFar);

          // 飞行过程 (Travel)
          const nextPos = Cesium.Cartesian3.fromDegrees(nextGroup.lon, nextGroup.lat, nextGroup.alt);
          const distance = Cesium.Cartesian3.distance(pos, nextPos);
          const duration = Math.max(distance / flySpeed, 0.1);

          currentTime = Cesium.JulianDate.addSeconds(currentTime, duration, new Cesium.JulianDate());
        }
      }

      // 5. 实体创建 (保持不变)
      const stopJulian = currentTime.clone();
      const availability = new Cesium.TimeIntervalCollection([
        new Cesium.TimeInterval({
          start: Cesium.JulianDate.addSeconds(startJulian, -3600, new Cesium.JulianDate()),
          stop: Cesium.JulianDate.addSeconds(stopJulian, 3600, new Cesium.JulianDate())
        })
      ]);

      this.droneEntity = this.viewer.entities.add({
        availability: availability,
        position: positionProp,
        orientation: orientationProp,
        model: {
          uri: '/models/fly.glb',
          minimumPixelSize: 128,
          maximumScale: 2000,
          scale: 1.0,
          runAnimations: true
        },
        path: {
          resolution: 1,
          material: new Cesium.PolylineGlowMaterialProperty({ glowPower: 0.1, color: Cesium.Color.CYAN }),
          width: 5,
          leadTime: 0,
          trailTime: 9999
        }
      });

      this.viewer.clock.startTime = startJulian.clone();
      this.viewer.clock.stopTime = stopJulian.clone();
      this.viewer.clock.currentTime = startJulian.clone();
      this.viewer.clock.clockRange = Cesium.ClockRange.LOOP_STOP;
      this.viewer.clock.shouldAnimate = true;

      this.enableDynamicChaseCamera(this.droneEntity, cameraOffsetProp);
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

        const time = this.viewer.clock.currentTime;

        // 获取当前时刻的位置和朝向
        const position = entity.position.getValue(time);
        const orientation = entity.orientation.getValue(time);

        if (position && orientation) {
          // A. 计算模型变换矩阵 (Model Matrix)
          // 这个矩阵代表了无人机当前的坐标系：原点在无人机中心，轴向跟随无人机旋转
          const transform = Cesium.Matrix4.fromRotationTranslation(
              Cesium.Matrix3.fromQuaternion(orientation),
              position
          );

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
      controller.inertiaSpin = 0.4;
      controller.inertiaTranslate = 0.4;
      controller.inertiaZoom = 0.4;
      controller.minimumZoomRate = 0.2;
      controller.maximumZoomRate = 500000;
      controller._zoomFactor = 1.5;
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

    startTaskPolling() {
      this.fetchCurrentTask();
      this.taskPollTimer = setInterval(() => {
        this.fetchCurrentTask();
      }, 3000);
    },

    async fetchCurrentTask() {
      try {
        let response = await inspectTaskApi.getInspectTasks({
          detect_status__in: 'scanning,processing',
          ordering: '-updated_at',
          limit: 1
        });
        let tasks = response.results || response.data || [];
        if (tasks.length === 0) {
          response = await inspectTaskApi.getInspectTasks({
            ordering: '-created_at',
            limit: 1
          });
          tasks = response.results || response.data || [];
        }

        if (tasks.length > 0) {
          const task = tasks[0];
          this.currentTask = task.external_task_id || task.dji_task_name || '未命名任务';
          this.totalTasks = task.total_images || 0;
          this.completedTasks = task.completed_images || 0;
          if (this.totalTasks > 0) {
            this.taskProgress = Math.round((this.completedTasks / this.totalTasks) * 100);
          } else {
            this.taskProgress = 0;
          }
        }
      } catch (error) {
        console.error('获取当前任务失败:', error);
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
      const entities = [];
      details.forEach(d => {
        const lat = Number(d.lat);
        const lon = Number(d.lon);
        const h = Number(d.height || 0);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
        const position = Cesium.Cartesian3.fromDegrees(lon, lat, h);
        const entity = this.viewer.entities.add({
          position,
          point: {
            pixelSize: 8,
            color: Cesium.Color.CYAN.withAlpha(0.9),
            outlineColor: Cesium.Color.BLACK,
            outlineWidth: 1,
            disableDepthTestDistance: Number.POSITIVE_INFINITY
          },
          label: {
            text: d.uuid ? d.uuid.slice(0, 8) : 'action',
            font: '12px sans-serif',
            fillColor: Cesium.Color.WHITE,
            outlineColor: Cesium.Color.BLACK,
            outlineWidth: 2,
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            pixelOffset: new Cesium.Cartesian2(0, -20),
            disableDepthTestDistance: Number.POSITIVE_INFINITY
          }
        });
        entities.push(entity);
      });
      this.actionDetailEntities = entities;
    },
    clearActionDetailMarkers() {
      if (this.viewer && this.actionDetailEntities.length) {
        this.actionDetailEntities.forEach(e => this.viewer.entities.remove(e));
      }
      this.actionDetailEntities = [];
    },

    handleLocateAlarm(alarm) {
      const lat = this.toNumber(alarm?.latitude);
      const lon = this.toNumber(alarm?.longitude);
      if (!Number.isFinite(lat) || !Number.isFinite(lon) || !this.viewer) return;
      const Cesium = this.cesiumLib || window.Cesium;
      if (!Cesium) return;
      const height = this.toNumber(alarm?.altitude) || 200;
      const destination = Cesium.Cartesian3.fromDegrees(lon, lat, height);
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
        const position = Cesium.Cartesian3.fromDegrees(lon, lat, this.toNumber(alarm.altitude) || 0);
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

/* 直播监控区域样式 */
.live-monitor-section {
  flex: 1;
  min-height: 350px;
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

.stream-selector-wrapper {
  position: relative;
}

.stream-selector {
  background: rgba(11, 16, 36, 0.8);
  border: 1px solid rgba(0, 212, 255, 0.3);
  color: #e2e8f0;
  padding: 4px 24px 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  outline: none;
  cursor: pointer;
  appearance: none; /* 移除默认箭头 */
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2300d4ff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 4px center;
  background-size: 14px;
}

.stream-selector:focus {
  border-color: #00d4ff;
  box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.1);
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