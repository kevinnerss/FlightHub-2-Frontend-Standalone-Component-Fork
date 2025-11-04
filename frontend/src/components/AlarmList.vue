<template>
  <div class="alarm-list-container tech-border glass-effect">
    <div class="header-actions">
      <h2 class="title text-blue-400 tech-title">告警信息列表</h2>
    </div>
    
    <!-- 搜索和筛选 -->
        <div class="search-filters mb-4">
          <el-input
            v-model="searchQuery"
            placeholder="搜索告警内容"
            prefix-icon="el-icon-search"
            clearable
            @clear="loadAlarms"
            class="search-input tech-input"
            id="alarm-search-input"
          />
          <el-select
            v-model="statusFilter"
            placeholder="筛选状态"
            clearable
            @change="loadAlarms"
            class="status-filter tech-select"
            id="alarm-status-select"
            :style="{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#d1d5db' }"
          >
            <el-option label="全部" value="" />
            <el-option label="待处理" value="PENDING" />
            <el-option label="处理中" value="PROCESSING" />
            <el-option label="已完成" value="COMPLETED" />
            <el-option label="已忽略" value="IGNORED" />
          </el-select>
          <el-select
            v-model="waylineIdFilter"
            placeholder="筛选航线"
            clearable
            @change="loadAlarms"
            class="wayline-filter tech-select"
            id="alarm-wayline-select"
            :style="{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#d1d5db' }"
          >
            <el-option label="全部" value="" />
            <el-option
              v-for="wayline in waylines"
              :key="wayline.id"
              :label="`${wayline.wayline_id} - ${wayline.name}`"
              :value="wayline.wayline_id"
            />
          </el-select>
        </div>
    
    <!-- 告警列表 -->
    <el-table
      v-loading="loading"
      :data="filteredAlarms"
      style="width: 100%"
      border
      empty-text="暂无告警数据"
      :fit="true"
      :scroll-x="'max-content'"
      class="tech-table"
    >
      <el-table-column prop="id" label="告警ID" min-width="80" />
      <el-table-column label="航线ID" min-width="100">
        <template #default="{row}">
          {{ getWaylineId(row) }}
        </template>
      </el-table-column>
      
      <el-table-column label="航线名称" min-width="150">
        <template #default="{row}">
          {{ getWaylineName(row) }}
        </template>
      </el-table-column>
      
      <el-table-column prop="created_at" label="报警日期时间" min-width="180">
        <template #default="{row}">
          {{ formatDate(row?.created_at || '') }}
        </template>
      </el-table-column>
      
      <el-table-column prop="category_name" label="报警类型" min-width="120">
        <template #default="{row}">
          <el-tag :type="getCategoryType(row?.category_name || '')" class="tech-badge-glow">
            {{ row?.category_name || '未分类' }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="content" label="告警描述" min-width="200" show-overflow-tooltip />
      
      <!-- 移除表格中的图片显示，改为在详情弹窗中显示 -->
      
      <el-table-column prop="location" label="报警位置" min-width="150">
        <template #default="{row}">
          坐标({{ row?.latitude || '--' }}, {{ row?.longitude || '--' }})
        </template>
      </el-table-column>
      
      <el-table-column prop="status" label="状态" min-width="100">
        <template #default="{row}">
          <el-tag 
            :type="getStatusType(row?.status || '')" 
            class="tech-badge-glow" 
            :class="`alarm-status-${(row?.status || '').toLowerCase()}`"
          >
            {{ getStatusText(row?.status || '') }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column label="操作" min-width="180">
        <template #default="{row}">
          <el-button size="small" class="tech-button" @click="viewAlarmDetail(row)">查看</el-button>
          <el-button size="small" type="primary" class="tech-button-primary" @click="updateAlarmStatus(row)">更新状态</el-button>
          <el-button size="small" type="danger" class="tech-button-danger" @click="deleteAlarm(row?.id || 0)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination-container tech-pagination">
      <el-pagination
        v-model="currentPage"
        :page-size="pageSize"
        :total="totalAlarms"
        layout="total, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        background
        class="tech-pagination"
      />
    </div>
    
    <!-- 状态更新对话框 -->
    <el-dialog
      title="更新告警状态"
      v-model="showStatusDialog"
      width="400px"
      class="tech-dialog glass-effect"
    >
      <div class="status-dialog-content">
        <h4 class="text-blue-400">告警信息</h4>
        <p><strong class="text-gray-300">告警ID:</strong> <span class="text-blue-300">{{ currentAlarm?.id }}</span></p>
        <p><strong class="text-gray-300">告警描述:</strong> <span class="text-blue-300">{{ currentAlarm?.content }}</span></p>
        <p><strong class="text-gray-300">当前状态:</strong> 
          <el-tag :type="getStatusType(currentAlarm?.status || '')" class="tech-badge-glow">
            {{ getStatusText(currentAlarm?.status || '') }}
          </el-tag>
        </p>
        
        <h4 class="text-blue-400" style="margin-top: 20px;">更新为</h4>
        <el-select v-model="newAlarmStatus" placeholder="请选择新状态" style="width: 100%;" class="tech-select">
          <el-option label="待处理" value="PENDING" />
          <el-option label="处理中" value="PROCESSING" />
          <el-option label="已完成" value="COMPLETED" />
          <el-option label="已忽略" value="IGNORED" />
        </el-select>
      </div>
      
      <div slot="footer" class="dialog-footer">
        <el-button class="tech-button" @click="showStatusDialog = false">取消</el-button>
        <el-button type="primary" class="tech-button-primary" @click="confirmStatusUpdate">确定</el-button>
      </div>
    </el-dialog>
    
    <!-- 告警详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      title="告警详情"
      width="700px"
      :close-on-click-modal="false"
      class="tech-dialog glass-effect"
    >
      <div class="alarm-detail-container">
        <div class="detail-item">
          <label class="detail-label">告警ID：</label>
          <span class="detail-value">{{ currentAlarm?.id || '--' }}</span>
        </div>
        
        <div class="detail-item">
          <label class="detail-label">告警类型：</label>
          <el-tag :type="getCategoryType(currentAlarm?.category_name || '')">
            {{ currentAlarm?.category_name || '未分类' }}
          </el-tag>
        </div>
        
        <div class="detail-item">
          <label class="detail-label">告警描述：</label>
          <div class="detail-content">{{ currentAlarm?.content || '--' }}</div>
        </div>
        
        <div class="detail-item">
          <label class="detail-label">报警位置：</label>
          <span class="detail-value">坐标({{ currentAlarm?.latitude || '--' }}, {{ currentAlarm?.longitude || '--' }})</span>
        </div>
        
        <div class="detail-item">
          <label class="detail-label">报警时间：</label>
          <span class="detail-value">{{ formatDate(currentAlarm?.created_at || '') }}</span>
        </div>
        
        <div class="detail-item">
          <label class="detail-label">告警状态：</label>
          <el-tag :type="getStatusType(currentAlarm?.status || '')">
            {{ getStatusText(currentAlarm?.status || '') }}
          </el-tag>
        </div>
        
        <div class="detail-item">
          <label class="detail-label">航线信息：</label>
          <span class="detail-value">
            {{ getWaylineName(currentAlarm) }} ({{ getWaylineId(currentAlarm) }})
          </span>
        </div>
        
        <div class="detail-item">
          <label class="detail-label">报警图片：</label>
          <div v-if="currentAlarm?.image_url" class="alarm-image-container">
            <el-image
              :src="currentAlarm.image_url"
              :preview-src-list="[currentAlarm.image_url]"
              fit="contain"
              style="max-width: 100%; max-height: 400px; cursor: zoom-in"
            />
          </div>
          <span v-else class="text-gray-400">暂无图片</span>
        </div>
      </div>
      
      <div slot="footer" class="dialog-footer">
          <el-button class="tech-button" @click="showDetailDialog = false">关闭</el-button>
        </div>
      </el-dialog>
    </div>
  </template>

<style scoped>
/* 主容器样式 */
.alarm-list-container {
  background-color: #1f2937;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

/* 标题样式 */
.tech-title {
  position: relative;
  padding-bottom: 8px;
  margin-bottom: 20px;
  font-weight: 600;
  font-size: 20px;
}

.tech-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 80px;
  height: 2px;
  background: linear-gradient(90deg, #3b82f6, #10b981);
}

/* 搜索和筛选区域 */
.search-filters {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.search-input, .status-filter, .wayline-filter {
  margin-bottom: 10px;
}

.search-input {
  width: 300px;
}

.status-filter, .wayline-filter {
  width: 200px;
}

/* 科技风格输入框 */
.tech-input {
  background-color: #111827;
  border: 1px solid #374151;
  color: #f3f4f6;
}

.tech-input :deep(.el-input__inner) {
  background-color: #111827;
  border: 1px solid #374151;
  color: #f3f4f6;
}

.tech-input :deep(.el-input__inner:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

/* 科技风格下拉选择框 */
.tech-select {
  background-color: #111827;
  border: 1px solid #374151;
}

.tech-select :deep(.el-input__inner) {
  background-color: #111827;
  border: 1px solid #374151;
  color: #f3f4f6;
}

.tech-select :deep(.el-input__inner:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.tech-select :deep(.el-select-dropdown) {
  background-color: #1f2937;
  border: 1px solid #374151;
}

.tech-select :deep(.el-select-dropdown__item) {
  color: #f3f4f6;
}

.tech-select :deep(.el-select-dropdown__item:hover) {
  background-color: #1e3a8a;
}

.tech-select :deep(.el-select-dropdown__item.selected) {
  color: #3b82f6;
  background-color: #1e3a8a;
}

/* 科技风格表格 */
.tech-table {
  background-color: #111827;
  color: #d1d5db;
  border: 1px solid #374151;
}

.tech-table :deep(.el-table__header) {
  background-color: #1f2937;
}

.tech-table :deep(.el-table__header th) {
  background-color: #1f2937;
  color: #3b82f6;
  font-weight: 600;
  border-bottom: 1px solid #374151;
}

.tech-table :deep(.el-table__body tr) {
  background-color: #111827;
  border-bottom: 1px solid #374151;
}

.tech-table :deep(.el-table__body tr:hover > td) {
  background-color: #1e3a8a;
}

.tech-table :deep(.el-table__body tr.current-row > td) {
  background-color: #1e3a8a;
  color: #3b82f6;
}

.tech-table :deep(.el-table__empty-text) {
  color: #9ca3af;
}

/* 科技风格按钮 */
.tech-button {
  background-color: #1f2937;
  border: 1px solid #374151;
  color: #d1d5db;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.tech-button:hover {
  background-color: #374151;
  border-color: #3b82f6;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}

.tech-button-primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: 1px solid #3b82f6;
  color: white;
}

.tech-button-primary:hover {
  background: linear-gradient(135deg, #2563eb, #1e40af);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
}

.tech-button-danger {
  background: linear-gradient(135deg, #ef4444, #b91c1c);
  border: 1px solid #ef4444;
  color: white;
}

.tech-button-danger:hover {
  background: linear-gradient(135deg, #dc2626, #991b1b);
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.5);
}

/* 科技风格标签 */
.tech-badge-glow {
  position: relative;
  overflow: hidden;
}

.tech-badge-glow::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255,255,255,0.3), transparent);
  transform: rotate(45deg);
  animation: badgeGlow 2s infinite;
}

@keyframes badgeGlow {
  0% { transform: translateX(-100%) rotate(45deg); }
  100% { transform: translateX(100%) rotate(45deg); }
}

/* 待处理状态样式 - 红色 */
.alarm-status-pending {
  background: linear-gradient(135deg, #ef4444, #b91c1c) !important;
  border-color: #ef4444 !important;
  color: white !important;
  font-weight: 500;
}

/* 处理中状态样式 - 橙色 */
.alarm-status-processing {
  background: linear-gradient(135deg, #f59e0b, #d97706) !important;
  border-color: #f59e0b !important;
  color: white !important;
  font-weight: 500;
}

/* 已完成状态样式 - 绿色 */
.alarm-status-completed {
  background: linear-gradient(135deg, #10b981, #059669) !important;
  border-color: #10b981 !important;
  color: white !important;
  font-weight: 500;
}

/* 已忽略状态样式 - 蓝色 */
.alarm-status-ignored {
  background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
  border-color: #3b82f6 !important;
  color: white !important;
  font-weight: 500;
}

/* 分页样式 */
.tech-pagination {
  margin-top: 20px;
  text-align: center;
}

.tech-pagination :deep(.el-pagination) {
  color: #d1d5db;
}

.tech-pagination :deep(.el-pagination button) {
  background-color: #1f2937;
  border: 1px solid #374151;
  color: #d1d5db;
}

.tech-pagination :deep(.el-pagination button:hover) {
  color: #3b82f6;
  border-color: #3b82f6;
}

.tech-pagination :deep(.el-pagination .el-pager li) {
  color: #d1d5db;
}

.tech-pagination :deep(.el-pagination .el-pager li:hover) {
  color: #3b82f6;
}

.tech-pagination :deep(.el-pagination .el-pager li.active) {
  color: #3b82f6;
  border-color: #3b82f6;
}

.tech-pagination :deep(.el-pagination__editor) {
  background-color: #111827;
  border: 1px solid #374151;
  color: #f3f4f6;
}

/* 对话框样式 */
.tech-dialog {
  background-color: #1f2937;
  border: 1px solid #374151;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

.tech-dialog :deep(.el-dialog__header) {
  background-color: #111827;
  border-bottom: 1px solid #374151;
}

.tech-dialog :deep(.el-dialog__title) {
  color: #3b82f6;
  font-weight: 600;
}

.tech-dialog :deep(.el-dialog__body) {
  background-color: #1f2937;
  color: #d1d5db;
}

/* 确保状态更新对话框中的标题颜色正确显示 */
.status-dialog-content h4 {
  color: #93c5fd !important;
  font-weight: 600;
}

/* 定义text-blue-400类以确保一致的颜色 */
.text-blue-400 {
  color: #93c5fd !important;
}

.tech-dialog :deep(.el-dialog__footer) {
  background-color: #111827;
  border-top: 1px solid #374151;
}

/* 详情容器样式 */
.alarm-detail-container {
  background-color: #111827;
  padding: 20px;
  border-radius: 6px;
  border: 1px solid #374151;
}

.detail-item {
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
}

/* 更新标签样式，使其与状态更新对话框保持一致 */
.detail-label {
  color: #9ca3af !important;
  font-weight: 600 !important;
  margin-right: 8px;
  min-width: 100px;
}

/* 更新值样式，使用蓝色突出显示，与状态更新对话框中的text-blue-300保持一致 */
.detail-value {
  color: #93c5fd !important;
  font-weight: 500;
}

/* 更新内容样式，使其更易读 */
.detail-content {
  color: #93c5fd !important;
  line-height: 1.6;
  font-weight: 500;
  flex: 1;
  min-width: 0;
  word-break: break-word;
}

/* 科技风格边框 */
  .tech-border {
    border: 1px solid #374151;
    position: relative;
    background: linear-gradient(135deg, rgba(31, 41, 55, 0.9), rgba(17, 24, 39, 0.9));
  }

  .tech-border::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: linear-gradient(45deg, #3b82f6, #10b981, #3b82f6);
    z-index: -1;
    animation: borderRotate 8s linear infinite;
    opacity: 0.3;
    border-radius: 8px;
  }

  @keyframes borderRotate {
    0% { background-position: 0% 0%; }
    100% { background-position: 300% 0%; }
  }

  /* 玻璃效果 */
  .glass-effect {
    backdrop-filter: blur(8px);
    background-color: rgba(31, 41, 55, 0.8);
  }

  /* 加载动画 */
  .tech-table :deep(.el-loading-spinner .path) {
    stroke: #3b82f6;
  }

  .tech-table :deep(.el-loading-text) {
    color: #3b82f6;
  }

  /* 科技风格输入框 */
  .tech-input {
    background-color: #1f2937;
    border: 1px solid #374151;
    color: #d1d5db;
  }

  .tech-input :deep(.el-input__wrapper) {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    box-shadow: none !important;
  }

  .tech-input :deep(.el-input__inner) {
    background-color: #1f2937 !important;
    border: none !important;
    color: #d1d5db !important;
  }

  .tech-input :deep(.el-input__inner):focus {
    color: #93c5fd !important;
  }

  /* 科技风格下拉选择框 - 全面增强优先级 */
  .search-filters .status-filter, 
  .search-filters .wayline-filter {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    color: #d1d5db !important;
  }

  /* 直接针对特定类的样式 */
  .search-filters .status-filter :deep(.el-input__wrapper),
  .search-filters .wayline-filter :deep(.el-input__wrapper) {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    box-shadow: none !important;
  }

  .search-filters .status-filter :deep(.el-input__inner),
  .search-filters .wayline-filter :deep(.el-input__inner) {
    background-color: #1f2937 !important;
    color: #d1d5db !important;
  }

  /* 图标样式 */
  .search-filters .status-filter :deep(.el-input__suffix-inner .el-input__icon),
  .search-filters .wayline-filter :deep(.el-input__suffix-inner .el-input__icon) {
    color: #9ca3af !important;
  }

  /* 聚焦状态 */
  .search-filters .status-filter :deep(.el-input__inner:focus),
  .search-filters .wayline-filter :deep(.el-input__inner:focus) {
    color: #93c5fd !important;
  }

  /* 搜索筛选区域内的所有下拉菜单 */
  .search-filters .tech-select {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    color: #d1d5db !important;
  }

  .search-filters .tech-select :deep(.el-input__wrapper) {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    box-shadow: none !important;
  }

  /* 全局Element Plus下拉组件样式覆盖 */
  :deep(.el-select-dropdown) {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
  }

  :deep(.el-select-dropdown__item) {
    color: #d1d5db !important;
  }

  :deep(.el-select-dropdown__item:hover) {
    background-color: #374151 !important;
    color: #93c5fd !important;
  }

  :deep(.el-select-dropdown__item.selected) {
    background-color: #1e3a8a !important;
    color: #93c5fd !important;
  }

  /* 针对特定ID的筛选框样式 - 最高优先级 */
  #alarm-status-select,
  #alarm-wayline-select {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    color: #d1d5db !important;
    --el-input-bg-color: #1f2937 !important;
    --el-input-border-color: #374151 !important;
    --el-input-text-color: #d1d5db !important;
  }

  /* 使用深度选择器确保样式穿透 */
  #alarm-status-select :deep(.el-input__wrapper),
  #alarm-wayline-select :deep(.el-input__wrapper) {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    box-shadow: none !important;
  }

  #alarm-status-select :deep(.el-input__inner),
  #alarm-wayline-select :deep(.el-input__inner) {
    background-color: #1f2937 !important;
    color: #d1d5db !important;
  }

  #alarm-status-select :deep(.el-input__suffix-inner .el-input__icon),
  #alarm-wayline-select :deep(.el-input__suffix-inner .el-input__icon) {
    color: #9ca3af !important;
  }

  /* 强制覆盖Element Plus组件样式 */
  .search-filters .el-select.el-input--suffix .el-input__wrapper {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
  }

  .search-filters .el-select.el-input--suffix .el-input__wrapper .el-input__inner {
    background-color: #1f2937 !important;
    color: #d1d5db !important;
  }

  /* 最高优先级的全局样式覆盖 */
  html :deep(.el-select .el-input__wrapper) {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
  }

  html :deep(.el-select .el-input__inner) {
    background-color: #1f2937 !important;
    color: #d1d5db !important;
  }

  /* 全局输入组件样式 */
  :deep(.el-input__wrapper) {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
  }

  :deep(.el-input__inner) {
    background-color: #1f2937 !important;
    color: #d1d5db !important;
  }

  /* 确保全局覆盖 */
  .el-select {
    --el-input-bg-color: #1f2937 !important;
    --el-input-border-color: #374151 !important;
    --el-input-text-color: #d1d5db !important;
  }

  /* 科技风格分页控件 */
  .tech-pagination {
    background-color: #1f2937 !important;
    color: #d1d5db !important;
  }

  .tech-pagination :deep(.el-pagination__total) {
    color: #9ca3af !important;
  }

  .tech-pagination :deep(.el-pagination button) {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    color: #d1d5db !important;
  }

  .tech-pagination :deep(.el-pagination button:hover:not(:disabled)) {
    background-color: #374151 !important;
    border-color: #3b82f6 !important;
    color: #93c5fd !important;
    box-shadow: 0 0 10px rgba(59, 130, 246, 0.3) !important;
  }

  .tech-pagination :deep(.el-pagination button:disabled) {
    background-color: #1f2937 !important;
    border-color: #374151 !important;
    color: #4b5563 !important;
  }

  .tech-pagination :deep(.el-pagination .el-pager li) {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    color: #d1d5db !important;
  }

  .tech-pagination :deep(.el-pagination .el-pager li:hover:not(.active)) {
    background-color: #374151 !important;
    border-color: #3b82f6 !important;
    color: #93c5fd !important;
    box-shadow: 0 0 10px rgba(59, 130, 246, 0.3) !important;
  }

  .tech-pagination :deep(.el-pagination .el-pager li.active) {
    background-color: #3b82f6 !important;
    border-color: #3b82f6 !important;
    color: white !important;
    box-shadow: 0 0 15px rgba(59, 130, 246, 0.5) !important;
  }

  .tech-pagination :deep(.el-pagination__editor) {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    color: #d1d5db !important;
  }

  .tech-pagination :deep(.el-pagination__editor:focus) {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 10px rgba(59, 130, 246, 0.3) !important;
  }
</style>

<style scoped>
.alarm-detail-container {
  padding: 10px 0;
}

.detail-item {
  margin-bottom: 20px;
  display: flex;
  align-items: flex-start;
}

.detail-label {
  width: 100px;
  font-weight: bold;
  color: #606266;
  margin-right: 10px;
}

.detail-value {
  flex: 1;
  color: #303133;
}

.detail-content {
  flex: 1;
  color: #303133;
  line-height: 1.8;
  word-break: break-all;
}

.alarm-image-container {
  flex: 1;
  text-align: center;
  padding: 20px 0;
}

.text-gray-400 {
  color: #c0c4cc;
}
</style>

<script>
import alarmApi from '../api/alarmApi'

export default {
  name: 'AlarmList',
  data() {
    return {
      alarms: [],
      categories: [],
      waylines: [], // 存储航线数据
      loading: false,
      searchQuery: '',
      statusFilter: '',
      waylineIdFilter: '',
      currentPage: 1,
      pageSize: 10,
      totalAlarms: 0,
      showStatusDialog: false,
      showDetailDialog: false, // 详情弹窗显示状态
      currentAlarm: null,
      newAlarmStatus: ''
    }
  },
  watch: {
    // 监听搜索关键词变化
    searchQuery: {
      handler() {
        this.currentPage = 1 // 重置到第一页
        this.loadAlarms()
      },
      debounce: 300 // 防抖，避免频繁请求
    },
    // 监听状态筛选变化
    statusFilter() {
      this.currentPage = 1
      this.loadAlarms()
    },
    // 监听航线ID筛选变化
    waylineIdFilter: {
      handler() {
        this.currentPage = 1
        this.loadAlarms()
      },
      debounce: 300
    }
  },
  computed: {
    // 直接使用从后端获取的数据，不再需要前端过滤
    filteredAlarms() {
      return this.alarms
    }
  },
  async mounted() {
    await this.loadAlarms()
    await this.loadCategories()
    await this.loadWaylines()
    
    // 使用JavaScript直接修改筛选框样式 - 最高优先级
    this.$nextTick(() => {
      console.log('应用内联样式到筛选框')
      
      // 为所有筛选框设置样式
      const applyFilterStyles = () => {
        // 查找所有选择器容器
        const selectElements = document.querySelectorAll('#alarm-status-select, #alarm-wayline-select')
        selectElements.forEach(select => {
          // 获取输入框包装器
          const wrapper = select.querySelector('.el-input__wrapper')
          if (wrapper) {
            wrapper.style.backgroundColor = '#1f2937'
            wrapper.style.borderColor = '#374151'
            wrapper.style.boxShadow = 'none'
          }
          
          // 获取输入框
          const input = select.querySelector('.el-input__inner')
          if (input) {
            input.style.backgroundColor = '#1f2937'
            input.style.color = '#d1d5db'
          }
          
          // 获取图标
          const icon = select.querySelector('.el-input__suffix-inner .el-input__icon')
          if (icon) {
            icon.style.color = '#9ca3af'
          }
        })
        
        // 特别处理搜索输入框
        const searchInput = document.getElementById('alarm-search-input')
        if (searchInput) {
          const searchWrapper = searchInput.querySelector('.el-input__wrapper')
          const searchInner = searchInput.querySelector('.el-input__inner')
          if (searchWrapper) {
            searchWrapper.style.backgroundColor = '#1f2937'
            searchWrapper.style.borderColor = '#374151'
          }
          if (searchInner) {
            searchInner.style.backgroundColor = '#1f2937'
            searchInner.style.color = '#d1d5db'
          }
        }
        
        // 设置下拉菜单样式
        const dropdowns = document.querySelectorAll('.el-select-dropdown')
        dropdowns.forEach(dropdown => {
          dropdown.style.backgroundColor = '#1f2937'
          dropdown.style.borderColor = '#374151'
          
          const items = dropdown.querySelectorAll('.el-select-dropdown__item')
          items.forEach(item => {
            item.style.color = '#d1d5db'
            item.onmouseenter = () => {
              item.style.backgroundColor = '#374151'
              item.style.color = '#93c5fd'
            }
            item.onmouseleave = () => {
              if (!item.classList.contains('selected')) {
                item.style.backgroundColor = 'transparent'
                item.style.color = '#d1d5db'
              }
            }
          })
          
          const selectedItems = dropdown.querySelectorAll('.el-select-dropdown__item.selected')
          selectedItems.forEach(item => {
            item.style.backgroundColor = '#1e3a8a'
            item.style.color = '#93c5fd'
          })
        })
      }
      
      // 立即应用样式
      applyFilterStyles()
      
      // 监听选择器点击事件，重新应用样式（因为下拉菜单是动态创建的）
      const selects = document.querySelectorAll('#alarm-status-select, #alarm-wayline-select')
      selects.forEach(select => {
        select.addEventListener('click', () => {
          setTimeout(applyFilterStyles, 100)
        })
      })
    })
  },
  methods: {
    async loadAlarms() {
      this.loading = true
      try {
        // 构建请求参数，包含分页和筛选条件
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          search: this.searchQuery, // 搜索关键词
          status: this.statusFilter, // 状态筛选
          wayline_id: this.waylineIdFilter // 航线ID筛选(后端过滤器使用的参数名)
        }
        
        const response = await alarmApi.getAlarms(params)
        
        // 转换数据格式，确保前端显示正确
        this.alarms = (response?.results || []).map(alarm => ({
          id: alarm.id,
          created_at: alarm.created_at,
          category_name: alarm.category_details ? alarm.category_details.name : (alarm.category ? alarm.category.name : '未分类'),
          category_id: alarm.category_details ? alarm.category_details.id : (alarm.category ? alarm.category.id : null),
          latitude: alarm.latitude,
          longitude: alarm.longitude,
          content: alarm.content,
          image_url: alarm.image_url,
          status: alarm.status,
          // 支持新的外键关系结构，同时保持兼容旧格式
          wayline_id: alarm.wayline?.wayline_id || alarm.wayline_id || null,
          wayline_name: alarm.wayline?.name || null,
          // 保留完整的wayline对象
          wayline: alarm.wayline || null,
          // 保留category_details以便后续使用
          category_details: alarm.category_details || null
        }))
        
        this.totalAlarms = response?.count || this.alarms.length
      } catch (error) {
        this.$message.error('获取告警列表失败，显示模拟数据')
        console.error('Load alarms error:', error)
        
        // 使用模拟数据，确保页面功能正常
        let mockAlarms = [
          {
            id: 1,
            created_at: new Date().toISOString(),
            category_name: '设备故障',
            category_id: 1,
            latitude: 39.9042,
            longitude: 116.4074,
            content: '无人机电机过热，温度达到98°C，建议立即降落检查。电机表面出现异常颜色变化，可能存在严重故障风险。',
            image_url: 'https://picsum.photos/800/600?random=1',
            status: 'PENDING',
            wayline_id: 'WL001'
          },
          {
            id: 2,
            created_at: new Date(Date.now() - 3600000).toISOString(),
            category_name: '信号丢失',
            category_id: 2,
            latitude: 39.9142,
            longitude: 116.4174,
            content: '遥控信号弱，信号强度低于30%，无人机可能失控。请立即调整操作位置，确保视线内飞行。',
            image_url: 'https://picsum.photos/800/600?random=2',
            status: 'RESOLVED',
            wayline_id: 'WL002'
          },
          {
            id: 3,
            created_at: new Date(Date.now() - 7200000).toISOString(),
            category_name: '电量警告',
            category_id: 3,
            latitude: 39.9242,
            longitude: 116.4274,
            content: '电池电量低于20%，请尽快返航降落。预计剩余飞行时间不超过5分钟，请注意安全。',
            image_url: 'https://picsum.photos/800/600?random=3',
            status: 'COMPLETED',
            wayline_id: 'WL001'
          },
          {
            id: 4,
            created_at: new Date(Date.now() - 10800000).toISOString(),
            category_name: '天气异常',
            category_id: 4,
            latitude: 39.9342,
            longitude: 116.4374,
            content: '检测到强风，风速超过20m/s，可能影响飞行稳定性。建议立即降落至安全区域，避免发生意外。',
            image_url: null,
            status: 'IGNORED',
            wayline_id: 'WL003'
          }
        ]
        
        // 当API调用失败时，在前端进行模拟过滤，确保筛选功能可见
        if (this.searchQuery) {
          const query = this.searchQuery.toLowerCase()
          mockAlarms = mockAlarms.filter(alarm => 
            alarm.content.toLowerCase().includes(query) ||
            alarm.category_name.toLowerCase().includes(query) ||
            (alarm.wayline_id && alarm.wayline_id.toLowerCase().includes(query))
          )
        }
        
        if (this.statusFilter) {
          mockAlarms = mockAlarms.filter(alarm => alarm.status === this.statusFilter)
        }
        
        if (this.waylineIdFilter) {
          // 适配下拉选择框的航线ID筛选
          mockAlarms = mockAlarms.filter(alarm => 
            (alarm.wayline && alarm.wayline.wayline_id === this.waylineIdFilter) ||
            alarm.wayline_id === this.waylineIdFilter
          )
        }
        
        // 模拟分页
        const start = (this.currentPage - 1) * this.pageSize
        const end = start + this.pageSize
        this.alarms = mockAlarms.slice(start, end)
        this.totalAlarms = mockAlarms.length
      } finally {
        this.loading = false
      }
    },
    
    async loadCategories() {
      try {
        const categories = await alarmApi.getAlarmCategories()
        this.categories = categories?.results || categories || []
      } catch (error) {
        this.$message.error('获取告警类型失败，使用默认类型')
        console.error('Load categories error:', error)
        
        // 使用模拟数据
        this.categories = [
          { id: 1, name: '设备故障', code: 'EQUIPMENT_FAILURE' },
          { id: 2, name: '信号丢失', code: 'SIGNAL_LOSS' },
          { id: 3, name: '电量警告', code: 'BATTERY_WARNING' },
          { id: 4, name: '天气异常', code: 'WEATHER_ABNORMAL' }
        ]
      }
    },
    
    async loadWaylines() {
      try {
        // 假设alarmApi中有获取航线列表的方法
        const response = await alarmApi.getWaylines()
        this.waylines = response?.results || response || []
      } catch (error) {
        this.$message.error('获取航线列表失败')
        console.error('Load waylines error:', error)
        
        // 使用模拟数据
        this.waylines = [
          { id: 1, wayline_id: 'WL001', name: '测试航线1' },
          { id: 2, wayline_id: 'WL002', name: '测试航线2' },
          { id: 3, wayline_id: 'WL003', name: '河道巡查航线' },
          { id: 4, wayline_id: 'WL004', name: '农林监测航线' },
          { id: 5, wayline_id: 'WL005', name: '矿区测绘航线' }
        ]
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
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
    
    getStatusType(status) {
      const typeMap = {
        'PENDING': 'danger',
        'PROCESSING': 'warning',
        'COMPLETED': 'success',
        'IGNORED': 'info'
      }
      return typeMap[status] || 'default'
    },
    
    getCategoryType(categoryName) {
      // 确保categoryName是字符串
      if (!categoryName || typeof categoryName !== 'string') {
        return 'info'
      }
      
      // 根据不同的告警类型返回不同的标签类型
      const typeKeywords = {
        '发热': 'danger',
        '损伤': 'warning',
        '故障': 'danger',
        '异常': 'warning',
        '隐患': 'warning'
      }
      
      for (const [keyword, type] of Object.entries(typeKeywords)) {
        if (categoryName.includes(keyword)) {
          return type
        }
      }
      
      return 'info'
    },
    
    // 获取航线ID，支持新旧数据结构
    getWaylineId(row) {
      // 优先使用新的外键关系结构
      if (row.wayline) {
        return row.wayline.wayline_id || '--'
      }
      // 兼容旧的wayline_id字段
      return row.wayline_id || '--'
    },
      
    // 获取航线名称，支持新旧数据结构
    getWaylineName(row) {
      // 优先使用新的外键关系结构
      if (row.wayline) {
        return row.wayline.name || '--'
      }
      // 兼容从后端转换的wayline_name字段
      return row.wayline_name || '--'
    },
    
    viewAlarmDetail(alarm) {
      // 设置当前告警并显示详情弹窗
      this.currentAlarm = {...alarm};
      this.showDetailDialog = true;
    },
    
    updateAlarmStatus(alarm) {
      console.log('更新状态按钮被点击', alarm)
      // 确保currentAlarm是响应式的
      this.currentAlarm = {...alarm};
      this.newAlarmStatus = alarm.status || 'PENDING';
      // 直接设置显示状态
      this.showStatusDialog = true;
      console.log('对话框显示状态设置为true', this.showStatusDialog);
    },
    
    async confirmStatusUpdate() {
      if (!this.newAlarmStatus || !this.currentAlarm?.id) {
        this.$message.error('请选择有效的状态')
        return
      }
      
      try {
        // 使用patchAlarm方法只更新状态字段
        await alarmApi.patchAlarm(this.currentAlarm.id, { status: this.newAlarmStatus })
        this.$message.success('告警状态更新成功')
        this.showStatusDialog = false
        await this.loadAlarms() // 重新加载列表
      } catch (error) {
        this.$message.error('状态更新失败')
        console.error('Update alarm status error:', error)
      }
    },
    
    async deleteAlarm(alarmId) {
      this.$confirm('确定要删除这条告警吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await alarmApi.deleteAlarm(alarmId)
          this.$message.success('删除成功')
          await this.loadAlarms() // 重新加载列表
        } catch (error) {
          this.$message.error('删除失败')
          console.error('Delete alarm error:', error)
        }
      }).catch(() => {
        // 取消删除
      })
    },
    
    handleSizeChange(size) {
      this.pageSize = size
      this.loadAlarms()
    },
    
    handleCurrentChange(current) {
      this.currentPage = current
      this.loadAlarms()
    }
  }
}
</script>

<style scoped>
/* 使用 :deep() 选择器修改筛选框样式 */
.search-filters :deep(.el-select) {
  width: 150px;
}

.search-filters :deep(.el-input__wrapper) {
  background-color: #1f2937 !important;
  border: 1px solid #374151 !important;
  box-shadow: none !important;
}

.search-filters :deep(.el-input__wrapper:hover) {
  border-color: #4f46e5 !important;
}

.search-filters :deep(.el-input__wrapper.is-focus) {
  border-color: #4f46e5 !important;
  box-shadow: 0 0 0 1px rgba(79, 70, 229, 0.1) !important;
}

.search-filters :deep(.el-input__inner) {
  background-color: #1f2937 !important;
  color: #d1d5db !important;
  height: 32px;
}

.search-filters :deep(.el-input__icon) {
  color: #9ca3af !important;
}

.search-filters :deep(.el-input__icon:before) {
  color: #9ca3af !important;
}

/* 搜索输入框样式 */
.search-filters :deep(.el-input .el-input__wrapper) {
  background-color: #1f2937 !important;
  border: 1px solid #374151 !important;
}

.search-filters :deep(.el-input .el-input__inner) {
  background-color: #1f2937 !important;
  color: #d1d5db !important;
}

/* 特定筛选框样式 */
#alarm-status-select :deep(.el-input__wrapper),
#alarm-wayline-select :deep(.el-input__wrapper) {
  background-color: #1f2937 !important;
  border-color: #374151 !important;
}
</style>

<style>
/* 全局样式 - 影响下拉菜单 */
.selectFrom {
  background-color: #1f2937 !important;
  border: 1px solid #374151 !important;
}

.el-select-dropdown {
  background-color: #1f2937 !important;
  border: 1px solid #374151 !important;
}

.el-select-dropdown__item {
  color: #d1d5db !important;
}

.el-select-dropdown__item:hover {
  background-color: #374151 !important;
  color: #93c5fd !important;
}

.el-select-dropdown__item.selected {
  background-color: #1e3a8a !important;
  color: #93c5fd !important;
}
</style>

<style scoped>
.alarm-list-container {
  padding: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title {
  font-size: 20px;
  font-weight: bold;
  margin: 0;
}

.search-filters {
  display: flex;
  gap: 16px;
}

.search-input {
  width: 300px;
}

.status-filter {
  width: 150px;
}

.wayline-filter {
  width: 150px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.status-dialog-content {
  line-height: 1.8;
}

.status-dialog-content h4 {
  margin-bottom: 10px;
  color: #303133;
}
</style>