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
      <!-- 左侧：三级树形结构（检测类型 → 航线 → 历史任务） -->
      <div class="scan-section">
        <div class="scan-compact-card">
          <div class="scan-compact-header">
            <h3 class="compact-title">检测类型管理</h3>
            <div class="scan-actions-compact">
              <button
                class="compact-btn primary"
                @click="loadHistoryTree"
                :disabled="treeLoading"
              >
                {{ treeLoading ? '加载中...' : '刷新' }}
              </button>
            </div>
          </div>
          <div class="scan-compact-body" v-if="treeError">
            <div class="error-state-compact">{{ treeError }}</div>
          </div>
          <div class="scan-compact-body" v-else-if="!detectionTree.length">
            <div class="empty-state-compact">点击刷新按钮加载历史任务</div>
          </div>
          <div class="scan-compact-body" v-else>
            <!-- 第一级：检测类型 -->
            <div
              class="location-group"
              v-for="categoryGroup in detectionTree"
              :key="categoryGroup.code"
            >
              <div
                class="location-header"
                @click="toggleCategory(categoryGroup.code)"
              >
                <span class="location-icon">{{ categoryGroup.icon }}</span>
                <span class="location-name">{{ categoryGroup.name }}</span>
                <span class="location-count">({{ categoryGroup.taskCount }})</span>
                <span class="toggle-icon">{{ isCategoryExpanded(categoryGroup.code) ? '▼' : '▶' }}</span>
              </div>

              <!-- 第二级：航线 -->
              <div v-show="isCategoryExpanded(categoryGroup.code)">
                <div
                  class="type-group"
                  v-for="waylineGroup in categoryGroup.waylines"
                  :key="waylineGroup.id"
                >
                  <div
                    class="type-header"
                    @click="toggleWaylineInTree(categoryGroup.code, waylineGroup.id)"
                  >
                    <span class="type-icon">🛤️</span>
                    <span class="type-name">{{ waylineGroup.name }}</span>
                    <span class="type-count" :class="{ 'highlight-count': waylineGroup.tasks.length > 0 }">({{ waylineGroup.tasks.length }})</span>
                    <span class="toggle-icon">{{ isWaylineExpanded(categoryGroup.code, waylineGroup.id) ? '▼' : '▶' }}</span>
                  </div>

                  <!-- 第三级：历史任务 -->
                  <div v-show="isWaylineExpanded(categoryGroup.code, waylineGroup.id)">
                    <div
                      class="task-item-compact clickable"
                      v-for="task in waylineGroup.tasks"
                      :key="task.id"
                      @click="startInspectPlaybackForFolder(task, true)"
                      :class="{ active: currentInspectTaskId === task.id }"
                    >
                      <div class="task-info-compact">
                        <div class="task-name-compact">{{ task.dji_task_name || task.external_task_id }}</div>
                        <div class="task-meta-compact">
                          <span class="task-time">{{ formatTaskDate(task.created_at) }}</span>
                          <span class="task-divider">|</span>
                          <span class="device-sn" v-if="task.device_sn">🚁 {{ task.device_sn }}</span>
                          <span class="task-divider" v-if="task.device_sn">|</span>
                          <span class="alarm-count">🚨 {{ task.alarm_count }} 个异常</span>
                        </div>
                      </div>
                      
                      <!-- 轮播异常按钮 -->
                      <button 
                        v-if="task.alarm_count > 0"
                        class="action-btn-compact"
                        @click.stop="playTaskAlarms(task)"
                        title="轮播异常"
                      >
                        <span class="btn-icon">▶</span>
                        <span>轮播异常</span>
                      </button>

                      <span class="status-compact" :class="`status-${task.detect_status}`">
                        {{ formatDbStatus(task.detect_status) }}
                      </span>
                    </div>

                    <!-- 空状态提示 -->
                    <div v-if="!waylineGroup.tasks.length" class="empty-tasks-hint">
                      暂无历史任务
                    </div>
                  </div>
                </div>
                
                <!-- 无航线提示 -->
                <div v-if="!categoryGroup.waylines.length" class="empty-tasks-hint">
                  该检测类型暂无航线
                </div>
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
            <div class="progress-count">
              {{ activeIndex + 1 }}/{{ flowSlides.length }}
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
            <div class="legend" v-if="currentInspectTaskId">
              <span class="legend-dot processing"></span>
              <span>检测中</span>
              <span class="legend-dot done"></span>
              <span>已识别</span>
              <span class="legend-dot error"></span>
              <span>异常发现</span>
            </div>
          </div>

          <div v-if="!currentInspectImage && !inspectImages.length" class="flow-slide empty">
            <p>等待检测图片产生...</p>
          </div>
          <div v-else-if="currentInspectImage" class="flow-slide">
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
              <div class="progress-count">
                {{ inspectIndex + 1 }}/{{ inspectImages.length }}
              </div>
              <button
                class="control-btn ghost"
                @click="jumpToLatestInspectImage"
                :disabled="!inspectImages.length || inspectIndex >= inspectImages.length - 1"
              >
                跳到最新
              </button>
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
import { ElMessage, ElNotification } from 'element-plus'

export default {
  name: 'CarouselDetection',
  data() {
    return {
      loading: true,
      error: '',
      loadingWaylines: false,
      waylines: [],
      allWaylines: [],
      locationTree: [],
      expandedLocations: new Set(),
      expandedTypes: new Set(),
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
      scanRefreshTimer: null, // 预扫描列表刷新定时器
      isDetectMode: false, // 是否为检测模式（true=检测，false=回放）
      // 新增：三级树结构
      detectionTree: [], // 检测类型树
      treeLoading: false,
      treeError: '',
      expandedCategories: new Set(),
      expandedWaylines: new Set(),
      selectedHistoryTask: null,
      latestManualTaskId: null,
      taskProgressMap: {} // 记录每个任务的播放进度
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
    this.loadHistoryTree() // 初始加载历史任务树
    // 启动刷新定时器（10秒一次）
    this.scanRefreshTimer = setInterval(() => {
      this.loadHistoryTree(true) // 静默刷新
    }, 10000)
    
    // 检查是否有回放参数
    const playbackTaskId = this.$route.query.playback
    if (playbackTaskId) {
      console.log('🎬 检测到回放参数:', playbackTaskId)
      setTimeout(() => {
        this.startInspectPlaybackForFolder(playbackTaskId, true)
      }, 500)
    }
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
    async loadPendingTasks(silent = false) {
      console.log('🔍 [Debug] 开始加载待启动任务...', silent ? '(静默)' : '')
      if (this.scanLoading) {
        console.log('⚠️ [Debug] 加载中，跳过重复请求')
        return
      }

      // 只有非静默模式才显示 loading 状态
      if (!silent) {
        this.scanLoading = true
      }
      this.scanError = ''

      try {
        console.log('📡 [Debug] 调用 getInspectTasks API 查询待启动任务...')
        const res = await inspectTaskApi.getInspectTasks({
          detect_status__in: 'pending,scanning',  // 包含 pending 和 scanning 状态
          parent_task__isnull: false,  // 只查询子任务
          page_size: 100,
          ordering: '-created_at'
        })
        console.log('✅ [Debug] API 响应:', res)

        const tasks = this.normalizeList(res)
        console.log('📋 [Debug] 待启动子任务列表:', tasks)

        // 将任务匹配到地点树形结构
        this.matchTasksToTree(tasks)

        // 保留原有的日期分组逻辑（用于兼容）
        const grouped = {}
        tasks.forEach(task => {
          const dateMatch = task.external_task_id?.match(/^(\d{8})/)
          const dateKey = dateMatch ? dateMatch[1] : '未知日期'
          if (!grouped[dateKey]) {
            grouped[dateKey] = {
              date: dateKey,
              tasks: []
            }
          }
          grouped[dateKey].tasks.push(task)
        })

        this.candidateGroups = Object.values(grouped)
        console.log('📊 [Debug] 分组后的待启动任务:', this.candidateGroups)
      } catch (err) {
        console.error('❌ [Debug] 加载待启动任务异常:', err)
        console.error('❌ [Debug] 错误详情:', err.response?.data || err.message)
        this.scanError = '加载待启动任务失败，请稍后重试'
      } finally {
        if (!silent) {
          this.scanLoading = false
        }
        console.log('🏁 [Debug] 加载结束，loading状态:', this.scanLoading)
      }
    },

    toggleFolderSelection(taskId) {
      const idx = this.selectedFolders.indexOf(taskId)
      if (idx >= 0) {
        this.selectedFolders.splice(idx, 1)
      } else {
        this.selectedFolders.push(taskId)
      }
    },

    isFolderSelected(taskId) {
      return this.selectedFolders.includes(taskId)
    },

    async startInspectPlaybackForFolder(taskOrId, isPlaybackMode = false) {
      // 保存当前任务进度
      if (this.currentInspectTaskId) {
        this.taskProgressMap[this.currentInspectTaskId] = this.inspectIndex
      }

      try {
        // 🔥 [Fix] 增强参数解析：如果是 JSON 字符串，先解析为对象
        if (typeof taskOrId === 'string' && (taskOrId.startsWith('{') || taskOrId.startsWith('%7B'))) {
           try {
              const decoded = decodeURIComponent(taskOrId)
              if (decoded.startsWith('{')) {
                 const parsed = JSON.parse(decoded)
                 if (parsed && (parsed.id || parsed.external_task_id)) {
                    taskOrId = parsed
                    console.log('🔄 [Auto-Fix] 成功将 JSON 字符串参数解析为对象')
                 }
              }
           } catch (e) {
              console.warn('解析 JSON 参数失败:', e)
           }
        }

        let task = null
        let folderName = ''

        // 1. 判断传入的是对象还是ID字符串
        if (typeof taskOrId === 'object' && taskOrId !== null) {
          task = taskOrId
          folderName = task.external_task_id
          console.log('🎯 [Direct] 直接使用传入的任务对象:', folderName)
        } else {
          folderName = taskOrId
          
          // 🔥 [Fix] 防止将 JSON 串或非法字符发给后端
          if (typeof folderName === 'string' && (folderName.includes('{') || folderName.includes('}'))) {
             console.error('❌ [Error] 参数疑似 JSON 但解析失败，拒绝发送搜索请求:', folderName)
             ElMessage.error('参数格式错误，无法启动任务')
             return
          }

          console.log('🔍 [Search] 通过ID查找任务:', folderName)
          const params = { page_size: 20, search: folderName }
          const res = await inspectTaskApi.getInspectTasks(params)
          const list = this.normalizeList(res)
          console.log(`🔍 [Search Result] 搜索 "${folderName}" 返回结果数: ${list.length}`)
          
          // 优先完全匹配
          task = list.find(item => item.external_task_id === folderName) || list[0]
          
          if (!task && list.length === 0) {
             console.warn(`⚠️ [Search Warning] 搜索 "${folderName}" 未返回任何结果！API Params:`, params)
          }
        }

        if (!task) {
          console.error(`❌ [Error] 无法找到任务: ${folderName}`)
          ElMessage.error(`未找到对应的巡检任务: ${folderName}`)
          return
        }
        console.log('🔍 选中的任务数据:', task)
        this.currentInspectTaskId = task.id
        this.currentInspectTaskName = task.external_task_id || `任务 ${task.id}`
        // 如果是从外部调用（回放模式），设置标记
        if (isPlaybackMode) {
          this.isDetectMode = false
          this.taskQueue = [folderName]
          this.currentTaskIndex = 0
        }
        
        // 提取父任务名称
        if (task.parent_task_details && task.parent_task_details.external_task_id) {
          this.currentParentTaskName = task.parent_task_details.external_task_id
        } else if (task.external_task_id) {
          // 备用方案：从 external_task_id 提取日期部分
          const match = task.external_task_id.match(/^(\d{8})/)
          this.currentParentTaskName = match ? `${match[1]}检测` : task.external_task_id
        } else {
          this.currentParentTaskName = '未知父任务'
        }
        
        // 提取子任务名称（当前任务的external_task_id）
        this.currentSubTaskName = task.external_task_id || '未知子任务'
        
        // 提取检测类型
        if (task.category_details && task.category_details.name) {
          this.currentDetectionType = task.category_details.name
        } else if (task.detect_category_name) {
          this.currentDetectionType = task.detect_category_name
        } else if (task.external_task_id) {
          // 从 external_task_id 中推断检测类型
          const typeMatch = task.external_task_id.match(/\d{8}(.+)/)
          this.currentDetectionType = typeMatch ? typeMatch[1] : '未知类型'
        } else {
          this.currentDetectionType = '未知类型'
        }
        
        console.log('📋 任务信息:', {
          父任务: this.currentParentTaskName,
          子任务: this.currentSubTaskName,
          检测类型: this.currentDetectionType,
          task数据: task
        })
        
        this.inspectIndex = 0
        this.inspectImages = []
        this.inspectPausedOnAnomaly = false
        this.startInspectTimers()
        await this.pollInspectImages()

        // 恢复任务进度
        if (this.taskProgressMap[this.currentInspectTaskId] !== undefined) {
          const savedIndex = this.taskProgressMap[this.currentInspectTaskId]
          if (this.inspectImages.length > 0) {
            this.inspectIndex = Math.min(savedIndex, this.inspectImages.length - 1)
          }
        }
      } catch (err) {
        console.error('选择巡检任务进行回放失败:', err)
        ElMessage.error('选择巡检任务失败')
      }
    },

    async startSelectedTasks() {
      if (!this.selectedFolders.length || this.startLoading) return
      
      console.log('🚀 [Debug] 准备启动选中的任务:', this.selectedFolders)
      this.startLoading = true
      
      try {
        // 批量调用 start 接口启动任务
        const updatePromises = this.selectedFolders.map(taskId => 
          inspectTaskApi.startTask(taskId)
        )
        
        await Promise.all(updatePromises)
        console.log('✅ [Debug] 已将选中任务状态改为 scanning')
        
        ElMessage.success(`已启动 ${this.selectedFolders.length} 个检测任务`)
        
        // 获取任务对象用于回放
        const tasks = []
        for (const taskId of this.selectedFolders) {
          const taskData = this.candidateGroups
            .flatMap(g => g.tasks)
            .find(t => t.id === taskId)
          if (taskData) {
            tasks.push(taskData)
          }
        }
        
        // 保存任务队列用于顺序回放 (存对象，避免后续搜索失败)
        this.taskQueue = tasks
        this.currentTaskIndex = 0
        this.selectedFolders = []
        this.isDetectMode = true // 标记为检测模式
        
        await this.refreshAll()
        await this.loadPendingTasks(true)  // 静默刷新待启动任务列表
        
        // 自动开始回放第一个任务
        if (this.taskQueue.length > 0) {
          setTimeout(async () => {
            await this.startNextTaskPlayback()
          }, 500)
        }
      } catch (err) {
        console.error('❌ [Debug] 启动检测失败:', err)
        ElMessage.error('启动检测失败: ' + (err.message || '未知错误'))
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
        // 后端已禁用分页，不需要传 page_size
        const res = await waylineApi.getWaylines({})
        const list = this.normalizeList(res)

        console.log('📊 API返回航线数量:', list.length)
        console.log('📊 所有航线ID:', list.map(w => w.id).sort((a, b) => a - b))

        // 保存所有航线数据
        this.allWaylines = list

        // 构建原有的 waylines 数组（用于筛选）
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

        // 构建地点树形结构
        this.buildLocationTree()
      } catch (err) {
        console.warn('加载航线列表失败，使用空列表', err)
        this.waylines = []
        this.allWaylines = []
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

    jumpToLatestInspectImage() {
      if (!this.inspectImages.length) return
      this.inspectIndex = Math.max(this.inspectImages.length - 1, 0)
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
        console.log('✅ 所有任务完成')
        this.allTasksCompleted = true
        // 根据模式显示不同提示
        if (this.isDetectMode) {
          ElMessage.success('所有任务检测完成')
        } else {
          ElMessage.success('所有任务回放完毕')
        }
      }
    },

    // 开始回放下一个任务
    async startNextTaskPlayback() {
      if (this.currentTaskIndex >= this.taskQueue.length) {
        console.log('⚠️ 任务队列已空')
        return
      }
      const taskOrName = this.taskQueue[this.currentTaskIndex]
      const name = taskOrName.external_task_id || taskOrName
      
      console.log(`🎬 开始回放任务: ${name} (第 ${this.currentTaskIndex + 1}/${this.taskQueue.length} 个)`)
      this.allTasksCompleted = false // 重置完成标志
      await this.startInspectPlaybackForFolder(taskOrName)
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
    },

    // ==================== 地点树形结构相关方法 ====================

    // 构建地点树形结构
    buildLocationTree() {
      const locationMap = new Map()

      // 定义固定的检测类型
      const fixedTypes = [
        { typeName: '铁路检测', typeKey: 'rail', icon: '🛤️' },
        { typeName: '接触网检测', typeKey: 'contactline', icon: '⚡' },
        { typeName: '桥梁检测', typeKey: 'bridge', icon: '🌉' },
        { typeName: '保护区检测', typeKey: 'protected_area', icon: '🛡️' }
      ]

      // 🔍 调试：打印所有航线名称
      console.log('🔍 所有航线数据:', this.allWaylines.map(w => ({ id: w.id, name: w.name })))

      // 遍历所有航线，提取地点和检测类型
      this.allWaylines.forEach(wayline => {
        console.log(`🔍 解析航线: "${wayline.name}"`)

        const locationInfo = this.parseWaylineName(wayline.name)
        console.log(`  → 解析结果:`, locationInfo)

        if (!locationMap.has(locationInfo.location)) {
          locationMap.set(locationInfo.location, {
            location: locationInfo.location,
            types: new Map()
          })
        }

        const locationData = locationMap.get(locationInfo.location)
        if (!locationData.types.has(locationInfo.typeKey)) {
          locationData.types.set(locationInfo.typeKey, {
            typeName: locationInfo.typeName,
            typeKey: locationInfo.typeKey,
            icon: locationInfo.icon,
            waylines: [],
            tasks: []
          })
        }

        locationData.types.get(locationInfo.typeKey).waylines.push(wayline)
      })

      // 转换为数组格式，并确保每个地点都有三种检测类型
      this.locationTree = Array.from(locationMap.values()).map(loc => {
        const existingTypes = loc.types

        // 创建三种固定类型，如果已存在则使用现有的，否则创建空的
        const types = fixedTypes.map(fixedType => {
          if (existingTypes.has(fixedType.typeKey)) {
            return existingTypes.get(fixedType.typeKey)
          } else {
            return {
              typeName: fixedType.typeName,
              typeKey: fixedType.typeKey,
              icon: fixedType.icon,
              waylines: [],
              tasks: []
            }
          }
        })

        return {
          location: loc.location,
          types: types
        }
      })

      console.log('📍 地点树结构:', this.locationTree)
      console.log('📍 地点列表:', this.locationTree.map(loc => loc.location))
    },

    // 解析航线名称，提取地点和检测类型
    parseWaylineName(name) {
      if (!name) return {
        location: '其他地点',
        typeName: '铁路检测',
        typeKey: 'rail',
        icon: '🛤️'
      }

      // 先去掉后缀
      let cleanName = name.replace(/-拼接航线$/, '')

      // 映射到完整类型名和英文key
      const typeMap = {
        '铁路': { name: '铁路检测', key: 'rail', icon: '🛤️' },
        '轨道': { name: '铁路检测', key: 'rail', icon: '🛤️' },
        '桥梁': { name: '桥梁检测', key: 'bridge', icon: '🌉' },
        '接触网': { name: '接触网检测', key: 'contactline', icon: '⚡' },
        '保护区': { name: '保护区检测', key: 'protected_area', icon: '🛡️' }
      }

      // 格式1: 工业大学左侧轨道 (标准格式)
      let match = cleanName.match(/^(.+)(左侧|右侧)(轨道|铁路|桥梁|接触网|保护区)$/)

      if (match) {
        const location = match[1]
        const side = match[2]
        const detectType = match[3]
        const typeInfo = typeMap[detectType] || typeMap['轨道']

        return {
          location: location,
          typeName: typeInfo.name,
          typeKey: typeInfo.key,
          icon: typeInfo.icon,
          side: side
        }
      }

      // 格式2: 宁官至余量良桥梁左侧 (地点+类型+侧别，顺序相反)
      match = cleanName.match(/^(.+)(轨道|铁路|桥梁|接触网|保护区)(左侧|右侧)$/)

      if (match) {
        const location = match[1]
        const detectType = match[2]
        const side = match[3]
        const typeInfo = typeMap[detectType] || typeMap['轨道']

        return {
          location: location,
          typeName: typeInfo.name,
          typeKey: typeInfo.key,
          icon: typeInfo.icon,
          side: side
        }
      }

      // 格式3: 余良至地下轨道 (没有侧别)
      match = cleanName.match(/^(.+)(轨道|铁路|桥梁|接触网|保护区)$/)

      if (match) {
        const location = match[1]
        const detectType = match[2]
        const typeInfo = typeMap[detectType] || typeMap['轨道']

        return {
          location: location,
          typeName: typeInfo.name,
          typeKey: typeInfo.key,
          icon: typeInfo.icon,
          side: ''
        }
      }

      // 格式4: 包含检测关键字的模糊匹配
      for (const [keyword, typeInfo] of Object.entries(typeMap)) {
        if (cleanName.includes(keyword)) {
          let location = cleanName.replace(keyword, '').replace(/^[左右]侧/, '').replace(/^[左右]侧$/, '')
          location = location.replace(/-/g, '')
          return {
            location: location || cleanName,
            typeName: typeInfo.name,
            typeKey: typeInfo.key,
            icon: typeInfo.icon,
            side: ''
          }
        }
      }

      // 默认返回（归入轨道检测）
      return {
        location: cleanName,
        typeName: '铁路检测',
        typeKey: 'rail',
        icon: '🛤️'
      }
    },

    // 将任务匹配到树形结构
    matchTasksToTree(tasks) {
      // 先清空所有任务
      this.locationTree.forEach(loc => {
        loc.types.forEach(type => {
          type.tasks = []
        })
      })

      // 匹配任务到对应位置
      tasks.forEach(task => {
        if (!task.wayline) return

        // 获取任务对应的航线
        const wayline = this.allWaylines.find(w => w.id === task.wayline)
        if (!wayline) return

        // 解析航线名称
        const locationInfo = this.parseWaylineName(wayline.name)

        // 找到对应的地点和类型
        const location = this.locationTree.find(loc => loc.location === locationInfo.location)
        if (!location) return

        const type = location.types.find(t => t.typeKey === locationInfo.typeKey)
        if (!type) return

        // 添加任务
        type.tasks.push(task)
      })

      console.log('🌳 匹配任务后的树结构:', this.locationTree)
    },

    // 展开/折叠地点
    toggleLocation(location) {
      if (this.expandedLocations.has(location)) {
        this.expandedLocations.delete(location)
      } else {
        this.expandedLocations.add(location)
      }
    },

    isLocationExpanded(location) {
      return this.expandedLocations.has(location)
    },

    // 展开/折叠检测类型
    toggleType(location, typeKey) {
      const key = `${location}|${typeKey}`
      if (this.expandedTypes.has(key)) {
        this.expandedTypes.delete(key)
      } else {
        this.expandedTypes.add(key)
      }
    },

    isTypeExpanded(location, typeKey) {
      const key = `${location}|${typeKey}`
      return this.expandedTypes.has(key)
    },

    // 获取地点下所有任务数量
    getTotalTasksCount(locGroup) {
      return locGroup.types.reduce((sum, type) => sum + type.tasks.length, 0)
    },

    // 获取任务的侧别（左侧/右侧）
    getTaskSide(task) {
      const wayline = this.allWaylines.find(w => w.id === task.wayline)
      if (wayline) {
        const match = wayline.name.match(/(左侧|右侧)/)
        return match ? match[1] : ''
      }
      return ''
    },

    // 格式化任务时间
    formatTaskTime(task) {
      const match = task.external_task_id?.match(/^(\d{8})/)
      return match ? match[1] : ''
    },

    // 检查任务是否被选中
    isTaskSelected(taskId) {
      return this.selectedFolders.includes(taskId)
    },

    // ==================== 新增：三级树结构方法 ====================

    // 加载历史任务树
    async loadHistoryTree(silent = false) {
      if (this.treeLoading) return
      if (!silent) this.treeLoading = true
      this.treeError = ''

      try {
        // 1. 获取所有检测类型
        // 🔥 移除 .slice(0, 4) 限制，显示所有配置的检测类型
        const categoryRes = await alarmApi.getAlarmCategories({ page_size: 100 })
        const categories = this.normalizeList(categoryRes)

        // 图标映射
        const iconMap = {
          'rail': '🛤️',
          'contactline': '⚡',
          'bridge': '🌉',
          'protected_area': '🛡️',
          'catenary': '⚡',
          'overhead': '⚡',
          'insulator': '⚡',
          'pole': '⚡',
          'protection_zone': '🛡️'
        }

        // 2. 构建树结构
        const tree = []
        for (const category of categories) {
          const categoryNode = {
            code: category.code,
            name: category.name,
            icon: iconMap[category.code] || '🔍',
            taskCount: 0,
            waylines: []
          }

          // 🔥 3. 混合模式：确保第二级是“航线”
          // 策略：
          // A. 先获取该分类绑定的所有航线 (作为骨架)
          // B. 再获取该分类下的所有任务 (填充内容)
          // C. 如果有任务但不属于 A 中的航线，也需要补全 (防止漏掉数据)

          // Step A: 获取航线骨架 (减少 N+1，但保证结构正确)
          const waylineRes = await waylineApi.getWaylines({
             detect_type: category.code, 
             page_size: 100
          })
          const waylines = this.normalizeList(waylineRes)
          
          const waylineMap = new Map()
          
          // 初始化骨架 (即时没有任务，也会显示航线节点，状态为 0 任务)
          for (const w of waylines) {
             waylineMap.set(w.id, {
                id: w.id,
                name: w.name,
                tasks: [] // 初始为空
             })
          }

          // Step B: 获取任务数据 (批量获取，高效)
          const taskRes = await inspectTaskApi.getInspectTasks({
            detect_category: String(category.id),
            parent_task__isnull: 'false',
            page_size: 500,
            ordering: '-created_at'
          })
          const allTasks = this.normalizeList(taskRes)
          
          console.log(`📍 检测类型 ${category.name} 的任务总数:`, allTasks.length)

          // Step C: 将任务填入航线槽位
          let unboundCount = 0
          for (const task of allTasks) {
            if (task.parent_task === null) continue
            // 跳过没有关联航线的任务
            if (!task.wayline) {
              unboundCount += 1
              continue
            }
            
            const wId = task.wayline
            const wName = (task.wayline_details && task.wayline_details.name) 
              ? task.wayline_details.name 
              : (typeof task.external_task_id === 'string' ? task.external_task_id.replace(/^\d{8}/, '') || `未知航线-${wId}` : `未知航线-${wId}`)

            // 如果这个航线不在骨架里 (可能是历史数据，或者 detect_type 没对上)，自动补全
            if (!waylineMap.has(wId)) {
              waylineMap.set(wId, {
                id: wId,
                name: wName,
                tasks: []
              })
            }
            
            const alarmCount = task.alarm_count || 0 
            
            waylineMap.get(wId).tasks.push({
              ...task,
              alarm_count: alarmCount
            })
          }

          // 5. 转换为数组结构 (显示所有航线，包括无任务的)
          for (const wData of waylineMap.values()) {
             // 策略调整：显示所有关联航线，即便是空航线
             categoryNode.waylines.push(wData)
             categoryNode.taskCount += wData.tasks.length
          }
          
          // 6. 统计未绑定航线的任务，不展示分组
          if (unboundCount > 0) {
            categoryNode.taskCount += unboundCount
          }

          // 🔥 排序：将有任务的航线置顶
          categoryNode.waylines.sort((a, b) => {
             const countA = a.tasks ? a.tasks.length : 0
             const countB = b.tasks ? b.tasks.length : 0
             // 有任务的排前面
             if (countA > 0 && countB === 0) return -1
             if (countA === 0 && countB > 0) return 1
             // 都有任务或都没有任务，保持原序 (或者按名称排，这里保持原序比较稳妥)
             return 0
          })

          tree.push(categoryNode)
        }

        // ==========================================
        // 🔥 新增：处理未分类/手动上传的任务
        // ==========================================
        try {
          const uncategorizedTasksRes = await inspectTaskApi.getInspectTasks({
             detect_category__isnull: 'true',
             page_size: 100,
             ordering: '-created_at'
          })
          let uncategorizedTasks = this.normalizeList(uncategorizedTasksRes)
          
          // 🔥 过滤掉父任务 (parent_task 为 null 的容器任务)
          // 只保留真正的子任务（这些子任务确实没匹配到分类）
          // 避免在界面上显示重复的父任务节点
          uncategorizedTasks = uncategorizedTasks.filter(t => t.parent_task !== null)

          if (uncategorizedTasks.length > 0) {
             const uncatNode = {
               code: 'uncategorized',
               name: '未分类/手动上传',
               icon: '📁',
               taskCount: uncategorizedTasks.length,
               waylines: []
             }
             
             // 虚拟航线分组
             const uncatWayline = {
               id: 'manual',
               name: '手动上传文件夹',
               tasks: uncategorizedTasks.map(t => ({
                  ...t,
                  alarm_count: t.alarm_count || 0
               }))
             }
             
             uncatNode.waylines.push(uncatWayline)
             tree.push(uncatNode)
          }
        } catch (e) {
          console.warn('获取未分类任务失败:', e)
        }

        this.detectionTree = tree
        console.log('✅ 历史任务树加载完成:', tree)

        // ==========================================
        // 🔥 全局自动播放逻辑 (Global Auto-Play)
        // ==========================================
        // 遍历整个树，寻找最新创建的任务 (ID最大的)
        let newestGlobalTask = null

        // 1. 遍历所有分类节点 (包括未分类)
        for (const node of tree) {
          if (!node.waylines) continue
          
          for (const wayline of node.waylines) {
             if (!wayline.tasks) continue
             
             for (const task of wayline.tasks) {
                if (!newestGlobalTask) {
                   newestGlobalTask = task
                } else {
                   // 比较 ID 或 created_at
                   if (task.id > newestGlobalTask.id) {
                      newestGlobalTask = task
                   }
                }
             }
          }
        }

        if (newestGlobalTask) {
           // 检查是否是新出现的任务
           const isNewTask = newestGlobalTask.id !== this.latestManualTaskId
           // 如果是首次加载（没有记录过ID），我们只记录不自动播放（避免一进页面就乱跳）
           // 除非用户明确处于空闲状态且没有选定任务
           const isFirstLoad = !this.latestManualTaskId

           if (isFirstLoad || isNewTask) {
              // 更新记录
              this.latestManualTaskId = newestGlobalTask.id

              if (isNewTask && !isFirstLoad) {
                 console.log(`✨ [Auto] 发现新任务 (ID: ${newestGlobalTask.id}):`, newestGlobalTask.external_task_id)
                 
                 // 1. 自动展开对应的菜单
                 // 找到这个任务归属的 categoryCode 和 waylineId
                 // 由于我们这里只有 task 对象，需要反向查找或者在遍历时记录
                 // 简单做法：直接把所有相关层级展开（略显粗暴但有效），或者根据 task 信息推断
                 
                 // 尝试从 task 信息中获取分类
                 let targetCategoryCode = null
                 if (newestGlobalTask.detect_category_code) {
                    targetCategoryCode = newestGlobalTask.detect_category_code
                 } else if (newestGlobalTask.detect_category === null) {
                    targetCategoryCode = 'uncategorized'
                 } else {
                    // 遍历树查找归属
                    for (const n of tree) {
                       const found = n.waylines?.some(w => w.tasks?.some(t => t.id === newestGlobalTask.id))
                       if (found) {
                          targetCategoryCode = n.code
                          break
                       }
                    }
                 }

                 if (targetCategoryCode) {
                     this.expandedCategories.add(targetCategoryCode)
                  }
 
                  // 2. 弹窗提示 (更显眼)
                  ElNotification({
                     title: '新任务自动启动',
                     message: `检测到任务 ID: ${newestGlobalTask.id} (${newestGlobalTask.external_task_id})，正在自动切换至可视化界面...`,
                     type: 'success',
                     duration: 5000,
                     position: 'top-right'
                  })
 
                  // 3. 强制自动播放 (无需点击，且抢占当前播放)
                  console.log('▶️ [Auto] 强制切换到新任务')
                  this.startInspectPlaybackForFolder(newestGlobalTask, true)
               }
            }
         }
      } catch (err) {
        console.error('❌ 加载历史任务树失败:', err)
        if (!silent) this.treeError = '加载失败，请稍后重试'
      } finally {
        if (!silent) this.treeLoading = false
      }
    },

    // 展开/折叠检测类型
    toggleCategory(code) {
      if (this.expandedCategories.has(code)) {
        this.expandedCategories.delete(code)
      } else {
        this.expandedCategories.add(code)
      }
    },

    isCategoryExpanded(code) {
      return this.expandedCategories.has(code)
    },

    // 展开/折叠航线
    toggleWaylineInTree(categoryCode, waylineId) {
      const key = `${categoryCode}-${waylineId}`
      if (this.expandedWaylines.has(key)) {
        this.expandedWaylines.delete(key)
      } else {
        this.expandedWaylines.add(key)
      }
    },

    isWaylineExpanded(categoryCode, waylineId) {
      const key = `${categoryCode}-${waylineId}`
      return this.expandedWaylines.has(key)
    },

    // 回放任务的告警
    async playTaskAlarms(task) {
      this.selectedHistoryTask = task
      this.currentInspectTaskId = null // 确保切换回轮播模式
      console.log('🎬 开始回放任务告警:', task.external_task_id)

      try {
        // 获取该任务的所有告警
        const res = await alarmApi.getAlarms({
          source_task: task.id,
          page_size: 100,
          ordering: 'created_at'
        })
        const alarms = this.normalizeList(res)
        
        if (!alarms.length) {
          ElMessage.warning('该任务暂无异常记录')
          return
        }

        // 构建轮播数据
        this.flowSlides = alarms.map((alarm, idx) => ({
          ...alarm,
          key: `${alarm.id || idx}-${idx}`,
          state: 'abnormal',
          stateText: '异常',
          hint: alarm.content || '检测到异常',
          // 🔥 修复：优先使用 signed_url，否则图片无法加载
          image_url: alarm.image_signed_url || alarm.image_url
        }))

        this.activeIndex = 0
        this.stopAuto()
        this.startAuto()

        ElMessage.success(`开始回放：${task.external_task_id}（${alarms.length}个异常）`)
      } catch (err) {
        console.error('❌ 加载任务告警失败:', err)
        ElMessage.error('加载任务告警失败')
      }
    },

    // 格式化任务日期
    formatTaskDate(dateStr) {
      if (!dateStr) return '--'
      const dt = new Date(dateStr)
      if (isNaN(dt.getTime())) return '--'
      const pad = num => String(num).padStart(2, '0')
      return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}`
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

.action-btn-compact {
  background: rgba(14, 165, 233, 0.2);
  border: 1px solid rgba(14, 165, 233, 0.4);
  color: #38bdf8;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  cursor: pointer;
  margin-right: 8px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-btn-compact:hover {
  background: rgba(14, 165, 233, 0.4);
  transform: scale(1.05);
}

.action-btn-compact .btn-icon {
  font-size: 10px;
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

/* ==================== 地点树形结构样式 ==================== */

/* 地点组 */
.location-group {
  margin-bottom: 16px;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(14, 165, 233, 0.2);
}

.location-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(6, 182, 212, 0.1));
  border-bottom: 1px solid rgba(14, 165, 233, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
}

.location-header:hover {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.25), rgba(6, 182, 212, 0.15));
}

.location-icon {
  font-size: 16px;
}

.location-name {
  flex: 1;
  font-size: 14px;
  font-weight: 700;
  color: #7dd3fc;
}

.location-count {
  font-size: 12px;
  color: #94a3b8;
  padding: 2px 8px;
  background: rgba(14, 165, 233, 0.15);
  border-radius: 10px;
}

.toggle-icon {
  font-size: 10px;
  color: #64748b;
  transition: transform 0.3s ease;
}

/* 检测类型组 */
.type-group {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.type-group:last-child {
  border-bottom: none;
}

.type-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px 10px 30px;
  background: rgba(255, 255, 255, 0.02);
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.type-header:hover {
  background: rgba(255, 255, 255, 0.04);
}

.type-icon {
  font-size: 14px;
}

.type-name {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: #cbd5e1;
}

.type-count {
  font-size: 11px;
  color: #64748b;
  padding: 2px 6px;
  background: rgba(148, 163, 184, 0.15);
  border-radius: 8px;
}

.type-count.highlight-count {
  color: #38bdf8;
  background: rgba(14, 165, 233, 0.25);
  border: 1px solid rgba(14, 165, 233, 0.5);
  font-weight: 700;
  box-shadow: 0 0 10px rgba(14, 165, 233, 0.2);
}

/* 任务元信息 */
.task-meta-compact {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
}

.task-side {
  font-size: 11px;
  color: #06b6d4;
  padding: 1px 6px;
  background: rgba(6, 182, 212, 0.15);
  border-radius: 4px;
}

.task-divider {
  color: #475569;
  font-size: 10px;
}

.task-time {
  font-size: 11px;
  color: #64748b;
  font-family: 'Courier New', monospace;
}

/* 空任务提示 */
.empty-tasks-hint {
  padding: 20px;
  text-align: center;
  color: #64748b;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.01);
  margin: 0 12px 12px 12px;
  border-radius: 8px;
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

.progress-count {
  color: #e0f2fe;
  font-size: 14px;
  font-weight: 700;
  padding: 0 10px;
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

/* 新增：三级树结构样式 */
.task-item-compact.clickable {
  cursor: pointer;
  transition: all 0.2s ease;
}

.task-item-compact.clickable:hover {
  background: rgba(99, 102, 241, 0.1);
  transform: translateX(4px);
}

.task-item-compact.active {
  background: rgba(99, 102, 241, 0.15);
  border-left: 3px solid #6366f1;
}

.alarm-count {
  color: #ef4444;
  font-weight: 600;
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
