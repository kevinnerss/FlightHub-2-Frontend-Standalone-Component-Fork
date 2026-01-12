<template>
  <div class="main-view-container dashboard-grid">
    <!-- 左侧 -->
    <aside class="side-panel">
      <!--  设备列表-->
      <div class="glass-card">
        <div class="card-header">
          <h3>🛸 设备列表 (0{{ drones.length }})</h3>
        </div>
        <div class="device-list">
          <div
              v-for="drone in drones"
              :key="drone.id"
              class="drone-item hover-effect"
          >
            <div class="drone-info">
              <span class="name">{{ drone.name }}</span>
              <span class="status">{{ drone.status }}</span>
            </div>
            <div class="power-section">
              <span class="power-desc">电量</span>

              <div class="power-track">
                <div
                    class="power-fill"
                    :style="{
                    width: drone.power + '%',
                    background: drone.color,
                  }"
                ></div>
              </div>

              <div class="power-label" :style="{ color: drone.color }">
                {{ drone.power }}%
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 巡检航线 -->
      <div class="glass-card">
        <div class="card-header">
          <div class="header-title-wrapper">
            <div class="title-main">
              <h3>🚀 巡检航线</h3>
            </div>
            <router-link to="/inspect-task-management" class="more-btn">
              <span>更多</span>
            </router-link>
          </div>
        </div>
        <div class="wayline-scroll-area">
          <div
              v-for="item in showWaylines"
              :key="item.wayline_id"
              class="wayline-card hover-effect"
          >
            <div class="card-left">
              <div class="wayline-title-group">
                <span class="id-badge">{{ item.wayline_id }}</span>
                <span class="name-text">{{ item.name }}</span>
              </div>
              <div class="wayline-sub">
                <span class="desc-preview">{{ item.description }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- 中部 -->
    <section class="center-stage">
      <!-- 地图 -->
      <div class="glass-card twin-viewport">
        <img src="@/assets/map.gif" class="map-gif-bg" alt="Map Grid" />
      </div>

      <!-- 实时流媒体展示 -->
      <div class="bottom-media">
        <div class="glass-card hero-card hover-effect">
          <div class="hero-overlay"></div>
          <div class="hero-content">
            <div class="hero-header">
              <div>
                <p class="hero-label">安全运行天数</p>
                <div class="hero-number">
                  {{ safetyStats.safetyDays }}
                  <span class="hero-unit">天</span>
                </div>
              </div>
              <span class="hero-tag">近一年</span>
            </div>
            <div class="hero-summary">
              <div v-for="status in safetyStatuses" :key="status.label" class="summary-chip">
                <span class="chip-dot" :style="{ background: status.color }"></span>
                <span class="chip-label">{{ status.label }}</span>
                <span class="chip-value">{{ status.value }}</span>
              </div>
            </div>
            <div class="hero-summary">
              <div v-for="status in safetyStatuses" :key="status.label" class="summary-chip">
                <span class="chip-dot" :style="{ background: status.color }"></span>
                <span class="chip-label">{{ status.label }}</span>
                <span class="chip-value">{{ status.value }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 航迹回放 -->
        <div class="glass-card playback-card">
          <div class="card-header">
            <h3>🎞️ 航迹回放</h3>
          </div>
          <div class="playback-content">
            <div class="playback-ui">
              <button class="btn-play-large" />
            </div>
            <div class="time-stamp-v2">2026-01-06 14:20:05</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 右侧 -->
    <aside class="side-panel">
      <!-- 环境与飞行参数 -->
      <div class="glass-card">
        <div class="card-header">
          <div class="header-title-wrapper">
            <div class="title-main">
              <h3>📋 巡检任务/ID={{ showTaskId }}</h3>
            </div>
            <router-link to="/inspect-task-management" class="more-btn">
              <span>更多</span>
            </router-link>
          </div>
        </div>

        <div class="task-table">
          <div class="table-header">
            <span class="col-name">巡检子任务</span>
            <span class="col-type">巡检类型</span>
            <span class="col-time">巡检时间</span>
          </div>

          <div class="table-body">
            <div
                v-for="task in showSubTasks"
                :key="task.id"
                class="table-row hover-effect"
            >
              <div class="col-name text-emphasis">
                {{ task.wayline_details?.name || "--" }}
              </div>
              <div class="col-type">
                <span class="type-tag">{{
                    task.detect_category_name || "未设置"
                  }}</span>
              </div>
              <div class="col-time">{{ formatDate(task.started_at) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 异常告警 -->
      <div class="glass-card alarm-card">
        <div class="card-header">
          <div class="header-title-wrapper">
            <div class="title-main">
              <h3>🚨 异常告警</h3>
            </div>
            <router-link to="/alarm-management" class="more-btn">
              <span>更多</span>
            </router-link>
          </div>
        </div>
        <div v-for="alarm in showAlarms" :key="alarm.id">
          <div class="alarm-msg critical hover-effect">
            <div class="alarm-inner">
              <div>
                <div class="msg-t">{{ alarm.content || "未填写描述" }}</div>
                <div class="msg-d">
                  <span>时间:{{ formatDateTime(alarm.created_at) }}</span>
                  <span> | </span>
                  <span>航线:{{ resolveWaylineName(alarm) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script>
import alarmApi from "../api/alarmApi";
import waylineApi from "@/api/waylineApi";
import inspectTaskApi from "@/api/inspectTaskApi";
import { ElMessage } from "element-plus";

export default {
  name: "MainView",
  data() {
    return {
      loading: true,
      showNum: 3, // 首页展示数据数目
      drones: [
        {
          id: 1,
          name: "UAV-Alpha-01",
          status: "执行任务中",
          power: 88,
          color: "#38bdf8",
        },
        {
          id: 2,
          name: "UAV-Beta-02",
          status: "待机中",
          power: 100,
          color: "#10b981",
        },
        {
          id: 3,
          name: "UAV-Gamma-03",
          status: "维护中",
          power: 42,
          color: "#f59e0b",
        },
        {
          id: 4,
          name: "UAV-Delta-04",
          status: "待机中",
          power: 95,
          color: "#10b981",
        },
      ],
      showAlarms: [],
      showWaylines: [],
      waylineNameMap: {},
      showTaskId: 0,
      showSubTasks: [],
      safetyStats: {
        safetyDays: 0,
        todayAlarms: 0,
        monthAlarms: 0,
        totalAlarms: 0,
      },
    };
  },
  computed: {
    safetyStatuses() {
      return [
        { label: "今日异常", value: this.safetyStats.todayAlarms, color: "#38bdf8" },
        { label: "近月异常", value: this.safetyStats.monthAlarms, color: "#a855f7" },
        { label: "全年异常", value: this.safetyStats.totalAlarms, color: "#22c55e" },
      ];
    },
  },
  mounted() {
    this.loadData();
  },
  methods: {
    async loadData() {
      this.loading = true;
      try {
        await Promise.all([
          this.getAlarms(),
          this.loadWaylines(),
          this.loadTask(),
          this.loadSafetyStats(),
        ]);
      } catch (err) {
        console.error("加载告警统计失败", err);
      } finally {
        this.loading = false;
      }
    },
    async loadSafetyStats() {
      try {
        const latest = await this.fetchLatestCreatedAt();
        const anchor = latest || new Date();
        const start = new Date(anchor.getFullYear(), anchor.getMonth() - 11, 1, 0, 0, 0, 0);
        const end = new Date(anchor.getFullYear(), anchor.getMonth() + 1, 0, 23, 59, 59, 999);
        const alarms = await this.fetchAllAlarms({
          page_size: 20000,
          start_date: this.formatDateParam(start),
          end_date: this.formatDateParam(end),
        });
        this.buildSafetyStatsFromAlarms(alarms, start);
      } catch (err) {
        console.warn("加载安全运行天数失败", err);
        this.safetyStats = {
          safetyDays: 0,
          todayAlarms: 0,
          monthAlarms: 0,
          totalAlarms: 0,
        };
      }
    },
    async fetchAllAlarms(baseParams) {
      const pageSize = baseParams.page_size || 20000;
      let page = 1;
      const collected = [];
      let hasNext = true;
      let totalCount = null;
      while (hasNext) {
        const res = await alarmApi.getAlarms({ ...baseParams, page, page_size: pageSize });
        const list = this.normalizeList(res);
        collected.push(...list);

        if (totalCount === null && res && typeof res.count === "number") {
          totalCount = res.count;
        }

        const hasNextFlag = Boolean(res && res.next);
        const needByCount = totalCount !== null ? collected.length < totalCount : false;
        const needBySize = list.length === pageSize;

        hasNext = hasNextFlag || needByCount || needBySize;
        if (!hasNext) break;
        page += 1;
      }
      return collected;
    },
    async fetchLatestCreatedAt() {
      const res = await alarmApi.getAlarms({ page_size: 1, ordering: "-created_at" });
      const list = this.normalizeList(res);
      if (list.length && list[0].created_at) {
        return this.parsePlainDate(list[0].created_at);
      }
      return null;
    },
    buildSafetyStatsFromAlarms(alarms, windowStart = null) {
      const todayKey = this.formatDateParam(new Date());
      const todayAlarms = alarms.filter((item) => this.formatDateParam(this.parsePlainDate(item.created_at)) === todayKey).length;
      const monthAlarms = alarms.filter((item) => this.isInCurrentMonth(item.created_at)).length;
      const totalAlarms = alarms.length;

      const latest = alarms.reduce((latestTs, alarm) => {
        const ts = this.parsePlainDate(alarm.created_at);
        if (Number.isNaN(ts.getTime())) return latestTs;
        if (!latestTs) return ts;
        return ts > latestTs ? ts : latestTs;
      }, null);

      const dayMs = 1000 * 60 * 60 * 24;
      let safetyDays = 0;
      if (latest) {
        safetyDays = Math.max(Math.floor((Date.now() - latest.getTime()) / dayMs), 0);
      } else if (windowStart instanceof Date && !Number.isNaN(windowStart.getTime())) {
        safetyDays = Math.max(Math.floor((Date.now() - windowStart.getTime()) / dayMs), 0);
      }

      this.safetyStats = {
        safetyDays,
        todayAlarms,
        monthAlarms,
        totalAlarms,
      };
    },
    isInCurrentMonth(dateLike) {
      const dt = this.parsePlainDate(dateLike);
      const now = new Date();
      return dt.getFullYear() === now.getFullYear() && dt.getMonth() === now.getMonth();
    },
    formatDateParam(date) {
      const dt = this.parsePlainDate(date);
      const pad = (num) => String(num).padStart(2, "0");
      return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}`;
    },
    parsePlainDate(dateLike) {
      if (typeof dateLike === "string") {
        const parts = this.parseDateParts(dateLike);
        if (parts) return this.buildDateFromParts(parts);
      }
      return new Date(dateLike);
    },
    parseDateParts(dateLike) {
      if (typeof dateLike !== "string") return null;
      const raw = dateLike.trim();
      const cleaned = raw.replace(/([+-]\d{2}:?\d{2}|Z)$/i, "");
      const match = cleaned.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d+))?)?/);
      if (!match) return null;
      const [, y, m, d, h, mi, s, ms = "0"] = match;
      return {
        year: Number(y),
        month: Number(m),
        day: Number(d),
        hour: Number(h),
        minute: Number(mi),
        second: Number(s || 0),
        milli: Number(String(ms).padEnd(3, "0").slice(0, 3)),
      };
    },
    buildDateFromParts(parts) {
      return new Date(parts.year, parts.month - 1, parts.day, parts.hour, parts.minute, parts.second, parts.milli || 0);
    },
    // 获取要展示的告警信息
    async getAlarms() {
      try {
        const res = await alarmApi.getAlarms({ page: 1, page_size: 10 });
        const list = this.normalizeList(res);
        if (list.length > this.showNum) {
          this.showAlarms = list.slice(0, this.showNum);
        } else {
          this.showAlarms = list;
        }
      } catch (err) {
        console.warn("加载告警列表失败，使用空列表", err);
      }
    },
    // 获取航线信息
    async loadWaylines() {
      try {
        const response = await waylineApi.getWaylines({});
        const list = response?.results || [];
        this.waylineNameMap = list.reduce((acc, item) => {
          if (item && item.wayline_id !== undefined && item.wayline_id !== null) {
            acc[item.wayline_id] = item.name || `航线${item.wayline_id}`;
          }
          return acc;
        }, {});
        if (list.length > this.showNum) {
          this.showWaylines = list.slice(0, this.showNum);
        } else {
          this.showWaylines = list;
        }
      } catch (error) {
        console.error("加载航线列表失败:", error);
      }
    },
    // 获取任务信息
    async loadTask() {
      try {
        const response = await inspectTaskApi.getInspectTasks({
          page: 1,
          page_size: 10,
        });
        const allTasks = response?.results || [];
        // 获取第一个任务->无 parent_task 的代表任务
        const task = allTasks.find((item) => !item.parent_task);
        if (!task) {
          this.showTaskId = 0;
          this.showSubTasks = [];
          return;
        }
        this.showTaskId = task.id;
        await this.loadSubTask(task.id);
      } catch (error) {
        console.error("加载巡检任务失败:", error);
        ElMessage.error("加载巡检任务失败");
      } finally {
        this.loading = false;
      }
    },
    // 获取子任务信息
    async loadSubTask(taskId) {
      try {
        const res = await inspectTaskApi.getSubTasks(taskId);
        this.showSubTasks = Array.isArray(res) ? res : res?.results || [];
      } catch (error) {
        console.error("加载子任务失败:", error);
        ElMessage.error("加载子任务失败");
      }
    },
    normalizeList(res) {
      if (!res) return [];
      if (Array.isArray(res)) return res;
      if (res.results) return res.results;
      if (res.data) return res.data;
      return [];
    },
    formatDateTime(dateLike) {
      if (typeof dateLike === "string") {
        const trimmed = dateLike.trim().replace("T", " ");
        const noMs = trimmed.split(".")[0];
        return noMs || trimmed;
      }
      const dt = this.parsePlainDate(dateLike);
      if (Number.isNaN(dt.getTime())) return "--";
      const pad = (num) => String(num).padStart(2, "0");
      return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(
          dt.getDate()
      )} ${pad(dt.getHours())}:${pad(dt.getMinutes())}`;
    },
    formatDate(dateString) {
      if (!dateString) return "--";
      const date = new Date(dateString);
      return date.toLocaleString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      });
    },
    resolveWaylineName(alarm) {
      const id = this.resolveWaylineId(alarm);
      return (
          alarm?.wayline?.name ||
          alarm?.wayline_details?.name ||
          (this.waylineNameMap ? this.waylineNameMap[id] : undefined) ||
          (id ? `航线${id}` : "未知航线")
      );
    },
    resolveWaylineId(alarm) {
      return (
          alarm?.wayline_id ??
          alarm?.wayline?.id ??
          alarm?.wayline?.wayline_id ??
          alarm?.wayline_details?.id ??
          alarm?.wayline_details?.wayline_id ??
          null
      );
    },
  },
};
</script>

<style scoped>
/* 基础容器 */
.main-view-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: calc(100vh - 120px);
  padding-bottom: 50px;
  box-sizing: border-box;
  animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 玻璃卡片 */
.glass-card {
  background: rgba(30, 41, 59, 0.45);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  font-size: 15px;
  color: #f1f5f9;
  margin: 0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 320px 1fr 340px;
  gap: 20px;
  flex: 1;
  align-items: stretch;
}

.side-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.side-panel > .glass-card:last-child {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.hover-effect {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

/* 设备列表 */
.device-list {
  padding: 10px 20px 20px;
  max-height: 400px;
  overflow-y: auto;
}

.drone-item {
  padding: 12px 15px;
  margin-bottom: 4px;
  border-radius: 6px;
  border: 1px solid transparent;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.drone-item:hover:not(.active-drone) {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
}

.drone-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.drone-info .name {
  font-size: 14px;
  color: #e2e8f0;
  font-weight: 500;
}
.drone-info .status {
  font-size: 12px;
  color: #64748b;
}

.power-section {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.power-desc {
  font-size: 11px;
  color: #94a3b8;
  white-space: nowrap;
  flex-shrink: 0;
}

.power-track {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: hidden;
}

.power-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.8s ease;
}

.power-label {
  font-size: 12px;
  font-weight: bold;
  width: 35px;
  text-align: right;
  flex-shrink: 0;
}

/* 巡检航线 */
.wayline-scroll-area {
  padding: 12px;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.wayline-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.wayline-card:hover {
  background: rgba(56, 189, 248, 0.08);
  border-color: rgba(56, 189, 248, 0.3);
  transform: translateX(5px);
  box-shadow: -5px 0 15px rgba(56, 189, 248, 0.1);
}

.wayline-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  min-width: 0;
  width: 100%;
  overflow: hidden;
}

.name-text {
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.id-badge {
  background: rgba(56, 189, 248, 0.15);
  border: 1px solid rgba(56, 189, 248, 0.3);
  color: #38bdf8;
  font-family: "JetBrains Mono", "Monaco", monospace;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  letter-spacing: 0.5px;
  flex-shrink: 0;
  box-shadow: inset 0 0 4px rgba(56, 189, 248, 0.1);
}

.wayline-sub {
  padding-left: 2px;
}

.desc-preview {
  font-size: 12px;
  color: #94a3b8;
  opacity: 0.8;
  display: block;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.desc-preview {
  font-size: 11px;
  color: #64748b;
  max-width: 180px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.slider-info .label {
  font-size: 12px;
  color: #94a3b8;
}
.slider-info .val {
  font-size: 18px;
  color: #38bdf8;
  font-weight: bold;
  font-family: "Orbitron", sans-serif;
}
.slider-info small {
  font-size: 10px;
  margin-left: 2px;
  color: #64748b;
}

/* 中间视口支撑 */
.center-stage {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.twin-viewport {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.map-gif-bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.7;
  filter: brightness(0.8) contrast(1.2) saturate(0.8);
}

/* 底部媒体容器布局调整 */
.bottom-media {
  display: grid;
  grid-template-columns: 1.8fr 1.2fr;
  gap: 20px;
  height: 220px;
}

.hero-card {
  position: relative;
  background: linear-gradient(135deg, rgba(12, 74, 110, 0.85), rgba(30, 64, 175, 0.85));
  min-height: 220px;
  height: 100%;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 80% 20%, rgba(56, 189, 248, 0.35), transparent 45%),
    radial-gradient(circle at 20% 80%, rgba(94, 234, 212, 0.25), transparent 40%);
  filter: blur(10px);
  opacity: 0.8;
}

.hero-content {
  position: relative;
  padding: 22px 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  z-index: 1;
}

.hero-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.hero-label {
  color: #cbd5e1;
  font-size: 14px;
  letter-spacing: 1px;
}

.hero-number {
  font-size: 48px;
  font-weight: 800;
  color: #e0f2fe;
  text-shadow: 0 0 16px rgba(14, 165, 233, 0.7);
}

.hero-unit {
  font-size: 16px;
  color: #bae6fd;
  margin-left: 6px;
}

.hero-tag {
  padding: 8px 12px;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 999px;
  color: #e0f2fe;
  font-size: 12px;
}

.hero-summary {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.summary-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(15, 23, 42, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  color: #cbd5e1;
}

.chip-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
}

.chip-label {
  font-size: 13px;
}

.chip-value {
  font-size: 16px;
  font-weight: 700;
  color: #e2e8f0;
}

/* 实时载荷画面卡片 */
.video-card {
  position: relative;
  border: 1px solid rgba(56, 189, 248, 0.2);
  background: #000;
}

.media-tag {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  padding: 10px 15px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.8), transparent);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tag-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rec-dot {
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
  box-shadow: 0 0 10px #ef4444;
  animation: blink 1s infinite;
}

.tag-text {
  color: #ef4444;
  font-weight: bold;
  font-size: 12px;
}

.cam-info {
  color: #fff;
  font-size: 11px;
  letter-spacing: 1px;
  border-left: 1px solid rgba(255, 255, 255, 0.3);
  padding-left: 8px;
}

.stream-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.8;
}

/* 航迹回放卡片 */
.playback-card {
  background: rgba(15, 23, 42, 0.8);
  display: flex;
  flex-direction: column;
}

.playback-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 15px;
}

.playback-ui {
  display: flex;
  align-items: center;
  gap: 25px;
}

.btn-play-large {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(56, 189, 248, 0.1);
  border: 2px solid #38bdf8;
  color: #38bdf8;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
}

.btn-play-large:hover {
  background: #38bdf8;
  color: #fff;
  box-shadow: 0 0 25px rgba(56, 189, 248, 0.5);
  transform: scale(1.1);
}

.time-stamp-v2 {
  font-family: "Orbitron", sans-serif;
  color: #475569;
  font-size: 12px;
}

@keyframes blink {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
  100% {
    opacity: 1;
  }
}

/* 环境与飞行参数*/
.task-table {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 15px 15px;
  width: 100%;
  overflow-x: hidden;
}

.task-table .col-name,
.task-table .col-type,
.task-table .col-time {
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.table-header,
.table-row {
  width: 100%;
  box-sizing: border-box;
}

.table-body {
  overflow-x: hidden !important;
}

.col-name {
  flex: 1.5;
}
.col-type {
  flex: 1;
  text-align: center;
}
.col-time {
  flex: 1.2;
  text-align: right;
}

.table-header {
  display: flex;
  gap: 8px;
  padding: 10px 0;
  border-bottom: none;
}

.table-header span {
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.3);
  color: #38bdf8;
  font-size: 12px;
  font-weight: bold;
  padding: 6px 4px;
  border-radius: 4px;
  text-align: center;
  box-shadow: inset 0 0 8px rgba(56, 189, 248, 0.1);
}

.table-body {
  overflow-y: auto;
  max-height: 320px;
}

.table-row {
  display: flex;
  align-items: center;
  padding: 16px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.2s ease;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: rgba(56, 189, 248, 0.1);
  box-shadow: inset 4px 0 0 #38bdf8;
  transform: translateX(4px);
}

.text-emphasis {
  color: #f1f5f9;
  font-size: 14px;
  font-weight: 500;
}

.type-tag {
  display: inline-block;
  padding: 5px 12px;
  background: rgba(139, 92, 246, 0.2);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

.col-time {
  font-size: 14px;
  color: #f1f5f9;
}

/* 异常监测报警*/
.alarm-card {
  flex: 1; /* 自动撑开，填满底部 */
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(239, 68, 68, 0.2);
  background: rgba(15, 23, 42, 0.7);
  transition: all 0.3s ease;
  min-height: 0; /* 覆盖之前的 300px，允许自适应 */
}

.alarm-card .card-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.header-title-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.title-main {
  display: flex;
  align-items: center;
  gap: 8px;
}

.more-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 6px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.2);
  color: #00d4ff;
  font-size: 13px;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
}

.more-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
  transform: translateX(2px);
}

.alarm-msg.critical {
  margin: 15px;
  padding: 14px;
  background: rgba(239, 68, 68, 0.1);
  border-left: 4px solid #ef4444;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.alarm-msg.critical:hover {
  background: rgba(239, 68, 68, 0.2);
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.15);
  transform: translateX(4px); /* 向右微移增加警示感 */
}

.alarm-inner {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.msg-t {
  font-size: 14px;
  color: #fca5a5;
  font-weight: bold;
}

.msg-d {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

@keyframes alarm-blink {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
  100% {
    opacity: 1;
  }
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 5px;
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
</style>
