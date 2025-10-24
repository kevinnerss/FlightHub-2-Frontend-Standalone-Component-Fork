<template>
  <div class="dji-cockpit-container">
    <DjiSpaceComponent 
      ref="cockpitComponent"
      component-name="cockpit"
      :component-props="componentProps"
      :config="config"
    />
  </div>
</template>

<script>
import DjiSpaceComponent from './DjiSpaceComponent.vue'

export default {
  name: 'DjiCockpit',
  components: {
    DjiSpaceComponent
  },
  props: {
    gatewaySn: {
      type: String,
      default: ''
    },
    droneSn: {
      type: String,
      default: ''
    },
    config: {
      type: Object,
      required: true
    }
  },
  computed: {
    componentProps() {
      return {
        gateway_sn: this.gatewaySn,
        drone_sn: this.droneSn
      }
    }
  },
  methods: {
    refresh() {
      if (this.$refs.cockpitComponent) {
        this.$refs.cockpitComponent.initComponent()
      }
    }
  }
}
</script>

<style scoped>
.dji-cockpit-container {
  width: 100%;
  height: 100%;
}
</style>