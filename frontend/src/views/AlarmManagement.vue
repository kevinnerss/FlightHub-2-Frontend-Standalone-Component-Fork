<template>
  <div class="alarm-management grid-bg">
    <!-- 页面标题 -->
    <div class="page-header glass-effect tech-border">
      <h1 class="text-2xl font-bold text-blue-400">告警管理</h1>
      <p class="text-gray-400">查看、管理和处理所有系统告警信息</p>
    </div>
    
    <!-- 告警列表组件 -->
    <div class="alarm-list-wrapper p-4">
      <AlarmList />
    </div>
  </div>
</template>

<script>
import AlarmList from '../components/AlarmList.vue'

export default {
  name: 'AlarmManagement',
  components: {
    AlarmList
  },
  metaInfo: {
    title: '告警管理 - 无人机巡检系统'
  }
}
</script>

<style scoped>
.alarm-management {
  width: 100%;
  height: 100%;
  background-color: #111827;
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  background-position: center center;
  display: flex;
  flex-direction: column;
}

.page-header {
  background-color: #1f2937;
  padding: 20px 30px;
  border-bottom: 1px solid #374151;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #3b82f6;
  position: relative;
  display: inline-block;
}

.page-header h1::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, #3b82f6, #10b981);
}

.page-header p {
  margin: 0;
  font-size: 14px;
  color: #9ca3af;
}

.alarm-list-wrapper {
  flex: 1;
  overflow: auto;
}

/* 科技风格边框 */
.tech-border {
  border: 1px solid #374151;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.15);
  position: relative;
  background: linear-gradient(135deg, rgba(31, 41, 55, 0.9), rgba(17, 24, 39, 0.9));
}

.tech-border::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #3b82f6, #10b981, #3b82f6);
  z-index: -1;
  animation: borderRotate 8s linear infinite;
  opacity: 0.3;
}

@keyframes borderRotate {
  0% { background-position: 0% 0%; }
  100% { background-position: 300% 0%; }
}

/* 玻璃效果 */
.glass-effect {
  backdrop-filter: blur(8px);
  background-color: rgba(31, 41, 55, 0.8);
}

/* 滚动条样式 */
.alarm-list-wrapper::-webkit-scrollbar {
  width: 8px;
}

.alarm-list-wrapper::-webkit-scrollbar-track {
  background: #1f2937;
}

.alarm-list-wrapper::-webkit-scrollbar-thumb {
  background-color: #4b5563;
  border-radius: 4px;
}

.alarm-list-wrapper::-webkit-scrollbar-thumb:hover {
  background-color: #6b7280;
}
</style>