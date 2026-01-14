<template>
  <div class="map-shell">
    <div class="map-grid" aria-hidden="true"></div>
    <div class="map-noise" aria-hidden="true"></div>
    <div class="scan-line" aria-hidden="true"></div>

    <div class="map-center">
      <div class="badge">{{ label }}</div>
      <div class="hint">地图模型待接入 · 当前位置为占位渲染</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MapPlaceholder',
  props: {
    label: { type: String, default: '地图模块' }
  }
}
</script>

<style scoped>
.map-shell {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 420px;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(0, 212, 255, 0.22);
  background: radial-gradient(circle at 20% 30%, rgba(0, 212, 255, 0.10), transparent 45%),
    radial-gradient(circle at 80% 70%, rgba(168, 85, 247, 0.08), transparent 45%),
    rgba(10, 14, 39, 0.85);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35), 0 0 60px rgba(0, 212, 255, 0.10);
}

.map-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 212, 255, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 212, 255, 0.06) 1px, transparent 1px);
  background-size: 42px 42px;
  opacity: 0.6;
  transform: perspective(900px) rotateX(18deg) scale(1.12);
  transform-origin: center;
}

.map-noise {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.04), transparent 55%);
  mix-blend-mode: overlay;
  opacity: 0.6;
}

.scan-line {
  position: absolute;
  left: -20%;
  right: -20%;
  height: 140px;
  top: -20%;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(0, 212, 255, 0.08) 35%,
    rgba(0, 212, 255, 0.22) 50%,
    rgba(0, 212, 255, 0.08) 65%,
    transparent 100%
  );
  filter: blur(0px);
  animation: scan 4.5s linear infinite;
  pointer-events: none;
}

@keyframes scan {
  0% {
    transform: translateY(0) skewY(-6deg);
    opacity: 0.0;
  }
  10% {
    opacity: 1;
  }
  50% {
    opacity: 0.9;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(140%) skewY(-6deg);
    opacity: 0;
  }
}

.map-center {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 10px;
  z-index: 2;
  text-align: center;
  padding: 24px;
}

.badge {
  padding: 10px 16px;
  border-radius: 999px;
  background: rgba(0, 212, 255, 0.10);
  border: 1px solid rgba(0, 212, 255, 0.35);
  color: #e0f2fe;
  font-weight: 800;
  letter-spacing: 1px;
  text-shadow: 0 0 14px rgba(0, 212, 255, 0.35);
}

.hint {
  color: #94a3b8;
  font-size: 12px;
  letter-spacing: 0.6px;
}
</style>
