<template>
  <div class="dashboard-card">
    <div class="card-header">
      <div class="header-left">
        <span v-if="icon" class="card-icon" aria-hidden="true">{{ icon }}</span>
        <h3 class="card-title">{{ title }}</h3>
      </div>
      <router-link v-if="moreTo" :to="moreTo" class="more-btn">
        <span>更多</span>
      </router-link>
    </div>

    <div class="card-body">
      <div v-if="loading" class="state-block">
        <div class="loading-spinner"></div>
        <div class="state-text">加载中...</div>
      </div>

      <div v-else-if="error" class="state-block error">
        <div class="state-text">{{ error }}</div>
      </div>

      <div v-else-if="isEmpty" class="state-block">
        <div class="state-text">{{ emptyText }}</div>
      </div>

      <slot v-else />
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardCard',
  props: {
    title: { type: String, required: true },
    icon: { type: String, default: '' },
    moreTo: { type: [String, Object], default: '' },
    loading: { type: Boolean, default: false },
    error: { type: String, default: '' },
    emptyText: { type: String, default: '暂无数据' },
    isEmpty: { type: Boolean, default: false }
  }
}
</script>

<style scoped>
.dashboard-card {
  background: rgba(30, 41, 59, 0.45);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 212, 255, 0.18);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25), 0 0 40px rgba(0, 212, 255, 0.08);
}

.card-header {
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: linear-gradient(
    135deg,
    rgba(0, 212, 255, 0.10) 0%,
    rgba(0, 153, 255, 0.08) 100%
  );
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.card-icon {
  width: 28px;
  height: 28px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #e0f2fe;
  background: rgba(0, 212, 255, 0.12);
  border: 1px solid rgba(0, 212, 255, 0.22);
  box-shadow: 0 0 18px rgba(0, 212, 255, 0.15);
  flex-shrink: 0;
}

.card-title {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.more-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border-radius: 10px;
  background: rgba(0, 212, 255, 0.10);
  border: 1px solid rgba(0, 212, 255, 0.22);
  color: #7dd3fc;
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.more-btn:hover {
  background: rgba(0, 212, 255, 0.18);
  border-color: rgba(0, 212, 255, 0.42);
  color: #e0f2fe;
  transform: translateY(-1px);
  box-shadow: 0 0 16px rgba(0, 212, 255, 0.18);
}

.card-body {
  padding: 14px 16px 16px;
  min-height: 120px;
}

.state-block {
  min-height: 96px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #cbd5e1;
}

.state-block.error {
  color: #fecaca;
}

.state-text {
  font-size: 12px;
  color: inherit;
  opacity: 0.9;
  text-align: center;
}

.loading-spinner {
  width: 22px;
  height: 22px;
  border: 3px solid rgba(0, 212, 255, 0.18);
  border-top-color: rgba(0, 212, 255, 0.75);
  border-radius: 999px;
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
