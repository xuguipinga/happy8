# 服务管理指南 (Service Management Guide)

本文档提供了电商管理系统后端和前端服务的启动、停止、重启的详细命令及说明。

---

## 📋 目录

- [后端服务管理](#后端服务管理)
- [前端服务管理](#前端服务管理)
- [常见问题](#常见问题)

---

## 🔧 后端服务管理

### 环境要求
- Python 3.10+ (当前使用 Python 3.14.3)
- MySQL 数据库 (或 SQLite)
- 虚拟环境 `.venv`

### 1. 启动后端服务

#### 方式一：开发模式启动（推荐）

```powershell
# 1. 进入后端目录
cd ecommerce-admin/backend

# 2. 激活虚拟环境
.\.venv\Scripts\activate

# 3. 启动服务
python run.py
```

**说明：**
- 服务将运行在 `http://127.0.0.1:5000`
- 开启了 Debug 模式，代码修改后会自动重载
- 按 `Ctrl+C` 可停止服务

#### 方式二：生产模式启动（使用 Gunicorn）

```powershell
# 激活虚拟环境后
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

**参数说明：**
- `-w 4`: 使用 4 个工作进程
- `-b 0.0.0.0:5000`: 绑定到所有网络接口的 5000 端口
- `"app:create_app()"`: 应用工厂函数

### 2. 停止后端服务

#### 开发模式停止

```powershell
# 在运行服务的终端窗口按下
Ctrl + C
```

#### 生产模式停止（Gunicorn）

```powershell
# 查找进程 ID
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# 或者查找占用 5000 端口的进程
netstat -ano | findstr :5000

# 停止进程（替换 <PID> 为实际进程 ID）
Stop-Process -Id <PID> -Force
```

### 3. 重启后端服务

#### 开发模式重启

```powershell
# 方法 1: 先停止再启动
# 按 Ctrl+C 停止，然后重新运行
python run.py

# 方法 2: 修改代码后自动重载（Debug 模式下）
# 只需保存代码文件，Flask 会自动检测并重载
```

#### 生产模式重启（Gunicorn）

```powershell
# 优雅重启（推荐）
# 发送 HUP 信号重新加载配置和代码
kill -HUP <MASTER_PID>

# 或者完全重启
Stop-Process -Id <PID> -Force
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### 4. 后台运行服务

```powershell
# 使用 Start-Process 在后台运行
Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "run.py" -WindowStyle Hidden

# 或者使用 nohup（如果在 WSL 或 Linux 环境）
nohup python run.py > backend.log 2>&1 &
```

### 5. 查看后端日志

```powershell
# 如果使用后台运行并重定向到日志文件
Get-Content backend.log -Tail 50 -Wait

# 实时查看最后 50 行并持续监控
```

---

## 🎨 前端服务管理

### 环境要求
- Node.js 14+ 
- npm 或 yarn

### 1. 启动前端服务

#### 开发模式启动

```powershell
# 1. 进入前端目录
cd ecommerce-admin/frontend

# 2. 首次运行需要安装依赖
npm install
# 或
yarn install

# 3. 启动开发服务器
npm run dev
# 或
yarn dev
```

**说明：**
- 通常运行在 `http://localhost:3000` 或 `http://localhost:5173`（Vite）
- 支持热模块替换（HMR），代码修改后自动刷新
- 按 `Ctrl+C` 停止服务

#### 生产模式启动

```powershell
# 1. 构建生产版本
npm run build
# 或
yarn build

# 2. 使用静态服务器运行（需要安装 serve）
npm install -g serve
serve -s dist -l 3000
```

### 2. 停止前端服务

#### 开发模式停止

```powershell
# 在运行服务的终端窗口按下
Ctrl + C
```

#### 生产模式停止（serve）

```powershell
# 查找 Node 进程
Get-Process | Where-Object {$_.ProcessName -eq "node"}

# 停止进程
Stop-Process -Id <PID> -Force
```

### 3. 重启前端服务

#### 开发模式重启

```powershell
# 先停止（Ctrl+C），然后重新启动
npm run dev
```

#### 生产模式重启

```powershell
# 停止当前服务
Stop-Process -Id <PID> -Force

# 重新构建（如果代码有更新）
npm run build

# 重新启动
serve -s dist -l 3000
```

### 4. 前端后台运行

```powershell
# 使用 Start-Process 在后台运行
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Hidden

# 或者使用 PM2（推荐用于生产环境）
npm install -g pm2
pm2 start "npm run dev" --name "ecommerce-frontend"
pm2 list
pm2 stop ecommerce-frontend
pm2 restart ecommerce-frontend
```

---

## 🔍 常见问题

### 1. 端口被占用

**问题：** `Address already in use` 或 `端口 5000 已被占用`

**解决方案：**

```powershell
# 查找占用端口的进程（以 5000 为例）
netstat -ano | findstr :5000

# 停止占用进程
Stop-Process -Id <PID> -Force

# 或者修改配置使用其他端口
# 后端：修改 run.py 中的 port=5000
# 前端：修改 vite.config.js 或 package.json 中的端口配置
```

### 2. 虚拟环境未激活

**问题：** `ModuleNotFoundError` 或找不到依赖包

**解决方案：**

```powershell
# 确保在后端目录下激活虚拟环境
cd ecommerce-admin/backend
.\.venv\Scripts\activate

# 验证虚拟环境已激活（提示符前会显示 (.venv)）
# 如果虚拟环境不存在，重新创建
python -m venv .venv
```

### 3. 数据库连接失败

**问题：** `Can't connect to MySQL server` 或 `Access denied`

**解决方案：**

```powershell
# 1. 检查 MySQL 服务是否运行
Get-Service | Where-Object {$_.Name -like "*mysql*"}

# 2. 启动 MySQL 服务
Start-Service MySQL80  # 服务名可能不同

# 3. 验证 .env 文件中的数据库配置
# DATABASE_URL=mysql://root:root@localhost:3306/ecommerce_admin

# 4. 测试数据库连接
mysql -u root -p
```

### 4. 依赖包缺失或版本冲突

**后端：**

```powershell
# 重新安装依赖
cd ecommerce-admin/backend
.\.venv\Scripts\activate
pip install -r requirements.txt

# 如果有冲突，清空并重新安装
pip freeze | ForEach-Object {pip uninstall -y $_}
pip install -r requirements.txt
```

**前端：**

```powershell
# 删除 node_modules 和 lock 文件
cd ecommerce-admin/frontend
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json  # 或 yarn.lock

# 重新安装
npm install
```

### 5. 查看所有运行的服务

```powershell
# 查看 Python 进程
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# 查看 Node 进程
Get-Process | Where-Object {$_.ProcessName -eq "node"}

# 查看端口占用情况
netstat -ano | findstr "LISTENING"
```

---

## 📝 快速参考

### 后端快速命令

```powershell
# 启动
cd ecommerce-admin/backend && .\.venv\Scripts\activate && python run.py

# 停止
Ctrl + C

# 重启数据库
python reset_db.py && python seed.py
```

### 前端快速命令

```powershell
# 启动
cd ecommerce-admin/frontend && npm run dev

# 停止
Ctrl + C

# 构建生产版本
npm run build
```

---

## 🚀 推荐工作流

### 日常开发

1. 启动后端（终端 1）：
   ```powershell
   cd ecommerce-admin/backend
   .\.venv\Scripts\activate
   python run.py
   ```

2. 启动前端（终端 2）：
   ```powershell
   cd ecommerce-admin/frontend
   npm run dev
   ```

3. 开发完成后，分别在两个终端按 `Ctrl+C` 停止服务

### 生产部署

1. 后端使用 Gunicorn + Nginx
2. 前端构建静态文件部署到 Nginx 或 CDN
3. 使用 PM2 或 systemd 管理进程
4. 配置自动重启和日志管理

---

**最后更新：** 2026-02-12  
**维护者：** Ecommerce Admin Team
