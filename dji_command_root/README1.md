
# dji_command_center - DJI 司空 2 数字孪生告警管理后端

**最后更新日期: 2025-10-25**

## 🎯 项目概述

本项目是基于 Django 和 Django REST Framework (DRF) 构建的后端服务，旨在为前端数字孪生应用提供数据管理能力，并对接 DJI 司空 2 私有版 (FlightHub 2 On-Premises) 的实时数据流。

### 核心技术栈

* **框架:** Python 3.9+, Django, Django REST Framework  
* **通信协议:** MQTT (实时遥测), HTTP/S (REST, Webhook)  
* **数据库:** SQLite (开发环境), [生产数据库类型] (生产环境)

---

## 🚀 快速启动与部署指南

**前提条件:** 确保已安装 Git、Python 3.9+ 并创建虚拟环境。

### 1️⃣ 启动流程

```bash
# 克隆仓库
git clone [您的 GitHub 仓库地址]
cd dji_command_center

# 激活虚拟环境
source venv/bin/activate

 python -m venv venv# windows激活环境
 
#进入虚拟环境 
 venv\Scripts\activate
# 安装依赖

pip install -r requirements.txt

# 初始化数据库
python manage.py migrate


# 启动服务
python manage.py runserver 
