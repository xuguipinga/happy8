from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from app.api import api
from app.models.user import User
from app.extensions import db
from app.utils.jwt_helper import generate_token

@api.route('/auth/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()
    
    # 验证必填字段
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    # 支持用户名、邮箱、手机号登录
    user = User.query.filter(
        (User.username == username) | 
        (User.email == username) | 
        (User.phone == username)
    ).first()
    
    if not user:
        return jsonify({'code': 401, 'message': '用户不存在'}), 401
    
    if not user.is_active:
        return jsonify({'code': 403, 'message': '账号已被禁用'}), 403
    
    # 验证密码
    if not check_password_hash(user.password_hash, password):
        return jsonify({'code': 401, 'message': '密码错误'}), 401
    
    # 生成 Token
    token = generate_token(user.id, user.username)
    
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone
            }
        }
    }), 200


@api.route('/auth/register', methods=['POST'])
def register():
    """用户注册接口"""
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
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400
    
    # 检查邮箱是否已存在
    if email and User.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'message': '邮箱已被注册'}), 400
    
    # 检查手机号是否已存在
    if phone and User.query.filter_by(phone=phone).first():
        return jsonify({'code': 400, 'message': '手机号已被注册'}), 400
    
    # 创建新用户
    new_user = User(
        username=username,
        email=email,
        phone=phone,
        password_hash=generate_password_hash(password),
        is_active=True
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # 生成 Token
    token = generate_token(new_user.id, new_user.username)
    
    return jsonify({
        'code': 200,
        'message': '注册成功',
        'data': {
            'token': token,
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'phone': new_user.phone
            }
        }
    }), 201


@api.route('/auth/info', methods=['GET'])
def get_user_info():
    """获取当前用户信息（需要 Token）"""
    from app.utils.jwt_helper import verify_token
    
    # 从请求头获取 Token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'code': 401, 'message': '未提供认证令牌'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return jsonify({'code': 401, 'message': '令牌无效或已过期'}), 401
    
    user = User.query.get(payload['user_id'])
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'is_active': user.is_active,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    }), 200
