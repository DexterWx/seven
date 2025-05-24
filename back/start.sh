#!/bin/bash

# 创建日志目录
mkdir -p logs

# 启动 gunicorn
nohup gunicorn app:app \
    --bind 0.0.0.0:5001 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --workers 2 \
    > logs/output.log 2>&1 &

# 输出进程 ID
echo "Gunicorn started with PID: $!" 