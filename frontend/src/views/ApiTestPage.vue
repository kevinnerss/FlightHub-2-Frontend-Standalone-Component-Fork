<template>
  <div class="api-test-page">
    <h1>大疆接口测试工具</h1>
    
    <!-- 全局配置区域 -->
    <div class="global-config">
      <h2>全局配置</h2>
      <div class="config-form">
        <div class="form-item">
          <label for="apiBaseUrl">API基础URL:</label>
          <input v-model="globalConfig.apiBaseUrl" id="apiBaseUrl" type="text" placeholder="https://es-flight-api-cn.djigate.com" />
        </div>
        <div class="form-item">
          <label for="xUserToken">X-User-Token:</label>
          <input v-model="globalConfig.xUserToken" id="xUserToken" type="text" />
        </div>
        <div class="form-item">
          <label for="xProjectUuid">X-Project-Uuid:</label>
          <input v-model="globalConfig.xProjectUuid" id="xProjectUuid" type="text" />
        </div>
        <div class="form-item">
          <label for="xLanguage">X-Language:</label>
          <select v-model="globalConfig.xLanguage" id="xLanguage">
            <option value="zh">中文</option>
            <option value="en">英文</option>
          </select>
        </div>
        <div class="form-item" style="grid-column: 1 / -1; justify-self: end;">
          <button class="reset-button" @click="resetGlobalConfig">重置配置</button>
        </div>
      </div>
    </div>

    <!-- 接口测试区域 -->
    <div class="api-test-section">
      <h2>接口测试</h2>
      
      <!-- 接口类型选择 -->
      <div class="api-tabs">
        <button 
          v-for="tab in apiTabs" 
          :key="tab.key"
          :class="['tab-button', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          {{ tab.name }}
        </button>
      </div>

      <!-- 地图接口 -->
      <div v-if="activeTab === 'map'" class="api-content">
        <h3>地图接口</h3>
        
        <!-- 创建地图标注 -->
        <div class="interface-item">
          <h4>创建地图标注</h4>
          <div class="interface-params">
            <div class="form-item">
              <label for="mapElementName">标注名称 *:</label>
              <input v-model="mapInterfaces.createElement.name" id="mapElementName" type="text" placeholder="请输入标注名称" />
            </div>
            <div class="form-item">
              <label for="mapElementDesc">标注描述 *:</label>
              <input v-model="mapInterfaces.createElement.desc" id="mapElementDesc" type="text" placeholder="请输入标注描述" />
            </div>
            <div class="form-item">
              <label for="mapElementType">标注类型 *:</label>
              <select v-model="mapInterfaces.createElement.type" id="mapElementType">
                <option value="0">点</option>
                <option value="1">线</option>
                <option value="2">面</option>
              </select>
            </div>
            <div class="form-item">
              <label for="mapElementColor">标注颜色:</label>
              <input v-model="mapInterfaces.createElement.color" id="mapElementColor" type="color" />
            </div>
            <div class="form-item">
              <label for="mapElementClamp">是否贴地:</label>
              <input v-model="mapInterfaces.createElement.clampToGround" id="mapElementClamp" type="checkbox" />
            </div>
            
            <!-- 坐标设置 -->
            <div class="form-item" style="grid-column: 1 / -1;">
              <label>坐标设置:</label>
              <div class="coordinate-settings">
                <div class="form-item">
                  <label for="coordPreset">预设坐标:</label>
                  <select v-model="mapInterfaces.createElement.coordinatePreset" id="coordPreset">
                    <option value="custom">自定义</option>
                    <option value="demo1">示例1 (深圳大疆总部)</option>
                    <option value="demo2">示例2 (北京)</option>
                  </select>
                </div>
                
                <!-- 点坐标输入 -->
                <div v-if="mapInterfaces.createElement.type === '0'" class="point-coordinates">
                  <div class="form-item">
                    <label for="pointCoordX">经度 X:</label>
                    <input v-model="mapInterfaces.createElement.pointCoordX" id="pointCoordX" type="number" step="0.0000001" placeholder="经度" />
                  </div>
                  <div class="form-item">
                    <label for="pointCoordY">纬度 Y:</label>
                    <input v-model="mapInterfaces.createElement.pointCoordY" id="pointCoordY" type="number" step="0.0000001" placeholder="纬度" />
                  </div>
                  <div class="form-item">
                    <label for="pointCoordZ">高度 Z:</label>
                    <input v-model="mapInterfaces.createElement.pointCoordZ" id="pointCoordZ" type="number" step="0.1" placeholder="高度" />
                  </div>
                </div>
              </div>
            </div>
          </div>
          <button class="test-button" @click="testMapElementCreate">测试调用</button>
        </div>
        
        <!-- 获取地图标注列表（预留） -->
        <div class="interface-item">
          <h4>获取地图标注列表</h4>
          <div class="interface-params">
            <div class="form-item">
              <label for="page">页码:</label>
              <input v-model.number="mapInterfaces.getElementList.page" id="page" type="number" min="1" />
            </div>
            <div class="form-item">
              <label for="pageSize">每页数量:</label>
              <input v-model.number="mapInterfaces.getElementList.pageSize" id="pageSize" type="number" min="1" max="100" />
            </div>
          </div>
          <button class="test-button" @click="testGetElementList">测试调用</button>
        </div>
        
        <!-- 删除地图标注（预留） -->
        <div class="interface-item">
          <h4>删除地图标注</h4>
          <div class="interface-params">
            <div class="form-item">
              <label for="elementId">标注ID:</label>
              <input v-model="mapInterfaces.deleteElement.elementId" id="elementId" type="text" placeholder="请输入要删除的标注ID" />
            </div>
          </div>
          <button class="test-button" @click="testDeleteElement">测试调用</button>
        </div>
      </div>

      <!-- 飞行接口 -->
      <div v-if="activeTab === 'flight'" class="api-content">
        <h3>飞行接口</h3>
        
        <!-- 获取飞行任务信息 -->
        <div class="interface-item">
          <h4>获取飞行任务信息</h4>
          <div class="interface-params">
            <div class="form-item">
              <label for="taskUuid">任务UUID *:</label>
              <input v-model="flightInterfaces.getTaskInfo.taskUuid" id="taskUuid" type="text" placeholder="请输入任务UUID" />
            </div>
          </div>
          <div class="button-group">
            <button class="test-button" @click="testFlightTaskInfo">测试</button>
          </div>
        </div>
        
        <!-- 获取飞行任务列表 -->
        <div class="interface-item">
          <h4>获取飞行任务列表</h4>
          <div class="interface-params">
            <div class="form-item">
              <label for="sn">设备SN *:</label>
              <input v-model="flightInterfaces.getTaskList.sn" id="sn" type="text" placeholder="请输入设备SN" />
            </div>
            <div class="form-item">
              <label for="beginAt">任务开始时间戳 *:</label>
              <input v-model="flightInterfaces.getTaskList.beginAt" id="beginAt" type="number" placeholder="请输入任务开始时间戳" />
            </div>
            <div class="form-item">
              <label for="endAt">任务结束时间戳 *:</label>
              <input v-model="flightInterfaces.getTaskList.endAt" id="endAt" type="number" placeholder="请输入任务结束时间戳" />
            </div>
            <div class="form-item">
              <label for="taskType">任务类型:</label>
              <select v-model="flightInterfaces.getTaskList.taskType" id="taskType">
                <option value="">全部类型</option>
                <option value="immediate">立即任务</option>
                <option value="timed">单次定时任务</option>
                <option value="recurring">重复任务</option>
                <option value="continuous">连续任务</option>
              </select>
            </div>
          </div>
          <div class="button-group">
            <button class="test-button" @click="testFlightTaskList">测试</button>
          </div>
        </div>
        
        <!-- 获取飞行任务产生的媒体资源 -->
        <div class="interface-item">
          <h4>获取飞行任务产生的媒体资源</h4>
          <div class="interface-params">
            <div class="form-item">
               <label for="mediaTaskUuid">任务UUID *:</label>
               <input v-model="flightInterfaces.getTaskMedia.taskUuid" id="mediaTaskUuid" type="text" placeholder="请输入任务UUID" />
             </div>
          </div>
          <div class="button-group">
            <button class="test-button" @click="testGetTaskMedia">测试</button>
          </div>
        </div>

        <!-- 更新飞行任务状态 -->
        <div class="interface-item">
          <h4>更新飞行任务状态</h4>
          <div class="interface-params">
            <div class="form-item">
              <label for="updateTaskUuid">任务UUID *:</label>
              <input v-model="flightInterfaces.updateTaskStatus.taskUuid" id="updateTaskUuid" type="text" placeholder="请输入任务UUID" />
            </div>
            <div class="form-item">
              <label for="taskStatus">任务状态 *:</label>
              <select v-model="flightInterfaces.updateTaskStatus.status" id="taskStatus">
                <option value="suspended">任务挂起</option>
                <option value="restored">任务恢复</option>
              </select>
            </div>
          </div>
          <div class="button-group">
            <button class="test-button" @click="testUpdateTaskStatus">测试</button>
          </div>
        </div>

        <!-- 获取飞行任务轨迹信息 -->
        <div class="interface-item">
          <h4>获取飞行任务轨迹信息</h4>
          <div class="interface-params">
            <div class="form-item">
              <label for="trackTaskUuid">任务UUID *:</label>
              <input v-model="flightInterfaces.getTaskTrack.taskUuid" id="trackTaskUuid" type="text" placeholder="请输入任务UUID" />
            </div>
          </div>
          <div class="button-group">
            <button class="test-button" @click="testGetTaskTrack">测试</button>
          </div>
        </div>
      </div>

      <!-- 航线接口 -->
      <div v-if="activeTab === 'wayline'" class="api-content">
        <h3>航线接口</h3>
        
        <!-- 获取项目下的航线列表 -->
        <div class="interface-item">
          <h4>获取项目下的航线列表</h4>
          <div class="interface-params">
            <div class="form-item">
              <p>此接口不需要额外参数，使用全局配置中的项目编号</p>
            </div>
          </div>
          <div class="button-group">
            <button class="test-button" @click="testWaylineList">测试</button>
          </div>
        </div>
        
        <!-- 获取航线详情 -->
        <div class="interface-item">
          <h4>获取航线详情</h4>
          <div class="interface-params">
            <div class="form-item">
              <label for="waylineId">航线ID *:</label>
              <input v-model="waylineInterfaces.getWaylineDetail.waylineId" id="waylineId" type="text" placeholder="请输入航线ID" />
            </div>
          </div>
          <div class="button-group">
            <button class="test-button" @click="testWaylineDetail">测试</button>
          </div>
        </div>

        <!-- 航线上传完成通知 -->
        <div class="interface-item">
          <h4>航线上传完成通知</h4>
          <div class="interface-params">
            <div class="form-item">
              <label for="waylineName">航线名称 *:</label>
              <input v-model="waylineInterfaces.finishUpload.name" id="waylineName" type="text" placeholder="请输入航线名称" />
            </div>
            <div class="form-item">
              <label for="objectKey">航线存储对象标识 *:</label>
              <input v-model="waylineInterfaces.finishUpload.objectKey" id="objectKey" type="text" placeholder="请输入航线存储对象的唯一标识" />
            </div>
          </div>
          <div class="button-group">
            <button class="test-button" @click="testFinishUpload">测试</button>
          </div>
        </div>
      </div>

      <!-- 模型接口 -->
      <div v-if="activeTab === 'model'" class="api-content">
        <h3>模型接口</h3>
        
        <!-- 获取项目下的模型列表 -->
        <div class="interface-item">
          <h4>获取项目下的模型列表</h4>
          <div class="interface-params">
            <div class="form-item">
              <p>此接口不需要额外参数，使用全局配置中的项目编号</p>
            </div>
          </div>
          <div class="button-group">
            <button class="test-button" @click="testModelList">测试</button>
          </div>
        </div>
        
        <!-- 模型重建 -->
        <div class="interface-item">
          <h4>模型重建</h4>
          <div class="interface-params">
            <div class="form-item">
              <label for="modelName">模型名称 *:</label>
              <input v-model="modelInterfaces.createModel.name" id="modelName" type="text" placeholder="请输入模型名称" />
            </div>
            <div class="form-item">
              <label for="reconstructionType">重建类型 *:</label>
              <select v-model="modelInterfaces.createModel.reconstructionType" id="reconstructionType">
                <option value="model_2d">二维</option>
                <option value="model_3d">三维</option>
              </select>
            </div>
            <div class="form-item">
              <label for="simplifiedFactor">模型简化系数 *:</label>
              <input v-model="modelInterfaces.createModel.simplifiedFactor" id="simplifiedFactor" type="number" step="0.1" placeholder="建议设置为0.2" />
            </div>
            <div class="form-item">
              <label for="taskFolderId">任务文件夹ID *:</label>
              <input v-model="modelInterfaces.createModel.taskFolderId" id="taskFolderId" type="number" placeholder="飞行任务产生的资源文件夹编号" />
            </div>
            <div class="form-item">
              <label for="wkt">坐标系 *:</label>
              <input v-model="modelInterfaces.createModel.wkt" id="wkt" type="text" placeholder="例如: EPSG:32649" />
            </div>
            <div class="form-item">
              <label for="qualityLevel">重建质量 *:</label>
              <select v-model="modelInterfaces.createModel.qualityLevel" id="qualityLevel">
                <option value="high">高质量</option>
                <option value="medium">中质量</option>
                <option value="low">低质量</option>
              </select>
            </div>
            <div class="form-item">
              <label for="reconstructionMode">建图场景 *:</label>
              <select v-model="modelInterfaces.createModel.reconstructionMode" id="reconstructionMode">
                <option value="normal">普通模式</option>
                <option value="surround">环绕模式</option>
              </select>
            </div>
            <div class="form-item" style="grid-column: 1 / -1;">
              <label>生成模型格式 *:</label>
              <div class="checkbox-group">
                <label>
                  <input type="checkbox" v-model="modelInterfaces.createModel.generateModelFormats" value="b3dm" />
                  b3dm (mesh模型：默认生成以在司空中显示)
                </label>
                <label>
                  <input type="checkbox" v-model="modelInterfaces.createModel.generateModelFormats" value="osgb" />
                  osgb (mesh模型：LOD模型格式)
                </label>
                <label>
                  <input type="checkbox" v-model="modelInterfaces.createModel.generateModelFormats" value="ply" />
                  ply (mesh模型：非LOD模型格式)
                </label>
                <label>
                  <input type="checkbox" v-model="modelInterfaces.createModel.generateModelFormats" value="obj" />
                  obj (mesh模型：非LOD模型格式)
                </label>
                <label>
                  <input type="checkbox" v-model="modelInterfaces.createModel.generateModelFormats" value="pnts" />
                  pnts (点云模型：默认生成以在司空显示)
                </label>
                <label>
                  <input type="checkbox" v-model="modelInterfaces.createModel.generateModelFormats" value="las" />
                  las (点云模型：ASPRS LASer格式)
                </label>
                <label>
                  <input type="checkbox" v-model="modelInterfaces.createModel.generateModelFormats" value="point_ply" />
                  point_ply (点云模型：非LOD点云格式)
                </label>
              </div>
            </div>
          </div>
          <div class="button-group">
            <button class="test-button" @click="testCreateModel">测试</button>
          </div>
        </div>
        
        <!-- 获取模型详情 -->
        <div class="interface-item">
          <h4>获取模型详情</h4>
          <div class="interface-params">
            <div class="form-item">
              <label for="modelId">模型ID *:</label>
              <input v-model="modelInterfaces.getModelDetail.modelId" id="modelId" type="text" placeholder="请输入模型ID" />
            </div>
          </div>
          <div class="button-group">
            <button class="test-button" @click="testModelDetail">测试</button>
          </div>
        </div>

        <!-- 获取模型文件下载链接 -->
        <div class="interface-item">
          <h4>获取模型文件下载链接</h4>
          <div class="interface-params">
            <div class="form-item">
              <label for="fileId">模型文件ID *:</label>
              <input v-model="modelInterfaces.getModelDownloadUrl.fileId" id="fileId" type="text" placeholder="请输入模型文件的唯一标识" />
            </div>
          </div>
          <div class="button-group">
            <button class="test-button" @click="testGetModelDownloadUrl">测试</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 结果展示区域 -->
    <div class="result-section">
      <div class="section-header">
        <h2>接口返回结果</h2>
        <div class="action-buttons">
          <button v-if="result || error" class="action-button" @click="clearResult">清除结果</button>
          <button v-if="result" class="action-button" @click="copyResult">复制结果</button>
        </div>
      </div>
      
      <!-- 请求信息 -->
      <div v-if="requestInfo" class="request-info">
        <h3>请求信息</h3>
        <pre>{{ formattedRequestInfo }}</pre>
      </div>
      
      <!-- 响应结果 -->
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="result" class="result">
        <h3>响应数据</h3>
        <div class="response-meta">
          <span class="meta-item">状态: {{ result.status }} {{ result.statusText }}</span>
          <span class="meta-item">响应时间: {{ result.responseTime }}</span>
        </div>
        <pre>{{ JSON.stringify(result.data, null, 2) }}</pre>
      </div>
      <div v-else-if="error" class="error">
        <h3>错误信息</h3>
        <pre>{{ error }}</pre>
      </div>
      <div v-else class="empty">请选择接口进行测试</div>
      
      <!-- 请求历史 -->
      <div v-if="requestHistory.length > 0" class="history-section">
        <h3>请求历史</h3>
        <div class="history-list">
          <div 
            v-for="item in requestHistory" 
            :key="item.id"
            class="history-item"
            :class="{ 'success': item.success, 'error': !item.success }"
          >
            <div class="history-info">
              <span class="method">{{ item.method }}</span>
              <span class="url">{{ item.url }}</span>
              <span class="timestamp">{{ item.timestamp }}</span>
            </div>
            <button class="retry-button" @click="reExecuteHistory(item)">重试</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ApiTestPage',
  data() {
    const savedConfig = localStorage.getItem('apiTestGlobalConfig');
    return {
      // 全局配置
      globalConfig: savedConfig 
        ? JSON.parse(savedConfig) 
        : {
            apiBaseUrl: 'https://es-flight-api-cn.djigate.com',
            xUserToken: '',
            xProjectUuid: '',
            xLanguage: 'zh'
          },
      
      
      // 标签页
      activeTab: 'map',
      apiTabs: [
        { key: 'map', name: '地图接口' },
        { key: 'flight', name: '飞行接口' },
        { key: 'wayline', name: '航线接口' },
        { key: 'model', name: '模型接口' }
      ],
      
      // 地图接口参数
      mapInterfaces: {
        createElement: {
          name: '',
          desc: '',
          type: '0', // 0:点, 1:线, 2:面
          color: '#2D8CF0',
          clampToGround: true,
          // 预设坐标选项
          coordinatePreset: 'custom',
          // 自定义坐标输入
          pointCoordX: '',
          pointCoordY: '',
          pointCoordZ: ''
        },
        // 预留其他地图接口的参数结构
        getElementList: {
          page: 1,
          pageSize: 20
        },
        deleteElement: {
          elementId: ''
        }
      },
      
      // 飞行接口参数
    flightInterfaces: {
      getTaskInfo: {
        taskUuid: ''
      },
      getTaskList: {
        sn: '',
        beginAt: Date.now() - 30 * 24 * 60 * 60 * 1000, // 默认30天前
        endAt: Date.now(), // 默认现在
        taskType: ''
      },
      getTaskMedia: {
        taskUuid: ''
      },
      updateTaskStatus: {
        taskUuid: '',
        status: 'restored' // suspended: 任务挂起, restored: 任务恢复
      },
      getTaskTrack: {
        taskUuid: ''
      }
    },
      
      // 航线接口参数
      waylineInterfaces: {
        getWaylineList: {
          page: 1,
          pageSize: 10
        },
        getWaylineDetail: {
          waylineId: ''
        },
        finishUpload: {
          name: '',
          objectKey: ''
        }
      },
      
      // 飞行任务媒体资源接口参数
      flightMediaInterfaces: {
        getTaskMedia: {
          taskUuid: ''
        }
      },
      
      // 模型接口参数
      modelInterfaces: {
        createModel: {
          name: '',
          reconstructionType: 'model_3d',
          simplifiedFactor: 0.2,
          taskFolderId: '',
          wkt: 'EPSG:32649',
          qualityLevel: 'high',
          reconstructionMode: 'normal',
          generateModelFormats: ['b3dm']
        },
        getModelDetail: {
          modelId: ''
        },
        getModelDownloadUrl: {
          fileId: ''
        }
      },
      
      // 结果状态
      loading: false,
      result: null,
      error: null,
      requestInfo: null,
      requestHistory: []
    }
  },
  watch: {
    // 监听全局配置变化并保存到localStorage
    globalConfig: {
      handler(newConfig) {
        localStorage.setItem('apiTestGlobalConfig', JSON.stringify(newConfig));
      },
      deep: true
    }
  },
  computed: {
    formattedResult() {
      return this.result ? JSON.stringify(this.result, null, 2) : '';
    },
    formattedRequestInfo() {
      return this.requestInfo ? JSON.stringify(this.requestInfo, null, 2) : '';
    }
  },
  methods: {
    // 通用API调用方法
    async callApi(endpoint, method = 'GET', params = null, data = null) {
      try {
        // 重置状态
        this.loading = true;
        this.error = null;
        this.result = null;
        
        // 验证全局配置
        if (!this.globalConfig.apiBaseUrl) {
          throw new Error('请配置API基础URL');
        }
        if (!this.globalConfig.xProjectUuid) {
          throw new Error('请配置项目编号(X-Project-Uuid)');
        }
        
        // 构建请求头
        const headers = {
          'Content-Type': 'application/json',
          'X-Language': this.globalConfig.xLanguage
        };
        
        // 添加可选的认证头
        if (this.globalConfig.xUserToken) {
          headers['X-User-Token'] = this.globalConfig.xUserToken;
        }
        if (this.globalConfig.xProjectUuid) {
          headers['X-Project-Uuid'] = this.globalConfig.xProjectUuid;
        }
        
        // 构建完整URL
        let url = `${this.globalConfig.apiBaseUrl}${endpoint}`;
        let fullUrl = url;
        
        // 添加查询参数
        if (params) {
          // 过滤空值参数
          const filteredParams = Object.fromEntries(
            Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== '')
          );
          
          if (Object.keys(filteredParams).length > 0) {
            const queryParams = new URLSearchParams(filteredParams);
            fullUrl += `?${queryParams.toString()}`;
          }
        }
        
        // 构建请求选项
        const options = {
          method,
          headers
        };
        
        // 添加请求体
        if (data) {
          options.body = JSON.stringify(data);
        }
        
        // 记录请求信息
        this.requestInfo = {
          method,
          url: fullUrl,
          headers,
          params: method === 'GET' ? params : null,
          data: method !== 'GET' ? data : null,
          timestamp: new Date().toLocaleString()
        };
        
        // 发送请求
        const startTime = performance.now();
        const response = await fetch(fullUrl, options);
        const endTime = performance.now();
        
        // 获取响应头
        const responseHeaders = {};
        response.headers.forEach((value, key) => {
          responseHeaders[key] = value;
        });
        
        // 检查响应状态
        if (!response.ok) {
          // 尝试获取错误响应体
          try {
            const errorBody = await response.json();
            const errorMessage = errorBody.message || errorBody.error || JSON.stringify(errorBody, null, 2);
            throw new Error(`HTTP错误! 状态码: ${response.status}\n${errorMessage}`);
          } catch (jsonError) {
            throw new Error(`HTTP错误! 状态码: ${response.status}`);
          }
        }
        
        // 解析响应
        let resultData;
        try {
          resultData = await response.json();
        } catch (e) {
          throw new Error('无法解析响应数据，可能是非JSON格式');
        }
        
        this.result = {
          data: resultData,
          responseTime: `${(endTime - startTime).toFixed(2)} ms`,
          status: response.status,
          statusText: response.statusText,
          headers: responseHeaders
        };
        
        // 添加到请求历史
        this.addToHistory({
          id: Date.now(),
          method,
          url: fullUrl,
          success: true,
          timestamp: new Date().toLocaleString(),
          requestInfo: this.requestInfo,
          response: this.result
        });
        
      } catch (err) {
        const errorMessage = `请求失败: ${err.message}`;
        this.error = errorMessage;
        this.result = null;
        
        // 记录错误请求信息
        if (!this.requestInfo) {
          this.requestInfo = {
            method,
            url: `${this.globalConfig.apiBaseUrl || '未配置'}${endpoint}`,
            error: errorMessage,
            timestamp: new Date().toLocaleString()
          };
        }
        
        // 错误也添加到历史
        this.addToHistory({
          id: Date.now(),
          method,
          url: `${this.globalConfig.apiBaseUrl || '未配置'}${endpoint}`,
          success: false,
          timestamp: new Date().toLocaleString(),
          requestInfo: this.requestInfo,
          error: errorMessage
        });
      } finally {
        this.loading = false;
      }
    },
    
    // 添加到请求历史
    addToHistory(isError = false) {
      const historyItem = {
        id: Date.now(),
        method: this.requestInfo?.method || '',
        url: this.requestInfo?.url || '',
        timestamp: new Date().toLocaleString(),
        success: !isError
      };
      
      this.requestHistory.unshift(historyItem);
      // 限制历史记录数量
      if (this.requestHistory.length > 20) {
        this.requestHistory.pop();
      }
    },
    
    // 复制结果到剪贴板
    async copyResult() {
      try {
        await navigator.clipboard.writeText(this.formattedResult);
        alert('结果已复制到剪贴板');
      } catch (err) {
        console.error('复制失败:', err);
        alert('复制失败，请手动复制');
      }
    },
    
    // 重新执行历史请求
    reExecuteHistory() {
      // 从历史记录中查找完整请求信息
      // 这里简化处理，实际应用中可以保存更详细的请求参数
      alert('重新执行功能需要进一步实现');
    },
    
    // 地图接口测试
    async testMapElementCreate() {
      const { name, desc, type, color, clampToGround, coordinatePreset, pointCoordX, pointCoordY, pointCoordZ } = this.mapInterfaces.createElement
      
      // 验证必填字段
      if (!name || !desc) {
        this.error = '请填写必填字段：标注名称和标注描述';
        this.loading = false;
        return;
      }
      
      // 准备坐标数据
      let coordinates = null;
      const typeNum = parseInt(type);
      
      // 根据类型和预设生成坐标
      if (typeNum === 0) { // 点
        if (coordinatePreset === 'demo1') {
          coordinates = [113.940253, 22.542886, 0]; // 深圳大疆总部附近
        } else if (coordinatePreset === 'demo2') {
          coordinates = [116.397470, 39.909230, 0]; // 北京
        } else if (pointCoordX && pointCoordY) {
          coordinates = [parseFloat(pointCoordX), parseFloat(pointCoordY), pointCoordZ ? parseFloat(pointCoordZ) : 0];
        } else {
          coordinates = [108.42625652534299, 30.59263023356542, 0]; // 默认坐标
        }
      } else if (typeNum === 1) { // 线
        coordinates = [[108.426, 30.592, 0], [108.427, 30.593, 0]];
      } else if (typeNum === 2) { // 面
        coordinates = [[[108.426, 30.592, 0], [108.427, 30.592, 0], [108.427, 30.593, 0], [108.426, 30.593, 0], [108.426, 30.592, 0]]];
      }
      
      // 准备请求数据
      const data = {
        name,
        desc,
        element_source: 0, // 保留字段
        resource: {
          type: typeNum,
          content: {
            type: 'Feature',
            properties: {
              color,
              clampToGround
            },
            geometry: {
              type: typeNum === 0 ? 'Point' : typeNum === 1 ? 'LineString' : 'Polygon',
              coordinates
            }
          }
        }
      }
      
      await this.callApi('/openapi/v0.1/map/element', 'POST', null, data)
    },
    
    // 获取地图标注列表
    async testGetElementList() {
      const { page, pageSize } = this.mapInterfaces.getElementList;
      await this.callApi('/openapi/v0.1/map/element/list', 'GET', {
        page,
        page_size: pageSize
      });
    },
    
    // 删除地图标注
    async testDeleteElement() {
      const { elementId } = this.mapInterfaces.deleteElement;
      if (!elementId) {
        this.error = '请输入标注ID';
        this.loading = false;
        return;
      }
      await this.callApi(`/openapi/v0.1/map/element/${elementId}`, 'DELETE');
    },
    
    // 飞行接口测试
    async testFlightTaskInfo() {
      const { taskUuid } = this.flightInterfaces.getTaskInfo
      if (!taskUuid) {
        this.error = '请输入任务UUID';
        this.loading = false;
        return;
      }
      await this.callApi(`/openapi/v0.1/flight-task/${taskUuid}`, 'GET')
    },
    
    async testGetTaskMedia() {
      const { taskUuid } = this.flightInterfaces.getTaskMedia;
      
      if (!taskUuid) {
        this.error = '请输入任务UUID';
        this.loading = false;
        return;
      }
      
      try {
        this.error = null;
        this.loading = true;
        await this.callApi(`/openapi/v0.1/flight-task/${taskUuid}/media`, 'GET', null, null)
      } catch (error) {
        this.error = error.message || '调用失败';
      } finally {
        this.loading = false;
      }
    },

    // 更新飞行任务状态
    async testUpdateTaskStatus() {
      const { taskUuid, status } = this.flightInterfaces.updateTaskStatus;
      
      if (!taskUuid) {
        this.error = '请输入任务UUID';
        this.loading = false;
        return;
      }
      
      const data = {
        status
      };
      
      await this.callApi(`/openapi/v0.1/flight-task/${taskUuid}/status`, 'PUT', null, data);
    },

    // 获取飞行任务轨迹信息
    async testGetTaskTrack() {
      const { taskUuid } = this.flightInterfaces.getTaskTrack;
      
      if (!taskUuid) {
        this.error = '请输入任务UUID';
        this.loading = false;
        return;
      }
      
      await this.callApi(`/openapi/v0.1/flight-task/${taskUuid}/track`, 'GET');
    },
    
    async testFlightTaskList() {
      const { sn, beginAt, endAt } = this.flightInterfaces.getTaskList
      await this.callApi('/openapi/v0.1/flight-task/list', 'GET', {
        sn,
        begin_at: beginAt,
        end_at: endAt
      })
    },
    
    // 航线接口测试
    async testWaylineList() {
      await this.callApi('/openapi/v0.1/wayline', 'GET')
    },
    
    async testWaylineDetail() {
      const { waylineId } = this.waylineInterfaces.getWaylineDetail
      if (!waylineId) {
        this.error = '请输入航线ID';
        this.loading = false;
        return;
      }
      await this.callApi(`/openapi/v0.1/wayline/${waylineId}`, 'GET')
    },

    // 航线上传完成通知
    async testFinishUpload() {
      const { name, objectKey } = this.waylineInterfaces.finishUpload;
      
      if (!name) {
        this.error = '请输入航线名称';
        this.loading = false;
        return;
      }
      
      if (!objectKey) {
        this.error = '请输入航线存储对象标识';
        this.loading = false;
        return;
      }
      
      const data = {
        name,
        object_key: objectKey
      };
      
      await this.callApi('/openapi/v0.1/wayline/finish-upload', 'POST', null, data);
    },
    
    // 模型接口测试
    async testModelList() {
      await this.callApi('/openapi/v0.1/model', 'GET')
    },
    
    async testCreateModel() {
      const { name, reconstructionType, simplifiedFactor, taskFolderId, wkt, qualityLevel, reconstructionMode, generateModelFormats } = this.modelInterfaces.createModel
      
      // 参数验证
      if (!name) {
        this.error = '请输入模型名称';
        this.loading = false;
        return;
      }
      if (!reconstructionType) {
        this.error = '请选择重建类型';
        this.loading = false;
        return;
      }
      if (!simplifiedFactor && simplifiedFactor !== 0) {
        this.error = '请输入模型简化系数';
        this.loading = false;
        return;
      }
      if (!taskFolderId && taskFolderId !== 0) {
        this.error = '请输入任务文件夹ID';
        this.loading = false;
        return;
      }
      if (!wkt) {
        this.error = '请输入坐标系';
        this.loading = false;
        return;
      }
      if (!qualityLevel) {
        this.error = '请选择重建质量';
        this.loading = false;
        return;
      }
      if (!reconstructionMode) {
        this.error = '请选择建图场景';
        this.loading = false;
        return;
      }
      if (!generateModelFormats || generateModelFormats.length === 0) {
        this.error = '请至少选择一种生成模型格式';
        this.loading = false;
        return;
      }
      
      const data = {
        name,
        reconstruction_type: [reconstructionType], // 接口需要数组格式
        simplified_factor: simplifiedFactor,
        task_folder_id: taskFolderId,
        wkt,
        quality_level: qualityLevel,
        reconstruction_mode: reconstructionMode,
        generate_model_formats: generateModelFormats
      }
      
      await this.callApi('/openapi/v0.1/model/create', 'POST', null, data)
    },
    
    async testModelDetail() {
      const { modelId } = this.modelInterfaces.getModelDetail
      
      // 参数验证
      if (!modelId) {
        this.error = '请输入模型ID';
        this.loading = false;
        return;
      }
      
      await this.callApi(`/openapi/v0.1/model/${modelId}`, 'GET')
    },

    // 获取模型文件下载链接
    async testGetModelDownloadUrl() {
      const { fileId } = this.modelInterfaces.getModelDownloadUrl
      
      // 参数验证
      if (!fileId) {
        this.error = '请输入模型文件ID';
        this.loading = false;
        return;
      }
      
      await this.callApi(`/openapi/v0.1/model/download-url/${fileId}/`, 'GET')
    },
    
    // 重置全局配置
    resetGlobalConfig() {
      this.globalConfig = {
        apiBaseUrl: 'https://es-flight-api-cn.djigate.com',
        xUserToken: '',
        xProjectUuid: '',
        xLanguage: 'zh'
      };
      localStorage.removeItem('apiTestGlobalConfig');
    },
    
    // 清除当前结果
    clearResult() {
      this.result = null;
      this.error = null;
      this.requestInfo = null;
    }
  }
}
</script>

<style scoped>
.api-test-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1, h2, h3, h4 {
  color: #333;
}

/* 全局配置区域 */
.global-config {
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.config-form {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

/* 接口测试区域 */
.api-test-section {
  margin-bottom: 20px;
}

.api-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tab-button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background-color: #fff;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s;
}

.tab-button:hover {
  background-color: #f0f0f0;
}

.tab-button.active {
  background-color: #409eff;
  color: white;
  border-color: #409eff;
}

.api-content {
  padding: 20px;
  background-color: #fafafa;
  border-radius: 8px;
}

.interface-item {
  margin-bottom: 20px;
  padding: 15px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #eee;
}

.interface-params {
  margin: 10px 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.coordinate-settings {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.point-coordinates {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-item label {
  font-weight: bold;
  font-size: 14px;
}

.form-item input, .form-item select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.test-button {
  padding: 8px 16px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.test-button:hover {
  background-color: #66b1ff;
}

.reset-button {
  padding: 8px 16px;
  background-color: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.reset-button:hover {
  background-color: #f78989;
}

/* 结果展示区域 */
.result-section {
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  min-height: 200px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.action-button {
  padding: 6px 12px;
  background-color: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.action-button:hover {
  background-color: #85ce61;
}

.request-info {
  background-color: #ecf5ff;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #d9ecff;
  margin-bottom: 15px;
}

.request-info h3 {
  margin-top: 0;
  color: #409eff;
  font-size: 16px;
}

.request-info pre {
  margin: 10px 0 0 0;
  white-space: pre-wrap;
  word-break: break-all;
  background-color: white;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #eee;
}

.result, .error, .loading, .empty {
  background-color: white;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #eee;
  min-height: 150px;
}

.result h3, .error h3 {
  margin-top: 0;
  font-size: 16px;
}

.result h3 {
  color: #67c23a;
}

.error h3 {
  color: #f56c6c;
}

.response-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
  font-size: 14px;
  color: #606266;
}

.meta-item {
  padding: 2px 8px;
  background-color: #f5f7fa;
  border-radius: 3px;
}

.result pre, .error pre {
  margin: 10px 0 0 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.error {
  border-color: #fbc4c4;
}

.error pre {
  color: #f56c6c;
}

.loading {
  text-align: center;
  line-height: 150px;
  color: #909399;
}

.empty {
  text-align: center;
  line-height: 150px;
  color: #909399;
}

/* 历史记录样式 */
.history-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.history-section h3 {
  margin-top: 0;
  font-size: 16px;
  color: #606266;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin-bottom: 8px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #eee;
  cursor: pointer;
  transition: all 0.3s;
}

.history-item:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.history-item.success {
  border-left: 3px solid #67c23a;
}

.history-item.error {
  border-left: 3px solid #f56c6c;
}

.history-info {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
  overflow: hidden;
}

.method {
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 3px;
  background-color: #409eff;
  color: white;
  font-size: 12px;
  min-width: 40px;
  text-align: center;
}

.url {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

.timestamp {
  font-size: 12px;
  color: #909399;
}

.retry-button {
  padding: 4px 8px;
  background-color: #909399;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

.retry-button:hover {
  background-color: #a6a9ad;
}
</style>