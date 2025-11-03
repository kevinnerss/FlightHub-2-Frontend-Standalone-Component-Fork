import os
import django
import sys
import datetime

# --- 配置变量 (用于文档生成) ---
PROJECT_NAME = "dji_command_center"
APP_NAME = "telemetry_app"
TODAY = datetime.date.today().strftime("%Y-%m-%d")

# 假设的内网配置 (请根据您的现场 IP 替换！)
DJI_IP_EXAMPLE = "10.94.98.15"   # 司空服务器内网 IP
DJI_PORT_EXAMPLE = "38080"       # 司空桥接 API 端口
YOUR_IP_EXAMPLE = "192.168.1.50"  # 您的服务器/笔记本电脑内网 IP
YOUR_PORT_EXAMPLE = "8001"       # 您的 Django 端口
YOUR_BROKER_PORT = "1883"        # 您的 MQTT Broker 端口


# --- 核心函数：生成 README.md ---
def generate_readme():
    """生成项目概览和启动指南 (README.md)"""
    readme_content = f"""
# {PROJECT_NAME} - DJI 司空 2 数字孪生告警管理后端

**最后更新日期: {TODAY}**

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
cd {PROJECT_NAME}

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python manage.py migrate

# 启动服务
# 启动服务
python manage.py runserver 0.0.0.0:{YOUR_PORT_EXAMPLE}
"""
    return readme_content
if __name__ == "__main__":
        try:
            readme_content = generate_readme()
            with open("README1.md", "w", encoding="utf-8") as f:
                f.write(readme_content)
            print("✅ 文档生成成功！")
            print("文件 'README1.md' 已在项目根目录创建。")
        except Exception as e:
            print(f"❌ 文档生成失败: {e}")
            print("请检查 generate_docs.py 文件顶部变量是否正确定义。")
