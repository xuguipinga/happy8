# 电商后台管理系统 - 技术架构文档

## 1. 技术栈选型 (Technology Stack)

### 后端 (Backend)
*   **语言**: Python 3.9+
*   **Web框架**: Flask 2.0+ (轻量、灵活)
*   **数据库ORM**: SQLAlchemy (强大的数据库抽象层)
*   **数据分析**: Pandas (核心组件，用于处理Excel与盈亏计算)
*   **认证**: PyJWT (JWT Token 机制)
*   **任务调度**: APScheduler (用于定时执行盈亏计算任务)

### 前端 (Frontend)
*   **框架**: Vue 3 (Composition API)
*   **UI库**: Element Plus (Element UI 的 Vue3 版本，适合后台管理)
*   **脚手架**: Vite (极速构建)
*   **状态管理**: Pinia
*   **图表**: ECharts 5.0 (数据可视化)
*   **HTTP请求**: Axios

### 数据库 (Database)
*   **开发环境**: SQLite (无需配置，文件型数据库)
*   **生产环境**: MySQL 8.0 (推荐)

## 2. 系统架构图 (Architecture)

```mermaid
graph TD
    Client[浏览器/Vue3前端] --> |REST API| Gateway[Flask 后端接口]
    
    subgraph "Backend Layer"
        Gateway --> Auth[认证模块]
        Gateway --> Business[业务逻辑层]
        
        Business --> ExcelParser[Excel 解析引擎 (Pandas)]
        Business --> Calculator[盈亏计算引擎]
        Business --> ORM[SQLAlchemy ORM]
    end
    
    subgraph "Data Layer"
        ORM --> DB[(MySQL/SQLite)]
        ExcelParser --> FileSystem[Excel 文件存储]
    end
```

## 3. 核心模块实现细节

### 3.1 Excel 导入解析器
*   **设计模式**: 策略模式 (Strategy Pattern)
*   **逻辑**:
    *   定义一个基类 `BaseImporter`。
    *   为 Amazon, Shopee, 采购单, 物流单分别实现子类 (如 `AmazonOrderImporter`)。
    *   根据用户选择的“上传类型”动态实例化对应的 Importer。
    *   **Pandas 优势**: 利用 `pandas.read_excel()` 快速读取，使用 `df.rename()` 映射列名，使用 `df.to_sql()` 批量入库。

### 3.2 盈亏计算逻辑
*   这是一个耗时操作，不应在 API 请求中同步执行。
*   **异步处理**: 用户点击“重新计算”后，后端开启一个后台线程（或 Celery 任务）进行计算，前端轮询进度。
*   **增量计算**: 仅计算状态发生变更的订单，避免全量重算。

## 4. 后端目录结构
```text
ecommerce-admin/backend/
├── app/
│   ├── __init__.py         # App工厂
│   ├── api/                # API 路由 blueprint
│   ├── core/               # 核心业务逻辑
│   │   ├── importer/       # Excel 导入策略
│   │   └── calculator.py   # 盈亏计算逻辑
│   ├── models/             # 数据库模型
│   └── utils/              # 工具类
├── config.py               # 配置
├── run.py                  # 启动脚本
└── requirements.txt        # 依赖

## 5. 服务器准备清单 (Server Preparation)

您已经有一台阿里云服务器，为了部署本项目，您还需要准备以下环境：

### 5.1 基础环境 (Infrastructure)
*   **操作系统**: 推荐 **Ubuntu 20.04/22.04 LTS** (或 CentOS 7.9)。
*   **Docker**: 必须安装。我们采用 **Docker Compose** 容器化部署，这样就不用在服务器上一个个装 Python, MySQL, Nginx 了，一键启动。
    *   *安装命令参考*: `apt-get install docker.io docker-compose`
*   **安全组 (防火墙)**:
    *   开放 **80** (HTTP) 和 **443** (HTTPS) 端口。
    *   开放 **22** (SSH) 端口用于远程连接。
    *   *注意*: 数据库端口 (3306) 建议不对外开放，仅限内网访问。

### 5.2 域名与SSL
*   **域名**: 比如 `admin.your-domain.com`。
*   **解析**: 在阿里云控制台将域名 A 记录解析到服务器公网 IP。
*   **SSL证书**: 建议在阿里云申请免费的 SSL 证书，用于 HTTPS 加密访问（电商后台涉及资金数据，HTTPS 是必须的）。

### 5.3 第三方服务 (可选但推荐)
*   **对象存储 (OSS)**: 如果不想把图片/Excel存在服务器本地硬盘，可以开通阿里云 OSS。
*   **邮件推送 (DirectMail)**: 用于找回密码或发送每日报表。

```
