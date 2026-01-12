<template>
  <div class="command-center">
    <!-- 顶部标题栏 -->
    <div class="top-header">
      <div class="header-left">
        <div class="logo-placeholder"><img src="/photo/e24eceb32a305d118702799bd1e2c84f.jpg" alt="Logo" class="logo-left" />
</div>
      </div>
      <div class="header-center">
        <div class="main-title">无人机智能巡检平台</div>
        <div class="sub-title">Command & Control Center</div>
      </div>
      <div class="header-right">
        <div class="logo-placeholder"><img src="/photo/e24eceb32a305d118702799bd1e2c84f.jpg" alt="Logo" class="logo-left" />
</div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 左侧统计面板 -->
      <div class="left-panel">
        <!-- 任务统计 -->
        <div class="panel-card">
          <div class="card-header">
            <div class="header-icon">📊</div>
            <div class="header-title">任务统计</div>
          </div>
          <div class="card-body">
            <div class="stat-grid">
              <div class="stat-item">
                <div class="stat-value">{{ stats.totalTasks }}</div>
                <div class="stat-label">总任务数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value text-success">{{ stats.completedTasks }}</div>
                <div class="stat-label">已完成</div>
              </div>
              <div class="stat-item">
                <div class="stat-value text-warning">{{ stats.runningTasks }}</div>
                <div class="stat-label">进行中</div>
              </div>
              <div class="stat-item">
                <div class="stat-value text-danger">{{ stats.failedTasks }}</div>
                <div class="stat-label">失败</div>
              </div>
            </div>
            <div class="progress-ring">
              <svg class="ring-svg" viewBox="0 0 120 120">
                <circle class="ring-bg" cx="60" cy="60" r="50" />
                <circle 
                  class="ring-progress" 
                  cx="60" 
                  cy="60" 
                  r="50" 
                  :style="{ strokeDashoffset: progressOffset }"
                />
              </svg>
              <div class="ring-text">
                <div class="ring-value">{{ completionRate }}%</div>
                <div class="ring-label">完成率</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 任务日历 -->
        <div class="panel-card">
          <div class="card-header">
            <div class="header-icon">📅</div>
            <div class="header-title">任务日历</div>
          </div>
          <div class="card-body">
            <div class="calendar">
              <!-- 月份头部 -->
              <div class="calendar-header">
                <button class="calendar-btn" @click="previousMonth">◀</button>
                <div class="calendar-title">{{ currentYear }}年 {{ currentMonth }}月</div>
                <button class="calendar-btn" @click="nextMonth">▶</button>
              </div>
              <!-- 星期头 -->
              <div class="calendar-weekdays">
                <div class="weekday" v-for="day in weekdays" :key="day">{{ day }}</div>
              </div>
              <!-- 日期网格 -->
              <div class="calendar-days">
                <div 
                  class="day-cell" 
                  v-for="(day, index) in calendarDays" 
                  :key="index"
                  :class="{
                    'other-month': day.isOtherMonth,
                    'today': day.isToday,
                    'has-task': day.hasTask
                  }"
                >
                  <span class="day-number">{{ day.day }}</span>
                  <span v-if="day.hasTask" class="task-badge">{{ day.taskCount }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 实时状态 -->
        <div class="panel-card">
          <div class="card-header">
            <div class="header-icon">📡</div>
            <div class="header-title">告警状态</div>
          </div>
          <div class="card-body">
            <div class="status-list">
              <div class="status-item">
                <div class="status-dot warning"></div>
                <span>待处理: {{ deviceStatus.pendingAlarms }} 条</span>
              </div>
              <div class="status-item">
                <div class="status-dot online"></div>
                <span>处理中: {{ deviceStatus.processingAlarms }} 条</span>
              </div>
              <div class="status-item">
                <div class="status-dot offline"></div>
                <span>已完成: {{ deviceStatus.completedAlarms }} 条</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 航线树 -->
        <div class="panel-card">
          <div class="card-header">
            <div class="header-icon">🌲</div>
            <div class="header-title">航线树</div>
          </div>
          <div class="card-body">
            <div v-if="treeLoading" class="empty-placeholder">加载中...</div>
            <div v-else-if="treeError" class="empty-placeholder">{{ treeError }}</div>
            <div v-else class="tree-container">
              <div class="tree-group" v-for="group in waylineTree" :key="group.type">
                <div class="tree-group-header" @click="toggleGroup(group.type)">
                  <span class="group-name">{{ group.label }}</span>
                  <span class="group-count">（{{ group.count }} 条航线）</span>
                  <span class="toggle-icon">{{ expandedMap[group.type] ? '▼' : '▶' }}</span>
                </div>
                <div class="tree-items" v-show="expandedMap[group.type]">
                  <div class="tree-item" v-for="item in group.items" :key="item.id" @click="selectWayline(item)">
                    <span class="item-name">{{ item.name }}</span>
                    <span class="item-meta" v-if="item.recent_task_time">最近任务：{{ formatTime(item.recent_task_time) }}</span>
                  </div>
                  <div v-if="!group.items.length" class="empty-placeholder">暂无航线</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间3D模型展示区 -->
      <div class="center-panel">
        <div class="model-display-area">
          <div class="placeholder-content">
            <div class="placeholder-icon">🚁</div>
            <div class="placeholder-text">3D模型展示区</div>
            <div class="placeholder-subtitle">3D Model Display Area</div>
          </div>
        </div>
      </div>

      <!-- 右侧统计面板 -->
      <div class="right-panel">
        <!-- 告警统计 -->
        <div class="panel-card">
          <div class="card-header">
            <div class="header-icon">⚠️</div>
            <div class="header-title">告警统计</div>
          </div>
          <div class="card-body">
            <div class="alarm-bar-chart">
              <!-- Y轴刻度线 -->
              <div class="chart-y-axis">
                <div class="y-label" v-for="i in 5" :key="i">{{ Math.floor(maxAlarmCount - (i - 1) * (maxAlarmCount / 4)) }}</div>
              </div>
              <!-- 条形图主体 -->
              <div class="chart-bars">
                <div 
                  class="bar-column" 
                  v-for="item in alarmStats.slice(0, 4)" 
                  :key="item.type"
                >
                  <div class="bar-wrapper">
                    <div 
                      class="bar" 
                      :style="{ 
                        height: getBarHeight(item.count) + '%',
                        backgroundColor: item.color 
                      }"
                    >
                      <span class="bar-count">{{ item.count }}</span>
                    </div>
                  </div>
                  <div class="bar-label">{{ item.type }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 最近事件 -->
        <div class="panel-card">
          <div class="card-header">
            <div class="header-icon">📋</div>
            <div class="header-title">最近事件</div>
          </div>
          <div class="card-body">
            <div class="event-list">
              <div 
                class="event-item" 
                v-for="event in recentEvents" 
                :key="event.id"
              >
                <div class="event-time">{{ formatTime(event.time) }}</div>
                <div class="event-content">
                  <div class="event-title">{{ event.title }}</div>
                  <div class="event-desc">{{ event.description }}</div>
                </div>
                <div class="event-status" :class="event.status">
                  {{ getStatusText(event.status) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部装饰线 -->
    <div class="bottom-decoration">
      <div class="decoration-line"></div>
    </div>
  </div>
</template>

<script>
import alarmApi from '../api/alarmApi.js'
import inspectTaskApi from '../api/inspectTaskApi.js'
import waylineApi from '../api/waylineApi.js'

export default {
  name: 'CommandCenter',
  data() {
    return {
      // 任务统计数据（InspectTask）
      stats: {
        totalTasks: 0,
        completedTasks: 0,  // detect_status='done'
        runningTasks: 0,    // detect_status='processing'
        failedTasks: 0      // detect_status='failed'
      },
      // 日历相关
      currentYear: new Date().getFullYear(),
      currentMonth: new Date().getMonth() + 1,
      weekdays: ['日', '一', '二', '三', '四', '五', '六'],
      taskDates: [], // 存储有任务的日期和任务数
      // 告警统计（Alarm）
      deviceStatus: {
        pendingAlarms: 0,      // status='PENDING'
        processingAlarms: 0,   // status='PROCESSING'
        completedAlarms: 0     // status='COMPLETED'
      },
      // 告警分类统计（按AlarmCategory分组）
      alarmStats: [],
      // 最近事件（最新的InspectTask）
      recentEvents: [],
      // 定时器
      refreshTimer: null,
      waylineTree: [],
      treeLoading: false,
      treeError: '',
      expandedMap: {}
    }
  },
  computed: {
    completionRate() {
      if (this.stats.totalTasks === 0) return 0
      return Math.round((this.stats.completedTasks / this.stats.totalTasks) * 100)
    },
    progressOffset() {
      const circumference = 2 * Math.PI * 50
      return circumference - (circumference * this.completionRate) / 100
    },
    maxAlarmCount() {
      if (this.alarmStats.length === 0) return 10
      const max = Math.max(...this.alarmStats.map(item => item.count))
      return Math.ceil(max * 1.2) // 留出20%的上方空间
    },
    calendarDays() {
      const days = []
      const firstDay = new Date(this.currentYear, this.currentMonth - 1, 1)
      const lastDay = new Date(this.currentYear, this.currentMonth, 0)
      const firstDayOfWeek = firstDay.getDay()
      const daysInMonth = lastDay.getDate()
      
      // 上月填充
      const prevMonthLastDay = new Date(this.currentYear, this.currentMonth - 1, 0).getDate()
      for (let i = firstDayOfWeek - 1; i >= 0; i--) {
        days.push({
          day: prevMonthLastDay - i,
          isOtherMonth: true,
          isToday: false,
          hasTask: false,
          taskCount: 0
        })
      }
      
      // 当月日期
      const today = new Date()
      for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = `${this.currentYear}-${String(this.currentMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`
        const taskInfo = this.taskDates.find(t => t.date === dateStr)
        
        days.push({
          day,
          isOtherMonth: false,
          isToday: today.getFullYear() === this.currentYear && 
                   today.getMonth() + 1 === this.currentMonth && 
                   today.getDate() === day,
          hasTask: !!taskInfo,
          taskCount: taskInfo ? taskInfo.count : 0
        })
      }
      
      // 下月填充
      const remainingDays = 42 - days.length
      for (let day = 1; day <= remainingDays; day++) {
        days.push({
          day,
          isOtherMonth: true,
          isToday: false,
          hasTask: false,
          taskCount: 0
        })
      }
      
      return days
    }
  },
  mounted() {
    this.loadAllData()
    this.loadWaylineTree()
    // 每30秒刷新一次数据
    this.refreshTimer = setInterval(() => {
      this.loadAllData()
    }, 30000)
  },
  beforeUnmount() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer)
    }
  },
  methods: {
    async loadWaylineTree() {
      try {
        this.treeLoading = true
        this.treeError = ''
        const res = await waylineApi.getWaylineTree()
        const groups = res.groups || []
        groups.forEach(g => {
          if (Array.isArray(g.items)) {
            g.items.sort((a, b) => {
              const ta = a.recent_task_time ? new Date(a.recent_task_time).getTime() : 0
              const tb = b.recent_task_time ? new Date(b.recent_task_time).getTime() : 0
              return tb - ta
            })
          }
          if (this.expandedMap[g.type] === undefined) {
            this.$set ? this.$set(this.expandedMap, g.type, true) : (this.expandedMap[g.type] = true)
          }
        })
        this.waylineTree = groups
      } catch (e) {
        this.treeError = '加载失败'
      } finally {
        this.treeLoading = false
      }
    },
    toggleGroup(type) {
      const current = !!this.expandedMap[type]
      if (this.$set) {
        this.$set(this.expandedMap, type, !current)
      } else {
        this.expandedMap[type] = !current
      }
    },
    selectWayline(item) {
      if (!item || !item.id) return
      this.$router.push({ name: 'DjiDashboard', query: { wayline_id: item.id } })
    },
    async loadAllData() {
      await Promise.all([
        this.loadTaskStats(),
        this.loadTaskCalendar(),
        this.loadDeviceStatus(),
        this.loadAlarmStats(),
        this.loadRecentEvents()
      ])
    },
    
    async loadTaskStats() {
      try {
        const tasks = await inspectTaskApi.getInspectTasks({ limit: 10000 })
        const taskList = tasks.results || []
        
        this.stats.totalTasks = taskList.length
        this.stats.completedTasks = taskList.filter(t => t.detect_status === 'done').length
        this.stats.runningTasks = taskList.filter(t => t.detect_status === 'processing').length
        this.stats.failedTasks = taskList.filter(t => t.detect_status === 'failed').length
      } catch (error) {
        console.error('加载任务统计失败:', error)
        this.stats = { totalTasks: 0, completedTasks: 0, runningTasks: 0, failedTasks: 0 }
      }
    },
    
    async loadTaskCalendar() {
      try {
        const tasks = await inspectTaskApi.getInspectTasks({ limit: 10000 })
        const taskList = tasks.results || []
        
        // 统计每个日期的任务数
        const dateMap = {}
        taskList.forEach(task => {
          if (task.created_at) {
            const date = task.created_at.split('T')[0] // 获取YYYY-MM-DD部分
            dateMap[date] = (dateMap[date] || 0) + 1
          }
        })
        
        // 转换为数组格式
        this.taskDates = Object.entries(dateMap).map(([date, count]) => ({
          date,
          count
        }))
        
      } catch (error) {
        console.error('加载任务日历失败:', error)
        this.taskDates = []
      }
    },
    
    async loadDeviceStatus() {
      try {
        const alarms = await alarmApi.getAlarms({ limit: 10000 })
        const alarmList = alarms.results || alarms || []
        
        this.deviceStatus.pendingAlarms = alarmList.filter(a => a.status === 'PENDING').length
        this.deviceStatus.processingAlarms = alarmList.filter(a => a.status === 'PROCESSING').length
        this.deviceStatus.completedAlarms = alarmList.filter(a => a.status === 'COMPLETED').length
      } catch (error) {
        console.error('加载告警状态失败:', error)
        this.deviceStatus = {
          pendingAlarms: 0,
          processingAlarms: 0,
          completedAlarms: 0
        }
      }
    },
    
    async loadAlarmStats() {
      try {
        const alarms = await alarmApi.getAlarms({ limit: 10000 })
        const alarmList = alarms.results || alarms || []
        
        // 按告警类型分组统计
        const categoryMap = {}
        alarmList.forEach(alarm => {
          const categoryName = alarm.category_details?.name || '未分类'
          if (!categoryMap[categoryName]) {
            categoryMap[categoryName] = 0
          }
          categoryMap[categoryName]++
        })
        
        const total = alarmList.length || 1
        const colors = ['#ff4757', '#ffa502', '#1e90ff', '#2ed573', '#a29bfe', '#fd79a8']
        
        // 生成告警统计数组
        this.alarmStats = Object.entries(categoryMap)
          .map(([type, count], index) => ({
            type,
            count,
            percentage: Math.round((count / total) * 100),
            color: colors[index % colors.length]
          }))
          .sort((a, b) => b.count - a.count)
          .slice(0, 6) // 最多显示6种类型
        
        // 直接从 AlarmCategory 表获取检测类型（根节点）
        const categories = await alarmApi.getAlarmCategories()
        const categoryList = categories.results || categories || []
        console.log('所有分类数据:', categoryList)
        
        // 筛选出根节点（parent 为 null 或 undefined）
        const rootCategories = categoryList.filter(cat => !cat.parent)
        console.log('根节点分类:', rootCategories)
        
        // 统计每个检测类型的任务数
        const tasks = await inspectTaskApi.getInspectTasks({ limit: 10000 })
        const taskList = tasks.results || []
        console.log('任务列表:', taskList)
        
        const icons = ['⚙️', '🌡️', '🛡️', '✅', '🔍', '📊']
        const detectColors = ['#00d4ff', '#0099ff', '#00d4ff', '#0099ff', '#00d4ff', '#0099ff']
        
        this.detectionTypes = rootCategories.map((category, index) => {
          // 统计该类型的任务数
          const count = taskList.filter(task => 
            task.detect_category?.id === category.id || 
            task.detect_category?.name === category.name
          ).length
          
          return {
            type: category.name,
            count,
            icon: icons[index % icons.length],
            color: detectColors[index % detectColors.length],
            code: category.code
          }
        })
        .sort((a, b) => b.count - a.count)
        .slice(0, 4) // 显示前4种类型
        
      } catch (error) {
        console.error('加载告警统计失败:', error)
        this.alarmStats = []
        this.detectionTypes = []
      }
    },
    
    async loadRecentEvents() {
      try {
        const tasks = await inspectTaskApi.getInspectTasks({ limit: 10, ordering: '-created_at' })
        const taskList = tasks.results || []
        
        this.recentEvents = taskList.map((task) => ({
          id: task.id,
          time: task.created_at || new Date().toISOString(),
          title: task.external_task_id || `任务 ${task.id}`,
          description: `检测类型: ${task.detect_category?.name || task.detect_type || '未知'}`,
          status: task.detect_status === 'done' ? 'success' : 
                  task.detect_status === 'failed' ? 'error' : 
                  task.detect_status === 'processing' ? 'running' : 'pending'
        }))
      } catch (error) {
        console.error('加载最近事件失败:', error)
        this.recentEvents = []
      }
    },
    
    formatTime(timestamp) {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = Math.floor((now - date) / 1000)
      
      if (diff < 60) return '刚刚'
      if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
      if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
      
      return date.toLocaleString('zh-CN', { 
        month: '2-digit', 
        day: '2-digit', 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },
    
    getStatusText(status) {
      const statusMap = {
        success: '已完成',
        running: '进行中',
        error: '失败',
        pending: '待处理'
      }
      return statusMap[status] || '未知'
    },
    
    getBarHeight(count) {
      if (this.maxAlarmCount === 0) return 0
      return Math.max((count / this.maxAlarmCount) * 100, 5) // 最小5%高度
    },
    
    previousMonth() {
      if (this.currentMonth === 1) {
        this.currentMonth = 12
        this.currentYear--
      } else {
        this.currentMonth--
      }
    },
    
    nextMonth() {
      if (this.currentMonth === 12) {
        this.currentMonth = 1
        this.currentYear++
      } else {
        this.currentMonth++
      }
    }
  }
}
</script>

<style scoped>
.command-center {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #e2e8f0;
  padding: 20px;
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}

/* 顶部标题栏 */
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: none;
  border-radius: 12px;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.header-left, .header-right {
  width: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-left, .logo-right {
  max-width: 100%;
  max-height: 60px;
  object-fit: contain;
  filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.5));
}

.logo-placeholder {
  width: 140px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  color: #00d4ff;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(0, 153, 255, 0.15) 100%);
  border: 2px solid rgba(0, 212, 255, 0.4);
  border-radius: 8px;
  letter-spacing: 2px;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}

.header-center {
  text-align: center;
  flex: 1;
}

.main-title {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
  margin-bottom: 8px;
  letter-spacing: 2px;
}

.sub-title {
  font-size: 14px;
  color: #64b5f6;
  letter-spacing: 3px;
  text-transform: uppercase;
}

/* 主内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 320px 1fr 320px;
  gap: 20px;
  position: relative;
  z-index: 1;
  min-height: calc(100vh - 180px);
}

/* 左右面板 */
.left-panel, .right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 面板卡片 */
.panel-card {
  background: rgba(26, 31, 58, 0.3);
  border: 1px solid rgba(0, 212, 255, 0.15);
  border-radius: 12px;
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  transition: all 0.3s ease;
}

.panel-card:hover {
  border-color: rgba(0, 212, 255, 0.5);
  box-shadow: 0 8px 40px rgba(0, 212, 255, 0.2);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 0;
  padding-left: 30px;
  padding-top: 20px;
  padding-bottom: 8px;
  background: transparent;
  border: none;
  position: relative;
  margin-bottom: 20px;
}

/* 左侧小圆点 */
.card-header::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 5px;
  width: 8px;
  height: 8px;
  background: radial-gradient(circle, rgba(0, 212, 255, 1) 0%, rgba(0, 212, 255, 0.6) 100%);
  border-radius: 50%;
  border: 1px solid rgba(0, 212, 255, 0.8);
  box-shadow: 
    0 0 10px rgba(0, 212, 255, 0.8),
    inset 0 0 4px rgba(0, 212, 255, 0.5);
}

/* 从圆点出来的斜线 */
.card-header::after {
  content: '';
  position: absolute;
  left: 9px;
  top: 13px;
  width: 30px;
  height: 1px;
  background: linear-gradient(90deg, 
    rgba(0, 212, 255, 0.8) 0%, 
    rgba(0, 212, 255, 0.6) 100%);
  transform: rotate(45deg);
  transform-origin: left center;
  box-shadow: 0 0 5px rgba(0, 212, 255, 0.4);
}

/* 底部横线 */
.card-header {
  border-bottom: 1px solid transparent;
  background-image: linear-gradient(90deg, 
    rgba(0, 212, 255, 0.8) 0%, 
    rgba(0, 212, 255, 0.4) 50%, 
    rgba(0, 212, 255, 0.1) 80%,
    transparent 100%);
  background-repeat: no-repeat;
  background-position: 0 100%;
  background-size: calc(100% - 10px) 1px;
}

/* 右侧面板的标题样式 */
.right-panel .card-header {
  flex-direction: row-reverse;
  padding-left: 0;
  padding-right: 25px;
  background-image: linear-gradient(90deg, 
    transparent 0%,
    rgba(0, 212, 255, 0.1) 20%, 
    rgba(0, 212, 255, 0.4) 50%, 
    rgba(0, 212, 255, 0.8) 100%);
}

.right-panel .card-header::before {
  left: auto;
  right: 0;
}

.right-panel .card-header::after {
  left: auto;
  right: 4px;
}

.right-panel .header-icon {
  margin-right: 0;
  margin-left: 8px;
}

.header-icon {
  font-size: 18px;
  filter: drop-shadow(0 0 8px rgba(0, 212, 255, 0.8));
  margin-right: 8px;
  z-index: 1;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #00d4ff;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.6);
  z-index: 1;
}

.card-body {
  padding: 20px;
}

/* 任务统计 */

.tree-container {
  max-height: 280px;
  overflow-y: auto;
}
.tree-group {
  margin-bottom: 12px;
}
.tree-group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #e0f2fe;
  margin-bottom: 6px;
}
.group-count {
  color: #94a3b8;
  font-size: 12px;
}
.toggle-icon {
  margin-left: auto;
  color: #64b5f6;
  font-size: 12px;
}
.tree-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
}
.tree-item:last-child {
  border-bottom: none;
}
.item-name {
  color: #e2e8f0;
  font-size: 13px;
}
.item-meta {
  color: #94a3b8;
  font-size: 12px;
}
.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: rgba(0, 212, 255, 0.1);
  transform: scale(1.05);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #00d4ff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #94a3b8;
}

.text-success {
  color: #2ed573;
}

.text-warning {
  color: #ffa502;
}

.text-danger {
  color: #ff4757;
}

/* 进度环 */
.progress-ring {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto;
}

.ring-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: rgba(0, 212, 255, 0.1);
  stroke-width: 8;
}

.ring-progress {
  fill: none;
  stroke: url(#gradient);
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 314;
  transition: stroke-dashoffset 0.5s ease;
}

.ring-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.ring-value {
  font-size: 24px;
  font-weight: 700;
  color: #00d4ff;
}

.ring-label {
  font-size: 12px;
  color: #94a3b8;
}

/* 日历组件 */
.calendar {
  width: 100%;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  padding: 10px;
  background: rgba(0, 212, 255, 0.05);
  border-radius: 8px;
}

.calendar-title {
  font-size: 16px;
  font-weight: 700;
  color: #00d4ff;
}

.calendar-btn {
  width: 32px;
  height: 32px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 6px;
  background: rgba(0, 212, 255, 0.1);
  color: #00d4ff;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.calendar-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: rgba(0, 212, 255, 0.5);
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.weekday {
  text-align: center;
  font-size: 12px;
  color: #94a3b8;
  padding: 8px 4px;
  font-weight: 600;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.day-cell {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 6px;
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.day-cell:hover {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.3);
}

.day-cell.other-month {
  opacity: 0.3;
}

.day-cell.today {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

.day-cell.has-task {
  background: linear-gradient(135deg, rgba(255, 165, 2, 0.2) 0%, rgba(255, 71, 87, 0.2) 100%);
  border-color: #ffa502;
}

.day-number {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
}

.task-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 16px;
  height: 16px;
  background: #ff4757;
  border-radius: 50%;
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 8px rgba(255, 71, 87, 0.5);
}

/* 实时状态 */
.status-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: rgba(0, 212, 255, 0.05);
  border-radius: 6px;
  font-size: 14px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  box-shadow: 0 0 10px currentColor;
  animation: pulse 2s infinite;
}

.status-dot.online {
  background-color: #2ed573;
}

.status-dot.offline {
  background-color: #94a3b8;
}

.status-dot.warning {
  background-color: #ff4757;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 告警统计竖向条形图 */
.alarm-bar-chart {
  display: flex;
  gap: 15px;
  height: 220px;
  padding: 10px 0;
}

.chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 40px;
  padding-right: 10px;
  border-right: 1px solid rgba(0, 212, 255, 0.2);
}

.y-label {
  font-size: 11px;
  color: #94a3b8;
  text-align: right;
  line-height: 1;
}

.chart-bars {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  gap: 10px;
  border-bottom: 2px solid rgba(0, 212, 255, 0.3);
  padding: 0 10px;
}

.bar-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.bar-wrapper {
  width: 100%;
  height: 180px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.bar {
  width: 100%;
  max-width: 50px;
  min-height: 5%;
  border-radius: 6px 6px 0 0;
  position: relative;
  transition: all 0.5s ease;
  box-shadow: 0 0 15px currentColor;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 8px;
}

.bar:hover {
  opacity: 0.8;
  transform: scaleY(1.05);
}

.bar-count {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 0 8px rgba(0, 0, 0, 0.5);
}

.bar-label {
  font-size: 12px;
  color: #cbd5e1;
  text-align: center;
  word-break: keep-all;
  white-space: nowrap;
}

/* 检测类型网格 */
.detection-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.detection-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 15px;
  background: rgba(0, 212, 255, 0.05);
  border: 2px solid rgba(0, 212, 255, 0.2);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.detection-item:hover {
  background: rgba(0, 212, 255, 0.1);
  transform: scale(1.05);
  border-color: rgba(0, 212, 255, 0.4);
}

.detection-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  border: 2px solid;
  border-radius: 50%;
  background: rgba(0, 212, 255, 0.1);
}

.detection-name {
  font-size: 13px;
  color: #cbd5e1;
}

.detection-count {
  font-size: 20px;
  font-weight: 700;
  color: #00d4ff;
}

/* 空状态占位符 */
.empty-placeholder {
  padding: 40px 20px;
  text-align: center;
  color: #64748b;
  font-size: 14px;
}

/* 最近事件列表 */
.event-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.event-list::-webkit-scrollbar {
  width: 6px;
}

.event-list::-webkit-scrollbar-track {
  background: rgba(0, 212, 255, 0.05);
  border-radius: 3px;
}

.event-list::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.3);
  border-radius: 3px;
}

.event-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 212, 255, 0.05);
  border-left: 3px solid #00d4ff;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.event-item:hover {
  background: rgba(0, 212, 255, 0.1);
  transform: translateX(5px);
}

.event-time {
  font-size: 11px;
  color: #64b5f6;
  white-space: nowrap;
  min-width: 80px;
}

.event-content {
  flex: 1;
}

.event-title {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 4px;
}

.event-desc {
  font-size: 12px;
  color: #94a3b8;
}

.event-status {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
  align-self: center;
}

.event-status.success {
  background: rgba(46, 213, 115, 0.2);
  color: #2ed573;
  border: 1px solid #2ed573;
}

.event-status.running {
  background: rgba(255, 165, 2, 0.2);
  color: #ffa502;
  border: 1px solid #ffa502;
}

.event-status.error {
  background: rgba(255, 71, 87, 0.2);
  color: #ff4757;
  border: 1px solid #ff4757;
}

.event-status.pending {
  background: rgba(148, 163, 184, 0.2);
  color: #94a3b8;
  border: 1px solid #94a3b8;
}

/* 中间3D模型区 */
.center-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.model-display-area {
  flex: 1;
  min-height: 600px;
  position: relative;
  overflow: hidden;
  /* 弧形裁剪 */
  clip-path: ellipse(50% 50% at 50% 50%);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 弧形边界发光效果 */
.model-display-area::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: radial-gradient(ellipse at center, transparent 49%, rgba(0, 212, 255, 0.3) 49.5%, transparent 50%);
  pointer-events: none;
  animation: glow 3s ease-in-out infinite;
}

@keyframes glow {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

.placeholder-content {
  text-align: center;
  z-index: 1;
}

.placeholder-icon {
  font-size: 80px;
  margin-bottom: 20px;
  filter: drop-shadow(0 0 30px rgba(0, 212, 255, 0.8));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.placeholder-text {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 10px;
}

.placeholder-subtitle {
  font-size: 14px;
  color: #64b5f6;
  letter-spacing: 2px;
}

/* 底部装饰 */
.bottom-decoration {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    #00d4ff 50%, 
    transparent 100%
  );
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
  z-index: 1;
}

/* 响应式设计 */
@media (max-width: 1600px) {
  .main-content {
    grid-template-columns: 280px 1fr 280px;
  }
}

@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .left-panel, .right-panel {
    max-width: 100%;
  }
}
</style>
