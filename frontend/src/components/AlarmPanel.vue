<template>
  <div class="alarm-panel-premium">
    <!-- 面板头部 -->
    <div class="panel-header">
      <div class="header-left">
        <h3 class="panel-title">报警信息</h3>
        <span v-if="alarms.length > 0" class="alarm-count">{{ alarms.length }}</span>
      </div>
      <button @click="handleRefresh" class="refresh-btn">
        <span class="refresh-icon">⟳</span>
        刷新
      </button>
    </div>
    
    <!-- 告警列表 -->
    <div class="alarm-list-container">
      <div v-if="alarms.length === 0" class="empty-state">
        <div class="empty-icon">✓</div>
        <p>暂无报警信息</p>
      </div>
      
      <div v-else class="alarm-items">
        <div v-for="alarm in alarms" :key="alarm.id" class="alarm-item">
          <div class="alarm-item-header">
            <span class="status-indicator" :class="`status-${alarm.status.toLowerCase()}`"></span>
            <span class="alarm-title">{{ getAlarmTitle(alarm) }}</span>
            <span class="alarm-time">{{ formatTime(alarm.created_at) }}</span>
          </div>
          
          <div class="alarm-item-body">
            <p class="alarm-description">{{ alarm.content }}</p>
            <div class="alarm-location">
              <span class="location-icon">📍</span>
              <span>{{ alarm.latitude }}, {{ alarm.longitude }}</span>
            </div>
            
            <div v-if="alarm.image_url" class="alarm-image">
              <img :src="alarm.image_url" :alt="alarm.content" />
            </div>
            
            <div class="alarm-actions">
              <button @click="viewAlarmDetail(alarm)" class="action-btn view-btn">
                查看详情
              </button>
              <button @click="processAlarm(alarm.id)" class="action-btn process-btn">
                标记处理
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AlarmPanel',
  props: {
    alarms: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    formatTime(timestamp) {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    getAlarmTitle(alarm) {
      if (alarm.category_details && alarm.category_details.name) {
        return alarm.category_details.name
      }
      return alarm.content ? alarm.content.substring(0, 30) + (alarm.content.length > 30 ? '...' : '') : '未知告警'
    },
    
    handleRefresh() {
      this.$emit('refresh')
    },
    
    viewAlarmDetail(alarm) {
      this.$emit('view-detail', alarm)
    },
    
    processAlarm(alarmId) {
      this.$emit('process-alarm', alarmId)
    }
  }
}
</script>

<style scoped>
.alarm-panel-premium {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(26, 31, 58, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(239, 68, 68, 0.2);
  overflow: hidden;
}

/* 面板头部 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%);
  border-bottom: 1px solid rgba(239, 68, 68, 0.2);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.panel-title {
  font-size: 16px;
  font-weight: 700;
  color: #ef4444;
  margin: 0;
}

.alarm-count {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 8px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border-radius: 12px;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 4px 16px rgba(239, 68, 68, 0.6);
  }
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  color: #ef4444;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: #ef4444;
  transform: translateY(-1px);
}

.refresh-icon {
  font-size: 16px;
  transition: transform 0.3s ease;
}

.refresh-btn:hover .refresh-icon {
  transform: rotate(180deg);
}

/* 告警列表容器 */
.alarm-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

/* 自定义滚动条 */
.alarm-list-container::-webkit-scrollbar {
  width: 6px;
}

.alarm-list-container::-webkit-scrollbar-track {
  background: rgba(10, 14, 39, 0.4);
  border-radius: 3px;
}

.alarm-list-container::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border-radius: 3px;
}

.alarm-list-container::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #64748b;
}

.empty-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(16, 185, 129, 0.1);
  border: 2px solid rgba(16, 185, 129, 0.3);
  border-radius: 50%;
  font-size: 32px;
  color: #10b981;
  margin-bottom: 16px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* 告警项 */
.alarm-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alarm-item {
  background: rgba(10, 14, 39, 0.6);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.alarm-item:hover {
  border-color: rgba(239, 68, 68, 0.4);
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.2);
  transform: translateY(-2px);
}

.alarm-item-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.05);
  border-bottom: 1px solid rgba(239, 68, 68, 0.1);
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-indicator.status-pending {
  background: #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.6);
  animation: blink 1.5s ease-in-out infinite;
}

.status-indicator.status-processing {
  background: #f59e0b;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.6);
}

.status-indicator.status-completed {
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
}

.status-indicator.status-ignored {
  background: #3b82f6;
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.6);
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

.alarm-title {
  flex: 1;
  color: #e2e8f0;
  font-size: 14px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.alarm-time {
  color: #94a3b8;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  flex-shrink: 0;
}

.alarm-item-body {
  padding: 16px;
}

.alarm-description {
  color: #cbd5e1;
  font-size: 13px;
  line-height: 1.6;
  margin: 0 0 12px 0;
}

.alarm-location {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #94a3b8;
  font-size: 12px;
  margin-bottom: 12px;
}

.location-icon {
  font-size: 14px;
}

.alarm-image {
  margin: 12px 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.alarm-image img {
  width: 100%;
  height: auto;
  display: block;
}

.alarm-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(239, 68, 68, 0.1);
}

.action-btn {
  flex: 1;
  padding: 8px 14px;
  border-radius: 6px;
  border: none;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.view-btn:hover {
  background: rgba(59, 130, 246, 0.25);
  transform: translateY(-1px);
}

.process-btn {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.process-btn:hover {
  background: rgba(239, 68, 68, 0.25);
  transform: translateY(-1px);
}
</style>