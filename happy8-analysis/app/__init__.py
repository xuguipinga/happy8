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
    
    # 初始化定时任务调度器
    from app.services.scheduler import scheduler
    from app.services.auto_updater import auto_updater
    
    scheduler.init_app(app)
    
    # 添加自动更新任务
    if app.config.get('AUTO_UPDATE_ENABLED', False):
        with app.app_context():
            interval = app.config.get('UPDATE_INTERVAL_MINUTES', 15)
            scheduler.add_interval_job(
                func=auto_updater.check_and_update,
                minutes=interval,
                job_id='auto_data_update'
            )
            app.logger.info(f'自动数据更新任务已配置 (间隔: {interval}分钟)')
    
    # 尝试加载ML模型
    try:
        from app.services.ml_predictor import ml_predictor
        with app.app_context():
            if ml_predictor.load_models():
                app.logger.info('ML预测模型已加载')
            else:
                app.logger.info('ML模型文件不存在,请运行 train_ml_model.py 训练模型')
    except Exception as e:
        app.logger.warning(f'ML模型加载失败: {e}')
    
    # 启动调度器
    scheduler.start()
    
    return app
