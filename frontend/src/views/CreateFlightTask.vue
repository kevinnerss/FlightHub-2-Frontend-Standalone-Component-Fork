<template>
  <div class="create-flight-task-premium">
    <div class="page-header-premium">
      <div class="header-content">
        <div class="header-left">
          <div class="header-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="header-text">
            <h1 class="page-title">创建飞行任务</h1>
            <p class="page-subtitle">配置并下发一键起飞任务</p>
          </div>
        </div>
      </div>
    </div>

    <div class="form-card-premium">
      <el-form
        ref="taskForm"
        :model="form"
        :rules="rules"
        label-width="140px"
        class="task-form-premium"
        status-icon
      >
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入任务名称"></el-input>
        </el-form-item>

        <el-form-item label="执行设备" prop="sn">
          <el-select
            v-model="form.sn"
            placeholder="请选择执行设备"
            class="full-width"
            :loading="loadingDevices"
            filterable
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

        <el-form-item label="选择航线" prop="wayline_uuid">
          <el-select v-model="form.wayline_uuid" placeholder="请选择航线" class="full-width" :loading="loadingWaylines">
            <el-option
              v-for="wayline in waylines"
              :key="wayline.id"
              :label="wayline.name"
              :value="wayline.wayline_id || wayline.id"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="任务类型" prop="task_type">
          <el-select v-model="form.task_type" placeholder="请选择任务类型" class="full-width">
            <el-option label="立即任务 (Immediate)" value="immediate"></el-option>
            <el-option label="单次定时 (Timed)" value="timed"></el-option>
            <el-option label="重复任务 (Recurring)" value="recurring"></el-option>
            <el-option label="连续任务 (Continuous)" value="continuous"></el-option>
          </el-select>
        </el-form-item>

       <el-form-item label="返航高度" prop="rth_altitude">
          <el-input
            v-model.number="form.rth_altitude"
            placeholder="请输入 20-500 之间的整数"
            class="full-width"
          >
            <template #suffix>
              <span style="color: #94a3b8; margin-right: 5px;">米</span>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="返航模式" prop="rth_mode">
          <el-radio-group v-model="form.rth_mode">
            <el-radio value="optimal">最优路径 (Optimal)</el-radio>
            <el-radio value="preset">预设高度 (Preset)</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="航线精度" prop="wayline_precision_type">
          <el-radio-group v-model="form.wayline_precision_type">
            <el-radio value="rtk">RTK</el-radio>
            <el-radio value="gps">GPS</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="断点续飞" prop="resumable_status">
          <el-radio-group v-model="form.resumable_status">
            <el-radio value="auto">自动 (Auto)</el-radio>
            <el-radio value="manual">手动 (Manual)</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="submitting">创建任务</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>

        <div class="section-title">任务控制</div>

        <el-form-item label="设备控制">
          <div class="control-section-premium">
            <div class="control-buttons-premium">
              <el-button
                type="warning"
                @click="handleReturnHome"
                :disabled="!form.sn"
                :loading="commandLoading.returnHome"
                class="control-btn-premium warning-btn"
              >
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <polyline points="9 22 9 12 15 12 15 22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                返航
              </el-button>
              <el-button
                @click="handleCancelReturn"
                :disabled="!form.sn"
                :loading="commandLoading.cancelReturn"
                class="control-btn-premium default-btn"
              >
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
                  <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                取消返航
              </el-button>
              <el-button
                type="info"
                @click="handlePause"
                :disabled="!form.sn"
                :loading="commandLoading.pause"
                class="control-btn-premium info-btn"
              >
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
                  <rect x="6" y="4" width="4" height="16" stroke="currentColor" stroke-width="2"/>
                  <rect x="14" y="4" width="4" height="16" stroke="currentColor" stroke-width="2"/>
                </svg>
                暂停
              </el-button>
              <el-button
                type="success"
                @click="handleResume"
                :disabled="!form.sn"
                :loading="commandLoading.resume"
                class="control-btn-premium success-btn"
              >
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none">
                  <polygon points="5 3 19 12 5 21 5 3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                恢复
              </el-button>
            </div>
            <div class="control-tip">
              <el-text size="small" type="info">
                请先选择设备，然后点击相应的控制按钮
              </el-text>
            </div>
          </div>
        </el-form-item>
      </el-form>
    </div>

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
        time_zone: 'Asia/Chongqing',
        rth_altitude: 100,
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
          { required: true, message: '请输入返航高度', trigger: 'blur' },
          { type: 'number', message: '返航高度必须为数字', trigger: 'blur' }, // 确保是数字
          { type: 'number', min: 20, max: 500, message: '高度需在 20 到 500 米之间', trigger: 'blur' } // 限制范围
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
        const res = await waylineApi.getWaylines({ page_size: 100 })
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
          ...this.form
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
/* ========== 全局容器与变量 ========== */
.create-flight-task-premium {
  --bg-dark-color: rgba(20, 30, 50, 0.6);
  --border-color-base: rgba(59, 130, 246, 0.2);
  --text-color-base: #ffffff;
  
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100%;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

/* ========== 头部样式 ========== */
.page-header-premium { margin-bottom: 32px; }
.header-content {
  padding: 24px 32px;
  background: rgba(13, 22, 45, 0.6);
  backdrop-filter: blur(12px);
  border-radius: 16px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  align-items: center;
}
.header-left { display: flex; align-items: center; gap: 20px; }
.header-icon {
  width: 48px; height: 48px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.4) 100%);
  border: 1px solid rgba(59, 130, 246, 0.5);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center; color: #60a5fa;
}
.page-title { font-size: 26px; font-weight: 700; color: #ffffff; margin: 0 0 4px 0; }
.page-subtitle { color: #94a3b8; font-size: 14px; margin: 0; }

/* ========== 表单卡片 ========== */
.form-card-premium {
  background: rgba(13, 22, 45, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 40px;
  border: 1px solid rgba(59, 130, 246, 0.15);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.task-form-premium { max-width: 900px; margin: 0 auto; }

/* ========== 核心对齐修复 (修复返航高度对齐问题) ========== */

/* 1. 强制每一行 Form Item 变成 Flex 容器，且必须垂直居中 */
.task-form-premium :deep(.el-form-item) {
  display: flex;
  align-items: center !important; /* 关键：让 Label 和右侧内容垂直对齐 */
  margin-bottom: 24px;
}

/* 2. 强制 Label 的高度和行高逻辑 */
.task-form-premium :deep(.el-form-item__label) {
  color: #93c5fd;
  font-weight: 500;
  padding-right: 20px;
  height: auto !important;
  line-height: 1.2 !important; /* 防止文字本身偏上 */
  margin-bottom: 0 !important;
  display: flex;
  align-items: center; /* Label 内部文字居中 */
  justify-content: flex-end;
}

/* 3. 关键修改：强制内容区域 (Input 所在的容器) 使用 Flex 居中 */
.task-form-premium :deep(.el-form-item__content) {
  line-height: 40px !important;
  margin-left: 0 !important;
  display: flex !important; /* 新增：让内部元素 Flex 布局 */
  align-items: center !important; /* 新增：垂直居中 */
}

/* ========== 新增：小标题样式 (任务控制) ========== */
.section-title {
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  margin: 30px 0 20px 0;
  padding-left: 12px;
  border-left: 4px solid #409EFF; /* 左侧蓝色竖条 */
  line-height: 1;
}

/* ========== 输入框外观统一 ========== */

/* 强制 Input Number 撑满宽度并垂直对齐 */
.task-form-premium :deep(.el-input-number) {
  width: 100% !important;
  line-height: 38px;
  display: flex !important;
  align-items: center;
}
.task-form-premium :deep(.el-input-number .el-input) {
  width: 100% !important;
}

/* 统一 Wrapper 样式 */
.task-form-premium :deep(.el-input__wrapper),
.task-form-premium :deep(.el-textarea__inner),
.task-form-premium :deep(.el-select__wrapper) {
  background-color: var(--bg-dark-color) !important;
  box-shadow: 0 0 0 1px var(--border-color-base) inset !important;
  border-radius: 8px;
  padding: 1px 11px;
  height: 40px !important;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

/* 错误状态样式修复 */
.task-form-premium :deep(.el-form-item.is-error .el-input__wrapper) {
  background-color: rgba(245, 108, 108, 0.1) !important;
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}
.task-form-premium :deep(.el-form-item__error) {
  padding-top: 4px;
  color: #f56c6c;
}

/* 输入框内部文字 */
.task-form-premium :deep(.el-input__inner) {
  color: #ffffff !important;
  background: transparent !important;
  border: none !important;
  height: 100% !important;
  font-family: inherit;
  line-height: 40px !important;
}

/* Input Number 加减按钮修复 */
.task-form-premium :deep(.el-input-number__decrease),
.task-form-premium :deep(.el-input-number__increase) {
  background-color: rgba(255, 255, 255, 0.05) !important;
  border: none !important;
  color: #ffffff !important;
  width: 40px;
  height: 38px !important;
  top: 1px !important;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}
.task-form-premium :deep(.el-input-number__decrease) { left: 1px; border-right: 1px solid rgba(255,255,255,0.1) !important; }
.task-form-premium :deep(.el-input-number__increase) { right: 1px; border-left: 1px solid rgba(255,255,255,0.1) !important; }

/* 悬停与聚焦 */
.task-form-premium :deep(.el-input__wrapper:hover),
.task-form-premium :deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.6) inset !important;
}
.task-form-premium :deep(.el-input__wrapper.is-focus),
.task-form-premium :deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px #3b82f6 inset, 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
  background-color: rgba(59, 130, 246, 0.15) !important;
}

/* ========== 其他组件样式 ========== */
.task-form-premium :deep(.el-radio-group) {
  height: 40px; display: flex; align-items: center;
}
.task-form-premium :deep(.el-radio) { margin-right: 32px; height: 32px; }
.task-form-premium :deep(.el-radio__label) { color: #cbd5e1; }
.task-form-premium :deep(.el-radio__input.is-checked + .el-radio__label) { color: #60a5fa; font-weight: bold; }
.task-form-premium :deep(.el-radio__inner) { background: transparent; border-color: rgba(255, 255, 255, 0.4); }
.task-form-premium :deep(.el-radio__input.is-checked .el-radio__inner) { background: #3b82f6; border-color: #3b82f6; }

/* 按钮高度固定 */
.task-form-premium :deep(.el-button) { height: 36px; border-radius: 6px; border: none; }
.task-form-premium :deep(.el-button--primary) {
  background: linear-gradient(90deg, #2563eb, #3b82f6); color: white;
}
.task-form-premium :deep(.el-button--default) {
  background: transparent; border: 1px solid rgba(255, 255, 255, 0.2) !important; color: #cbd5e1;
}
.task-form-premium :deep(.el-button--default:hover) { border-color: #fff !important; color: #fff; }

.control-section-premium {
  background: rgba(0, 0, 0, 0.2); border: 1px dashed rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 20px;
}
.control-buttons-premium { display: flex; gap: 12px; flex-wrap: wrap; }
.control-btn-premium {
  height: 34px !important; background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3) !important; color: #93c5fd;
}

@media (max-width: 768px) {
  .form-card-premium { padding: 20px; }
  .task-form-premium :deep(.el-form-item__label) { 
    text-align: left; 
    margin-bottom: 8px; 
    line-height: normal !important;
    height: auto !important;
    justify-content: flex-start;
  }
  .task-form-premium :deep(.el-form-item) {
    display: block; 
  }
}
</style>