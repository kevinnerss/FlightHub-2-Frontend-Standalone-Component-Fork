<template>
  <div class="wayline-list-premium">
    <!-- 航线列表头部 -->
    <div class="list-header">
      <h3 class="list-title">航线列表</h3>
      <span v-if="waylineTree.length > 0" class="wayline-count">{{ totalWaylineCount }}</span>
    </div>
    
    <!-- 航线项列表 -->
    <div class="wayline-items" v-loading="loading">
      <div v-if="!loading && waylineTree.length === 0" class="empty-state">
        <div class="empty-icon">📍</div>
        <p>暂无航线</p>
      </div>
      
      <div v-else>
        <div 
          class="tree-group" 
          v-for="group in waylineTree" 
          :key="group.type"
        >
          <div class="tree-group-header" @click="toggleGroup(group.type)">
            <span class="group-name">{{ group.label }}</span>
            <span class="group-count">（{{ group.count }} 条航线）</span>
            <span class="toggle-icon">{{ expandedMap[group.type] ? '▼' : '▶' }}</span>
          </div>
          <div class="tree-items" v-show="expandedMap[group.type]">
            <div 
              class="wayline-item"
              v-for="item in group.items" 
              :key="item.id"
              :class="{ selected: item.id === currentSelectedId }"
              @click="handleSelect(item)"
            >
              <div class="wayline-item-header">
                <span class="wayline-id">ID: {{ item.id }}</span>
                <span class="wayline-duration" v-if="item.estimated_duration">
                  <span class="duration-icon">⏱️</span>
                  {{ formatDuration(item.estimated_duration) }}
                </span>
              </div>
              <div class="wayline-name">
                {{ item.name }}
                <span class="recent-meta" v-if="item.recent_task_time">（最近任务：{{ formatRecent(item.recent_task_time) }}）</span>
              </div>
              <div class="select-indicator"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import waylineApi from '../api/waylineApi'

export default {
  name: 'WaylineList',
  props: {
    currentSelectedId: {
      type: Number,
      default: null
    }
  },
  emits: ['wayline-selected'],
  data() {
    return {
      waylineTree: [],
      loading: false,
      expandedMap: {}
    }
  },
  computed: {
    totalWaylineCount() {
      return this.waylineTree.reduce((sum, g) => {
        const count = Array.isArray(g.items) ? g.items.length : 0
        return sum + count
      }, 0)
    }
  },
  async mounted() {
    await this.loadWaylineTree()
  },
  methods: {
    async loadWaylineTree() {
      this.loading = true
      try {
        const res = await waylineApi.getWaylineTree()
        const groups = res.groups || []
        groups.forEach(g => {
          if (Array.isArray(g.items)) {
            g.items.sort((a, b) => {
              const ta = a.recent_task_time ? new Date(a.recent_task_time).getTime() : 0
              const tb = b.recent_task_time ? new Date(b.recent_task_time).getTime() : 0
              return tb - ta
            })
          }
        })
        this.waylineTree = groups
        this.ensureDefaultExpand()
        this.autoSelectFirstIfNeeded()
      } catch (error) {
        console.error('加载航线树失败，回退到平铺列表:', error)
        await this.loadFlatWaylinesFallback()
      } finally {
        this.loading = false
      }
    },
    async loadFlatWaylinesFallback() {
      try {
        const response = await waylineApi.getWaylines({})
        const list = (response?.results || []).map(wayline => ({
          id: wayline.id,
          name: wayline.name,
          estimated_duration: wayline.estimated_duration
        }))
        this.waylineTree = list.length ? [{
          type: 'all',
          label: '全部航线',
          count: list.length,
          items: list
        }] : []
        this.ensureDefaultExpand()
        this.autoSelectFirstIfNeeded()
      } catch (e) {
        console.error('加载航线列表失败:', e)
        this.waylineTree = []
      }
    },
    
    handleSelect(wayline) {
      this.$emit('wayline-selected', wayline)
    },
    
    formatDuration(seconds) {
      const minutes = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${minutes}:${secs.toString().padStart(2, '0')}`
    },
    formatRecent(ts) {
      const date = new Date(ts)
      const now = new Date()
      const diff = Math.floor((now - date) / 1000)
      if (diff < 60) return '刚刚'
      if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
      if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
      return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
    },
    ensureDefaultExpand() {
      this.expandedMap = this.expandedMap || {}
      this.waylineTree.forEach(g => {
        if (this.expandedMap[g.type] === undefined) {
          this.expandedMap[g.type] = true
        }
      })
    },
    toggleGroup(type) {
      this.expandedMap = this.expandedMap || {}
      this.expandedMap[type] = !this.expandedMap[type]
    },
    autoSelectFirstIfNeeded() {
      if (!this.currentSelectedId) {
        const firstGroup = this.waylineTree[0]
        const firstItem = firstGroup && Array.isArray(firstGroup.items) ? firstGroup.items[0] : null
        if (firstItem) {
          this.$emit('wayline-selected', firstItem)
        }
      }
    }
  }
}
</script>

<style scoped>
.wayline-list-premium {
  background: rgba(26, 31, 58, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(0, 212, 255, 0.2);
  overflow: hidden;
}

/* 列表头部 */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 153, 255, 0.15) 100%);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
}

.list-title {
  font-size: 16px;
  font-weight: 700;
  color: #00d4ff;
  margin: 0;
}

.wayline-count {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 8px;
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  border-radius: 12px;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.4);
}

/* 航线项容器 */
.wayline-items {
  max-height: 400px;
  overflow-y: auto;
  padding: 12px;
}
/* 树分组样式 */
.tree-group {
  margin-bottom: 10px;
}
.tree-group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(0, 212, 255, 0.08);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  color: #e2e8f0;
}
.group-name {
  font-size: 13px;
  font-weight: 600;
}
.group-count {
  color: #94a3b8;
  font-size: 12px;
}
.toggle-icon {
  margin-left: auto;
  color: #64b5f6;
  font-size: 12px;
}
.tree-items {
  padding: 8px 2px 2px;
}

/* 自定义滚动条 */
.wayline-items::-webkit-scrollbar {
  width: 6px;
}

.wayline-items::-webkit-scrollbar-track {
  background: rgba(10, 14, 39, 0.4);
  border-radius: 3px;
}

.wayline-items::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  border-radius: 3px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #64748b;
}

.empty-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border: 2px solid rgba(0, 212, 255, 0.3);
  border-radius: 50%;
  font-size: 32px;
  margin-bottom: 16px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* 航线项 */
.wayline-item {
  position: relative;
  padding: 14px 16px;
  margin-bottom: 8px;
  background: rgba(10, 14, 39, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.wayline-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.wayline-item:hover {
  border-color: rgba(0, 212, 255, 0.4);
  background: rgba(10, 14, 39, 0.8);
  transform: translateX(4px);
}

.wayline-item:hover::before {
  opacity: 1;
}

.wayline-item.selected {
  border-color: #00d4ff;
  background: rgba(0, 212, 255, 0.15);
  box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3);
}

.wayline-item.selected::before {
  opacity: 1;
  width: 4px;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.8);
}

.wayline-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.wayline-id {
  font-size: 12px;
  color: #94a3b8;
  font-family: 'Courier New', monospace;
}

.wayline-duration {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #00d4ff;
  font-family: 'Courier New', monospace;
}

.duration-icon {
  font-size: 14px;
}

.wayline-name {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
  line-height: 1.4;
}
.recent-meta {
  margin-left: 6px;
  font-size: 12px;
  color: #94a3b8;
}

.wayline-item.selected .wayline-name {
  color: #00d4ff;
}

.select-indicator {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(0, 212, 255, 0.3);
  opacity: 0;
  transition: all 0.3s ease;
}

.wayline-item.selected .select-indicator {
  opacity: 1;
  background: #00d4ff;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.8);
  animation: selectPulse 2s ease-in-out infinite;
}

@keyframes selectPulse {
  0%, 100% {
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.8);
  }
  50% {
    box-shadow: 0 0 20px rgba(0, 212, 255, 1);
  }
}
</style>
