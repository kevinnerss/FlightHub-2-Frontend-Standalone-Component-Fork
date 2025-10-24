<template>
  <div ref="container" class="dji-space-component-container">
    <div v-if="loading" class="loading-placeholder">
      <p>组件加载中...</p>
    </div>
    <div v-if="error" class="error-placeholder">
      <p>组件加载失败: {{ error }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DjiSpaceComponent',
  props: {
    componentName: {
      type: String,
      required: true
    },
    componentProps: {
      type: Object,
      default: () => ({})
    },
    config: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      error: null,
      loaded: false
    }
  },
  mounted() {
    this.initComponent()
  },
  beforeUnmount() {
    // 清理组件
    if (this.loaded && window.FH2 && this.$refs.container) {
      this.$refs.container.innerHTML = ''
    }
  },
  methods: {
    async initComponent() {
      this.loading = true
      this.error = null
      
      try {
        // 检查FH2是否存在
        if (!window.FH2) {
          throw new Error('FH2未正确加载，请检查paas.js是否正确引入')
        }
        
        // 初始化配置
        if (this.config) {
          window.FH2.initConfig(this.config)
        }
        
        // 等待DOM更新
        await this.$nextTick()
        
        // 检查容器引用是否存在
        if (!this.$refs.container) {
          throw new Error('容器元素不存在')
        }
        
        // 生成唯一的容器ID
        const containerId = `dji-component-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        this.$refs.container.id = containerId
        
        // 检查容器元素是否存在
        if (!document.getElementById(containerId)) {
          throw new Error('容器元素未正确创建')
        }
        
        // 根据组件名称加载对应组件
        switch (this.componentName) {
          case 'project':
            window.FH2.loadProject(containerId)
            break
          case 'cockpit':
            window.FH2.loadCockpit(containerId, this.componentProps)
            break
          case 'wayline':
            window.FH2.loadWayline(containerId, this.componentProps)
            break
          case 'waylineCreation':
            window.FH2.loadWaylineCreation(containerId)
            break
          default:
            throw new Error(`不支持的组件名称: ${this.componentName}`)
        }
        
        this.loaded = true
      } catch (err) {
        this.error = err.message
        console.error('组件加载失败:', err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.dji-space-component-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.loading-placeholder,
.error-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
}

.loading-placeholder p,
.error-placeholder p {
  font-size: 16px;
  color: #666;
}
</style>