"""
快乐8彩票分析系统 - 应用初始化
"""
from flask import Flask
from config import get_config
import os


def create_app(config_name=None):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(get_config(config_name))
    
    # 确保必要的目录存在
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    os.makedirs(app.config['LOG_DIR'], exist_ok=True)
    
    # 初始化日志
    from app.utils.logger import setup_logger
    setup_logger(app)
    
    # 注册路由
    from app.routes import register_routes
    register_routes(app)
    
    return app
