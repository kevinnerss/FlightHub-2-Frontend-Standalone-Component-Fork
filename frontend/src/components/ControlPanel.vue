<template>
  <el-card shadow="hover">
    <!-- 标题栏 -->
    <template #header>
      <div class="flex items-center">
        <span>无人机控制</span>
      </div>
    </template>
    
    <!-- 控制面板 -->
    <div class="space-y-4">
      <!-- 主控制按钮 -->
      <el-row :gutter="12">
        <el-col :span="12">
          <el-button 
            type="primary" 
            size="large"
            class="w-full h-24 flex flex-col justify-center"
            @click="handleControl('start')"
            :disabled="currentStatus === '飞行中'"
          >
            启动
          </el-button>
        </el-col>
        <el-col :span="12">
          <el-button 
            type="warning" 
            size="large"
            class="w-full h-24 flex flex-col justify-center"
            @click="handleControl('pause')"
            :disabled="currentStatus !== '飞行中'"
          >
            暂停
          </el-button>
        </el-col>
        <el-col :span="12">
          <el-button 
            type="danger" 
            size="large"
            class="w-full h-24 flex flex-col justify-center"
            @click="handleControl('stop')"
            :disabled="currentStatus === '待命' || currentStatus === '已停止'"
          >
            停止
          </el-button>
        </el-col>
        <el-col :span="12">
          <el-button 
            type="info" 
            size="large"
            class="w-full h-24 flex flex-col justify-center"
            @click="handleControl('return')"
            :disabled="currentStatus === '待命' || currentStatus === '已停止' || currentStatus === '返回中'"
          >
            返航
          </el-button>
        </el-col>
      </el-row>
      
      <!-- 高度控制 -->
      <div>
        <div class="flex justify-between items-center mb-2">
          <label class="text-sm text-gray-700 dark:text-gray-300">目标高度</label>
          <el-tag type="primary" size="small">{{ targetAltitude }} m</el-tag>
        </div>
        <el-slider
          v-model.number="localTargetAltitude"
          :min="0"
          :max="100"
          :step="1"
          @change="handleAltitudeChange"
          :disabled="currentStatus !== '飞行中'"
          show-stops
        ></el-slider>
      </div>
      
      <!-- 速度控制 -->
      <div>
        <div class="flex justify-between items-center mb-2">
          <label class="text-sm text-gray-700 dark:text-gray-300">目标速度</label>
          <el-tag type="primary" size="small">{{ targetSpeed }} m/s</el-tag>
        </div>
        <el-slider
          v-model.number="localTargetSpeed"
          :min="0"
          :max="15"
          :step="0.5"
          @change="handleSpeedChange"
          :disabled="currentStatus !== '飞行中'"
          show-stops
        ></el-slider>
      </div>
      
      <!-- 紧急停止按钮 -->
      <el-button 
        type="danger" 
        size="large"
        class="w-full py-6"
        @click="$emit('emergency-stop')"
        :loading="isProcessingEmergencyStop"
      >
        <span class="font-medium">紧急停止</span>
      </el-button>
    </div>
  </el-card>
</template>

<script>
export default {
  name: 'ControlPanel',
  props: {
    currentStatus: {
      type: String,
      default: '待命'
    },
    targetAltitude: {
      type: Number,
      default: 0
    },
    targetSpeed: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      localTargetAltitude: this.targetAltitude,
      localTargetSpeed: this.targetSpeed,
      isProcessingEmergencyStop: false
    }
  },
  watch: {
    targetAltitude(newVal) {
      this.localTargetAltitude = newVal
    },
    targetSpeed(newVal) {
      this.localTargetSpeed = newVal
    }
  },
  methods: {
    // 处理控制动作
    handleControl(action) {
      this.$emit('control-action', action)
    },
    
    // 处理高度变更
    handleAltitudeChange() {
      this.$emit('update-altitude', this.localTargetAltitude)
    },
    
    // 处理速度变更
    handleSpeedChange() {
      this.$emit('update-speed', this.localTargetSpeed)
    },
    
    // 处理紧急停止 (添加防抖功能)
    async handleEmergencyStop() {
      if (this.isProcessingEmergencyStop) return
      
      this.isProcessingEmergencyStop = true
      this.$emit('emergency-stop')
      
      // 3秒后重置状态
      setTimeout(() => {
        this.isProcessingEmergencyStop = false
      }, 3000)
    }
  }
}
</script>

<style scoped>
/* 紧急停止按钮脉冲动画 */
.el-button--danger {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(235, 87, 87, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(235, 87, 87, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(235, 87, 87, 0);
  }
}

/* 按钮样式优化 */
.el-button {
  transition: all 0.3s ease;
}

.el-button:hover:not(:disabled) {
  transform: translateY(-2px);
}

.el-button:active:not(:disabled) {
  transform: translateY(0);
}

/* 滑块样式优化 */
.el-slider__runway {
  border-radius: 4px;
}

.el-slider__bar {
  border-radius: 4px;
}
</style>