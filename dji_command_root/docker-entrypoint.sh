#!/bin/bash
set -e

# 等待数据库就绪（如果需要）
echo "等待数据库就绪..."

# 运行数据库迁移
echo "运行数据库迁移..."
python manage.py migrate --noinput

# 收集静态文件（如果需要）
echo "收集静态文件..."
python manage.py collectstatic --noinput || true

# 执行传入的命令（默认是 gunicorn）
exec "$@"
