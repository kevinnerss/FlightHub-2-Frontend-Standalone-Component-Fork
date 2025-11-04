<template>
  <div class="task-progress-bar tech-border">
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
    <div class="progress-container tech-border-light">
      <el-progress 
        :percentage="progress" 
        :stroke-width="20" 
        :text-inside="true"
        :color="progressColors"
        :show-text="true"
        class="tech-progress"
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
        { color: '#3b82f6', percentage: 0 },  // 蓝色 - 初始
        { color: '#10b981', percentage: 50 }, // 绿色 - 中间
        { color: '#10b981', percentage: 100 } // 绿色 - 完成
      ]
    }
  }
}
</script>

<style scoped>
.task-progress-bar {
  padding: 15px;
  background: #1f2937;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

/* 科技感背景 */
.task-progress-bar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(59, 130, 246, 0.1) 25%, transparent 25%, transparent 50%, rgba(59, 130, 246, 0.1) 50%, rgba(59, 130, 246, 0.1) 75%, transparent 75%, transparent);
  background-size: 10px 10px;
  z-index: 0;
}

.task-progress-bar > * {
  position: relative;
  z-index: 1;
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
  color: #93c5fd;
  text-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
}

.task-stats {
  color: #9ca3af;
  font-size: 12px;
}

.time-info {
  display: flex;
  align-items: center;
  color: #d1d5db;
}

.time-info i {
  margin-right: 5px;
  color: #3b82f6;
}

.progress-container {
  width: 100%;
  background: #111827;
  padding: 8px;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.progress-container::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* Element Plus 进度条样式覆盖 */
:deep(.el-progress-bar__outer) {
  background-color: #374151;
  border: 1px solid #4b5563;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3) inset;
}

:deep(.el-progress-bar__inner) {
  border-radius: 10px;
  background: linear-gradient(90deg, #3b82f6, #10b981);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
  transition: width 0.6s ease;
}

:deep(.el-progress__text) {
  color: #ffffff;
  font-weight: 500;
  text-shadow: 0 0 2px rgba(59, 130, 246, 0.8);
}

/* 科技感进度条边框 */
.tech-progress {
  position: relative;
}

.tech-progress::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 12px;
  background: linear-gradient(45deg, #3b82f6, transparent, #3b82f6);
  z-index: -1;
  animation: borderGlow 2s linear infinite;
}

@keyframes borderGlow {
  0% { background-position: 0 0; }
  100% { background-position: 100px 100px; }
}
</style>