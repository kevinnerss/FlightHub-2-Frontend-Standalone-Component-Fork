# 机场状态监控组件 - 部署和使用指南

## 📋 概述

已成功创建了一个完整的机场状态实时监控系统，可以通过 MQTT 消息动态更新机场状态，并在前端实时展示。

---

## 🚀 部署步骤

### 1. 后端部署

#### 1.1 生成数据库迁移文件

```bash
cd dji_command_root
python manage.py makemigrations
python manage.py migrate
```

#### 1.2 创建超级用户（如果还没有）

```bash
python manage.py createsuperuser
```

#### 1.3 启动 Django 服务

```bash
python manage.py runserver 0.0.0.0:8000
```

#### 1.4 启动 MQTT 监听服务

在另一个终端窗口中：

```bash
python manage.py mqtt_listener
```

---

### 2. 前端部署

#### 2.1 安装依赖（如果还没有）

```bash
cd frontend
npm install
```

#### 2.2 启动开发服务器

```bash
npm run serve
```

---

## 📁 已创建的文件清单

### 后端文件

1. **数据模型** - `dji_command_root/telemetry_app/models.py`
   - 添加了 `DockStatus` 模型（第 397-473 行）

2. **序列化器** - `dji_command_root/telemetry_app/serializers.py`
   - 添加了 `DockStatusSerializer`（第 454-495 行）

3. **视图** - `dji_command_root/telemetry_app/views.py`
   - 添加了 `DockStatusViewSet`（第 3305-3441 行）
   - 包含以下 API 端点：
     - `GET /api/v1/dock-status/` - 获取机场列表
     - `GET /api/v1/dock-status/all_docks/` - 获取所有机场
     - `GET /api/v1/dock-status/online_docks/` - 获取在线机场
     - `GET /api/v1/dock-status/{id}/` - 获取单个机场详情
     - `GET /api/v1/dock-status/{id}/history/` - 获取历史记录
     - `GET /api/v1/dock-status/statistics/` - 获取统计信息

4. **URL 路由** - `dji_command_root/telemetry_app/urls.py`
   - 注册了 `dock-status` 路由（第 34 行）

5. **MQTT 监听器** - `dji_command_root/telemetry_app/management/commands/mqtt_listener.py`
   - 增强了 `handle_position_data` 方法（第 235-320 行）
   - 添加了 `update_dock_status` 方法（第 322-446 行）
   - 自动识别机场设备（SN 以 8 开头）

### 前端文件

1. **API 服务** - `frontend/src/api/dockStatusApi.js`
   - 提供机场状态相关的 API 调用方法

2. **Vue 组件** - `frontend/src/components/DockStatusPanel.vue`
   - 完整的机场状态监控面板组件

---

## 🎯 核心功能

### 1. MQTT 自动更新机制

- ✅ 监听 MQTT topic: `thing/product/{机场SN}/osd`
- ✅ 自动识别机场设备（SN 以 8 开头）
- ✅ 实时更新数据库中的机场状态
- ✅ 支持多个机场同时监控

### 2. 机场状态数据

**环境信息：**
- 环境温度
- 机场内部温度
- 湿度
- 风速
- 降雨量

**硬件状态：**
- 舱盖状态（开/关）
- 推杆状态
- 补光灯状态
- 急停状态

**电源信息：**
- 供电电压
- 工作电压/电流
- 备用电池状态

**无人机状态：**
- 是否在舱内
- 充电状态
- 电池电量

**网络与存储：**
- 网络类型/质量/速率
- 存储使用情况

**任务统计：**
- 任务次数
- 累计工作时长
- 激活时间

### 3. 前端展示功能

**统计卡片：**
- 📊 机场总数
- ✅ 在线机场数
- ❌ 离线机场数
- ⚠️ 告警机场数

**机场卡片：**
- 实时状态指示器（在线/离线）
- 核心参数快速预览
- 告警标识
- 最后更新时间

**详情弹窗：**
- 完整的机场信息展示
- 分类展示各项参数
- 美观的 UI 设计

**自动刷新：**
- 每 30 秒自动刷新数据
- 手动刷新按钮

---

## 📊 MQTT 数据格式示例

根据您提供的日志，机场 MQTT 消息格式如下：

```json
{
  "gateway": "8UUXN4900A052C",
  "timestamp": 1767932168841,
  "data": {
    "network_state": {
      "type": 2,
      "quality": 0,
      "rate": 749
    },
    "drone_charge_state": {
      "state": 0,
      "capacity_percent": 95
    },
    "drone_in_dock": 1,
    "rainfall": 0,
    "wind_speed": 0,
    "environment_temperature": 3.9,
    "temperature": 27.1,
    "humidity": 23,
    "latitude": 41.72815646837488,
    "longitude": 123.25647700918904,
    "height": 62.8761329650879,
    "mode_code": 4,
    "cover_state": 1,
    "storage": {
      "total": 53082240,
      "used": 15064
    },
    "job_number": 48,
    "acc_time": 16505229,
    "electric_supply_voltage": 226,
    "working_voltage": 47040,
    "working_current": 2270,
    "backup_battery": {
      "voltage": 12338,
      "temperature": 19.6,
      "switch": 1
    }
  }
}
```

---

## 🔧 如何在页面中使用组件

### 方式一：在现有页面中集成

在 `frontend/src/views/MainView.vue` 或其他页面中：

```vue
<template>
  <div class="main-view">
    <!-- 其他内容 -->

    <DockStatusPanel />

    <!-- 其他内容 -->
  </div>
</template>

<script>
import DockStatusPanel from '@/components/DockStatusPanel.vue'

export default {
  name: 'MainView',
  components: {
    DockStatusPanel
  }
}
</script>
```

### 方式二：创建独立路由页面

在 `frontend/src/router/index.js` 中添加路由：

```javascript
{
  path: '/dock-status',
  name: 'DockStatus',
  component: () => import('@/components/DockStatusPanel.vue')
}
```

---

## 🧪 测试步骤

### 1. 测试后端 API

```bash
# 获取机场列表
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/v1/dock-status/all_docks/

# 获取统计信息
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/v1/dock-status/statistics/
```

### 2. 测试 MQTT 自动更新

1. 确保 MQTT 监听服务正在运行
2. 查看日志输出，应该能看到：
   ```
   🏭 识别为机场设备: 8UUXN4900A052C
   ✅ 机场状态创建成功！8UUXN4900A052C
   ```
3. 访问后台管理界面检查数据：
   ```
   http://localhost:8000/admin/telemetry_app/dockstatus/
   ```

### 3. 测试前端组件

1. 访问集成了组件的页面
2. 应该能看到：
   - 统计卡片显示数据
   - 机场卡片列表
   - 点击卡片可以查看详情

---

## 🎨 界面预览

### 统计卡片
- 紫色渐变：机场总数
- 绿色渐变：在线机场
- 橙色渐变：离线机场
- 粉色渐变：告警机场

### 机场卡片
- 绿色边框：在线机场
- 橙色边框：离线机场（半透明）
- 红色边框：有告警的机场
- 右上角红色徽章：告警提示

### 详情弹窗
- 分为 6 个区块：
  1. 基本信息
  2. 环境参数
  3. 电源状态
  4. 硬件状态
  5. 无人机信息
  6. 网络与存储

---

## 🔍 故障排查

### 问题1：机场数据不更新

**检查项：**
1. MQTT 监听服务是否运行？
   ```bash
   ps aux | grep mqtt_listener
   ```

2. 查看 MQTT 日志输出
   ```bash
   python manage.py mqtt_listener --debug
   ```

3. 检查机场 SN 是否以 8 开头

### 问题2：前端显示空数据

**检查项：**
1. 是否已登录并获取 token？
2. 检查浏览器控制台的网络请求
3. 检查 API 响应状态码

### 问题3：数据库错误

**解决方案：**
```bash
# 重新生成迁移文件
python manage.py makemigrations telemetry_app

# 应用迁移
python manage.py migrate
```

---

## 📚 API 文档

### 获取所有机场
```
GET /api/v1/dock-status/all_docks/
Response: Array of DockStatus objects
```

### 获取在线机场
```
GET /api/v1/dock-status/online_docks/
Response: Array of online DockStatus objects
```

### 获取机场统计
```
GET /api/v1/dock-status/statistics/
Response: {
  "total_docks": 2,
  "online_docks": 2,
  "offline_docks": 0,
  "alarm_docks": 0,
  "average_job_number": 29.0,
  "total_accumulated_time_seconds": 32998854,
  "total_accumulated_time_hours": 9166.35
}
```

### 获取单个机场详情
```
GET /api/v1/dock-status/{id}/
Response: Single DockStatus object
```

---

## 🎉 完成！

您的机场状态监控系统已经部署完成！现在可以：

1. ✅ 实时监控多个机场的状态
2. ✅ 查看环境、硬件、电源等全方位信息
3. ✅ 自动接收 MQTT 消息并更新数据库
4. ✅ 在美观的界面中展示机场信息
5. ✅ 快速识别在线/离线/告警状态

如有任何问题，请查看日志文件或联系技术支持。
