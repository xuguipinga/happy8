from flask import Flask
from config import config
from app.extensions import db, migrate, cors

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    
    # 注册模型 (确保迁移工具能检测到)
    from app import models

    # 注册蓝图
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    @app.route('/')
    def index():
        return 'Ecommerce Admin API is running!'

    # 静态文件服务：图片上传目录 (增加 /api 前缀以利用 Nginx 的 /api 代理)
    @app.route('/api/uploads/<path:filename>')
    def uploaded_file(filename):
        from flask import send_from_directory
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app
