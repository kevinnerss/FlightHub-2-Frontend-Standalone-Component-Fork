<template>
  <div class="dji-dashboard h-screen flex flex-col">
    <!-- 顶部导航 -->
    <div class="header bg-white border-b flex items-center justify-between px-4 h-16 flex-shrink-0">
      <div class="flex items-center">
        <h1 class="text-xl font-bold">无人机巡检主控台</h1>
      </div>
      <div class="flex items-center gap-2">
        <el-button @click="resetView">重置视角</el-button>
        <el-button @click="toggleWireframe">{{ wireframe ? '实体模式' : '线框模式' }}</el-button>
      </div>
    </div>
    
    <!-- 主内容区 -->
    <div class="main-content flex flex-1 overflow-hidden">
      <!-- 左侧控制面板 -->
      <div class="left-panel w-60 bg-white border-r p-4 overflow-y-auto flex-shrink-0">
        <!-- 航线管理 -->
        <div class="panel-section mb-6">
          <h3 class="text-base font-medium mb-3">航线管理</h3>
          <div class="space-y-2">
            <!-- <el-button type="primary" @click="openWaylineCreation" class="w-full" :disabled="!fh2Loaded">新增航线</el-button> -->
            
            <!-- 当FH2未加载时，显示我们的备用航线列表组件 -->
            <WaylineFallback 
              v-if="!fh2Loaded" 
              class="mt-4" 
              :current-selected-id="selectedWayline?.id"
              @wayline-selected="handleWaylineSelected"
            />
            
            <div v-else class="text-sm text-gray-500">
              <p>航线列表将在这里显示（由大疆组件提供）</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 3D模型视图区域 -->
      <div class="model-view flex-1 flex flex-col">
        <!-- 任务进度条 -->
        <div class="progress-container bg-white border-b p-4">
          <h3 class="text-base font-medium mb-2">任务进度</h3>
          <TaskProgressBar 
            :progress="taskProgress"
            :current-task="currentTask"
            :remaining-time="remainingTime"
            :completed-tasks="completedTasks"
            :total-tasks="totalTasks"
          />
        </div>
        
        <!-- Cesium容器 -->
        <div ref="cesiumWrapper" class="cesium-wrapper flex-1 relative">
          <!-- 加载指示器 -->
          <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 z-10">
            <div class="flex flex-col items-center">
              <div class="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-2"></div>
              <span class="text-white">正在加载模型...</span>
            </div>
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
          
          <!-- 显示FH2加载状态提示
          <div v-if="!fh2Loaded && !loading && !error" class="absolute top-4 right-4 z-10">
            <el-alert
              title="大疆组件未正确加载，使用备用功能"
              type="warning"
              show-icon
              :closable="false"
              class="max-w-xs"
            />
          </div> -->
        </div>
      </div>
      
      <!-- 右侧控制面板 -->
      <div class="right-panel w-60 bg-white border-l p-4 overflow-y-auto flex-shrink-0">
        <!-- 报警信息 -->
        <div class="panel-section mb-6">
          <h3 class="text-base font-medium mb-3">报警信息</h3>
          <div class="mb-2 text-sm">
            <span v-if="selectedWayline">
              当前航线: {{ selectedWayline.name }}
            </span>
            <span v-else class="text-gray-500">
              未选择航线
            </span>
          </div>
          <div v-if="loadingAlarms" class="loading-container h-64 flex items-center justify-center">
            <el-spinner type="primary" />
          </div>
          <AlarmPanel 
            v-else
            :alarms="getFilteredAlarms()"
            @refresh="handleAlarmRefresh"
            @view-detail="handleViewAlarmDetail"
            @process-alarm="handleProcessAlarm"
            class="h-64"
          />
        </div>
        
        <!-- 实时监控 -->
        <div class="panel-section mb-6">
          <h3 class="text-base font-medium mb-3">实时监控</h3>
          <div class="h-32 flex items-center justify-center">
            <p class="text-gray-500 text-sm">实时监控将在这里显示（由大疆组件提供）</p>
          </div>
        </div>
        
        <!-- 无人机控制 -->
        <div class="panel-section mb-6">
          <h3 class="text-base font-medium mb-3">无人机控制</h3>
          <div class="h-32 flex items-center justify-center">
            <p class="text-gray-500 text-sm">控制面板将在这里显示（由大疆组件提供）</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 航线创建对话框 -->
    <el-dialog
      v-model="showWaylineCreation"
      title="创建航线"
      width="90%"
      height="90%"
      destroy-on-close
    >
      <div style="height: 70vh">
        <DjiWaylineCreation 
          v-if="showWaylineCreation"
          ref="waylineCreationComponent"
          :config="djiConfig"
        />
      </div>
    </el-dialog>
    
    <!-- 告警详情弹窗 -->
    <el-dialog
      v-model="showAlarmDetail"
      title="告警详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="currentAlarm" class="alarm-detail-container">
        <div class="detail-row">
          <div class="detail-label">告警ID：</div>
          <div class="detail-value">{{ currentAlarm.id }}</div>
        </div>
        
        <div class="detail-row">
          <div class="detail-label">告警类型：</div>
          <div class="detail-value">{{ currentAlarm.category_details?.name || '未分类' }}</div>
        </div>
        
        <div class="detail-row">
          <div class="detail-label">告警状态：</div>
          <div class="detail-value">
            <el-tag :type="currentAlarm.status === 'PENDING' || currentAlarm.status === 'PROCESSING' ? 'warning' : currentAlarm.status === 'COMPLETED' ? 'success' : 'info'">
              {{ getStatusText(currentAlarm.status) }}
            </el-tag>
          </div>
        </div>
        
        <div class="detail-row">
          <div class="detail-label">告警时间：</div>
          <div class="detail-value">{{ currentAlarm.created_at ? new Date(currentAlarm.created_at).toLocaleString('zh-CN') : '--' }}</div>
        </div>
        
        <div class="detail-row">
          <div class="detail-label">告警位置：</div>
          <div class="detail-value">坐标({{ currentAlarm.latitude || '--' }}, {{ currentAlarm.longitude || '--' }})</div>
        </div>
        
        <div class="detail-row">
          <div class="detail-label">航线信息：</div>
          <div class="detail-value">{{ currentAlarm.wayline?.name || currentAlarm.wayline_details?.name || '未知航线' }}</div>
        </div>
        
        <div class="detail-row">
          <div class="detail-label">告警描述：</div>
          <div class="detail-value full-width">{{ currentAlarm.content || '--' }}</div>
        </div>
        
        <div v-if="currentAlarm.specific_data" class="detail-row">
          <div class="detail-label">特定详情：</div>
          <div class="detail-value full-width">{{ JSON.stringify(currentAlarm.specific_data, null, 2) }}</div>
        </div>
        
        <div v-if="currentAlarm.image_url" class="detail-row">
          <div class="detail-label">告警图片：</div>
          <div class="detail-value full-width">
            <el-image
              :src="currentAlarm.image_url"
              :preview-src-list="[currentAlarm.image_url]"
              fit="contain"
              style="max-width: 100%; max-height: 400px; cursor: zoom-in"
            />
          </div>
        </div>
      </div>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="showAlarmDetail = false">关闭</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.alarm-detail-container {
  padding: 10px 0;
}

.detail-row {
  margin-bottom: 20px;
  display: flex;
  align-items: flex-start;
}

.detail-label {
  width: 100px;
  font-weight: bold;
  color: #606266;
  margin-right: 10px;
}

.detail-value {
  flex: 1;
  color: #303133;
}

.full-width {
  word-break: break-all;
  line-height: 1.8;
}
</style>

<script>
import { DjiWaylineCreation } from '../djispace-components'
import TaskProgressBar from '../components/TaskProgressBar.vue'
import AlarmPanel from '../components/AlarmPanel.vue'
import WaylineFallback from '../components/WaylineFallback.vue'
import alarmApi from '../api/alarmApi.js'

export default {
  name: 'DjiDashboard',
  components: {
    DjiWaylineCreation,
    TaskProgressBar,
    AlarmPanel,
    WaylineFallback
  },
  data() {
    return {
      showWaylineCreation: false,
      taskProgress: 65,
      currentTask: '变电站设备检查',
      remainingTime: '12:45',
      completedTasks: 8,
      totalTasks: 12,
      // Cesium相关数据
      viewer: null,
      tileset: null,
      loading: false,
      error: '',
      wireframe: false,
      resizeObserver: null,
      debouncedForceResize: null,
      // 大疆组件加载状态
      fh2Loaded: false,
      // 全局变量：当前选中的航线
      selectedWayline: null,
      // 告警信息
      alarms: [],
      // 告警加载状态
      loadingAlarms: false,
      // 告警详情弹窗
      showAlarmDetail: false,
      currentAlarm: null,
      // 配置信息需要根据实际环境进行修改
      djiConfig: {
        serverUrl: 'http://your-dji-server-ip-or-domain:30812',
        wssUrl: 'ws://your-dji-server-ip-or-domain:30812/duplex/web',
        hostUrl: 'http://your-dji-server-ip-or-domain',
        // 复制 prjId 到这里
        prjId: 'cdca2736-8096-4729-9bc7-497ad5b60d5e',
        // 复制 projectToken 到这里
        projectToken: 'your-project-token-here'
      },
      // 模拟报警数据，添加航线ID关联
      mockAlarms: [
        {
          id: 1,
          title: '电力线异常发热',
          description: '在坐标(23.124, 113.235)处检测到电力线温度异常升高，可能存在线路老化或过载情况。',
          timestamp: '2024-01-15T14:22:35',
          location: '变电站A区域-东线路',
          type: '温度异常',
          severity: '高',
          imageUrl: 'https://picsum.photos/800/600?random=1',
          waylineId: 1
        },
        {
          id: 2,
          title: '绝缘子损伤',
          description: '在铁塔#128处发现绝缘子表面有明显裂纹，需要进一步检查。',
          timestamp: '2024-01-15T13:45:12',
          location: '铁塔#128',
          type: '设备损伤',
          severity: '中',
          imageUrl: 'https://picsum.photos/800/600?random=2',
          waylineId: 1
        },
        {
          id: 3,
          title: '无人机信号弱',
          description: '在航线中段区域信号强度明显减弱，建议调整飞行高度。',
          timestamp: '2024-01-15T12:30:45',
          location: '桥梁中部区域',
          type: '信号异常',
          severity: '低',
          imageUrl: 'https://picsum.photos/800/600?random=3',
          waylineId: 2
        },
        {
          id: 4,
          title: '电池电量警告',
          description: '无人机电池电量低于30%，建议尽快返航。',
          timestamp: '2024-01-15T11:15:20',
          location: '河道巡查区段',
          type: '电量警告',
          severity: '中',
          imageUrl: 'https://picsum.photos/800/600?random=4',
          waylineId: 3
        }
      ]
    }
  },
  async mounted() {
    // 检查FH2是否已加载
    this.checkFh2Availability()
    
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
  },
  methods: {
    // 检查FH2是否可用
    checkFh2Availability() {
      // 检查全局是否存在FH2对象
      if (typeof window.FH2 !== 'undefined') {
        this.fh2Loaded = true
        console.log('FH2已成功加载')
      } else {
        this.fh2Loaded = false
        console.warn('FH2未正确加载，将使用备用组件')
        
        // 设置一个定时器，再次检查FH2是否加载完成
        setTimeout(() => {
          this.checkFh2Availability()
        }, 1000)
      }
    },
    
    openWaylineCreation() {
      if (!this.fh2Loaded) {
        this.$message.warning('大疆组件未正确加载，无法创建航线')
        return
      }
      this.showWaylineCreation = true
    },
    handleAlarmRefresh() {
      console.log('刷新报警信息')
      // 如果有选中的航线，刷新告警信息
      if (this.selectedWayline) {
        this.fetchAlarmsByWayline(this.selectedWayline.id)
      }
    },
    handleViewAlarmDetail(alarm) {
      console.log('查看报警详情:', alarm)
      this.currentAlarm = alarm
      this.showAlarmDetail = true
    },
    handleProcessAlarm(alarmId) {
      console.log('处理报警:', alarmId)
      // 从alarms数组中移除已处理的报警
      this.alarms = this.alarms.filter(alarm => alarm.id !== alarmId)
      
      // 调用API更新告警状态
      this.updateAlarmStatus(alarmId)
    },
    
    // 更新告警状态
    async updateAlarmStatus(alarmId) {
      try {
        // 根据后端模型，正确的完成状态是'COMPLETED'
        await alarmApi.patchAlarm(alarmId, { status: 'COMPLETED' })
        console.log('告警状态更新成功')
      } catch (error) {
        console.error('更新告警状态失败:', error)
        // 不影响前端显示，仅记录错误
      }
    },
    
    // 处理航线选择事件
    handleWaylineSelected(wayline) {
      console.log('选中航线:', wayline)
      this.selectedWayline = wayline
      // 当选择航线时，获取该航线的告警信息
      this.fetchAlarmsByWayline(wayline.id)
    },
    
    // 根据航线ID获取告警信息
    async fetchAlarmsByWayline(waylineId) {
      if (!waylineId) {
        this.alarms = []
        return
      }
      
      this.loadingAlarms = true
      try {
        // 调用API获取告警信息，使用wayline_id参数过滤
        const response = await alarmApi.getAlarms({ wayline_id: waylineId })
        // 转换API返回的数据格式以适配AlarmPanel组件
        this.alarms = this.transformAlarmData(response)
      } catch (error) {
        console.error('获取告警信息失败:', error)
        this.$message.error('获取告警信息失败，请稍后重试')
        // 出错时使用空数组，避免显示错误数据
        this.alarms = []
      } finally {
        this.loadingAlarms = false
      }
    },
    
    // 转换API返回的告警数据格式
    transformAlarmData(alarmData) {
      // 确保alarmData是数组
      const alarms = Array.isArray(alarmData) ? alarmData : (alarmData.results || [])
      
      // 直接返回后端API的数据，不再转换为旧格式
      // 保留原始字段结构，确保与AlarmPanel组件兼容
      return alarms
    },
    
    // 获取告警严重级别
    getSeverityLevel(level) {
      switch (level) {
        case 3:
        case 'high':
        case '高':
          return '高'
        case 2:
        case 'medium':
        case '中':
          return '中'
        case 1:
        case 'low':
        case '低':
          return '低'
        default:
          return '低'
      }
    },
    
    // 获取当前选中航线的告警信息
    getFilteredAlarms() {
      // 直接返回从API获取的告警信息，因为我们已经根据航线ID过滤过了
      return this.alarms
    },
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
        
        // 等待并确保容器有正确的尺寸
        let attempts = 0;
        const maxAttempts = 20;
        let width, height;
        
        do {
          width = wrapper.offsetWidth
          height = wrapper.offsetHeight
          
          if (width <= 0 || height <= 0) {
            await new Promise(resolve => setTimeout(resolve, 50));
            attempts++;
          } else {
            break;
          }
        } while (attempts < maxAttempts);
        
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
    // 获取状态文本
    getStatusText(status) {
      const statusMap = {
        'PENDING': '待处理',
        'PROCESSING': '处理中',
        'COMPLETED': '已完成',
        'IGNORED': '已忽略'
      }
      return statusMap[status] || status
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
        
        // 更新错误信息
        this.error = ''
        
        // 关键修改：使用百分比而非像素值，让CSS自动处理
        container.style.width = '100%'
        container.style.height = '100%'
        
        // 确保canvas元素也使用百分比
        if (this.viewer && this.viewer.canvas) {
          this.viewer.canvas.style.width = '100%'
          this.viewer.canvas.style.height = '100%'
          console.log('设置canvas样式为100%宽高')
        }
        
        // 直接强制重新创建视图，使用try-catch防止resize方法不存在的错误
        if (this.viewer) {
          console.log('尝试调整视图大小')
          try {
            // 安全调用resize方法
            if (this.viewer.scene && typeof this.viewer.scene.resize === 'function') {
              this.viewer.scene.resize()
            }
            if (typeof this.viewer.resize === 'function') {
              this.viewer.resize()
            }
          } catch (resizeError) {
            console.warn('调整视图大小方法调用失败，但不影响功能:', resizeError)
          }
          
          // 强制重排和重绘
          void container.offsetHeight
        }
      } catch (error) {
        console.error('调整大小失败:', error)
      }
    },
    async loadModel() {
      if (!this.viewer) return
      
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
        this.tileset = await Cesium.Cesium3DTileset.fromUrl('/models/Model_0/tileset.json')
        
        this.viewer.scene.primitives.add(this.tileset)
        
        // 缩放到模型
        if (this.tileset.readyPromise) {
          this.tileset.readyPromise.then(() => {
            this.flyToModel()
          }).catch(error => {
            this.error = '模型加载失败: ' + error.message
            console.error('Tileset loading error:', error)
          }).finally(() => {
            this.loading = false
          })
        } else {
          // 如果没有readyPromise，直接设置状态
          this.flyToModel()
          this.loading = false
        }
      } catch (err) {
        this.error = '模型加载失败: ' + err.message
        this.loading = false
        console.error('Model loading error:', err)
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
    }
  }
}
</script>

<style scoped>
/* 基础布局样式 */
.dji-dashboard {
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

.cesium-wrapper {
  flex: 1;
  position: relative;
  min-height: 0; /* 防止flex子元素溢出 */
  border: 1px solid #f5f5f5; /* 使用浅灰色边框，与页面背景融为一体 */
  border-radius: 4px; /* 添加圆角 */
  margin: 8px;
  margin-top: 0;
}

.left-panel, .right-panel {
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

/* 进度条容器样式 */
.progress-container {
  flex-shrink: 0;
  border: 1px solid #f5f5f5;
  border-radius: 4px;
  margin: 8px;
  margin-bottom: 0;
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
  width: 100%;
  height: 100%;
}

/* 加载状态样式 */
.loading-container {
  background-color: #f5f7fa;
  border-radius: 4px;
}

/* 强制所有元素正确计算大小 */
* {
  box-sizing: border-box;
}
</style>