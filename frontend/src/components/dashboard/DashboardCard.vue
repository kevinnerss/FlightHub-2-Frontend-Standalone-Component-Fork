<template>
  <div class="dashboard-card">
    <div class="card-header">
      <div class="header-main">
        <span v-if="icon" class="card-icon" aria-hidden="true">{{ icon }}</span>
        <h3 class="card-title">{{ title }}</h3>
      </div>

      <router-link v-if="moreTo" :to="moreTo" class="more-btn">
        详情 <i class="arrow"></i>
      </router-link>
    </div>

    <div class="card-body">
      <div class="corner top-left"></div>
      <div class="corner top-right"></div>
      <div class="corner bottom-left"></div>
      <div class="corner bottom-right"></div>

      <div class="body-inner-container">
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
  </div>
</template>

<script>
export default {
  name: 'DashboardCard1',
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
  background: rgba(10, 35, 65, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 191, 255, 0.3);
  box-shadow: 0 0 20px rgba(0, 140, 255, 0.2) inset;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: visible;
  height: 100%;
  transition: all 0.3s ease;
}

.dashboard-card:hover {
  border-color: rgba(0, 191, 255, 0.5);
  box-shadow: 0 0 25px rgba(0, 140, 255, 0.3) inset;
}

.corner {
  position: absolute;
  width: 10px;
  height: 10px;
  border: 2px solid #00bfff;
  z-index: 2;
}
.top-left { top: -1px; left: -1px; border-right: none; border-bottom: none; }
.top-right { top: -1px; right: -1px; border-left: none; border-bottom: none; }
.bottom-left { bottom: -1px; left: -1px; border-right: none; border-top: none; }
.bottom-right { bottom: -1px; right: -1px; border-left: none; border-top: none; }

.card-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  background: linear-gradient(to bottom, rgba(0, 110, 255, 0.25), transparent);
  border-bottom: 1px solid rgba(0, 191, 255, 0.15);
  min-height: 48px;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 60%;
}

.more-btn {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);

  background: rgba(0, 162, 255, 0.1);
  border: 1px solid rgba(0, 191, 255, 0.6);
  color: #aaddff;
  padding: 4px 12px;
  cursor: pointer;
  font-size: 12px;
  text-decoration: none;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  white-space: nowrap;
}

.more-btn:hover {
  background: rgba(0, 191, 255, 0.3);
  color: #ffffff;
  box-shadow: 0 0 10px rgba(0, 191, 255, 0.5);
}

.card-icon {
  font-size: 16px;
  filter: drop-shadow(0 0 5px rgba(0, 191, 255, 0.8));
}

.card-title {
  margin: 0;
  color: #ffffff;
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(0, 191, 255, 0.8);
}

.arrow {
  display: inline-block;
  width: 5px;
  height: 5px;
  border-top: 1px solid #aaddff;
  border-right: 1px solid #aaddff;
  transform: rotate(45deg);
  margin-left: 6px;
}

.card-body {
  flex: 1;
  padding: 10px;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.body-inner-container {
  flex: 1;
  border: 1px solid rgba(0, 191, 255, 0.15);
  padding: 12px;
  overflow-y: auto;
  position: relative;
  background: rgba(0, 0, 0, 0.1);
}

.body-inner-container::-webkit-scrollbar {
  width: 4px;
}
.body-inner-container::-webkit-scrollbar-thumb {
  background: rgba(0, 191, 255, 0.3);
  border-radius: 2px;
}

.state-block {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #aaddff;
}

.state-block.error {
  color: #ff6b6b;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(0, 191, 255, 0.2);
  border-top-color: #00bfff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.state-text {
  font-size: 13px;
  opacity: 0.8;
}
</style>