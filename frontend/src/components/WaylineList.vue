<template>
  <div class="wayline-list-container">
    <div class="header-actions">
      <!-- <h2 class="title">航线列表</h2> -->
    </div>
    
    <!-- 航线列表 -->
    <el-table
      v-loading="loading"
      :data="waylines"
      style="width: 100%"
      border
      empty-text="暂无航线数据"
      :fit="true"
      :row-class-name="tableRowClassName"
      @row-click="handleRowClick"
    >
      <el-table-column prop="id" label="ID" min-width="60" />
      <el-table-column prop="name" label="航线名称" min-width="180" show-overflow-tooltip />
      <el-table-column prop="estimated_duration" label="预计时间(秒)" min-width="120">
        <template #default="{row}">
          {{ row?.estimated_duration || '-' }}
        </template>
      </el-table-column>
    </el-table>
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
      waylines: [],
      loading: false
    }
  },
  async mounted() {
    await this.loadWaylines()
  },
  methods: {
    async loadWaylines() {
      this.loading = true
      try {
        const response = await waylineApi.getWaylines({})
        
        // 转换数据格式，只保留需要的字段
        this.waylines = (response?.results || []).map(wayline => ({
          id: wayline.id,
          name: wayline.name,
          estimated_duration: wayline.estimated_duration
        }))
        
        // 如果有航线数据且没有选中的航线，默认选择第一条
        if (this.waylines.length > 0 && !this.currentSelectedId) {
          this.$emit('wayline-selected', this.waylines[0])
        }
      } catch (error) {
        this.$message.error('获取航线列表失败，显示模拟数据')
        console.error('Load waylines error:', error)
        
        // 使用模拟数据，确保页面功能正常
        let mockWaylines = [
          {
            id: 1,
            wayline_id: 'WL001',
            name: '电力巡检航线一',
            description: '110kV输电线路常规巡检',
            waypoints: [{lat: 39.9042, lng: 116.4074}, {lat: 39.9142, lng: 116.4174}],
            length: 1250.5,
            estimated_duration: 300,
            status: 'ACTIVE',
            created_by: 'admin',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          },
          {
            id: 2,
            wayline_id: 'WL002',
            name: '桥梁检测航线',
            description: '大跨度桥梁结构安全检测',
            waypoints: [{lat: 39.9242, lng: 116.4274}, {lat: 39.9342, lng: 116.4374}],
            length: 850.3,
            estimated_duration: 180,
            status: 'DRAFT',
            created_by: 'user1',
            created_at: new Date(Date.now() - 86400000).toISOString(),
            updated_at: new Date(Date.now() - 86400000).toISOString()
          },
          {
            id: 3,
            wayline_id: 'WL003',
            name: '河道巡查航线',
            description: '城市河道水质监测与垃圾巡查',
            waypoints: [{lat: 39.9442, lng: 116.4474}, {lat: 39.9542, lng: 116.4574}],
            length: 2100.8,
            estimated_duration: 420,
            status: 'ARCHIVED',
            created_by: 'admin',
            created_at: new Date(Date.now() - 172800000).toISOString(),
            updated_at: new Date(Date.now() - 172800000).toISOString()
          }
        ]
        
        // 当API调用失败时，在前端进行模拟过滤
        if (this.searchQuery) {
          const query = this.searchQuery.toLowerCase()
          mockWaylines = mockWaylines.filter(wayline => 
            wayline.name.toLowerCase().includes(query) ||
            wayline.wayline_id.toLowerCase().includes(query) ||
            (wayline.description && wayline.description.toLowerCase().includes(query))
          )
        }
        
        if (this.statusFilter) {
          mockWaylines = mockWaylines.filter(wayline => wayline.status === this.statusFilter)
        }
        
        // 简化模拟数据，只保留需要的字段
        this.waylines = mockWaylines.map(wayline => ({
          id: wayline.id,
          name: wayline.name,
          estimated_duration: wayline.estimated_duration
        }))
        
        // 如果有航线数据且没有选中的航线，默认选择第一条
        if (this.waylines.length > 0 && !this.currentSelectedId) {
          this.$emit('wayline-selected', this.waylines[0])
        }
      } finally {
        this.loading = false
      }
    },
    
    // 行点击事件处理
    handleRowClick(row) {
      this.$emit('wayline-selected', row)
    },
    
    // 为选中的行添加特殊样式
    tableRowClassName({row}) {
      return row.id === this.currentSelectedId ? 'selected-row' : ''
    }
  }
}
</script>

<style scoped>
.wayline-list-container {
  padding: 10px;
  background: #fff;
  border-radius: 4px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.header-actions {
  margin-bottom: 15px;
}

.title {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

/* 为选中的行添加特殊样式 */
:deep(.el-table__row.selected-row) {
  background-color: #e6f7ff !important;
}

:deep(.el-table__row.selected-row:hover) {
  background-color: #bae7ff !important;
}
</style>