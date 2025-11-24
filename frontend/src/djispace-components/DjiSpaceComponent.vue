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
import componentConfigApi from '../api/componentConfigApi.js'

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
      default: () => ({})
    },
    // 可选：手动指定容器 ID（默认自动生成）
    containerId: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      loading: false,
      error: null,
      loaded: false,
      backendConfig: null
    }
  },
  mounted() {
    this.initComponent()
  },
  beforeUnmount() {
    if (this.loaded && window.FH2 && this.$refs.container) {
      this.$refs.container.innerHTML = ''
    }
  },
  methods: {
    async initComponent() {
      this.loading = true
      this.error = null

      try {
        if (!window.FH2) {
          throw new Error('FH2未正确加载，请检查paas.js是否正确引入')
        }

        // 优先拉取后端保存的公共参数，再用前端传入覆盖
        let mergedConfig = {}
        try {
          this.backendConfig = await componentConfigApi.getConfig()
          if (this.backendConfig && typeof this.backendConfig === 'object') {
            mergedConfig = { ...this.backendConfig }
          }
        } catch (err) {
          console.warn('获取组件配置失败，使用前端传入配置', err)
        }
        mergedConfig = { ...mergedConfig, ...(this.config || {}) }

        // demo 中要求的关键字段
        if (!mergedConfig.serverUrl || !mergedConfig.hostUrl || !mergedConfig.projectToken) {
          console.warn('FH2 配置缺少 serverUrl/hostUrl/projectToken，请在“组件参数配置”页面补全')
        }
        window.FH2.initConfig(mergedConfig)

        await this.$nextTick()

        if (!this.$refs.container) {
          throw new Error('容器元素不存在')
        }

        const containerId = this.containerId || `dji-component-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        this.$refs.container.id = containerId

        if (!document.getElementById(containerId)) {
          throw new Error('容器元素未正确创建')
        }

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
