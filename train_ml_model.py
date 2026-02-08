"""
机器学习模型训练脚本
训练并保存预测模型
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.data_loader import read_from_csv
from app.services.ml_predictor import LotteryMLPredictor
from app import create_app

def main():
    """训练模型"""
    print("=" * 60)
    print("快乐8 机器学习模型训练")
    print("=" * 60)
    
    # 创建Flask应用上下文
    app = create_app()
    
    with app.app_context():
        # 读取历史数据
        print("\n[1/4] 读取历史数据...")
        history_data = read_from_csv(limit=100)
        
        if not history_data:
            print("❌ 错误: 无法读取历史数据")
            return
        
        print(f"[OK] 成功读取 {len(history_data)} 期历史数据")
        
        # 创建预测器
        print("\n[2/4] 初始化ML预测器...")
        predictor = LotteryMLPredictor(model_path='d:/happy8/data/ml_models')
        print("[OK] 预测器初始化完成")
        
        # 训练模型
        print("\n[3/4] 开始训练模型...")
        print("(这可能需要几分钟时间,请耐心等待...)")
        
        result = predictor.train(history_data, test_size=0.2)
        
        if result['success']:
            print(f"\n[OK] 模型训练完成!")
            print(f"  - 训练样本数: {result['sample_count']}")
            print(f"  - 特征数量: {result['feature_count']}")
            print(f"  - 平均训练分数: {result['avg_train_score']:.3f}")
            print(f"  - 平均测试分数: {result['avg_test_score']:.3f}")
        else:
            print(f"[ERROR] 训练失败: {result.get('message', '未知错误')}")
            return
        
        # 保存模型
        print("\n[4/4] 保存模型...")
        if predictor.save_models():
            print("[OK] 模型已保存到: d:/happy8/data/ml_models/")
        else:
            print("[ERROR] 模型保存失败")
            return
        
        # 测试预测
        print("\n" + "=" * 60)
        print("测试预测功能")
        print("=" * 60)
        
        probabilities = predictor.predict_probabilities(history_data)
        if probabilities:
            # 显示概率最高的10个号码
            sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
            print("\n概率最高的10个号码:")
            for i, (num, prob) in enumerate(sorted_probs[:10], 1):
                print(f"  {i}. 号码 {num}: {prob:.3f}")
            
            # 生成推荐
            recommendations = predictor.generate_recommendations(history_data)
            print("\nML推荐结果:")
            for key, value in recommendations.items():
                if key != 'probabilities':
                    print(f"  - {key}: {' '.join(value)}")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] 训练完成!")
        print("=" * 60)
        print("\n提示: 重启应用后,系统将自动加载训练好的模型")

if __name__ == '__main__':
    main()
