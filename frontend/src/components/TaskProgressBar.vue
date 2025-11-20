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
    
    <!-- 进度指示器 -->
    <div class="progress-indicators">
      <div 
        v-for="index in totalTasks" 
        :key="index" 
        class="indicator" 
        :class="{ completed: index <= completedTasks, active: index === completedTasks + 1 }"
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

/* 进度指示器 */
.progress-indicators {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(100, 116, 139, 0.3);
  border: 1px solid rgba(100, 116, 139, 0.5);
  transition: all 0.3s ease;
}

.indicator.completed {
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  border-color: #00d4ff;
  box-shadow: 0 0 8px rgba(0, 212, 255, 0.6);
}

.indicator.active {
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  border-color: #00d4ff;
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.8);
  animation: activePulse 1.5s ease-in-out infinite;
  transform: scale(1.3);
}

@keyframes activePulse {
  0%, 100% {
    box-shadow: 0 0 12px rgba(0, 212, 255, 0.8);
  }
  50% {
    box-shadow: 0 0 20px rgba(0, 212, 255, 1);
  }
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