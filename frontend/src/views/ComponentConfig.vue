<template>
  <div class="config-page">
    <div class="page-header-premium">
      <div class="header-content">
        <div class="header-left">
          <div class="header-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 7h16M4 12h10M4 17h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="18" cy="17" r="2" stroke="currentColor" stroke-width="2"/>
              <circle cx="20" cy="7" r="2" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="header-text">
            <h1 class="page-title">组件参数配置</h1>
            <p class="page-subtitle">为大疆二开组件集中配置公共参数，保存到数据库供全局使用</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" :loading="loading" @click="loadConfig">
            重新拉取
          </el-button>
          <el-button type="success" :loading="saving" @click="handleSave">
            保存配置
          </el-button>
        </div>
      </div>
    </div>

    <div class="config-content">
      <el-card class="config-card" shadow="hover">
        <div class="card-header">
          <div>
            <h3>大疆组件公共参数</h3>
            <p class="card-subtitle">与官方 demo 一致的 FH2 配置（serverUrl / wssUrl / hostUrl / prjId / projectToken）</p>
          </div>
          <div class="meta-text" v-if="lastUpdated">
            <span class="dot"></span>
            上次保存时间：{{ lastUpdated }}
          </div>
        </div>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="160px"
          label-position="left"
          class="config-form"
        >
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="serverUrl" prop="serverUrl">
                <el-input
                  v-model="form.serverUrl"
                  placeholder="例如 http://127.0.0.1:30812"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="wssUrl" prop="wssUrl">
                <el-input
                  v-model="form.wssUrl"
                  placeholder="例如 ws://127.0.0.1:30812/duplex/web"
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="hostUrl" prop="hostUrl">
                <el-input
                  v-model="form.hostUrl"
                  placeholder="例如 http://127.0.0.1"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="prjId" prop="prjId">
                <el-input v-model="form.prjId" placeholder="项目 ID，可选" clearable />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="projectToken" prop="projectToken">
                <el-input v-model="form.projectToken" placeholder="组织密钥（必填）" clearable />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="用户 ID" prop="userId">
                <el-input v-model="form.userId" placeholder="可选：当前调用者用户 ID" clearable />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Workspace / Org ID" prop="workspaceId">
                <el-input v-model="form.workspaceId" placeholder="可选：空间或组织 ID" clearable />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="其它自定义 JSON" prop="extra_params">
                <el-input
                  v-model="form.extra_params"
                  type="textarea"
                  :autosize="{ minRows: 2, maxRows: 4 }"
                  placeholder='可选，JSON 字符串，如 {"customKey":"customValue"}'
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import componentConfigApi from '../api/componentConfigApi.js'

export default {
  name: 'ComponentConfig',
  data() {
    return {
      form: {
        serverUrl: '',
        wssUrl: '',
        hostUrl: '',
        prjId: '',
        projectToken: '',
        userId: '',
        workspaceId: '',
        fh2_project_id: '', // 兼容旧字段
        extra_params: ''
      },
      rules: {
        serverUrl: [{ required: true, message: '请输入 serverUrl', trigger: 'blur' }],
        wssUrl: [{ required: true, message: '请输入 wssUrl', trigger: 'blur' }],
        hostUrl: [{ required: true, message: '请输入 hostUrl', trigger: 'blur' }],
        projectToken: [{ required: true, message: '请输入 projectToken', trigger: 'blur' }]
      },
      loading: false,
      saving: false,
      lastUpdated: ''
    }
  },
  mounted() {
    this.loadConfig()
  },
  methods: {
    async loadConfig() {
      this.loading = true
      try {
        const data = await componentConfigApi.getConfig(true)
        if (data && typeof data === 'object') {
          this.form = {
            ...this.form,
            ...data
          }
          if (data.extra_params && typeof data.extra_params === 'object') {
            this.form.extra_params = JSON.stringify(data.extra_params, null, 2)
          }
          if (data.updated_at) {
            this.lastUpdated = new Date(data.updated_at).toLocaleString('zh-CN')
          }
        }
      } catch (error) {
        console.error('加载配置失败:', error)
        ElMessage.error('加载配置失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    async handleSave() {
      if (this.saving) return
      this.saving = true
      try {
        let extraParams = this.form.extra_params
        if (extraParams && typeof extraParams === 'string') {
          try {
            extraParams = JSON.parse(extraParams)
          } catch (e) {
            throw new Error('extra_params 不是合法的 JSON')
          }
        }

        const payload = { ...this.form, extra_params: extraParams }
        const result = await componentConfigApi.updateConfig(payload)
        if (result?.updated_at) {
          this.lastUpdated = new Date(result.updated_at).toLocaleString('zh-CN')
        } else {
          this.lastUpdated = new Date().toLocaleString('zh-CN')
        }
        ElMessage.success('配置已保存并更新到数据库')
      } catch (error) {
        console.error('保存配置失败:', error)
        let detail = error?.message || '保存失败，请检查网络或数据格式'
        if (error?.response?.data) {
          detail = JSON.stringify(error.response.data)
        }
        ElMessage.error(detail)
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.config-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 0 32px 0;
  color: #e2e8f0;
  position: relative;
}

.config-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 15% 20%, rgba(56, 189, 248, 0.12), transparent 45%),
    radial-gradient(circle at 85% 10%, rgba(94, 234, 212, 0.14), transparent 40%);
  pointer-events: none;
  z-index: 0;
  opacity: 0.8;
}

.page-header-premium {
  margin: 24px 0;
  position: relative;
  z-index: 1;
}

.header-content {
  padding: 24px 28px;
  background: linear-gradient(135deg, rgba(26, 31, 58, 0.85), rgba(20, 25, 46, 0.9));
  border-radius: 16px;
  border: 1px solid rgba(14, 165, 233, 0.35);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35), inset 0 0 0 1px rgba(255, 255, 255, 0.03);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 16px rgba(14, 165, 233, 0.4);
}

.header-text .page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-text .page-subtitle {
  margin: 6px 0 0 0;
  color: #94a3b8;
  line-height: 1.6;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.config-content {
  display: flex;
  flex-direction: column;
  gap: 18px;
  position: relative;
  z-index: 1;
}

.config-card {
  background: rgba(20, 25, 46, 0.82);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 18px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.35);
  overflow: hidden;
}

:deep(.el-card__body) {
  padding: 20px 24px 24px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  color: #e2e8f0;
  font-size: 18px;
}

.card-subtitle {
  margin: 4px 0 0 0;
  color: #94a3b8;
  font-size: 13px;
  line-height: 1.6;
}

.meta-text {
  color: #67e8f9;
  font-size: 12px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.35);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.meta-text .dot {
  width: 8px;
  height: 8px;
  background: #22d3ee;
  border-radius: 50%;
  box-shadow: 0 0 0 6px rgba(34, 211, 238, 0.18);
}

.config-form {
  margin-top: 12px;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}

:deep(.el-form-item__label) {
  color: #cbd5e1;
  font-weight: 600;
  letter-spacing: 0.2px;
}

:deep(.el-form-item__content) {
  align-items: center;
}

:deep(.el-form-item__error) {
  color: #fca5a5;
}

:deep(.el-input__wrapper) {
  background: radial-gradient(circle at 20% 20%, rgba(56, 189, 248, 0.08), transparent 45%),
    rgba(10, 12, 26, 0.9);
  border: 1px solid rgba(56, 189, 248, 0.35);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 10px 28px rgba(0, 0, 0, 0.35);
  border-radius: 12px;
  padding: 10px 12px;
  transition: all 0.2s ease;
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-input__wrapper:hover) {
  border-color: #22d3ee;
  box-shadow:
    0 0 0 1px rgba(34, 211, 238, 0.45),
    0 0 0 6px rgba(34, 211, 238, 0.12),
    0 14px 32px rgba(0, 0, 0, 0.4);
}

:deep(.el-input__inner),
:deep(.el-textarea__inner) {
  color: #e2e8f0;
}

:deep(.el-input__inner::placeholder),
:deep(.el-textarea__inner::placeholder) {
  color: #64748b;
}

:deep(.el-input__suffix),
:deep(.el-input__prefix) {
  color: #cbd5e1;
}

:deep(.el-textarea__inner) {
  background: rgba(10, 12, 26, 0.9);
  border: 1px solid rgba(56, 189, 248, 0.35);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 10px 28px rgba(0, 0, 0, 0.35);
  border-radius: 12px;
  transition: all 0.2s ease;
  padding: 12px;
}

:deep(.el-textarea__inner:focus),
:deep(.el-textarea__inner:hover) {
  border-color: #22d3ee;
  box-shadow:
    0 0 0 1px rgba(34, 211, 238, 0.45),
    0 0 0 6px rgba(34, 211, 238, 0.12),
    0 14px 32px rgba(0, 0, 0, 0.4);
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #0ea5e9, #22d3ee);
  border: 1px solid rgba(14, 165, 233, 0.7);
  box-shadow: 0 8px 24px rgba(14, 165, 233, 0.3);
}

:deep(.el-button--success) {
  background: linear-gradient(135deg, #10b981, #34d399);
  border: 1px solid rgba(16, 185, 129, 0.7);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.25);
}

:deep(.el-button) {
  border-radius: 10px;
}
</style>
