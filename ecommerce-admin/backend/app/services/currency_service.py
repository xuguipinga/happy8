import requests
from datetime import datetime
from decimal import Decimal

class CurrencyService:
    """
    汇率服务
    支持按日期查询历史汇率
    """
    
    # 默认汇率 (作为兜底)
    DEFAULT_RATE = Decimal('7.25')

    @staticmethod
    def get_rate_to_cny(from_currency='USD', target_date=None):
        """
        获取指定日期从指定币种转为 CNY 的汇率
        """
        if from_currency == 'CNY':
            return Decimal('1.0')
            
        # TODO: 实际生产中可以调用 1688 API 或 Open Exchange Rates API
        # 这里模拟一个基于日期的简单波动或返回默认值
        # 针对 1688 的汇率通常比较稳定，可以先用默认值，预留接口
        
        # 示例：如果日期在 2024 年之后，使用 7.25，否则 7.0
        if target_date and isinstance(target_date, datetime):
            if target_date.year >= 2024:
                return Decimal('7.25')
            else:
                return Decimal('7.0')
                
        return CurrencyService.DEFAULT_RATE

    @staticmethod
    def convert_to_cny(amount, from_currency='USD', target_date=None):
        """将金额转换为人民币"""
        if not amount:
            return Decimal('0.0')
        
        rate = CurrencyService.get_rate_to_cny(from_currency, target_date)
        return Decimal(str(amount)) * rate
