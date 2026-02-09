"""
Flask 路由模块
定义所有的 API 端点
"""
from flask import render_template, jsonify, request, current_app
from datetime import datetime, timedelta
from app.utils.data_loader import read_from_csv, fetch_data, save_manual_data
from app.services.analyzer import get_analysis_results, load_recommendation_history
from app.services.pattern import get_pattern_analysis


# 全局缓存
cached_data = []


def register_routes(app):
    """注册所有路由"""
    
    @app.route('/')
    def index():
        """主页"""
        return render_template('index.html')
    
    @app.route('/api/data')
    def get_data():
        """获取分析数据（实时读取模式）"""
        limit = request.args.get('limit', default=50, type=int)
        
        # 强制实时从本地 CSV 读取
        current_app.logger.info(f'实时分析请求: limit={limit}')
        data_from_file = read_from_csv(limit if limit > 50 else 50)
        
        if not data_from_file:
            return jsonify({
                'error': True,
                'message': '无法获取开奖数据，请检查 data/happy8_history.csv'
            }), 503
        
        # 切片数据
        data_to_analyze = data_from_file[:limit]
        
        # 分析数据
        analysis = get_analysis_results(data_to_analyze)
        
        # 添加模式分析
        pattern_results = get_pattern_analysis(data_to_analyze)
        
        return jsonify({
            'history': data_to_analyze,
            'analysis': analysis,
            'pattern_analysis': pattern_results
        })
    
    @app.route('/api/refresh')
    def refresh_data():
        """强制刷新数据"""
        global cached_data
        
        limit = request.args.get('num', default=50, type=int)
        
        # 强制从网络重新获取
        temp_data = fetch_data(limit=limit, force_network=True)
        
        # 检查是否成功获取数据
        if not temp_data:
            return jsonify({
                'error': True,
                'message': f'无法获取最近{limit}期数据，请检查网络连接后重试'
            }), 503
        
        # 更新缓存
        cached_data = temp_data
        analysis = get_analysis_results(cached_data)
        pattern_results = get_pattern_analysis(cached_data)
        
        current_app.logger.info(f'成功刷新 {limit} 期数据')
        
        return jsonify({
            'history': cached_data,
            'analysis': analysis,
            'pattern_analysis': pattern_results,
            'message': f'成功更新 {limit} 期数据'
        })
    
    @app.route('/api/history')
    def get_history():
        """获取推荐历史和验证记录"""
        history = load_recommendation_history()
        
        # 将字典转换为列表并按期号倒序排序
        history_list = []
        for period, data in history.items():
            data['period'] = period
            history_list.append(data)
        
        # 按期号倒序
        history_list.sort(key=lambda x: x['period'], reverse=True)
        
        return jsonify(history_list)
    
    @app.route('/api/submit_data', methods=['POST'])
    def submit_data():
        """手动提交开奖数据"""
        global cached_data
        
        try:
            data = request.json
            period = data.get('period')
            numbers = data.get('numbers')
            
            if not period or not numbers or len(numbers) != 20:
                return jsonify({
                    'success': False,
                    'message': '数据格式错误: 需要期号和20个号码'
                }), 400
            
            result = save_manual_data(period, numbers)
            
            if result['success']:
                # 重新加载数据
                limit = 50
                cached_data = read_from_csv(limit)
                
                # 执行分析
                analysis = get_analysis_results(cached_data)
                
                current_app.logger.info(f'手动录入期号 {period} 成功')
                
                return jsonify({
                    'success': True,
                    'message': '录入成功，分析已更新',
                    'history': cached_data,
                    'analysis': analysis
                })
            else:
                return jsonify(result), 400
                
        except Exception as e:
            current_app.logger.error(f'提交数据失败: {e}')
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/scheduler/status')
    def scheduler_status():
        """获取调度器状态"""
        from app.services.scheduler import scheduler
        from app.services.auto_updater import auto_updater
        
        if not scheduler.scheduler:
            return jsonify({
                'enabled': False,
                'message': '自动更新功能未启用'
            })
        
        return jsonify({
            'enabled': True,
            'running': scheduler.scheduler.running,
            'jobs': scheduler.get_jobs(),
            'updater_status': auto_updater.get_status()
        })
    
    @app.route('/health')
    def health_check():
        """健康检查端点"""
        return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
