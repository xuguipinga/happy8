import re
import pandas as pd

def _parse_float(value):
    """解析数值格式"""
    if pd.isna(value) or value == '':
        return 0.0
    try:
        # 如果已经是数字，直接返回
        if isinstance(value, (int, float)):
            return float(value)
        
        # 如果是字符串，尝试提取数字
        str_val = str(value)
        # 提取数字部分 (支持负数和小数)
        # Fix: The previous regex might have been too simple or imported incorrectly in the context
        match = re.search(r'-?\d+(\.\d+)?', str_val)
        if match:
            return float(match.group())
        return 0.0
    except Exception as e:
        print(f"Error parsing {value}: {e}")
        return 0.0

test_values = [
    "CNY 220.82",
    "$ 40.00",
    "USD 40.00",
    "123.45",
    100,
    None,
    float('nan'),
    "¥ 500.00"
]

print("Testing _parse_float logic:")
for val in test_values:
    result = _parse_float(val)
    print(f"Input: {repr(val)} -> Output: {result}")
