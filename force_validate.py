
import json
import csv
import os

def force_validate():
    csv_path = 'data/happy8_history.csv'
    json_path = 'data/recommendations_history.json'
    
    if not os.path.exists(csv_path) or not os.path.exists(json_path):
        print("文件缺失，无法验证")
        return

    # 读取 CSV 开奖数据
    winning_data = {}
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            period = row.get('期号', '').strip()
            numbers = [row[f'号码{i+1}'] for i in range(20) if f'号码{i+1}' in row]
            winning_data[period] = numbers

    # 读取并更新校验 JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        history = json.load(f)

    updated_count = 0
    for period, record in history.items():
        if period in winning_data:
            actual = winning_data[period]
            recommendations = record.get('recommendations', {})
            
            validation = {}
            for key, predicted in recommendations.items():
                if isinstance(predicted, list):
                    hits = [n for n in predicted if n in actual]
                    validation[key] = {
                        'predicted': predicted,
                        'hits': hits,
                        'hit_count': len(hits),
                        'hit_rate': f"{len(hits)/len(predicted)*100:.1f}%" if predicted else "0%"
                    }
            
            history[period]['actual_result'] = actual
            history[period]['validation'] = validation
            updated_count += 1
            print(f"成功验证期号: {period}")

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    print(f"共强制更新 {updated_count} 条验证记录。")

if __name__ == "__main__":
    force_validate()
