<template>
  <div class="task-progress-bar">
    <div class="progress-header">
      <div class="task-info">
        <span class="task-name">{{ currentTask || '暂无任务' }}</span>
        <span class="task-stats">{{ completedTasks }}/{{ totalTasks }} 个任务已完成</span>
      </div>
      <div class="time-info">
        <i class="el-icon-timer"></i>
        <span>剩余时间: {{ remainingTime || '--:--' }}</span>
      </div>
    </div>
    <div class="progress-container">
      <el-progress 
        :percentage="progress" 
        :stroke-width="20" 
        :text-inside="true"
        :color="progressColors"
        :show-text="true"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'TaskProgressBar',
  props: {
    progress: {
      type: Number,
      default: 0
    },
    currentTask: {
      type: String,
      default: ''
    },
    remainingTime: {
      type: String,
      default: '00:00:00'
    },
    completedTasks: {
      type: Number,
      default: 0
    },
    totalTasks: {
      type: Number,
      default: 0
    }
  },
  computed: {
    // 根据进度值生成颜色渐变
    progressColors() {
      // Element Plus 的 color 属性需要数组格式
      return [
        { color: '#1890ff', percentage: 0 },
        { color: '#52c41a', percentage: 100 }
      ]
    }
  }
}
</script>

<style scoped>
.task-progress-bar {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
}

.task-info {
  display: flex;
  flex-direction: column;
}

.task-name {
  font-weight: bold;
  margin-bottom: 4px;
  color: #303133;
}

.task-stats {
  color: #909399;
  font-size: 12px;
}

.time-info {
  display: flex;
  align-items: center;
  color: #606266;
}

.time-info i {
  margin-right: 5px;
}

.progress-container {
  width: 100%;
}
</style>