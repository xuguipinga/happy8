import os
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.api import api
from app.services.excel_service import ExcelService
from app.utils.jwt_helper import verify_token

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload_file(file):
    if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
        os.makedirs(current_app.config['UPLOAD_FOLDER'])
    
    filename = secure_filename(file.filename)
    # 给文件名加时间戳防止重名覆盖
    import time
    filename = f"{int(time.time())}_{filename}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    return file_path

@api.route('/upload/orders/preview', methods=['POST'])
def preview_orders():
    """预览订单Excel导入"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未找到文件'}), 400
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        try:
            file_path = save_upload_file(file)
            result = ExcelService.preview_orders(file_path)
            
            # 预览后删除临时文件
            try:
                os.remove(file_path)
            except:
                pass
            
            if result['success']:
                return jsonify({
                    'code': 200, 
                    'message': '预览成功',
                    'data': result['data']
                }), 200
            else:
                return jsonify({'code': 500, 'message': result['message']}), 500
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)}), 500
            
    return jsonify({'code': 400, 'message': '不支持的文件格式'}), 400

@api.route('/upload/orders', methods=['POST'])
def upload_orders():
    """上传订单Excel"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未找到文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'message': '未选择文件'}), 400
    
    if file and allowed_file(file.filename):
        try:
            file_path = save_upload_file(file)
            result = ExcelService.import_orders(file_path)
            
            # 可以在处理完后删除文件，或者保留备份
            # os.remove(file_path)
            
            if result['success']:
                return jsonify({
                    'code': 200, 
                    'message': f"成功导入 {result['count']} 条订单数据",
                    'data': {'errors': result['errors']}
                }), 200
            else:
                return jsonify({'code': 500, 'message': result['message']}), 500
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)}), 500
    
    return jsonify({'code': 400, 'message': '不支持的文件格式'}), 400

@api.route('/upload/purchases/preview', methods=['POST'])
def preview_purchases():
    """预览采购Excel导入"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未找到文件'}), 400
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        try:
            file_path = save_upload_file(file)
            result = ExcelService.preview_purchases(file_path)
            
            # 预览后删除临时文件
            try:
                os.remove(file_path)
            except:
                pass
            
            if result['success']:
                return jsonify({
                    'code': 200, 
                    'message': '预览成功',
                    'data': result['data']
                }), 200
            else:
                return jsonify({'code': 500, 'message': result['message']}), 500
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)}), 500
            
    return jsonify({'code': 400, 'message': '不支持的文件格式'}), 400

@api.route('/upload/purchases', methods=['POST'])
def upload_purchases():
    """上传采购Excel"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未找到文件'}), 400
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        try:
            file_path = save_upload_file(file)
            result = ExcelService.import_purchases(file_path)
            
            if result['success']:
                return jsonify({
                    'code': 200, 
                    'message': f"成功导入 {result['count']} 条采购数据",
                    'data': {'errors': result['errors']}
                }), 200
            else:
                return jsonify({'code': 500, 'message': result['message']}), 500
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)}), 500
            
    return jsonify({'code': 400, 'message': '不做支持的文件格式'}), 400

@api.route('/upload/logistics/preview', methods=['POST'])
def preview_logistics():
    """预览物流Excel导入"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未找到文件'}), 400
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        try:
            file_path = save_upload_file(file)
            result = ExcelService.preview_logistics(file_path)
            
            # 预览后删除临时文件
            try:
                os.remove(file_path)
            except:
                pass
            
            if result['success']:
                return jsonify({
                    'code': 200, 
                    'message': '预览成功',
                    'data': result['data']
                }), 200
            else:
                return jsonify({'code': 500, 'message': result['message']}), 500
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)}), 500
            
    return jsonify({'code': 400, 'message': '不支持的文件格式'}), 400

@api.route('/upload/logistics', methods=['POST'])
def upload_logistics():
    """上传物流Excel"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '未找到文件'}), 400
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        try:
            file_path = save_upload_file(file)
            result = ExcelService.import_logistics(file_path)
            
            if result['success']:
                return jsonify({
                    'code': 200, 
                    'message': f"成功导入 {result['count']} 条物流数据",
                    'data': {'errors': result['errors']}
                }), 200
            else:
                return jsonify({'code': 500, 'message': result['message']}), 500
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)}), 500
            
    return jsonify({'code': 400, 'message': '不支持的文件格式'}), 400
