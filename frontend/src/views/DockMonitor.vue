<template>
  <div class="dock-monitor-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <span class="title-icon">🏭</span>
          机场监控中心
        </h1>
        <p class="page-subtitle">实时监控所有机场设备的运行状态</p>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="page-content">
      <DockStatusPanel />
    </div>
  </div>
</template>

<script>
import DockStatusPanel from '@/components/DockStatusPanel.vue'

export default {
  name: 'DockMonitor',
  components: {
    DockStatusPanel
  },
  mounted() {
    // 设置页面标题
    document.title = '机场监控 - FlightHub'
  }
}
</script>

<style scoped>
.dock-monitor-page {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0;
  min-height: 100%;
}

.page-header {
  margin-bottom: 32px;
}

.header-content {
  padding: 28px 36px;
  background: rgba(26, 31, 58, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(56, 189, 248, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2), 0 0 40px rgba(56, 189, 248, 0.1);
}

.page-title {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 32px;
  filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.4));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-8px);
  }
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: #94a3b8;
  font-weight: 400;
}

.page-content {
  background: rgba(26, 31, 58, 0.4);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(56, 189, 248, 0.2);
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 24px 20px;
  }

  .page-title {
    font-size: 24px;
  }

  .title-icon {
    font-size: 28px;
  }

  .page-subtitle {
    font-size: 12px;
  }
}

/* 打印样式 */
@media print {
  .dock-monitor-page {
    background: white;
  }

  .header-content {
    box-shadow: none;
    border: 1px solid #e0e0e0;
  }
}
</style>
