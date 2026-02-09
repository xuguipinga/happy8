"""
机器学习预测模块
使用随机森林模型预测号码出现概率
"""
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from flask import current_app
from app.services.ml_features import (
    extract_all_features,
    create_training_dataset,
    extract_number_frequency,
    extract_number_omission
)


class LotteryMLPredictor:
    """快乐8机器学习预测器"""
    
    def __init__(self, model_path=None):
        """
        初始化预测器
        
        Args:
            model_path: 模型保存路径
        """
        self.models = {}  # 为每个号码存储一个模型
        self.model_path = model_path or 'data/ml_models'
        self.is_trained = False
        
    def train(self, history_data, test_size=0.2):
        """
        训练模型
        
        Args:
            history_data: 历史数据列表
            test_size: 测试集比例
            
        Returns:
            dict: 训练结果统计
        """
        current_app.logger.info(f'开始训练ML模型,数据量: {len(history_data)}期')
        
        # 创建训练数据集
        X, y, number_labels = create_training_dataset(history_data, window_size=10)
        
        if len(X) < 20:
            current_app.logger.warning('数据量不足,无法训练模型')
            return {'success': False, 'message': '数据量不足'}
        
        current_app.logger.info(f'训练样本数: {len(X)}, 特征数: {X.shape[1]}')
        
        # 分割训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # 为每个号码训练一个分类器
        results = {}
        for i, number in enumerate(number_labels):
            # 创建随机森林分类器
            clf = RandomForestClassifier(
                n_estimators=50,  # 树的数量
                max_depth=10,     # 最大深度
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1  # 使用所有CPU核心
            )
            
            # 训练
            clf.fit(X_train, y_train[:, i])
            
            # 评估
            train_score = clf.score(X_train, y_train[:, i])
            test_score = clf.score(X_test, y_test[:, i])
            
            self.models[number] = clf
            results[number] = {
                'train_score': train_score,
                'test_score': test_score
            }
        
        self.is_trained = True
        
        # 计算平均得分
        avg_train_score = np.mean([r['train_score'] for r in results.values()])
        avg_test_score = np.mean([r['test_score'] for r in results.values()])
        
        current_app.logger.info(f'模型训练完成! 平均训练分数: {avg_train_score:.3f}, 平均测试分数: {avg_test_score:.3f}')
        
        return {
            'success': True,
            'avg_train_score': avg_train_score,
            'avg_test_score': avg_test_score,
            'sample_count': len(X),
            'feature_count': X.shape[1]
        }
    
    def predict_probabilities(self, history_data):
        """
        预测每个号码的出现概率
        
        Args:
            history_data: 历史数据列表(用于提取特征)
            
        Returns:
            dict: {号码: 概率}
        """
        if not self.is_trained:
            current_app.logger.warning('模型未训练,无法预测')
            return {}
        
        # 提取最新一期的特征
        features = extract_all_features(history_data, target_index=0)
        if features is None:
            return {}
        
        # 转换为特征向量
        feature_vector = np.array([list(features.values())]).reshape(1, -1)
        
        # 预测每个号码的概率
        probabilities = {}
        for number, model in self.models.items():
            # 获取正类(号码出现)的概率
            prob = model.predict_proba(feature_vector)[0][1]
            probabilities[number] = prob
        
        return probabilities
    
    def generate_recommendations(self, history_data, balance=True):
        """
        基于预测概率生成推荐
        
        Args:
            history_data: 历史数据
            balance: 是否进行区间平衡
            
        Returns:
            dict: 推荐号码
        """
        # 预测概率
        probabilities = self.predict_probabilities(history_data)
        
        if not probabilities:
            current_app.logger.warning('无法生成ML推荐:概率预测失败')
            return {}
        
        # 按概率排序
        sorted_numbers = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        
        recommendations = {}
        
        if balance:
            # 带平衡的推荐
            recommendations['ml_pick5'] = self._balanced_selection(sorted_numbers, 5)
            recommendations['ml_pick6'] = self._balanced_selection(sorted_numbers, 6)
            recommendations['ml_pick7'] = self._balanced_selection(sorted_numbers, 7)
            recommendations['ml_pick10'] = self._balanced_selection(sorted_numbers, 10)
        else:
            # 纯概率推荐
            recommendations['ml_pick5'] = [num for num, prob in sorted_numbers[:5]]
            recommendations['ml_pick6'] = [num for num, prob in sorted_numbers[:6]]
            recommendations['ml_pick7'] = [num for num, prob in sorted_numbers[:7]]
            recommendations['ml_pick10'] = [num for num, prob in sorted_numbers[:10]]
        
        # 混合推荐:结合热号和ML预测
        hot_numbers = self._get_hot_numbers(history_data, 10)
        ml_top = [num for num, prob in sorted_numbers[:10]]
        mixed = list(set(hot_numbers[:5] + ml_top[:5]))[:7]
        recommendations['ml_mixed'] = sorted(mixed)
        
        # 保存概率信息(用于前端展示)
        recommendations['probabilities'] = {
            num: round(prob, 3) for num, prob in sorted_numbers[:20]
        }
        
        return recommendations
    
    def _balanced_selection(self, sorted_numbers, count):
        """
        平衡选择号码(考虑区间分布)
        
        Args:
            sorted_numbers: 按概率排序的号码列表
            count: 需要选择的数量
            
        Returns:
            list: 选中的号码
        """
        selected = []
        zone_counts = [0, 0, 0, 0]  # 四个区间的计数
        
        # 期望每个区间的数量
        expected_per_zone = count / 4
        
        for number, prob in sorted_numbers:
            if len(selected) >= count:
                break
            
            num_int = int(number)
            zone_idx = min((num_int - 1) // 20, 3)
            
            # 如果该区间还没达到期望数量,或者已经选够了但这个号码概率很高
            if zone_counts[zone_idx] < expected_per_zone + 1 or len(selected) < count // 2:
                selected.append(number)
                zone_counts[zone_idx] += 1
        
        # 如果还不够,继续添加概率最高的
        for number, prob in sorted_numbers:
            if len(selected) >= count:
                break
            if number not in selected:
                selected.append(number)
        
        return sorted(selected[:count])
    
    def _get_hot_numbers(self, history_data, count):
        """获取热号"""
        frequency = extract_number_frequency(history_data, periods=20)
        sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        return [num for num, freq in sorted_freq[:count]]
    
    def save_models(self):
        """保存模型到文件"""
        if not self.is_trained:
            current_app.logger.warning('模型未训练,无法保存')
            return False
        
        os.makedirs(self.model_path, exist_ok=True)
        model_file = os.path.join(self.model_path, 'lottery_models.pkl')
        
        try:
            with open(model_file, 'wb') as f:
                pickle.dump(self.models, f)
            current_app.logger.info(f'模型已保存到: {model_file}')
            return True
        except Exception as e:
            current_app.logger.error(f'保存模型失败: {e}')
            return False
    
    def load_models(self):
        """从文件加载模型"""
        model_file = os.path.join(self.model_path, 'lottery_models.pkl')
        
        if not os.path.exists(model_file):
            current_app.logger.warning(f'模型文件不存在: {model_file}')
            return False
        
        try:
            with open(model_file, 'rb') as f:
                self.models = pickle.load(f)
            self.is_trained = True
            current_app.logger.info(f'模型已加载: {len(self.models)}个分类器')
            return True
        except Exception as e:
            current_app.logger.error(f'加载模型失败: {e}')
            return False


# 全局预测器实例
ml_predictor = LotteryMLPredictor()
