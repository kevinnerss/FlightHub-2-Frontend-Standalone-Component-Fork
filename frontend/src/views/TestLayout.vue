<template>
  <div class="test-layout h-screen flex flex-col">
    <div class="header bg-blue-500 text-white p-4 flex-shrink-0">
      <h1>测试布局</h1>
    </div>
    <div class="main-content flex-grow flex">
      <div class="model-view bg-green-200 flex-grow flex items-center justify-center">
        <div class="w-full h-full bg-red-200 flex items-center justify-center">
          <span class="text-2xl">模型显示区域</span>
        </div>
      </div>
      <div class="sidebar bg-yellow-200 w-60 flex-shrink-0 p-4">
        <p>侧边栏</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TestLayout'
}
</script>

<style scoped>
.test-layout {
  width: 100%;
  height: 100%;
}
</style>