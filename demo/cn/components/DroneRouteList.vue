<template>
  <div class="drone-route-list p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md h-full flex flex-col">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">无人机航线列表</h3>
      <div class="relative">
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="搜索航线..."
          class="py-2 pl-10 pr-4 text-sm border border-gray-300 dark:border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 w-full"
        >
        <svg class="absolute left-3 top-3 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </div>
    </div>
    
    <div class="overflow-y-auto flex-grow">
      <div 
        v-for="route in filteredRoutes" 
        :key="route.id"
        class="route-item mb-3 p-3 rounded-md cursor-pointer transition-all duration-200 hover:bg-blue-50 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700"
        :class="{ 'bg-blue-100 dark:bg-blue-900': selectedRouteId === route.id }"
        @click="selectRoute(route.id)"
      >
        <div class="flex justify-between items-start">
          <div>
            <h4 class="font-medium text-gray-900 dark:text-white">{{ route.name }}</h4>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ route.description }}</p>
          </div>
          <span class="px-2 py-1 text-xs rounded-full" :class="routeStatusClass(route.status)">
            {{ route.status }}
          </span>
        </div>
        <div class="flex justify-between items-center mt-2 text-sm text-gray-600 dark:text-gray-300">
          <span>任务点: {{ route.waypoints }}个</span>
          <span>距离: {{ route.distance }}m</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DroneRouteList',
  props: {
    routes: {
      type: Array,
      default: () => []
    }
  },
  emits: ['route-selected'],
  data() {
    return {
      searchQuery: '',
      selectedRouteId: null
    }
  },
  computed: {
    filteredRoutes() {
      const query = this.searchQuery.toLowerCase();
      return this.routes.filter(route => 
        route.name.toLowerCase().includes(query) || 
        route.description.toLowerCase().includes(query)
      );
    }
  },
  methods: {
    selectRoute(routeId) {
      this.selectedRouteId = routeId;
      this.$emit('route-selected', routeId);
    },
    routeStatusClass(status) {
      switch(status) {
        case '待执行':
          return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100';
        case '执行中':
          return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100';
        case '已完成':
          return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100';
        case '已暂停':
          return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100';
        default:
          return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100';
      }
    }
  }
}
</script>

<style scoped>
.drone-route-list {
  max-height: 100%;
}

.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f7fafc;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}
</style>