# 1. 基础镜像 (使用稳定的 bookworm 版本)
FROM python:3.10-slim-bookworm

# 2. 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 工作目录
WORKDIR /app

# --- 【关键修改点：换源】 ---
# 4. 先把官方源替换为清华源，再安装系统依赖
# 这一步是为了解决 502 Bad Gateway 网络问题
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources \
    && sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*
# -------------------------

# 5. 安装 Python 依赖 (使用清华源)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 6. 复制所有代码到容器
COPY . /app/

# 7. 收集静态文件
RUN python manage.py collectstatic --noinput

# 8. 启动命令
CMD ["gunicorn", "dji_command_root.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]