# HTTP 服务运行系统指南

本文档详细说明了如何在项目中运行和配置HTTP服务系统，基于现有的Django后端架构。

## 1. 现有HTTP服务架构概述

当前项目使用以下技术栈实现HTTP服务：

- **后端框架**：Django + Django REST Framework
- **数据库**：SQLite
- **API格式**：RESTful API
- **身份验证**：基于Token的认证机制
- **跨域支持**：已配置CORS中间件

## 2. 后端服务启动步骤

### 2.1 环境准备

1. **检查Python版本**：确保安装了Python 3.13.9

```bash
python --version
```

2. **激活虚拟环境**（推荐）

```bash
# Windows系统
venv\Scripts\activate
```

3. **安装依赖**

```bash
cd dji_command_root
pip install -r requirements.txt
pip install django-filter django-cors-headers
```

### 2.2 数据库迁移

首次运行或模型变更后需要执行：

```bash
cd dji_command_root
python manage.py migrate
```

### 2.3 启动开发服务器

```bash
# 启动在本地访问
python manage.py runserver 8000

# 或者启动在所有网络接口（便于局域网访问）
python manage.py runserver 0.0.0.0:8001
```

服务启动后可通过以下地址访问：
- `http://127.0.0.1:8000/`（本地访问）
- `http://<your-ip>:8001/`（局域网访问）

## 3. HTTP服务配置说明

### 3.1 URL路由配置

当前API端点结构：

- 基础路径：`/api/v1/`
- 告警管理：`/api/v1/alarms/`
- 告警类型：`/api/v1/alarm-categories/`
- 航线管理：`/api/v1/waylines/`

所有端点都支持标准的REST操作（GET、POST、PUT、DELETE）。

### 3.2 中间件配置

项目已配置以下关键中间件：

- **CORS中间件**：允许前端跨域访问
- **认证中间件**：处理用户认证
- **CSRF保护**：防止跨站请求伪造

### 3.3 安全与权限设置

- 当前配置为开发环境（DEBUG=True）
- 生产环境需修改：
  - 设置`DEBUG=False`
  - 配置`ALLOWED_HOSTS`为具体域名
  - 修改`SECRET_KEY`
  - 配置HTTPS

## 4. API接口使用说明

### 4.1 请求头配置

API请求需要包含以下请求头：

- `Content-Type: application/json`
- 认证相关（可选）：
  - `X-User-Token`
  - `X-Project-Uuid`

### 4.2 主要接口功能

#### 告警管理接口 (`/api/v1/alarms/`)
- **GET**：获取告警列表，支持分页、过滤、搜索和排序
- **POST**：创建新告警
- **GET /{id}**：获取单个告警详情
- **PUT /{id}**：更新告警信息
- **DELETE /{id}**：删除告警

#### 航线管理接口 (`/api/v1/waylines/`)
- **GET**：获取航线列表，支持分页、搜索和排序
- **POST**：创建新航线
- **GET /{id}**：获取单个航线详情
- **PUT /{id}**：更新航线信息
- **DELETE /{id}**：删除航线

## 5. 前端与后端交互

前端通过Axios等HTTP客户端库与后端交互：

```javascript
// 示例：获取告警列表
async function fetchAlarms() {
  const response = await fetch('http://127.0.0.1:8000/api/v1/alarms/', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'X-User-Token': 'your-token-here',
      'X-Project-Uuid': 'your-project-uuid'
    }
  });
  return response.json();
}
```

## 6. 常见问题与排查

### 6.1 CORS错误

如果前端遇到CORS错误，请检查：
- `settings.py`中的`CORS_ALLOWED_ORIGINS`是否包含前端地址
- 尝试添加`CORS_ALLOW_ALL_ORIGINS = True`（仅用于开发环境）

### 6.2 数据库问题

如果遇到数据库错误：
```bash
# 删除旧数据库（注意：会丢失所有数据）
del db.sqlite3
# 重新创建数据库
python manage.py migrate
```

### 6.3 依赖冲突

解决依赖冲突：
```bash
pip install --force-reinstall -r requirements.txt
pip install --force-reinstall django-filter django-cors-headers
```

## 7. 生产环境部署建议

1. 使用Gunicorn/uWSGI作为WSGI服务器
2. 配置Nginx作为反向代理
3. 设置数据库备份策略
4. 配置日志监控
5. 使用环境变量存储敏感信息

## 8. 接口测试工具

可以使用以下工具测试API：
- Postman
- curl
- 项目中的API测试页面 (`http://localhost:8080/api-test`)

---

通过以上步骤，您可以成功运行和管理项目的HTTP服务系统。如有其他需求，可以基于现有架构进行扩展开发。