<template>
  <div class="dji-wayline-creation-container">
    <DjiSpaceComponent 
      ref="waylineCreationComponent"
      component-name="waylineCreation"
      :config="config"
    />
  </div>
</template>

<script>
import DjiSpaceComponent from './DjiSpaceComponent.vue'

export default {
  name: 'DjiWaylineCreation',
  components: {
    DjiSpaceComponent
  },
  props: {
    config: {
      type: Object,
      required: true
    }
  },
  methods: {
    refresh() {
      if (this.$refs.waylineCreationComponent) {
        this.$refs.waylineCreationComponent.initComponent()
      }
    }
  }
}
</script>

<style scoped>
.dji-wayline-creation-container {
  width: 100%;
  height: 100%;
}
</style>