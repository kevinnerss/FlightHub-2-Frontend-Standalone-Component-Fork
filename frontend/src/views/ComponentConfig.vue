<template>
  <div class="config-page">
    <!-- 页面头部 -->
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

    <!-- 配置表单 -->
    <div class="config-content">
      <el-card class="config-card" shadow="hover">
        <div class="card-header">
          <div>
            <h3>大疆组件公共参数</h3>
            <p class="card-subtitle">与官方 demo 一致的 FH2 配置（serverUrl / wssUrl / hostUrl / prjId / projectToken）</p>
          </div>
          <div class="meta-text" v-if="lastUpdated">
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
                <el-input v-model="form.wssUrl" placeholder="例如 ws://127.0.0.1:30812/duplex/web" clearable />
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

      <div class="footer-actions">
      </div>
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
        // 校验 extra_params JSON
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
}

.page-header-premium {
  margin: 24px 0;
}

.header-content {
  padding: 24px 28px;
  background: rgba(26, 31, 58, 0.6);
  border-radius: 16px;
  border: 1px solid rgba(14, 165, 233, 0.4);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
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
}

.header-actions {
  display: flex;
  gap: 12px;
}

.config-content {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.config-card {
  background: rgba(26, 31, 58, 0.6);
  border: 1px solid rgba(14, 165, 233, 0.2);
  border-radius: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
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
}

.meta-text {
  color: #cbd5e1;
  font-size: 12px;
}

.config-form {
  margin-top: 12px;
}

</style>
