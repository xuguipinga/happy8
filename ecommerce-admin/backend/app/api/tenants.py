"""
租户管理API
提供租户信息查询、更新等功能
"""
from flask import request, jsonify, g
from app.api import api
from app.models.tenant import Tenant
from app.models.user import User
from app.extensions import db
from app.middleware import require_auth, require_admin


@api.route('/tenants/current', methods=['GET'])
@require_auth
def get_current_tenant():
    """获取当前用户的租户信息"""
    tenant = Tenant.query.get(g.tenant_id)
    if not tenant:
        return jsonify({'code': 404, 'message': '租户不存在'}), 404
    
    # 统计租户下的用户数
    user_count = User.query.filter_by(tenant_id=tenant.id).count()
    
    return jsonify({
        'code': 200,
        'data': {
            **tenant.to_dict(),
            'user_count': user_count
        }
    }), 200


@api.route('/tenants/current', methods=['PUT'])
@require_auth
@require_admin
def update_current_tenant():
    """更新当前租户信息(仅管理员)"""
    tenant = Tenant.query.get(g.tenant_id)
    if not tenant:
        return jsonify({'code': 404, 'message': '租户不存在'}), 404
    
    data = request.get_json()
    
    # 允许更新的字段
    allowed_fields = ['name', 'contact_person', 'contact_phone', 'contact_email']
    for field in allowed_fields:
        if field in data:
            setattr(tenant, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': tenant.to_dict()
    }), 200


@api.route('/tenants/users', methods=['GET'])
@require_auth
def get_tenant_users():
    """获取当前租户下的所有用户"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = User.query.filter_by(tenant_id=g.tenant_id)
    
    # 搜索
    search = request.args.get('search')
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.username.like(search_term)) |
            (User.email.like(search_term)) |
            (User.phone.like(search_term))
        )
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'role': user.role,
            'is_active': user.is_active,
            'parent_id': user.parent_id,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None
        })
    
    return jsonify({
        'code': 200,
        'data': {
            'items': data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
    }), 200


@api.route('/tenants/users', methods=['POST'])
@require_auth
@require_admin
def create_tenant_user():
    """创建子账号(仅管理员)"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['username', 'password']
    for field in required_fields:
        if not data or not data.get(field):
            return jsonify({'code': 400, 'message': f'{field} 不能为空'}), 400
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    phone = data.get('phone')
    role = data.get('role', 'user')  # 默认为普通用户
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400
    
    # 检查邮箱是否已存在
    if email and User.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'message': '邮箱已被注册'}), 400
    
    # 检查手机号是否已存在
    if phone and User.query.filter_by(phone=phone).first():
        return jsonify({'code': 400, 'message': '手机号已被注册'}), 400
    
    # 创建子账号
    from werkzeug.security import generate_password_hash
    new_user = User(
        username=username,
        email=email,
        phone=phone,
        password_hash=generate_password_hash(password),
        tenant_id=g.tenant_id,  # 使用当前用户的租户ID
        parent_id=g.current_user.id,  # 设置父账号
        role=role,
        is_active=True
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'code': 201,
        'message': '子账号创建成功',
        'data': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'phone': new_user.phone,
            'role': new_user.role
        }
    }), 201


@api.route('/tenants/users/<int:user_id>', methods=['PUT'])
@require_auth
@require_admin
def update_tenant_user(user_id):
    """更新子账号信息(仅管理员)"""
    user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id).first()
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 允许更新的字段
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'role' in data:
        user.role = data['role']
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    # 更新密码
    if 'password' in data and data['password']:
        from werkzeug.security import generate_password_hash
        user.password_hash = generate_password_hash(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功'
    }), 200


@api.route('/tenants/users/<int:user_id>', methods=['DELETE'])
@require_auth
@require_admin
def delete_tenant_user(user_id):
    """删除子账号(仅管理员)"""
    user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id).first()
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    # 不能删除自己
    if user.id == g.current_user.id:
        return jsonify({'code': 400, 'message': '不能删除自己'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    }), 200
