<template>
  <div class="alarm-list-premium">
    <!-- 搜索和筛选 -->
    <div class="search-filters-premium">
      <div class="search-wrapper">
        <div class="search-icon">🔍</div>
        <input 
          v-model="searchQuery"
          @input="handleSearch"
          placeholder="搜索告警内容..."
          class="search-input"
        />
      </div>
      
      <select v-model="statusFilter" @change="loadAlarms" class="filter-select">
        <option value="">全部状态</option>
        <option value="PENDING">待处理</option>
        <option value="PROCESSING">处理中</option>
        <option value="COMPLETED">已完成</option>
        <option value="IGNORED">已忽略</option>
      </select>

      <select v-model="detectTypeFilter" @change="loadAlarms" class="filter-select">
        <option value="">全部检测类型</option>
        <option value="rail">铁路</option>
        <option value="contactline">接触网</option>
        <option value="bridge">桥梁</option>
        <option value="protected_area">保护区</option>
      </select>

      <select v-model="waylineIdFilter" @change="loadAlarms" class="filter-select">
        <option value="">全部航线</option>
        <option v-for="wayline in waylines" :key="wayline.id" :value="wayline.wayline_id">
          {{ wayline.wayline_id }} - {{ wayline.name }}
        </option>
      </select>

      <button @click="clearAllAlarms" class="action-btn delete-btn clear-all-btn">
        清空记录
      </button>
    </div>
    
    <!-- 告警表格 -->
    <div class="table-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <table v-else class="alarm-table">
        <thead>
          <tr>
            <th width="80">ID</th>
            <th width="100">航线ID</th>
            <th width="150">航线名称</th>
            <th width="180">时间</th>
            <th width="120">类型</th>
            <th>描述</th>
            <th width="150">位置</th>
            <th width="100">状态</th>
            <th width="200">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredAlarms.length === 0">
            <td colspan="9" class="empty-row">暂无告警数据</td>
          </tr>
          <tr v-for="alarm in filteredAlarms" :key="alarm.id" class="alarm-row">
            <td>
              <span class="id-badge">{{ alarm.id }}</span>
            </td>
            <td>{{ getWaylineId(alarm) }}</td>
            <td>{{ getWaylineName(alarm) }}</td>
            <td>
              <span class="datetime-text">{{ formatDate(alarm.created_at) }}</span>
            </td>
            <td>
              <span class="category-badge" :class="getCategoryClass(alarm.category_name)">
                {{ alarm.category_name || '未分类' }}
              </span>
            </td>
            <td class="description-cell">{{ alarm.content }}</td>
            <td>坐标({{ alarm.latitude || '--' }}, {{ alarm.longitude || '--' }})</td>
            <td>
              <span class="status-badge" :class="`status-${alarm.status.toLowerCase()}`">
                {{ getStatusText(alarm.status) }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button @click="viewAlarmDetail(alarm)" class="action-btn view-btn">
                  查看
                </button>
                <button @click="updateAlarmStatus(alarm)" class="action-btn update-btn">
                  更新
                </button>
                <button @click="deleteAlarm(alarm.id)" class="action-btn delete-btn">
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
        显示 {{ Math.min((currentPage - 1) * pageSize + 1, totalAlarms) }} - {{ Math.min(currentPage * pageSize, totalAlarms) }} 条，共 {{ totalAlarms }} 条
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
          :max="Math.ceil(totalAlarms / pageSize)"
        />
        <span class="pagination-separator">/</span>
        <span class="total-pages">{{ Math.ceil(totalAlarms / pageSize) || 1 }}</span>
        <button @click="handlePageChange(currentPage + 1)" :disabled="currentPage >= Math.ceil(totalAlarms / pageSize)" class="pagination-btn">
          ›
        </button>
      </div>
    </div>
    
    <!-- 状态更新对话框 -->
    <div v-if="showStatusDialog" class="modal-overlay" @click.self="showStatusDialog = false">
      <div class="modal-premium">
        <div class="modal-header">
          <h3 class="modal-title">更新告警状态</h3>
          <button @click="showStatusDialog = false" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div class="info-row">
            <span class="info-label">告警ID:</span>
            <span class="info-value">{{ currentAlarm?.id }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">告警描述:</span>
            <span class="info-value">{{ currentAlarm?.content }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">当前状态:</span>
            <span class="status-badge" :class="`status-${currentAlarm?.status.toLowerCase()}`">
              {{ getStatusText(currentAlarm?.status) }}
            </span>
          </div>
          <div class="form-group">
            <label class="form-label">更新为</label>
            <select v-model="newAlarmStatus" class="form-select">
              <option value="PENDING">待处理</option>
              <option value="PROCESSING">处理中</option>
              <option value="COMPLETED">已完成</option>
              <option value="IGNORED">已忽略</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showStatusDialog = false" class="modal-btn secondary-btn">取消</button>
          <button @click="confirmStatusUpdate" class="modal-btn primary-btn">确定</button>
        </div>
      </div>
    </div>
    
    <!-- 详情对话框 -->
    <div v-if="showDetailDialog" class="modal-overlay" @click.self="showDetailDialog = false">
      <div class="modal-premium detail-modal">
        <div class="modal-header">
          <h3 class="modal-title">告警详情</h3>
          <button @click="showDetailDialog = false" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">告警ID</span>
              <span class="detail-value">{{ currentAlarm?.id }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">告警类型</span>
              <span class="category-badge" :class="getCategoryClass(currentAlarm?.category_name)">
                {{ currentAlarm?.category_name || '未分类' }}
              </span>
            </div>
            <div class="detail-item full-width">
              <span class="detail-label">告警描述</span>
              <span class="detail-value">{{ currentAlarm?.content }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">报警位置</span>
              <span class="detail-value">坐标({{ currentAlarm?.latitude }}, {{ currentAlarm?.longitude }})</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">报警时间</span>
              <span class="detail-value">{{ formatDate(currentAlarm?.created_at) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">告警状态</span>
              <span class="status-badge" :class="`status-${currentAlarm?.status.toLowerCase()}`">
                {{ getStatusText(currentAlarm?.status) }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">航线信息</span>
              <span class="detail-value">{{ getWaylineName(currentAlarm) }} ({{ getWaylineId(currentAlarm) }})</span>
            </div>
            <div v-if="currentAlarm?.image_url" class="detail-item full-width">
              <span class="detail-label">报警图片</span>
              <div class="alarm-image">
                <img :src="currentAlarm.image_url" alt="告警图片" />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showDetailDialog = false" class="modal-btn secondary-btn">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import alarmApi from '../api/alarmApi.js'
import waylineApi from '../api/waylineApi.js'

export default {
  name: 'AlarmList',
  data() {
    return {
      alarms: [],
      waylines: [],
      filteredAlarms: [],
      searchQuery: '',
      statusFilter: '',
      detectTypeFilter: '',
      waylineIdFilter: '',
      loading: false,
      currentPage: 1,
      pageSize: 10,
      totalAlarms: 0,
      showStatusDialog: false,
      showDetailDialog: false,
      currentAlarm: null,
      newAlarmStatus: ''
    }
  },
  mounted() {
    this.loadAlarms()
    this.loadWaylines()
  },
  methods: {
    async loadAlarms() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize
        }
        if (this.searchQuery) params.search = this.searchQuery
        if (this.statusFilter) params.status = this.statusFilter
        if (this.detectTypeFilter) params.detect_type = this.detectTypeFilter
        if (this.waylineIdFilter) params.wayline_id = this.waylineIdFilter
        
        const response = await alarmApi.getAlarms(params)
        const list = response.results || response
        // 处理图片URL和分类名称
        this.alarms = list.map(item => ({
          ...item,
          image_url: item.image_signed_url || item.image_url,
          category_name: item.category_details?.name || item.category_name || '未分类'
        }))
        this.totalAlarms = response.count || this.alarms.length
        this.filteredAlarms = this.alarms
      } catch (error) {
        console.error('加载告警失败:', error)
      } finally {
        this.loading = false
      }
    },
    async loadWaylines() {
      try {
        const response = await waylineApi.getWaylines()
        this.waylines = response.results || response
      } catch (error) {
        console.error('加载航线失败:', error)
      }
    },
    handleSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.currentPage = 1
        this.loadAlarms()
      }, 300)
    },
    handlePageChange(page) {
      if (page < 1 || page > Math.ceil(this.totalAlarms / this.pageSize)) return
      this.currentPage = page
      this.loadAlarms()
    },
    formatDate(dateString) {
      if (!dateString) return '--'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    getWaylineId(alarm) {
      return alarm.wayline_details?.wayline_id || alarm.wayline_id || '--'
    },
    getWaylineName(alarm) {
      return alarm.wayline_details?.name || alarm.wayline?.name || '未知航线'
    },
    getStatusText(status) {
      const statusMap = {
        'PENDING': '待处理',
        'PROCESSING': '处理中',
        'COMPLETED': '已完成',
        'IGNORED': '已忽略'
      }
      return statusMap[status] || status
    },
    getCategoryClass(category) {
      if (!category) return ''
      return `category-${category.toLowerCase().replace(/\s+/g, '-')}`
    },
    viewAlarmDetail(alarm) {
      this.currentAlarm = alarm
      this.showDetailDialog = true
    },
    updateAlarmStatus(alarm) {
      this.currentAlarm = alarm
      this.newAlarmStatus = alarm.status
      this.showStatusDialog = true
    },
    async confirmStatusUpdate() {
      try {
        await alarmApi.patchAlarm(this.currentAlarm.id, { status: this.newAlarmStatus })
        this.showStatusDialog = false
        this.loadAlarms()
      } catch (error) {
        console.error('更新状态失败:', error)
      }
    },
    async deleteAlarm(id) {
      if (!confirm('确定要删除这条告警吗？')) return
      try {
        await alarmApi.deleteAlarm(id)
        this.loadAlarms()
      } catch (error) {
        console.error('删除告警失败:', error)
      }
    }
  }
}
</script>

<style scoped>
/* 主容器 */
.alarm-list-premium {
  background: rgba(10, 15, 35, 0.75);
  backdrop-filter: blur(20px) saturate(180%);
  border-radius: 16px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  overflow: hidden;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.5),
    0 0 40px rgba(59, 130, 246, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  padding: 28px 36px;
  animation: cardSlideIn 0.5s ease-out;
}

@keyframes cardSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 搜索筛选 */
.search-filters-premium {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-wrapper {
  flex: 1;
  min-width: 250px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(10, 14, 39, 0.6);
  border-radius: 10px;
  border: 1px solid rgba(239, 68, 68, 0.2);
  transition: all 0.3s ease;
}

.search-wrapper:focus-within {
  border-color: #ef4444;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
}

.search-icon {
  font-size: 16px;
  opacity: 0.7;
}

.search-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: #e2e8f0;
  font-size: 14px;
}

.search-input::placeholder {
  color: #64748b;
}

.filter-select {
  padding: 12px 16px;
  background: rgba(10, 14, 39, 0.6);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 10px;
  color: #e2e8f0;
  font-size: 14px;
  outline: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-select:focus {
  border-color: #ef4444;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
}

/* 表格 */
.table-container {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(239, 68, 68, 0.1);
}

.alarm-table {
  width: 100%;
  border-collapse: collapse;
}

.alarm-table thead tr {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%);
}

.alarm-table th {
  padding: 14px 16px;
  text-align: left;
  color: #ef4444;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid rgba(239, 68, 68, 0.3);
}

.alarm-table tbody tr {
  border-bottom: 1px solid rgba(239, 68, 68, 0.1);
  transition: all 0.3s ease;
}

.alarm-table tbody tr:hover {
  background: rgba(239, 68, 68, 0.05);
}

.alarm-table td {
  padding: 14px 16px;
  color: #e2e8f0;
  font-size: 13px;
}

.id-badge {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(239, 68, 68, 0.15);
  border-radius: 6px;
  color: #ef4444;
  font-weight: 600;
  font-size: 12px;
}

.datetime-text {
  color: #94a3b8;
  font-size: 12px;
}

.category-badge,
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.status-pending {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.status-processing {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.status-completed {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.status-ignored {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.description-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-row {
  text-align: center;
  padding: 40px;
  color: #64748b;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 6px;
}

.action-btn {
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.view-btn:hover {
  background: rgba(59, 130, 246, 0.3);
  transform: translateY(-1px);
}

.update-btn {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.update-btn:hover {
  background: rgba(16, 185, 129, 0.3);
  transform: translateY(-1px);
}

.delete-btn {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.3);
  transform: translateY(-1px);
}

.clear-all-btn {
  margin-left: auto;
  padding: 8px 16px;
  font-weight: 600;
  border: 1px solid rgba(239, 68, 68, 0.4);
  background: rgba(239, 68, 68, 0.15);
}

.clear-all-btn:hover {
  background: rgba(239, 68, 68, 0.3);
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
}

/* 分页器 - 复用UserManagement样式 */
.pagination-premium {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.pagination-info {
  color: #94a3b8;
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination-btn:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
  transform: translateY(-1px);
}

.pagination-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-input {
  width: 45px;
  height: 32px;
  text-align: center;
  background: rgba(26, 31, 58, 0.8);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: #e2e8f0;
  font-size: 13px;
  outline: none;
}

.page-input:focus {
  border-color: #ef4444;
}

.pagination-separator {
  color: #64748b;
  font-size: 14px;
}

.total-pages {
  color: #94a3b8;
  font-size: 14px;
}

/* 模态框 - 复用UserManagement样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(10, 14, 39, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.modal-premium {
  background: rgba(26, 31, 58, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(239, 68, 68, 0.3);
  box-shadow: 0 16px 64px rgba(0, 0, 0, 0.5), 0 0 40px rgba(239, 68, 68, 0.2);
  width: 100%;
  max-width: 500px;
  animation: modalSlideIn 0.3s ease;
}

.detail-modal {
  max-width: 700px;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
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
  padding: 20px 24px;
  border-bottom: 1px solid rgba(239, 68, 68, 0.2);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #ef4444;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.modal-close:hover {
  background: rgba(239, 68, 68, 0.3);
  transform: rotate(90deg);
}

.modal-body {
  padding: 24px;
}

.info-row {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-label {
  color: #94a3b8;
  font-size: 14px;
  font-weight: 500;
  min-width: 80px;
}

.info-value {
  color: #e2e8f0;
  font-size: 14px;
  flex: 1;
}

.form-group {
  margin-top: 20px;
}

.form-label {
  display: block;
  color: #94a3b8;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.form-select {
  width: 100%;
  padding: 10px 14px;
  background: rgba(10, 14, 39, 0.6);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

.form-select:focus {
  border-color: #ef4444;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(239, 68, 68, 0.1);
}

.modal-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.secondary-btn {
  background: rgba(100, 116, 139, 0.2);
  color: #94a3b8;
  border: 1px solid rgba(100, 116, 139, 0.3);
}

.secondary-btn:hover {
  background: rgba(100, 116, 139, 0.3);
}

.primary-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #fff;
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.3);
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.5);
}

/* 详情网格 */
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  color: #94a3b8;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  color: #e2e8f0;
  font-size: 14px;
}

.alarm-image {
  margin-top: 8px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.alarm-image img {
  width: 100%;
  height: auto;
  display: block;
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
  border: 3px solid rgba(239, 68, 68, 0.2);
  border-top-color: #ef4444;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>