<template>
  <div class="inspect-relationship-page">
    <!-- 星空背景 -->
    <div class="starry-background">
      <div class="stars"></div>
      <div class="stars2"></div>
      <div class="stars3"></div>
    </div>

    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <span class="title-icon">🔗</span>
        检测类型与航线关系可视化
      </h1>
      <div class="subtitle">Detection Type & Wayline Relationship Visualization</div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载数据中...</p>
    </div>

    <!-- 主可视化区域 -->
    <div v-else class="visualization-container">
      <div class="viz-canvas">
        <!-- 左侧：检测类型卡片 -->
        <div class="detection-types">
          <div
            v-for="(category, index) in categories"
            :key="category.id"
            :ref="el => { if (el) typeRefs[index] = el }"
            class="type-card"
            :class="{ 'active': hoveredType === category.id }"
            :style="{ animationDelay: `${index * 0.1}s` }"
            @mouseenter="hoveredType = category.id"
            @mouseleave="hoveredType = null"
          >
            <div class="type-icon-wrapper">
              <div class="type-icon" v-html="getTypeIcon(category.code)" :key="`icon-${category.id}-${category.code}`"></div>
              <div class="type-glow"></div>
            </div>
            <div class="type-info">
              <div class="type-name">{{ category.name }}</div>
              <div class="type-code">CODE: {{ category.code || '未设置' }}</div>
            </div>
            <div class="type-badge">
              <span class="badge-label">航线</span>
              <span class="badge-value">{{ category.wayline_name || '未关联' }}</span>
            </div>
          </div>
        </div>

        <!-- 右侧：航线信息卡片 -->
        <div class="waylines">
          <div
            v-for="(category, index) in categories"
            :key="`wayline-${category.id}`"
            :ref="el => { if (el) waylineRefs[index] = el }"
            class="wayline-card"
            :class="{ 'active': hoveredType === category.id }"
            :style="{ animationDelay: `${index * 0.1 + 0.2}s` }"
            @mouseenter="hoveredType = category.id"
            @mouseleave="hoveredType = null"
          >
            <div class="wayline-header">
              <div class="wayline-icon">✈️</div>
              <div class="wayline-title">{{ category.wayline_name || '未关联航线' }}</div>
            </div>
            <div class="wayline-stats">
              <div class="stat-item">
                <span class="stat-label">ID</span>
                <span class="stat-value">{{ category.wayline_id || '--' }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">检测类型</span>
                <span class="stat-value">{{ category.name }}</span>
              </div>
            </div>
            <div class="wayline-visual">
              <svg width="100%" height="60" viewBox="0 0 240 60" preserveAspectRatio="xMidYMid meet">
                <!-- 航线预览折线 -->
                <path
                  :d="getWaylinePreview(index)"
                  :stroke="getTypeColor(category.code)"
                  stroke-width="3"
                  fill="none"
                  opacity="0.8"
                  class="preview-path"
                />
                <!-- 预览折线的闪烁节点 -->
                <g v-for="(point, pIndex) in getWaylinePreviewPoints(index)" :key="`preview-point-${index}-${pIndex}`">
                  <!-- 外圈发光圆 -->
                  <circle
                    :cx="point.x"
                    :cy="point.y"
                    r="8"
                    :fill="getTypeColor(category.code)"
                    opacity="0.3"
                    :class="['wayline-point-glow-small', { 'active': hoveredType === category.id }]"
                  />
                  <!-- 内圈实心圆 -->
                  <circle
                    :cx="point.x"
                    :cy="point.y"
                    r="4"
                    :fill="getTypeColor(category.code)"
                    :class="['wayline-point-small', { 'active': hoveredType === category.id }]"
                  />
                </g>
              </svg>
            </div>
          </div>
        </div>
        
        <!-- SVG 连接线画布 -->
        <svg 
          class="connection-svg"
          :style="{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none'
          }"
        >
          <defs>
            <!-- 渐变定义 -->
            <linearGradient 
              v-for="(category, index) in categories" 
              :key="`grad-${category.id}`"
              :id="`gradient-${index}`"
              x1="0%" y1="0%" x2="100%" y2="0%"
            >
              <stop offset="0%" :stop-color="getTypeColor(category.code)" stop-opacity="0.8" />
              <stop offset="50%" :stop-color="getTypeColor(category.code)" stop-opacity="1" />
              <stop offset="100%" :stop-color="getTypeColor(category.code)" stop-opacity="0.8" />
            </linearGradient>
            
            <!-- 滤镜定义 -->
            <filter :id="`glow-${index}`" v-for="(category, index) in categories" :key="`filter-${category.id}`">
              <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          <!-- 连接线 -->
          <g v-for="(category, index) in categories" :key="`connection-${category.id}`">
            <!-- 背景发光线 -->
            <path
              :d="getConnectionPath(index)"
              :stroke="getTypeColor(category.code)"
              stroke-width="3"
              fill="none"
              opacity="0.2"
              :filter="`url(#glow-${index})`"
              class="connection-glow"
              :class="{ 'active': hoveredType === category.id }"
            />
            
            <!-- 主连接线 -->
            <path
              :d="getConnectionPath(index)"
              :stroke="`url(#gradient-${index})`"
              stroke-width="2.5"
              fill="none"
              stroke-linecap="round"
              class="connection-line"
              :class="{ 'active': hoveredType === category.id }"
              :style="{ animationDelay: `${index * 0.3}s` }"
            />
            
            <!-- 起点高亮圆点 -->
            <circle
              :cx="getConnectionPoints(index).startX"
              :cy="getConnectionPoints(index).startY"
              r="6"
              :fill="getTypeColor(category.code)"
              opacity="0.3"
              class="connection-point-glow"
              :class="{ 'active': hoveredType === category.id }"
            />
            <circle
              :cx="getConnectionPoints(index).startX"
              :cy="getConnectionPoints(index).startY"
              r="4"
              :fill="getTypeColor(category.code)"
              class="connection-point"
              :class="{ 'active': hoveredType === category.id }"
            />
            
            <!-- 终点高亮圆点 -->
            <circle
              :cx="getConnectionPoints(index).endX"
              :cy="getConnectionPoints(index).endY"
              r="6"
              :fill="getTypeColor(category.code)"
              opacity="0.3"
              class="connection-point-glow"
              :class="{ 'active': hoveredType === category.id }"
            />
            <circle
              :cx="getConnectionPoints(index).endX"
              :cy="getConnectionPoints(index).endY"
              r="4"
              :fill="getTypeColor(category.code)"
              class="connection-point"
              :class="{ 'active': hoveredType === category.id }"
            />
            
            <!-- 波动粒子 -->
            <circle
              :r="4"
              :fill="getTypeColor(category.code)"
              class="flow-particle"
              :class="{ 'active': hoveredType === category.id }"
            >
              <animateMotion
                :path="getConnectionPath(index)"
                :dur="`${3 + index * 0.5}s`"
                repeatCount="indefinite"
              />
            </circle>
            
            <!-- 第二个波动粒子（延迟） -->
            <circle
              :r="3"
              :fill="getTypeColor(category.code)"
              opacity="0.6"
              class="flow-particle"
              :class="{ 'active': hoveredType === category.id }"
            >
              <animateMotion
                :path="getConnectionPath(index)"
                :dur="`${3 + index * 0.5}s`"
                :begin="`${1.5 + index * 0.25}s`"
                repeatCount="indefinite"
              />
            </circle>
          </g>
        </svg>
      </div>
    </div>
  </div>
</template>

<script>
import alarmApi from '../api/alarmApi'

export default {
  name: 'InspectRelationship',
  data() {
    return {
      loading: true,
      categories: [],
      hoveredType: null,
      canvasWidth: 800,
      canvasHeight: 600,
      typeRefs: [],
      waylineRefs: [],
      connectionPoints: [], // 存储计算好的连接点位置
      svgWidth: 1200,
      svgHeight: 800
    }
  },
  async mounted() {
    await this.loadData()
    this.updateCanvasSize()
    // 等待DOM渲染完成后计算连接点位置
    this.$nextTick(() => {
      setTimeout(() => {
        this.updateConnectionPositions()
      }, 200) // 增加延迟到200ms
    })
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
  },
  methods: {
    async loadData() {
      try {
        const response = await alarmApi.getAlarmCategories()
        const allCategories = response?.results || response || []
        
        console.log('🔍 加载的检测类型数据:', allCategories)
        
        // 只取有航线的前4个检测类型
        this.categories = allCategories
          .filter(cat => cat.wayline)
          .slice(0, 4)
          .map(cat => {
            console.log(`🎯 检测类型: ${cat.name}, code: ${cat.code}, 航线ID: ${cat.wayline}`)
            return {
              ...cat,
              wayline_id: cat.wayline,
              wayline_name: cat.wayline_details?.name || `航线 ${cat.wayline}`
            }
          })
        
        console.log('🌐 最终显示的类型:', this.categories)
        console.log('📊 航线信息:', this.categories.map(c => ({ 
          type: c.name, 
          waylineId: c.wayline_id, 
          waylineName: c.wayline_name 
        })))
        this.loading = false
        
        // 数据加载完成后再次计算连接点
        this.$nextTick(() => {
          setTimeout(() => {
            this.updateConnectionPositions()
          }, 300)
        })
      } catch (error) {
        console.error('加载检测类型数据失败:', error)
        this.loading = false
      }
    },

    updateCanvasSize() {
      const container = document.querySelector('.visualization-container')
      if (container) {
        this.canvasWidth = container.clientWidth
        this.canvasHeight = Math.min(container.clientHeight, 600)
      }
      // 更新连接点位置
      this.$nextTick(() => {
        this.updateConnectionPositions()
      })
    },
    
    handleResize() {
      this.updateCanvasSize()
    },
    
    updateConnectionPositions() {
      // 动态计算每个连接点的实际位置
      this.connectionPoints = this.categories.map((category, index) => {
        const typeEl = this.typeRefs[index]
        const waylineEl = this.waylineRefs[index]
        
        if (!typeEl || !waylineEl) {
          console.log(`⚠️ 元素未找到: index ${index}`)
          return { startX: 0, startY: 0, endX: 0, endY: 0 }
        }
        
        const canvas = document.querySelector('.viz-canvas')
        if (!canvas) {
          return { startX: 0, startY: 0, endX: 0, endY: 0 }
        }
        
        const typeRect = typeEl.getBoundingClientRect()
        const waylineRect = waylineEl.getBoundingClientRect()
        const canvasRect = canvas.getBoundingClientRect()
        
        // 计算相对于画布的位置
        const startX = typeRect.left + typeRect.width / 2 - canvasRect.left
        const startY = typeRect.bottom - canvasRect.top
        const endX = waylineRect.left + waylineRect.width / 2 - canvasRect.left
        const endY = waylineRect.top - canvasRect.top
        
        console.log(`🔗 连接点 ${index}:`, {
          startX: Math.round(startX),
          startY: Math.round(startY),
          endX: Math.round(endX),
          endY: Math.round(endY)
        })
        
        return { startX, startY, endX, endY }
      })
    },

    getTypeIcon(code) {
      // 将 code 转为小写以兼容大小写
      const lowerCode = (code || '').toLowerCase()
      
      const icons = {
        // 轨道检测 - 铁轨横截面图标
        'rail': `<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- 铁轨枕木 -->
          <rect x="8" y="28" width="48" height="8" fill="currentColor" opacity="0.3" rx="2"/>
          <!-- 左侧钢轨 -->
          <path d="M12 20 L12 44 L16 44 L16 20 Z" fill="currentColor"/>
          <rect x="10" y="18" width="8" height="4" fill="currentColor" rx="1"/>
          <!-- 右侧钢轨 -->
          <path d="M48 20 L48 44 L52 44 L52 20 Z" fill="currentColor"/>
          <rect x="46" y="18" width="8" height="4" fill="currentColor" rx="1"/>
          <!-- 螺栓装饰 -->
          <circle cx="14" cy="30" r="1.5" fill="currentColor" opacity="0.6"/>
          <circle cx="14" cy="34" r="1.5" fill="currentColor" opacity="0.6"/>
          <circle cx="50" cy="30" r="1.5" fill="currentColor" opacity="0.6"/>
          <circle cx="50" cy="34" r="1.5" fill="currentColor" opacity="0.6"/>
          <!-- 中间连接线 -->
          <line x1="20" y1="32" x2="44" y2="32" stroke="currentColor" stroke-width="1" opacity="0.4"/>
        </svg>`,
        
        // 绝缘子/电线杆检测 - 绝缘子串联图标 (POLE, insulator)
        'insulator': `<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- 顶部连接 -->
          <circle cx="32" cy="8" r="3" fill="currentColor"/>
          <line x1="32" y1="11" x2="32" y2="16" stroke="currentColor" stroke-width="2"/>
          <!-- 第一层绝缘子 -->
          <ellipse cx="32" cy="20" rx="10" ry="4" fill="currentColor" opacity="0.8"/>
          <rect x="24" y="20" width="16" height="6" fill="currentColor" opacity="0.6" rx="1"/>
          <ellipse cx="32" cy="26" rx="10" ry="4" fill="currentColor" opacity="0.8"/>
          <!-- 连接线 -->
          <line x1="32" y1="26" x2="32" y2="30" stroke="currentColor" stroke-width="2"/>
          <!-- 第二层绝缘子 -->
          <ellipse cx="32" cy="34" rx="10" ry="4" fill="currentColor" opacity="0.8"/>
          <rect x="24" y="34" width="16" height="6" fill="currentColor" opacity="0.6" rx="1"/>
          <ellipse cx="32" cy="40" rx="10" ry="4" fill="currentColor" opacity="0.8"/>
          <!-- 连接线 -->
          <line x1="32" y1="40" x2="32" y2="44" stroke="currentColor" stroke-width="2"/>
          <!-- 第三层绝缘子 -->
          <ellipse cx="32" cy="48" rx="10" ry="4" fill="currentColor" opacity="0.8"/>
          <rect x="24" y="48" width="16" height="6" fill="currentColor" opacity="0.6" rx="1"/>
          <ellipse cx="32" cy="54" rx="10" ry="4" fill="currentColor" opacity="0.8"/>
          <!-- 底部连接 -->
          <line x1="32" y1="54" x2="32" y2="58" stroke="currentColor" stroke-width="2"/>
          <circle cx="32" cy="60" r="2" fill="currentColor"/>
        </svg>`,
        'pole': `<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- 顶部连接 -->
          <circle cx="32" cy="8" r="3" fill="currentColor"/>
          <line x1="32" y1="11" x2="32" y2="16" stroke="currentColor" stroke-width="2"/>
          <!-- 第一层绝缘子 -->
          <ellipse cx="32" cy="20" rx="10" ry="4" fill="currentColor" opacity="0.8"/>
          <rect x="24" y="20" width="16" height="6" fill="currentColor" opacity="0.6" rx="1"/>
          <ellipse cx="32" cy="26" rx="10" ry="4" fill="currentColor" opacity="0.8"/>
          <!-- 连接线 -->
          <line x1="32" y1="26" x2="32" y2="30" stroke="currentColor" stroke-width="2"/>
          <!-- 第二层绝缘子 -->
          <ellipse cx="32" cy="34" rx="10" ry="4" fill="currentColor" opacity="0.8"/>
          <rect x="24" y="34" width="16" height="6" fill="currentColor" opacity="0.6" rx="1"/>
          <ellipse cx="32" cy="40" rx="10" ry="4" fill="currentColor" opacity="0.8"/>
          <!-- 连接线 -->
          <line x1="32" y1="40" x2="32" y2="44" stroke="currentColor" stroke-width="2"/>
          <!-- 第三层绝缘子 -->
          <ellipse cx="32" cy="48" rx="10" ry="4" fill="currentColor" opacity="0.8"/>
          <rect x="24" y="48" width="16" height="6" fill="currentColor" opacity="0.6" rx="1"/>
          <ellipse cx="32" cy="54" rx="10" ry="4" fill="currentColor" opacity="0.8"/>
          <!-- 底部连接 -->
          <line x1="32" y1="54" x2="32" y2="58" stroke="currentColor" stroke-width="2"/>
          <circle cx="32" cy="60" r="2" fill="currentColor"/>
        </svg>`,
        
        // 桥梁/轨道检测 - 拱桥结构图标 (TRACK, bridge)
        'bridge': `<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- 桥面 -->
          <rect x="4" y="36" width="56" height="4" fill="currentColor" rx="1"/>
          <!-- 拱形结构 -->
          <path d="M 8 36 Q 16 20 24 36" stroke="currentColor" stroke-width="2.5" fill="none" opacity="0.8"/>
          <path d="M 24 36 Q 32 16 40 36" stroke="currentColor" stroke-width="2.5" fill="none" opacity="0.8"/>
          <path d="M 40 36 Q 48 20 56 36" stroke="currentColor" stroke-width="2.5" fill="none" opacity="0.8"/>
          <!-- 支撑柱 -->
          <rect x="14" y="36" width="3" height="16" fill="currentColor" opacity="0.6" rx="0.5"/>
          <rect x="30.5" y="36" width="3" height="16" fill="currentColor" opacity="0.6" rx="0.5"/>
          <rect x="47" y="36" width="3" height="16" fill="currentColor" opacity="0.6" rx="0.5"/>
          <!-- 桥墩基座 -->
          <rect x="12" y="52" width="7" height="3" fill="currentColor" rx="1"/>
          <rect x="28.5" y="52" width="7" height="3" fill="currentColor" rx="1"/>
          <rect x="45" y="52" width="7" height="3" fill="currentColor" rx="1"/>
          <!-- 装饰线条 -->
          <line x1="4" y1="40" x2="60" y2="40" stroke="currentColor" stroke-width="1" opacity="0.3"/>
        </svg>`,
        'track': `<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- 桥面 -->
          <rect x="4" y="36" width="56" height="4" fill="currentColor" rx="1"/>
          <!-- 拱形结构 -->
          <path d="M 8 36 Q 16 20 24 36" stroke="currentColor" stroke-width="2.5" fill="none" opacity="0.8"/>
          <path d="M 24 36 Q 32 16 40 36" stroke="currentColor" stroke-width="2.5" fill="none" opacity="0.8"/>
          <path d="M 40 36 Q 48 20 56 36" stroke="currentColor" stroke-width="2.5" fill="none" opacity="0.8"/>
          <!-- 支撑柱 -->
          <rect x="14" y="36" width="3" height="16" fill="currentColor" opacity="0.6" rx="0.5"/>
          <rect x="30.5" y="36" width="3" height="16" fill="currentColor" opacity="0.6" rx="0.5"/>
          <rect x="47" y="36" width="3" height="16" fill="currentColor" opacity="0.6" rx="0.5"/>
          <!-- 桥墩基座 -->
          <rect x="12" y="52" width="7" height="3" fill="currentColor" rx="1"/>
          <rect x="28.5" y="52" width="7" height="3" fill="currentColor" rx="1"/>
          <rect x="45" y="52" width="7" height="3" fill="currentColor" rx="1"/>
          <!-- 装饰线条 -->
          <line x1="4" y1="40" x2="60" y2="40" stroke="currentColor" stroke-width="1" opacity="0.3"/>
        </svg>`,
        
        // 接触网/接地线检测 - 接地符号图标 (OVERHEAD, glm)
        'overhead': `<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- 导线 -->
          <line x1="32" y1="8" x2="32" y2="28" stroke="currentColor" stroke-width="2.5"/>
          <!-- 连接点 -->
          <circle cx="32" cy="28" r="3" fill="currentColor"/>
          <!-- 接地符号 - 三层递减的横线 -->
          <line x1="20" y1="36" x2="44" y2="36" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
          <line x1="24" y1="42" x2="40" y2="42" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" opacity="0.8"/>
          <line x1="28" y1="48" x2="36" y2="48" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity="0.6"/>
          <!-- 垂直连接线 -->
          <line x1="32" y1="28" x2="32" y2="36" stroke="currentColor" stroke-width="2"/>
          <!-- 大地符号装饰 -->
          <path d="M 26 52 L 32 56 L 38 52" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.5"/>
        </svg>`,
        'glm': `<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- 导线 -->
          <line x1="32" y1="8" x2="32" y2="28" stroke="currentColor" stroke-width="2.5"/>
          <!-- 连接点 -->
          <circle cx="32" cy="28" r="3" fill="currentColor"/>
          <!-- 接地符号 - 三层递减的横线 -->
          <line x1="20" y1="36" x2="44" y2="36" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
          <line x1="24" y1="42" x2="40" y2="42" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" opacity="0.8"/>
          <line x1="28" y1="48" x2="36" y2="48" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity="0.6"/>
          <!-- 垂直连接线 -->
          <line x1="32" y1="28" x2="32" y2="36" stroke="currentColor" stroke-width="2"/>
          <!-- 大地符号装饰 -->
          <path d="M 26 52 L 32 56 L 38 52" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.5"/>
        </svg>`
      }
      
      // 返回对应图标，默认使用轨道图标
      return icons[lowerCode] || icons['rail']
    },

    getTypeColor(code) {
      // 将 code 转为小写以兼容大小写
      const lowerCode = (code || '').toLowerCase()
      
      const colors = {
        'rail': '#3b82f6',      // 蓝色 - 轨道
        'insulator': '#f59e0b', // 橙色 - 绝缘子
        'pole': '#f59e0b',      // 橙色 - 电线杆（同绝缘子）
        'bridge': '#8b5cf6',    // 紫色 - 桥梁
        'track': '#8b5cf6',     // 紫色 - 轨道结构（同桥梁）
        'overhead': '#10b981',  // 绿色 - 接触网
        'glm': '#10b981'        // 绿色 - 接地线
      }
      return colors[lowerCode] || '#3b82f6'
    },

    getConnectionPath(index) {
      // 计算连接线路径：从上方检测类型卡片到下方航线卡片
      const points = this.getConnectionPoints(index)
      const { startX, startY, endX, endY } = points
      
      // 创建垂直S形曲线路径（使用贝塞尔曲线）
      const controlX1 = startX + Math.sin(index * 0.5) * 20 // 轻微波动
      const controlY1 = startY + (endY - startY) * 0.3
      const controlX2 = endX + Math.cos(index * 0.5) * 20 // 轻微波动
      const controlY2 = endY - (endY - startY) * 0.3
      
      return `M ${startX} ${startY} C ${controlX1} ${controlY1}, ${controlX2} ${controlY2}, ${endX} ${endY}`
    },
    
    getConnectionPoints(index) {
      // 返回实际计算好的连接点位置
      if (this.connectionPoints[index]) {
        return this.connectionPoints[index]
      }
      
      // 默认位置（首次渲染时使用）
      const cardWidth = 240
      const cardHeight = 280
      const gap = 24 // 与CSS一致
      const totalWidth = 4 * cardWidth + 3 * gap
      const leftOffset = (this.svgWidth - totalWidth) / 2
      
      const startX = leftOffset + cardWidth / 2 + index * (cardWidth + gap)
      const startY = cardHeight
      const endX = startX
      const endY = cardHeight + 60 // 与CSS gap一致
      
      return { startX, startY, endX, endY }
    },

    getWaylinePreview(index) {
      // 航线卡片内的小型预览折线
      const points = this.getWaylinePreviewPoints(index)
      const pathSegments = points.map((point, i) => {
        return i === 0 ? `M ${point.x} ${point.y}` : `L ${point.x} ${point.y}`
      })
      return pathSegments.join(' ')
    },

    getWaylinePreviewPoints(index) {
      // 生成预览折线的关键点（用于绘制圆点）- 增加弯曲幅度
      return [
        { x: 20, y: 30 },
        { x: 60, y: 20 + Math.sin(index) * 15 },      // 增加幅度从 6 到 15
        { x: 100, y: 30 + Math.cos(index) * 18 },    // 增加幅度从 6 到 18
        { x: 140, y: 25 + Math.sin(index * 2) * 12 },// 增加幅度从 5 到 12
        { x: 180, y: 35 + Math.cos(index * 1.2) * 10 }, // 增加变化
        { x: 220, y: 30 + Math.sin(index * 1.5) * 8 } // 增加变化从 4 到 8
      ]
    }
  }
}
</script>

<style scoped>
.inspect-relationship-page {
  min-height: calc(100vh - 70px);
  padding: 32px;
  position: relative;
  overflow: hidden;
  background: radial-gradient(ellipse at bottom, #1a1f3a 0%, #0a0e1f 100%);
}

/* 星空背景 */
.starry-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.stars,
.stars2,
.stars3 {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: transparent;
}

.stars {
  background-image: 
    radial-gradient(2px 2px at 20px 30px, #eee, transparent),
    radial-gradient(2px 2px at 60px 70px, #fff, transparent),
    radial-gradient(1px 1px at 50px 50px, #ddd, transparent),
    radial-gradient(1px 1px at 130px 80px, #fff, transparent),
    radial-gradient(2px 2px at 90px 10px, #eee, transparent);
  background-size: 200px 200px;
  background-repeat: repeat;
  animation: twinkle 3s ease-in-out infinite;
}

.stars2 {
  background-image:
    radial-gradient(1px 1px at 100px 120px, #fff, transparent),
    radial-gradient(1px 1px at 40px 140px, #eee, transparent),
    radial-gradient(2px 2px at 180px 60px, #ddd, transparent),
    radial-gradient(1px 1px at 140px 180px, #fff, transparent);
  background-size: 250px 250px;
  background-repeat: repeat;
  animation: twinkle 4s ease-in-out infinite 1s;
}

.stars3 {
  background-image:
    radial-gradient(1px 1px at 70px 90px, #fff, transparent),
    radial-gradient(2px 2px at 160px 40px, #eee, transparent),
    radial-gradient(1px 1px at 110px 150px, #ddd, transparent);
  background-size: 300px 300px;
  background-repeat: repeat;
  animation: twinkle 5s ease-in-out infinite 2s;
}

@keyframes twinkle {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 48px;
  animation: fadeInDown 0.8s ease;
  position: relative;
  z-index: 1;
}

.page-title {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.title-icon {
  font-size: 42px;
  filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.6));
}

.subtitle {
  font-size: 14px;
  color: #94a3b8;
  letter-spacing: 2px;
  text-transform: uppercase;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #94a3b8;
  position: relative;
  z-index: 1;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(59, 130, 246, 0.2);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 24px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 主可视化容器 */
.visualization-container {
  background: rgba(26, 31, 58, 0.4);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  padding: 32px; /* 从 48px 减小到 32px */
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: fadeIn 0.8s ease;
  position: relative;
  z-index: 1;
}

.viz-canvas {
  position: relative;
  min-height: 800px; /* 从 900px 减小到 800px */
  display: flex;
  flex-direction: column;
  gap: 60px; /* 从 80px 减小到 60px */
  align-items: center;
  justify-content: center;
  max-width: 1200px; /* 从 1400px 减小到 1200px */
  margin: 0 auto;
  padding: 20px; /* 从 40px 减小到 20px */
}

/* SVG连接线画布 */
.connection-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

/* 检测类型卡片区域 */
.detection-types {
  display: grid;
  grid-template-columns: repeat(4, 240px);
  gap: 24px; /* 从 30px 减小到 24px */
  justify-content: center;
  z-index: 2;
  position: relative;
}

/* 航线卡片区域 */
.waylines {
  display: grid;
  grid-template-columns: repeat(4, 240px);
  gap: 24px; /* 从 30px 减小到 24px */
  justify-content: center;
  z-index: 2;
  position: relative;
}

.type-card {
  background: rgba(10, 14, 39, 0.8);
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  animation: slideInUp 0.6s ease forwards;
  opacity: 0;
  width: 240px; /* 与航线卡片保持一致 */
  flex-shrink: 0;
}

.type-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.type-card:hover::before,
.type-card.active::before {
  opacity: 1;
}

.type-card:hover,
.type-card.active {
  border-color: #3b82f6;
  box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
  transform: translateY(-8px) scale(1.02);
}

.type-icon-wrapper {
  position: relative;
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
}

.type-icon {
  width: 64px;
  height: 64px;
  color: #3b82f6;
  filter: drop-shadow(0 4px 12px rgba(59, 130, 246, 0.4));
  transition: all 0.3s ease;
}

.type-card:hover .type-icon,
.type-card.active .type-icon {
  transform: scale(1.1) rotate(5deg);
  filter: drop-shadow(0 6px 20px rgba(59, 130, 246, 0.6));
}

.type-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.3) 0%, transparent 70%);
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.type-card:hover .type-glow,
.type-card.active .type-glow {
  opacity: 1;
  animation: pulse 2s ease infinite;
}

.type-info {
  margin-bottom: 12px;
}

.type-name {
  font-size: 18px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 4px;
}

.type-code {
  font-size: 12px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.type-badge {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.badge-label {
  font-size: 11px;
  color: #64748b;
  text-transform: uppercase;
}

.badge-value {
  font-size: 12px;
  color: #60a5fa;
  font-weight: 600;
}

/* SVG 连接线画布 */
.connection-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
  overflow: visible;
}

/* 连接线背景发光 */
.connection-glow {
  transition: all 0.4s ease;
}

.connection-glow.active {
  opacity: 0.5 !important;
  stroke-width: 6;
}

/* SVG 连接线 - 只在中间区域 */
.connection-canvas {
  display: none;
}

/* 航线预览折线 */
.preview-path {
  transition: all 0.3s ease;
}

/* 航线节点闪烁动画 */
.wayline-point {
  animation: pointPulse 2s ease-in-out infinite;
  transition: all 0.3s ease;
}

.wayline-point.active {
  animation: pointPulseActive 1s ease-in-out infinite;
}

.wayline-point-glow {
  animation: glowPulse 2s ease-in-out infinite;
}

.wayline-point-glow.active {
  animation: glowPulseActive 1s ease-in-out infinite;
}

/* 小型节点动画（用于预览折线）*/
.wayline-point-small {
  animation: pointPulseSmall 2.5s ease-in-out infinite;
  transition: all 0.3s ease;
}

.wayline-point-small.active {
  animation: pointPulseSmallActive 1.2s ease-in-out infinite;
}

.wayline-point-glow-small {
  animation: glowPulseSmall 2.5s ease-in-out infinite;
}

.wayline-point-glow-small.active {
  animation: glowPulseSmallActive 1.2s ease-in-out infinite;
}

@keyframes pointPulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.2);
  }
}

@keyframes pointPulseActive {
  0%, 100% {
    opacity: 1;
    r: 3;
  }
  50% {
    opacity: 0.8;
    r: 4;
  }
}

@keyframes glowPulse {
  0%, 100% {
    opacity: 0.3;
    r: 6;
  }
  50% {
    opacity: 0.6;
    r: 8;
  }
}

@keyframes glowPulseActive {
  0%, 100% {
    opacity: 0.5;
    r: 8;
  }
  50% {
    opacity: 0.8;
    r: 10;
  }
}

/* 小型节点动画关键帧 */
@keyframes pointPulseSmall {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes pointPulseSmallActive {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

@keyframes glowPulseSmall {
  0%, 100% {
    opacity: 0.25;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes glowPulseSmallActive {
  0%, 100% {
    opacity: 0.4;
  }
  50% {
    opacity: 0.7;
  }
}

@keyframes dashMove {
  to { stroke-dashoffset: -1000; }
}

.connection-line {
  stroke-dasharray: 10 5;
  animation: dashFlow 20s linear infinite;
  transition: all 0.4s ease;
}

.connection-line.active {
  stroke-width: 3.5;
  filter: drop-shadow(0 0 8px currentColor);
  animation: dashFlow 10s linear infinite, pulseLine 1.5s ease infinite;
}

@keyframes dashFlow {
  to { stroke-dashoffset: -1000; }
}

@keyframes pulseLine {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.flow-particle {
  filter: drop-shadow(0 0 6px currentColor);
  transition: all 0.3s ease;
}

.flow-particle.active {
  filter: drop-shadow(0 0 12px currentColor);
}

/* 连接点高亮效果 */
.connection-point {
  transition: all 0.4s ease;
  animation: pointPulse 2s ease-in-out infinite;
}

.connection-point.active {
  animation: pointPulseActive 1s ease-in-out infinite;
}

.connection-point-glow {
  animation: glowPulse 2s ease-in-out infinite;
}

.connection-point-glow.active {
  animation: glowPulseActive 1s ease-in-out infinite;
  opacity: 0.6 !important;
}

@keyframes pointPulse {
  0%, 100% {
    r: 4;
    opacity: 1;
  }
  50% {
    r: 5;
    opacity: 0.8;
  }
}

@keyframes pointPulseActive {
  0%, 100% {
    r: 4;
    opacity: 1;
  }
  50% {
    r: 6;
    opacity: 0.9;
  }
}

@keyframes glowPulse {
  0%, 100% {
    r: 6;
    opacity: 0.3;
  }
  50% {
    r: 8;
    opacity: 0.5;
  }
}

@keyframes glowPulseActive {
  0%, 100% {
    r: 6;
    opacity: 0.6;
  }
  50% {
    r: 10;
    opacity: 0.8;
  }
}

/* 航线卡片样式 */
.wayline-card {
  background: rgba(10, 14, 39, 0.8);
  border: 2px solid rgba(139, 92, 246, 0.3);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: slideInUp 0.6s ease forwards;
  opacity: 0;
  width: 240px; /* 减小宽度以适应一行显示 */
  flex-shrink: 0;
}

.wayline-card:hover,
.wayline-card.active {
  border-color: #8b5cf6;
  box-shadow: 0 8px 32px rgba(139, 92, 246, 0.3);
  transform: translateY(-8px) scale(1.02);
}

.wayline-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.wayline-icon {
  font-size: 28px;
  filter: drop-shadow(0 2px 8px rgba(139, 92, 246, 0.4));
}

.wayline-title {
  font-size: 16px;
  font-weight: 700;
  color: #e2e8f0;
}

.wayline-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 11px;
  color: #64748b;
  text-transform: uppercase;
}

.stat-value {
  font-size: 13px;
  color: #a78bfa;
  font-weight: 600;
}

.wayline-visual {
  background: rgba(139, 92, 246, 0.05);
  border-radius: 8px;
  padding: 8px;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
  from {
    opacity: 0;
    transform: translateY(30px);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}
</style>
