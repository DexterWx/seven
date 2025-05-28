#!/bin/bash

# 设置日期变量
DATE=$(date +%Y%m%d)
LOG_DIR="/data/logs/app/seven/tasks"
LOG_FILE="$LOG_DIR/daily_task_$DATE.log"

# 创建日志目录
mkdir -p $LOG_DIR

# 激活Python环境
source /home/workspace/tools/miniconda3/bin/activate py310

# 切换到项目目录
cd /home/workspace/projects/seven/back

# 执行脚本并记录日志
echo "=== Task Started at $(date) ===" >> "$LOG_FILE" 2>&1
python agents/task.py >> "$LOG_FILE" 2>&1
echo "=== Task Finished at $(date) ===" >> "$LOG_FILE" 2>&1

# 只保留最近30天的日志
find $LOG_DIR -name "daily_task_*.log" -mtime +30 -delete
