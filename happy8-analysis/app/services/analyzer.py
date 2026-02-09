"""
彩票数据分析服务
负责核心的数据分析功能：遗漏分析、热号分析、推荐生成等
"""
from collections import Counter
from flask import current_app
import json
import os
from datetime import datetime

# ML预测器(可选,如果模型未训练则跳过)
try:
    from app.services.ml_predictor import ml_predictor
    ML_AVAILABLE = True
except Exception as e:
    ML_AVAILABLE = False
    ml_predictor = None


def analyze_omission(data):
    """
    分析号码遗漏
    
    Args:
        data: 历史数据列表
        
    Returns:
        dict: 包含遗漏数据和排行的字典
    """
    omission = {str(i).zfill(2): 0 for i in range(1, 81)}
    
    for item in data:
        for num in range(1, 81):
            num_str = str(num).zfill(2)
            if num_str in item['numbers']:
                omission[num_str] = 0
            else:
                omission[num_str] += 1
    
    # 排序
    sorted_omission = sorted(omission.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'data': omission,
        'top10': [{'number': k, 'omission': v} for k, v in sorted_omission[:10]]
    }


def analyze_hot_numbers(data):
    """
    分析热号
    
    Args:
        data: 历史数据列表
        
    Returns:
        dict: 包含热号数据和排行的字典
    """
    periods = current_app.config['HOT_NUMBER_PERIODS']
    counter = Counter()
    
    for item in data[:periods]:
        for num in item['numbers']:
            counter[num] += 1
    
    hot_list = counter.most_common(10)
    
    return {
        'data': dict(counter),
        'top10': [{'number': k, 'count': v} for k, v in hot_list]
    }


def analyze_repeat_numbers(data):
    """
    分析重号（与上期重复的号码）
    
    Args:
        data: 历史数据列表
        
    Returns:
        dict: 重号分析结果
    """
    if len(data) < 2:
        return {'recent_repeats': [], 'avg_repeat_count': 0}
    
    repeat_counts = []
    recent_repeats = []
    
    for i in range(min(10, len(data) - 1)):
        current = set(data[i]['numbers'])
        previous = set(data[i + 1]['numbers'])
        repeats = list(current & previous)
        
        repeat_counts.append(len(repeats))
        if i < 5:
            recent_repeats.append({
                'period': data[i]['period'],
                'count': len(repeats),
                'numbers': sorted(repeats)
            })
    
    avg_count = sum(repeat_counts) / len(repeat_counts) if repeat_counts else 0
    
    return {
        'recent_repeats': recent_repeats,
        'avg_repeat_count': round(avg_count, 1)
    }


def generate_recommendations(data, omission, hot_numbers):
    """
    生成推荐号码
    
    Args:
        data: 历史数据
        omission: 遗漏分析结果
        hot_numbers: 热号分析结果
        
    Returns:
        dict: 各种推荐策略的号码
    """
    # 胆码：结合遗漏和热度
    omission_top = [item['number'] for item in omission['top10'][:5]]
    hot_top = [item['number'] for item in hot_numbers['top10'][:10]]
    
    # 使用 sorted 确保确定性
    banker_codes = sorted(list(set(omission_top[:3] + hot_top[:3])))[:5]
    
    # 智能选号池
    all_candidates = sorted(list(set(omission_top[:8] + hot_top[:8])))
    
    # 选十推荐
    smart_pick10 = []
    smart_pick10.extend([item['number'] for item in hot_numbers['top10'][:7]])
    
    cold = [item['number'] for item in omission['top10'][:5]]
    for c in cold:
        if c not in smart_pick10:
            smart_pick10.append(c)
        if len(smart_pick10) >= 10:
            break
    
    # 补足10个
    for cand in all_candidates:
        if cand not in smart_pick10:
            smart_pick10.append(cand)
        if len(smart_pick10) >= 10:
            break
    
    smart_pick10 = sorted(smart_pick10[:10])
    
    recommendations = {
        'banker_codes': banker_codes[:3],
        'pick4_3dan': sorted(list(set(hot_top[:5]))[:3]),
        'pick5_4dan': sorted(list(set(hot_top[:6]))[:4]),
        'pick5_direct': sorted(list(set(hot_top[:7]))[:5]),
        'smart_pick5': sorted(all_candidates[:5]),
        'smart_pick6': sorted(all_candidates[:6]),
        'smart_pick7': sorted(all_candidates[:7]),
        'smart_pick10': smart_pick10
    }
    
    # 添加ML推荐(如果可用)
    if ML_AVAILABLE and ml_predictor and ml_predictor.is_trained:
        try:
            ml_recs = ml_predictor.generate_recommendations(data, balance=True)
            if ml_recs:
                recommendations.update(ml_recs)
                current_app.logger.info('ML推荐已生成')
        except Exception as e:
            current_app.logger.warning(f'ML推荐生成失败: {e}')
    
    return recommendations



def generate_trend_rows(data, limit=50):
    """
    生成走势图行数据
    
    Args:
        data: 历史数据
        limit: 返回的行数限制
        
    Returns:
        list: 走势图行数据
    """
    if not data:
        return []
    
    # 预热数据
    warmup = 50
    total_needed = limit + warmup
    
    # 按时间正序排列
    effective_data = data[:total_needed][::-1]
    
    # 初始化遗漏计数器
    current_omission = {str(i).zfill(2): 0 for i in range(1, 81)}
    
    rows = []
    
    for idx, row in enumerate(effective_data):
        period = row['period']
        winning_numbers = set(row['numbers'])
        
        row_data = {}
        for i in range(1, 81):
            num_str = str(i).zfill(2)
            is_hit = num_str in winning_numbers
            
            if is_hit:
                current_omission[num_str] = 0
                cell_data = {'hit': True, 'omission': 0}
            else:
                current_omission[num_str] += 1
                cell_data = {'hit': False, 'omission': current_omission[num_str]}
            
            row_data[i] = cell_data
        
        # 只收集请求数量的行
        if idx >= len(effective_data) - limit:
            rows.append({
                'period': period,
                'data': row_data
            })
    
    return rows


def generate_prediction_scores(hot_numbers, omission, limit=None):
    """
    生成预测分数
    
    Args:
        hot_numbers: 热号分析结果
        omission: 遗漏分析结果
        limit: 返回数量限制
        
    Returns:
        list: 预测分数列表
    """
    scores = []
    hot_data = hot_numbers.get('data', {})
    omission_data = omission.get('data', {})
    
    for i in range(1, 81):
        num_str = str(i).zfill(2)
        hot_val = hot_data.get(num_str, 0)
        miss_val = omission_data.get(num_str, 0)
        
        # 权重：热度优先，遗漏次要
        score = (hot_val * 10) + (miss_val * 3)
        scores.append({'num': num_str, 'score': score})
    
    # 按分数降序排列
    sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    
    if limit:
        return sorted_scores[:limit]
    return sorted_scores


def validate_recommendations(current_data):
    """
    验证历史推荐
    对比已保存的推荐号码与实际开奖号码
    """
    history_file = current_app.config['RECOMMENDATIONS_FILE']
    if not os.path.exists(history_file):
        return
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        updated = False
        # 遍历历史记录进行验证
        for item in current_data:
            period = str(item['period']).strip() # 强制转换并去除空格
            if period in history:
                # 即使已经有 validation，如果 actual_result 缺失也补上
                if 'validation' not in history[period] or 'actual_result' not in history[period]:
                    actual = item['numbers']
                    recommendations = history[period].get('recommendations', {})
                    
                    validation = {}
                    for key, predicted in recommendations.items():
                        if isinstance(predicted, list):
                            # 对比推荐号码与实际开奖号码
                            hits = [n for n in predicted if n in actual]
                            validation[key] = {
                                'predicted': predicted,
                                'hits': hits,
                                'hit_count': len(hits),
                                'hit_rate': f"{len(hits)/len(predicted)*100:.1f}%" if predicted else "0%"
                            }
                    
                    history[period]['actual_result'] = actual
                    history[period]['validation'] = validation
                    updated = True
                    current_app.logger.info(f"强制验证期号 {period} 成功")
        
        if updated:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
    except Exception as e:
        current_app.logger.error(f"验证推荐失败: {e}")


def get_analysis_results(data):
    """
    获取完整的分析结果
    
    Args:
        data: 历史数据列表
        
    Returns:
        dict: 完整的分析结果
    """
    if not data or len(data) < 10:
        current_app.logger.warning('数据不足，无法进行分析')
        return {}
    
    current_app.logger.info(f'开始分析 {len(data)} 期数据')
    
    # 首先自动验证历史推荐
    validate_recommendations(data)
    
    # 遗漏分析
    omission = analyze_omission(data)
    
    # 热号分析
    hot_numbers = analyze_hot_numbers(data)
    
    # 生成推荐（基于最新一期，预测下一期）
    recommendations = generate_recommendations(data, omission, hot_numbers)
    
    # 保存下一期的推荐
    try:
        last_period = int(data[0]['period'])
        next_period = str(last_period + 1)
        save_recommendation(next_period, recommendations)
    except Exception as e:
        current_app.logger.error(f'保存推荐失败: {e}')
    
    # 重号分析
    repeat_analysis = analyze_repeat_numbers(data)
    
    return {
        'last_period': data[0]['period'],  # 传出最新期号供前端显示
        'next_period': str(int(data[0]['period']) + 1),  # 预测期号
        'omission': omission,
        'omission_data': {
            'rows': generate_trend_rows(data),
            'stats': omission['data']
        },
        'hot_numbers': hot_numbers,
        'hot_nums': hot_numbers['top10'],
        'cold_nums': omission['top10'][:6],
        'top_hot_nums': hot_numbers['top10'],
        'top_cold_nums': omission['top10'][:10],
        'most_common': [[item['number'], item['count']] for item in hot_numbers['top10']],
        'least_common': [[item['number'], item['omission']] for item in omission['top10'][:10]],
        'co_occurrence': {
            'top_hot_nums': [item['number'] for item in hot_numbers['top10'][:6]],
            'history': []
        },
        'full_frequency': [[str(i).zfill(2), hot_numbers['data'].get(str(i).zfill(2), 0)] for i in range(1, 81)],
        'total_periods': len(data),
        'zones': {
            'zone1': {'count': 0, 'numbers': []},
            'zone2': {'count': 0, 'numbers': []},
            'zone3': {'count': 0, 'numbers': []},
            'zone4': {'count': 0, 'numbers': []}
        },
        'prediction_scores': generate_prediction_scores(hot_numbers, omission, limit=20),
        'recommendations': recommendations,
        'strategies': {
            'pick4_3dan': recommendations['pick4_3dan'],
            'pick5_4dan': recommendations['pick5_4dan'],
            'pick5_direct': recommendations['pick5_direct'],
            'pick6_direct': recommendations['smart_pick6'],
            'pick7_direct': recommendations['smart_pick7'],
            'smart_pick5': recommendations['smart_pick5'],
            'smart_pick6': recommendations['smart_pick6'],
            'smart_pick7': recommendations['smart_pick7'],
            'smart_pick10': recommendations['smart_pick10'],
            # ML推荐(如果存在)
            'ml_pick5': recommendations.get('ml_pick5'),
            'ml_pick6': recommendations.get('ml_pick6'),
            'ml_pick7': recommendations.get('ml_pick7'),
            'ml_pick10': recommendations.get('ml_pick10'),
            'ml_mixed': recommendations.get('ml_mixed')
        },
        'recommendation': {
            'hot_zone': '40-60区间',
            'dan_codes': recommendations['banker_codes'],
            'pick4_3dan': recommendations['pick4_3dan'],
            'pick5_4dan': recommendations['pick5_4dan'],
            'pick5_direct': recommendations['pick5_direct'],
            'smart_pick5': recommendations['smart_pick5'],
            'smart_pick6': recommendations['smart_pick6'],
            'smart_pick7': recommendations['smart_pick7']
        },
        'repeat_analysis': repeat_analysis['recent_repeats'],
    }


def save_recommendation(period, recommendations):
    """
    保存推荐到历史
    
    Args:
        period: 期号
        recommendations: 推荐号码
        
    Returns:
        bool: 是否成功
    """
    try:
        history_file = current_app.config['RECOMMENDATIONS_FILE']
        
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = {}
        
        history[period] = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'recommendations': recommendations
        }
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        current_app.logger.info(f'保存期号 {period} 推荐成功')
        return True
        
    except Exception as e:
        current_app.logger.error(f'保存推荐失败: {e}')
        return False


def load_recommendation_history():
    """
    加载推荐历史
    
    Returns:
        dict: 推荐历史
    """
    try:
        history_file = current_app.config['RECOMMENDATIONS_FILE']
        
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
        
    except Exception as e:
        current_app.logger.error(f'加载历史失败: {e}')
        return {}
