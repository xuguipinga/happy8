# 阿里云服务器部署指南 (小白保姆级教程)

这份文档专门为您准备，教您如何在已经运行着 `happy8-analysis` 项目的服务器上，**安全地部署** 新的 `ecommerce-admin` 项目，并管理它们。

## 0. 核心概念 (先看这里)

服务器就像一台永远不关机的电脑。
*   **Docker**: 就像手机的应用商店。我们把项目打包成“APP”（镜像），安装到手机里就能跑，不用关心底层环境。
*   **Nginx**: 就像公司的前台。所有访问服务器的流量（比如访问 `admin.com` 或 `happy8.com`）都先找它，它再根据域名把请求转给不同的部门（项目）。
*   **端口 (Port)**: 就像银行窗口。
    *   `80` 号窗口是默认网页访问窗口。
    *   **现在的冲突点**：您的旧项目 `happy8-analysis` 已经占用了 `80` 和 `5000` 窗口。新项目如果还想用这俩窗口，就会报错“端口被占用”。

---

## 1. 关停旧项目 (Happy8 Analysis)

如果您暂时不想跑旧项目，或者想腾出端口，可以用以下命令。

### 1.1 找到它在哪里
假设旧项目在 `/opt/happy8-analysis` (请根据实际情况调整)。
```bash
cd /opt/happy8-analysis/deployment/docker
```

### 1.2 停止它
```bash
# down = 停止并移除容器 (数据保留在 volume 里)
docker-compose down
```
*执行完这步，旧项目就停止运行了，80端口也释放出来了。*

---

## 2. 部署新项目 (Ecommerce Admin)

### 2.1 上传代码
推荐使用 Git 同步代码。
1. **本地推送**: `git push origin master` (如果第一次推，用 `git push --set-upstream origin master`)。
2. **服务器拉取**:
   ```bash
   cd /opt
   git clone <仓库地址> ecommerce-admin
   # 注意：由于仓库结构，代码通常在下一层
   cd /opt/ecommerce-admin/ecommerce-admin 
   ```

### 2.2 修改端口 (避免冲突)
*   **MySQL**: `3307:3306` (外部访问用 3307)
*   **后端 API**: `5001:5000` (外部访问用 5001)

### 2.3 启动项目 (提速版)
由于已经在 `Dockerfile` 中配置了阿里云国内镜像，启动速度会非常快。
```bash
# 启动后台及数据库
docker-compose up -d --build

# [推荐] 启动全量生产环境 (含前端界面)
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 3. 运维与外部访问

### 3.1 阿里云防火墙配置 (安全组)
必须在阿里云后台放行以下端口：
*   **3344**: 网页端口 (浏览器输入 `http://IP:3344`)
*   **3307**: 数据库访问 (Navicat)
*   **5001**: 后端 API (可选，用于调试)

### 3.2 本地 Navicat 连接
*   **连接方式**: 直接连接 (不要勾选 SSH 隧道，速度更快)
*   **端口**: `3307`
*   **用户名**: `app_user`
*   **密码**: `app_password_123`

---

## 5. 小白避坑指南 (必看)
1.  **路径坑**: 记得执行命令前先 `ls` 确认当前文件夹下有 `docker-compose.yml`。如果提示 "no configuration file provided"，说明你还没进到最里层的文件夹。
2.  **网络坑**: 如果构建时卡在 `apt-get` 或 `npm install`，请检查 `Dockerfile` 是否包含我为您添加的 `mirrors.aliyun.com` 或 `npmmirror.com` 镜像脚本。
3.  **刷新坑**: 网页终端卡住没反应时，直接 **刷新浏览器页面** 重新进入，千万别等。
