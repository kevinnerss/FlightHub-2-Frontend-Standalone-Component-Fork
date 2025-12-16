<template>
  <div class="inspect-task-management-premium">
    <!-- 页面头部 -->
    <div class="page-header-premium">
      <div class="header-content">
        <div class="header-left">
          <div class="header-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="header-text">
            <h1 class="page-title">巡检任务管理</h1>
            <p class="page-subtitle">管理和监控无人机巡检任务执行情况</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 任务列表 -->
    <div class="task-content">
      <InspectTaskList />
    </div>
  </div>
</template>

<script>
import InspectTaskList from '../components/InspectTaskList.vue'

export default {
  name: 'InspectTaskManagement',
  components: {
    InspectTaskList
  },
  metaInfo: {
    title: '巡检任务管理 - FlightHub'
  }
}
</script>

<style scoped>
/* 主容器 */
.inspect-task-management-premium {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0;
  min-height: 100%;
}

/* 页面头部 */
.page-header-premium {
  margin-bottom: 32px;
}

.header-content {
  padding: 28px 36px;
  background: rgba(26, 31, 58, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2), 0 0 40px rgba(59, 130, 246, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
  animation: iconPulse 3s ease-in-out infinite;
}

@keyframes iconPulse {
  0%, 100% {
    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
  }
  50% {
    box-shadow: 0 4px 24px rgba(59, 130, 246, 0.6);
  }
}

.header-icon svg {
  width: 28px;
  height: 28px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 4px 0;
}

.page-subtitle {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
}

/* 任务内容区域 */
.task-content {
  background: rgba(26, 31, 58, 0.4);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}
</style>
