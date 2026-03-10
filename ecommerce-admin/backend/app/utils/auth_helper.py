"""
认证辅助函数
用于简化API端点的认证和租户上下文获取
"""
from flask import request, jsonify
from app.utils.jwt_helper import verify_token
from app.models.user import User


def _get_user_from_header(auth_header):
    """内部函数: 从 Authorization header 解析出 User 对象"""
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, (jsonify({'code': 401, 'message': '未提供认证令牌'}), 401)

    token = auth_header.split(' ')[1]
    payload = verify_token(token)

    if not payload:
        return None, (jsonify({'code': 401, 'message': '令牌无效或已过期'}), 401)

    user = User.query.get(payload['user_id'])
    if not user or not user.is_active:
        return None, (jsonify({'code': 401, 'message': '用户无效或已禁用'}), 401)

    return user, None


def get_tenant_from_request():
    """
    从请求中获取租户ID（向后兼容，保持原有接口）
    返回: (tenant_id, error_response)
    """
    user, error = _get_user_from_header(request.headers.get('Authorization'))
    if error:
        return None, error
    return user.tenant_id, None


def get_user_from_request():
    """
    从请求中获取完整用户对象（用于需要记录操作人的场景）
    返回: (user, error_response)
    """
    return _get_user_from_header(request.headers.get('Authorization'))
