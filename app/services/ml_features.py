"""
机器学习特征提取模块
从历史开奖数据中提取用于预测的特征
"""
import numpy as np
from collections import Counter


def extract_basic_features(numbers):
    """
    提取基础统计特征
    
    Args:
        numbers: 开奖号码列表,如 ['01', '02', ...]
        
    Returns:
        dict: 特征字典
    """
    nums = [int(n) for n in numbers]
    nums_sorted = sorted(nums)
    
    features = {}
    
    # 和值
    features['sum'] = sum(nums)
    
    # 跨度
    features['span'] = max(nums) - min(nums)
    
    # 奇偶比
    odd_count = sum(1 for n in nums if n % 2 == 1)
    even_count = 20 - odd_count
    features['odd_count'] = odd_count
    features['even_count'] = even_count
    features['odd_even_ratio'] = odd_count / even_count if even_count > 0 else 20
    
    # 大小比 (1-40为小,41-80为大)
    small_count = sum(1 for n in nums if n <= 40)
    big_count = 20 - small_count
    features['small_count'] = small_count
    features['big_count'] = big_count
    features['big_small_ratio'] = big_count / small_count if small_count > 0 else 20
    
    # 质数统计
    primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 
              53, 59, 61, 67, 71, 73, 79}
    prime_count = sum(1 for n in nums if n in primes)
    features['prime_count'] = prime_count
    
    return features


def extract_zone_features(numbers):
    """
    提取区间分布特征
    
    Args:
        numbers: 开奖号码列表
        
    Returns:
        dict: 区间特征
    """
    nums = [int(n) for n in numbers]
    
    # 将1-80分为4个区间
    zones = {
        'zone1': 0,  # 1-20
        'zone2': 0,  # 21-40
        'zone3': 0,  # 41-60
        'zone4': 0   # 61-80
    }
    
    for n in nums:
        if n <= 20:
            zones['zone1'] += 1
        elif n <= 40:
            zones['zone2'] += 1
        elif n <= 60:
            zones['zone3'] += 1
        else:
            zones['zone4'] += 1
    
    # 区间方差(衡量分布均匀度)
    zone_counts = list(zones.values())
    zones['zone_variance'] = np.var(zone_counts)
    
    return zones


def extract_pattern_features(numbers):
    """
    提取模式特征
    
    Args:
        numbers: 开奖号码列表
        
    Returns:
        dict: 模式特征
    """
    nums = sorted([int(n) for n in numbers])
    
    features = {}
    
    # 连号数量
    consecutive_count = 0
    for i in range(len(nums) - 1):
        if nums[i+1] - nums[i] == 1:
            consecutive_count += 1
    features['consecutive_count'] = consecutive_count
    
    # 同尾号数量
    tail_counter = Counter([n % 10 for n in nums])
    same_tail_count = sum(1 for count in tail_counter.values() if count > 1)
    features['same_tail_count'] = same_tail_count
    
    # AC值(号码离散度)
    ac_value = calculate_ac_value(nums)
    features['ac_value'] = ac_value
    
    return features


def calculate_ac_value(nums):
    """
    计算AC值(Arithmetic Complexity)
    AC值越大,号码越分散
    
    Args:
        nums: 排序后的号码列表
        
    Returns:
        int: AC值
    """
    if len(nums) < 2:
        return 0
    
    differences = set()
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            differences.add(abs(nums[i] - nums[j]))
    
    return len(differences) - (len(nums) - 1)


def extract_repeat_features(current_numbers, previous_numbers):
    """
    提取重号特征
    
    Args:
        current_numbers: 当前期号码
        previous_numbers: 上一期号码
        
    Returns:
        dict: 重号特征
    """
    if not previous_numbers:
        return {'repeat_count': 0}
    
    current_set = set(current_numbers)
    previous_set = set(previous_numbers)
    
    repeat_count = len(current_set & previous_set)
    
    return {'repeat_count': repeat_count}


def extract_number_frequency(history_data, periods=20):
    """
    提取号码频率特征
    
    Args:
        history_data: 历史数据列表
        periods: 统计的期数
        
    Returns:
        dict: 每个号码的出现频率
    """
    frequency = {str(i).zfill(2): 0 for i in range(1, 81)}
    
    for item in history_data[:periods]:
        for num in item['numbers']:
            frequency[num] += 1
    
    return frequency


def extract_number_omission(history_data):
    """
    提取号码遗漏值
    
    Args:
        history_data: 历史数据列表(按时间倒序)
        
    Returns:
        dict: 每个号码的遗漏期数
    """
    omission = {str(i).zfill(2): 0 for i in range(1, 81)}
    
    for item in history_data:
        for num in range(1, 81):
            num_str = str(num).zfill(2)
            if num_str in item['numbers']:
                # 找到了,停止计数
                break
            else:
                omission[num_str] += 1
    
    return omission


def extract_all_features(history_data, target_index=0):
    """
    提取所有特征
    
    Args:
        history_data: 历史数据列表(按时间倒序)
        target_index: 目标期在列表中的索引
        
    Returns:
        dict: 所有特征的字典
    """
    if target_index >= len(history_data):
        return None
    
    target_item = history_data[target_index]
    features = {}
    
    # 基础特征
    basic = extract_basic_features(target_item['numbers'])
    features.update(basic)
    
    # 区间特征
    zones = extract_zone_features(target_item['numbers'])
    features.update(zones)
    
    # 模式特征
    patterns = extract_pattern_features(target_item['numbers'])
    features.update(patterns)
    
    # 重号特征
    if target_index + 1 < len(history_data):
        previous_item = history_data[target_index + 1]
        repeat = extract_repeat_features(
            target_item['numbers'],
            previous_item['numbers']
        )
        features.update(repeat)
    else:
        features['repeat_count'] = 0
    
    # 号码频率(基于目标期之前的数据)
    if target_index + 1 < len(history_data):
        freq_data = history_data[target_index + 1:]
        frequency = extract_number_frequency(freq_data, periods=20)
        # 只保存频率的统计特征,不保存每个号码的频率
        freq_values = list(frequency.values())
        features['freq_mean'] = np.mean(freq_values)
        features['freq_std'] = np.std(freq_values)
        features['freq_max'] = max(freq_values)
        features['freq_min'] = min(freq_values)
    
    return features


def create_training_dataset(history_data, window_size=10):
    """
    创建训练数据集
    
    Args:
        history_data: 历史数据列表
        window_size: 特征窗口大小
        
    Returns:
        tuple: (X, y, number_labels)
            X: 特征矩阵
            y: 标签矩阵(80列,每列表示一个号码是否出现)
            number_labels: 号码列表
    """
    X = []
    y = []
    
    # 为每个可以作为目标的期号创建样本
    for i in range(len(history_data) - window_size):
        # 提取特征(基于前window_size期的数据)
        feature_dict = extract_all_features(history_data, i)
        if feature_dict is None:
            continue
        
        # 转换为特征向量
        feature_vector = list(feature_dict.values())
        X.append(feature_vector)
        
        # 创建标签向量(80个号码的出现情况)
        target_numbers = history_data[i]['numbers']
        label_vector = []
        for num in range(1, 81):
            num_str = str(num).zfill(2)
            label_vector.append(1 if num_str in target_numbers else 0)
        y.append(label_vector)
    
    return np.array(X), np.array(y), [str(i).zfill(2) for i in range(1, 81)]


if __name__ == '__main__':
    # 测试代码
    test_numbers = ['01', '05', '12', '18', '23', '28', '35', '42', '48', '55',
                    '61', '62', '63', '68', '70', '72', '75', '77', '78', '80']
    
    print("基础特征:")
    print(extract_basic_features(test_numbers))
    
    print("\n区间特征:")
    print(extract_zone_features(test_numbers))
    
    print("\n模式特征:")
    print(extract_pattern_features(test_numbers))
