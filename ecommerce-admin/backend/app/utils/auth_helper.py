"""
认证辅助函数
用于简化API端点的认证和租户上下文获取
"""
from flask import request, jsonify
from app.utils.jwt_helper import verify_token
from app.models.user import User


def get_tenant_from_request():
    """
    从请求中获取租户ID
    返回: (tenant_id, error_response)
    如果成功,error_response为None
    如果失败,tenant_id为None,error_response为Flask响应对象
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, (jsonify({'code': 401, 'message': '未提供认证令牌'}), 401)
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return None, (jsonify({'code': 401, 'message': '令牌无效或已过期'}), 401)
    
    user = User.query.get(payload['user_id'])
    if not user or not user.is_active:
        return None, (jsonify({'code': 401, 'message': '用户无效或已禁用'}), 401)
    
    return user.tenant_id, None
