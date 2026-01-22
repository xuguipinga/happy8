#!/bin/bash

# 快乐8分析项目 - 阿里云自动部署脚本
# 运行环境：Ubuntu/CentOS + Docker

PROJECT_NAME="happy8"
DEPLOY_PATH="/app/$PROJECT_NAME"
COMPOSE_FILE="$DEPLOY_PATH/deployment/docker/docker-compose.yml"

echo "=========================================="
echo "    快乐8分析系统 - 开始自动化部署"
echo "=========================================="

# 1. 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "[错误] 未检测到 Docker，请先安装 Docker。"
    exit 1
fi

# 2. 进入项目目录并拉取最新代码 (如果有 Git 环境)
# cd $DEPLOY_PATH
# git pull origin master

# 3. 停止当前运行的容器
echo "[步骤 1/3] 停止旧服务..."
docker-compose -f $COMPOSE_FILE down --remove-orphans

# 4. 构建并启动新服务
echo "[步骤 2/3] 构建镜像并启动容器..."
docker-compose -f $COMPOSE_FILE up -d --build

# 5. 健康检查
echo "[步骤 3/3] 等待服务启动并进行健康检查..."
MAX_RETRIES=10
RETRY_COUNT=0
HEALTH_URL="http://localhost:5000/health"

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)
    if [ "$HTTP_STATUS" == "200" ]; then
        echo "[成功] 系统已成功启动并在运行中！"
        echo "访问地址: http://your_server_ip"
        echo "=========================================="
        exit 0
    fi
    echo "正在检查健康状态... (重试 $RETRY_COUNT/$MAX_RETRIES)"
    sleep 5
    ((RETRY_COUNT++))
done

echo "[错误] 系统启动超时或异常，请检查 logs/app.log 了解详情。"
echo "=========================================="
exit 1
