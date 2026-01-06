<template>
  <div class="create-flight-task">
    <div class="page-header">
      <h2>创建飞行任务</h2>
      <p class="subtitle">配置并下发一键起飞任务</p>
    </div>

    <div class="form-card">
      <el-form 
        ref="taskForm" 
        :model="form" 
        :rules="rules" 
        label-width="140px"
        class="task-form"
        status-icon
      >
        <!-- 任务名称 -->
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入任务名称"></el-input>
        </el-form-item>

        <!-- 设备SN -->
        <el-form-item label="执行设备" prop="sn">
          <el-select v-model="form.sn" placeholder="请选择设备" class="full-width" :loading="loadingDevices">
            <el-option
              v-for="device in devices"
              :key="device.gateway.sn"
              :label="`${device.gateway.callsign || '未命名设备'} (${device.gateway.sn})`"
              :value="device.gateway.sn"
            >
              <span style="float: left">{{ device.gateway.callsign || '未命名设备' }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{ device.gateway.sn }}</span>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 航线选择 -->
        <el-form-item label="选择航线" prop="wayline_uuid">
          <el-select v-model="form.wayline_uuid" placeholder="请选择航线" class="full-width" :loading="loadingWaylines">
            <el-option
              v-for="wayline in waylines"
              :key="wayline.id"
              :label="wayline.name"
              :value="wayline.wayline_id || wayline.id" 
            >
              <!-- assuming wayline object has name and id/wayline_id -->
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 任务类型 -->
        <el-form-item label="任务类型" prop="task_type">
          <el-select v-model="form.task_type" placeholder="请选择任务类型" class="full-width">
            <el-option label="立即任务 (Immediate)" value="immediate"></el-option>
            <el-option label="单次定时 (Timed)" value="timed"></el-option>
            <el-option label="重复任务 (Recurring)" value="recurring"></el-option>
            <el-option label="连续任务 (Continuous)" value="continuous"></el-option>
          </el-select>
        </el-form-item>

        <!-- 返航高度 -->
        <el-form-item label="返航高度 (m)" prop="rth_altitude">
          <el-input-number v-model="form.rth_altitude" :min="20" :max="500" controls-position="right"></el-input-number>
        </el-form-item>

        <!-- 返航模式 -->
        <el-form-item label="返航模式" prop="rth_mode">
          <el-radio-group v-model="form.rth_mode">
            <el-radio label="optimal">最优路径 (Optimal)</el-radio>
            <el-radio label="preset">预设高度 (Preset)</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 航线精度类型 -->
        <el-form-item label="航线精度" prop="wayline_precision_type">
          <el-radio-group v-model="form.wayline_precision_type">
            <el-radio label="rtk">RTK</el-radio>
            <el-radio label="gps">GPS</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 断点续飞 -->
        <el-form-item label="断点续飞" prop="resumable_status">
          <el-radio-group v-model="form.resumable_status">
            <el-radio label="auto">自动 (Auto)</el-radio>
            <el-radio label="manual">手动 (Manual)</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 失控行为 (隐藏或高级选项) -->
        <el-form-item label="失控行为" prop="out_of_control_action_in_flight" v-if="false">
          <el-input v-model="form.out_of_control_action_in_flight"></el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="submitting">创建任务</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 起飞确认弹窗 -->
    <el-dialog
      title="确认起飞"
      v-model="confirmDialogVisible"
      width="400px"
      :before-close="handleDialogClose"
      center
    >
      <div class="confirm-content">
        <p class="confirm-icon">🚀</p>
        <p class="confirm-text">任务已准备就绪</p>
        <p class="confirm-subtext">请确认是否立即下发并执行起飞任务？</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button 
            type="danger" 
            @click="executeTask" 
            :disabled="countdown > 0"
            :loading="submitting"
          >
            {{ countdown > 0 ? `确认起飞 (${countdown}s)` : '确认起飞' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import flightTaskApi from '../api/flightTaskApi'
import waylineApi from '../api/waylineApi'
import { ElMessage } from 'element-plus'

export default {
  name: 'CreateFlightTask',
  data() {
    return {
      loadingDevices: false,
      loadingWaylines: false,
      submitting: false,
      confirmDialogVisible: false,
      countdown: 5,
      timer: null,
      devices: [],
      waylines: [],
      form: {
        name: '',
        sn: '',
        wayline_uuid: '',
        time_zone: 'Asia/Chongqing', // Default parameter
        rth_altitude: 100, // Default sensible value
        rth_mode: 'optimal',
        wayline_precision_type: 'rtk',
        resumable_status: 'manual',
        task_type: 'immediate',
        out_of_control_action_in_flight: 'return_home'
      },
      rules: {
        name: [
          { required: true, message: '请输入任务名称', trigger: 'blur' },
          { min: 3, max: 50, message: '长度在 3 到 50 个字符', trigger: 'blur' }
        ],
        sn: [
          { required: true, message: '请选择执行设备', trigger: 'change' }
        ],
        wayline_uuid: [
          { required: true, message: '请选择航线', trigger: 'change' }
        ],
        task_type: [
          { required: true, message: '请选择任务类型', trigger: 'change' }
        ],
        rth_altitude: [
          { required: true, message: '请输入返航高度', trigger: 'blur' }
        ]
      }
    }
  },
  mounted() {
    this.fetchDevices()
    this.fetchWaylines()
  },
  beforeUnmount() {
    if (this.timer) clearInterval(this.timer)
  },
  methods: {
    async fetchDevices() {
      this.loadingDevices = true
      try {
        const list = await flightTaskApi.getDevices()
        this.devices = list || []
      } catch (error) {
        ElMessage.error('获取设备列表失败')
      } finally {
        this.loadingDevices = false
      }
    },
    async fetchWaylines() {
      this.loadingWaylines = true
      try {
        // Assuming getWaylines returns a list or a paginated object
        const res = await waylineApi.getWaylines({ page_size: 100 })
        // Adapt based on actual API response structure. 
        // Based on waylineApi.js: return response (which is response.data)
        // Usually Django DRF returns { results: [], count: ... } or just []
        if (Array.isArray(res)) {
          this.waylines = res
        } else if (res && res.results) {
          this.waylines = res.results
        } else {
          this.waylines = []
        }
      } catch (error) {
        ElMessage.error('获取航线列表失败')
      } finally {
        this.loadingWaylines = false
      }
    },
    submitForm() {
      this.$refs.taskForm.validate((valid) => {
        if (valid) {
          this.startCountdown()
        } else {
          return false
        }
      })
    },
    startCountdown() {
      this.confirmDialogVisible = true
      this.countdown = 5
      if (this.timer) clearInterval(this.timer)
      this.timer = setInterval(() => {
        this.countdown--
        if (this.countdown <= 0) {
          clearInterval(this.timer)
          this.timer = null
        }
      }, 1000)
    },
    handleDialogClose() {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
      this.confirmDialogVisible = false
    },
    async executeTask() {
      this.submitting = true
      try {
        const payload = {
          ...this.form,
          // Ensure numeric types if needed, though v-model.number or input-number handles it
        }
        const res = await flightTaskApi.createFlightTask(payload)
        if (res.code === 0) {
          ElMessage.success('任务创建成功！')
          this.handleDialogClose()
          this.resetForm()
        } else {
          ElMessage.error(res.message || '任务创建失败')
        }
      } catch (error) {
        ElMessage.error('请求失败：' + (error.message || '未知错误'))
      } finally {
        this.submitting = false
      }
    },
    resetForm() {
      this.$refs.taskForm.resetFields()
      // Reset defaults that might not be covered by resetFields if prop is missing in initial form?
      // resetFields resets to initial value defined in data().
    }
  }
}
</script>

<style scoped>
.create-flight-task {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
  border-bottom: 1px solid #eee;
  padding-bottom: 16px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.subtitle {
  color: #909399;
  margin-top: 8px;
  font-size: 14px;
}

.form-card {
  background: #fff;
  padding: 32px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.full-width {
  width: 100%;
}

.confirm-content {
  text-align: center;
  padding: 20px 0;
}

.confirm-icon {
  font-size: 48px;
  margin: 0 0 16px;
}

.confirm-text {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 8px;
}

.confirm-subtext {
  color: #909399;
  font-size: 14px;
  margin: 0;
}
</style>
