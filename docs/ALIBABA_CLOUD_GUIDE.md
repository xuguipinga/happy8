# 快乐8分析系统：云端管理与部署全流程手册

本手册分为两大部分：**本地代码管理**与**阿里云自动化部署**。

---

## 第一部分：本地代码管理 (Git)

Git 是目前最主流的代码版本控制工具。

### 1.1 初始化本地仓库
在项目根目录下打开终端（PowerShell），执行：
```bash
git init
git add .
git commit -m "feat: 项目框架优化与自动化部署准备"
```

### 1.2 托管代码 (推荐使用 码云 Gitee 或 GitHub)
1. 在 [Gitee](https://gitee.com) 或 GitHub 创建一个新仓库，命名为 `happy8-analysis`。
2. 将本地代码关联到远程仓库：
```bash
git remote add origin https://gitee.com/您的用户名/happy8-analysis.git
git push -u origin "master"
```

---

## 第二部分：阿里云环境准备 (ECS)

### 2.1 购买与系统选择
- **规格**：最低配即可（如 1核2G）。
- **镜像**：选择 **Ubuntu 20.04 或 22.04 LTS** (强烈推荐，生态最稳)。

### 2.2 安全组配置 (关键)
在阿里云控制台 -> 实例 -> 安全组 -> 入方向，放行以下端口：
- **80** (HTTP)
- **443** (HTTPS)
- **22** (SSH 远程登录)

### 2.3 安装 Docker 环境
登录服务器后，执行以下命令安装 Docker 套件：
```bash
# 更新并安装依赖
sudo apt update && sudo apt install -y docker.io docker-compose git
# 启动并设置开机自启
sudo systemctl start docker
sudo systemctl enable docker
```

---

## 第三部分：自动化部署实战

### 3.1 首次部署
1. **拉取代码**：
   ```bash
   cd /app
   sudo git clone https://gitee.com/您的用户名/happy8-analysis.git
   cd happy8-analysis
   ```
2. **执行一键部署脚本**（我已为您写好）：
   ```bash
   bash deployment/scripts/deploy.sh
   ```
   *该脚本会自动构建镜像、配置网络并启动服务。*

### 3.2 之后如何更新 (极简三步)
当您在本地修改了代码想同步到阿里云时：

1. **本地推送**：
   ```bash
   git add .
   git commit -m "优化了XXX功能"
   git push
   ```
2. **服务器拉取并发起更新**（在服务器执行）：
   ```bash
   cd /app/happy8-analysis
   git pull
   bash deployment/scripts/deploy.sh
   ```

---

## 第四部分：进阶 - 实现真正的“一键推送，全自动部署”

如果您希望在本地执行一个命令，服务器就自动同步并重启，可以配置 **SSH 免密登录**。

### 4.1 本地配置 SSH 公钥
1. 在本地 PowerShell 执行：`ssh-keygen -t rsa` (一路回车)。
2. 将公钥发送到服务器：`ssh-copy-id root@您的服务器IP`。

### 4.2 本地一键触发脚本 (可选)
您可以创建一个 `update_server.ps1` 脚本放在本地项目根目录：
```powershell
# 本地推送
git add .
git commit -m "update"
git push

# 远程触发部署
ssh root@您的服务器IP "cd /app/happy8-analysis && git pull && bash deployment/scripts/deploy.sh"
```
*以后您改完代码，直接运行这个脚本，剩下的事情系统自动全搞定！*
