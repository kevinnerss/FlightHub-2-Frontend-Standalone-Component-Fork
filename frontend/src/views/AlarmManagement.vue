<template>
  <div class="alarm-management-premium">
    <!-- 页面头部 -->
    <div class="page-header-premium">
      <div class="header-content">
        <div class="header-left">
          <div class="header-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="12" y1="9" x2="12" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="12" y1="17" x2="12.01" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="header-text">
            <h1 class="page-title">告警管理</h1>
            <p class="page-subtitle">监控和处理系统告警信息</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 告警列表 -->
    <div class="alarm-content">
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
    title: '告警管理 - FlightHub'
  }
}
</script>

<style scoped>
/* 主容器 */
.alarm-management-premium {
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
  border: 1px solid rgba(239, 68, 68, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2), 0 0 40px rgba(239, 68, 68, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.4);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 4px 16px rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 4px 24px rgba(239, 68, 68, 0.6);
  }
}

.header-icon svg {
  width: 28px;
  height: 28px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
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

/* 告警内容区域 */
.alarm-content {
  background: rgba(26, 31, 58, 0.4);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(239, 68, 68, 0.2);
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}
</style>