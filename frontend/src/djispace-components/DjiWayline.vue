<template>
  <div class="dji-wayline-container">
    <DjiSpaceComponent 
      ref="waylineComponent"
      component-name="wayline"
      :component-props="componentProps"
      :config="config"
    />
  </div>
</template>

<script>
import DjiSpaceComponent from './DjiSpaceComponent.vue'

export default {
  name: 'DjiWayline',
  components: {
    DjiSpaceComponent
  },
  props: {
    waylineId: {
      type: String,
      required: true
    },
    config: {
      type: Object,
      default: () => ({})
    }
  },
  computed: {
    componentProps() {
      return {
        wayline_id: this.waylineId
      }
    }
  },
  methods: {
    refresh() {
      if (this.$refs.waylineComponent) {
        this.$refs.waylineComponent.initComponent()
      }
    }
  }
}
</script>

<style scoped>
.dji-wayline-container {
  width: 100%;
  height: 100%;
}
</style>
