import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_token(user_id, username, tenant_id):
    """生成 JWT Token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'tenant_id': tenant_id,  # 添加租户ID
        'exp': datetime.utcnow() + timedelta(days=7),  # 7天过期
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    """验证 JWT Token"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token 已过期
    except jwt.InvalidTokenError:
        return None  # Token 无效
