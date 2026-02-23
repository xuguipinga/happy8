# 阿里上部署上线 - 终结手册

本手册记录了 2026-02-23 本次成功上线的所有关键配置和日常运维命令。

## 📍 访问信息
- **管理后台**: [http://47.123.7.106:3344](http://47.123.7.106:3344)
- **数据库 (3307)**: `47.123.7.106:3307`

## 🔐 凭据汇总
- **超管账号**: `admin` / `123456`
- **DB 账号**: `app_user` / `app_password_123`
- **DB Root**: `root` / `root`

## 🛠️ 日常维护常用命令

### 1. 更新前端（本地重打包场景）
如果您在本地修改了前端代码：
1. 本地执行 `npm run build`。
2. 将 `dist` 文件夹上传到服务器对应目录。
3. 服务器执行：`docker compose -f docker-compose.prod.yml restart frontend`。

### 2. 更新后端（Git 同步场景）
1. 服务器执行：`git pull`。
2. 服务器执行：`docker compose -f docker-compose.prod.yml up -d --build backend`。

### 3. 查看日志（排查问题）
```bash
# 查看后端实时日志
docker logs -f ecommerce_backend --tail 50
```

### 4. 数据库表初始化（如需重置）
```bash
docker exec -it ecommerce_backend python -c "from app import create_app, db; from app.models.user import User; from app.models.tenant import Tenant; from werkzeug.security import generate_password_hash; app=create_app(); app.app_context().push(); db.create_all(); t=Tenant.query.filter_by(code='DEFAULT').first() or Tenant(name='默认租户', code='DEFAULT'); db.session.add(t); db.session.commit(); u=User.query.filter_by(username='admin').first(); [db.session.add(User(username='admin', email='admin@example.com', password_hash=generate_password_hash('123456'), tenant_id=t.id, role='admin', is_active=True)) if not u else None]; db.session.commit(); print('数据库初始化完成！')"
```

---
**提示**: 为了安全起见，建议系统上线稳定后在阿里云后台关闭 3307 端口的入方向规则，仅在需要维护时开启。
