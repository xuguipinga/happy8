from flask import jsonify
from app.api import api
from app.services.analysis_service import AnalysisService

@api.route('/analysis/calculate', methods=['POST'])
def calculate_profit():
    """触发利润计算"""
    result = AnalysisService.calculate_profit()
    if result['success']:
        return jsonify({'code': 200, 'message': f"成功计算 {result['count']} 条订单利润"}), 200
    else:
        return jsonify({'code': 500, 'message': result['message']}), 500

@api.route('/analysis/dashboard', methods=['GET'])
def get_dashboard_stats():
    """获取仪表盘统计数据"""
    stats = AnalysisService.get_profit_stats()
    return jsonify({'code': 200, 'data': stats}), 200
