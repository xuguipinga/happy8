import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://root:root@localhost/ecommerce_admin'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 租户配置
    TENANT_ID_HEADER = 'X-Tenant-ID'

config = Config()
