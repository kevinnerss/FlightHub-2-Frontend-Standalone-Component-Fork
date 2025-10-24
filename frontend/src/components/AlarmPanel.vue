<template>
  <div class="alarm-panel h-full flex flex-col">
    <!-- 面板标题 -->
    <div class="panel-header flex justify-between items-center p-2 border-b">
      <h3 class="font-medium text-gray-900">报警信息</h3>
      <div class="flex items-center gap-2">
        <el-badge 
          v-if="alarms.length > 0" 
          :value="alarms.length" 
          type="danger" 
          size="small"
        />
        <el-button 
          size="small" 
          @click="handleRefresh" 
          plain
        >
          刷新
        </el-button>
        <el-button 
          v-if="alarms.length > 0" 
          size="small" 
          type="primary" 
          plain
          @click="markAllAsProcessed"
        >
          全部处理
        </el-button>
      </div>
    </div>
    
    <!-- 报警列表 -->
    <div class="alarm-list flex-grow overflow-y-auto p-2">
      <el-empty v-if="alarms.length === 0" description="暂无报警信息" class="py-4" />
      
      <el-timeline :reverse="false">
        <el-timeline-item
          v-for="alarm in alarms"
          :key="alarm.id"
          :timestamp="formatTime(alarm.timestamp)"
          :type="getAlarmType(alarm.severity)"
          placement="top"
        >
          <el-card :shadow="'hover'" class="alarm-card">
            <div class="flex justify-between items-start mb-2">
              <h4 class="font-medium text-gray-900">{{ alarm.title }}</h4>
              <el-tag 
                size="small" 
                :type="getAlarmType(alarm.severity)"
                effect="dark"
              >
                {{ alarm.severity }}级
              </el-tag>
            </div>
            <div class="text-sm text-gray-500 mb-2">{{ alarm.location }}</div>
            <p class="text-sm text-gray-600 mb-3">{{ alarm.description }}</p>
            
            <!-- 报警图片 -->
            <div v-if="alarm.imageUrl" class="mt-3 mb-3">
              <el-image
                :src="alarm.imageUrl"
                :preview-src-list="[alarm.imageUrl]"
                class="w-full h-40 object-cover rounded"
                fit="cover"
              ></el-image>
            </div>
            
            <div class="flex justify-end gap-2">
              <el-button 
                size="small" 
                type="danger" 
                @click="$emit('alarm-processed', alarm.id)"
              >
                标记已处理
              </el-button>
              <el-button 
                size="small" 
                type="primary" 
                @click="showAlarmDetail(alarm)"
              >
                查看详情
              </el-button>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
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
    // 刷新报警列表
    handleRefresh() {
      // 这里可以添加刷新逻辑
      console.log('刷新报警列表')
      this.$message.info('报警列表已刷新')
    },
    
    // 格式化日期时间
    formatTime(timestamp) {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    
    // 显示报警详情
    showAlarmDetail(alarm) {
      console.log('查看报警详情:', alarm)
      // 这里可以打开详情对话框
    },
    
    // 标记单个报警为已处理
    markAsProcessed(alarmId) {
      this.$emit('alarm-processed', alarmId)
      this.$message.success('报警已标记为已处理')
    },
    
    // 标记所有报警为已处理
    markAllAsProcessed() {
      this.$confirm('确定要标记所有报警为已处理吗？', '确认操作', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.alarms.forEach(alarm => {
          this.$emit('alarm-processed', alarm.id)
        })
        this.$message.success('所有报警已标记为已处理')
      }).catch(() => {
        this.$message.info('已取消操作')
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
    }
  }
}
</script>

<style scoped>
.alarm-panel {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background-color: #ffffff;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 滚动条样式 */
.alarm-list {
  flex-grow: 1;
  overflow-y: auto;
}

.alarm-list ::v-deep(.el-scrollbar__wrap) {
  overflow-x: hidden;
}

/* 卡片样式 */
.alarm-card {
  margin-bottom: 10px;
  animation: slideIn 0.3s ease-out;
  transition: all 0.2s ease;
}

.alarm-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 时间线样式调整 */
::v-deep(.el-timeline) {
  padding: 0;
}

::v-deep(.el-timeline-item) {
  padding-bottom: 20px;
}

::v-deep(.el-timeline-item__timestamp) {
  top: 2px;
  font-size: 12px;
  color: #909399;
}

/* 标题栏样式 */
.panel-header {
  border-bottom: 1px solid #ebeef5;
  padding: 10px 15px;
  background-color: #fafafa;
  border-top-left-radius: 6px;
  border-top-right-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 卡片内边距调整 */
::v-deep(.el-card__body) {
  padding: 15px;
}

/* 按钮样式优化 */
.el-button--small {
  font-size: 12px;
  padding: 6px 12px;
}

/* 高优先级报警闪烁效果 */
::v-deep(.el-timeline-item__node--danger) {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
  }
}

/* 动画效果 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .alarm-panel {
    border-radius: 0;
    border-left: none;
    border-right: none;
  }
  
  ::v-deep(.el-timeline-item__timestamp) {
    position: static;
    margin-bottom: 5px;
  }
  
  ::v-deep(.el-timeline-item__wrapper) {
    flex-direction: column;
  }
}
</style>