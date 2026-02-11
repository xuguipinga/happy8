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
参考之前的步骤，把 `ecommerce-admin` 传到 `/opt/ecommerce-admin`。

### 2.2 修改端口 (避免冲突)
**这是最关键的一步！** 为了让新旧项目能**同时运行**，我们需要给新项目换个窗口。

1.  打开 `docker-compose.yml`。
2.  找到 `db` (MySQL) 服务：把 `3306:3306` 改成 `3307:3306` (防止和旧项目数据库冲突)。
    *   **为什么要改？(小白必读)**
        *   **原理**：每个 MySQL 容器都在自己的“小房间”里，默认都用 `3306` 插座。但是你的服务器（大楼）只有一个对外的 `3306` 接口。
        *   **冲突**：旧项目已经占用了大楼的 `3306` 接口，新项目如果也想用，就会打架（端口冲突）。
        *   **解决**：我们把 `3306:3306` 改成 `3307:3306`。
            *   **冒号左边 (3307)**：是借用大楼的一个新接口。
            *   **冒号右边 (3306)**：是连到房间里的 3306 插座。
        *   **结论**：
            *   **Python代码不用改**：容器内部通讯依然用 `3306`，完全无感。
            *   **Navicat要改**：如果你从电脑远程连数据库，记得填 `3307`。
    *   **老板定下的规矩 (Port Standard)**：
        *   从本项目开始，端口号依次递增。
        *   **电商项目 (Ecommerce)**: MySQL=`3307`, Token=`6380`, 后端=`5001`。
        *   **未来项目 (Proejct X)**: MySQL=`3308`, Token=`6381`, 后端=`5002`... 以此类推。
3.  找到 `backend` 服务 (如果有)：把 `5000:5000` 改成 `5001:5000`。

### 2.3 启动新项目
```bash
cd /opt/ecommerce-admin
docker-compose up -d
```

### 2.4 查看运行状态
```bash
docker ps
```
**规范的 Docker 应用**：
*   Status 是 `Up` (运行中)。
*   PORTS 显示了正确的映射 (比如 `0.0.0.0:3307->3306/tcp`)。

---

## 3. Nginx 配置 (如何让两个项目共存)

如果您希望：
*   访问 `happy8.com` -> 进旧项目
*   访问 `admin.happy8.com` -> 进新项目

您需要一个**总 Nginx** 来做分发。

### 3.1 安装总 Nginx (推荐方式)
不要用项目里的 Nginx，直接在服务器宿主机装一个 Nginx。
```bash
sudo apt-get install nginx
```

### 3.2 配置转发
编辑配置文件：`sudo vim /etc/nginx/sites-available/default`

```nginx
# 旧项目 (Happy8 Analysis)
server {
    listen 80;
    server_name happy8.com; # 您的旧域名

    location / {
        # 转发给旧项目的容器端口 (假设旧项目跑在 5000)
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
    }
}

# 新项目 (Ecommerce Admin)
server {
    listen 80;
    server_name admin.happy8.com; # 您的新域名

    location / {
        # 转发给新项目的容器端口 (假设新项目跑在 5001)
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
    }
}
```

### 3.3 重启 Nginx
```bash
sudo systemctl reload nginx
```

---

## 4. 常用命令速查表 (Cheat Sheet)

| 动作 | 命令 | 解释 |
| :--- | :--- | :--- |
| **看所有容器** | `docker ps -a` | 就像任务管理器，看谁在跑，谁死了 |
| **看日志** | `docker logs -f <容器名>` | 比如 `docker logs -f ecommerce_backend`，实时看报错 |
| **进容器内部** | `docker exec -it <容器名> bash` | 就像远程登录到了容器系统里 |
| **重启容器** | `docker restart <容器名>` | 卡死的时候用 |
| **清理垃圾** | `docker system prune -f` | 删掉没用的镜像和缓存，释放硬盘空间 |

---

## 5. 小白避坑指南
1.  **不要直接在此处改代码**：永远在本地 VS Code 改好，测试没问题了，再传上去重启。不要直接在服务器用 vim 改代码，很难调试。
2.  **数据备份**：我们在 `docker-compose.yml` 里配置了 `./data:/var/lib/mysql`。这意味着数据文件就在你眼皮子底下的 `data` 文件夹里。**定期把这个 data 文件夹下载到本地备份**，你就永远不会丢数据。
3.  **不要随便删文件**：`docker-compose down` 没事，但如果你删了 `data` 文件夹，数据就真没了。
