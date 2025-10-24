<template>
  <el-container class="h-screen overflow-hidden bg-gray-50">
    <!-- 左侧导航 -->
    <el-aside width="240px" class="bg-white shadow-sm overflow-hidden">
      <el-card shadow="never" class="h-full border-0">
        <template #header>
          <div class="flex items-center justify-between">
            <span class="text-lg font-medium">航线管理</span>
            <el-button type="primary" size="small" plain>
              新增
            </el-button>
          </div>
        </template>
        <el-scrollbar class="h-[calc(100%-50px)]">
          <drone-route-list 
            :routes="droneRoutes" 
            :selected-route-id="selectedRoute?.id"
            @route-selected="handleRouteSelected"
          />
        </el-scrollbar>
      </el-card>
    </el-aside>
    
    <el-container>
      <!-- 顶部进度条 -->
      <el-header height="60px" class="bg-white border-b p-0">
        <task-progress-bar 
          :progress="taskProgress" 
          :current-task="currentTask" 
          :remaining-time="remainingTime"
          :completed-tasks="completedTasks" 
          :total-tasks="totalTasks"
        />
      </el-header>
      
      <el-container class="p-4 gap-4">
        <!-- 主内容区 - 3D可视化 -->
        <el-main class="p-0">
          <el-card shadow="hover" class="h-full border-0">
            <template #header>
              <div class="flex items-center justify-between">
                <span class="text-lg font-medium">3D可视化</span>
                <div class="flex items-center gap-2">
                  <el-dropdown>
                    <el-button type="primary" size="small" plain>
                      视图模式
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item>标准视图</el-dropdown-item>
                        <el-dropdown-item>俯视图</el-dropdown-item>
                        <el-dropdown-item>侧视图</el-dropdown-item>
                        <el-dropdown-item>第一人称视图</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                  <el-button type="primary" size="small" plain>
                    刷新
                  </el-button>
                </div>
              </div>
            </template>
            <visualization-panel 
              :selected-route="selectedRoute"
              :alarm-points="alarms"
              @view-mode-changed="handleViewModeChanged"
              @layers-changed="handleLayersChanged"
              class="h-[calc(100%-60px)]"
            />
          </el-card>
        </el-main>
        
        <!-- 右侧面板 -->
        <el-aside width="320px" class="space-y-4 overflow-hidden">
          <!-- 报警信息面板 -->
          <el-card shadow="hover" class="h-[35%] border-0">
            <template #header>
              <div class="flex items-center justify-between">
                <span class="text-base font-medium">报警信息</span>
                <el-badge 
                  v-if="alarms.length > 0" 
                  :value="alarms.length" 
                  type="danger"
                />
              </div>
            </template>
            <alarm-panel 
              :alarms="alarms" 
              @alarm-processed="handleAlarmProcessed"
              class="h-[calc(100%-50px)]"
            />
          </el-card>
          
          <!-- 实时监控面板 -->
          <el-card shadow="hover" class="h-[30%] border-0">
            <template #header>
              <div class="flex items-center justify-between">
                <span class="text-base font-medium">实时监控</span>
                <el-button 
                  type="primary" 
                  size="small" 
                  plain 
                  @click="handleRefreshStream"
                  :loading="!isStreaming"
                >
                  {{ isStreaming ? '刷新' : '加载中' }}
                </el-button>
              </div>
            </template>
            <monitor-panel 
              :video-stream-url="videoStreamUrl"
              :is-streaming="isStreaming"
              :drone-status="droneStatus"
              :battery-level="batteryLevel"
              :altitude="currentAltitude"
              :speed="currentSpeed"
              class="h-[calc(100%-50px)]"
            />
          </el-card>
          
          <!-- 控制面板 -->
          <el-card shadow="hover" class="h-[35%] border-0">
            <template #header>
              <div class="flex items-center justify-between">
                <span class="text-base font-medium">无人机控制</span>
                <el-tag :type="getStatusTagType(droneStatus)">
                  {{ droneStatus }}
                </el-tag>
              </div>
            </template>
            <control-panel 
              :current-status="droneStatus"
              :target-altitude="targetAltitude"
              :target-speed="targetSpeed"
              @control-action="handleControlAction"
              @update-altitude="handleUpdateAltitude"
              @update-speed="handleUpdateSpeed"
              @emergency-stop="handleEmergencyStop"
              class="h-[calc(100%-50px)]"
            />
          </el-card>
        </el-aside>
      </el-container>
    </el-container>
  </el-container>
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
      this.$confirm('确定执行紧急停止？这将立即中断所有飞行操作。', '紧急操作', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.emergencyStop()
        this.$message.success('紧急停止指令已执行')
      }).catch(() => {
        this.$message.info('已取消紧急停止操作')
      })
    },
    
    // 获取状态标签类型
    getStatusTagType(status) {
      switch (status) {
        case '飞行中':
          return 'success'
        case '悬停中':
          return 'info'
        case '待命':
          return 'primary'
        case '返回中':
          return 'warning'
        case '已停止':
          return 'danger'
        default:
          return 'info'
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