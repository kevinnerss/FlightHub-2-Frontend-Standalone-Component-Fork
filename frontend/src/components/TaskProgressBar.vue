<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
    <div class="flex flex-col space-y-3">
      <!-- 任务信息 -->
      <div class="flex justify-between items-center">
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">当前任务</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">{{ currentTask?.name || '无活动任务' }} <span v-if="currentTask?.id">({{ currentTask.id }})</span></p>
        </div>
        <div class="flex flex-col items-end">
          <span class="text-xs text-gray-500 dark:text-gray-400">剩余时间</span>
          <span class="text-lg font-semibold text-blue-600 dark:text-blue-400">{{ remainingTime || '--:--' }}</span>
        </div>
      </div>
      
      <!-- 进度条 -->
      <div class="w-full">
        <div class="relative pt-1">
          <div class="flex items-center justify-between mb-1">
            <div>
              <span class="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200 dark:bg-blue-900 dark:text-blue-300">
                进度
              </span>
            </div>
            <div class="text-right">
              <span class="text-xs font-semibold inline-block text-blue-600 dark:text-blue-400">
                {{ progress }}%
              </span>
            </div>
          </div>
          
          <!-- 背景进度条 -->
          <div class="overflow-hidden h-2 mb-4 text-xs flex rounded-full bg-gray-200 dark:bg-gray-700">
            <!-- 进度条填充 -->
            <div 
              class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-600 transition-all duration-500 ease-in-out"
              :style="{ width: progress + '%' }"
            ></div>
          </div>
        </div>
      </div>
      
      <!-- 任务统计 -->
      <div class="flex justify-between items-center text-sm">
        <div class="flex items-center text-gray-600 dark:text-gray-400">
          <i class="fa fa-check-circle text-green-500 mr-2"></i>
          <span>已完成 {{ completedTasks }} / {{ totalTasks }} 个任务</span>
        </div>
        <button class="text-blue-600 dark:text-blue-400 hover:underline flex items-center">
          <span>查看任务详情</span>
          <i class="fa fa-angle-right ml-1"></i>
        </button>
      </div>
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
      type: Object,
      default: null
    },
    remainingTime: {
      type: String,
      default: ''
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
/* 进度条动画 */
.bg-blue-600 {
  animation: progressAnimation 2s ease-in-out;
}

@keyframes progressAnimation {
  from {
    opacity: 0.7;
  }
  to {
    opacity: 1;
  }
}

/* 脉冲动画效果 */
@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

/* 当进度变化时触发动画 */
.bg-blue-600 {
  transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>