<template>
  <el-card shadow="never" class="border-0 p-2">
    <div class="flex items-center justify-between h-full">
      <!-- 任务信息 -->
      <div class="task-info">
        <div class="flex items-center">
          <el-badge :value="currentTask ? '进行中' : '空闲'" :type="currentTask ? 'primary' : 'info'" />
          <div class="task-name font-medium ml-2 text-gray-900">{{ typeof currentTask === 'object' ? currentTask.name : currentTask || '暂无任务' }}</div>
        </div>
        <div class="task-stats text-sm text-gray-500">
          已完成 {{ completedTasks }}/{{ totalTasks }} 个任务
        </div>
      </div>
      
      <!-- 进度和时间 -->
      <div class="progress-container flex items-center space-x-6">
        <div class="progress-bar-wrapper">
          <el-progress 
            :percentage="progress" 
            :stroke-width="8" 
            :text-inside="true"
            :color="progressColors"
            :show-text="true"
            class="w-80"
          ></el-progress>
        </div>
        
        <div class="remaining-time flex items-center">
          <el-icon class="text-blue-500 mr-2"><Timer /></el-icon>
          <div>
            <div class="text-xs text-gray-500">剩余时间</div>
            <div class="text-sm font-medium text-gray-700">{{ remainingTime || '--:--' }}</div>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script>
import { Timer } from '@element-plus/icons-vue'

export default {
  name: 'TaskProgressBar',
  components: {
    Timer
  },
  props: {
    progress: {
      type: Number,
      default: 0
    },
    currentTask: {
        type: [String, Object],
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
      return {
        '0%': '#1890ff',
        '100%': '#52c41a'
      }
    }
  }
}
</script>

<style scoped>
.task-progress-bar {
  height: 60px;
}

.progress-container {
  flex: 1;
  justify-content: flex-end;
}

.task-info {
  flex: 1;
}

/* 进度条样式 */
.el-progress-bar__inner {
  transition: width 1s ease-in-out;
}

/* 进度条文字样式 */
.el-progress-bar__innerText {
  color: #fff;
  font-size: 12px;
  font-weight: 500;
}

/* 动画效果 */
.task-info, .progress-container {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .w-80 {
    width: 200px !important;
  }
}

@media (max-width: 768px) {
  .el-card {
    padding: 1px;
  }
  
  .flex {
    flex-direction: column;
    gap: 10px;
  }
  
  .progress-container {
    width: 100%;
    justify-content: center;
  }
  
  .w-80 {
    width: 100% !important;
  }
  
  .task-info {
    width: 100%;
    text-align: center;
  }
}
</style>