<template>
  <div class="app-container">
    <!-- 导航栏 - 高级科技风格 -->
    <div v-if="isAuthenticated" class="premium-nav-bar">
      <div class="nav-content">
        <!-- Logo区域 -->
        <div class="logo-section">
          <div class="logo-icon">
            <img
                src="@/assets/logo.png"
                alt="沈阳地铁低空智能巡检平台 Logo"
                class="logo-img"
            />
          </div>
          <span class="logo-text">沈阳地铁低空智能巡检平台</span>
        </div>

        <!-- 导航菜单 -->
        <nav class="nav-menu">
          <router-link
              to="/main-view"
              class="nav-item"
              :class="{ active: $route.path === '/main-view' }"
          >
            <span class="nav-icon">
              <img :src="homeIcon" class="nav-icon-img" alt="首页" />
            </span>
            <span class="nav-label">首页</span>
          </router-link>

          <router-link
              to="/"
              class="nav-item"
              :class="{ active: $route.path === '/' }"
          >
            <span class="nav-icon">
              <img :src="dashboardIcon" class="nav-icon-img" alt="主控台" />
            </span>
            <span class="nav-label">主控台</span>
          </router-link>

          <router-link
              to="/alarm-management"
              class="nav-item"
              :class="{ active: $route.path === '/alarm-management' }"
          >
            <span class="nav-icon">
              <img :src="alarmIcon" class="nav-icon-img" alt="告警管理" />
            </span>
            <span class="nav-label">告警管理</span>
          </router-link>

          <router-link
              to="/alarm-stats"
              class="nav-item"
              :class="{ active: $route.path === '/alarm-stats' }"
          >
            <span class="nav-icon">
              <img :src="alarmStatsIcon" class="nav-icon-img" alt="告警统计" />
            </span>
            <span class="nav-label">告警统计</span>
          </router-link>

          <router-link
              to="/carousel-detection"
              class="nav-item"
              :class="{ active: $route.path === '/carousel-detection' }"
          >
            <span class="nav-icon">
              <img :src="detectIcon" class="nav-icon-img" alt="AI检测" />
            </span>
            <span class="nav-label">AI检测</span>
          </router-link>

          <router-link
              to="/create-flight-task"
              class="nav-item"
              :class="{ active: $route.path === '/create-flight-task' }"
          >
            <span class="nav-icon">➕</span>
            <span class="nav-label">创建任务</span>
          </router-link>

          <router-link
              to="/inspect-task-management"
              class="nav-item"
              :class="{ active: $route.path === '/inspect-task-management' }"
          >
            <span class="nav-icon">
              <img :src="inspectTaskIcon" class="nav-icon-img" alt="巡检任务" />
            </span>
            <span class="nav-label">巡检任务</span>
          </router-link>

          <router-link
              v-if="isAdmin"
              to="/user-management"
              class="nav-item"
              :class="{ active: $route.path === '/user-management' }"
          >
            <span class="nav-icon">
              <img :src="userManagementIcon" class="nav-icon-img" alt="人员管理" />
            </span>
            <span class="nav-label">人员管理</span>
          </router-link>

        </nav>

        <!-- 用户信息区域 -->
        <div class="user-section">
          <div class="user-info">
            <div class="user-avatar">
              {{ currentUserName.charAt(0).toUpperCase() }}
            </div>
            <div class="user-details">
              <div class="user-name">{{ currentUserName }}</div>
              <div v-if="isAdmin" class="user-role">系统管理员</div>
              <div v-else class="user-role">普通用户</div>
            </div>
          </div>
          <button @click="handleLogout" class="logout-button">
            <span class="logout-icon">🚪</span>
            <span>退出</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script>
import detectIcon from '../pho/Common_AI检测.svg'
import dashboardIcon from '../pho/主控台.svg'
import homeIcon from '../pho/首页-copy.svg'
import alarmIcon from '../pho/告警管理_实时告警.svg'
import alarmStatsIcon from '../pho/告警统计.svg'
import inspectTaskIcon from '../pho/巡检任务.svg'
import userManagementIcon from '../pho/人员管理.svg'

export default {
  name: "App",
  data() {
    return {
      detectIcon,
      dashboardIcon,
      homeIcon,
      alarmIcon,
      alarmStatsIcon,
      inspectTaskIcon,
      userManagementIcon,
      isAuthenticated: false,
      isAdmin: false,
      currentUserName: "",
    };
  },
  created() {
    console.log("App 组件已创建");
    this.updateAuthStatus();
  },
  mounted() {
    console.log("App 组件已挂载");

    // 监听路由变化，更新认证状态
    this.$router.afterEach(() => {
      this.updateAuthStatus();
    });
  },
  methods: {
    updateAuthStatus() {
      const token = localStorage.getItem("token");
      const userInfoStr = localStorage.getItem("userInfo");

      this.isAuthenticated = !!token;

      if (userInfoStr) {
        try {
          const userInfo = JSON.parse(userInfoStr);
          this.currentUserName = userInfo.name || userInfo.username;
          this.isAdmin = userInfo.role === "admin";
        } catch (e) {
          console.error("解析用户信息失败:", e);
          this.currentUserName = "";
          this.isAdmin = false;
        }
      } else {
        this.currentUserName = "";
        this.isAdmin = false;
      }
    },
    async handleLogout() {
      try {
        await this.$store.dispatch("logout");
        localStorage.removeItem("userInfo");
        this.isAuthenticated = false;
        this.isAdmin = false;
        this.currentUserName = "";
        this.$router.push("/login");
      } catch (error) {
        console.error("登出失败:", error);
        localStorage.removeItem("token");
        localStorage.removeItem("userInfo");
        this.$router.push("/login");
      }
    },
  },
};
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
  "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 应用容器 */
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0a0e27 100%);
  background-attachment: fixed;
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.app-container::before {
  content: "";
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(
      circle at 20% 30%,
      rgba(0, 212, 255, 0.08) 0%,
      transparent 50%
  ),
  radial-gradient(
      circle at 80% 70%,
      rgba(168, 85, 247, 0.06) 0%,
      transparent 50%
  );
  pointer-events: none;
  z-index: 0;
}

/* 高级导航栏 */
.premium-nav-bar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(26, 31, 58, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 212, 255, 0.1);
}

.nav-content {
  max-width: 1920px;
  margin: 0 auto;
  padding: 0 32px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
}

/* Logo区域 */
.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.logo-icon {
  width: 80px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 0 8px rgba(0, 212, 255, 0.4));
  animation: pulse 3s ease-in-out infinite;
}

.logo-img {
  width: 100%;
  height: 100%;
  display: block;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
}

/* 导航菜单 */
.nav-menu {
  display: flex;
  gap: 8px;
  flex: 1;
  justify-content: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 10px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
      135deg,
      rgba(0, 212, 255, 0.1) 0%,
      rgba(0, 153, 255, 0.1) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.nav-item:hover {
  color: #e2e8f0;
  transform: translateY(-1px);
}

.nav-item:hover::before {
  opacity: 1;
}

.nav-item.active {
  color: #00d4ff;
  background: linear-gradient(
      135deg,
      rgba(0, 212, 255, 0.15) 0%,
      rgba(0, 153, 255, 0.15) 100%
  );
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.2),
  inset 0 0 20px rgba(0, 212, 255, 0.1);
}

.nav-item.active::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 20px;
  right: 20px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, transparent);
  box-shadow: 0 0 8px rgba(0, 212, 255, 0.8);
}

.nav-icon {
  font-size: 18px;
  filter: grayscale(50%);
  transition: filter 0.3s ease;
}

.nav-icon-img {
  width: 18px;
  height: 18px;
  display: block;
  filter: invert(1) brightness(1.6);
}

.nav-item:hover .nav-icon,
.nav-item.active .nav-icon {
  filter: grayscale(0%);
}

.nav-label {
  position: relative;
  z-index: 1;
}

/* 用户信息区域 */
.user-section {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: rgba(42, 47, 74, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(0, 212, 255, 0.1);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  color: #e2e8f0;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.2;
}

.user-role {
  color: #00d4ff;
  font-size: 12px;
  line-height: 1.2;
}

/* 退出按钮 */
.logout-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: transparent;
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 10px;
  color: #ef4444;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-button:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.logout-icon {
  font-size: 16px;
}

/* 主内容区域 */
.main-content {
  position: relative;
  z-index: 1;
  min-height: calc(100vh - 72px);
  padding: 24px;
}

/* 全局滚动条 */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: rgba(26, 31, 58, 0.3);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
  border-radius: 5px;
  border: 2px solid rgba(26, 31, 58, 0.3);
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #00e5ff 0%, #00aaff 100%);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .nav-content {
    padding: 0 20px;
  }

  .user-info {
    display: none;
  }
}

@media (max-width: 768px) {
  .nav-content {
    flex-wrap: wrap;
    height: auto;
    padding: 16px;
    gap: 16px;
  }

  .nav-menu {
    width: 100%;
    justify-content: flex-start;
    overflow-x: auto;
  }

  .nav-item {
    white-space: nowrap;
  }

  .logo-text {
    display: none;
  }
}
</style>
