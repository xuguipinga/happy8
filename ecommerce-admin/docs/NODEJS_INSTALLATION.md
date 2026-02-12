# Node.js 安装指南 (Node.js Installation Guide)

您需要安装 Node.js 才能运行前端项目。本文档提供详细的安装步骤。

---

## 📋 前端项目信息

**项目类型：** Vite + Vue 3  
**Node.js 要求：** 14.18+ 或 16+ (推荐 18.x LTS)  
**包管理器：** npm 或 yarn

---

## 🚀 安装 Node.js

### 方法一：使用官方安装包（推荐）

#### 1. 下载 Node.js

访问官方网站下载：
- **官网：** https://nodejs.org/
- **推荐版本：** LTS (长期支持版本，当前为 20.x)

**下载选项：**
- Windows 64-bit: `node-v20.x.x-x64.msi`
- 选择 LTS 版本（左侧绿色按钮）

#### 2. 安装步骤

1. 双击下载的 `.msi` 文件
2. 点击 "Next" 接受许可协议
3. 选择安装路径（默认即可）
4. **重要：** 确保勾选 "Automatically install the necessary tools"
5. 点击 "Install" 开始安装
6. 安装完成后点击 "Finish"

#### 3. 验证安装

**重新打开一个新的 PowerShell 窗口**（重要！），然后运行：

```powershell
# 检查 Node.js 版本
node --version
# 应该显示类似：v20.11.0

# 检查 npm 版本
npm --version
# 应该显示类似：10.2.4
```

**如果命令无法识别：**
1. 确保您打开的是**新的** PowerShell 窗口
2. 检查环境变量是否正确配置（通常安装程序会自动配置）

---

### 方法二：使用 Winget（Windows 包管理器）

如果您的系统有 winget（Windows 11 默认包含）：

```powershell
# 安装 Node.js LTS
winget install OpenJS.NodeJS.LTS

# 或安装最新版本
winget install OpenJS.NodeJS
```

安装完成后，**重新打开 PowerShell** 并验证安装。

---

### 方法三：使用 Chocolatey

如果您已安装 Chocolatey 包管理器：

```powershell
# 以管理员身份运行 PowerShell
choco install nodejs-lts

# 或安装最新版本
choco install nodejs
```

---

## 📦 安装前端依赖

Node.js 安装完成后，在**新的 PowerShell 窗口**中执行：

```powershell
# 1. 进入前端目录
cd D:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\frontend

# 2. 安装依赖
npm install

# 如果 npm install 很慢，可以使用国内镜像
npm install --registry=https://registry.npmmirror.com
```

---

## 🎯 启动前端开发服务器

依赖安装完成后：

```powershell
# 启动开发服务器
npm run dev
```

**预期输出：**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## 🔧 常见问题

### 1. 命令找不到（即使安装了 Node.js）

**原因：** 环境变量未生效

**解决方案：**
1. **关闭所有 PowerShell 窗口**
2. **重新打开一个新的 PowerShell**
3. 再次尝试 `node --version`

如果还是不行：
```powershell
# 手动刷新环境变量
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# 再次验证
node --version
```

### 2. npm install 速度很慢

**解决方案：** 使用国内镜像

```powershell
# 临时使用淘宝镜像
npm install --registry=https://registry.npmmirror.com

# 或永久设置
npm config set registry https://registry.npmmirror.com

# 验证配置
npm config get registry
```

### 3. 权限错误

**解决方案：** 以管理员身份运行 PowerShell

1. 右键点击 PowerShell
2. 选择 "以管理员身份运行"
3. 重新执行命令

### 4. 端口被占用

**错误：** `Port 5173 is already in use`

**解决方案：**
```powershell
# 查找占用端口的进程
netstat -ano | findstr :5173

# 停止进程（替换 <PID> 为实际进程 ID）
Stop-Process -Id <PID> -Force
```

---

## 📝 快速参考

### 检查 Node.js 是否安装

```powershell
node --version && npm --version
```

### 完整启动流程

```powershell
# 1. 进入前端目录
cd D:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\frontend

# 2. 首次运行需要安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

### 停止开发服务器

```powershell
# 在运行服务的终端按
Ctrl + C
```

---

## 🌐 推荐的 Node.js 版本管理工具

如果您需要在多个项目间切换不同的 Node.js 版本：

### nvm-windows (Node Version Manager)

```powershell
# 下载地址
https://github.com/coreybutler/nvm-windows/releases

# 安装后使用
nvm install 20.11.0
nvm use 20.11.0
nvm list
```

---

## ✅ 验证清单

安装完成后，请确认以下内容：

- [ ] `node --version` 显示版本号（如 v20.11.0）
- [ ] `npm --version` 显示版本号（如 10.2.4）
- [ ] `npm install` 在前端目录成功执行
- [ ] `npm run dev` 成功启动开发服务器
- [ ] 浏览器访问 `http://localhost:5173` 可以看到前端页面

---

## 📚 下一步

Node.js 安装完成后，您可以：

1. **安装前端依赖：** `npm install`
2. **启动开发服务器：** `npm run dev`
3. **同时运行后端和前端：**
   - 终端 1：后端服务（端口 5000）
   - 终端 2：前端服务（端口 5173）

---

**最后更新：** 2026-02-12  
**维护者：** Ecommerce Admin Team
