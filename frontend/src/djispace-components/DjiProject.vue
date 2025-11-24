<template>
  <div class="dji-project-container">
    <DjiSpaceComponent 
      ref="projectComponent"
      component-name="project"
      :config="config"
    />
  </div>
</template>

<script>
import DjiSpaceComponent from './DjiSpaceComponent.vue'

export default {
  name: 'DjiProject',
  components: {
    DjiSpaceComponent
  },
  props: {
    config: {
      type: Object,
      default: () => ({})
    }
  },
  methods: {
    // 可以添加一些项目组件特有的方法
    refresh() {
      if (this.$refs.projectComponent) {
        this.$refs.projectComponent.initComponent()
      }
    }
  }
}
</script>

<style scoped>
.dji-project-container {
  width: 100%;
  height: 100%;
}
</style>
