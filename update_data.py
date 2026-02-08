"""
临时脚本:更新快乐8历史数据
"""
import requests
import csv
import os
import sys
from datetime import datetime

# 设置控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def fetch_latest_data(limit=100):
    """从福彩官网获取最新数据"""
    url = f'http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=kl8&issueCount={limit}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://www.cwl.gov.cn/ygkj/kjgg/kl8/'
    }
    
    print(f'正在从福彩官网获取最近 {limit} 期数据...')
    
    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        
        if response.status_code == 200:
            resp_json = response.json()
            
            if 'result' in resp_json:
                parsed_data = []
                for item in resp_json['result']:
                    # 格式化日期
                    raw_date = item.get('date', '')
                    clean_date = raw_date.split('(')[0] if '(' in raw_date else raw_date
                    
                    # 转换号码
                    raw_nums = item.get('red', '').split(',')
                    
                    parsed_data.append({
                        'period': item.get('code', ''),
                        'date': clean_date,
                        'numbers': [n.zfill(2) for n in raw_nums if n.strip()]
                    })
                
                print(f'成功获取 {len(parsed_data)} 期数据')
                if parsed_data:
                    print(f'最新期号: {parsed_data[0]["period"]} ({parsed_data[0]["date"]})')
                    print(f'最早期号: {parsed_data[-1]["period"]} ({parsed_data[-1]["date"]})')
                return parsed_data
            else:
                print('响应格式错误: 未找到 result 字段')
                return []
        else:
            print(f'请求失败: HTTP {response.status_code}')
            return []
            
    except Exception as e:
        print(f'获取数据失败: {e}')
        return []


def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
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
        
        print(f'[成功] 保存 {len(data)} 期数据到 {filename}')
        return True
        
    except Exception as e:
        print(f'[失败] 保存失败: {e}')
        return False


if __name__ == '__main__':
    # 获取数据
    data = fetch_latest_data(limit=100)
    
    if data:
        # 保存到CSV
        csv_file = os.path.join('data', 'happy8_history.csv')
        if save_to_csv(data, csv_file):
            print(f'\n数据更新完成! 共 {len(data)} 期')
        else:
            print('\n数据保存失败')
    else:
        print('\n无法获取数据')
