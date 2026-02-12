"""
租户上下文中间件
提供认证装饰器和租户隔离功能
"""
from flask import g, request, jsonify
from functools import wraps
from app.utils.jwt_helper import verify_token
from app.models.user import User

def require_auth(f):
    """
    认证装饰器
    - 验证JWT Token
    - 设置全局上下文 g.current_user 和 g.tenant_id
    - 确保用户激活状态
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取 Token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'code': 401, 'message': '未提供认证令牌'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'code': 401, 'message': '令牌无效或已过期'}), 401
        
        # 获取用户信息
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        if not user.is_active:
            return jsonify({'code': 403, 'message': '账号已被禁用'}), 403
        
        # 设置全局上下文
        g.current_user = user
        g.tenant_id = user.tenant_id
        g.user_role = user.role
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_admin(f):
    """
    管理员权限装饰器
    - 必须先通过 @require_auth
    - 验证用户是否为管理员角色
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user_role') or g.user_role != 'admin':
            return jsonify({'code': 403, 'message': '需要管理员权限'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
