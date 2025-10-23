<template>
  <div class="p-4 h-screen overflow-hidden">
    <div class="grid-layout h-full">
      <!-- 左侧导航 -->
      <div class="grid-sidebar overflow-hidden">
        <drone-route-list 
          :routes="droneRoutes" 
          :selected-route-id="selectedRoute?.id"
          @route-selected="handleRouteSelected"
        />
      </div>
      
      <!-- 顶部进度条 -->
      <div class="grid-header">
        <task-progress-bar 
          :progress="taskProgress" 
          :current-task="currentTask" 
          :remaining-time="remainingTime"
          :completed-tasks="completedTasks" 
          :total-tasks="totalTasks"
        />
      </div>
      
      <!-- 主内容区 - 3D可视化 -->
      <div class="grid-main">
        <visualization-panel 
          :selected-route="selectedRoute"
          :alarm-points="alarms"
          @view-mode-changed="handleViewModeChanged"
          @layers-changed="handleLayersChanged"
        />
      </div>
      
      <!-- 右侧面板 -->
      <div class="grid-right flex flex-col gap-4 overflow-hidden">
        <!-- 报警信息面板 -->
        <alarm-panel 
          :alarms="alarms" 
          @alarm-processed="handleAlarmProcessed"
          class="flex-grow"
        />
        
        <!-- 实时监控面板 -->
        <monitor-panel 
          :video-stream-url="videoStreamUrl"
          :is-streaming="isStreaming"
          :drone-status="droneStatus"
          :battery-level="batteryLevel"
          :altitude="currentAltitude"
          :speed="currentSpeed"
          @refresh-stream="handleRefreshStream"
        />
        
        <!-- 控制面板 -->
        <control-panel 
          :current-status="droneStatus"
          :target-altitude="targetAltitude"
          :target-speed="targetSpeed"
          @control-action="handleControlAction"
          @update-altitude="handleUpdateAltitude"
          @update-speed="handleUpdateSpeed"
          @emergency-stop="handleEmergencyStop"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import DroneRouteList from '../components/DroneRouteList.vue'
import TaskProgressBar from '../components/TaskProgressBar.vue'
import AlarmPanel from '../components/AlarmPanel.vue'
import MonitorPanel from '../components/MonitorPanel.vue'
import ControlPanel from '../components/ControlPanel.vue'
import VisualizationPanel from '../components/VisualizationPanel.vue'

export default {
  name: 'Dashboard',
  components: {
    DroneRouteList,
    TaskProgressBar,
    AlarmPanel,
    MonitorPanel,
    ControlPanel,
    VisualizationPanel
  },
  computed: {
    ...mapState([
      'droneRoutes',
      'selectedRoute',
      'taskProgress',
      'currentTask',
      'remainingTime',
      'completedTasks',
      'totalTasks',
      'alarms',
      'droneStatus',
      'batteryLevel',
      'currentAltitude',
      'currentSpeed',
      'targetAltitude',
      'targetSpeed',
      'videoStreamUrl',
      'isStreaming'
    ])
  },
  async mounted() {
    // 初始化系统数据
    await this.initializeSystem()
    
    // 启动数据模拟更新
    this.startDataSimulation()
  },
  methods: {
    ...mapActions([
      'initializeSystem',
      'selectRoute',
      'processAlarm',
      'controlDrone',
      'updateTargetAltitude',
      'updateTargetSpeed',
      'emergencyStop',
      'refreshStream'
    ]),
    
    // 处理航线选择
    handleRouteSelected(routeId) {
      const route = this.droneRoutes.find(r => r.id === routeId)
      this.selectRoute(route)
    },
    
    // 处理报警
    handleAlarmProcessed(alarmId) {
      this.processAlarm(alarmId)
    },
    
    // 处理控制动作
    handleControlAction(action) {
      this.controlDrone(action)
    },
    
    // 处理高度更新
    handleUpdateAltitude(altitude) {
      this.updateTargetAltitude(altitude)
    },
    
    // 处理速度更新
    handleUpdateSpeed(speed) {
      this.updateTargetSpeed(speed)
    },
    
    // 处理紧急停止
    handleEmergencyStop() {
      if (confirm('确定执行紧急停止？这将立即中断所有飞行操作。')) {
        this.emergencyStop()
      }
    },
    
    // 处理刷新视频流
    handleRefreshStream() {
      this.refreshStream()
    },
    
    // 处理视图模式变更
    handleViewModeChanged(viewMode) {
      console.log('视图模式变更为:', viewMode)
    },
    
    // 处理图层变更
    handleLayersChanged(layers) {
      console.log('图层设置变更:', layers)
    },
    
    // 启动数据模拟
    startDataSimulation() {
      // 模拟电池电量逐渐下降
      setInterval(() => {
        if (this.droneStatus === '飞行中' && this.batteryLevel > 0) {
          this.$store.commit('SET_BATTERY_LEVEL', Math.max(0, this.batteryLevel - 0.5))
        }
      }, 10000)
      
      // 模拟当前高度和目标高度逐渐接近
      setInterval(() => {
        if (this.droneStatus === '飞行中' && Math.abs(this.currentAltitude - this.targetAltitude) > 1) {
          const newAltitude = this.currentAltitude + (this.targetAltitude > this.currentAltitude ? 1 : -1)
          this.$store.commit('SET_CURRENT_ALTITUDE', newAltitude)
        }
        if (this.droneStatus === '飞行中' && Math.abs(this.currentSpeed - this.targetSpeed) > 0.5) {
          const newSpeed = this.currentSpeed + (this.targetSpeed > this.currentSpeed ? 0.5 : -0.5)
          this.$store.commit('SET_CURRENT_SPEED', newSpeed)
        }
      }, 2000)
      
      // 模拟任务进度更新
      setInterval(() => {
        if (this.droneStatus === '飞行中' && this.taskProgress < 100) {
          this.$store.commit('SET_TASK_PROGRESS', Math.min(100, this.taskProgress + 0.5))
        }
      }, 5000)
    }
  }
}
</script>