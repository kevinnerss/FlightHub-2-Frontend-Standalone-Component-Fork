<template>
  <div class="task-progress-bar p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md">
    <div class="flex justify-between items-center mb-2">
      <h3 class="font-medium text-gray-900 dark:text-white">{{ currentTask?.name || '当前任务' }}</h3>
      <span class="text-sm text-gray-600 dark:text-gray-400">{{ progress }}%</span>
    </div>
    <div class="h-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
      <div 
        class="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-1000 ease-out" 
        :style="{ width: `${progress}%` }"
      ></div>
    </div>
    <div class="mt-2 grid grid-cols-2 gap-4 text-sm">
      <div>
        <p class="text-gray-500 dark:text-gray-400">剩余时间</p>
        <p class="font-medium text-gray-900 dark:text-white">{{ remainingTime }}</p>
      </div>
      <div>
        <p class="text-gray-500 dark:text-gray-400">已执行</p>
        <p class="font-medium text-gray-900 dark:text-white">{{ completedTasks }}/{{ totalTasks }}</p>
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
.task-progress-bar {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>