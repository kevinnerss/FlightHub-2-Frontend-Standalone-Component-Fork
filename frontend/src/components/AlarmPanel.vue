<template>
  <div class="alarm-panel tech-border-glow">
    <div class="panel-header tech-border">
      <h3 class="panel-title text-blue-400">报警信息</h3>
      <div class="header-actions">
        <el-badge 
          v-if="alarms.length > 0" 
          :value="alarms.length" 
          type="danger" 
          size="small"
          class="tech-badge-glow"
        />
        <el-button 
          size="small" 
          icon="Refresh" 
          @click="handleRefresh" 
          plain
          class="tech-button-text"
        >
          刷新
        </el-button>
      </div>
    </div>
    
    <div class="alarm-list tech-scrollbar">
      <div v-if="alarms.length === 0" class="empty-alarms tech-border">
        <p class="text-gray-400">暂无报警信息</p>
      </div>
      
      <el-collapse v-else v-model="activeAlarms" accordion class="tech-collapse">
        <el-collapse-item 
          v-for="alarm in alarms" 
          :key="alarm.id"
          :name="alarm.id"
          class="tech-collapse-item"
        >
          <template #title>
            <div class="alarm-summary">
              <el-tag 
                size="small" 
                :type="getAlarmStatusType(alarm.status)"
                :class="['tech-label-glow', `alarm-status-${alarm.status.toLowerCase()}`]"
              >
                {{ getStatusText(alarm.status) }}
              </el-tag>
              <span class="alarm-title">{{ getAlarmTitle(alarm) }}</span>
              <span class="alarm-time text-gray-400">{{ formatTime(alarm.created_at) }}</span>
            </div>
          </template>
          <div class="alarm-details tech-border-light">
            <p class="alarm-description">{{ alarm.content }}</p>
            <p class="alarm-location text-gray-300">
              <i class="el-icon-location-information"></i>
              位置: {{ alarm.latitude }}, {{ alarm.longitude }}
            </p>
            <div v-if="alarm.image_url" class="alarm-image tech-border-light">
              <el-image
                :src="alarm.image_url"
                :preview-src-list="[alarm.image_url]"
                fit="cover"
                style="width: 100%; height: 200px"
                class="tech-image-glow"
              />
            </div>
            <div class="alarm-actions">
              <el-button 
                size="small" 
                type="primary" 
                @click="viewAlarmDetail(alarm)"
                class="tech-button-primary-glow"
              >
                查看详情
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="processAlarm(alarm.id)"
                class="tech-button-danger-glow"
              >
                标记已处理
              </el-button>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
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
  data() {
    return {
      activeAlarms: []
    }
  },
  methods: {
    // 格式化时间
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
    
    // 获取告警标题
    getAlarmTitle(alarm) {
      // 优先使用告警类型名称作为标题
      if (alarm.category_details && alarm.category_details.name) {
        return alarm.category_details.name
      }
      // 如果没有类型信息，使用content的前30个字符
      return alarm.content ? alarm.content.substring(0, 30) + (alarm.content.length > 30 ? '...' : '') : '未知告警'
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
    
    // 获取状态样式类型
    getAlarmStatusType(status) {
      const typeMap = {
        'PENDING': 'danger',    // 待处理 - 红色
        'PROCESSING': 'warning', // 处理中 - 橙色
        'COMPLETED': 'success',  // 已完成 - 绿色
        'IGNORED': 'info'        // 已忽略 - 蓝色
      }
      return typeMap[status] || 'default'
    },
    
    // 处理刷新
    handleRefresh() {
      this.$emit('refresh')
    },
    
    // 查看报警详情
    viewAlarmDetail(alarm) {
      this.$emit('view-detail', alarm)
    },
    
    // 处理报警
    processAlarm(alarmId) {
      this.$emit('process-alarm', alarmId)
    }
  }
}
</script>

<style scoped>
.alarm-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #1f2937;
  border-radius: 6px;
  padding: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

/* 告警状态标签样式 */
.tech-label-glow {
  position: relative;
  overflow: hidden;
}

.tech-label-glow::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255,255,255,0.3), transparent);
  transform: rotate(45deg);
  animation: badgeGlow 2s infinite;
}

@keyframes badgeGlow {
  0% { transform: translateX(-100%) rotate(45deg); }
  100% { transform: translateX(100%) rotate(45deg); }
}

/* 待处理状态样式 - 红色 */
.alarm-status-pending {
  background: linear-gradient(135deg, #ef4444, #b91c1c) !important;
  border-color: #ef4444 !important;
  color: white !important;
  font-weight: 500;
}

/* 处理中状态样式 - 橙色 */
.alarm-status-processing {
  background: linear-gradient(135deg, #f59e0b, #d97706) !important;
  border-color: #f59e0b !important;
  color: white !important;
  font-weight: 500;
}

/* 已完成状态样式 - 绿色 */
.alarm-status-completed {
  background: linear-gradient(135deg, #10b981, #059669) !important;
  border-color: #10b981 !important;
  color: white !important;
  font-weight: 500;
}

/* 已忽略状态样式 - 蓝色 */
.alarm-status-ignored {
  background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
  border-color: #3b82f6 !important;
  color: white !important;
  font-weight: 500;
}

/* 全局覆盖折叠面板的所有可能白边 */
:deep(.el-collapse) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

:deep(.el-collapse-item) {
  background: #111827 !important;
  border: 1px solid #374151 !important;
  margin-bottom: 12px !important;
  border-radius: 4px !important;
  overflow: hidden !important;
}

:deep(.el-collapse-item__wrap) {
  background: #111827 !important;
  border: none !important;
  box-shadow: none !important;
  margin: 0 !important;
  overflow: hidden !important;
}

:deep(.el-collapse-item__content) {
  background: #111827 !important;
  padding: 0 !important;
  margin: 0 !important;
  border: none !important;
  overflow: hidden !important;
}

:deep(.el-collapse-item__header) {
  background: #1f2937 !important;
  color: #d1d5db !important;
  border-bottom: 1px solid #374151 !important;
  margin: 0 !important;
  padding-left: 12px !important;
}

:deep(.el-collapse-item__arrow) {
  background: transparent !important;
  color: #6b7280 !important;
}

:deep(.el-collapse-transition) {
  background: transparent !important;
  overflow: hidden !important;
}

/* 科技感背景纹理 */
.alarm-panel::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  z-index: 0;
  pointer-events: none;
}

.alarm-panel > * {
  position: relative;
  z-index: 1;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid rgba(75, 85, 99, 0.3);
  background-color: #111827;
  margin-bottom: 15px;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.panel-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
  animation: panelShimmer 3s infinite;
  pointer-events: none;
}

.panel-title {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
  color: #3b82f6;
  text-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
  position: relative;
}

.panel-title::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, #3b82f6, transparent);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.alarm-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  position: relative;
}

.alarm-summary {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 10px;
  padding: 8px 0;
  transition: all 0.3s ease;
}

.alarm-title {
  flex: 1;
  font-weight: 500;
  color: #d1d5db;
  text-shadow: 0 0 2px rgba(59, 130, 246, 0.3);
  transition: color 0.3s ease;
}

.alarm-title:hover {
  color: #93c5fd;
}

.alarm-time {
  font-size: 12px;
  color: #9ca3af;
  font-family: 'JetBrains Mono', monospace;
}

.alarm-details {
  padding: 15px;
  background: #111827;
  border-radius: 4px;
  margin-top: 10px;
  position: relative;
  overflow: hidden;
}

.alarm-details::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, #3b82f6, transparent);
}

.alarm-description {
  margin: 0 0 10px 0;
  color: #d1d5db;
  line-height: 1.5;
  padding-left: 10px;
  border-left: 2px solid #374151;
}

.alarm-location {
  margin: 10px 0;
  color: #9ca3af;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 10px;
}

.alarm-location i {
  color: #3b82f6;
  text-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
}

.alarm-image {
  margin: 15px 0;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  transition: all 0.3s ease;
}

.alarm-image:hover {
  transform: scale(1.02);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
}

.alarm-image img {
  border-radius: 4px;
  transition: all 0.3s ease;
}

.alarm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #374151;
}

/* 高级科技感边框样式 */
.tech-border-glow {
  border: 1px solid #374151;
  position: relative;
  overflow: hidden;
  box-shadow: 
    0 0 15px rgba(59, 130, 246, 0.2),
    inset 0 0 15px rgba(59, 130, 246, 0.05);
}

.tech-border-glow::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 1px solid transparent;
  border-radius: 6px;
  background: linear-gradient(90deg, #3b82f6, transparent, #3b82f6) border-box;
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  animation: borderRotate 6s linear infinite;
}

.tech-border {
  border: 1px solid #374151;
  position: relative;
  overflow: hidden;
}

.tech-border::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, #3b82f6, transparent);
  animation: techGlow 3s infinite;
}

.tech-border-light {
  border: 1px solid #4b5563;
  position: relative;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.1);
  transition: all 0.3s ease;
}

.tech-border-light:hover {
  border-color: #6b7280;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
}

/* 科技感按钮样式 */
.tech-button-text {
  color: #93c5fd;
  background: transparent;
  border: 1px solid #374151;
  transition: all 0.3s ease;
}

.tech-button-text:hover {
  color: #60a5fa;
  background: rgba(59, 130, 246, 0.1);
  border-color: #4b5563;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}

.tech-button-primary-glow {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border: 1px solid #60a5fa;
  color: white;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.tech-button-primary-glow::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transform: rotate(45deg);
  animation: buttonGlow 3s infinite;
}

.tech-button-primary-glow:hover {
  background: linear-gradient(135deg, #1d4ed8, #2563eb);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.6);
  border-color: #93c5fd;
}

.tech-button-danger-glow {
  background: linear-gradient(135deg, #dc2626, #ef4444);
  border: 1px solid #fca5a5;
  color: white;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.tech-button-danger-glow::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transform: rotate(45deg);
  animation: buttonGlow 3s infinite;
}

.tech-button-danger-glow:hover {
  background: linear-gradient(135deg, #b91c1c, #dc2626);
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.6);
  border-color: #fecaca;
}

/* 标签样式 */
.tech-label-glow {
  text-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
  border: 1px solid rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
  background: rgba(59, 130, 246, 0.05);
}

.tech-label-glow:hover {
  border-color: #3b82f6;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}

/* 徽章样式 */
.tech-badge-glow {
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.6);
  animation: badgePulse 2s infinite;
}

/* 图片样式 */
.tech-image-glow {
  border: 1px solid #374151;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.tech-image-glow::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent, rgba(59, 130, 246, 0.1), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.tech-image-glow:hover {
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
  border-color: #4b5563;
}

.tech-image-glow:hover::after {
  opacity: 1;
}

/* 折叠面板样式 */
.tech-collapse {
  width: 100%;
  background: transparent;
  border: none;
}

/* 确保整个折叠面板组没有边框和背景 */
.el-collapse {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.tech-collapse-item {
  background: #111827;
  border: 1px solid #374151;
  margin-bottom: 12px;
  border-radius: 4px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.tech-collapse-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, #3b82f6, transparent);
}

.tech-collapse-item:hover {
  border-color: #4b5563;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
}

.tech-collapse-item .el-collapse-item__header {
  color: #d1d5db;
  background: #1f2937;
  border-bottom: 1px solid #374151;
  transition: all 0.3s ease;
  padding-left: 12px;
  margin: 0;
}

/* 修复折叠面板内容区域的白边问题 */
.tech-collapse-item .el-collapse-item__wrap {
  background: #111827 !important;
  border: none !important;
  box-shadow: none !important;
  margin: 0 !important;
}

.tech-collapse-item .el-collapse-item__content {
  background: #111827 !important;
  padding: 0 !important;
  margin: 0 !important;
  border: none !important;
  overflow: hidden !important;
}

/* 确保折叠面板的所有子元素都使用深色背景 */
.tech-collapse-item > * {
  background: #111827 !important;
}

/* 修复可能的白色过渡或动画背景 */
.el-collapse-transition {
  background: transparent !important;
}

/* 修复折叠图标区域的背景 */
.tech-collapse-item .el-collapse-item__arrow {
  background: transparent !important;
  color: #6b7280 !important;
}

.tech-collapse-item .el-collapse-item__header:hover {
  background: #1e3a8a;
  color: #93c5fd;
}

.tech-collapse-item .el-collapse-item__arrow {
  color: #6b7280;
  transition: all 0.3s ease;
}

.tech-collapse-item .el-collapse-item__header:hover .el-collapse-item__arrow {
  color: #3b82f6;
}

/* 空状态样式 */
.empty-alarms {
  text-align: center;
  padding: 40px 20px;
  background: #111827;
  border-radius: 4px;
  border: 1px dashed #374151;
  margin: 20px 0;
  position: relative;
  overflow: hidden;
}

.empty-alarms::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 25%, transparent 25%, transparent 50%, rgba(59, 130, 246, 0.05) 50%, rgba(59, 130, 246, 0.05) 75%, transparent 75%, transparent);
  background-size: 20px 20px;
  animation: emptyGridMove 10s linear infinite;
  pointer-events: none;
}

/* 科技感滚动条 */
.tech-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.tech-scrollbar::-webkit-scrollbar-track {
  background: #1f2937;
  border-radius: 4px;
  border: 1px solid #374151;
}

.tech-scrollbar::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #3b82f6, #1d4ed8);
  border-radius: 4px;
  border: 1px solid #4b5563;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
}

.tech-scrollbar::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #2563eb, #1e40af);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
  transform: scaleX(1.2);
}

.tech-scrollbar::-webkit-scrollbar-corner {
  background: #1f2937;
  border: 1px solid #374151;
}

/* 动画效果 */
@keyframes techGlow {
  0% {
    opacity: 0.5;
    background-position: -100% 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.5;
    background-position: 100% 0;
  }
}

@keyframes borderRotate {
  0% {
    background-position: 0% 0%;
  }
  100% {
    background-position: 300% 0%;
  }
}

@keyframes buttonGlow {
  0% {
    left: -100%;
    opacity: 0;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    left: 100%;
    opacity: 0;
  }
}

@keyframes badgePulse {
  0% {
    box-shadow: 0 0 15px rgba(239, 68, 68, 0.6);
  }
  50% {
    box-shadow: 0 0 25px rgba(239, 68, 68, 0.8);
  }
  100% {
    box-shadow: 0 0 15px rgba(239, 68, 68, 0.6);
  }
}

@keyframes panelShimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes emptyGridMove {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 40px 40px;
  }
}
</style>