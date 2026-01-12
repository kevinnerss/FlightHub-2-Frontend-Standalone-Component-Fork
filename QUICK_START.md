# 🚀 机场监控页面 - 快速启动指南

## ✅ 已完成的工作

### 1. 创建了独立的机场监控页面
**文件位置**: [frontend/src/views/DockMonitor.vue](frontend/src/views/DockMonitor.vue)

**页面特点**:
- ✨ 美观的渐变背景
- 🎨 现代化的页面设计
- 📱 完全响应式布局
- 🔄 集成了 DockStatusPanel 组件

### 2. 配置了前端路由
**文件位置**: [frontend/src/router/index.js](frontend/src/router/index.js:119-127)

**路由配置**:
```javascript
{
  path: '/dock-monitor',
  name: 'DockMonitor',
  component: DockMonitor,
  meta: {
    title: '机场监控',
    requiresAuth: true  // 需要登录才能访问
  }
}
```

### 3. 添加了导航菜单项
**文件位置**: [frontend/src/App.vue](frontend/src/App.vue:95-102)

**菜单位置**: 在"巡检任务"和"人员管理"之间

---

## 🎯 如何访问

### 方式一：直接访问 URL
启动前端服务后，在浏览器中访问：
```
http://localhost:8080/dock-monitor
```

### 方式二：通过导航菜单
1. 登录系统
2. 在顶部导航栏找到 **🏭 机场监控** 菜单项
3. 点击即可进入

---

## 📸 页面预览

### 页面结构

```
┌─────────────────────────────────────────────┐
│  🏭 机场监控中心                             │
│  实时监控所有机场设备的运行状态              │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐      │
│  │ 📊   │ │ ✅   │ │ ❌   │ │ ⚠️   │      │
│  │ 总数 │ │ 在线 │ │ 离线 │ │ 告警 │      │
│  └──────┘ └──────┘ └──────┘ └──────┘      │
│                                             │
│  ┌─────────────┐  ┌─────────────┐         │
│  │ 机场卡片 1  │  │ 机场卡片 2  │         │
│  │ • 温度      │  │ • 温度      │         │
│  │ • 风速      │  │ • 风速      │         │
│  │ • 湿度      │  │ • 湿度      │         │
│  │ • 舱盖状态  │  │ • 舱盖状态  │         │
│  │ • 无人机    │  │ • 无人机    │         │
│  └─────────────┘  └─────────────┘         │
│                                             │
└─────────────────────────────────────────────┘
```

### 视觉特点

- **顶部区域**: 紫色渐变背景，白色半透明卡片
- **标题区域**: 大号标题 + 浮动动画图标
- **统计卡片**: 4种渐变色彩（紫色/绿色/橙色/粉色）
- **机场卡片**:
  - 绿色边框 = 在线机场
  - 橙色边框 = 离线机场
  - 红色边框 = 有告警的机场
  - 点击卡片可查看详情

---

## 🔧 启动步骤

### 1. 后端服务

```bash
# 终端 1 - 启动 Django
cd dji_command_root
python manage.py runserver 0.0.0.0:8000

# 终端 2 - 启动 MQTT 监听（重要！用于实时更新机场数据）
python manage.py mqtt_listener
```

### 2. 前端服务

```bash
# 终端 3 - 启动 Vue
cd frontend
npm run serve
```

### 3. 访问系统

1. 打开浏览器访问: `http://localhost:8080`
2. 登录系统
3. 点击导航栏的 **🏭 机场监控** 菜单

---

## 📊 功能特性

### 实时数据展示

✅ **环境监控**
- 环境温度
- 机场内部温度
- 湿度
- 风速
- 降雨量

✅ **硬件状态**
- 舱盖状态（开/关）
- 推杆状态
- 补光灯状态
- 急停状态

✅ **电源监控**
- 供电电压
- 工作电压/电流
- 功率计算
- 备用电池状态

✅ **无人机状态**
- 是否在舱内
- 充电状态
- 电池电量

✅ **网络与存储**
- 网络类型/质量
- 存储使用率

✅ **任务统计**
- 任务次数
- 累计工作时长
- 激活时间

### 交互功能

- 🔄 **自动刷新**: 每30秒自动更新数据
- 🖱️ **点击详情**: 点击机场卡片查看完整信息
- 🔍 **状态筛选**: 通过颜色快速识别机场状态
- 📱 **响应式**: 支持手机、平板、PC多端访问

---

## 🎨 UI 设计亮点

### 配色方案

1. **背景渐变**: 紫色到粉色（`#667eea → #764ba2`）
2. **统计卡片**:
   - 机场总数: 紫色渐变
   - 在线机场: 绿色渐变
   - 离线机场: 橙色渐变
   - 告警机场: 粉色渐变
3. **机场卡片边框**:
   - 在线: `#4CAF50` (绿色)
   - 离线: `#ff9800` (橙色)
   - 告警: `#f44336` (红色)

### 动画效果

- 标题图标浮动动画
- 在线指示器脉冲动画
- 刷新按钮旋转动画
- 卡片悬停上浮效果

---

## 🔍 数据来源

### MQTT 自动更新
机场数据通过 MQTT 实时推送：

```
Topic: thing/product/8UUXN4900A052C/osd
       ↓
MQTT Listener (mqtt_listener.py)
       ↓
识别机场设备 (SN以8开头)
       ↓
更新数据库 (DockStatus表)
       ↓
前端定时拉取 (每30秒)
       ↓
实时展示
```

### API 端点

前端通过以下 API 获取数据：

```javascript
// 获取所有机场
GET /api/v1/dock-status/all_docks/

// 获取统计信息
GET /api/v1/dock-status/statistics/

// 获取单个机场详情
GET /api/v1/dock-status/{id}/
```

---

## 📝 注意事项

### 1. 认证要求
- ⚠️ 页面需要登录后才能访问
- 未登录用户会被重定向到登录页

### 2. MQTT 服务
- ⚠️ 必须启动 MQTT 监听服务才能接收实时数据
- 命令: `python manage.py mqtt_listener`

### 3. 数据显示
- 首次访问可能没有数据（需要等待 MQTT 消息推送）
- 可以通过后台管理界面手动添加测试数据

### 4. 浏览器兼容性
- 推荐使用 Chrome、Edge、Firefox 最新版本
- 需要支持 CSS Grid 和 Flexbox

---

## 🐛 故障排查

### 问题1: 页面显示空白
**解决方案**:
1. 检查是否已登录
2. 查看浏览器控制台是否有错误
3. 确认后端服务正在运行

### 问题2: 没有机场数据
**解决方案**:
1. 检查 MQTT 监听服务是否运行
2. 查看 MQTT 日志是否有机场消息
3. 手动在后台添加测试数据

### 问题3: 数据不更新
**解决方案**:
1. 检查网络连接
2. 查看浏览器控制台的 API 请求
3. 确认后端 API 返回正常

---

## 📚 相关文件

### 前端文件
- 页面组件: `frontend/src/views/DockMonitor.vue`
- 状态组件: `frontend/src/components/DockStatusPanel.vue`
- API 服务: `frontend/src/api/dockStatusApi.js`
- 路由配置: `frontend/src/router/index.js`
- 导航菜单: `frontend/src/App.vue`

### 后端文件
- 数据模型: `dji_command_root/telemetry_app/models.py`
- API 视图: `dji_command_root/telemetry_app/views.py`
- 序列化器: `dji_command_root/telemetry_app/serializers.py`
- MQTT 监听: `dji_command_root/telemetry_app/management/commands/mqtt_listener.py`
- URL 路由: `dji_command_root/telemetry_app/urls.py`

---

## 🎉 完成！

您的机场监控页面已经准备就绪！

**快速访问**:
1. 启动所有服务
2. 访问 `http://localhost:8080/dock-monitor`
3. 享受实时监控！

有任何问题，请查看 [DOCK_STATUS_GUIDE.md](DOCK_STATUS_GUIDE.md) 获取更详细的文档。
