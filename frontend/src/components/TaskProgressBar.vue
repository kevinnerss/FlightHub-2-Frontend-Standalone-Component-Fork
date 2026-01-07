<template>
  <div class="task-progress-premium">
    <!-- 任务信息 -->
    <div class="progress-header">
      <div class="task-info">
        <span class="task-name">{{ currentTask || '暂无任务' }}</span>
        <span class="task-stats">{{ completedTasks }} / {{ totalTasks }} 个任务已完成</span>
      </div>
      <div class="time-info">
        <span class="time-icon">⏱️</span>
        <span>{{ remainingTime || '--:--' }}</span>
      </div>
    </div>
    
    <!-- 进度条 -->
    <div class="progress-bar-container">
      <div class="progress-bar-bg">
        <div class="progress-bar-fill" :style="{ width: progress + '%' }">
          <div class="progress-glow"></div>
        </div>
      </div>
      <div class="progress-text">{{ progress }}%</div>
    </div>
    
    <!-- 进度计数 -->
    <div class="progress-count-display">
      <span class="count-number">{{ Math.min(completedTasks + 1, totalTasks) }}</span>
      <span class="count-separator">/</span>
      <span class="count-total">{{ totalTasks }}</span>
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
  }
}
</script>

<style scoped>
.task-progress-premium {
  background: rgba(26, 31, 58, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(0, 212, 255, 0.2);
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

/* 进度头部 */
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.task-name {
  font-size: 16px;
  font-weight: 700;
  color: #00d4ff;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.task-stats {
  font-size: 13px;
  color: #94a3b8;
}

.time-info {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 8px;
  color: #00d4ff;
  font-size: 14px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.time-icon {
  font-size: 16px;
}

/* 进度条容器 */
.progress-bar-container {
  position: relative;
  margin-bottom: 16px;
}

.progress-bar-bg {
  height: 32px;
  background: rgba(10, 14, 39, 0.8);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3);
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff 0%, #0099ff 50%, #00d4ff 100%);
  background-size: 200% 100%;
  border-radius: 16px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  animation: shimmer 2s linear infinite;
  box-shadow: 
    0 0 20px rgba(0, 212, 255, 0.4),
    inset 0 0 20px rgba(255, 255, 255, 0.2);
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.progress-glow {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: glow 2s linear infinite;
}

@keyframes glow {
  0% {
    left: -100%;
  }
  100% {
    left: 200%;
  }
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  pointer-events: none;
}

/* 进度计数 */
.progress-count-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
  margin-top: 8px;
}

.count-number {
  font-size: 24px;
  font-weight: 700;
  color: #00d4ff;
  font-family: 'DIN Alternate', 'Courier New', sans-serif;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.4);
}

.count-separator {
  font-size: 16px;
  color: #64748b;
  margin: 0 2px;
}

.count-total {
  font-size: 16px;
  color: #94a3b8;
  font-weight: 600;
}

/* 响应式 */
@media (max-width: 768px) {
  .progress-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .time-info {
    align-self: flex-start;
  }
}
</style>