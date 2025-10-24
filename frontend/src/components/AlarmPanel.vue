<template>
  <div class="alarm-panel">
    <div class="panel-header">
      <h3 class="panel-title">报警信息</h3>
      <div class="header-actions">
        <el-badge 
          v-if="alarms.length > 0" 
          :value="alarms.length" 
          type="danger" 
          size="small"
        />
        <el-button 
          size="small" 
          icon="Refresh" 
          @click="handleRefresh" 
          plain
        >
          刷新
        </el-button>
      </div>
    </div>
    
    <div class="alarm-list">
      <el-empty v-if="alarms.length === 0" description="暂无报警信息" />
      
      <el-collapse v-else v-model="activeAlarms" accordion>
        <el-collapse-item 
          v-for="alarm in alarms" 
          :key="alarm.id"
          :name="alarm.id"
        >
          <template #title>
            <div class="alarm-summary">
              <el-tag 
                size="small" 
                :type="getAlarmType(alarm.severity)"
              >
                {{ alarm.severity }}级
              </el-tag>
              <span class="alarm-title">{{ alarm.title }}</span>
              <span class="alarm-time">{{ formatTime(alarm.timestamp) }}</span>
            </div>
          </template>
          <div class="alarm-details">
            <p class="alarm-description">{{ alarm.description }}</p>
            <p class="alarm-location">
              <i class="el-icon-location-information"></i>
              {{ alarm.location }}
            </p>
            <div v-if="alarm.imageUrl" class="alarm-image">
              <el-image
                :src="alarm.imageUrl"
                :preview-src-list="[alarm.imageUrl]"
                fit="cover"
                style="width: 100%; height: 200px"
              />
            </div>
            <div class="alarm-actions">
              <el-button 
                size="small" 
                type="primary" 
                @click="viewAlarmDetail(alarm)"
              >
                查看详情
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="processAlarm(alarm.id)"
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
    
    // 获取报警类型样式
    getAlarmType(severity) {
      switch(severity) {
        case '高':
          return 'danger'
        case '中':
          return 'warning'
        case '低':
          return 'info'
        default:
          return 'info'
      }
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
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #ebeef5;
  background-color: #f5f7fa;
}

.panel-title {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
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
}

.alarm-summary {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 10px;
}

.alarm-title {
  flex: 1;
  font-weight: 500;
  color: #606266;
}

.alarm-time {
  font-size: 12px;
  color: #909399;
}

.alarm-details {
  padding: 10px 0;
}

.alarm-description {
  margin: 0 0 10px 0;
  color: #606266;
  line-height: 1.5;
}

.alarm-location {
  margin: 10px 0;
  color: #909399;
  font-size: 14px;
}

.alarm-location i {
  margin-right: 5px;
}

.alarm-image {
  margin: 15px 0;
}

.alarm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 15px;
}
</style>