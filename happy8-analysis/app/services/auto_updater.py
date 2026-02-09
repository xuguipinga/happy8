"""
自动数据更新服务
定期从网络获取最新的快乐8开奖数据
"""
from datetime import datetime
from flask import current_app
from app.utils.data_loader import fetch_from_network, save_to_csv, read_from_csv


class AutoUpdater:
    """自动数据更新服务"""
    
    def __init__(self):
        self.last_update_time = None
        self.last_period = None
    
    def check_and_update(self):
        """检查并更新数据"""
        try:
            current_app.logger.info('开始自动检查数据更新...')
            
            # 读取本地最新期号
            local_data = read_from_csv(limit=1)
            local_period = local_data[0]['period'] if local_data else None
            
            # 从网络获取最新数据
            network_data = fetch_from_network(limit=10)
            
            if not network_data:
                current_app.logger.warning('无法从网络获取数据')
                return False
            
            network_period = network_data[0]['period']
            
            # 检查是否有新数据
            if local_period and network_period == local_period:
                current_app.logger.info(f'数据已是最新 (期号: {local_period})')
                return False
            
            # 发现新数据,获取完整历史并保存
            current_app.logger.info(f'发现新数据! 本地: {local_period}, 网络: {network_period}')
            full_data = fetch_from_network(limit=100)
            
            if full_data and save_to_csv(full_data):
                self.last_update_time = datetime.now()
                self.last_period = network_period
                current_app.logger.info(f'✓ 数据更新成功! 最新期号: {network_period}')
                return True
            else:
                current_app.logger.error('数据保存失败')
                return False
                
        except Exception as e:
            current_app.logger.error(f'自动更新失败: {e}')
            return False
    
    def get_status(self):
        """获取更新状态"""
        return {
            'last_update_time': self.last_update_time.isoformat() if self.last_update_time else None,
            'last_period': self.last_period
        }


# 全局实例
auto_updater = AutoUpdater()
