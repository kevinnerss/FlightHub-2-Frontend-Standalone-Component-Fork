<template>
  <div class="wayline-fallback">
    <!-- 当大疆组件不可用时显示自定义航线列表 -->
    <WaylineList 
      v-if="showCustomWaylineList" 
      :current-selected-id="currentSelectedId"
      @wayline-selected="handleWaylineSelected"
    />
    
    <!-- 用于放置大疆原始组件的容器 -->
    <div 
      v-else 
      ref="djiContainer" 
      class="dji-container"
    ></div>
  </div>
</template>

<script>
import WaylineList from './WaylineList.vue'

export default {
  name: 'WaylineFallback',
  components: {
    WaylineList
  },
  props: {
    currentSelectedId: {
      type: Number,
      default: null
    }
  },
  emits: ['wayline-selected'],
  data() {
    return {
      showCustomWaylineList: false,
      djiComponentLoaded: false,
      checkTimer: null
    }
  },
  async mounted() {
    // 尝试加载大疆组件
    await this.tryLoadDjiComponent()
  },
  beforeDestroy() {
    // 清理定时器
    if (this.checkTimer) {
      clearTimeout(this.checkTimer)
    }
  },
  methods: {
    async tryLoadDjiComponent() {
      try {
        // 检查大疆组件是否可用
        this.djiComponentLoaded = await this.checkDjiComponentAvailability()
        
        if (!this.djiComponentLoaded) {
          // 如果不可用，使用自定义组件
          this.showCustomWaylineList = true
          this.$message.warning('大疆航线组件加载失败，已切换至自定义航线列表')
        } else {
          // 尝试渲染大疆组件
          this.renderDjiComponent()
          
          // 设置一个定时器再次检查，确保组件正常工作
          this.checkTimer = setTimeout(() => {
            this.verifyDjiComponent()
          }, 3000)
        }
      } catch (error) {
        console.error('加载大疆组件时出错:', error)
        this.showCustomWaylineList = true
        this.$message.warning('大疆航线组件加载失败，已切换至自定义航线列表')
      }
    },
    
    async checkDjiComponentAvailability() {
      try {
        // 检查全局是否存在大疆相关对象
        if (typeof window.DJI !== 'undefined' && 
            typeof window.DJI.WaylineComponent !== 'undefined') {
          return true
        }
        
        // 检查是否有特定的大疆API端点
        if (window.djiApi && typeof window.djiApi.getWaylines === 'function') {
          return true
        }
        
        // 尝试简单的API调用
        const response = await fetch('/api/dji/health', {
          method: 'GET',
          timeout: 2000
        })
        return response.ok
      } catch (error) {
        return false
      }
    },
    
    renderDjiComponent() {
      try {
        // 这里应该是渲染大疆原始组件的代码
        // 根据实际的大疆组件API进行调整
        if (this.$refs.djiContainer) {
          // 模拟渲染大疆组件
          this.$refs.djiContainer.innerHTML = '<div class="dji-placeholder">正在加载大疆航线组件...</div>'
          
          // 尝试调用实际的大疆组件初始化
          if (typeof window.DJI?.WaylineComponent?.init === 'function') {
            window.DJI.WaylineComponent.init(this.$refs.djiContainer, {
              // 配置参数
              showList: true,
              showMap: true
            })
          }
        }
      } catch (error) {
        console.error('渲染大疆组件失败:', error)
        this.showCustomWaylineList = true
        this.$message.error('大疆组件渲染失败，已切换至自定义列表')
      }
    },
    
    verifyDjiComponent() {
      try {
        // 验证大疆组件是否正常工作
        // 检查容器中是否有实际内容或特定的标记元素
        const container = this.$refs.djiContainer
        if (container && container.querySelector('.dji-placeholder')) {
          // 仍然显示占位符，表示组件未正确加载
          this.showCustomWaylineList = true
          this.$message.warning('大疆航线组件未正常初始化，已切换至自定义列表')
        }
      } catch (error) {
        console.error('验证大疆组件失败:', error)
        this.showCustomWaylineList = true
      }
    },
    
    // 处理航线选择事件并向上传递
    handleWaylineSelected(wayline) {
      this.$emit('wayline-selected', wayline)
    }
  }
}
</script>

<style scoped>
.wayline-fallback {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.dji-container {
  width: 100%;
  height: 300px;
  min-height: 300px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.dji-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  background-color: #f5f7fa;
}
</style>