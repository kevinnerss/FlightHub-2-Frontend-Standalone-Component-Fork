<template>
  <div class="dock-status-panel">
    <!-- 头部标题栏 -->
    <div class="panel-header">
      <h3 class="panel-title">
        <span class="icon">🏭</span>
        机场状态监控
      </h3>
      <div class="header-actions">
        <button @click="refreshData" class="btn-refresh" :disabled="loading">
          <span v-if="!loading">🔄</span>
          <span v-else class="spinner">⏳</span>
          刷新
        </button>
        <span class="update-time">更新: {{ lastUpdateTime }}</span>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="statistics-cards">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.total_docks }}</div>
          <div class="stat-label">机场总数</div>
        </div>
      </div>
      <div class="stat-card online">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.online_docks }}</div>
          <div class="stat-label">在线机场</div>
        </div>
      </div>
      <div class="stat-card offline">
        <div class="stat-icon">❌</div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.offline_docks }}</div>
          <div class="stat-label">离线机场</div>
        </div>
      </div>
      <div class="stat-card alarm">
        <div class="stat-icon">⚠️</div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.alarm_docks }}</div>
          <div class="stat-label">告警机场</div>
        </div>
      </div>
    </div>

    <!-- 机场列表 -->
    <div class="docks-list">
      <div v-if="loading && docks.length === 0" class="loading-state">
        <div class="spinner-large">⏳</div>
        <p>加载中...</p>
      </div>

      <div v-else-if="docks.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <p>暂无机场数据</p>
      </div>

      <div v-else class="dock-cards">
        <div
          v-for="dock in docks"
          :key="dock.id"
          class="dock-card"
          :class="{
            'online': dock.is_online,
            'offline': !dock.is_online,
            'has-alarm': dock.alarm_state > 0
          }"
          @click="selectDock(dock)"
        >
          <!-- 卡片头部 -->
          <div class="dock-card-header">
            <div class="dock-name">
              <span class="status-indicator" :class="{ 'online': dock.is_online }"></span>
              <h4>{{ dock.display_name || dock.dock_name || dock.dock_sn }}</h4>
            </div>
            <span class="dock-sn">{{ dock.dock_sn }}</span>
          </div>

          <!-- 核心状态信息 -->
          <div class="dock-info-grid">
            <!-- 环境信息 -->
            <div class="info-item">
              <span class="info-icon">🌡️</span>
              <div class="info-content">
                <span class="info-label">环境温度</span>
                <span class="info-value">{{ formatTemperature(dock.environment_temperature) }}</span>
              </div>
            </div>

            <div class="info-item">
              <span class="info-icon">💨</span>
              <div class="info-content">
                <span class="info-label">风速</span>
                <span class="info-value">{{ formatWindSpeed(dock.wind_speed) }}</span>
              </div>
            </div>

            <div class="info-item">
              <span class="info-icon">💧</span>
              <div class="info-content">
                <span class="info-label">湿度</span>
                <span class="info-value">{{ formatHumidity(dock.humidity) }}</span>
              </div>
            </div>

            <!-- 硬件状态 -->
            <div class="info-item">
              <span class="info-icon">🚪</span>
              <div class="info-content">
                <span class="info-label">舱盖</span>
                <span class="info-value">{{ getCoverStateText(dock.cover_state) }}</span>
              </div>
            </div>

            <!-- 无人机状态 -->
            <div class="info-item">
              <span class="info-icon">🚁</span>
              <div class="info-content">
                <span class="info-label">无人机</span>
                <span class="info-value">{{ getDroneInDockText(dock.drone_in_dock) }}</span>
              </div>
            </div>

            <div class="info-item" v-if="dock.drone_battery_percent">
              <span class="info-icon">🔋</span>
              <div class="info-content">
                <span class="info-label">无人机电量</span>
                <span class="info-value">{{ dock.drone_battery_percent }}%</span>
              </div>
            </div>

            <!-- 存储信息 -->
            <div class="info-item">
              <span class="info-icon">💾</span>
              <div class="info-content">
                <span class="info-label">存储</span>
                <span class="info-value">{{ formatStorage(dock) }}</span>
              </div>
            </div>

            <!-- 任务统计 -->
            <div class="info-item">
              <span class="info-icon">📋</span>
              <div class="info-content">
                <span class="info-label">任务次数</span>
                <span class="info-value">{{ dock.job_number || 0 }}</span>
              </div>
            </div>
          </div>

          <!-- 告警标识 -->
          <div v-if="dock.alarm_state > 0" class="alarm-badge">
            ⚠️ 有告警
          </div>

          <!-- 更新时间 -->
          <div class="dock-card-footer">
            <span class="last-update">
              最后更新: {{ formatTime(dock.last_update_time) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="selectedDock" class="dock-detail-modal" @click="closeDockDetail">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedDock.display_name || selectedDock.dock_name || selectedDock.dock_sn }}</h3>
          <button class="btn-close" @click="closeDockDetail">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-section">
            <h4>基本信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">机场SN:</span>
                <span class="detail-value">{{ selectedDock.dock_sn }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">在线状态:</span>
                <span class="detail-value" :class="{ 'text-success': selectedDock.is_online, 'text-danger': !selectedDock.is_online }">
                  {{ selectedDock.online_status }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">模式代码:</span>
                <span class="detail-value">{{ selectedDock.mode_code }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">激活时间:</span>
                <span class="detail-value">{{ formatTimestamp(selectedDock.activation_time) }}</span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4>环境参数</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">环境温度:</span>
                <span class="detail-value">{{ selectedDock.environment_temperature }}℃</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">机场温度:</span>
                <span class="detail-value">{{ selectedDock.temperature }}℃</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">湿度:</span>
                <span class="detail-value">{{ selectedDock.humidity }}%</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">风速:</span>
                <span class="detail-value">{{ selectedDock.wind_speed }} m/s</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">降雨量:</span>
                <span class="detail-value">{{ selectedDock.rainfall }}</span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4>电源状态</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">供电电压:</span>
                <span class="detail-value">{{ selectedDock.electric_supply_voltage }} V</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">工作电压:</span>
                <span class="detail-value">{{ selectedDock.working_voltage }} mV</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">工作电流:</span>
                <span class="detail-value">{{ selectedDock.working_current }} mA</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">功率:</span>
                <span class="detail-value">{{ selectedDock.power_status }} W</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">备用电池电压:</span>
                <span class="detail-value">{{ selectedDock.backup_battery_voltage }} mV</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">备用电池温度:</span>
                <span class="detail-value">{{ selectedDock.backup_battery_temperature }}℃</span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4>硬件状态</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">舱盖状态:</span>
                <span class="detail-value">{{ getCoverStateText(selectedDock.cover_state) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">推杆状态:</span>
                <span class="detail-value">{{ selectedDock.putter_state }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">补光灯:</span>
                <span class="detail-value">{{ selectedDock.supplement_light_state === 1 ? '开启' : '关闭' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">急停状态:</span>
                <span class="detail-value" :class="{ 'text-danger': selectedDock.emergency_stop_state === 1 }">
                  {{ selectedDock.emergency_stop_state === 1 ? '已触发' : '正常' }}
                </span>
              </div>
            </div>
          </div>

          <div class="detail-section" v-if="selectedDock.drone_sn">
            <h4>无人机信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">无人机SN:</span>
                <span class="detail-value">{{ selectedDock.drone_sn }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">在舱状态:</span>
                <span class="detail-value">{{ getDroneInDockText(selectedDock.drone_in_dock) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">充电状态:</span>
                <span class="detail-value">{{ selectedDock.drone_charge_state }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">电池电量:</span>
                <span class="detail-value">{{ selectedDock.drone_battery_percent }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import dockStatusApi from '@/api/dockStatusApi'

export default {
  name: 'DockStatusPanel',
  data() {
    return {
      docks: [],
      statistics: {
        total_docks: 0,
        online_docks: 0,
        offline_docks: 0,
        alarm_docks: 0
      },
      selectedDock: null,
      loading: false,
      lastUpdateTime: '--:--:--',
      refreshInterval: null
    }
  },
  mounted() {
    this.loadData()
    // 每30秒自动刷新
    this.refreshInterval = setInterval(() => {
      this.loadData(true)
    }, 30000)
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  },
  methods: {
    async loadData(silent = false) {
      if (!silent) {
        this.loading = true
      }
      try {
        // 并行获取机场列表和统计信息
        const [docksData, statsData] = await Promise.all([
          dockStatusApi.getAllDocks(),
          dockStatusApi.getDockStatistics()
        ])

        this.docks = docksData || []
        this.statistics = statsData || this.statistics
        this.updateTime()
      } catch (error) {
        console.error('加载机场数据失败:', error)
      } finally {
        this.loading = false
      }
    },

    async refreshData() {
      await this.loadData()
    },

    selectDock(dock) {
      this.selectedDock = dock
    },

    closeDockDetail() {
      this.selectedDock = null
    },

    updateTime() {
      const now = new Date()
      this.lastUpdateTime = now.toLocaleTimeString('zh-CN', { hour12: false })
    },

    formatTemperature(temp) {
      return temp !== null && temp !== undefined ? `${temp}℃` : '--'
    },

    formatWindSpeed(speed) {
      return speed !== null && speed !== undefined ? `${speed} m/s` : '--'
    },

    formatHumidity(humidity) {
      return humidity !== null && humidity !== undefined ? `${humidity}%` : '--'
    },

    getCoverStateText(state) {
      const stateMap = {
        0: '关闭',
        1: '打开',
        2: '半开',
        null: '--'
      }
      return stateMap[state] || '未知'
    },

    getDroneInDockText(state) {
      const stateMap = {
        0: '不在舱内',
        1: '在舱内',
        null: '--'
      }
      return stateMap[state] || '未知'
    },

    formatTime(timeStr) {
      if (!timeStr) return '--'
      try {
        const date = new Date(timeStr)
        return date.toLocaleString('zh-CN', { hour12: false })
      } catch {
        return timeStr
      }
    },

    formatTimestamp(timestamp) {
      if (!timestamp) return '--'
      try {
        const date = new Date(timestamp * 1000)
        return date.toLocaleString('zh-CN', { hour12: false })
      } catch {
        return '--'
      }
    },

    formatStorage(dock) {
      if (dock.storage_total && dock.storage_used) {
        const usedPercent = Math.round((dock.storage_used / dock.storage_total) * 100)
        return `${usedPercent}%`
      }
      return '--'
    }
  }
}
</script>

<style scoped>
.dock-status-panel {
  background: transparent;
  border-radius: 12px;
  padding: 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #f1f5f9;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-title .icon {
  font-size: 24px;
  filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.4));
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-refresh {
  padding: 8px 16px;
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s;
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(56, 189, 248, 0.25);
  border-color: #38bdf8;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
  transform: translateY(-1px);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.update-time {
  font-size: 13px;
  color: #94a3b8;
}

/* 统计卡片 */
.statistics-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.3);
  color: #f1f5f9;
  padding: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(56, 189, 248, 0.2);
}

.stat-card.online {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
}

.stat-card.online:hover {
  box-shadow: 0 6px 12px rgba(34, 197, 94, 0.2);
}

.stat-card.offline {
  background: rgba(249, 115, 22, 0.1);
  border-color: rgba(249, 115, 22, 0.3);
}

.stat-card.offline:hover {
  box-shadow: 0 6px 12px rgba(249, 115, 22, 0.2);
}

.stat-card.alarm {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
}

.stat-card.alarm:hover {
  box-shadow: 0 6px 12px rgba(239, 68, 68, 0.2);
}

.stat-icon {
  font-size: 32px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
  color: #f1f5f9;
}

.stat-label {
  font-size: 13px;
  color: #cbd5e1;
}

/* 机场卡片列表 */
.docks-list {
  min-height: 300px;
}

.dock-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.dock-card {
  background: rgba(30, 41, 59, 0.45);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.dock-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
  border-color: rgba(56, 189, 248, 0.3);
}

.dock-card.online {
  border-color: rgba(34, 197, 94, 0.3);
}

.dock-card.online:hover {
  box-shadow: 0 8px 16px rgba(34, 197, 94, 0.2);
}

.dock-card.offline {
  border-color: rgba(249, 115, 22, 0.3);
  opacity: 0.7;
}

.dock-card.offline:hover {
  box-shadow: 0 8px 16px rgba(249, 115, 22, 0.2);
}

.dock-card.has-alarm {
  border-color: rgba(239, 68, 68, 0.5);
  background: rgba(239, 68, 68, 0.05);
}

.dock-card.has-alarm:hover {
  box-shadow: 0 8px 16px rgba(239, 68, 68, 0.3);
}

.dock-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.dock-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dock-name h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #f1f5f9;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #64748b;
}

.status-indicator.online {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.dock-sn {
  font-size: 12px;
  color: #94a3b8;
  font-family: monospace;
}

/* 信息网格 */
.dock-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-icon {
  font-size: 18px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
}

.info-content {
  flex: 1;
  min-width: 0;
}

.info-label {
  display: block;
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 2px;
}

.info-value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.alarm-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
  animation: alarmPulse 2s infinite;
}

@keyframes alarmPulse {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 2px 12px rgba(239, 68, 68, 0.7);
  }
}

.dock-card-footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.last-update {
  font-size: 12px;
  color: #64748b;
}

/* 加载和空状态 */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.spinner-large {
  font-size: 48px;
  animation: spin 1.5s linear infinite;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.empty-state p,
.loading-state p {
  color: #cbd5e1;
  font-size: 16px;
}

/* 详情弹窗 */
.dock-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 16px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(56, 189, 248, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: #f1f5f9;
  font-weight: 600;
}

.btn-close {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 20px;
  cursor: pointer;
  color: #cbd5e1;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-close:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}

.modal-body {
  padding: 24px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #f1f5f9;
  padding-bottom: 8px;
  border-bottom: 2px solid rgba(56, 189, 248, 0.5);
  font-weight: 600;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.detail-label {
  font-size: 14px;
  color: #94a3b8;
  font-weight: 500;
}

.detail-value {
  font-size: 14px;
  color: #e2e8f0;
  font-weight: 600;
}

.text-success {
  color: #22c55e;
}

.text-danger {
  color: #ef4444;
}

/* 响应式 */
@media (max-width: 768px) {
  .statistics-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .dock-cards {
    grid-template-columns: 1fr;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .dock-info-grid {
    grid-template-columns: 1fr;
  }
}

/* 滚动条样式 */
.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: rgba(56, 189, 248, 0.3);
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: rgba(56, 189, 248, 0.5);
}
</style>
