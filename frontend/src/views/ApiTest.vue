<template>
  <div class="api-test">
    <el-container class="h-screen overflow-hidden">
      <el-header class="bg-white shadow-sm p-4 flex items-center justify-between">
        <h1 class="text-2xl font-bold">API连通性测试</h1>
        <el-button type="primary" @click="runAllTests">运行全部测试</el-button>
      </el-header>
      
      <el-container class="p-4 gap-4">
        <el-main class="p-0">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="h-full">
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-medium">告警类型测试</span>
                    <el-button @click="testAlarmTypes">测试</el-button>
                  </div>
                </template>
                <div class="test-result">
                  <div v-if="alarmTypes.loading" class="text-center py-4">
                    <i class="el-icon-loading"></i> 测试中...
                  </div>
                  <div v-else-if="alarmTypes.error" class="text-red-500">
                    错误: {{ alarmTypes.error }}
                  </div>
                  <div v-else-if="alarmTypes.data" class="space-y-2">
                    <div v-for="type in alarmTypes.data" :key="type.id" class="border-b pb-2">
                      <p><strong>{{ type.name }}</strong> ({{ type.code }})</p>
                      <p class="text-gray-600 text-sm">{{ type.description }}</p>
                    </div>
                  </div>
                  <div v-else class="text-gray-500 text-center py-4">
                    点击"测试"按钮运行测试
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="12">
              <el-card class="h-full">
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-medium">告警信息测试</span>
                    <el-button @click="testAlarms">测试</el-button>
                  </div>
                </template>
                <div class="test-result">
                  <div v-if="alarms.loading" class="text-center py-4">
                    <i class="el-icon-loading"></i> 测试中...
                  </div>
                  <div v-else-if="alarms.error" class="text-red-500">
                    错误: {{ alarms.error }}
                  </div>
                  <div v-else-if="alarms.data" class="space-y-2 max-h-96 overflow-y-auto">
                    <div v-for="alarm in alarms.data" :key="alarm.id" class="border-b pb-2">
                      <p><strong>{{ alarm.type_name }}</strong> - {{ alarm.status }}</p>
                      <p class="text-gray-600 text-sm">{{ alarm.content }}</p>
                      <p class="text-gray-500 text-xs">
                        位置: {{ alarm.latitude }}, {{ alarm.longitude }}
                      </p>
                    </div>
                  </div>
                  <div v-else class="text-gray-500 text-center py-4">
                    点击"测试"按钮运行测试
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
          
          <el-row :gutter="20" class="mt-4">
            <el-col :span="12">
              <el-card class="h-full">
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-medium">处理告警测试</span>
                    <el-button @click="testProcessAlarm">测试</el-button>
                  </div>
                </template>
                <div class="test-result">
                  <div class="mb-4">
                    <label class="block mb-2">选择告警ID:</label>
                    <el-input v-model="alarmIdToProcess" placeholder="输入告警ID"></el-input>
                  </div>
                  <div v-if="processAlarm.loading" class="text-center py-4">
                    <i class="el-icon-loading"></i> 处理中...
                  </div>
                  <div v-else-if="processAlarm.error" class="text-red-500">
                    错误: {{ processAlarm.error }}
                  </div>
                  <div v-else-if="processAlarm.success" class="text-green-500">
                    成功处理告警ID: {{ alarmIdToProcess }}
                  </div>
                  <div v-else class="text-gray-500">
                    输入告警ID并点击"测试"按钮处理告警
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="12">
              <el-card class="h-full">
                <template #header>
                  <div class="flex items-center justify-between">
                    <span class="font-medium">综合测试结果</span>
                    <el-button @click="runAllTests">全部测试</el-button>
                  </div>
                </template>
                <div class="test-result">
                  <div class="space-y-4">
                    <div class="flex items-center">
                      <span class="w-32">告警类型接口:</span>
                      <el-tag :type="testResults.alarmTypes ? 'success' : 'danger'">
                        {{ testResults.alarmTypes ? '通过' : '失败' }}
                      </el-tag>
                    </div>
                    <div class="flex items-center">
                      <span class="w-32">告警信息接口:</span>
                      <el-tag :type="testResults.alarms ? 'success' : 'danger'">
                        {{ testResults.alarms ? '通过' : '失败' }}
                      </el-tag>
                    </div>
                    <div class="flex items-center">
                      <span class="w-32">处理告警接口:</span>
                      <el-tag :type="testResults.processAlarm ? 'success' : 'danger'">
                        {{ testResults.processAlarm ? '通过' : '失败' }}
                      </el-tag>
                    </div>
                  </div>
                  
                  <div class="mt-6 p-4 bg-blue-50 rounded">
                    <h3 class="font-medium mb-2">测试说明:</h3>
                    <ul class="text-sm text-gray-700 list-disc pl-5 space-y-1">
                      <li>点击各个测试按钮分别测试对应的API接口</li>
                      <li>点击"全部测试"按钮运行所有测试</li>
                      <li>处理告警测试需要输入一个有效的告警ID</li>
                      <li>测试结果会显示在右侧综合测试结果区域</li>
                    </ul>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ApiTest',
  data() {
    return {
      alarmTypes: {
        loading: false,
        error: null,
        data: null
      },
      alarms: {
        loading: false,
        error: null,
        data: null
      },
      processAlarm: {
        loading: false,
        error: null,
        success: false
      },
      alarmIdToProcess: '',
      testResults: {
        alarmTypes: false,
        alarms: false,
        processAlarm: false
      }
    }
  },
  methods: {
    async testAlarmTypes() {
      this.alarmTypes.loading = true
      this.alarmTypes.error = null
      try {
        // 使用代理路径而不是直接访问后端地址
        const response = await axios.get('/api/v1/alarmtypes/')
        this.alarmTypes.data = response.data
        this.testResults.alarmTypes = true
      } catch (error) {
        this.alarmTypes.error = error.message
        this.testResults.alarmTypes = false
      } finally {
        this.alarmTypes.loading = false
      }
    },
    
    async testAlarms() {
      this.alarms.loading = true
      this.alarms.error = null
      try {
        // 使用代理路径而不是直接访问后端地址
        const response = await axios.get('/api/v1/alarms/')
        this.alarms.data = response.data
        this.testResults.alarms = true
      } catch (error) {
        this.alarms.error = error.message
        this.testResults.alarms = false
      } finally {
        this.alarms.loading = false
      }
    },
    
    async testProcessAlarm() {
      if (!this.alarmIdToProcess) {
        this.processAlarm.error = '请输入告警ID'
        return
      }
      
      this.processAlarm.loading = true
      this.processAlarm.error = null
      this.processAlarm.success = false
      
      try {
        // 使用代理路径而不是直接访问后端地址
        await axios.patch(
          `/api/v1/alarms/${this.alarmIdToProcess}/`,
          {
            status: 'PROCESSING',
            handler: 'Frontend Test'
          }
        )
        this.processAlarm.success = true
        this.testResults.processAlarm = true
      } catch (error) {
        this.processAlarm.error = error.response?.data || error.message
        this.testResults.processAlarm = false
      } finally {
        this.processAlarm.loading = false
      }
    },
    
    async runAllTests() {
      await this.testAlarmTypes()
      await this.testAlarms()
      // 不自动运行处理告警测试，因为需要用户输入ID
    }
  }
}
</script>

<style scoped>
.test-result {
  min-height: 200px;
}
</style>