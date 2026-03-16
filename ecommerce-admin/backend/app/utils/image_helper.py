import os
from PIL import Image
from flask import current_app
import uuid
from werkzeug.utils import secure_filename

def compress_image(image_file, max_size=(800, 800), quality=70):
    """
    压缩图片并返回保存后的路径
    """
    # 确保上传目录存在
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/inventory')
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
    return f"/uploads/inventory/{filename}"

def save_image_from_bytes(image_bytes, filename, max_size=(800, 800), quality=70):
    """
    从二进制流保存并压缩图片 (用于 Excel 导入)
    """
    import io
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/inventory')
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
    
    return f"/uploads/inventory/{new_filename}"
