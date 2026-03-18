# 企业级互联网开发规范与架构指南

本指南旨在将本项目升级为符合大型互联网公司（如阿里、腾讯、字节）标准的工程化规范。核心思想是**解耦、规范、自动化**。

---

## 🏗️ 1. 模块分层 (Module Layering)

遵循典型的 **DDD (领域驱动设计)** 简化版或 **Clean Architecture**，后端应分为以下层次：

### 后端分层 (Backend Layers)
1.  **Controller / API 层** (`app/api/`):
    *   **职责**：负责接口定义、请求参数校验（DTO）、统一返回格式及 HTTP 状态码管理。
    *   **规范**：严禁在此编写业务逻辑。
2.  **Service / 业务逻辑层** (`app/services/`):
    *   **职责**：核心业务逻辑、事务控制、多模型协同。
    *   **规范**：不依赖具体的数据库操作，仅处理逻辑。
3.  **Manager / 通用业务层** (可选):
    *   **职责**：跨 Service 的调用、第三方 API 封装、通用能力。
4.  **Repository / 持久化层** (`app/repositories/`):
    *   **职责**：单纯的 SQL/ORM 操作，抽象出领域对象（DO）。
    *   **规范**：解耦数据库选型变化对业务层的影响。
5.  **Domain / 领域模型层** (`app/models/`):
    *   **职责**：定义实体（Entity）和值对象。

### 统一数据对象命名
*   **DTO (Data Transfer Object)**: 前端提交或返回给前端的对象。
*   **DO (Domain Object)**: 数据库表映射对象。
*   **VO (View Object)**: 专门给前端展示的对象。

---

## 🛠️ 2. 推荐项目结构 (Proposed Structure)

```text
ecommerce-admin/
├── backend/
│   ├── app/
│   │   ├── api/ v1/        # API 路由，支持版本控制
│   │   ├── services/       # 业务逻辑
│   │   ├── repositories/   # 数据库交互
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # 参数校验 (Pydantic/Marshmallow)
│   │   ├── core/           # 核心配置 (Config, Logging, Security)
│   │   ├── common/         # 工具类 (Utils, Constants, Enums)
│   │   └── exceptions/     # 统一异常定义
│   ├── tests/              # 单元测试与集成测试
│   ├── run.py
│   └── requirements.txt
├── frontend/ (Vue3)
│   ├── src/
│   │   ├── api/            # 接口封装 (Axios)
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 通用组件
│   │   ├── store/          # 状态管理 (Pinia)
│   │   └── utils/          # 前端工具
├── deploy/                 # 部署相关脚本 (K8s, Docker)
└── docs/                   # 技术方案、API 文档 (Swagger)
```

---

## 🔄 3. 开发流程 (Development Workflow)

### Git 分支管理 (Git-flow)
*   `master`: 生产分支，严禁直接 Push。
*   `release`: 预发布分支。
*   `develop`: 主开发分支。
*   `feature/*`: 新功能开发分支。
*   `hotfix/*`: 线上紧急修复。

### 代码提交规范 (Commit Message)
使用约定式提交 (Conventional Commits):
*   `feat: 新增登录功能`
*   `fix: 修复搜索列表分页 Bug`
*   `docs: 更新 API 文档`

---

## 📏 4. 开发规范 (Coding Standards)

### API 设计 (RESTful)
*   使用名词复数: `/api/v1/products`
*   统一响应格式:
    ```json
    {
      "code": 200,          // 业务状态码
      "message": "success",
      "data": { ... },      // 返回数据
      "traceId": "uuid"     // 全链路追踪 ID
    }
    ```

### 错误处理
*   定义全局异常拦截器，禁止直接向前端抛出 `Internal Server Error`。
*   业务错误通过 `exceptions.py` 定义，并带有明确的错误代码。

### 测试驱动
*   **单元测试**: 核心 Service 逻辑覆盖率需 > 80%。
*   **集成测试**: 关键 API 链路必须有集成测试用例。

---

## 🚀 5. 环境自动化 (DevOps)

1.  **配置隔离**: 使用 `.env` 管理不同环境的配置（Dev, Test, Prod）。
2.  **CI/CD**: 通过 GitHub Actions 或 GitLab CI 进行自动化构建、测试、部署。
3.  **监控**: 集成 Sentry (异常监控) 和 Prometheus (性能指标)。
