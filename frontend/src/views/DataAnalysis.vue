<template>
  <div class="p-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">数据分析</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <!-- 统计卡片 -->
        <div class="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg">
          <h3 class="text-blue-600 dark:text-blue-400 text-lg font-semibold">巡检总里程</h3>
          <p class="text-3xl font-bold mt-2 text-gray-900 dark:text-white">156.2 km</p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">较上周增长 8.3%</p>
        </div>
        <div class="bg-green-50 dark:bg-green-900/30 p-4 rounded-lg">
          <h3 class="text-green-600 dark:text-green-400 text-lg font-semibold">发现隐患</h3>
          <p class="text-3xl font-bold mt-2 text-gray-900 dark:text-white">24 处</p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">其中 18 处已处理</p>
        </div>
        <div class="bg-purple-50 dark:bg-purple-900/30 p-4 rounded-lg">
          <h3 class="text-purple-600 dark:text-purple-400 text-lg font-semibold">设备完好率</h3>
          <p class="text-3xl font-bold mt-2 text-gray-900 dark:text-white">97.8%</p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">较上月提升 1.2%</p>
        </div>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 隐患类型分布 -->
        <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <h3 class="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">隐患类型分布</h3>
          <div class="h-64 bg-white dark:bg-gray-800 rounded-md flex items-center justify-center">
            <i class="fa fa-pie-chart text-5xl text-gray-300 dark:text-gray-600"></i>
          </div>
        </div>
        
        <!-- 巡检趋势 -->
        <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <h3 class="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">巡检趋势</h3>
          <div class="h-64 bg-white dark:bg-gray-800 rounded-md flex items-center justify-center">
            <i class="fa fa-line-chart text-5xl text-gray-300 dark:text-gray-600"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataAnalysis'
}
</script>