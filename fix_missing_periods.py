"""
手动为缺失的期号生成推荐和验证
用于补充历史推荐记录
"""
import json
import os
from datetime import datetime

# 读取CSV数据
def read_csv_data():
    csv_file = 'd:/happy8/data/happy8_history.csv'
    data = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[1:]  # 跳过标题行
        for line in lines:
            if line.strip():
                parts = line.strip().split(',')
                if len(parts) >= 22:
                    data.append({
                        'period': parts[0],
                        'date': parts[1],
                        'numbers': [parts[i].zfill(2) for i in range(2, 22)]
                    })
    return data

# 简化的推荐生成(基于热号)
def generate_simple_recommendations(history_data, target_index):
    """基于目标期号之前的数据生成推荐"""
    # 使用目标期号之前的20期数据
    analysis_data = history_data[target_index+1:target_index+21]
    
    # 统计热号
    from collections import Counter
    counter = Counter()
    for item in analysis_data:
        for num in item['numbers']:
            counter[num] += 1
    
    hot_nums = [num for num, count in counter.most_common(10)]
    
    return {
        'banker_codes': sorted(hot_nums[:3]),
        'pick4_3dan': sorted(hot_nums[:3]),
        'pick5_4dan': sorted(hot_nums[:4]),
        'pick5_direct': sorted(hot_nums[:5]),
        'smart_pick5': sorted(hot_nums[:5]),
        'smart_pick6': sorted(hot_nums[:6]),
        'smart_pick7': sorted(hot_nums[:7]),
        'smart_pick10': sorted(hot_nums[:10])
    }

# 验证推荐
def validate_recommendation(recommendations, actual_result):
    validation = {}
    for key, predicted in recommendations.items():
        if isinstance(predicted, list):
            hits = [n for n in predicted if n in actual_result]
            validation[key] = {
                'predicted': predicted,
                'hits': hits,
                'hit_count': len(hits),
                'hit_rate': f"{len(hits)/len(predicted)*100:.1f}%" if predicted else "0%"
            }
    return validation

# 主函数
def main():
    print("开始补充缺失的推荐记录...")
    
    # 读取历史数据
    history_data = read_csv_data()
    print(f"读取到 {len(history_data)} 期历史数据")
    
    # 读取现有推荐历史
    rec_file = 'd:/happy8/data/recommendations_history.json'
    with open(rec_file, 'r', encoding='utf-8') as f:
        rec_history = json.load(f)
    
    # 查找缺失的期号
    missing_periods = []
    for idx, item in enumerate(history_data):
        period = item['period']
        if period not in rec_history and period.startswith('2026'):
            missing_periods.append((period, idx, item))
    
    print(f"发现 {len(missing_periods)} 个缺失的期号: {[p[0] for p in missing_periods]}")
    
    # 为每个缺失的期号生成推荐和验证
    for period, idx, item in missing_periods:
        print(f"\n处理期号 {period}...")
        
        # 生成推荐(基于该期之前的数据)
        recommendations = generate_simple_recommendations(history_data, idx)
        
        # 验证推荐
        validation = validate_recommendation(recommendations, item['numbers'])
        
        # 添加到历史记录
        rec_history[period] = {
            'date': item['date'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'recommendations': recommendations,
            'actual_result': item['numbers'],
            'validation': validation
        }
        
        print(f"[OK] 期号 {period} 推荐已生成并验证")
        for key, val in validation.items():
            if val['hit_count'] > 0:
                print(f"  - {key}: {val['hit_count']}中 ({val['hit_rate']})")
    
    # 保存更新后的推荐历史
    with open(rec_file, 'w', encoding='utf-8') as f:
        json.dump(rec_history, f, ensure_ascii=False, indent=2)
    
    print(f"\n[SUCCESS] 完成!已更新 {len(missing_periods)} 个期号的推荐记录")
    print(f"推荐历史文件已保存: {rec_file}")

if __name__ == '__main__':
    main()
