<template>
  <div class="dji-dashboard">
    <el-container class="h-screen overflow-hidden">
      <!-- 左侧导航 -->
      <el-aside width="240px" class="bg-white shadow-sm overflow-hidden">
        <el-card shadow="never" class="h-full border-0">
          <template #header>
            <div class="flex items-center justify-between">
              <span class="text-lg font-medium">航线管理</span>
              <el-button type="primary" size="small" plain @click="openWaylineCreation">
                新增
              </el-button>
            </div>
          </template>
          <el-scrollbar class="h-[calc(100%-50px)]">
            <!-- 使用大疆提供的航线列表组件 -->
            <div class="p-4">
              <p class="text-gray-500 text-sm">航线列表将在这里显示（由大疆组件提供）</p>
            </div>
          </el-scrollbar>
        </el-card>
      </el-aside>
      
      <el-container>
        <!-- 顶部进度条 -->
        <el-header height="60px" class="bg-white border-b p-0">
          <TaskProgressBar 
            :progress="taskProgress"
            :current-task="currentTask"
            :remaining-time="remainingTime"
            :completed-tasks="completedTasks"
            :total-tasks="totalTasks"
          />
        </el-header>
        
        <el-container class="p-4 gap-4">
          <!-- 主内容区 - 项目地图 -->
          <el-main class="p-0">
            <el-card shadow="hover" class="h-full border-0">
              <template #header>
                <div class="flex items-center justify-between">
                  <span class="text-lg font-medium">项目地图</span>
                  <div class="flex items-center gap-2">
                    <el-button type="primary" size="small" plain @click="refreshProject">
                      刷新
                    </el-button>
                  </div>
                </div>
              </template>
              <DjiProject 
                ref="projectComponent"
                :config="djiConfig"
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
                </div>
              </template>
              <AlarmPanel 
                :alarms="mockAlarms"
                @refresh="handleAlarmRefresh"
                @view-detail="handleViewAlarmDetail"
                @process-alarm="handleProcessAlarm"
                class="h-[calc(100%-50px)]"
              />
            </el-card>
            
            <!-- 实时监控面板 -->
            <el-card shadow="hover" class="h-[30%] border-0">
              <template #header>
                <div class="flex items-center justify-between">
                  <span class="text-base font-medium">实时监控</span>
                </div>
              </template>
              <div class="h-[calc(100%-50px)] flex items-center justify-center">
                <p class="text-gray-500 text-sm">实时监控将在这里显示（由大疆组件提供）</p>
              </div>
            </el-card>
            
            <!-- 控制面板 -->
            <el-card shadow="hover" class="h-[35%] border-0">
              <template #header>
                <div class="flex items-center justify-between">
                  <span class="text-base font-medium">无人机控制</span>
                </div>
              </template>
              <div class="h-[calc(100%-50px)] flex items-center justify-center">
                <p class="text-gray-500 text-sm">控制面板将在这里显示（由大疆组件提供）</p>
              </div>
            </el-card>
          </el-aside>
        </el-container>
      </el-container>
    </el-container>
    
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
  </div>
</template>

<script>
import { DjiProject, DjiWaylineCreation } from '../djispace-components'
import TaskProgressBar from '../components/TaskProgressBar.vue'
import AlarmPanel from '../components/AlarmPanel.vue'

export default {
  name: 'DjiDashboard',
  components: {
    DjiProject,
    DjiWaylineCreation,
    TaskProgressBar,
    AlarmPanel
  },
  data() {
    return {
      showWaylineCreation: false,
      taskProgress: 65,
      currentTask: '变电站设备检查',
      remainingTime: '12:45',
      completedTasks: 8,
      totalTasks: 12,
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
      // 模拟报警数据
      mockAlarms: [
        {
          id: 1,
          title: '电力线异常发热',
          description: '在坐标(23.124, 113.235)处检测到电力线温度异常升高，可能存在线路老化或过载情况。',
          timestamp: '2024-01-15T14:22:35',
          location: '变电站A区域-东线路',
          type: '温度异常',
          severity: '高',
          imageUrl: 'https://picsum.photos/800/600?random=1'
        },
        {
          id: 2,
          title: '绝缘子损伤',
          description: '在铁塔#128处发现绝缘子表面有明显裂纹，需要进一步检查。',
          timestamp: '2024-01-15T13:45:12',
          location: '铁塔#128',
          type: '设备损伤',
          severity: '中',
          imageUrl: 'https://picsum.photos/800/600?random=2'
        }
      ]
    }
  },
  methods: {
    openWaylineCreation() {
      this.showWaylineCreation = true
    },
    refreshProject() {
      if (this.$refs.projectComponent) {
        this.$refs.projectComponent.refresh()
      }
    },
    handleAlarmRefresh() {
      console.log('刷新报警信息')
    },
    handleViewAlarmDetail(alarm) {
      console.log('查看报警详情:', alarm)
    },
    handleProcessAlarm(alarmId) {
      console.log('处理报警:', alarmId)
      // 从mockAlarms中移除已处理的报警
      this.mockAlarms = this.mockAlarms.filter(alarm => alarm.id !== alarmId)
    }
  }
}
</script>

<style scoped>
.dji-dashboard {
  width: 100%;
  height: 100%;
}
</style>