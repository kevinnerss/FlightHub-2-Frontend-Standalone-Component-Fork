<template>
  <div>Monitor Panel</div>
</template>

<script>
export default {
  name: 'MonitorPanel',
  props: {
    videoStreamUrl: {
      type: String,
      default: ''
    },
    isStreaming: {
      type: Boolean,
      default: false
    },
    droneStatus: {
      type: String,
      default: '正常'
    },
    batteryLevel: {
      type: Number,
      default: 100
    },
    altitude: {
      type: Number,
      default: 0
    },
    speed: {
      type: Number,
      default: 0
    }
  }
}
</script>