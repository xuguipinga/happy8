"""
数据加载模块
负责从 CSV 文件和网络 API 获取彩票数据
"""
import csv
import os
import requests
from datetime import datetime
from flask import current_app


def read_from_csv(limit=50):
    """
    从CSV文件读取历史数据
    
    Args:
        limit: 读取的数据条数
        
    Returns:
        list: 历史数据列表，每项包含 period, date, numbers
    """
    history_file = current_app.config['HISTORY_FILE']
    
    if not os.path.exists(history_file):
        current_app.logger.warning(f'数据文件不存在: {history_file}')
        return []
    
    data = []
    try:
        with open(history_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 提取号码
                numbers = []
                for key in row.keys():
                    if key.startswith('号码') or (key.isdigit() or key[1:].isdigit() if len(key) > 1 else False):
                        if row[key]:
                            numbers.append(row[key].zfill(2))
                
                # 如果没有找到号码列，尝试从所有列中提取
                if not numbers:
                    for key, value in row.items():
                        if value and value.isdigit() and 1 <= int(value) <= 80:
                            numbers.append(value.zfill(2))
                
                if len(numbers) >= 20:
                    data.append({
                        'period': row.get('期号', row.get(list(row.keys())[0], '')),
                        'date': row.get('日期', row.get(list(row.keys())[1], '')),
                        'numbers': numbers[:20]
                    })
                
                if len(data) >= limit:
                    break
                    
        current_app.logger.info(f'从CSV读取 {len(data)} 期数据')
        return data
        
    except Exception as e:
        current_app.logger.error(f'读取CSV文件失败: {e}')
        return []


def save_to_csv(data):
    """
    保存数据到CSV文件
    
    Args:
        data: 要保存的数据列表
        
    Returns:
        bool: 保存是否成功
    """
    history_file = current_app.config['HISTORY_FILE']
    
    try:
        with open(history_file, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['期号', '日期'] + [f'号码{i+1}' for i in range(20)]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in data:
                row = {
                    '期号': item['period'],
                    '日期': item['date']
                }
                for i, num in enumerate(item['numbers'][:20]):
                    row[f'号码{i+1}'] = num
                writer.writerow(row)
                
        current_app.logger.info(f'保存 {len(data)} 期数据到CSV')
        return True
        
    except Exception as e:
        current_app.logger.error(f'保存CSV文件失败: {e}')
        return False


def save_manual_data(period, numbers):
    """
    保存手动录入的数据
    
    Args:
        period: 期号
        numbers: 号码列表
        
    Returns:
        dict: 包含 success 和 message 的结果字典
    """
    try:
        current_data = read_from_csv(limit=1000)
        
        # 检查期号是否已存在
        for item in current_data:
            if item['period'] == period:
                return {'success': False, 'message': f'期号 {period} 已存在'}
        
        # 添加新数据
        today = datetime.now().strftime('%Y-%m-%d')
        new_item = {
            'period': period,
            'date': today,
            'numbers': [str(n).zfill(2) for n in numbers]
        }
        
        current_data.insert(0, new_item)
        current_data.sort(key=lambda x: x['period'], reverse=True)
        
        if save_to_csv(current_data):
            current_app.logger.info(f'手动录入期号 {period} 成功')
            return {'success': True, 'message': '保存成功'}
        else:
            return {'success': False, 'message': '保存失败'}
            
    except Exception as e:
        current_app.logger.error(f'手动录入数据失败: {e}')
        return {'success': False, 'message': str(e)}


def fetch_from_network(limit=50):
    """
    从网络API获取数据
    
    Args:
        limit: 获取的数据条数
        
    Returns:
        list: 获取的数据列表，失败返回空列表
    """
    current_app.logger.info(f'从网络获取最近 {limit} 期数据')
    
    # 清除代理
    os.environ.pop('HTTP_PROXY', None)
    os.environ.pop('HTTPS_PROXY', None)
    
    sources = current_app.config['DATA_SOURCES']
    # 福彩官网必须带上 Referer
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'http://www.cwl.gov.cn/ygkj/kjgg/kl8/'
    }
    timeout = current_app.config['REQUEST_TIMEOUT']
    
    for source in sources:
        try:
            url = source['url'].format(limit=limit)
            current_app.logger.debug(f"尝试数据源: {source['name']}")
            
            # 使用 verify=False 绕过某些环境下的 SSL 证书问题
            response = requests.get(url, headers=headers, timeout=timeout, verify=False)
            
            if response.status_code == 200:
                resp_json = response.json()
                
                # 解析福彩官网格式
                if source['name'] == '福彩官网' and 'result' in resp_json:
                    parsed_data = []
                    for item in resp_json['result']:
                        # 格式化日期: "2024-01-21(日)" -> "2024-01-21"
                        raw_date = item.get('date', '')
                        clean_date = raw_date.split('(')[0] if '(' in raw_date else raw_date
                        
                        # 转换号码: "01,02,03..." -> ["01", "02", "03"...]
                        raw_nums = item.get('red', '').split(',')
                        
                        parsed_data.append({
                            'period': item.get('code', ''),
                            'date': clean_date,
                            'numbers': [n.zfill(2) for n in raw_nums if n.strip()]
                        })
                    
                    if parsed_data:
                        current_app.logger.info(f"{source['name']} 解析成功，获取 {len(parsed_data)} 期数据")
                        return parsed_data
                
                # TODO: 实现其他数据源解析
                current_app.logger.warning(f"{source['name']} 返回数据，但解析逻辑未适配")
                
        except Exception as e:
            current_app.logger.error(f"{source['name']} 请求失败: {str(e)[:100]}")
    
    return []


def fetch_data(limit=50, force_network=False):
    """
    获取数据（优先本地，可强制网络）
    
    Args:
        limit: 数据条数
        force_network: 是否强制从网络获取
        
    Returns:
        list: 数据列表
    """
    # 如果不是强制网络模式，优先读取本地
    if not force_network:
        local_data = read_from_csv(limit)
        if local_data and len(local_data) >= limit:
            current_app.logger.info(f'使用本地缓存数据 {len(local_data)} 期')
            return local_data
    else:
        current_app.logger.info('强制刷新模式，跳过本地缓存')
    
    # 尝试网络获取
    network_data = fetch_from_network(limit)
    if network_data:
        save_to_csv(network_data)
        return network_data
    
    # 降级使用本地数据
    current_app.logger.warning('网络获取失败，降级使用本地数据')
    return read_from_csv(limit)
