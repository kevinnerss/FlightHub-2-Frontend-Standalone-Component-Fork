<template>
  <div class="live-stream-player">
    <div class="player-header">
      <div class="header-left">
        <span class="stream-label">{{ streamName || '保护区直播' }}</span>
        <span v-if="isPlaying" class="live-badge">
          <span class="live-dot"></span>
          LIVE
        </span>
        <span v-if="isMonitoring" class="monitor-badge">
          <span class="monitor-dot"></span>
          检测中
        </span>
      </div>
      <div class="header-right">
        <!-- 检测控制按钮 -->
        <button 
          @click="toggleMonitor" 
          class="monitor-control-btn"
          :class="{ 'active': isMonitoring, 'loading': monitorLoading }"
          :disabled="monitorLoading"
          :title="isMonitoring ? '停止保护区检测' : '开始保护区检测'"
        >
          <svg v-if="!monitorLoading" viewBox="0 0 24 24" fill="currentColor">
            <path v-if="!isMonitoring" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            <path v-else d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11H7v-2h10v2z"/>
          </svg>
          <div v-else class="mini-spinner"></div>
          <span>{{ isMonitoring ? '停止检测' : '开始检测' }}</span>
        </button>
        
        <button @click="togglePlay" class="control-icon-btn" :title="isPlaying ? '暂停' : '播放'">
          <svg v-if="!isPlaying" viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
          </svg>
        </button>
        <button @click="toggleMute" class="control-icon-btn" :title="isMuted ? '取消静音' : '静音'">
          <svg v-if="!isMuted" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor">
            <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
          </svg>
        </button>
        <button @click="reload" class="control-icon-btn" title="重新加载">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
          </svg>
        </button>
      </div>
    </div>

    <div ref="playerContainer" class="player-container" :class="{ 'loading': loading, 'error': hasError }">
      <!-- 视频元素 -->
      <video 
        ref="videoElement"
        class="video-element"
        :muted="isMuted"
        autoplay
        playsinline
        @loadstart="onLoadStart"
        @canplay="onCanPlay"
        @playing="onPlaying"
        @error="onError"
        @waiting="onWaiting"
      ></video>

      <!-- 加载中 -->
      <div v-if="loading" class="overlay loading-overlay">
        <div class="loading-spinner"></div>
        <p>正在连接直播流...</p>
      </div>

      <!-- 错误提示 -->
      <div v-if="hasError" class="overlay error-overlay">
        <div class="error-icon">⚠️</div>
        <p class="error-message">{{ errorMessage }}</p>
        <button @click="reload" class="reload-btn">重新加载</button>
      </div>

      <!-- 无流提示 -->
      <div v-if="!streamUrl && !loading && !hasError" class="overlay placeholder-overlay">
        <div class="placeholder-icon">📹</div>
        <p>等待直播流推送...</p>
      </div>
    </div>

    <div class="player-footer">
      <div class="stream-info">
        <span class="info-item">
          <span class="info-label">流地址:</span>
          <span class="info-value">{{ streamUrl || '未配置' }}</span>
        </span>
        <span v-if="isPlaying" class="info-item">
          <span class="info-label">状态:</span>
          <span class="info-value status-active">正在播放</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import liveMonitorApi from '../api/liveMonitorApi'

export default {
  name: 'LiveStreamPlayer',
  props: {
    // 流ID (例如: drone01, protection_zone_01)
    streamId: {
      type: String,
      default: 'drone01'
    },
    // 流名称显示
    streamName: {
      type: String,
      default: ''
    },
    // 是否自动播放
    autoPlay: {
      type: Boolean,
      default: true
    },
    // ZLM服务器地址（从配置中心获取或使用默认值）
    zlmServer: {
      type: String,
      default: 'http://192.168.10.10'
    }
  },
  data() {
    return {
      player: null,
      isPlaying: false,
      isMuted: false,
      loading: false,
      hasError: false,
      errorMessage: '',
      flvjs: null,
      // 监听状态
      isMonitoring: false,
      monitorLoading: false,
      monitorCheckTimer: null
    }
  },
  computed: {
    // HTTP-FLV 流地址
    streamUrl() {
      if (!this.streamId) return ''
      // ZLMediaKit 的 HTTP-FLV 地址格式: http://server/live/streamId.flv
      return `${this.zlmServer}/live/${this.streamId}.flv`
    }
  },
  mounted() {
    this.loadFlvJs()
    this.checkMonitorStatus()
    // 定时检查监听状态
    this.monitorCheckTimer = setInterval(() => {
      this.checkMonitorStatus()
    }, 5000)
  },
  beforeUnmount() {
    this.destroyPlayer()
    if (this.monitorCheckTimer) {
      clearInterval(this.monitorCheckTimer)
    }
  },
  methods: {
    // 动态加载 flv.js
    async loadFlvJs() {
      if (window.flvjs) {
        this.flvjs = window.flvjs
        if (this.autoPlay && this.streamUrl) {
          this.initPlayer()
        }
        return
      }

      this.loading = true
      try {
        // 从 CDN 加载 flv.js
        const script = document.createElement('script')
        script.src = 'https://cdn.jsdelivr.net/npm/flv.js@1.6.2/dist/flv.min.js'
        script.async = true
        
        await new Promise((resolve, reject) => {
          script.onload = () => {
            this.flvjs = window.flvjs
            resolve()
          }
          script.onerror = reject
          document.head.appendChild(script)
        })

        console.log('✅ flv.js 加载成功')
        if (this.autoPlay && this.streamUrl) {
          this.initPlayer()
        }
      } catch (err) {
        console.error('❌ flv.js 加载失败:', err)
        this.hasError = true
        this.errorMessage = 'flv.js 加载失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },

    // 初始化播放器
    initPlayer() {
      if (!this.flvjs || !this.streamUrl) {
        console.warn('flv.js 未加载或流地址为空')
        return
      }

      if (!this.flvjs.isSupported()) {
        this.hasError = true
        this.errorMessage = '您的浏览器不支持 FLV 播放'
        console.error('❌ 浏览器不支持 FLV')
        return
      }

      try {
        this.loading = true
        this.hasError = false

        // 销毁旧播放器
        this.destroyPlayer()

        // 创建 FLV 播放器
        this.player = this.flvjs.createPlayer({
          type: 'flv',
          url: this.streamUrl,
          isLive: true,
          hasAudio: true,
          hasVideo: true
        }, {
          enableWorker: false,
          enableStashBuffer: false,
          stashInitialSize: 128,
          autoCleanupSourceBuffer: true
        })

        // 绑定到 video 元素
        this.player.attachMediaElement(this.$refs.videoElement)

        // 监听事件
        this.player.on(this.flvjs.Events.ERROR, (errorType, errorDetail, errorInfo) => {
          console.error('FLV 播放器错误:', errorType, errorDetail, errorInfo)
          this.hasError = true
          this.loading = false
          this.isPlaying = false
          
          if (errorType === 'NetworkError') {
            this.errorMessage = '网络连接失败，请检查流服务器是否可访问'
          } else if (errorType === 'MediaError') {
            this.errorMessage = '媒体解码错误，流格式可能不正确'
          } else {
            this.errorMessage = `播放错误: ${errorDetail}`
          }
        })

        // 加载流
        this.player.load()

        // 自动播放
        if (this.autoPlay) {
          this.$refs.videoElement.play().then(() => {
            console.log('✅ 自动播放成功')
          }).catch(err => {
            console.warn('自动播放被阻止，需要用户交互:', err)
            this.loading = false
          })
        }

      } catch (err) {
        console.error('❌ 播放器初始化失败:', err)
        this.hasError = true
        this.errorMessage = '播放器初始化失败: ' + err.message
        this.loading = false
      }
    },

    // 销毁播放器
    destroyPlayer() {
      if (this.player) {
        try {
          this.player.pause()
          this.player.unload()
          this.player.detachMediaElement()
          this.player.destroy()
        } catch (err) {
          console.warn('销毁播放器时出错:', err)
        }
        this.player = null
      }
      this.isPlaying = false
    },

    // 切换播放/暂停
    togglePlay() {
      const video = this.$refs.videoElement
      if (!video) return

      if (this.isPlaying) {
        video.pause()
      } else {
        if (!this.player) {
          this.initPlayer()
        } else {
          video.play().catch(err => {
            console.error('播放失败:', err)
          })
        }
      }
    },

    // 切换静音
    toggleMute() {
      this.isMuted = !this.isMuted
      if (this.$refs.videoElement) {
        this.$refs.videoElement.muted = this.isMuted
      }
    },

    // 重新加载
    reload() {
      this.hasError = false
      this.errorMessage = ''
      this.destroyPlayer()
      setTimeout(() => {
        this.initPlayer()
      }, 300)
    },

    // 视频事件处理
    onLoadStart() {
      this.loading = true
      console.log('开始加载流...')
    },

    onCanPlay() {
      this.loading = false
      console.log('流加载完成，可以播放')
    },

    onPlaying() {
      this.loading = false
      this.isPlaying = true
      this.hasError = false
      console.log('正在播放')
    },

    onError(e) {
      console.error('视频元素错误:', e)
      if (!this.hasError) {
        this.hasError = true
        this.errorMessage = '视频加载失败'
      }
      this.loading = false
      this.isPlaying = false
    },

    onWaiting() {
      console.log('缓冲中...')
      // 直播流缓冲很正常，不显示 loading
    },

    // ======================================================================
    // 监听控制方法
    // ======================================================================

    async toggleMonitor() {
      if (this.monitorLoading) return

      if (this.isMonitoring) {
        await this.stopMonitor()
      } else {
        await this.startMonitor()
      }
    },

    async startMonitor() {
      this.monitorLoading = true
      try {
        const response = await liveMonitorApi.startMonitor(this.streamId, 3.0)
        console.log('✅ 监听已启动:', response)
        this.isMonitoring = true
        this.$emit('monitor-started', response)
      } catch (err) {
        console.error('❌ 启动监听失败:', err)
        const errorMsg = err.response?.data?.message || err.message || '启动失败'
        alert(`启动保护区检测失败: ${errorMsg}`)
      } finally {
        this.monitorLoading = false
      }
    },

    async stopMonitor() {
      this.monitorLoading = true
      try {
        const response = await liveMonitorApi.stopMonitor(this.streamId)
        console.log('✅ 监听已停止:', response)
        this.isMonitoring = false
        this.$emit('monitor-stopped', response)
      } catch (err) {
        console.error('❌ 停止监听失败:', err)
        const errorMsg = err.response?.data?.message || err.message || '停止失败'
        alert(`停止保护区检测失败: ${errorMsg}`)
      } finally {
        this.monitorLoading = false
      }
    },

    async checkMonitorStatus() {
      try {
        const status = await liveMonitorApi.getStatus(this.streamId)
        this.isMonitoring = status.is_running || false
      } catch (err) {
        // 静默失败，不影响用户使用
        console.warn('检查监听状态失败:', err)
      }
    }
  }
}
</script>

<style scoped>
.live-stream-player {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(10, 14, 39, 0.6);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(0, 212, 255, 0.2);
}

/* 播放器头部 */
.player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 153, 255, 0.1) 100%);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stream-label {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
}

.live-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: 12px;
  color: #ef4444;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.live-dot {
  width: 6px;
  height: 6px;
  background: #ef4444;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.monitor-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.4);
  border-radius: 12px;
  color: #10b981;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.monitor-dot {
  width: 6px;
  height: 6px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

.header-right {
  display: flex;
  gap: 8px;
}

.control-icon-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  background: rgba(26, 31, 58, 0.8);
  color: #00d4ff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.control-icon-btn svg {
  width: 18px;
  height: 18px;
}

.control-icon-btn:hover {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.5);
  transform: translateY(-1px);
}

/* 监听控制按钮 */
.monitor-control-btn {
  height: 32px;
  padding: 0 12px;
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 8px;
  background: rgba(26, 31, 58, 0.8);
  color: #10b981;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.monitor-control-btn svg {
  width: 16px;
  height: 16px;
}

.monitor-control-btn:hover:not(:disabled) {
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.5);
  transform: translateY(-1px);
}

.monitor-control-btn.active {
  background: rgba(16, 185, 129, 0.2);
  border-color: rgba(16, 185, 129, 0.5);
  color: #10b981;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
}

.monitor-control-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.mini-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(16, 185, 129, 0.2);
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

/* 播放器容器 */
.player-container {
  flex: 1;
  position: relative;
  background: #000;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* 覆盖层 */
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: rgba(10, 14, 39, 0.95);
  backdrop-filter: blur(10px);
  color: #e2e8f0;
  z-index: 10;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(0, 212, 255, 0.2);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon,
.placeholder-icon {
  font-size: 48px;
}

.error-message {
  font-size: 14px;
  color: #ef4444;
  text-align: center;
  margin: 0;
  max-width: 300px;
}

.reload-btn {
  padding: 8px 16px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  background: rgba(0, 212, 255, 0.15);
  color: #00d4ff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reload-btn:hover {
  background: rgba(0, 212, 255, 0.25);
  border-color: rgba(0, 212, 255, 0.5);
}

/* 播放器底部 */
.player-footer {
  padding: 10px 16px;
  background: rgba(10, 14, 39, 0.8);
  border-top: 1px solid rgba(0, 212, 255, 0.15);
}

.stream-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 12px;
}

.info-item {
  display: flex;
  gap: 6px;
}

.info-label {
  color: #94a3b8;
}

.info-value {
  color: #e2e8f0;
  font-family: 'Courier New', monospace;
}

.status-active {
  color: #10b981;
  font-weight: 600;
}

.placeholder-overlay p {
  color: #64748b;
  font-size: 14px;
  margin: 0;
}
</style>
