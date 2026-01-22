"""
快乐8彩票分析系统 - 配置文件
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

class Config:
    """基础配置"""
    # Flask 配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # 数据文件路径
    DATA_DIR = BASE_DIR / 'data'
    HISTORY_FILE = DATA_DIR / 'happy8_history.csv'
    RECOMMENDATIONS_FILE = DATA_DIR / 'recommendations_history.json'
    
    # 日志配置
    LOG_DIR = BASE_DIR / 'logs'
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 数据获取配置
    DEFAULT_LIMIT = 50
    CACHE_TIMEOUT = 3600  # 缓存超时时间（秒）
    REQUEST_TIMEOUT = 15  # 网络请求超时时间（秒）
    
    # API 数据源
    DATA_SOURCES = [
        {
            'name': '福彩官网',
            'url': 'http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=kl8&issueCount={limit}'
        },
        {
            'name': '彩票API',
            'url': 'https://api.kjapi.com/kl8/getOpenData.do?code=kl8&rows={limit}'
        }
    ]
    
    # 分析配置
    HOT_NUMBER_PERIODS = 20  # 热号分析期数
    PATTERN_ANALYSIS_PERIODS = 30  # 模式分析期数
    AC_ANALYSIS_PERIODS = 50  # AC值分析期数


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # 生产环境应该从环境变量读取敏感信息
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # 可以添加数据库配置等
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    LOG_LEVEL = 'DEBUG'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """获取配置对象"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
