import os
from PIL import Image
from flask import current_app
import uuid
from werkzeug.utils import secure_filename

def compress_image(image_file, max_size=(800, 800), quality=70):
    """
    压缩图片并返回保存后的路径
    """
    # 确保上传目录存在 (加上 inventory 子目录以匹配 URL)
    base_upload = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    upload_folder = os.path.join(base_upload, 'inventory')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    # 生成唯一文件名
    ext = os.path.splitext(image_file.filename)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
        ext = '.jpg'
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_folder, filename)
    
    # 打开并压缩
    img = Image.open(image_file)
    
    # 转为 RGB 以支持 JPG 保存
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    # 调整大小
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # 保存
    img.save(filepath, optimize=True, quality=quality)
    
    # 返回访问路径
    # 返回访问路径 (加上 /api 以便 Nginx 统一处理)
    return f"/api/uploads/inventory/{filename}"

def save_image_from_bytes(image_bytes, filename, max_size=(800, 800), quality=70):
    """
    从二进制流保存并压缩图片 (用于 Excel 导入)
    """
    import io
    # 确保上传目录存在 (加上 inventory 子目录以匹配 URL)
    base_upload = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    upload_folder = os.path.join(base_upload, 'inventory')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    ext = os.path.splitext(filename)[1].lower()
    if not ext: ext = '.jpg'
    new_filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_folder, new_filename)
    
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    img.save(filepath, optimize=True, quality=quality)
    
    # 返回访问路径 (加上 /api 以便 Nginx 统一处理)
    return f"/api/uploads/inventory/{new_filename}"
