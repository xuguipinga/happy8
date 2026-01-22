"""
快乐8彩票分析系统 - 主运行文件
"""
import os
from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("快乐8彩票分析系统")
    print("=" * 60)
    print("启动 Web 服务...")
    print("访问 http://127.0.0.1:5000 查看分析大屏")
    print("=" * 60)
    
    # 获取配置
    port = int(os.environ.get('PORT', 5000))
    debug = app.config.get('DEBUG', False)
    
    # 运行应用
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
