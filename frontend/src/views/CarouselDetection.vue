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

    

    <div class="content-grid">
      <!-- 左侧：预扫描区域 -->
      <div class="scan-section">
        <div class="scan-compact-card">
          <div class="scan-compact-header">
            <h3 class="compact-title">MinIO 预扫描</h3>
            <div class="scan-actions-compact">
              <button
                class="compact-btn primary"
                @click="scanFolders"
                :disabled="scanLoading"
              >
                {{ scanLoading ? '扫描中...' : '扫描' }}
              </button>
              <button
                class="compact-btn success"
                @click="startSelectedTasks"
                :disabled="!selectedFolders.length || startLoading"
              >
                {{ startLoading ? '启动中...' : `开始 (${selectedFolders.length})` }}
              </button>
            </div>
          </div>
          <div class="scan-compact-body" v-if="scanError">
            <div class="error-state-compact">{{ scanError }}</div>
          </div>
          <div class="scan-compact-body" v-else-if="!candidateGroups.length">
            <div class="empty-state-compact">点击扫描按钮</div>
          </div>
          <div class="scan-compact-body" v-else>
            <div class="scan-list-compact" v-for="group in candidateGroups" :key="group.date">
              <div class="date-header-compact">{{ group.date }} ({{ group.tasks.length }})</div>
              <div
                class="task-item-compact"
                v-for="item in group.tasks"
                :key="item.full_path"
              >
                <label class="checkbox-compact">
                  <input
                    type="checkbox"
                    :value="item.folder_name"
                    :checked="isFolderSelected(item.folder_name)"
                    @change="toggleFolderSelection(item.folder_name)"
                    :disabled="item.db_status === 'scanning'"
                  />
                  <span class="checkmark"></span>
                </label>
                <div class="task-info-compact">
                  <div class="task-name-compact">{{ item.folder_name }}</div>
                  <div class="task-type-compact">{{ item.detect_type }}</div>
                </div>
                <span class="status-compact" :class="`status-${item.db_status}`">
                  {{ formatDbStatus(item.db_status) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：轮播展示 -->
      <div class="carousel-section">
      <div class="flow-card" @mouseenter="stopAuto" @mouseleave="startAuto">
        <template v-if="!currentInspectTaskId">
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
        </template>

        <template v-else>
          <div class="card-header">
            <div>
              <h3 class="card-title">实时检测回放</h3>
              <p class="card-subtitle">当前任务：{{ currentInspectTaskName || '未选择' }}</p>
            </div>
          </div>

          <div v-if="!currentInspectImage" class="flow-slide empty">
            <p>等待检测图片产生...</p>
          </div>
          <div v-else class="flow-slide">
            <div class="slide-top">
              <div class="slide-pill" :class="inspectStatusClass">
                第{{ inspectIndex + 1 }}张 · {{ inspectStatusText }}
              </div>
              <div class="slide-pill ghost">ID: {{ currentInspectImage.id || '—' }}</div>
            </div>
            <!-- 当前任务信息 -->
            <div class="task-info-banner">
              <div class="task-info-item">
                <span class="task-label">执行任务：</span>
                <span class="task-value">{{ currentParentTaskName || '未知' }}</span>
              </div>
              <div class="task-info-item">
                <span class="task-label">当前子任务：</span>
                <span class="task-value">{{ currentSubTaskName || '未知' }}</span>
              </div>
              <div class="task-info-item">
                <span class="task-label">检测类型：</span>
                <span class="task-value">{{ currentDetectionType || '未知' }}</span>
              </div>
            </div>
            <div class="slide-body">
              <div class="slide-image">
                <img v-if="getInspectImageUrl(currentInspectImage)" :src="getInspectImageUrl(currentInspectImage)" alt="巡检图片" />
                <div v-else class="image-placeholder">暂无图片</div>
              </div>
              <div class="slide-meta">
                <div class="meta-row">
                  <div class="status-tag-inline" :class="inspectStatusClass">
                    {{ inspectStatusText }}
                  </div>
                </div>
                <div class="meta-row">
                  <div class="meta-title">巡检图片</div>
                  <span class="meta-time">{{ formatTime(currentInspectImage.created_at) }}</span>
                </div>
                <p class="meta-desc" v-if="currentInspectImage.result_info">
                  {{ getDefectsDescription(currentInspectImage.result_info) }}
                </p>
                <p class="meta-desc">
                  任务：{{ currentInspectTaskName || currentInspectImage.inspect_task }}
                </p>
              </div>
            </div>

            <div class="controls">
              <button
                class="control-btn ghost"
                @click="inspectIndex = Math.max(inspectIndex - 1, 0)"
                :disabled="inspectIndex === 0"
              >
                上一张
              </button>
              <div class="dots">
                <span
                  v-for="(img, idx) in inspectImages"
                  :key="img.id || idx"
                  class="dot"
                  :class="{ active: idx === inspectIndex }"
                />
              </div>
              <button
                v-if="inspectPausedOnAnomaly"
                class="control-btn"
                @click="confirmContinueAfterAnomaly"
              >
                确认继续
              </button>
              <button
                v-else
                class="control-btn ghost"
                @click="inspectIndex = Math.min(inspectIndex + 1, Math.max(inspectImages.length - 1, 0))"
                :disabled="inspectIndex >= inspectImages.length - 1"
              >
                下一张
              </button>
            </div>
          </div>
        </template>
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
import inspectTaskApi from '../api/inspectTaskApi'
import { ElMessage } from 'element-plus'

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
      marqueeWrapperWidth: 0,
      // 预扫描与任务控制
      scanLoading: false,
      scanError: '',
      candidateGroups: [],
      selectedFolders: [],
      startLoading: false,
      // 实时检测播放
      currentInspectTaskId: null,
      currentInspectTaskName: '',
      currentParentTaskName: '',
      currentSubTaskName: '',
      currentDetectionType: '',
      inspectImages: [],
      inspectIndex: 0,
      inspectPollTimer: null,
      inspectAutoTimer: null,
      inspectPausedOnAnomaly: false,
      // 多任务顺序回放
      taskQueue: [], // 待回放的任务列表
      currentTaskIndex: 0, // 当前回放的任务索引
      allTasksCompleted: false, // 所有任务是否已完成
      scanRefreshTimer: null // 预扫描列表刷新定时器
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
    },
    currentInspectImage() {
      return this.inspectImages[this.inspectIndex] || null
    },
    inspectStatusText() {
      const img = this.currentInspectImage
      if (!img) return '等待检测开始'
      if (img.status01 === 0) return '正常'
      if (img.status01 === 1) return '发现异常'
      return '检测中...'
    },
    inspectStatusClass() {
      const img = this.currentInspectImage
      if (!img) return ''
      if (img.status01 === 0) return 'done'
      if (img.status01 === 1) return 'abnormal'
      return 'processing'
    }
  },
  mounted() {
    this.loadWaylines()
    this.refreshAll()
    this.scanFolders() // 初始加载时扫描一次
    // 启动静默刷新定时器（5秒一次，只更新数据不显示loading）
    this.scanRefreshTimer = setInterval(() => {
      this.scanFolders(true) // 传入 true 表示静默刷新
    }, 5000)
  },
  beforeUnmount() {
    this.stopAuto()
    this.stopInspectTimers()
    if (this.scanRefreshTimer) {
      clearInterval(this.scanRefreshTimer)
      this.scanRefreshTimer = null
    }
  },
  methods: {
    async scanFolders(silent = false) {
      console.log('🔍 [Debug] 开始扫描...', silent ? '(静默)' : '')
      if (this.scanLoading) {
        console.log('⚠️ [Debug] 扫描中，跳过重复请求')
        return
      }
      
      // 只有非静默模式才显示 loading 状态
      if (!silent) {
        this.scanLoading = true
      }
      this.scanError = ''
      
      try {
        console.log('📡 [Debug] 调用 scanCandidateFolders API...')
        const res = await inspectTaskApi.scanCandidateFolders()
        console.log('✅ [Debug] API 响应:', res)
        
        if (res && res.code === 200) {
          this.candidateGroups = res.data || []
          console.log('📋 [Debug] 更新 candidateGroups:', this.candidateGroups)
        } else {
          this.scanError = res?.msg || '预扫描失败'
          console.error('❌ [Debug] 扫描失败:', this.scanError)
        }
      } catch (err) {
        console.error('❌ [Debug] 扫描异常:', err)
        console.error('❌ [Debug] 错误详情:', err.response?.data || err.message)
        this.scanError = '预扫描失败，请稍后重试'
      } finally {
        if (!silent) {
          this.scanLoading = false
        }
        console.log('🏁 [Debug] 扫描结束，loading状态:', this.scanLoading)
      }
    },

    toggleFolderSelection(folderName) {
      const idx = this.selectedFolders.indexOf(folderName)
      if (idx >= 0) {
        this.selectedFolders.splice(idx, 1)
      } else {
        this.selectedFolders.push(folderName)
      }
    },

    isFolderSelected(folderName) {
      return this.selectedFolders.includes(folderName)
    },

    async startInspectPlaybackForFolder(folderName) {
      try {
        const params = { page_size: 20, search: folderName }
        const res = await inspectTaskApi.getInspectTasks(params)
        const list = this.normalizeList(res)
        const task = list.find(item => item.external_task_id === folderName) || list[0]
        if (!task) {
          ElMessage.error('未找到对应的巡检任务')
          return
        }
        console.log('🔍 选中的任务数据:', task)
        this.currentInspectTaskId = task.id
        this.currentInspectTaskName = task.external_task_id || `任务 ${task.id}`
        
        // 提取父任务名称（从 external_task_id 中提取日期部分，如 "20251211检测"）
        if (task.external_task_id) {
          const match = task.external_task_id.match(/^(\d{8})/)
          this.currentParentTaskName = match ? `${match[1]}检测` : task.external_task_id
        } else {
          this.currentParentTaskName = '未知父任务'
        }
        
        // 提取子任务名称（任务完整名称或从 external_task_id 获取）
        this.currentSubTaskName = task.name || task.external_task_id || '未知子任务'
        
        // 提取检测类型（优先从 category_details，然后 detect_type，最后从 external_task_id 推断）
        if (task.category_details && task.category_details.name) {
          this.currentDetectionType = task.category_details.name
        } else if (task.detect_type) {
          this.currentDetectionType = task.detect_type
        } else if (task.external_task_id) {
          // 从 external_task_id 中推断检测类型（如 "20251211轨道检测" -> "轨道检测"）
          const typeMatch = task.external_task_id.match(/\d{8}(.+)/)
          this.currentDetectionType = typeMatch ? typeMatch[1] : '未知类型'
        } else {
          this.currentDetectionType = '未知类型'
        }
        
        console.log('📋 任务信息:', {
          父任务: this.currentParentTaskName,
          子任务: this.currentSubTaskName,
          检测类型: this.currentDetectionType
        })
        
        this.inspectIndex = 0
        this.inspectImages = []
        this.inspectPausedOnAnomaly = false
        this.startInspectTimers()
        await this.pollInspectImages()
      } catch (err) {
        console.error('选择巡检任务进行回放失败:', err)
        ElMessage.error('选择巡检任务失败')
      }
    },

    async startSelectedTasks() {
      if (!this.selectedFolders.length || this.startLoading) return
      this.startLoading = true
      try {
        const res = await inspectTaskApi.startSelectedTasks(this.selectedFolders)
        if (res && res.code === 200) {
          ElMessage.success(res.msg || '已启动检测任务')
          // 保存任务队列用于顺序回放
          this.taskQueue = [...this.selectedFolders]
          this.currentTaskIndex = 0
          this.selectedFolders = []
          await this.refreshAll()
          await this.scanFolders()
          // 自动开始回放第一个任务
          if (this.taskQueue.length > 0) {
            setTimeout(async () => {
              await this.startNextTaskPlayback()
            }, 500)
          }
        } else {
          ElMessage.error(res?.msg || '启动检测失败')
        }
      } catch (err) {
        console.error('启动检测失败:', err)
        ElMessage.error('启动检测失败')
      } finally {
        this.startLoading = false
      }
    },

    async refreshAll() {
      this.loading = true
      this.error = ''
      try {
        await this.loadAlarms()
      } catch (err) {
        console.error('加载告警图片失败:', err)
        this.error = '加载告警图片失败，请稍后重试'
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
      const list = this.normalizeList(res).filter(item => {
        // 优先使用 image_signed_url，其次是 image_url
        const hasImage = item && (item.image_signed_url || item.image_url)
        if (hasImage && item.image_signed_url) {
          // 如果有签名 URL，使用它作为显示 URL
          item.image_url = item.image_signed_url
        }
        return hasImage
      })
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
      console.log('🔍 加载航线图片，参数:', params)
      try {
        const res = await waylineImageApi.getImages(params)
        console.log('✅ 航线图片API响应:', res)
        const list = this.normalizeList(res).filter(item => item && item.image_url)
        console.log('📸 过滤后的图片列表:', list)
        this.marqueeItems = list.map((item, idx) => ({
          ...item,
          marqueeKey: `${item.id || idx}-marquee-${idx}`
        }))
        console.log('🎬 最终marqueeItems:', this.marqueeItems)
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
      } catch (err) {
        console.error('❌ 加载航线图片失败:', err)
        this.marqueeError = '航线图片加载失败: ' + (err.message || '未知错误')
      }
    },
    normalizeList(res) {
      if (!res) return []
      if (Array.isArray(res)) return res
      if (res.results) return res.results
      if (res.data) return res.data
      return []
    },
    async pollInspectImages() {
      if (!this.currentInspectTaskId) return
      try {
        const res = await inspectTaskApi.getTaskImages(this.currentInspectTaskId)
        const list = this.normalizeList(res)
        console.log('📸 [Debug] 巡检图片数据:', list.length > 0 ? list[0] : '无数据')
        console.log('📸 [Debug] 完整图片列表字段:', list.map(img => Object.keys(img)))
        this.inspectImages = list
        if (this.inspectIndex >= this.inspectImages.length) {
          this.inspectIndex = Math.max(this.inspectImages.length - 1, 0)
        }
      } catch (err) {
        console.error('轮询巡检图片失败:', err)
      }
    },
    startInspectTimers() {
      this.stopInspectTimers()
      this.inspectPollTimer = setInterval(() => {
        this.pollInspectImages()
      }, 2000)
      this.inspectAutoTimer = setInterval(() => {
        this.inspectTick()
      }, 3000)
    },
    stopInspectTimers() {
      if (this.inspectPollTimer) {
        clearInterval(this.inspectPollTimer)
        this.inspectPollTimer = null
      }
      if (this.inspectAutoTimer) {
        clearInterval(this.inspectAutoTimer)
        this.inspectAutoTimer = null
      }
    },
    inspectTick() {
      if (!this.currentInspectTaskId || this.inspectPausedOnAnomaly) return
      if (!this.inspectImages.length) return
      const img = this.inspectImages[this.inspectIndex]
      if (!img) return
      const s = img.status01
      if (s === 1) {
        this.inspectPausedOnAnomaly = true
        return
      }
      if (s === 0) {
        if (this.inspectIndex < this.inspectImages.length - 1) {
          this.inspectIndex += 1
        } else {
          // 当前任务所有图片回放完毕，检查是否有下一个任务
          this.checkAndPlayNextTask()
        }
      }
      // status01 为空表示还在检测中，不自动跳转
    },
    confirmContinueAfterAnomaly() {
      this.inspectPausedOnAnomaly = false
      if (this.inspectIndex < this.inspectImages.length - 1) {
        this.inspectIndex += 1
      } else {
        // 当前任务图片回放完毕，检查下一个任务
        this.checkAndPlayNextTask()
      }
    },

    // 检查并播放下一个任务
    async checkAndPlayNextTask() {
      if (this.allTasksCompleted) {
        // 已经提示过，不重复提示
        return
      }
      if (this.currentTaskIndex < this.taskQueue.length - 1) {
        this.currentTaskIndex += 1
        console.log(`🔄 当前任务完成，切换到第 ${this.currentTaskIndex + 1} 个任务`)
        await this.startNextTaskPlayback()
      } else {
        console.log('✅ 所有任务回放完毕')
        this.allTasksCompleted = true
        ElMessage.success('所有任务回放完毕')
      }
    },

    // 开始回放下一个任务
    async startNextTaskPlayback() {
      if (this.currentTaskIndex >= this.taskQueue.length) {
        console.log('⚠️ 任务队列已空')
        return
      }
      const folderName = this.taskQueue[this.currentTaskIndex]
      console.log(`🎬 开始回放任务: ${folderName} (第 ${this.currentTaskIndex + 1}/${this.taskQueue.length} 个)`)
      this.allTasksCompleted = false // 重置完成标志
      await this.startInspectPlaybackForFolder(folderName)
    },
    handleWaylineChange() {
      this.activeIndex = 0
      this.stopAuto()
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
    },
    formatDbStatus(status) {
      const map = {
        new: '未创建任务',
        pending: '待检测',
        processing: '检测中',
        done: '已完成',
        failed: '失败',
        scanning: '扫描中'
      }
      return map[status] || status || '未知'
    },
    getInspectImageUrl(image) {
      if (!image) return null
      // 优先使用标注后的图片（result_signed_url），其次是原图（signed_url）
      return image.result_signed_url || image.signed_url || null
    },
    getDefectsDescription(resultInfo) {
      if (!resultInfo) return ''
      try {
        const info = typeof resultInfo === 'string' ? JSON.parse(resultInfo) : resultInfo
        const defects = info.defects_description || []
        return defects.length > 0 ? defects.join('；') : '检测正常'
      } catch (err) {
        console.error('解析result_info失败:', err)
        return ''
      }
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

.scan-card {
  margin-bottom: 18px;
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(8, 47, 73, 0.6));
  border: 1px solid rgba(14, 165, 233, 0.35);
  border-radius: 16px;
  padding: 12px 16px;
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.4);
}

.scan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.scan-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.scan-body {
  max-height: 260px;
  overflow-y: auto;
  padding-top: 4px;
}

.scan-group {
  margin-bottom: 8px;
}

.scan-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.scan-date {
  font-weight: 600;
  color: #e0f2fe;
}

.scan-count {
  font-size: 11px;
}

.scan-table {
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.8);
}

.scan-row {
  display: grid;
  grid-template-columns: auto minmax(0, 3fr) minmax(0, 1.6fr) auto;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
}

.scan-row:last-child {
  border-bottom: none;
}

.scan-checkbox {
  display: flex;
  align-items: center;
  justify-content: center;
}

.scan-checkbox input {
  display: none;
}

.scan-checkbox span {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid rgba(148, 163, 184, 0.8);
  background: transparent;
  position: relative;
}

.scan-checkbox input:checked + span {
  background: rgba(34, 197, 94, 0.2);
  border-color: rgba(34, 197, 94, 0.9);
}

.scan-checkbox input:checked + span::after {
  content: '';
  position: absolute;
  left: 3px;
  top: 1px;
  width: 8px;
  height: 12px;
  border-right: 2px solid #4ade80;
  border-bottom: 2px solid #4ade80;
  transform: rotate(40deg);
}

.scan-folder {
  overflow: hidden;
}

.folder-name {
  font-size: 13px;
  color: #e2e8f0;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.folder-path {
  font-size: 11px;
  color: #64748b;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.scan-type {
  font-size: 12px;
  color: #cbd5e1;
}

.scan-status {
  text-align: right;
}

.scan-play-btn {
  margin-top: 4px;
  padding: 4px 8px;
  font-size: 11px;
  border-radius: 999px;
  border: 1px solid rgba(59, 130, 246, 0.6);
  background: rgba(37, 99, 235, 0.15);
  color: #bfdbfe;
  cursor: pointer;
  transition: all 0.2s ease;
}

.scan-play-btn:hover {
  border-color: rgba(59, 130, 246, 0.9);
  color: #e0f2fe;
}

.status-pill {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 500;
}

.status-pill.db-new {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.5);
  color: #bfdbfe;
}

.status-pill.db-pending {
  background: rgba(234, 179, 8, 0.18);
  border: 1px solid rgba(234, 179, 8, 0.6);
  color: #facc15;
}

.status-pill.db-processing,
.status-pill.db-scanning {
  background: rgba(14, 165, 233, 0.18);
  border: 1px solid rgba(14, 165, 233, 0.6);
  color: #7dd3fc;
}

.status-pill.db-done {
  background: rgba(34, 197, 94, 0.18);
  border: 1px solid rgba(34, 197, 94, 0.6);
  color: #86efac;
}

.status-pill.db-failed {
  background: rgba(239, 68, 68, 0.18);
  border: 1px solid rgba(239, 68, 68, 0.6);
  color: #fecaca;
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
  grid-template-columns: 360px 1fr;
  gap: 24px;
  align-items: start;
  width: 100%;
}

/* 左侧预扫描区域 */
.scan-section {
  position: sticky;
  top: 24px;
}

.scan-compact-card {
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.95), rgba(12, 74, 110, 0.5));
  border: 1px solid rgba(14, 165, 233, 0.3);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 40px rgba(14, 165, 233, 0.1);
}

.scan-compact-header {
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(6, 182, 212, 0.1));
  border-bottom: 1px solid rgba(14, 165, 233, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.compact-title {
  font-size: 15px;
  font-weight: 700;
  color: #7dd3fc;
  margin: 0;
}

.scan-actions-compact {
  display: flex;
  gap: 8px;
}

.compact-btn {
  padding: 7px 14px;
  border-radius: 8px;
  border: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 60px;
  transition: transform 0.15s ease, opacity 0.15s ease;
}

.compact-btn:active:not(:disabled) {
  transform: scale(0.95);
  opacity: 0.8;
}

.compact-btn.primary {
  background: linear-gradient(135deg, #0ea5e9, #22d3ee);
  color: #fff;
  box-shadow: 0 2px 6px rgba(14, 165, 233, 0.25);
}

.compact-btn.success {
  background: linear-gradient(135deg, #10b981, #34d399);
  color: #fff;
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.25);
}

.compact-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.scan-compact-body {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
  padding: 12px;
}

.scan-compact-body::-webkit-scrollbar {
  width: 6px;
}

.scan-compact-body::-webkit-scrollbar-thumb {
  background: rgba(14, 165, 233, 0.3);
  border-radius: 3px;
}

.empty-state-compact {
  text-align: center;
  padding: 40px 20px;
  color: #64748b;
  font-size: 13px;
}

.error-state-compact {
  text-align: center;
  padding: 40px 20px;
  color: #f87171;
  font-size: 13px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  margin: 12px;
}

.scan-list-compact {
  margin-bottom: 12px;
}

.date-header-compact {
  font-size: 12px;
  font-weight: 600;
  color: #06b6d4;
  padding: 6px 0;
  border-bottom: 1px solid rgba(14, 165, 233, 0.2);
  margin-bottom: 8px;
}

.task-item-compact {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  margin-bottom: 6px;
  transition: all 0.3s ease;
}

.task-item-compact:hover {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(14, 165, 233, 0.3);
  transform: translateX(4px);
}

.checkbox-compact {
  position: relative;
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.checkbox-compact input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
}

.checkbox-compact .checkmark {
  position: absolute;
  top: 0;
  left: 0;
  width: 18px;
  height: 18px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(14, 165, 233, 0.4);
  border-radius: 4px;
  transition: all 0.3s ease;
}

.checkbox-compact input:checked ~ .checkmark {
  background: linear-gradient(135deg, #0ea5e9, #22d3ee);
  border-color: #0ea5e9;
}

.checkbox-compact input:checked ~ .checkmark::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 2px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.task-info-compact {
  flex: 1;
  min-width: 0;
}

.task-name-compact {
  font-size: 13px;
  font-weight: 600;
  color: #e0f2fe;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-type-compact {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.status-compact {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.status-compact.status-new {
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.status-compact.status-scanning {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.status-compact.status-done {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

/* 右侧轮播区域 */
.carousel-section {
  min-width: 0;
}

.flow-card {
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

.slide-pill.abnormal {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #fecaca;
}

.slide-pill.ghost {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
}

/* 任务信息横幅 */
.task-info-banner {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  background: rgba(14, 165, 233, 0.08);
  border: 1px solid rgba(14, 165, 233, 0.25);
  border-radius: 10px;
  padding: 10px 12px;
}

.task-info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.task-label {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 500;
}

.task-value {
  font-size: 13px;
  color: #e0f2fe;
  font-weight: 600;
}

.slide-body {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 1fr);
  gap: 24px;
  align-items: stretch;
  min-height: 600px;
  height: 100%;
}

.slide-image {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  min-height: 600px;
  height: 700px;
  background: radial-gradient(circle at 20% 20%, rgba(14, 165, 233, 0.25), transparent 45%), #0b1224;
}

.slide-image img {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 完整显示图片 */
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

.status-tag-inline {
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  display: inline-block;
}

.status-tag.processing,
.status-tag-inline.processing {
  background: rgba(14, 165, 233, 0.22);
  border: 1px solid rgba(14, 165, 233, 0.45);
  color: #e0f2fe;
}

.status-tag.done,
.status-tag-inline.done {
  background: rgba(34, 197, 94, 0.22);
  border: 1px solid rgba(34, 197, 94, 0.45);
  color: #ecfdf3;
}

.status-tag.abnormal,
.status-tag-inline.abnormal {
  background: rgba(239, 68, 68, 0.22);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #fee2e2;
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
