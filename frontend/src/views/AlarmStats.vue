<template>
  <div class="alarm-stats-page">
    <div class="page-header">
      <div class="title-block">
        <p class="page-kicker">沈阳地铁三号线 智能轨道巡检无人机</p>
        <h1 class="page-title">告警统计</h1>
        <p class="page-subtitle">近一年各航线月度告警趋势，可点击节点查看当月详情</p>
      </div>
      <div class="header-meta">
        <div class="meta-chip">
          <span class="meta-label">统计周期</span>
          <span class="meta-value">近 12 个月</span>
        </div>
        <div class="meta-chip">
          <span class="meta-label">更新时间</span>
          <span class="meta-value">{{ lastUpdated }}</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载告警统计...</p>
    </div>
    <div v-else>
      <div v-if="error" class="error-state">{{ error }}</div>

      <div class="top-grid">
        <div class="card hero-card">
          <div class="hero-overlay"></div>
          <div class="hero-content">
            <div class="hero-header">
              <div>
                <p class="hero-label">安全运行天数</p>
                <div class="hero-number">
                  {{ stats.safetyDays }}
                  <span class="hero-unit">天</span>
                </div>
              </div>
              <span class="hero-tag">近一年</span>
            </div>
            <div class="hero-summary">
              <div v-for="status in safetyStatuses" :key="status.label" class="summary-chip">
                <span class="chip-dot" :style="{ background: status.color }"></span>
                <span class="chip-label">{{ status.label }}</span>
                <span class="chip-value">{{ status.value }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="card metrics-card">
          <div class="card-header">
            <h3 class="card-title">巡检指标</h3>
            <span class="card-subtitle">累计与当日概览</span>
          </div>
          <div class="metrics-grid">
            <div v-for="metric in metrics" :key="metric.label" class="metric-item">
              <div class="metric-label">{{ metric.label }}</div>
              <div class="metric-value">
                {{ metric.value }}
                <span v-if="metric.delta" class="metric-trend" :class="metric.trend">
                  <span v-if="metric.trend === 'up'">↑</span>
                  <span v-else-if="metric.trend === 'down'">↓</span>
                  <span v-else>→</span>
                  {{ metric.delta }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="card donut-card">
          <div class="card-header">
            <h3 class="card-title">异常点位趋势分布</h3>
            <span class="card-subtitle">按航线占比</span>
          </div>
          <div class="donut-content">
            <svg class="donut-chart" viewBox="0 0 140 140" role="img" aria-label="异常占比">
              <defs>
                <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
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
                v-for="(item, idx) in donutSeries"
                :key="item.name"
                class="donut-segment"
                filter="url(#glow)"
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
              <text x="70" y="64" text-anchor="middle" class="donut-label">总异常</text>
              <text x="70" y="84" text-anchor="middle" class="donut-value">
                {{ donutTotal }}
              </text>
            </svg>
            <div class="donut-legend">
              <div v-for="item in donutSeries" :key="item.name" class="legend-item">
                <span class="legend-dot" :style="{ background: item.color }"></span>
                <div class="legend-text">
                  <span class="legend-name">{{ item.name }}</span>
                  <span class="legend-value">{{ getDonutPercent(item.value) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

        <div class="card chart-card">
          <div class="card-header">
            <div>
              <h3 class="card-title">异常点位时间分布</h3>
              <span class="card-subtitle">按月份分布的航线异常趋势（点击节点查看当月告警）</span>
          </div>
          <div class="series-legend">
            <div v-for="serie in lineChart.series" :key="serie.id" class="series-chip">
              <span class="legend-dot" :style="{ background: serie.color }"></span>
              <span class="legend-name">{{ serie.name }}</span>
            </div>
          </div>
        </div>
        <div class="line-chart-wrapper" v-if="lineChart.series.length">
          <div class="chart-area">
            <div class="y-axis">
              <span v-for="value in yAxisTicks" :key="value">{{ value }}</span>
            </div>
            <svg
              class="line-chart"
              :viewBox="`0 0 ${chartSize.width} ${chartSize.height}`"
              preserveAspectRatio="none"
            >
              <g class="grid-lines">
                <line
                  v-for="(line, idx) in gridLines"
                  :key="idx"
                  :x1="0"
                  :y1="line.y"
                  :x2="chartSize.width"
                  :y2="line.y"
                  stroke="rgba(255,255,255,0.05)"
                  stroke-width="1"
                />
              </g>
              <g class="chart-series">
                <g v-for="serie in lineChart.series" :key="serie.id">
                  <path
                    :d="getLinePath(serie.data)"
                    :stroke="serie.color"
                    fill="none"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                  <g class="data-points">
                    <g v-for="(point, idx) in getLinePoints(serie.data)" :key="point.x + '-' + point.y">
                      <circle
                        :cx="point.x"
                        :cy="point.y"
                        :r="5"
                        :fill="getPointColor(serie, idx)"
                        stroke="rgba(255,255,255,0.8)"
                        stroke-width="1.5"
                        class="chart-point"
                        @click="handlePointClick(serie, idx, $event)"
                      />
                    </g>
                  </g>
                </g>
              </g>
            </svg>
          </div>
          <div class="x-axis" :style="axisPaddingStyle">
            <span v-for="label in lineChart.categories" :key="label">{{ label }}</span>
          </div>
        </div>
        <div v-else class="empty-state">暂无告警数据</div>
      </div>
    </div>

    <div v-if="detailModal.visible" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal-premium detail-modal">
        <div class="modal-header">
          <h3 class="modal-title">{{ detailModal.waylineName }} · {{ detailModal.monthLabel }} 告警</h3>
          <button @click="closeDetailModal" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div v-if="detailModal.loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载当月告警...</p>
          </div>
          <div v-else>
            <div v-if="!detailModal.alarms.length" class="empty-state">该月份暂无告警</div>
            <div v-else class="detail-list">
              <div v-for="alarm in detailModal.alarms" :key="alarm.id" class="detail-row">
                <div class="detail-main">
                  <div class="detail-title">{{ alarm.content || '未填写描述' }}</div>
                  <div class="detail-meta">
                    <span>时间：{{ formatDateTime(alarm.created_at) }}</span>
                    <span>航线：{{ resolveWaylineName(alarm) }}</span>
                    <span v-if="alarm.latitude && alarm.longitude">坐标：{{ alarm.latitude }}, {{ alarm.longitude }}</span>
                  </div>
                </div>
                <div class="detail-badges">
                  <span class="status-pill">ID: {{ alarm.id }}</span>
                  <span class="status-pill">{{ alarm.status || '未知状态' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeDetailModal" class="modal-btn secondary-btn">关闭</button>
        </div>
      </div>
    </div>

        <div
          v-if="selectionMenu.visible"
          class="selection-pop"
          :style="{ top: `${selectionMenu.y}px`, left: `${selectionMenu.x}px` }"
        >
      <div class="selection-header">
        <span>选择航线查看当月告警</span>
        <button class="close-btn" @click="selectionMenu.visible = false">×</button>
      </div>
      <div class="selection-options">
        <button
          v-for="option in selectionMenu.options"
          :key="option.id"
          class="selection-item"
          @click="selectSeriesOption(option)"
        >
          <span class="legend-dot" :style="{ background: option.color || '#38bdf8' }"></span>
          <span class="option-name">{{ option.name }}</span>
          <span class="option-value">{{ option.data?.[selectionMenu.monthIndex] || 0 }} 条</span>
        </button>
          </div>
        </div>

    <div
      v-if="emptyTip.visible"
      class="selection-pop"
      :style="{ top: `${emptyTip.y}px`, left: `${emptyTip.x}px` }"
    >
      <div class="selection-header">
        <span>{{ emptyTip.text }}</span>
        <button class="close-btn" @click="emptyTip.visible = false">×</button>
      </div>
    </div>
  </div>
</template>

<script>
import alarmApi from '../api/alarmApi'

export default {
  name: 'AlarmStats',
  data() {
    return {
      loading: true,
      error: '',
      lastUpdated: '',
      months: [],
      waylines: [],
      waylineNameMap: {},
      stats: {
        safetyDays: 0,
        totalAlarms: 0,
        todayAlarms: 0,
        totalMileage: '--',
        todayMileage: '--'
      },
      safetyStatuses: [
        { label: '同里程位', value: 0, color: '#38bdf8' },
        { label: '重要点位', value: 0, color: '#a855f7' },
        { label: '安全位', value: 0, color: '#22c55e' }
      ],
      metrics: [],
      lineChart: {
        categories: [],
        series: []
      },
      donutSeries: [],
      chartSize: {
        width: 1080,
        height: 320
      },
      chartPaddingX: 28,
      chartPaddingY: 16,
      latestAlarmDate: null,
      windowAlarms: [],
      detailModal: {
        visible: false,
        loading: false,
        waylineId: null,
        waylineName: '',
        monthLabel: '',
        alarms: []
      },
      // 高对比度调色板（顺序循环使用）
      seriesColors: [
        '#20A4F3', // 鲜亮蓝
        '#FF6B6B', // 亮红
        '#7C3AED', // 深紫
        '#16A34A', // 纯绿
        '#F59E0B', // 琥珀橙
        '#0EA5E9', // 青蓝
        '#EF4444', // 鲜红
        '#14B8A6', // 松石绿
        '#8B5CF6', // 紫罗兰
        '#F97316', // 亮橙
        '#22C55E', // 草绿
        '#C026D3'  // 品红
      ],
      selectionMenu: {
        visible: false,
        options: [],
        monthIndex: null,
        x: 0,
        y: 0
      },
      overlapColor: '#ffffff',
      emptyTip: {
        visible: false,
        text: '暂无告警信息',
        x: 0,
        y: 0
      },
      emptyTipTimer: null
    }
  },
  computed: {
    donutTotal() {
      return this.donutSeries.reduce((sum, item) => sum + item.value, 0)
    },
    maxLineValue() {
      const values = this.lineChart.series.flatMap(item => item.data)
      return Math.max(...values, 1)
    },
    gridLines() {
      const lines = []
      const steps = 5
      const innerHeight = Math.max(this.chartSize.height - this.chartPaddingY * 2, 1)
      for (let i = 0; i <= steps; i++) {
        const y = this.chartPaddingY + (innerHeight / steps) * i
        lines.push({ y })
      }
      return lines
    },
    yAxisTicks() {
      const steps = 5
      const max = this.maxLineValue || 1
      const stepVal = max / steps
      const ticks = []
      for (let i = 0; i <= steps; i++) {
        const val = Math.max(0, max - stepVal * i)
        ticks.push(Math.round(val * 10) / 10)
      }
      return ticks
    },
    axisPaddingStyle() {
      return {
        paddingLeft: `${this.chartPaddingX}px`,
        paddingRight: `${this.chartPaddingX}px`
      }
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = ''
      try {
        // 先获取最新告警时间，用作时间轴锚点
        const latest = await this.fetchLatestCreatedAt()
        this.initMonths(latest || new Date())
        await Promise.all([this.fetchWaylines(), this.fetchAndAggregateAlarms()])
        if (!this.lastUpdated && latest) {
          this.lastUpdated = this.formatDateTime(latest)
        }
      } catch (err) {
        console.error('加载告警统计失败', err)
        this.error = '加载告警统计失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    initMonths(baseDate = new Date()) {
      const months = []
      const anchor = this.parsePlainDate(baseDate) || new Date()
      for (let i = 11; i >= 0; i--) {
        const date = new Date(anchor.getFullYear(), anchor.getMonth() - i, 1)
        const start = new Date(date.getFullYear(), date.getMonth(), 1, 0, 0, 0, 0)
        const end = new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59, 999)
        months.push({
          label: `${date.getMonth() + 1}月`,
          key: `${date.getFullYear()}-${date.getMonth()}`,
          start,
          end
        })
      }
      this.months = months
      this.lineChart.categories = months.map(m => m.label)
    },
    async fetchWaylines() {
      try {
        const res = await alarmApi.getWaylines()
        const list = this.normalizeList(res)
        this.waylines = list
        this.waylineNameMap = list.reduce((map, item) => {
          const id = item.wayline_id || item.id
          if (id !== undefined && id !== null) {
            map[id] = item.name || `航线${id}`
          }
          return map
        }, {})
      } catch (err) {
        console.warn('加载航线列表失败，使用空列表', err)
        this.waylines = []
        this.waylineNameMap = {}
      }
    },
    normalizeList(res) {
      if (!res) return []
      if (Array.isArray(res)) return res
      if (res.results) return res.results
      if (res.data) return res.data
      return []
    },
    resolveWaylineId(alarm) {
      return (
        alarm?.wayline_id ??
        alarm?.wayline?.id ??
        alarm?.wayline?.wayline_id ??
        alarm?.wayline_details?.id ??
        alarm?.wayline_details?.wayline_id ??
        null
      )
    },
    resolveWaylineName(alarm) {
      const id = this.resolveWaylineId(alarm)
      return (
        alarm?.wayline?.name ||
        alarm?.wayline_details?.name ||
        this.waylineNameMap[id] ||
        (id ? `航线${id}` : '未知航线')
      )
    },
    async fetchAndAggregateAlarms() {
      // 若已有时间窗口，用其开始结束做服务端过滤，避免漏数据；否则先取全部再重建窗口
      const hasWindow = this.months.length > 0
      const params = { page_size: 20000 }
      if (hasWindow) {
        params.start_date = this.formatDateParam(this.months[0].start)
        params.end_date = this.formatDateParam(this.months[this.months.length - 1].end)
      }

      const alarms = await this.fetchAllAlarms(params)
      const latest = this.getLatestCreatedAt(alarms)

      // 用最新告警时间重建月份范围
      const anchor = latest || this.latestAlarmDate || new Date()
      this.initMonths(anchor)

      // 过滤出窗口内的数据再聚合（按时间范围判定月份）
      const inWindowAlarms = alarms.filter(item => this.getMonthIndexFromString(item.created_at) !== -1)
      this.windowAlarms = inWindowAlarms

      this.buildStatsFromAlarms(inWindowAlarms)
      this.buildSeries(inWindowAlarms)

      if (latest) {
        this.lastUpdated = this.formatDateTime(latest)
      } else if (!this.lastUpdated && this.latestAlarmDate) {
        this.lastUpdated = this.formatDateTime(this.latestAlarmDate)
      }
    },
    async fetchAllAlarms(baseParams) {
      const pageSize = baseParams.page_size || 20000
      let page = 1
      const collected = []
      let hasNext = true
      let totalCount = null
      // 分页抓取：优先看 next，其次看 count，再看页大小
      while (hasNext) {
        const res = await alarmApi.getAlarms({ ...baseParams, page, page_size: pageSize })
        const list = this.normalizeList(res)
        collected.push(...list)

        if (totalCount === null && res && typeof res.count === 'number') {
          totalCount = res.count
        }

        const hasNextFlag = Boolean(res && res.next)
        const needByCount = totalCount !== null ? collected.length < totalCount : false
        const needBySize = list.length === pageSize

        hasNext = hasNextFlag || needByCount || needBySize
        if (!hasNext) break
        page += 1
      }
      return collected
    },
    async fetchLatestCreatedAt() {
      try {
        const res = await alarmApi.getAlarms({ page_size: 1, ordering: '-created_at' })
        const list = this.normalizeList(res)
        if (list.length && list[0].created_at) {
          const ts = this.parsePlainDate(list[0].created_at)
          this.latestAlarmDate = ts
          this.lastUpdated = this.formatDateTime(ts)
          return ts
        }
      } catch (err) {
        console.warn('获取最新告警时间失败', err)
      }
      return null
    },
    buildStatsFromAlarms(alarms) {
      this.stats.totalAlarms = alarms.length
      const todayKey = this.formatDateParam(new Date())
      this.stats.todayAlarms = alarms.filter(item => this.formatDateParam(this.parsePlainDate(item.created_at)) === todayKey).length
      const latest = alarms.reduce((latestTs, alarm) => {
        const ts = this.parsePlainDate(alarm.created_at)
        if (Number.isNaN(ts.getTime())) return latestTs
        if (!latestTs) return ts
        return ts > latestTs ? ts : latestTs
      }, null)
      if (latest) {
        const now = Date.now()
        const diffDays = Math.floor((now - latest.getTime()) / (1000 * 60 * 60 * 24))
        this.stats.safetyDays = Math.max(diffDays, 0)
      } else {
        const windowStart = this.months && this.months.length ? this.months[0].start : null
        if (windowStart instanceof Date && !Number.isNaN(windowStart.getTime())) {
          const diffDays = Math.floor((Date.now() - windowStart.getTime()) / (1000 * 60 * 60 * 24))
          this.stats.safetyDays = Math.max(diffDays, 0)
        } else {
          this.stats.safetyDays = 0
        }
      }
      this.safetyStatuses = [
        { label: '今日异常', value: this.stats.todayAlarms, color: '#38bdf8' },
        { label: '近月异常', value: alarms.filter(a => this.isInCurrentMonth(a.created_at)).length, color: '#a855f7' },
        { label: '全年异常', value: this.stats.totalAlarms, color: '#22c55e' }
      ]
      this.metrics = [
        { label: '发现异常总数', value: this.stats.totalAlarms, trend: 'up', delta: '' },
        { label: '今日发现异常数', value: this.stats.todayAlarms, trend: this.stats.todayAlarms ? 'up' : 'flat', delta: this.stats.todayAlarms ? `+${this.stats.todayAlarms}` : '持平' },
        { label: '巡检总里程', value: this.stats.totalMileage, trend: 'flat', delta: '' },
        { label: '今日巡检里程', value: this.stats.todayMileage, trend: 'flat', delta: '' }
      ]
    },
    isInCurrentMonth(dateLike) {
      const dt = this.parsePlainDate(dateLike)
      const now = new Date()
      return dt.getFullYear() === now.getFullYear() && dt.getMonth() === now.getMonth()
    },
    buildSeries(alarms) {
      const seriesMap = new Map()
      alarms.forEach(alarm => {
        const waylineId = this.resolveWaylineId(alarm)
        if (waylineId === null || waylineId === undefined) return
        const monthIndex = this.getMonthIndexFromString(alarm.created_at)
        if (monthIndex === -1) return
        if (!seriesMap.has(waylineId)) {
          seriesMap.set(waylineId, {
            id: waylineId,
            name: this.resolveWaylineName(alarm),
            data: Array(this.months.length).fill(0)
          })
        }
        seriesMap.get(waylineId).data[monthIndex] += 1
      })

      const series = Array.from(seriesMap.values())
      series.sort((a, b) => b.data.reduce((sum, n) => sum + n, 0) - a.data.reduce((sum, n) => sum + n, 0))
      series.forEach((item, idx) => {
        item.color = this.getSeriesColor(idx)
      })
      this.lineChart.series = series
      this.lineChart.categories = this.months.map(m => m.label)

      this.donutSeries = series.map(item => ({
        name: item.name,
        value: item.data.reduce((sum, n) => sum + n, 0),
        color: item.color
      }))
    },
    getSeriesColor(index) {
      return this.seriesColors[index % this.seriesColors.length]
    },
    getDonutDash(value) {
      const circumference = 2 * Math.PI * 44
      const length = (value / (this.donutTotal || 1)) * circumference
      return `${length} ${circumference}`
    },
    getDonutOffset(index) {
      const circumference = 2 * Math.PI * 44
      const previous = this.donutSeries.slice(0, index).reduce((sum, item) => sum + item.value, 0)
      return -((previous / (this.donutTotal || 1)) * circumference)
    },
    getDonutPercent(value) {
      if (!this.donutTotal) return 0
      return Math.round((value / this.donutTotal) * 100)
    },
    getLinePoints(seriesData) {
      const count = this.lineChart.categories.length || 1
      const innerWidth = Math.max(this.chartSize.width - this.chartPaddingX * 2, 1)
      const innerHeight = Math.max(this.chartSize.height - this.chartPaddingY * 2, 1)
      const max = this.maxLineValue || 1
      const step = count > 1 ? innerWidth / (count - 1) : innerWidth
      return seriesData.map((value, idx) => {
        const x =
          count > 1
            ? this.chartPaddingX + step * idx
            : this.chartPaddingX + innerWidth / 2
        const y = this.chartPaddingY + innerHeight - (value / max) * innerHeight
        return { x, y }
      })
    },
    getLinePath(seriesData) {
      const points = this.getLinePoints(seriesData)
      if (!points.length) return ''
      const [first, ...rest] = points
      const pathParts = rest.map(point => `L ${point.x} ${point.y}`)
      return `M ${first.x} ${first.y} ${pathParts.join(' ')}`
    },
    getLatestCreatedAt(list) {
      const latest = list.reduce((acc, item) => {
        const ts = this.parsePlainDate(item.created_at)
        if (Number.isNaN(ts.getTime())) return acc
        if (!acc) return ts
        return ts > acc ? ts : acc
      }, null)
      return latest
    },
    handlePointClick(serie, monthIndex, event) {
      const month = this.months[monthIndex]
      if (!month) return
      const value = serie.data?.[monthIndex] || 0
      if (!value) {
        this.selectionMenu.visible = false
        this.showEmptyTip(event, '该月份无告警信息')
        return
      }
      const pointValue = serie.data?.[monthIndex] || 0
      const candidates = this.lineChart.series.filter(item => {
        const v = item.data?.[monthIndex] || 0
        return v > 0 && v === pointValue
      })
      if (candidates.length <= 1 || !event) {
        return this.openDetailFor(serie, monthIndex)
      }
      this.selectionMenu.visible = true
      this.selectionMenu.options = candidates
      this.selectionMenu.monthIndex = monthIndex
      this.selectionMenu.x = event.clientX + 12
      this.selectionMenu.y = event.clientY + 12 + window.scrollY
    },
    async openDetailFor(serie, monthIndex) {
      const month = this.months[monthIndex]
      if (!month) return
      this.selectionMenu.visible = false
      this.detailModal.visible = true
      this.detailModal.loading = true
      this.detailModal.alarms = []
      this.detailModal.waylineId = serie.id
      this.detailModal.waylineName = serie.name
      this.detailModal.monthLabel = month.label
      try {
      // 先使用已加载的数据，避免接口筛选造成偏差
      const filtered = this.windowAlarms.filter(alarm => {
        const waylineId = this.resolveWaylineId(alarm)
        const idx = this.getMonthIndexFromString(alarm.created_at)
        return waylineId === serie.id && idx === monthIndex
      })
        if (filtered.length) {
          this.detailModal.alarms = filtered
        } else {
          const res = await alarmApi.getAlarms({
            wayline_id: serie.id,
            start_date: this.formatDateParam(month.start),
            end_date: this.formatDateParam(month.end),
            page_size: 500
          })
          this.detailModal.alarms = this.normalizeList(res)
        }
      } catch (err) {
        console.error('加载单月告警失败', err)
        this.detailModal.alarms = []
      } finally {
        this.detailModal.loading = false
      }
    },
    selectSeriesOption(option) {
      const monthIdx = this.selectionMenu.monthIndex
      this.selectionMenu.visible = false
      if (option) {
        this.openDetailFor(option, monthIdx)
      }
    },
    closeDetailModal() {
      this.detailModal.visible = false
    },
    formatDateTime(dateLike) {
      if (typeof dateLike === 'string') {
        const trimmed = dateLike.trim().replace('T', ' ')
        const noMs = trimmed.split('.')[0]
        return noMs || trimmed
      }
      const dt = this.parsePlainDate(dateLike)
      if (Number.isNaN(dt.getTime())) return '--'
      const pad = num => String(num).padStart(2, '0')
      return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())} ${pad(dt.getHours())}:${pad(dt.getMinutes())}`
    },
    formatDateParam(date) {
      const dt = this.parsePlainDate(date)
      const pad = num => String(num).padStart(2, '0')
      return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}`
    },
    getMonthIndexForDate(dt) {
      return this.months.findIndex(m => dt >= m.start && dt <= m.end)
    },
    getMonthIndexFromString(dateLike) {
      const dt = this.parsePlainDate(dateLike)
      if (!dt || Number.isNaN(dt.getTime())) return -1
      return this.getMonthIndexForDate(dt)
    },
    parsePlainDate(dateLike) {
      if (typeof dateLike === 'string') {
        const parts = this.parseDateParts(dateLike)
        if (parts) return this.buildDateFromParts(parts)
      }
      const dt = new Date(dateLike)
      return dt
    },
    parseDateParts(dateLike) {
      if (typeof dateLike !== 'string') return null
      const raw = dateLike.trim()
      const cleaned = raw.replace(/([+-]\d{2}:?\d{2}|Z)$/i, '')
      const match = cleaned.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d+))?)?/)
      if (!match) return null
      const [, y, m, d, h, mi, s, ms = '0'] = match
      return {
        year: Number(y),
        month: Number(m),
        day: Number(d),
        hour: Number(h),
        minute: Number(mi),
        second: Number(s || 0),
        milli: Number(String(ms).padEnd(3, '0').slice(0, 3))
      }
    },
    buildDateFromParts(parts) {
      return new Date(
        parts.year,
        parts.month - 1,
        parts.day,
        parts.hour,
        parts.minute,
        parts.second,
        parts.milli || 0
      )
    },
    showEmptyTip(event, text = '暂无告警信息') {
      const { clientX = 0, clientY = 0 } = event || {}
      this.emptyTip.visible = true
      this.emptyTip.text = text
      this.emptyTip.x = clientX + 12
      this.emptyTip.y = clientY + 12 + window.scrollY
      if (this.emptyTipTimer) {
        clearTimeout(this.emptyTipTimer)
      }
      this.emptyTipTimer = setTimeout(() => {
        this.emptyTip.visible = false
      }, 1600)
    },
    getPointColor(serie, monthIndex) {
      // 若该月有多个航线点且值相同，使用重叠色
      const targetValue = serie.data?.[monthIndex] || 0
      if (!targetValue) return this.overlapColor
      const overlaps = this.lineChart.series.filter(s => {
        const v = s.data?.[monthIndex] || 0
        return v === targetValue && v > 0
      })
      if (overlaps.length > 1) {
        return this.overlapColor
      }
      return serie.color
    }
  }
}
</script>

<style scoped>
.alarm-stats-page {
  max-width: 1640px;
  margin: 0 auto;
  padding: 24px 18px 48px;
  color: #e2e8f0;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
}

.title-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-kicker {
  color: #7dd3fc;
  letter-spacing: 2px;
  font-size: 13px;
  text-transform: uppercase;
}

.page-title {
  font-size: 32px;
  font-weight: 800;
  color: #e0f2fe;
  letter-spacing: 1px;
}

.page-subtitle {
  color: #94a3b8;
  font-size: 14px;
}

.header-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-chip {
  padding: 10px 14px;
  background: rgba(51, 65, 85, 0.6);
  border: 1px solid rgba(56, 189, 248, 0.35);
  border-radius: 12px;
  min-width: 160px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.meta-label {
  display: block;
  color: #94a3b8;
  font-size: 12px;
  margin-bottom: 4px;
}

.meta-value {
  color: #e0f2fe;
  font-weight: 700;
}

.top-grid {
  display: grid;
  grid-template-columns: 1.25fr 1.1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.card {
  position: relative;
  background: linear-gradient(145deg, rgba(15, 23, 50, 0.95) 0%, rgba(15, 23, 42, 0.7) 100%);
  border: 1px solid rgba(59, 130, 246, 0.25);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35), 0 0 60px rgba(56, 189, 248, 0.12);
  backdrop-filter: blur(6px);
}

.hero-card {
  background: linear-gradient(135deg, rgba(12, 74, 110, 0.85), rgba(30, 64, 175, 0.85));
  min-height: 220px;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 80% 20%, rgba(56, 189, 248, 0.35), transparent 45%),
    radial-gradient(circle at 20% 80%, rgba(94, 234, 212, 0.25), transparent 40%);
  filter: blur(10px);
  opacity: 0.8;
}

.hero-content {
  position: relative;
  padding: 22px 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  z-index: 1;
}

.hero-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.hero-label {
  color: #cbd5e1;
  font-size: 14px;
  letter-spacing: 1px;
}

.hero-number {
  font-size: 48px;
  font-weight: 800;
  color: #e0f2fe;
  text-shadow: 0 0 16px rgba(14, 165, 233, 0.7);
}

.hero-unit {
  font-size: 16px;
  color: #bae6fd;
  margin-left: 6px;
}

.hero-tag {
  padding: 8px 12px;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 999px;
  color: #e0f2fe;
  font-size: 12px;
}

.hero-summary {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.summary-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(15, 23, 42, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  color: #cbd5e1;
}

.chip-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
}

.chip-label {
  font-size: 13px;
}

.chip-value {
  font-size: 16px;
  font-weight: 700;
  color: #e2e8f0;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px 8px;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #e0f2fe;
}

.card-subtitle {
  color: #94a3b8;
  font-size: 13px;
}

.metrics-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  padding: 0 16px 16px;
}

.metric-item {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 14px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.metric-label {
  color: #94a3b8;
  font-size: 13px;
  margin-bottom: 6px;
  letter-spacing: 0.3px;
}

.metric-value {
  font-size: 20px;
  font-weight: 700;
  color: #e0f2fe;
  display: flex;
  align-items: center;
  gap: 8px;
}

.metric-trend {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.35);
}

.metric-trend.up {
  color: #22d3ee;
}

.metric-trend.down {
  color: #f97316;
}

.metric-trend.flat {
  color: #cbd5e1;
}

.donut-card {
  display: flex;
  flex-direction: column;
}

.donut-content {
  display: flex;
  gap: 12px;
  padding: 4px 14px 16px;
  align-items: center;
}

.donut-chart {
  width: 180px;
  height: 180px;
  flex-shrink: 0;
}

.donut-track {
  opacity: 0.7;
}

.donut-segment {
  transition: opacity 0.2s ease;
}

.donut-card:hover .donut-segment {
  opacity: 0.85;
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

.donut-legend {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 16px;
  width: 100%;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(15, 23, 42, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 10px 12px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
}

.legend-text {
  display: flex;
  justify-content: space-between;
  width: 100%;
  color: #cbd5e1;
  font-size: 13px;
}

.legend-name {
  font-weight: 600;
}

.legend-value {
  color: #e0f2fe;
  font-weight: 700;
}

.chart-card {
  margin-top: 12px;
  padding-bottom: 12px;
}

.series-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.series-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: rgba(15, 23, 42, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: #cbd5e1;
  font-size: 12px;
}

.line-chart-wrapper {
  padding: 6px 14px 16px;
}

.chart-area {
  display: flex;
  gap: 8px;
  align-items: stretch;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: #94a3b8;
  font-size: 12px;
  min-width: 48px;
  padding: 4px 6px 8px 0;
}

.y-axis span {
  text-align: right;
}

.line-chart {
  width: 100%;
  height: auto;
}

.grid-lines line {
  stroke-dasharray: 4 4;
}

.x-axis {
  display: flex;
  justify-content: space-between;
  color: #94a3b8;
  font-size: 12px;
  margin-top: 6px;
}

.x-axis span {
  text-align: center;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
  color: #cbd5e1;
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid rgba(56, 189, 248, 0.3);
  border-top-color: #38bdf8;
  border-radius: 999px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-state {
  margin-bottom: 16px;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.4);
  color: #fecaca;
}

.empty-state {
  padding: 18px;
  text-align: center;
  color: #94a3b8;
}

.chart-point {
  cursor: pointer;
  transition: r 0.15s ease, opacity 0.15s ease;
}

.chart-point:hover {
  r: 7;
  opacity: 0.95;
}

.selection-pop {
  position: absolute;
  z-index: 1500;
  min-width: 220px;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 12px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35);
  overflow: hidden;
}

.selection-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  color: #e0f2fe;
  font-size: 13px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.selection-header .close-btn {
  background: transparent;
  border: none;
  color: #cbd5e1;
  font-size: 18px;
  cursor: pointer;
}

.selection-options {
  display: flex;
  flex-direction: column;
  max-height: 260px;
  overflow: auto;
}

.selection-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: transparent;
  border: none;
  color: #e2e8f0;
  cursor: pointer;
  text-align: left;
}

.selection-item:hover {
  background: rgba(59, 130, 246, 0.08);
}

.selection-item .option-name {
  flex: 1;
  font-weight: 600;
}

.selection-item .option-value {
  color: #94a3b8;
  font-size: 12px;
}
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
}

.modal-premium {
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 16px;
  width: min(1080px, 90vw);
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.detail-modal {
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 16px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.modal-title {
  color: #e0f2fe;
  font-size: 18px;
  font-weight: 700;
}

.modal-close {
  background: transparent;
  border: none;
  color: #cbd5e1;
  font-size: 22px;
  cursor: pointer;
}

.modal-body {
  padding: 16px 18px;
  overflow: auto;
}

.modal-footer {
  padding: 12px 18px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.modal-btn {
  padding: 10px 16px;
  border-radius: 10px;
  border: 1px solid rgba(59, 130, 246, 0.4);
  background: rgba(59, 130, 246, 0.2);
  color: #e0f2fe;
  cursor: pointer;
}

.secondary-btn {
  background: rgba(148, 163, 184, 0.15);
  border-color: rgba(148, 163, 184, 0.4);
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 12px 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.4);
}

.detail-title {
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 6px;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: #94a3b8;
  font-size: 12px;
}

.detail-badges {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
}

.status-pill {
  padding: 6px 10px;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.25);
  border-radius: 10px;
  color: #cbd5e1;
  font-size: 12px;
}

@media (max-width: 1280px) {
  .top-grid {
    grid-template-columns: 1fr;
  }

  .donut-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .donut-legend {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 960px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .donut-legend {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .alarm-stats-page {
    padding: 16px 12px 32px;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .donut-legend {
    grid-template-columns: 1fr;
  }

  .detail-row {
    flex-direction: column;
  }

  .detail-badges {
    flex-direction: row;
  }
}
</style>
