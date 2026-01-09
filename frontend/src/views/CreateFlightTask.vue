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
          <!-- 快速选择最近使用的设备 -->
          <el-input v-model="form.sn" placeholder="请输入或选择设备SN" class="full-width">
            <template #append>
              <el-dropdown @command="selectRecentDevice" :disabled="loadingRecentDevices">
                <el-button :loading="loadingRecentDevices">
                  最近使用
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item v-if="recentDevices.length === 0" disabled>
                      暂无历史记录
                    </el-dropdown-item>
                    <el-dropdown-item
                      v-for="device in recentDevices"
                      :key="device.sn"
                      :command="device.sn"
                      :label="device.sn"
                    >
                      <div style="display: flex; justify-content: space-between; align-items: center; min-width: 300px;">
                        <div>
                          <div style="font-weight: bold;">{{ device.sn }}</div>
                          <div style="font-size: 12px; color: #909399;">{{ device.name }}</div>
                        </div>
                        <el-text size="small" type="info">{{ formatTime(device.last_used) }}</el-text>
                      </div>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-input>

          <!-- 设备列表下拉选择 -->
          <el-select
            v-model="form.sn"
            placeholder="或从列表选择"
            class="full-width"
            :loading="loadingDevices"
            filterable
            style="margin-top: 8px;"
          >
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

        <!-- 任务控制按钮组 -->
        <el-divider content-position="left">
          <span style="color: #909399; font-size: 14px;">任务控制</span>
        </el-divider>

        <el-form-item label="设备控制">
          <div class="control-buttons">
            <el-button
              type="warning"
              @click="handleReturnHome"
              :disabled="!form.sn"
              :loading="commandLoading.returnHome"
              icon="House"
            >
              返航
            </el-button>
            <el-button
              @click="handleCancelReturn"
              :disabled="!form.sn"
              :loading="commandLoading.cancelReturn"
              icon="Close"
            >
              取消返航
            </el-button>
            <el-button
              type="info"
              @click="handlePause"
              :disabled="!form.sn"
              :loading="commandLoading.pause"
              icon="VideoPause"
            >
              暂停
            </el-button>
            <el-button
              type="success"
              @click="handleResume"
              :disabled="!form.sn"
              :loading="commandLoading.resume"
              icon="VideoPlay"
            >
              恢复
            </el-button>
          </div>
          <div class="control-tip">
            <el-text size="small" type="info">
              请先选择设备，然后点击相应的控制按钮
            </el-text>
          </div>
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
      loadingRecentDevices: false,
      submitting: false,
      confirmDialogVisible: false,
      countdown: 5,
      timer: null,
      devices: [],
      recentDevices: [],
      waylines: [],
      commandLoading: {
        returnHome: false,
        cancelReturn: false,
        pause: false,
        resume: false
      },
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
    this.fetchRecentDevices()
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
    async fetchRecentDevices() {
      this.loadingRecentDevices = true
      try {
        const res = await flightTaskApi.getRecentDevices()
        this.recentDevices = res || []
      } catch (error) {
        console.error('获取最近设备失败:', error)
        this.recentDevices = []
      } finally {
        this.loadingRecentDevices = false
      }
    },
    selectRecentDevice(sn) {
      this.form.sn = sn
      ElMessage.success(`已选择设备: ${sn}`)
    },
    formatTime(timeStr) {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      const now = new Date()
      const diff = now - date
      const minutes = Math.floor(diff / 60000)
      const hours = Math.floor(diff / 3600000)
      const days = Math.floor(diff / 86400000)

      if (minutes < 1) return '刚刚'
      if (minutes < 60) return `${minutes}分钟前`
      if (hours < 24) return `${hours}小时前`
      if (days < 7) return `${days}天前`
      return date.toLocaleDateString('zh-CN')
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
    },

    // 返航
    async handleReturnHome() {
      if (!this.form.sn) {
        ElMessage.warning('请先选择设备')
        return
      }

      this.$confirm('确认执行返航操作？', '提示', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        this.commandLoading.returnHome = true
        try {
          const res = await flightTaskApi.returnHome(this.form.sn)
          if (res.code === 0) {
            ElMessage.success('返航指令已发送')
          } else {
            ElMessage.error(res.msg || '返航指令发送失败')
          }
        } catch (error) {
          ElMessage.error('返航指令发送失败：' + (error.message || '未知错误'))
        } finally {
          this.commandLoading.returnHome = false
        }
      }).catch(() => {})
    },

    // 取消返航
    async handleCancelReturn() {
      if (!this.form.sn) {
        ElMessage.warning('请先选择设备')
        return
      }

      this.$confirm('确认取消返航？', '提示', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        this.commandLoading.cancelReturn = true
        try {
          const res = await flightTaskApi.cancelReturn(this.form.sn)
          if (res.code === 0) {
            ElMessage.success('已取消返航')
          } else {
            ElMessage.error(res.msg || '取消返航失败')
          }
        } catch (error) {
          ElMessage.error('取消返航失败：' + (error.message || '未知错误'))
        } finally {
          this.commandLoading.cancelReturn = false
        }
      }).catch(() => {})
    },

    // 暂停任务
    async handlePause() {
      if (!this.form.sn) {
        ElMessage.warning('请先选择设备')
        return
      }

      this.$confirm('确认暂停当前任务？', '提示', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'info'
      }).then(async () => {
        this.commandLoading.pause = true
        try {
          const res = await flightTaskApi.pauseTask(this.form.sn)
          if (res.code === 0) {
            ElMessage.success('任务已暂停')
          } else {
            ElMessage.error(res.msg || '暂停任务失败')
          }
        } catch (error) {
          ElMessage.error('暂停任务失败：' + (error.message || '未知错误'))
        } finally {
          this.commandLoading.pause = false
        }
      }).catch(() => {})
    },

    // 恢复任务
    async handleResume() {
      if (!this.form.sn) {
        ElMessage.warning('请先选择设备')
        return
      }

      this.$confirm('确认恢复任务？', '提示', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'success'
      }).then(async () => {
        this.commandLoading.resume = true
        try {
          const res = await flightTaskApi.resumeTask(this.form.sn)
          if (res.code === 0) {
            ElMessage.success('任务已恢复')
          } else {
            ElMessage.error(res.msg || '恢复任务失败')
          }
        } catch (error) {
          ElMessage.error('恢复任务失败：' + (error.message || '未知错误'))
        } finally {
          this.commandLoading.resume = false
        }
      }).catch(() => {})
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

.control-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.control-tip {
  margin-top: 8px;
}
</style>
