# 1. 基础镜像
FROM python:3.10-slim-bookworm

# 2. 环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 工作目录
WORKDIR /app

# 4. 换 apt 源 + 安装系统依赖
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources \
    && sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libc-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. 安装 Python 依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 6. 拷贝项目代码
COPY . /app/

# 7. 收集静态文件
RUN python manage.py collectstatic --noinput

# 8. 启动 gunicorn（统一用 8001 端口）
CMD ["gunicorn", "dji_command_root.wsgi:application", \
"--bind", "0.0.0.0:8001", \
"--workers", "3", \
"--timeout", "120", \
"--graceful-timeout", "120", \
"--access-logfile", "-"]