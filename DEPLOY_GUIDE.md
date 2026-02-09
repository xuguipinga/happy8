# 项目提交与部署指南

## 1. 提交本地修改 (Commit Local Changes)

由于你要提交的是重构后的整个项目结构，请按以下步骤操作。

### 步骤
1.  **查看状态**：确认所有文件移动操作都被 Git 识别。
    ```bash
    git status
    ```
    *你应该看到很多 deletes (原来的位置) 和 new file (新位置 `happy8-analysis/`)。*

2.  **全部添加到暂存区**：
    ```bash
    git add .
    ```
    *注意最后的点号 `.`，表示当前目录下所有变动。*

3.  **提交到本地仓库**：
    ```bash
    git commit -m "Refactor: Move project files to happy8-analysis subdirectory"
    ```

4.  **推送到远程仓库 (GitHub)**：
    ```bash
    git push origin master
    # 如果是 main 分支，则是 git push origin main
    ```

---

## 2. 服务器更新与发布 (Server Deployment)

你的项目似乎已经配置了 Docker 部署脚本。以下是在服务器上更新的通用步骤。

### 步骤
1.  **登录服务器**：
    使用 SSH 登录你的远程服务器。
    ```bash
    ssh user@your_server_ip
    ```

2.  **进入项目目录**：
    ```bash
    cd /app/happy8
    # 或者如果你放在其他位置，请进入相应目录
    ```

3.  **拉取最新代码**：
    ```bash
    git pull
    ```
    *这一步会把你在本地做的目录重构同步到服务器。*

4.  **执行部署脚本**：
    由于目录结构变了，需要使用新的路径来启动服务。你可以运行我们更新后的脚本（如果服务器上也有这个脚本）。
    
    或者，手动使用 Docker Compose 启动：
    ```bash
    # 停止旧服务 (如果 docker-compose.yml 还在旧位置，这步可能报错，可以直接跳到下一步强行重建)
    docker-compose down

    # 使用新路径启动服务
    # 注意：-f 指定了新结构下的 docker-compose.yml 文件路径
    docker-compose -f happy8-analysis/deployment/docker/docker-compose.yml up -d --build
    ```

### 极简自动部署脚本 (Optional)
你可以在服务器根目录下创建一个 `update.sh`：
```bash
#!/bin/bash
git pull
docker-compose -f happy8-analysis/deployment/docker/docker-compose.yml up -d --build
echo "Deployment completed!"
```
以后在服务器上只需要运行 `./update.sh` 即可。
