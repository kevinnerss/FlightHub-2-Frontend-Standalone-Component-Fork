<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden h-full flex flex-col">
    <!-- 标题栏 -->
    <div class="p-4 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
        <i class="fa fa-road text-blue-500 mr-2"></i>
        航线列表
      </h3>
    </div>
    
    <!-- 航线列表 -->
    <div class="flex-grow overflow-y-auto p-2">
      <el-empty v-if="routes.length === 0" description="暂无航线数据" />
      <el-menu
        v-else
        class="el-menu-vertical-demo"
        :default-active="String(selectedRouteId)"
        @select="handleRouteSelect"
      >
        <el-menu-item 
          v-for="route in routes" 
          :key="route.id"
          :index="String(route.id)"
          class="route-menu-item"
        >
          <template #title>
            <div class="route-info-container">
              <div class="route-header">
                <div class="route-name font-medium">{{ route.name }}</div>
                <el-tag 
                  size="small" 
                  :type="getStatusType(route.status)"
                  class="ml-2"
                >
                  {{ statusMap[route.status] }}
                </el-tag>
              </div>
              <div class="route-details flex flex-wrap gap-2 text-xs text-gray-500 mt-1">
                <span><i class="el-icon-location mr-1"></i>{{ route.length }} km</span>
                <span><i class="el-icon-timer mr-1"></i>{{ route.duration }} 分钟</span>
                <span><i class="el-icon-position mr-1"></i>{{ route.checkpoints }} 检查点</span>
                <span><i class="el-icon-date mr-1"></i>{{ formatDate(route.lastFlight) }}</span>
              </div>
              <!-- 进度指示器 -->
              <div v-if="route.status === 'in_progress'" class="mt-2">
                <el-progress :percentage="65" :stroke-width="3" :show-text="false" />
              </div>
            </div>
          </template>
        </el-menu-item>
      </el-menu>
    </div>
    
    <!-- 底部操作栏 -->
    <div class="p-3 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
      <button class="w-full flex items-center justify-center px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors">
        <i class="fa fa-plus mr-2"></i>
        新建航线
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DroneRouteList',
  
  props: {
    routes: {
      type: Array,
      required: true
    },
    selectedRouteId: {
      type: Number,
      default: null
    }
  },
  emits: ['route-selected'],
  data() {
    return {
      statusMap: {
        'completed': '已完成',
        'pending': '待执行',
        'in_progress': '进行中'
      }
    }
  },
  methods: {
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    handleRouteSelect(key) {
      this.$emit('route-selected', Number(key))
    },
    getStatusType(status) {
      switch(status) {
        case 'completed':
          return 'success'
        case 'in_progress':
          return 'primary'
        case 'pending':
          return 'warning'
        default:
          return 'info'
      }
    }
  }
}
</script>

<style scoped>
/* 菜单样式 */
.route-menu-item {
  height: auto;
  padding: 0;
  margin-bottom: 4px;
  transition: all 0.2s ease;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 100%;
}

.route-info-container {
  padding: 10px;
  width: 100%;
}

.route-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.route-name {
  font-size: 14px;
  margin: 0;
}

.route-details {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.el-menu-item.is-active {
  background-color: #e6f7ff;
  border-left: 4px solid #409eff;
}

.el-menu-item:hover {
  background-color: #f5f7fa;
}

/* 菜单分组样式 */
.el-menu--vertical {
  border-right: none;
}

/* 滚动条样式 */
.flex-grow ::v-deep(.el-scrollbar__wrap) {
  overflow-x: hidden;
}

/* 动画效果 */
.el-menu-item {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>