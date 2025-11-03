<template>
  <div class="alarm-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>告警管理</h1>
      <p>查看、管理和处理所有系统告警信息</p>
    </div>
    
    <!-- 告警列表组件 -->
    <AlarmList />
  </div>
</template>

<script>
import AlarmList from '../components/AlarmList.vue'

export default {
  name: 'AlarmManagement',
  components: {
    AlarmList
  },
  metaInfo: {
    title: '告警管理 - 无人机巡检系统'
  }
}
</script>

<style scoped>
.alarm-management {
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
}

.page-header {
  background-color: #fff;
  padding: 20px 30px;
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 500;
  color: #303133;
}

.page-header p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}
</style>