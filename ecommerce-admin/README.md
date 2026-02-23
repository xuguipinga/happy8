# Ecommerce Admin - 电商后台管理系统

由 Google DeepMind 团队设计的 Antigravity AI 协助构建的现代化、多租户电商后台管理系统。

## 🌟 项目亮点

- **多租户架构**: 支持多个独立店铺/租户，数据严格隔离。
- **现代化技术栈**: 前端 Vue3 + Vite，后端 Python Flask + SQLAlchemy。
- **高性能**: 集成 Redis 缓存，MySQL 8.0 持久化，Nginx 静态托管。
- **一键部署**: 专为云服务器优化的 Docker Compose 编排方案。
- **AI 驱动**: 项目架构与核心代码经过 AI 对齐优化，易于维护与扩展。

## 🏗️ 技术架构

### 后端 (Backend)
- **框架**: Flask
- **数据库**: MySQL 8.0 (通过 SQLAlchemy ORM)
- **缓存**: Redis
- **认证**: JWT (JSON Web Tokens)
- **迁移**: Flask-Migrate

### 前端 (Frontend)
- **框架**: Vue 3 + Vite
- **UI 组件**: Element Plus
- **构建工具**: Vite (本地构建，容器内静态托管)

## 🚀 快速启动

### 1. 本地开发
```bash
# 确保已安装 Docker 和 Node.js
docker-compose up -d  # 启动数据库和 Redis
cd backend && pip install -r requirements.txt && python run.py
cd frontend && npm install && npm run dev
```

### 2. 生产环境部署 (阿里云)
我们推荐 **本地构建 + 服务器托管** 方案，以应对低配服务器资源限制。

1. **本地构建**:
   ```bash
   cd frontend && npm run build
   ```
2. **上传 & 启动**:
   将代码推送到服务器，执行：
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```
3. **初始化数据库**:
   ```bash
   # 参见 docs/DEPLOYMENT_COMPLETE.md 中提供的初始化指令
   ```

## 📚 详细文档

项目的所有详细手册均存放在 [docs/](file:///d:/WorkSpec\Project\Ecommerce-admin\ecommerce-admin\docs) 目录：

- 📖 [阿里云全流程部署手册](file:///d:/WorkSpec\Project\Ecommerce-admin\ecommerce-admin\docs\FULL_DEPLOYMENT_GUIDE.md) - 适合初次部署。
- 🛠️ [本地构建与部署指南](file:///d:/WorkSpec\Project\Ecommerce-admin\ecommerce-admin\docs\LOCAL_BUILD_DEPLOY.md) - 解决资源限制。
- 📊 [数据库设计手册](file:///d:/WorkSpec\Project\Ecommerce-admin\ecommerce-admin\docs\DATABASE_DESIGN.md) - 表结构与关系说明。
- 🔒 [业务流程与 PRD](file:///d:/WorkSpec\Project\Ecommerce-admin\ecommerce-admin\docs\PRODUCT_PRD.md) - 项目逻辑定义。

## ⚖️ 许可说明
本项目遵循 MIT 协议。
