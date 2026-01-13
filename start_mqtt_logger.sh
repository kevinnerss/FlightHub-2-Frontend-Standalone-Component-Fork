#!/bin/bash

# MQTT 日志记录启动脚本
# 用途: 记录所有MQTT消息到文件，供后续分析

echo "📝 MQTT 日志记录器"
echo "=================="

# 配置参数
OUTPUT_FILE="${1:-mqtt_messages_$(date +%Y%m%d_%H%M%S).log}"
MAX_MESSAGES="${2:-0}"  # 0 表示无限制
DURATION="${3:-0}"      # 0 表示持续记录

echo "输出文件: $OUTPUT_FILE"
echo "最大消息数: $MAX_MESSAGES (0=无限制)"
echo "记录时长: $DURATION 秒 (0=持续记录)"
echo ""

# 进入 Django 项目目录
cd /app

# 启动日志记录器
python manage.py mqtt_logger \
    --output "$OUTPUT_FILE" \
    --max-messages "$MAX_MESSAGES" \
    --duration "$DURATION"
