<template>
  <div class="donut-ring">
    <svg class="donut-chart" viewBox="0 0 140 140" role="img" aria-label="占比圆环">
      <defs>
        <filter :id="glowId" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="3" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <circle
        class="donut-track"
        cx="70"
        cy="70"
        r="44"
        fill="none"
        stroke="rgba(255,255,255,0.05)"
        stroke-width="14"
      />

      <circle
        v-for="(item, idx) in normalizedSeries"
        :key="item.id ?? item.name ?? idx"
        class="donut-segment"
        :filter="`url(#${glowId})`"
        cx="70"
        cy="70"
        r="44"
        fill="none"
        :stroke="item.color"
        stroke-linecap="round"
        stroke-width="14"
        :stroke-dasharray="getDonutDash(item.value)"
        :stroke-dashoffset="getDonutOffset(idx)"
        transform="rotate(-90 70 70)"
      />

      <text x="70" y="64" text-anchor="middle" class="donut-label">{{ totalLabel }}</text>
      <text x="70" y="84" text-anchor="middle" class="donut-value">
        {{ displayTotal }}
      </text>
    </svg>
  </div>
</template>

<script>
export default {
  name: 'DonutRing',
  props: {
    series: { type: Array, default: () => [] },
    totalLabel: { type: String, default: '总异常' },
    totalValue: { type: [Number, String], default: null }
  },
  data() {
    return {
      glowId: `glow-${Math.random().toString(36).slice(2, 10)}`
    }
  },
  computed: {
    normalizedSeries() {
      return (this.series || []).filter(item => item && Number(item.value) > 0)
    },
    donutTotal() {
      return this.normalizedSeries.reduce((sum, item) => sum + Number(item.value || 0), 0)
    },
    displayTotal() {
      if (this.totalValue === null || this.totalValue === undefined || this.totalValue === '') {
        return this.donutTotal
      }
      const n = Number(this.totalValue)
      return Number.isFinite(n) ? n : this.totalValue
    }
  },
  methods: {
    getDonutDash(value) {
      const circumference = 2 * Math.PI * 44
      const total = this.donutTotal || 1
      const length = (Number(value || 0) / total) * circumference
      return `${length} ${circumference}`
    },
    getDonutOffset(index) {
      const circumference = 2 * Math.PI * 44
      const total = this.donutTotal || 1
      const previous = this.normalizedSeries.slice(0, index).reduce((sum, item) => sum + Number(item.value || 0), 0)
      return -((previous / total) * circumference)
    }
  }
}
</script>

<style scoped>
.donut-ring {
  display: flex;
  align-items: center;
  justify-content: center;
}

.donut-chart {
  width: 150px;
  height: 150px;
  flex-shrink: 0;
}

.donut-segment {
  transition: opacity 0.2s ease;
}

.donut-track {
  opacity: 0.75;
}

.donut-label {
  fill: #94a3b8;
  font-size: 12px;
  letter-spacing: 1px;
}

.donut-value {
  fill: #e0f2fe;
  font-size: 22px;
  font-weight: 800;
}
</style>

