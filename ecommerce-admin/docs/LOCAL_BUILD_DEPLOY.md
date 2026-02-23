# 本地打包前端并上传到服务器（绕开服务器打包）

本指南教你在本地完成前端打包，上传 `dist/` 到服务器，然后用 Nginx 直接托管静态文件，避免服务器上 `vite build` 卡住的问题。

## 适用场景
- 服务器网络不稳定或内存不足，容器内执行 `npm install`/`vite build` 经常卡住或失败
- 需要更快、更稳定的部署过程

## 前置条件
- 本地已安装 Node.js 18+（推荐与项目一致）
- 在本地仓库路径：`ecommerce-admin/frontend`

### 如何验证本地是否安装 Node.js 与 npm
- 在终端/命令行分别查看版本：
  - Windows（PowerShell）：
    ```powershell
    node -v
    npm -v
    ```
  - macOS/Linux（终端）：
    ```bash
    node -v
    npm -v
    ```
- 看到版本号（例如 v18.x / 9.x）表示已安装；如果提示“未找到命令”：
  - Windows：到 Node.js 官网安装包，或使用 nvm-windows 安装并选择 18.x 版本
  - macOS：使用 Homebrew 安装 `brew install node@18` 并 `brew link --force node@18`
  - Ubuntu/Debian：使用 apt 源安装 `sudo apt-get install nodejs npm` 或使用 nvm 安装 18.x


## 步骤一：本地打包
```bash
cd ecommerce-admin/frontend
npm ci
npm run build
```
成功后会生成 `frontend/dist/`。

## 步骤二：上传 dist 到服务器
任选其一方式上传到服务器目标目录 `ecommerce-admin/frontend/dist/`：

### 方式 A：SCP（Mac/Linux/Windows 10+ 自带 OpenSSH）
```bash
scp -r ./dist/ <用户名>@<服务器IP>:/opt/ecommerce-admin/ecommerce-admin/frontend/dist
```

### 方式 B：Windows 图形界面（WinSCP）
1. 连接到服务器（主机=服务器IP，端口=22，用户名密码为服务器账户）
2. 进入 `/opt/ecommerce-admin/ecommerce-admin/frontend/`
3. 将本地 `dist/` 文件夹拖拽上传

### 方式 C：rsync（带断点续传）
```bash
rsync -avz --delete ./dist/ <用户名>@<服务器IP>:/opt/ecommerce-admin/ecommerce-admin/frontend/dist
```

上传完成后，服务器上应存在：`/opt/ecommerce-admin/ecommerce-admin/frontend/dist/index.html` 等文件。

### 方式 D：Git（强制提交 dist，适合应急）
> 不推荐长期把构建产物留在主分支；建议使用专用分支或临时提交，部署完成后移除。

**方案 1：专用分支提交**
```bash
# 本地
cd ecommerce-admin/frontend
npm ci && npm run build
git switch -c deploy-dist
git add -f dist
git commit -m "Add dist for deployment"
git push origin deploy-dist

# 服务器
cd /opt/ecommerce-admin/ecommerce-admin
git fetch && git switch deploy-dist
```

**方案 2：当前分支临时提交**
```bash
cd ecommerce-admin/frontend
npm ci && npm run build
git add -f dist
git commit -m "Add dist for deployment"
git push

# 服务器
cd /opt/ecommerce-admin/ecommerce-admin && git pull
```

## 步骤三：切换为静态托管编排
生产编排文件位置：[`docker-compose.prod.yml`](file:///d:/WorkSpec/Project/Ecommerce-admin/ecommerce-admin/docker-compose.prod.yml)

将 `frontend` 服务的 `build.dockerfile` 设置为 `Dockerfile.static`（该 Dockerfile 会直接将本地上传的 `dist/` 复制到 Nginx 目录）：
```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.static
    container_name: ecommerce_frontend
    restart: always
    ports:
      - "3344:80"
    depends_on:
      - backend
```
参考文件：[`Dockerfile.static`](file:///d:/WorkSpec/Project/Ecommerce-admin/ecommerce-admin/frontend/Dockerfile.static)

## 步骤四：构建并启动
```bash
cd /opt/ecommerce-admin/ecommerce-admin
docker compose -f docker-compose.prod.yml up -d --build
```

## 验证
```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f frontend
```
浏览器访问：`http://<服务器IP>:3344`

## 常见问题
- 提示 `COPY dist/: not found`
  - 说明服务器的 `frontend/dist/` 不存在或为空，重新按步骤二上传后再构建。
- 前端页面空白或 404
  - 检查 `dist/` 是否为最新打包产物；确保路径为 `frontend/dist/`（不是把 dist 放到其他目录）。
- 想回到容器内打包模式
  - 将 `docker-compose.prod.yml` 的 `frontend.build.dockerfile` 改回 [`Dockerfile`](file:///d:/WorkSpec/Project/Ecommerce-admin/ecommerce-admin/frontend/Dockerfile)，然后执行 `up -d --build`。
