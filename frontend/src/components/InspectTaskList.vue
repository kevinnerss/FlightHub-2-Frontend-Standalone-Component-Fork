<template>
  <div class="inspect-task-list-premium">
    <!-- 头部 -->
    <div class="list-header">
      <h2 class="list-title">巡检任务列表</h2>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="search-filters-premium">
      <div class="search-wrapper">
        <div class="search-icon">🔍</div>
        <input 
          v-model="searchQuery"
          @input="handleSearch"
          placeholder="搜索任务ID、航线名称..."
          class="search-input"
        />
      </div>
      
      <select v-model="statusFilter" @change="loadTasks" class="filter-select">
        <option value="">全部状态</option>
        <option value="pending">待检测</option>
        <option value="processing">检测中</option>
        <option value="done">已完成</option>
        <option value="failed">失败</option>
      </select>
      
      <select v-model="waylineFilter" @change="loadTasks" class="filter-select">
        <option value="">全部航线</option>
        <option v-for="wayline in waylines" :key="wayline.id" :value="wayline.id">
          {{ wayline.name }}
        </option>
      </select>

      <!-- 🔥 新增：检测类型筛选 -->
      <select v-model="categoryFilter" @change="loadTasks" class="filter-select">
        <option value="">全部类型</option>
        <option value="rail">🛤️ 铁路检测</option>
        <option value="contactline">⚡ 接触网检测</option>
        <option value="bridge">🌉 桥梁检测</option>
        <option value="protected_area">🛡️ 保护区检测</option>
      </select>
    </div>
    
    <!-- 任务表格 -->
    <div class="table-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <table v-else class="task-table">
        <thead>
          <tr>
            <th width="80">ID</th>
            <th width="250">外部任务ID</th>
            <th width="140">执行设备</th> <!-- 🔥 新增列 -->
            <!-- 🔥 选了检测类型时显示航线和检测类型列 -->
            <th v-if="categoryFilter" width="180">航线名称</th>
            <th v-if="categoryFilter" width="120">检测类型</th>
            <th width="200">创建时间</th>
            <th width="120">状态</th>
            <th width="100">已清理</th>
            <th width="280">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredTasks.length === 0">
            <td :colspan="categoryFilter ? 9 : 7" class="empty-row">暂无任务数据</td>
          </tr>
          <tr v-for="task in filteredTasks" :key="task.id" class="task-row">
            <td>
              <span class="id-badge">{{ task.id }}</span>
            </td>
            <td>{{ task.external_task_id || '--' }}</td>
            <td>
              <span class="device-badge" :class="{'has-sn': task.device_sn}">
                {{ task.device_sn || '--' }}
              </span>
            </td>
            <!-- 🔥 选了检测类型时显示子任务的航线和检测类型 -->
            <td v-if="categoryFilter">{{ task.wayline_details?.name || '--' }}</td>
            <td v-if="categoryFilter">
              <span class="category-badge">
                {{ task.detect_category_name || getCategoryName(task.detect_category) || '未设置' }}
              </span>
            </td>
            <td>
              <span class="datetime-text">{{ formatDate(task.created_at) }}</span>
            </td>
            <td>
              <span class="status-badge" :class="`status-${task.detect_status}`">
                {{ getStatusText(task.detect_status) }}
              </span>
            </td>
            <td>
              <span class="clean-badge" :class="task.is_cleaned ? 'cleaned' : 'not-cleaned'">
                {{ task.is_cleaned ? '已清理' : '未清理' }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <!-- 🔥 如果是子任务，显示回放按钮 -->
                <button 
                  v-if="categoryFilter && task.detect_status === 'done'"
                  @click="playbackSubTask(task)" 
                  class="action-btn playback-btn"
                >
                  回放
                </button>
                <button v-else @click="viewTaskDetail(task)" class="action-btn view-btn">
                  查看
                </button>
                <!-- 父任务才显示查看子任务按钮 -->
                <button v-if="!categoryFilter" @click="viewSubTasks(task)" class="action-btn subtask-btn">
                  查看子任务
                </button>
                <button @click="deleteTask(task.id)" class="action-btn delete-btn">
                  删除
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 分页器 -->
    <div class="pagination-premium">
      <div class="pagination-info">
        显示 {{ Math.min((currentPage - 1) * pageSize + 1, totalTasks) }} - {{ Math.min(currentPage * pageSize, totalTasks) }} 条，共 {{ totalTasks }} 条
      </div>
      <div class="pagination-controls">
        <button @click="handlePageChange(currentPage - 1)" :disabled="currentPage === 1" class="pagination-btn">
          ‹
        </button>
        <input 
          type="number" 
          :value="currentPage"
          @change="handlePageChange(Number($event.target.value))"
          class="page-input"
          min="1"
          :max="Math.ceil(totalTasks / pageSize)"
        />
        <span class="pagination-separator">/</span>
        <span class="total-pages">{{ Math.ceil(totalTasks / pageSize) || 1 }}</span>
        <button @click="handlePageChange(currentPage + 1)" :disabled="currentPage >= Math.ceil(totalTasks / pageSize)" class="pagination-btn">
          ›
        </button>
      </div>
    </div>
    
    <!-- 父任务详情对话框 -->
    <div v-if="showDetailDialog" class="modal-overlay" @click.self="showDetailDialog = false">
      <div class="modal-premium detail-modal">
        <div class="modal-header">
          <h3 class="modal-title">父任务详情</h3>
          <button @click="showDetailDialog = false" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">任务ID</span>
              <span class="detail-value">{{ currentTask?.id }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">外部任务ID</span>
              <span class="detail-value">{{ currentTask?.external_task_id || '--' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">检测类型</span>
              <span class="detail-value">--（父任务无检测类型）</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">航线</span>
              <span class="detail-value">--（父任务无航线）</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">创建时间</span>
              <span class="detail-value">{{ formatDate(currentTask?.created_at) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">检测状态</span>
              <span class="status-badge" :class="`status-${currentTask?.detect_status}`">
                {{ getStatusText(currentTask?.detect_status) }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">媒体清理状态</span>
              <span class="clean-badge" :class="currentTask?.is_cleaned ? 'cleaned' : 'not-cleaned'">
                {{ currentTask?.is_cleaned ? '已清理' : '未清理' }}
              </span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showDetailDialog = false" class="modal-btn secondary-btn">关闭</button>
        </div>
      </div>
    </div>

    <!-- 子任务对话框 -->
    <div v-if="showSubTaskDialog" class="modal-overlay" @click.self="showSubTaskDialog = false">
      <div class="modal-premium detail-modal">
        <div class="modal-header">
          <h3 class="modal-title">子任务列表 - 父任务 {{ currentTask?.external_task_id || currentTask?.id }}</h3>
          <button @click="showSubTaskDialog = false" class="modal-close">×</button>
        </div>
        <div class="modal-body subtask-body">
          <div v-if="!subTasks.length" class="empty-row">暂无子任务</div>
          <table v-else class="task-table subtask-table">
            <thead>
              <tr>
                <th width="80">ID</th>
                <th width="180">外部任务ID / 文件夹</th>
                <th width="120">执行设备</th> <!-- 🔥 新增 -->
                <th width="140">航线名称</th>
                <th width="120">检测类型</th>
                <th width="160">开始时间</th>
                <th width="160">完成时间</th>
                <th width="100">状态</th>
                <th width="120">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in subTasks" :key="item.id" class="task-row">
                <td><span class="id-badge">{{ item.id }}</span></td>
                <td>{{ item.external_task_id || '--' }}</td>
                <td><span class="device-badge">{{ item.device_sn || '--' }}</span></td> <!-- 🔥 新增 -->
                <td>{{ item.wayline_details?.name || '--' }}</td>
                <td>
                  <span class="category-badge">
                    {{ item.detect_category_name || '未设置' }}
                  </span>
                </td>
                <td><span class="datetime-text">{{ formatDate(item.started_at) }}</span></td>
                <td><span class="datetime-text">{{ formatDate(item.finished_at) }}</span></td>
                <td>
                  <span class="status-badge" :class="`status-${item.detect_status}`">
                    {{ getStatusText(item.detect_status) }}
                  </span>
                </td>
                <td>
                  <button 
                    v-if="item.detect_status === 'done'"
                    @click="playbackSubTask(item)" 
                    class="action-btn playback-btn"
                  >
                    回放
                  </button>
                  <span v-else class="text-muted">未完成</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="modal-footer">
          <button @click="showSubTaskDialog = false" class="modal-btn secondary-btn">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import inspectTaskApi from '../api/inspectTaskApi'
import waylineApi from '../api/waylineApi'
import { ElMessage } from 'element-plus'

export default {
  name: 'InspectTaskList',
  data() {
    return {
      tasks: [],
      waylines: [],
      categories: [], // 检测类型列表
      filteredTasks: [],
      loading: false,
      searchQuery: '',
      statusFilter: '',
      waylineFilter: '',
      categoryFilter: '', // 🔥 新增：检测类型筛选
      currentPage: 1,
      pageSize: 10,
      totalTasks: 0,
      showDetailDialog: false,
      currentTask: null,
      showSubTaskDialog: false,
      subTasks: []
    }
  },
  async mounted() {
    await this.loadWaylines()
    await this.loadTasks()
  },
  methods: {
    async loadWaylines() {
      try {
        const response = await waylineApi.getWaylines({})
        this.waylines = response?.results || []
      } catch (error) {
        console.error('加载航线列表失败:', error)
      }
    },
    
    async loadTasks() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize
        }
        
        // 🔥 检测类型筛选逻辑：如果选了类型，只显示子任务
        if (this.categoryFilter) {
          // 先获取检测类型的 ID
          const alarmApi = await import('../api/alarmApi')
          const categoryRes = await alarmApi.default.getAlarmCategories({ page_size: 100 })
          const categories = Array.isArray(categoryRes) ? categoryRes : (categoryRes?.results || [])
          const normalizeCode = (code) => {
            const v = (code || '').toString().toLowerCase().trim()
            if (v === 'rail' || v === 'track') return 'rail'
            if (v === 'contactline' || v === 'catenary' || v === 'overhead' || v === 'insulator' || v === 'pole') return 'contactline'
            if (v === 'bridge') return 'bridge'
            if (v === 'protected_area' || v === 'protection_zone' || v === 'protection_area') return 'protected_area'
            return v
          }
          const targetCategory = categories.find(c => normalizeCode(c.code) === this.categoryFilter)
          
          if (targetCategory) {
            params.detect_category = targetCategory.id
            params.parent_task__isnull = false // 🔥 只查询子任务
          }
        } else {
          // 没选类型，只显示父任务
          params.parent_task__isnull = true
        }
        
        if (this.statusFilter) {
          params.detect_status = this.statusFilter
        }
        
        if (this.waylineFilter) {
          params.wayline = this.waylineFilter
        }
        
        if (this.searchQuery) {
          params.search = this.searchQuery
        }
        
        const response = await inspectTaskApi.getInspectTasks(params)
        const allTasks = response?.results || []
        
        // 🔥 根据是否选了检测类型决定显示父任务还是子任务
        if (this.categoryFilter) {
          // 选了类型，显示子任务
          this.tasks = allTasks
        } else {
          // 没选类型，显示父任务
          this.tasks = allTasks.filter(item => !item.parent_task)
        }
        
        this.totalTasks = response?.count || this.tasks.length
        this.filteredTasks = this.tasks
      } catch (error) {
        console.error('加载巡检任务失败:', error)
        ElMessage.error('加载巡检任务失败')
      } finally {
        this.loading = false
      }
    },
    
    handleSearch() {
      this.currentPage = 1
      this.loadTasks()
    },
    
    handlePageChange(page) {
      if (page >= 1 && page <= Math.ceil(this.totalTasks / this.pageSize)) {
        this.currentPage = page
        this.loadTasks()
      }
    },
    
    viewTaskDetail(task) {
      this.currentTask = task
      this.showDetailDialog = true
    },

    async viewSubTasks(task) {
      try {
        const res = await inspectTaskApi.getSubTasks(task.id)
        const list = Array.isArray(res) ? res : (res?.results || [])
        this.subTasks = list
        this.currentTask = task
        this.showSubTaskDialog = true
      } catch (error) {
        console.error('加载子任务失败:', error)
        ElMessage.error('加载子任务失败')
      }
    },
    
    async deleteTask(taskId) {
      if (!confirm('确定要删除这个巡检任务吗？')) {
        return
      }
      
      try {
        await inspectTaskApi.deleteInspectTask(taskId)
        ElMessage.success('删除成功')
        await this.loadTasks()
      } catch (error) {
        console.error('删除任务失败:', error)
        ElMessage.error('删除任务失败')
      }
    },
    
    playbackSubTask(subTask) {
      // 跳转到轮播检测页，并传递任务信息
      this.$router.push({
        name: 'CarouselDetection',
        query: {
          playback: subTask.external_task_id || subTask.id
        }
      })
      ElMessage.success(`开始回放任务: ${subTask.external_task_id || subTask.id}`)
    },
    
    getWaylineName(task) {
      return task?.wayline_details?.name || '--'
    },
    
    // 🔥 新增：获取检测类型名称
    getCategoryName(categoryValue) {
      if (!categoryValue) return ''
      if (typeof categoryValue !== 'string') return ''
      const categoryMap = {
        'rail': '铁路检测',
        'contactline': '接触网检测',
        'bridge': '桥梁检测',
        'protected_area': '保护区检测',
        'catenary': '接触网检测',
        'overhead': '接触网检测',
        'insulator': '接触网检测',
        'pole': '接触网检测',
        'protection_zone': '保护区检测'
      }
      return categoryMap[categoryValue] || ''
    },
    
    getStatusText(status) {
      const statusMap = {
        'pending': '待检测',
        'processing': '检测中',
        'done': '已完成',
        'failed': '失败'
      }
      return statusMap[status] || status
    },
    
    formatDate(dateString) {
      if (!dateString) return '--'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
/* 主容器 */
.inspect-task-list-premium {
  background: rgba(26, 31, 58, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  padding: 24px;
}

/* 列表头部 */
.list-header {
  margin-bottom: 20px;
}

.list-title {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

/* 搜索和筛选区域 */
.search-filters-premium {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-wrapper {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
}

.search-input {
  width: 100%;
  padding: 10px 14px 10px 40px;
  background: rgba(10, 14, 39, 0.6);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 14px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-select {
  padding: 10px 14px;
  background: rgba(10, 14, 39, 0.6);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 表格容器 */
.table-container {
  overflow-x: auto;
  margin-bottom: 20px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(59, 130, 246, 0.2);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 表格样式 */
.task-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 8px;
}

.task-table thead tr {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.15) 100%);
}

.task-table th {
  padding: 14px 12px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #3b82f6;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.task-table th:first-child {
  border-radius: 8px 0 0 8px;
}

.task-table th:last-child {
  border-radius: 0 8px 8px 0;
}

.task-row {
  background: rgba(10, 14, 39, 0.4);
  transition: all 0.3s ease;
}

.task-row:hover {
  background: rgba(10, 14, 39, 0.6);
  transform: translateX(2px);
}

.task-table td {
  padding: 14px 12px;
  color: #cbd5e1;
  font-size: 13px;
  border-top: 1px solid rgba(59, 130, 246, 0.1);
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

.task-table td:first-child {
  border-left: 1px solid rgba(59, 130, 246, 0.1);
  border-radius: 8px 0 0 8px;
}

.task-table td:last-child {
  border-right: 1px solid rgba(59, 130, 246, 0.1);
  border-radius: 0 8px 8px 0;
}

.empty-row {
  text-align: center;
  padding: 40px 20px !important;
  color: #64748b;
}

/* 徽章样式 */
.id-badge {
  display: inline-block;
  padding: 4px 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 6px;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  font-family: 'Courier New', monospace;
}

.status-badge {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
}

.status-pending {
  background: rgba(234, 179, 8, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(234, 179, 8, 0.3);
}

.status-processing {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
  animation: statusPulse 2s ease-in-out infinite;
}

.status-done {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.status-failed {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

@keyframes statusPulse {
  0%, 100% {
    box-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
  }
  50% {
    box-shadow: 0 0 15px rgba(59, 130, 246, 0.8);
  }
}

.category-badge {
  display: inline-block;
  padding: 5px 12px;
  background: rgba(139, 92, 246, 0.2);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.clean-badge {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.clean-badge.cleaned {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.clean-badge.not-cleaned {
  background: rgba(100, 116, 139, 0.2);
  color: #94a3b8;
  border: 1px solid rgba(100, 116, 139, 0.3);
}

.datetime-text {
  font-family: 'Courier New', monospace;
  color: #94a3b8;
  font-size: 12px;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.view-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #fff;
}

.view-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  transform: translateY(-1px);
}

.sync-btn {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: #fff;
}

.sync-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
  transform: translateY(-1px);
}

.detect-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
}

.detect-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  transform: translateY(-1px);
}

.delete-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #fff;
}

.delete-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
  transform: translateY(-1px);
}

.playback-btn {
  background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
  color: #fff;
}

.playback-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(20, 184, 166, 0.4);
  transform: translateY(-1px);
}

.subtask-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #fff;
}

.subtask-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
  transform: translateY(-1px);
}

.text-muted {
  color: #64748b;
  font-size: 12px;
}

.device-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  color: #94a3b8; /* Default muted color for '--' */
  background: rgba(148, 163, 184, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.device-badge.has-sn {
  color: #c084fc;
  border-color: rgba(192, 132, 252, 0.3);
  background: rgba(192, 132, 252, 0.1);
}

/* 分页器 */
.pagination-premium {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.pagination-info {
  color: #94a3b8;
  font-size: 13px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 6px;
  color: #3b82f6;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.3);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.pagination-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-input {
  width: 50px;
  padding: 6px 8px;
  background: rgba(10, 14, 39, 0.6);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 6px;
  color: #e2e8f0;
  text-align: center;
  font-size: 13px;
}

.page-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.pagination-separator {
  color: #64748b;
  font-size: 14px;
}

.total-pages {
  color: #94a3b8;
  font-size: 13px;
  min-width: 30px;
  text-align: center;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-premium {
  background: rgba(26, 31, 58, 0.95);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 28px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.modal-body {
  padding: 28px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 14px;
  color: #e2e8f0;
}

.prefix-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.prefix-item {
  padding: 6px 12px;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 6px;
  color: #60a5fa;
  font-size: 12px;
  font-family: 'Courier New', monospace;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 28px;
  border-top: 1px solid rgba(59, 130, 246, 0.2);
}

.modal-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.secondary-btn {
  background: rgba(100, 116, 139, 0.2);
  color: #94a3b8;
  border: 1px solid rgba(100, 116, 139, 0.3);
}

.secondary-btn:hover {
  background: rgba(100, 116, 139, 0.3);
}
</style>
