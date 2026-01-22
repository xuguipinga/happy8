"""
模式识别服务
包含：连号分析、同尾号分析、AC值分析
"""
from collections import Counter
from flask import current_app


def analyze_consecutive_numbers(data):
    """
    分析连号模式
    
    Args:
        data: 历史开奖数据列表
        
    Returns:
        dict: 连号分析结果
    """
    if not data:
        return {}
    
    consecutive_stats = {
        '2连': 0,
        '3连': 0,
        '4连': 0,
        '5连及以上': 0
    }
    
    recent_consecutive = []
    
    # 分析每期的连号情况
    for item in data[:10]:
        numbers = sorted([int(n) for n in item['numbers']])
        
        # 查找连号
        consecutive_groups = []
        current_group = [numbers[0]]
        
        for i in range(1, len(numbers)):
            if numbers[i] == numbers[i-1] + 1:
                current_group.append(numbers[i])
            else:
                if len(current_group) >= 2:
                    consecutive_groups.append(current_group[:])
                current_group = [numbers[i]]
        
        # 检查最后一组
        if len(current_group) >= 2:
            consecutive_groups.append(current_group)
        
        # 统计连号长度
        for group in consecutive_groups:
            length = len(group)
            if length == 2:
                consecutive_stats['2连'] += 1
            elif length == 3:
                consecutive_stats['3连'] += 1
            elif length == 4:
                consecutive_stats['4连'] += 1
            else:
                consecutive_stats['5连及以上'] += 1
            
            # 记录近期连号
            if len(recent_consecutive) < 5:
                recent_consecutive.append({
                    'period': item['period'],
                    'numbers': [str(n).zfill(2) for n in group]
                })
    
    # 推荐连号组合
    hot_zones = []
    for item in data[:20]:
        numbers = sorted([int(n) for n in item['numbers']])
        for i in range(len(numbers) - 1):
            if numbers[i+1] == numbers[i] + 1:
                zone = (numbers[i] // 10) * 10
                hot_zones.append(zone)
    
    # 找出最热的区间
    zone_counter = Counter(hot_zones)
    top_zones = [z for z, _ in zone_counter.most_common(3)]
    
    # 推荐连号
    recommended = []
    for zone in top_zones:
        start = zone + 3
        if start <= 77:
            recommended.append([str(start).zfill(2), str(start+1).zfill(2)])
    
    return {
        'stats': consecutive_stats,
        'recent_examples': recent_consecutive,
        'recommended': recommended[:2],
        'summary': f"近10期出现{sum(consecutive_stats.values())}组连号"
    }


def analyze_same_tail_numbers(data):
    """
    分析同尾号模式
    
    Args:
        data: 历史开奖数据列表
        
    Returns:
        dict: 同尾号分析结果
    """
    if not data:
        return {}
    
    periods = current_app.config['PATTERN_ANALYSIS_PERIODS']
    
    # 统计每个尾数的出现次数
    tail_counter = {str(i): 0 for i in range(10)}
    
    for item in data[:periods]:
        numbers = [int(n) for n in item['numbers']]
        for num in numbers:
            tail = str(num % 10)
            tail_counter[tail] += 1
    
    # 排序找出热尾和冷尾
    sorted_tails = sorted(tail_counter.items(), key=lambda x: x[1], reverse=True)
    hot_tails = [t[0] for t in sorted_tails[:3]]
    cold_tails = [t[0] for t in sorted_tails[-3:]]
    
    # 推荐同尾号
    recommended = []
    for tail in hot_tails[:2]:
        tail_numbers = []
        for num in range(int(tail), 81, 10):
            if num > 0:
                tail_numbers.append(str(num).zfill(2))
        
        if len(tail_numbers) >= 3:
            recommended.append(tail_numbers[2:5])
    
    return {
        'hot_tails': hot_tails,
        'cold_tails': cold_tails,
        'tail_frequency': tail_counter,
        'recommended': recommended,
        'summary': f"热尾: {','.join(hot_tails)} | 冷尾: {','.join(cold_tails)}"
    }


def calculate_ac_value(numbers):
    """
    计算AC值（算术复杂度）
    
    Args:
        numbers: 号码列表
        
    Returns:
        int: AC值
    """
    if len(numbers) < 2:
        return 0
    
    nums = sorted([int(n) for n in numbers])
    
    # 计算所有两两之差的绝对值
    differences = set()
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            diff = abs(nums[i] - nums[j])
            differences.add(diff)
    
    # AC值 = 差值个数 - (号码个数 - 1)
    ac_value = len(differences) - (len(nums) - 1)
    return ac_value


def analyze_ac_distribution(data):
    """
    分析历史AC值分布
    
    Args:
        data: 历史开奖数据列表
        
    Returns:
        dict: AC值分析结果
    """
    if not data:
        return {}
    
    periods = current_app.config['AC_ANALYSIS_PERIODS']
    ac_values = []
    
    # 计算每期的AC值
    for item in data[:periods]:
        ac = calculate_ac_value(item['numbers'])
        ac_values.append({
            'period': item['period'],
            'ac_value': ac
        })
    
    # 统计AC值分布
    ac_nums = [item['ac_value'] for item in ac_values]
    avg_ac = sum(ac_nums) / len(ac_nums) if ac_nums else 0
    min_ac = min(ac_nums) if ac_nums else 0
    max_ac = max(ac_nums) if ac_nums else 0
    
    # 找出最常见的AC值
    ac_counter = Counter(ac_nums)
    common_ac = [ac for ac, _ in ac_counter.most_common(3)]
    
    return {
        'average': round(avg_ac, 1),
        'min': min_ac,
        'max': max_ac,
        'common_values': common_ac,
        'recent_ac': ac_values[:10],
        'recommended_range': [int(avg_ac - 2), int(avg_ac + 2)],
        'summary': f"平均AC值: {avg_ac:.1f} | 常见范围: {min(common_ac) if common_ac else 0}-{max(common_ac) if common_ac else 0}"
    }


def get_pattern_analysis(data):
    """
    获取完整的模式分析结果
    
    Args:
        data: 历史开奖数据列表
        
    Returns:
        dict: 包含所有模式分析的字典
    """
    current_app.logger.info('开始模式分析')
    
    return {
        'consecutive': analyze_consecutive_numbers(data),
        'same_tail': analyze_same_tail_numbers(data),
        'ac_value': analyze_ac_distribution(data)
    }
