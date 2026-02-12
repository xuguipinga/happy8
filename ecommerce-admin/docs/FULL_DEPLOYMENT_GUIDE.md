# 电商管理系统 (Ecommerce-Admin) 全流程部署指南

本指南将指导您将 `ecommerce-admin` 项目从本地上传到阿里云（或其他云服务器），并完成部署和访问配置。

## 目录
1. [项目结构说明](#1-项目结构说明)
2. [服务器环境准备](#2-服务器环境准备)
3. [代码上传](#3-代码上传)
4. [项目配置](#4-项目配置)
5. [启动部署](#5-启动部署)
6. [域名与外网访问 (Nginx配置)](#6-域名与外网访问-nginx配置)
7. [常见问题与维护](#7-常见问题与维护)

---

## 1. 项目结构说明

本项目包含前端 (Vue3) 和后端 (Flask) 两部分，通过 Docker Compose 进行一键编排部署。

*   **backend/**: Python Flask 后端代码。
*   **frontend/**: Vue3 + Vite 前端代码。
*   **docker-compose.prod.yml**: 生产环境部署配置文件。
*   **data/**: 数据库和初始化脚本持久化目录。

---

## 2. 服务器环境准备

请确保您的云服务器已安装以下软件：

1.  **Git**: 用于拉取代码。
    ```bash
    sudo apt-get update
    sudo apt-get install git
    ```
2.  **Docker & Docker Compose**: 用于容器化运行。
    ```bash
    # 安装 Docker (以 Ubuntu 为例)
    curl -fsSL https://get.docker.com | bash
    
    # 安装 Docker Compose
    sudo apt-get install docker-compose-plugin
    # 或者旧版本
    sudo apt-get install docker-compose
    ```

---

## 3. 代码上传

推荐使用 Git 进行代码同步。

### 方法 A: Git (推荐)

1.  **在本地提交代码**:
    ```bash
    git add .
    git commit -m "Ready for deployment"
    git push origin master
    ```

2.  **在服务器拉取代码**:
    ```bash
    # 假设部署在 /opt 目录
    cd /opt
    git clone <您的仓库地址> ecommerce-admin
    # 如果已存在，则进入目录拉取最新
    cd ecommerce-admin
    git pull
    ```

### 方法 B: 手动上传 (SCP/SFTP)

如果不使用 Git，可以将整个 `ecommerce-admin` 文件夹压缩后上传到服务器 `/opt/` 目录并解压。

---

## 4. 项目配置

在启动前，请确认配置文件。

### 4.1 检查 `docker-compose.prod.yml`

项目根目录下已为您准备了 `docker-compose.prod.yml`。
**关键配置项**:
*   **Frontend Port**: 默认为 `80:80`。如果服务器上 80 端口已被占用（例如被 Nginx 或其他项目占用），请修改左边的端口，例如 `8080:80`。
*   **Database**: 默认端口映射为 `3307:3306`（避免与服务器默认 MySQL 冲突）。
*   **Passwords**: 请务必修改文件中的 `MYSQL_ROOT_PASSWORD` 和 `MYSQL_PASSWORD` 为强密码。

### 4.2 检查前端 Nginx 配置

前端容器内置了 Nginx，配置文件位于 `frontend/nginx.conf`。默认配置已处理好 API 转发：
```nginx
location /api {
    proxy_pass http://backend:5000;
    ...
}
```
通常无需修改。

---

## 5. 启动部署

在项目根目录下执行以下命令：

```bash
# 1. 构建并后台启动所有服务
docker-compose -f docker-compose.prod.yml up -d --build

# 2. 查看运行状态
docker-compose -f docker-compose.prod.yml ps
```

如果一切正常，您应该看到 `ecommerce_frontend`, `ecommerce_backend`, `ecommerce_db`, `ecommerce_redis` 四个容器状态为 `Up`。

---

## 6. 域名与外网访问 (Nginx配置)

通常我们会在宿主机安装一个 Nginx 作为总入口，将域名转发到我们的 Docker 容器。

### 6.1 场景一：直接通过 IP 访问
如果您的 `docker-compose.prod.yml` 中映射了 `80:80`，且服务器防火墙已开放 80 端口，直接访问服务器 IP 即可看到系统。

### 6.2 场景二：使用域名 (推荐)

假设您的域名是 `admin.example.com`，且容器映射端口为 `8080` (即 `8080:80`)。

1.  **在宿主机安装 Nginx**:
    ```bash
    sudo apt-get install nginx
    ```

2.  **创建配置文件**:
    ```bash
    sudo nano /etc/nginx/conf.d/ecommerce.conf
    ```

3.  **写入以下内容**:
    ```nginx
    server {
        listen 80;
        server_name admin.example.com;  # 替换为您的域名

        location / {
            proxy_pass http://127.0.0.1:8080; # 转发到 Docker 容器映射的端口
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
    ```

4.  **重启 Nginx**:
    ```bash
    sudo nginx -t  # 测试配置
    sudo systemctl reload nginx
    ```

---

## 7. 常见问题与维护

### Q1: 如何查看日志？
```bash
# 查看后端日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 查看前端访问日志
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Q2: 数据库如何备份？
数据文件持久化在 `data/mysql` 目录下。备份该目录即可，或者使用 `mysqldump` 命令：
```bash
docker exec ecommerce_db mysqldump -u root -p<密码> ecommerce_admin > backup.sql
```

### Q3: 代码更新后如何生效？
```bash
git pull
docker-compose -f docker-compose.prod.yml up -d --build frontend backend
# 只需重新构建应用容器，数据库和Redis通常无需重启
```

### Q4: 端口冲突怎么办？
修改 `docker-compose.prod.yml` 中的 `ports` 映射。例如将 `80:80` 改为 `8081:80`，然后重启容器。
