"""
用户个人信息管理API
"""
from flask import request, jsonify, g
from app.api import api
from app.models.user import User
from app.extensions import db
from app.middleware import require_auth
from werkzeug.security import check_password_hash, generate_password_hash


@api.route('/auth/profile', methods=['PUT'])
@require_auth
def update_profile():
    """更新个人信息"""
    data = request.get_json()
    user = g.current_user
    
    # 允许更新的字段
    if 'email' in data:
        # 检查邮箱是否被其他用户使用
        if data['email'] and User.query.filter(User.email == data['email'], User.id != user.id).first():
            return jsonify({'code': 400, 'message': '邮箱已被使用'}), 400
        user.email = data['email']
    
    if 'phone' in data:
        # 检查手机号是否被其他用户使用
        if data['phone'] and User.query.filter(User.phone == data['phone'], User.id != user.id).first():
            return jsonify({'code': 400, 'message': '手机号已被使用'}), 400
        user.phone = data['phone']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功'
    }), 200


@api.route('/auth/change-password', methods=['POST'])
@require_auth
def change_password():
    """修改密码"""
    data = request.get_json()
    user = g.current_user
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'code': 400, 'message': '请提供旧密码和新密码'}), 400
    
    # 验证旧密码
    if not check_password_hash(user.password_hash, old_password):
        return jsonify({'code': 400, 'message': '当前密码错误'}), 400
    
    # 验证新密码长度
    if len(new_password) < 6:
        return jsonify({'code': 400, 'message': '新密码长度不能少于6位'}), 400
    
    # 更新密码
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '密码修改成功'
    }), 200
