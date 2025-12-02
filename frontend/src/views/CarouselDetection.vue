<template>
  <div class="carousel-detection-page">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 7L12 2L21 7L12 12L3 7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M3 17L12 22L21 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M3 12L12 17L21 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
        <div class="header-text">
          <p class="eyebrow">推线检测流程展示</p>
          <h1 class="page-title">轮播检测</h1>
          <p class="page-subtitle">使用告警图片还原推线检测的处理状态，前两张保持“检测中”提示，自动轮播播放</p>
        </div>
      </div>
      <div class="header-stats">
        <div class="filter-group">
          <label class="filter-label" for="wayline-select">航线</label>
          <select
            id="wayline-select"
            class="wayline-select"
            v-model="selectedWayline"
            @change="handleWaylineChange"
            :disabled="loadingWaylines"
          >
            <option value="">全部航线</option>
            <option v-for="item in waylines" :key="item.optionValue" :value="item.optionValue">
              {{ item.name || ('航线 ' + item.optionValue) }}
            </option>
          </select>
        </div>
        <div class="stat-chip">
          <span class="stat-label">检测中</span>
          <span class="stat-value">{{ processingCount }}</span>
        </div>
        <div class="stat-chip">
          <span class="stat-label">已识别</span>
          <span class="stat-value">{{ recognizedCount }}</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在拉取带图片的告警...</p>
    </div>
    <div v-else-if="error" class="error-state">{{ error }}</div>
    <div v-else class="content-grid">
      <div class="flow-card" @mouseenter="stopAuto" @mouseleave="startAuto">
        <div class="card-header">
          <div>
            <h3 class="card-title">推线检测流程</h3>
            <p class="card-subtitle">按时间顺序轮播，第一、第二张保留检测中提示</p>
          </div>
          <div class="legend">
            <span class="legend-dot processing"></span>
            <span>检测中</span>
            <span class="legend-dot done"></span>
            <span>已识别</span>
          </div>
        </div>

        <transition name="fade" mode="out-in">
          <div v-if="currentSlide" :key="currentSlide.key" class="flow-slide">
            <div class="slide-top">
              <div class="slide-pill" :class="currentSlide.state">
                第{{ activeIndex + 1 }}张 · {{ currentSlide.stateText }}
              </div>
              <div class="slide-pill ghost">ID: {{ currentSlide.id || '—' }}</div>
            </div>
            <div class="slide-body">
              <div class="slide-image">
                <img v-if="currentSlide.image_url" :src="currentSlide.image_url" alt="告警图片" />
                <div v-else class="image-placeholder">暂无图片</div>
                <div class="status-tag" :class="currentSlide.state">
                  {{ currentSlide.stateText }}
                </div>
                <div class="status-hint">{{ currentSlide.hint }}</div>
              </div>
              <div class="slide-meta">
                <div class="meta-row">
                  <div class="meta-title">{{ currentSlide.content || '推线检测图片' }}</div>
                  <span class="meta-time">{{ formatTime(currentSlide.created_at) }}</span>
                </div>
                <p class="meta-desc">
                  航线：{{ currentSlide.wayline?.name || currentSlide.wayline_details?.name || '未记录' }} ·
                  坐标({{ currentSlide.latitude || '—' }}, {{ currentSlide.longitude || '—' }})
                </p>
              </div>
            </div>
          </div>
          <div v-else key="empty" class="flow-slide empty">
            <p>暂无带图片的告警记录</p>
          </div>
        </transition>

        <div v-if="flowSlides.length > 1" class="controls">
          <button class="control-btn ghost" @click="prevSlide">上一张</button>
          <div class="dots">
            <button
              v-for="(slide, idx) in flowSlides"
              :key="slide.key"
              class="dot"
              :class="{ active: idx === activeIndex }"
              @click="goTo(idx)"
            />
          </div>
          <button class="control-btn ghost" @click="nextSlide">下一张</button>
        </div>
      </div>

      <div class="marquee-card">
        <div class="card-header">
          <div>
            <h3 class="card-title">识别照片轮视</h3>
            <p class="card-subtitle">滚动展示拍摄图片</p>
          </div>
          <div class="light-badge">倒序</div>
        </div>
        <div v-if="marqueeError" class="error-state small">{{ marqueeError }}</div>
        <div v-else-if="!marqueeItems.length" class="empty-state small">暂无识别图片</div>
        <div v-else class="marquee-wrapper" ref="marqueeWrapper">
          <div class="marquee-track" :style="marqueeStyle" ref="marqueeTrack" @transitionend="handleMarqueeTransitionEnd">
            <div
              v-for="item in displayMarqueeItems"
              :key="item.marqueeKey"
              class="marquee-item"
              :class="{ active: isActiveMarquee(item) }"
              @click="handleMarqueeClick(item)"
            >
              <div class="marquee-image">
                <img v-if="item.image_url" :src="item.image_url" alt="识别图片" />
                <div v-else class="image-placeholder small">无图</div>
              </div>
              <div class="marquee-meta">
                <span class="meta-id">#{{ item.id || '—' }}</span>
                <span class="meta-time">{{ formatTime(item.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="previewItem" class="modal-overlay" @click.self="closePreview">
      <div class="modal-premium detail-modal">
        <div class="modal-header">
          <h3 class="modal-title">图片预览</h3>
          <button class="modal-close" @click="closePreview">×</button>
        </div>
        <div class="modal-body preview-body">
          <div class="preview-image">
            <img :src="previewItem.image_url" alt="航线图片预览" />
          </div>
          <div class="preview-meta">
            <div class="meta-row"><strong>ID：</strong> {{ previewItem.id || '—' }}</div>
            <div class="meta-row"><strong>航线：</strong> {{ previewItem.wayline_details?.name || previewItem.wayline?.name || '—' }}</div>
            <div class="meta-row"><strong>时间：</strong> {{ formatTime(previewItem.created_at) }}</div>
            <div class="meta-row" v-if="previewItem.title"><strong>标题：</strong> {{ previewItem.title }}</div>
            <div class="meta-row" v-if="previewItem.description"><strong>描述：</strong> {{ previewItem.description }}</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn secondary-btn" @click="closePreview">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import alarmApi from '../api/alarmApi'
import waylineApi from '../api/waylineApi'
import waylineImageApi from '../api/waylineImageApi'

export default {
  name: 'CarouselDetection',
  data() {
    return {
      loading: true,
      error: '',
      loadingWaylines: false,
      waylines: [],
      selectedWayline: '',
      flowSlides: [],
      marqueeItems: [],
      marqueeError: '',
      previewItem: null,
      activeIndex: 0,
      autoTimer: null,
      carouselInterval: 4500,
      marqueeIndex: 0,
      marqueeTimer: null,
      marqueeInterval: 3200,
      marqueeStep: 192,
      marqueeBaseOffset: 0,
      marqueeTransition: true,
      marqueeWrapperWidth: 0
    }
  },
  computed: {
    currentSlide() {
      return this.flowSlides[this.activeIndex] || null
    },
    processingCount() {
      return this.flowSlides.filter(item => item.state === 'processing').length
    },
    recognizedCount() {
      return this.flowSlides.filter(item => item.state === 'done').length
    },
    marqueeStyle() {
      const offset = this.marqueeIndex * this.marqueeStep
      return {
        transform: `translateX(${this.marqueeBaseOffset - offset}px)`,
        transition: this.marqueeTransition ? 'transform 0.6s ease' : 'none'
      }
    },
    displayMarqueeItems() {
      const items = this.marqueeItems
      if (!items.length) return []
      if (items.length === 1) return items
      const first = items[0]
      const last = items[items.length - 1]
      return [last, ...items, first]
    }
  },
  mounted() {
    this.loadWaylines()
    this.refreshAll()
  },
  beforeUnmount() {
    this.stopAuto()
    this.stopMarquee()
  },
  methods: {
    async refreshAll() {
      this.loading = true
      this.error = ''
      this.marqueeError = ''
        try {
          let alarmOk = true
          try {
            await this.loadAlarms()
          } catch (err) {
            alarmOk = false
            console.error('加载告警图片失败:', err)
            this.error = '加载告警图片失败，请稍后重试'
          }

          try {
          await this.loadWaylineImages()
          this.marqueeIndex = this.marqueeItems.length
          this.stopMarquee()
          this.startMarquee()
        } catch (err) {
            console.error('加载航线图片失败:', err)
            this.marqueeError = '航线图片加载失败，请稍后重试'
          }

        if (!alarmOk) return
      } finally {
        this.loading = false
      }
    },
    async loadWaylines() {
      this.loadingWaylines = true
      try {
        const res = await waylineApi.getWaylines({ page_size: 200 })
        const list = this.normalizeList(res)
        this.waylines = list
          .map(item => {
            const optionValue = item.wayline_id ?? item.id
            if (optionValue === undefined || optionValue === null) return null
            return {
              ...item,
              optionValue
            }
          })
          .filter(Boolean)
      } catch (err) {
        console.warn('加载航线列表失败，使用空列表', err)
        this.waylines = []
      } finally {
        this.loadingWaylines = false
      }
    },
    async loadAlarms() {
      const params = { page_size: 50, ordering: '-created_at' }
      if (this.selectedWayline) {
        params.wayline_id = this.selectedWayline
      }
      const res = await alarmApi.getAlarms(params)
      const list = this.normalizeList(res).filter(item => item && item.image_url)
      const sorted = list.sort((a, b) => {
        const aTime = new Date(a.created_at || 0).getTime()
        const bTime = new Date(b.created_at || 0).getTime()
        return bTime - aTime
      })
      this.flowSlides = this.buildSlides(sorted.slice(0, 10))
      this.activeIndex = 0
      this.stopAuto()
      this.startAuto()
    },
    async loadWaylineImages() {
      const params = { page_size: 200, ordering: '-created_at' }
      if (this.selectedWayline) {
        params.wayline_id = this.selectedWayline
      }
      const res = await waylineImageApi.getImages(params)
      const list = this.normalizeList(res).filter(item => item && item.image_url)
      this.marqueeItems = list.map((item, idx) => ({
        ...item,
        marqueeKey: `${item.id || idx}-marquee-${idx}`
      }))
      this.$nextTick(() => {
        this.updateMarqueeStep()
        const len = this.marqueeItems.length
        if (len > 1) {
          this.marqueeTransition = false
          this.marqueeIndex = 1
          requestAnimationFrame(() => {
            this.marqueeTransition = true
          })
        } else {
          this.marqueeTransition = true
          this.marqueeIndex = 0
        }
      })
    },
    normalizeList(res) {
      if (!res) return []
      if (Array.isArray(res)) return res
      if (res.results) return res.results
      if (res.data) return res.data
      return []
    },
    handleWaylineChange() {
      this.activeIndex = 0
      this.stopAuto()
      this.stopMarquee()
      this.refreshAll()
    },
    handleMarqueeClick(item) {
      this.previewItem = item
    },
    closePreview() {
      this.previewItem = null
    },
    buildSlides(list) {
      const hints = [
        '模型正在推线检测中',
        '二次校验中，等待结果确认'
      ]
      return list.map((item, idx) => {
        const processing = idx < 2
        return {
          ...item,
          key: `${item.id || idx}-${idx}`,
          state: processing ? 'processing' : 'done',
          stateText: processing ? '检测中' : '识别完成',
          hint: processing ? (hints[idx] || '检测中...') : '识别结果已入库，倒序展示'
        }
      })
    },
    startAuto() {
      if (this.autoTimer || this.flowSlides.length <= 1) return
      this.autoTimer = setInterval(() => {
        this.nextSlide()
      }, this.carouselInterval)
    },
    stopAuto() {
      if (this.autoTimer) {
        clearInterval(this.autoTimer)
        this.autoTimer = null
      }
    },
    startMarquee() {
      if (this.marqueeTimer || this.marqueeItems.length <= 1) return
      if (this.marqueeIndex < 1) {
        this.marqueeIndex = 1
      }
      this.marqueeTimer = setInterval(() => {
        const len = this.marqueeItems.length
        if (!len) return
        this.marqueeTransition = true
        this.marqueeIndex += 1
      }, this.marqueeInterval)
    },
    stopMarquee() {
      if (this.marqueeTimer) {
        clearInterval(this.marqueeTimer)
        this.marqueeTimer = null
      }
    },
    updateMarqueeStep() {
      const track = this.$refs.marqueeTrack
      const wrapper = this.$refs.marqueeWrapper
      if (!track || !track.firstElementChild) return
      const cardWidth = track.firstElementChild.offsetWidth
      const gap = 12
      this.marqueeStep = cardWidth + gap
      if (wrapper) {
        this.marqueeWrapperWidth = wrapper.offsetWidth
        this.marqueeBaseOffset = (wrapper.offsetWidth - cardWidth) / 2
      }
    },
    isActiveMarquee(item) {
      if (!item) return false
      const len = this.marqueeItems.length
      if (!len) return false
      // 因为display数组为 [last, ...items, first]，真实索引需要减1
      const realIndex = ((this.marqueeIndex - 1) % len + len) % len
      const currentKey = this.marqueeItems[realIndex]?.marqueeKey
      return currentKey === item.marqueeKey
    },
    handleMarqueeTransitionEnd() {
      const len = this.marqueeItems.length
      if (len <= 1) return
      const displayLen = len + 2
      if (this.marqueeIndex >= displayLen - 1) {
        this.marqueeTransition = false
        this.marqueeIndex = 1
        this.$nextTick(() => {
          requestAnimationFrame(() => {
            requestAnimationFrame(() => {
              this.marqueeTransition = true
            })
          })
        })
      } else if (this.marqueeIndex <= 0) {
        this.marqueeTransition = false
        this.marqueeIndex = displayLen - 2
        this.$nextTick(() => {
          requestAnimationFrame(() => {
            requestAnimationFrame(() => {
              this.marqueeTransition = true
            })
          })
        })
      }
    },
    nextSlide() {
      if (!this.flowSlides.length) return
      this.activeIndex = (this.activeIndex + 1) % this.flowSlides.length
    },
    prevSlide() {
      if (!this.flowSlides.length) return
      this.activeIndex = (this.activeIndex - 1 + this.flowSlides.length) % this.flowSlides.length
    },
    goTo(idx) {
      if (idx < 0 || idx >= this.flowSlides.length) return
      this.activeIndex = idx
    },
    formatTime(dateLike) {
      if (!dateLike) return '--'
      const dt = new Date(dateLike)
      if (Number.isNaN(dt.getTime())) return '--'
      const pad = num => String(num).padStart(2, '0')
      return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())} ${pad(dt.getHours())}:${pad(dt.getMinutes())}`
    }
  }
}
</script>

<style scoped>
.carousel-detection-page {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px 18px 48px;
  color: #e2e8f0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
  margin-bottom: 18px;
}

.header-left {
  display: flex;
  gap: 14px;
  align-items: center;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, #0ea5e9 0%, #22d3ee 100%);
  color: #fff;
  display: grid;
  place-items: center;
  box-shadow: 0 10px 30px rgba(14, 165, 233, 0.25);
}

.header-icon svg {
  width: 28px;
  height: 28px;
}

.header-text h1 {
  margin: 2px 0;
}

.eyebrow {
  color: #7dd3fc;
  letter-spacing: 1px;
  font-size: 12px;
  text-transform: uppercase;
}

.page-title {
  font-size: 30px;
  font-weight: 800;
  color: #e0f2fe;
}

.page-subtitle {
  color: #94a3b8;
  font-size: 14px;
}

.header-stats {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(14, 165, 233, 0.25);
  border-radius: 12px;
  padding: 8px 10px;
  min-width: 180px;
}

.filter-label {
  color: #94a3b8;
  font-size: 12px;
}

.wayline-select {
  width: 100%;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid rgba(14, 165, 233, 0.35);
  background: rgba(12, 18, 36, 0.8);
  color: #e2e8f0;
  outline: none;
}

.stat-chip {
  padding: 10px 14px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(14, 165, 233, 0.35);
  border-radius: 12px;
  min-width: 120px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}

.stat-label {
  display: block;
  color: #94a3b8;
  font-size: 12px;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 800;
  color: #e0f2fe;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(340px, 0.85fr);
  gap: 16px;
  align-items: stretch;
  width: 100%;
}

.flow-card,
.marquee-card {
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(12, 74, 110, 0.4));
  border: 1px solid rgba(14, 165, 233, 0.25);
  border-radius: 16px;
  padding: 16px 16px 12px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35), 0 0 50px rgba(14, 165, 233, 0.12);
  min-height: 440px;
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 12px;
}

.card-title {
  font-size: 18px;
  font-weight: 800;
  color: #e0f2fe;
  margin: 0;
}

.card-subtitle {
  color: #94a3b8;
  font-size: 13px;
  margin: 2px 0 0;
}

.legend {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #cbd5e1;
  font-size: 12px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.marquee-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.marquee-btn {
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid rgba(14, 165, 233, 0.35);
  background: rgba(14, 165, 233, 0.08);
  color: #e0f2fe;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.marquee-btn:hover {
  border-color: rgba(14, 165, 233, 0.6);
  color: #7dd3fc;
}

.legend-dot.processing {
  background: linear-gradient(135deg, #0ea5e9, #22d3ee);
}

.legend-dot.done {
  background: linear-gradient(135deg, #22c55e, #4ade80);
}

.flow-slide {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 14px;
  min-height: 360px;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.flow-slide.empty {
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}

.slide-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.slide-pill {
  padding: 8px 12px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 13px;
}

.slide-pill.processing {
  background: rgba(14, 165, 233, 0.12);
  border: 1px solid rgba(14, 165, 233, 0.4);
  color: #7dd3fc;
}

.slide-pill.done {
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.4);
  color: #86efac;
}

.slide-pill.ghost {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
}

.slide-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 0.9fr);
  gap: 12px;
  align-items: stretch;
  min-height: 260px;
  height: 100%;
}

.slide-image {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  min-height: 240px;
  height: 260px;
  background: radial-gradient(circle at 20% 20%, rgba(14, 165, 233, 0.25), transparent 45%), #0b1224;
}

.slide-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: #94a3b8;
  font-size: 14px;
  background: repeating-linear-gradient(45deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.05) 10px, rgba(255, 255, 255, 0.02) 10px, rgba(255, 255, 255, 0.02) 20px);
}

.status-tag {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 8px 12px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 13px;
  backdrop-filter: blur(6px);
}

.status-tag.processing {
  background: rgba(14, 165, 233, 0.22);
  border: 1px solid rgba(14, 165, 233, 0.45);
  color: #e0f2fe;
}

.status-tag.done {
  background: rgba(34, 197, 94, 0.22);
  border: 1px solid rgba(34, 197, 94, 0.45);
  color: #ecfdf3;
}

.status-hint {
  position: absolute;
  bottom: 12px;
  left: 12px;
  right: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(12, 74, 110, 0.7));
  border: 1px solid rgba(14, 165, 233, 0.3);
  font-size: 13px;
  color: #e2e8f0;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.slide-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 10px;
}

.meta-title {
  font-weight: 700;
  color: #e2e8f0;
  font-size: 16px;
}

.meta-time {
  color: #94a3b8;
  font-size: 12px;
}

.meta-desc {
  color: #cbd5e1;
  font-size: 13px;
}

.controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.control-btn {
  padding: 8px 14px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: #e2e8f0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.control-btn:hover {
  border-color: rgba(14, 165, 233, 0.5);
  color: #7dd3fc;
}

.control-btn.ghost {
  background: rgba(14, 165, 233, 0.08);
}

.dots {
  display: flex;
  gap: 6px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.14);
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease;
}

.dot.active {
  background: linear-gradient(135deg, #0ea5e9, #22d3ee);
  transform: scale(1.05);
}

.marquee-wrapper {
  overflow: hidden;
  position: relative;
  border-radius: 12px;
  border: 1px solid rgba(14, 165, 233, 0.25);
  background: rgba(12, 18, 36, 0.7);
  padding: 12px 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.marquee-track {
  display: flex;
  gap: 12px;
  flex-wrap: nowrap;
  width: max-content;
  transition: transform 0.6s ease;
}

.marquee-item {
  width: 180px;
  flex: 0 0 auto;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.marquee-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
}

.marquee-item.active {
  transform: scale(1.08);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.4);
  border-color: rgba(14, 165, 233, 0.5);
}

.marquee-image {
  height: 110px;
  background: #0b1224;
}

.marquee-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.image-placeholder.small {
  font-size: 12px;
}

.marquee-meta {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-id {
  font-weight: 700;
  color: #e2e8f0;
}

.meta-time {
  color: #94a3b8;
  font-size: 12px;
}

.light-badge {
  padding: 8px 10px;
  background: rgba(14, 165, 233, 0.12);
  border: 1px solid rgba(14, 165, 233, 0.35);
  border-radius: 10px;
  color: #7dd3fc;
  font-weight: 700;
}

.loading-state,
.error-state,
.empty-state {
  padding: 20px 16px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  text-align: center;
  color: #cbd5e1;
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 3px solid rgba(14, 165, 233, 0.3);
  border-top-color: #0ea5e9;
  margin: 0 auto 10px;
  animation: spin 1s linear infinite;
}

.empty-state.small {
  margin: 8px 0 0;
}

.error-state {
  color: #fecaca;
  border-color: rgba(248, 113, 113, 0.4);
  background: rgba(248, 113, 113, 0.08);
}

.error-state.small {
  margin: 8px 0 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.modal-premium {
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 16px;
  width: min(560px, 92vw);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.45);
  overflow: hidden;
}

.detail-modal {
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.modal-title {
  color: #e0f2fe;
  font-size: 16px;
  font-weight: 700;
  margin: 0;
}

.modal-close {
  background: transparent;
  border: none;
  color: #cbd5e1;
  font-size: 22px;
  cursor: pointer;
}

.modal-body {
  padding: 14px 16px;
}

.modal-footer {
  padding: 10px 16px 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.modal-btn {
  padding: 8px 14px;
  border-radius: 10px;
  border: 1px solid rgba(59, 130, 246, 0.35);
  background: rgba(59, 130, 246, 0.15);
  color: #e0f2fe;
  cursor: pointer;
}

.secondary-btn {
  background: rgba(148, 163, 184, 0.15);
  border-color: rgba(148, 163, 184, 0.4);
}

.preview-body {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.preview-image {
  background: #0b1224;
  border: 1px solid rgba(14, 165, 233, 0.25);
  border-radius: 12px;
  overflow: hidden;
  max-height: 320px;
}

.preview-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.preview-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #cbd5e1;
  font-size: 14px;
}

.preview-meta .meta-row strong {
  color: #e2e8f0;
}

@keyframes marquee {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-50%);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1220px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .flow-card,
  .marquee-card {
    min-height: auto;
  }
}

@media (max-width: 820px) {
  .slide-body {
    grid-template-columns: 1fr;
  }

  .controls {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
