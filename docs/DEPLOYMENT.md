# 部署指南

本文档介绍如何在本地服务器、Docker 以及阿里云 ECS 服务器上部署快乐8分析系统。

## 1. 系统要求

-   **操作系统**：Ubuntu 20.04+ (推荐) / Windows Server 2019+
-   **运行环境**：Python 3.9+
-   **内存**：至少 512MB RAM
-   **公网访问**：需开放 HTTP (80/5000) 端口

---

## 2. 阿里云服务器部署 (ECS)

### 方案 A：原生 Python 部署

1.  **安装必要环境**：
    ```bash
    sudo apt update
    sudo apt install python3-pip python3-venv nginx -y
    ```
2.  **上传代码**：使用 SCP、Git 或 FTP 将代码上传到 `/var/www/happy8`。
3.  **设置虚拟环境**：
    ```bash
    cd /var/www/happy8
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
4.  **配置 Nginx**：
    将 `deployment/nginx/nginx.conf` 复制到 `/etc/nginx/sites-available/happy8` 并启用。

### 方案 B：Docker 自动化部署 (推荐)

这是最稳定、最标准、最易于自动化的方案。

1.  **安装 Docker & Compose**：
    ```bash
    curl -fsSL https://get.docker.com | bash -s docker
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.x.x/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ```
2.  **一键启动**：
    ```bash
    cd /var/www/happy8
    docker-compose -f deployment/docker/docker-compose.yml up -d --build
    ```

---

## 3. 阿里云自动化部署脚本方案

为了实现快速迭代，项目提供了 `deployment/scripts/deploy.sh` 脚本。

**自动化流程图**：
`代码提交 -> 脚本执行 -> 拉取代码 -> 构建镜像 -> 停旧起新 -> 开启日志监控`

**本地一键发布 (PowerShell)**：
```powershell
# 假设配置了 SSH 免密登录
ssh root@your_aliyun_ip "cd /app/happy8 && git pull && bash deployment/scripts/deploy.sh"
```

---

## 4. 常见问题排查

-   **502 Bad Gateway**：检查 Flask 容器是否正常运行 (`docker ps`)，检查 Gunicorn 端口是否冲突。
-   **数据无法更新**：检查阿里云 ECS 安全组是否允许访问外网，检查福彩官网 API 是否有变动。
-   **中文显示异常**：确保系统环境支持 UTF-8 编码。
