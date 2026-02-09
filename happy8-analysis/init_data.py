
import requests
import csv
import os

def init_data():
    url = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=kl8&issueCount=50"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'http://www.cwl.gov.cn/ygkj/kjgg/kl8/'
    }
    
    print("正在尝试下载初始化数据...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()['result']
            
            os.makedirs('data', exist_ok=True)
            with open('data/happy8_history.csv', 'w', encoding='utf-8-sig', newline='') as f:
                fieldnames = ['期号', '日期'] + [f'号码{i+1}' for i in range(20)]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for item in data:
                    row = {'期号': item['code'], '日期': item['date'].split('(')[0]}
                    nums = item['red'].split(',')
                    for i, n in enumerate(nums):
                        row[f'号码{i+1}'] = n.zfill(2)
                    writer.writerow(row)
            print(f"成功初始化 50 期历史数据！文件已保存至 data/happy8_history.csv")
        else:
            print(f"下载失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"下载异常: {e}")

if __name__ == "__main__":
    init_data()
